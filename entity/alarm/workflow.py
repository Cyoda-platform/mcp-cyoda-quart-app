from datetime import datetime, timedelta
import logging
from common.config.config import ENTITY_VERSION

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_services():
    from app_init.app_init import entity_service, cyoda_auth_service
    return entity_service, cyoda_auth_service

BOILING_TIMES = {
    "soft": 4 * 60,
    "medium": 7 * 60,
    "hard": 10 * 60,
}

alarm_entity_name = "alarm"

async def process_alarm(entity: dict):
    egg_type = entity.get("egg_type")
    if egg_type not in BOILING_TIMES:
        raise ValueError(f"Invalid egg_type: {egg_type}")

    entity_service, cyoda_auth_service = get_services()

    try:
        alarms = await entity_service.get_items(
            token=cyoda_auth_service,
            entity_model=alarm_entity_name,
            entity_version=ENTITY_VERSION
        )
        for alarm in alarms:
            if alarm.get("status") in ("running", "ringing"):
                alarm["status"] = "cancelled"
                await entity_service.update_item(
                    token=cyoda_auth_service,
                    entity_model=alarm_entity_name,
                    entity_version=ENTITY_VERSION,
                    entity=alarm,
                    technical_id=alarm["id"],
                    meta={}
                )
    except Exception as e:
        logger.exception("Failed to cancel existing alarms in workflow: %s", e)

    if "end_time" not in entity:
        boiling_seconds = BOILING_TIMES[egg_type]
        end_time = datetime.utcnow() + timedelta(seconds=boiling_seconds)
        entity["end_time"] = end_time.isoformat()
    else:
        try:
            datetime.fromisoformat(entity["end_time"])
        except Exception:
            boiling_seconds = BOILING_TIMES[egg_type]
            end_time = datetime.utcnow() + timedelta(seconds=boiling_seconds)
            entity["end_time"] = end_time.isoformat()

    entity.setdefault("status", "running")
    entity.setdefault("set_at", datetime.utcnow().isoformat())

    return entity

async def is_time_up(entity: dict) -> bool:
    end_time_str = entity.get("end_time")
    if not end_time_str:
        return False
    try:
        end_time = datetime.fromisoformat(end_time_str)
    except Exception as e:
        logger.exception(e)
        return False
    return datetime.utcnow() >= end_time

async def is_cancel_requested(entity: dict) -> bool:
    return entity.get("cancel_requested", False) is True

async def has_ringing_duration_passed(entity: dict) -> bool:
    ring_start_str = entity.get("ring_start")
    if not ring_start_str:
        return False
    try:
        ring_start = datetime.fromisoformat(ring_start_str)
    except Exception as e:
        logger.exception(e)
        return False
    return (datetime.utcnow() - ring_start) >= timedelta(seconds=5)