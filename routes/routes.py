 from dataclasses import dataclass
import asyncio
import logging
from datetime import datetime, timedelta
import uuid

from quart import Quart, jsonify
from quart_schema import QuartSchema, validate_request

from app_init.app_init import BeanFactory
from common.config.config import ENTITY_VERSION

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

factory = BeanFactory(config={'CHAT_REPOSITORY': 'cyoda'})
entity_service = factory.get_services()['entity_service']
cyoda_auth_service = factory.get_services()["cyoda_auth_service"]

app = Quart(__name__)
QuartSchema(app)

COOKING_TIMES = {
    "soft": 4 * 60,
    "medium": 7 * 60,
    "hard": 10 * 60,
}

ENTITY_NAME = "alarm"  # entity name lowercase underscore

@dataclass
class SetAlarmRequest:
    egg_type: str

@dataclass
class CancelAlarmRequest:
    alarm_id: str

async def alarm_countdown(alarm_id: str):
    try:
        # Refresh alarm entity before waiting
        alarm = await entity_service.get_item(
            token=cyoda_auth_service,
            entity_model=ENTITY_NAME,
            entity_version=ENTITY_VERSION,
            technical_id=alarm_id
        )
        if not alarm or alarm.get("status") != "running":
            return

        now = datetime.utcnow()
        end_time = datetime.fromisoformat(alarm["end_time"])
        wait_seconds = (end_time - now).total_seconds()
        if wait_seconds > 0:
            await asyncio.sleep(wait_seconds)

        # Re-fetch alarm before update to avoid stale data issues
        alarm = await entity_service.get_item(
            token=cyoda_auth_service,
            entity_model=ENTITY_NAME,
            entity_version=ENTITY_VERSION,
            technical_id=alarm_id
        )
        if not alarm or alarm.get("status") != "running":
            return

        alarm["status"] = "finished"
        await entity_service.update_item(
            token=cyoda_auth_service,
            entity_model=ENTITY_NAME,
            entity_version=ENTITY_VERSION,
            entity=alarm,
            technical_id=alarm_id,
            meta={}
        )
        logger.info(f"Alarm {alarm_id} finished for egg type {alarm['egg_type']}")
        logger.info(f"ALARM TRIGGERED: {alarm_id}")

    except Exception as e:
        logger.exception(f"Exception in alarm_countdown for {alarm_id}: {e}")

async def process_alarm(entity: dict):
    """
    Workflow function applied to the alarm entity asynchronously before persistence.
    Validates and sets all alarm properties.
    Starts countdown task asynchronously.
    """
    # Assign a unique id if not present
    if "id" not in entity or not entity["id"]:
        entity["id"] = str(uuid.uuid4())

    # Validate egg_type presence and correctness
    egg_type = entity.get("egg_type")
    if not isinstance(egg_type, str) or egg_type not in COOKING_TIMES:
        raise ValueError(f"Invalid egg_type '{egg_type}'")

    now = datetime.utcnow()
    duration = COOKING_TIMES[egg_type]
    entity["status"] = "running"
    entity["requested_at"] = now.isoformat()
    entity["end_time"] = (now + timedelta(seconds=duration)).isoformat()

    # Spawn the countdown async task to handle finishing alarm after time expires
    # Fire and forget
    asyncio.create_task(alarm_countdown(entity["id"]))

    return entity

async def process_cancel_alarm(entity: dict):
    """
    Workflow function for cancelling alarm.
    This function is not used in this app but shown as example if update_item supported workflow.
    """
    status = entity.get("status")
    if status in ("finished", "cancelled"):
        raise ValueError(f"Alarm already {status}")
    entity["status"] = "cancelled"
    return entity

@app.route("/alarm/set", methods=["POST"])
@validate_request(SetAlarmRequest)
async def set_alarm(data: SetAlarmRequest):
    try:
        alarm_id = await entity_service.add_item(
            token=cyoda_auth_service,
            entity_model=ENTITY_NAME,
            entity_version=ENTITY_VERSION,
            entity={"egg_type": data.egg_type}
        )
    except ValueError as ve:
        # Raised inside process_alarm for invalid egg_type
        return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as e:
        logger.exception("Failed to add alarm")
        return jsonify({"status": "error", "message": "Failed to add alarm"}), 500

    duration = COOKING_TIMES.get(data.egg_type, 0)
    return jsonify({
        "status": "success",
        "alarm_id": alarm_id,
        "time_to_alarm_seconds": duration,
    })

@app.route("/alarm/status/<string:alarm_id>", methods=["GET"])
async def get_alarm_status(alarm_id: str):
    try:
        alarm = await entity_service.get_item(
            token=cyoda_auth_service,
            entity_model=ENTITY_NAME,
            entity_version=ENTITY_VERSION,
            technical_id=alarm_id
        )
    except Exception as e:
        logger.exception(f"Failed to retrieve alarm {alarm_id}")
        return jsonify({"status": "error", "message": "Failed to retrieve alarm"}), 500

    if not alarm:
        return jsonify({"status": "error", "message": "Alarm not found"}), 404

    now = datetime.utcnow()
    if alarm.get("status") == "running":
        try:
            end_time = datetime.fromisoformat(alarm["end_time"])
            time_remaining = max(0, int((end_time - now).total_seconds()))
        except Exception:
            time_remaining = 0
    else:
        time_remaining = 0

    return jsonify({
        "alarm_id": alarm_id,
        "egg_type": alarm.get("egg_type"),
        "time_remaining_seconds": time_remaining,
        "status": alarm.get("status"),
    })

@app.route("/alarm/cancel", methods=["POST"])
@validate_request(CancelAlarmRequest)
async def cancel_alarm(data: CancelAlarmRequest):
    alarm_id = data.alarm_id
    try:
        alarm = await entity_service.get_item(
            token=cyoda_auth_service,
            entity_model=ENTITY_NAME,
            entity_version=ENTITY_VERSION,
            technical_id=alarm_id
        )
    except Exception as e:
        logger.exception(f"Failed to retrieve alarm {alarm_id} for cancel")
        return jsonify({"status": "error", "message": "Failed to retrieve alarm"}), 500

    if not alarm:
        return jsonify({"status": "error", "message": "Alarm not found"}), 404

    if alarm.get("status") in ("finished", "cancelled"):
        return jsonify({"status": "error", "message": f"Alarm already {alarm['status']}"}), 400

    alarm["status"] = "cancelled"

    try:
        await entity_service.update_item(
            token=cyoda_auth_service,
            entity_model=ENTITY_NAME,
            entity_version=ENTITY_VERSION,
            entity=alarm,
            technical_id=alarm_id,
            meta={}
        )
    except Exception as e:
        logger.exception(f"Failed to cancel alarm {alarm_id}")
        return jsonify({"status": "error", "message": "Failed to cancel alarm"}), 500

    logger.info(f"Alarm {alarm_id} cancelled by user")

    return jsonify({
        "status": "success",
        "message": "Alarm cancelled"
    })

if __name__ == '__main__':
    import sys
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    app.run(use_reloader=False, debug=True, host='0.0.0.0', port=8000, threaded=True)
