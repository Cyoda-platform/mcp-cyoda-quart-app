import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

import httpx
from quart import Quart, request, jsonify
from quart_schema import QuartSchema, validate_request

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Quart(__name__)
QuartSchema(app)

# Workaround: validate_request must be last for POST due to quart-schema issue
@dataclass
class SignupData:
    email: str

# In-memory caches for prototype (simulate persistence)
subscribers_cache: Dict[str, Dict[str, Any]] = {}
email_open_stats = {
    "totalEmailsSent": 0,
    "totalOpens": 0,
}

CAT_FACT_API_URL = "https://catfact.ninja/fact"

async def send_email(to_email: str, subject: str, body: str) -> None:
    # TODO: Replace with real email sending integration
    logger.info(f"Sending email to {to_email} with subject '{subject}'")
    await asyncio.sleep(0.1)

@app.route("/api/signup", methods=["POST"])
@validate_request(SignupData)  # Workaround: POST validation last
async def signup(data: SignupData):
    try:
        email = data.email
        if not email:
            return jsonify({"error": "Email is required"}), 400

        if email in subscribers_cache:
            return jsonify({
                "message": "Email already subscribed",
                "subscriberId": subscribers_cache[email]["id"]
            }), 200

        subscriber_id = f"sub-{len(subscribers_cache) + 1}"
        subscribers_cache[email] = {
            "id": subscriber_id,
            "email": email,
            "subscribedAt": datetime.utcnow().isoformat()
        }
        logger.info(f"New subscriber: {email} (id: {subscriber_id})")
        return jsonify({"message": "Subscription successful", "subscriberId": subscriber_id})
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500

async def fetch_cat_fact() -> str:
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(CAT_FACT_API_URL, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            fact = data.get("fact")
            if not fact:
                raise ValueError("No fact found")
            return fact
        except Exception as e:
            logger.exception(e)
            return "Cats are mysterious creatures."

async def process_send_facts():
    fact = await fetch_cat_fact()
    subject = "Your Weekly Cat Fact 🐱"
    body = f"Hello!\n\nHere is your weekly cat fact:\n\n{fact}\n\nEnjoy your week!"
    tasks = [send_email(sub["email"], subject, body) for sub in subscribers_cache.values()]
    await asyncio.gather(*tasks)
    email_open_stats["totalEmailsSent"] += len(subscribers_cache)
    # TODO: Implement real open tracking
    return fact

@app.route("/api/fetch-and-send", methods=["POST"])
async def fetch_and_send():
    try:
        fact = await process_send_facts()
        return jsonify({"message": "Cat fact sent to subscribers", "catFact": fact})
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "Failed to fetch/send cat fact"}), 500

@app.route("/api/report/subscribers", methods=["GET"])
async def report_subscribers():
    return jsonify({"subscriberCount": len(subscribers_cache)})

@app.route("/api/report/interactions", methods=["GET"])
async def report_interactions():
    total = email_open_stats["totalEmailsSent"]
    opens = email_open_stats["totalOpens"]
    rate = (opens / total) if total else 0
    return jsonify({"totalEmailsSent": total, "totalOpens": opens, "openRate": round(rate, 3)})

if __name__ == '__main__':
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=8000, threaded=True)