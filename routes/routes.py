import asyncio
import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import httpx
from quart import Blueprint, jsonify, request, abort
from quart_schema import validate_request, validate_querystring

from service.registry import get_entity_service, get_auth_service
from common.config.config import ENTITY_VERSION
# Removed health and metrics modules for simplicity

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Services will be accessed through the registry
entity_service = None
cyoda_auth_service = None

routes_bp = Blueprint('routes', __name__)


def get_services():
    """Get services from the registry lazily."""
    global entity_service, cyoda_auth_service
    if entity_service is None:
        entity_service = get_entity_service()
    if cyoda_auth_service is None:
        cyoda_auth_service = get_auth_service()
    return entity_service, cyoda_auth_service

@dataclass
class SubscriberRequest:
    email: Optional[str]
    webhook_url: Optional[str]

@dataclass
class LaureateQuery:
    year: Optional[str]
    category: Optional[str]

NOBEL_API_URL = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/nobel-prize-laureates/records?limit=100"

def validate_laureate(raw: dict) -> Optional[dict]:
    fields = raw.get("record", {}).get("fields", {})
    required = [
        "id", "firstname", "surname", "gender", "born", "borncountry",
        "borncountrycode", "borncity", "year", "category", "motivation",
        "name", "city", "country",
    ]
    for f in required:
        if fields.get(f) is None:
            logger.warning(f"Missing required laureate field: {f}")
            return None
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

async def process_subscriber(entity: dict):
    if entity.get("email"):
        entity["email"] = entity["email"].lower()
    if "status" not in entity:
        entity["status"] = "active"
    return entity

async def process_job(entity: dict):
    entity_service, cyoda_auth_service = get_services()

    entity["state"] = "INGESTING"
    entity["started_at"] = datetime.utcnow().isoformat()
    entity["completed_at"] = None
    entity["error_message"] = None

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(NOBEL_API_URL)
            resp.raise_for_status()
            data = resp.json()

        records = data.get("records", [])
        valid_laureates = [l for rec in records if (l := validate_laureate(rec))]

        for l in valid_laureates:
            try:
                await entity_service.update_item(
                    token=cyoda_auth_service,
                    entity_model="laureate",
                    entity_version=ENTITY_VERSION,
                    entity=l,
                    technical_id=str(l["id"]),
                    meta={}
                )
            except Exception as e:
                logger.exception(f"Failed to update laureate id={l['id']}: {e}")

        entity["state"] = "SUCCEEDED"
        entity["completed_at"] = datetime.utcnow().isoformat()
        entity["error_message"] = None

    except Exception as e:
        logger.exception(e)
        entity["state"] = "FAILED"
        entity["completed_at"] = datetime.utcnow().isoformat()
        entity["error_message"] = str(e)

    try:
        subscribers = await entity_service.get_items(
            token=cyoda_auth_service,
            entity_model="subscriber",
            entity_version=ENTITY_VERSION,
        )
        notify_payload = {
            "job_id": entity.get("job_id"),
            "status": entity.get("state"),
            "error": entity.get("error_message"),
            "timestamp": datetime.utcnow().isoformat(),
        }

        async def notify(sub):
            try:
                if sub.get("email"):
                    logger.info(f"Notify email {sub['email']}: {notify_payload}")
                if sub.get("webhook_url"):
                    async with httpx.AsyncClient() as client:
                        resp = await client.post(sub["webhook_url"], json=notify_payload, timeout=10)
                        resp.raise_for_status()
                    logger.info(f"Notify webhook {sub['webhook_url']} succeeded")
            except Exception as e:
                logger.exception(f"Notification failed for subscriber {sub.get('subscriber_id')}: {e}")

        await asyncio.gather(*(notify(sub) for sub in subscribers))
        entity["state"] = "NOTIFIED_SUBSCRIBERS"
    except Exception as e:
        logger.exception(f"Failed to notify subscribers: {e}")
        entity.setdefault("notification_error", str(e))

    return entity

