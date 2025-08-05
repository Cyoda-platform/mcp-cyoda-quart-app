import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any

import httpx
from quart import Quart, jsonify
from quart_schema import QuartSchema, validate_request

from app_init.app_init import BeanFactory
from common.config.config import ENTITY_VERSION

factory = BeanFactory(config={'CHAT_REPOSITORY': 'cyoda'})
entity_service = factory.get_services()['entity_service']
cyoda_auth_service = factory.get_services()["cyoda_auth_service"]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Quart(__name__)
QuartSchema(app)

@dataclass
class SignupData:
    email: str

CAT_FACT_API_URL = "https://catfact.ninja/fact"

email_open_stats = {
    "totalEmailsSent": 0,
    "totalOpens": 0,
}

async def send_email(to_email: str, subject: str, body: str) -> None:
    # Simulated email sending
    logger.info(f"Sending email to {to_email} with subject '{subject}'")
    await asyncio.sleep(0.1)

# Workflow function for subscriber entity
async def process_subscriber(entity_data: Dict[str, Any]) -> Dict[str, Any]:
    # Set subscribedAt timestamp if missing
    if "subscribedAt" not in entity_data:
        entity_data["subscribedAt"] = datetime.utcnow().isoformat()

    # Set status active by default
    entity_data.setdefault("status", "active")

    # Send welcome email asynchronously (fire and forget)
    async def fire_and_forget_send():
        subject = "Welcome to Cat Facts!"
        body = (
            f"Hello!\n\n"
            f"Thank you for subscribing with {entity_data.get('email')}.\n"
            f"You will start receiving weekly cat facts."
        )
        try:
            await send_email(entity_data.get("email"), subject, body)
            logger.info(f"Welcome email sent to {entity_data.get('email')}")
        except Exception:
            logger.exception("Failed to send welcome email")

    # Trigger without awaiting - do not block persistence
    asyncio.create_task(fire_and_forget_send())

    return entity_data

@app.route("/api/signup", methods=["POST"])
@validate_request(SignupData)
async def signup(data: SignupData):
    try:
        email = data.email
        if not email:
            return jsonify({"error": "Email is required"}), 400

        # Check if subscriber with this email exists (cannot move to workflow)
        condition = {
            "cyoda": {
                "type": "group",
                "operator": "AND",
                "conditions": [
                    {
                        "jsonPath": "$.email",
                        "operatorType": "EQUALS",
                        "value": email,
                        "type": "simple"
                    }
                ]
            }
        }
        items = await entity_service.get_items_by_condition(
            token=cyoda_auth_service,
            entity_model="subscriber",
            entity_version=ENTITY_VERSION,
            condition=condition
        )
        if items:
            subscriber = items[0]
            return jsonify({
                "message": "Email already subscribed",
                "subscriberId": subscriber["id"]
            }), 200

        # Just pass minimal data; workflow sets subscribedAt, status, sends welcome email
        data_dict = {
            "email": email
        }
        subscriber_id = await entity_service.add_item(
            token=cyoda_auth_service,
            entity_model="subscriber",
            entity_version=ENTITY_VERSION,
            entity=data_dict
        )
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
    subject = "Your Weekly Cat Fact 
"
    body = f"Hello!\n\nHere is your weekly cat fact:\n\n{fact}\n\nEnjoy your week!"

    subscribers = await entity_service.get_items(
        token=cyoda_auth_service,
        entity_model="subscriber",
        entity_version=ENTITY_VERSION
    )
    tasks = [send_email(sub["email"], subject, body) for sub in subscribers]
    await asyncio.gather(*tasks)

    email_open_stats["totalEmailsSent"] += len(subscribers)
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
    try:
        subscribers = await entity_service.get_items(
            token=cyoda_auth_service,
            entity_model="subscriber",
            entity_version=ENTITY_VERSION
        )
        return jsonify({"subscriberCount": len(subscribers)})
    except Exception as e:
        logger.exception(e)
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/report/interactions", methods=["GET"])
async def report_interactions():
    total = email_open_stats["totalEmailsSent"]
    opens = email_open_stats["totalOpens"]
    rate = (opens / total) if total else 0
    return jsonify({"totalEmailsSent": total, "totalOpens": opens, "openRate": round(rate, 3)})

if __name__ == '__main__':
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=8000, threaded=True)
