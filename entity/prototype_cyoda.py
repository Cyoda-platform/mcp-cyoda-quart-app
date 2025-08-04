from dataclasses import dataclass
import asyncio
import logging
from datetime import datetime, timedelta
import uuid

from quart import Quart, request, jsonify
from quart_schema import QuartSchema, validate_request, validate_querystring

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
        # TODO: Notify user about alarm completion
        logger.info(f"ALARM TRIGGERED: {alarm_id}")

    except Exception as e:
        logger.exception(f"Exception in alarm_countdown for {alarm_id}: {e}")

@app.route("/alarm/set", methods=["POST"])
@validate_request(SetAlarmRequest)
async def set_alarm(data: SetAlarmRequest):
    egg_type = data.egg_type
    if egg_type not in COOKING_TIMES:
        return jsonify({"status": "error", "message": "Invalid egg_type"}), 400

    now = datetime.utcnow()
    duration = COOKING_TIMES[egg_type]
    end_time = now + timedelta(seconds=duration)

    alarm_data = {
        "egg_type": egg_type,
        "status": "running",
        "requested_at": now.isoformat(),
        "end_time": end_time.isoformat(),
    }

    try:
        alarm_id = await entity_service.add_item(
            token=cyoda_auth_service,
            entity_model=ENTITY_NAME,
            entity_version=ENTITY_VERSION,
            entity=alarm_data
        )
    except Exception as e:
        logger.exception(e)
        return jsonify({"status": "error", "message": "Failed to add alarm"}), 500

    asyncio.create_task(alarm_countdown(alarm_id))

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
        logger.exception(e)
        return jsonify({"status": "error", "message": "Failed to retrieve alarm"}), 500

    if not alarm:
        return jsonify({"status": "error", "message": "Alarm not found"}), 404

    now = datetime.utcnow()
    if alarm.get("status") == "running":
        end_time = datetime.fromisoformat(alarm["end_time"])
        time_remaining = max(0, int((end_time - now).total_seconds()))
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
        logger.exception(e)
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
        logger.exception(e)
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