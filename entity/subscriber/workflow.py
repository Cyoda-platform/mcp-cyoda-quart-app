import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
from common.config.config import ENTITY_VERSION

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_services():
    from app_init.app_init import entity_service, cyoda_auth_service
    return entity_service, cyoda_auth_service

entity_service, cyoda_auth_service = get_services()

async def process_subscriber(entity: Dict[str, Any]):
    try:
        if "subscribedAt" not in entity:
            entity["subscribedAt"] = datetime.utcnow().isoformat()
        entity.setdefault("status", "active")

        async def fire_and_forget_send():
            subject = "Welcome to Cat Facts!"
            body = (
                f"Hello!\n\n"
                f"Thank you for subscribing with {entity.get('email')}.\n"
                f"You will start receiving weekly cat facts."
            )
            try:
                await send_email(entity.get("email"), subject, body)
                logger.info(f"Welcome email sent to {entity.get('email')}")
            except Exception:
                logger.exception("Failed to send welcome email")

        asyncio.create_task(fire_and_forget_send())
    except Exception as e:
        logger.exception(e)
    return entity

async def is_new_subscriber(entity: Dict[str, Any]) -> bool:
    try:
        return "subscribedAt" not in entity
    except Exception as e:
        logger.exception(e)
        return False

async def is_active(entity: Dict[str, Any]) -> bool:
    try:
        return entity.get("status") == "active"
    except Exception as e:
        logger.exception(e)
        return False

async def fetch_and_store_cat_fact(entity: Dict[str, Any]) -> Dict[str, Any]:
    try:
        fact = await fetch_cat_fact()
        entity["latestCatFact"] = fact
        entity["factFetchedAt"] = datetime.utcnow().isoformat()
    except Exception as e:
        logger.exception(e)
    return entity

async def send_weekly_fact_emails(entity: Dict[str, Any]) -> Dict[str, Any]:
    try:
        subscribers = entity.get("subscribers", [])
        subject = "Your Weekly Cat Fact 🐱"
        fact = entity.get("latestCatFact", "Did you know cats purr?")
        body = f"Hello!\n\nHere is your weekly cat fact:\n\n{fact}\n\nEnjoy your week!"

        async def send_to(email: str):
            try:
                await send_email(email, subject, body)
                logger.info(f"Weekly cat fact email sent to {email}")
            except Exception:
                logger.exception(f"Failed to send weekly cat fact email to {email}")

        tasks = [send_to(sub.get("email")) for sub in subscribers if sub.get("status") == "active"]
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.exception(e)
    return entity

# Helpers (from initial code, assumed available)

async def send_email(to_email: str, subject: str, body: str) -> None:
    # TODO: Replace with real email sending integration
    logger.info(f"Sending email to {to_email} with subject '{subject}'")
    await asyncio.sleep(0.1)

async def fetch_cat_fact() -> str:
    import httpx
    CAT_FACT_API_URL = "https://catfact.ninja/fact"
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
