from datetime import timezone, datetime
import logging
from quart import Blueprint, request, abort, jsonify
from quart_schema import validate, validate_querystring, tag, operation_id
from dataclasses import dataclass
import asyncio
from app_init.app_init import BeanFactory
from common.config.config import ENTITY_VERSION

logger = logging.getLogger(__name__)

FINAL_STATES = {'FAILURE', 'SUCCESS', 'CANCELLED', 'CANCELLED_BY_USER', 'UNKNOWN', 'FINISHED'}
PROCESSING_STATE = 'PROCESSING'

routes_bp = Blueprint('routes', __name__)

factory = BeanFactory(config={'CHAT_REPOSITORY': 'cyoda'})
entity_service = factory.get_services()['entity_service']
cyoda_auth_service = factory.get_services()["cyoda_auth_service"]

@dataclass
class AlarmRequest:
    egg_type: str

BOILING_TIMES = {
    "soft": 4 * 60,
    "medium": 7 * 60,
    "hard": 10 * 60,
}

alarm_entity_name = "alarm"

async def alarm_countdown(egg_type: str, end_time: datetime, technical_id: str):
    try:
        while True:
            now = datetime.utcnow()
            remaining = (end_time - now).total_seconds()
            if remaining <= 0:
                try:
                    alarm = await entity_service.get_item(
                        token=cyoda_auth_service,
                        entity_model=alarm_entity_name,
                        entity_version=ENTITY_VERSION,
                        technical_id=technical_id
                    )
                    if alarm and alarm.get("egg_type") == egg_type and alarm.get("status") == "running":
                        alarm["status"] = "ringing"
                        await entity_service.update_item(
                            token=cyoda_auth_service,
                            entity_model=alarm_entity_name,
                            entity_version=ENTITY_VERSION,
                            entity=alarm,
                            technical_id=technical_id,
                            meta={}
                        )
                except Exception as e:
                    logger.exception("Failed to update alarm to ringing: %s", e)
                logger.info(f"Alarm for {egg_type} egg is ringing now.")
                await asyncio.sleep(5)
                try:
                    alarm = await entity_service.get_item(
                        token=cyoda_auth_service,
                        entity_model=alarm_entity_name,
                        entity_version=ENTITY_VERSION,
                        technical_id=technical_id
                    )
                    if alarm and alarm.get("egg_type") == egg_type and alarm.get("status") == "ringing":
                        alarm["status"] = "stopped"
                        await entity_service.update_item(
                            token=cyoda_auth_service,
                            entity_model=alarm_entity_name,
                            entity_version=ENTITY_VERSION,
                            entity=alarm,
                            technical_id=technical_id,
                            meta={}
                        )
                        logger.info(f"Alarm for {egg_type} egg stopped automatically after ringing.")
                except Exception as e:
                    logger.exception("Failed to update alarm to stopped: %s", e)
                break
            await asyncio.sleep(min(remaining, 1))
    except Exception as e:
        logger.exception("Exception in alarm countdown: %s", e)
        try:
            alarm = await entity_service.get_item(
                token=cyoda_auth_service,
                entity_model=alarm_entity_name,
                entity_version=ENTITY_VERSION,
                technical_id=technical_id
            )
            if alarm and alarm.get("egg_type") == egg_type:
                alarm["status"] = "stopped"
                await entity_service.update_item(
                    token=cyoda_auth_service,
                    entity_model=alarm_entity_name,
                    entity_version=ENTITY_VERSION,
                    entity=alarm,
                    technical_id=technical_id,
                    meta={}
                )
        except Exception as e2:
            logger.exception("Failed to update alarm to stopped after exception: %s", e2)

@routes_bp.route("/alarm/set", methods=["POST"])
@validate(AlarmRequest)
async def set_alarm(data: AlarmRequest):
    egg_type = data.egg_type
    if egg_type not in BOILING_TIMES:
        return jsonify({"status": "error", "message": "Invalid egg_type"}), 400

    alarm_data = {
        "egg_type": egg_type,
    }

    try:
        alarm_id = await entity_service.add_item(
            token=cyoda_auth_service,
            entity_model=alarm_entity_name,
            entity_version=ENTITY_VERSION,
            entity=alarm_data
        )
    except Exception as e:
        logger.exception("Failed to add alarm item: %s", e)
        return jsonify({"status": "error", "message": "Failed to set alarm"}), 500

    try:
        persisted_alarm = await entity_service.get_item(
            token=cyoda_auth_service,
            entity_model=alarm_entity_name,
            entity_version=ENTITY_VERSION,
            technical_id=alarm_id
        )
        end_time = datetime.fromisoformat(persisted_alarm["end_time"])
        egg_type = persisted_alarm["egg_type"]
        asyncio.create_task(alarm_countdown(egg_type, end_time, alarm_id))
    except Exception as e:
        logger.exception("Failed to start countdown task after alarm add: %s", e)

    boiling_seconds = BOILING_TIMES[egg_type]
    message = f"Alarm set for {egg_type}-boiled egg, {boiling_seconds // 60} minutes"
    logger.info(message)
    return jsonify({"status": "success", "message": message, "id": alarm_id})

@routes_bp.route("/alarm/remaining", methods=["GET"])
async def get_remaining():
    try:
        alarms = await entity_service.get_items(
            token=cyoda_auth_service,
            entity_model=alarm_entity_name,
            entity_version=ENTITY_VERSION
        )
        alarm = None
        for a in alarms:
            if a.get("status") in ("running", "ringing"):
                alarm = a
                break
        if not alarm:
            return jsonify({"remaining_seconds": 0, "message": "No active alarm"})
        end_time = datetime.fromisoformat(alarm["end_time"])
        now = datetime.utcnow()
        remaining = max(0, int((end_time - now).total_seconds()))
        return jsonify({"remaining_seconds": remaining})
    except Exception as e:
        logger.exception("Failed to get remaining alarm time: %s", e)
        return jsonify({"remaining_seconds": 0, "message": "Error retrieving alarm"}), 500

@routes_bp.route("/alarm/cancel", methods=["POST"])
async def cancel_alarm():
    try:
        alarms = await entity_service.get_items(
            token=cyoda_auth_service,
            entity_model=alarm_entity_name,
            entity_version=ENTITY_VERSION
        )
        alarm = None
        for a in alarms:
            if a.get("status") in ("running", "ringing"):
                alarm = a
                break
        if not alarm:
            return jsonify({"status": "error", "message": "No active alarm to cancel"}), 400
        alarm["status"] = "cancelled"
        await entity_service.update_item(
            token=cyoda_auth_service,
            entity_model=alarm_entity_name,
            entity_version=ENTITY_VERSION,
            entity=alarm,
            technical_id=alarm["id"],
            meta={}
        )
        logger.info("Alarm cancelled by user request.")
        return jsonify({"status": "success", "message": "Alarm cancelled"})
    except Exception as e:
        logger.exception("Failed to cancel alarm: %s", e)
        return jsonify({"status": "error", "message": "Failed to cancel alarm"}), 500