@routes_bp.route("/jobs/schedule", methods=["POST"])
async def schedule_job():
    entity_service, cyoda_auth_service = get_services()

    job_id = str(uuid.uuid4())
    job_entity = {
        "job_id": job_id,
        "state": "SCHEDULED",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        job_entity_id = await entity_service.add_item(
            token=cyoda_auth_service,
            entity_model="job",
            entity_version=ENTITY_VERSION,
            entity=job_entity
        )
    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to schedule job")

    return jsonify({"job_id": job_id, "status": "SCHEDULED"}), 202

@routes_bp.route("/jobs/<string:job_id>", methods=["GET"])
async def get_job_status(job_id):
    entity_service, cyoda_auth_service = get_services()

    try:
        job = await entity_service.get_item(
            token=cyoda_auth_service,
            entity_model="job",
            entity_version=ENTITY_VERSION,
            technical_id=job_id
        )
    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to retrieve job status")
    if not job:
        abort(404, description="Job not found")
    return jsonify(job)

@routes_bp.route("/laureates", methods=["GET"])
@validate_querystring(LaureateQuery)
async def get_laureates():
    entity_service, cyoda_auth_service = get_services()

    args = LaureateQuery(**request.args)
    try:
        laureates = await entity_service.get_items(
            token=cyoda_auth_service,
            entity_model="laureate",
            entity_version=ENTITY_VERSION,
        )
    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to retrieve laureates")
    if args.year:
        laureates = [l for l in laureates if str(l.get("year")) == args.year]
    if args.category:
        laureates = [l for l in laureates if l.get("category") == args.category]
    return jsonify(laureates)

@routes_bp.route("/laureates/<string:technical_id>", methods=["GET"])
async def get_laureate(technical_id):
    entity_service, cyoda_auth_service = get_services()

    try:
        laureate = await entity_service.get_item(
            token=cyoda_auth_service,
            entity_model="laureate",
            entity_version=ENTITY_VERSION,
            technical_id=technical_id
        )
    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to retrieve laureate")
    if not laureate:
        abort(404, description="Laureate not found")
    return jsonify(laureate)

@routes_bp.route("/subscribers", methods=["GET"])
async def list_subscribers():
    entity_service, cyoda_auth_service = get_services()

    try:
        subscribers = await entity_service.get_items(
            token=cyoda_auth_service,
            entity_model="subscriber",
            entity_version=ENTITY_VERSION,
        )
    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to retrieve subscribers")
    return jsonify(subscribers)

@routes_bp.route("/subscribers", methods=["POST"])
@validate_request(SubscriberRequest)
async def add_subscriber(data: SubscriberRequest):
    entity_service, cyoda_auth_service = get_services()

    if not data.email and not data.webhook_url:
        abort(400, description="At least one contact must be provided")
    subscriber_obj = {
        "email": data.email,
        "webhook_url": data.webhook_url,
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
    }
    try:
        subscriber_id = await entity_service.add_item(
            token=cyoda_auth_service,
            entity_model="subscriber",
            entity_version=ENTITY_VERSION,
            entity=subscriber_obj
        )
    except Exception as e:
        logger.exception(e)


# Health Check and Monitoring Endpoints

@routes_bp.route('/health', methods=['GET'])
async def health_check():
    """Health check endpoint."""
    try:
        # Simple health check - just verify the app is running
        return jsonify({
            "status": "healthy",
            "message": "Application is running",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200

    except Exception as e:
        logger.exception("Health check failed")
        return jsonify({
            "status": "unhealthy",
            "message": f"Health check error: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 503


@routes_bp.route('/health/live', methods=['GET'])
async def liveness_check():
    """Kubernetes liveness probe endpoint."""
    return jsonify({
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200


@routes_bp.route('/health/ready', methods=['GET'])
async def readiness_check():
    """Kubernetes readiness probe endpoint."""
    try:
        # Simple readiness check
        return jsonify({
            "status": "ready",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200

    except Exception as e:
        logger.exception("Readiness check failed")
        return jsonify({
            "status": "not_ready",
            "message": f"Readiness check failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }), 503


@routes_bp.route('/metrics', methods=['GET'])
async def metrics():
    """Metrics endpoint in Prometheus format."""
    try:
        collector = get_metrics_collector()
        exporter = MetricsExporter(collector)

        # Check if Prometheus format is requested
        accept_header = request.headers.get('Accept', '')
        if 'application/json' in accept_header:
            metrics_data = exporter.export_json_format()
            return jsonify(metrics_data)
        else:
            # Default to Prometheus format
            prometheus_data = exporter.export_prometheus_format()
            return prometheus_data, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    except Exception as e:
        logger.exception("Metrics export failed")
        return jsonify({
            "error": f"Metrics export failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }), 500


@routes_bp.route('/metrics/summary', methods=['GET'])
async def metrics_summary():
    """Metrics summary endpoint in JSON format."""
    try:
        collector = get_metrics_collector()
        summary = collector.get_metrics_summary()
        return jsonify(summary)

    except Exception as e:
        logger.exception("Metrics summary failed")
        return jsonify({
            "error": f"Metrics summary failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }), 500


@routes_bp.route('/info', methods=['GET'])
async def system_info():
    """System information endpoint."""
    try:
        from common.config.manager import get_config_manager

        config_manager = get_config_manager()

        info = {
            "application": {
                "name": "Cyoda gRPC Client",
                "version": ENTITY_VERSION,
                "environment": config_manager.environment.value if hasattr(config_manager, 'environment') else "development",
                "uptime_seconds": time.time() - start_time if 'start_time' in globals() else 0
            },
            "configuration": {
                "sections": list(config_manager._sections.keys()) if hasattr(config_manager, '_sections') else [],
                "loaded_files": config_manager._loaded_files if hasattr(config_manager, '_loaded_files') else []
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        return jsonify(info)

    except Exception as e:
        logger.exception("System info failed")
        return jsonify({
            "error": f"System info failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }), 500
        abort(500, description="Failed to add subscriber")
    return jsonify({"subscriber_id": subscriber_id, "status": "active"}), 201