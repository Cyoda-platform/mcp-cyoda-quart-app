```python
import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

import httpx
from quart import Quart, jsonify, request, abort
from quart_schema import QuartSchema

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Quart(__name__)
QuartSchema(app)

# In-memory stores (async-safe usage via asyncio.Lock)
entity_jobs: Dict[str, dict] = {}
entity_laureates: Dict[int, dict] = {}
entity_subscribers: Dict[str, dict] = {}
lock = asyncio.Lock()

NOBEL_API_URL = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/nobel-prize-laureates/records?limit=100"

# --- Utility functions ---


def validate_laureate(raw: dict) -> Optional[dict]:
    """ Validate & extract required laureate fields from raw API data record. """
    fields = raw.get("record", {}).get("fields", {})
    # Required fields check (minimal)
    required = [
        "id",
        "firstname",
        "surname",
        "gender",
        "born",
        "borncountry",
        "borncountrycode",
        "borncity",
        "year",
        "category",
        "motivation",
        "name",
        "city",
        "country",
    ]
    for f in required:
        if fields.get(f) is None:
            logger.warning(f"Missing required laureate field: {f} in id={fields.get('id')}")
            return None

    # Normalize dates (born, died can be null)
    born = fields.get("born")
    died = fields.get("died")
    try:
        if born:
            datetime.fromisoformat(born)
        if died:
            datetime.fromisoformat(died)
    except Exception:
        logger.warning(f"Invalid date format for laureate id={fields.get('id')}")
        return None

    # Build laureate dict (subset)
    laureate = {
        "id": fields["id"],
        "firstname": fields["firstname"],
        "surname": fields["surname"],
        "gender": fields["gender"],
        "born": born,
        "died": died,
        "borncountry": fields["borncountry"],
        "borncountrycode": fields["borncountrycode"],
        "borncity": fields["borncity"],
        "year": fields["year"],
        "category": fields["category"],
        "motivation": fields["motivation"],
        "name": fields["name"],
        "city": fields["city"],
        "country": fields["country"],
    }
    return laureate


async def notify_subscribers(job_id: str, success: bool, error_message: Optional[str]):
    """Notify all active subscribers about job completion status."""
    async with lock:
        subscribers = list(entity_subscribers.values())
    notify_payload = {
        "job_id": job_id,
        "status": "SUCCEEDED" if success else "FAILED",
        "error": error_message,
        "timestamp": datetime.utcnow().isoformat(),
    }

    async def notify(sub):
        try:
            if sub.get("email"):
                # TODO: Implement real email sending (mocked here as log)
                logger.info(f"Notify email {sub['email']} for job {job_id}: {notify_payload}")
            if sub.get("webhook_url"):
                async with httpx.AsyncClient() as client:
                    resp = await client.post(sub["webhook_url"], json=notify_payload, timeout=10)
                    resp.raise_for_status()
                logger.info(f"Notify webhook {sub['webhook_url']} for job {job_id} succeeded")
        except Exception as e:
            logger.exception(f"Notification to subscriber {sub.get('subscriber_id')} failed: {e}")

    await asyncio.gather(*(notify(sub) for sub in subscribers))


async def process_job(job_id: str):
    """Main ingestion workflow: fetch data, validate/enrich, store, notify subscribers."""
    async with lock:
        job = entity_jobs.get(job_id)
        if not job:
            logger.error(f"Job {job_id} not found during processing")
            return
        job["state"] = "INGESTING"
        job["started_at"] = datetime.utcnow().isoformat()
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(NOBEL_API_URL)
            resp.raise_for_status()
            data = resp.json()
        records = data.get("records", [])
        valid_laureates = []
        for rec in records:
            laureate = validate_laureate(rec)
            if laureate:
                valid_laureates.append(laureate)

        async with lock:
            for l in valid_laureates:
                entity_laureates[l["id"]] = l

            job["state"] = "SUCCEEDED"
            job["completed_at"] = datetime.utcnow().isoformat()
            job["error_message"] = None

        await notify_subscribers(job_id, True, None)

    except Exception as e:
        logger.exception(e)
        async with lock:
            job["state"] = "FAILED"
            job["completed_at"] = datetime.utcnow().isoformat()
            job["error_message"] = str(e)
        await notify_subscribers(job_id, False, str(e))
    finally:
        async with lock:
            job["state"] = "NOTIFIED_SUBSCRIBERS"


# --- API routes ---


@app.route("/jobs/schedule", methods=["POST"])
async def schedule_job():
    job_id = str(uuid.uuid4())
    requested_at = datetime.utcnow().isoformat()
    async with lock:
        entity_jobs[job_id] = {
            "job_id": job_id,
            "state": "SCHEDULED",
            "created_at": requested_at,
            "completed_at": None,
            "error_message": None,
        }
    logger.info(f"Job {job_id} scheduled")
    # Fire and forget processing task
    asyncio.create_task(process_job(job_id))
    return jsonify({"job_id": job_id, "status": "SCHEDULED"}), 202


@app.route("/jobs/<string:job_id>", methods=["GET"])
async def get_job_status(job_id):
    async with lock:
        job = entity_jobs.get(job_id)
    if not job:
        abort(404, description="Job not found")
    return jsonify(job)


@app.route("/laureates", methods=["GET"])
async def get_laureates():
    year = request.args.get("year")
    category = request.args.get("category")
    async with lock:
        laureates = list(entity_laureates.values())
    if year:
        laureates = [l for l in laureates if str(l.get("year")) == str(year)]
    if category:
        laureates = [l for l in laureates if l.get("category") == category]
    return jsonify(laureates)


@app.route("/subscribers", methods=["POST"])
async def add_subscriber():
    data = await request.get_json(force=True)
    # minimal validation
    email = data.get("email")
    webhook_url = data.get("webhook_url")
    if not email and not webhook_url:
        abort(400, description="At least one contact (email or webhook_url) must be provided")
    subscriber_id = str(uuid.uuid4())
    subscriber = {
        "subscriber_id": subscriber_id,
        "email": email,
        "webhook_url": webhook_url,
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
    }
    async with lock:
        entity_subscribers[subscriber_id] = subscriber
    return jsonify({"subscriber_id": subscriber_id, "status": "active"}), 201


@app.route("/subscribers", methods=["GET"])
async def list_subscribers():
    async with lock:
        subscribers = list(entity_subscribers.values())
    return jsonify(subscribers)


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    app.run(use_reloader=False, debug=True, host="0.0.0.0", port=8000, threaded=True)
```
