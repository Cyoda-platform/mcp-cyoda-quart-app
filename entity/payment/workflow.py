import asyncio
import datetime
import uuid
import logging
from common.config.config import ENTITY_VERSION

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_services():
    from app_init.app_init import entity_service, cyoda_auth_service
    return entity_service, cyoda_auth_service

entity_service, cyoda_auth_service = get_services()

def gen_id():
    return str(uuid.uuid4())

async def process_order(entity: dict):
    try:
        if not entity.get('orderId'):
            entity['orderId'] = gen_id()
        # Additional processing logic can be added here
    except Exception as e:
        logger.exception(e)
    return entity

async def guard_cart_not_empty(entity: dict) -> bool:
    try:
        lines = entity.get("lines", [])
        if not lines:
            return False
        total_qty = sum(line.get("qty", 0) for line in lines)
        return total_qty > 0
    except Exception as e:
        logger.exception(e)
        return False

async def guard_cart_empty_or_invalid(entity: dict) -> bool:
    try:
        lines = entity.get("lines", [])
        if not lines:
            return True
        total_qty = sum(line.get("qty", 0) for line in lines)
        return total_qty == 0
    except Exception as e:
        logger.exception(e)
        return True

async def guard_payment_paid_and_shipments_delivered(entity: dict) -> bool:
    try:
        payment = entity.get("payment", {})
        if payment.get("status") != "PAID":
            return False
        shipments = entity.get("shipments", [])
        if not shipments:
            return False
        all_delivered = all(s.get("status") == "DELIVERED" for s in shipments)
        return all_delivered
    except Exception as e:
        logger.exception(e)
        return False

async def guard_payment_failed_or_cancelled(entity: dict) -> bool:
    try:
        payment = entity.get("payment", {})
        return payment.get("status") in {"FAILED", "CANCELED"}
    except Exception as e:
        logger.exception(e)
        return False

async def guard_order_in_fulfillment(entity: dict) -> bool:
    try:
        status = entity.get("status", "")
        return status == "PROCESSING"
    except Exception as e:
        logger.exception(e)
        return False