from dataclasses import dataclass
import asyncio
import logging
from datetime import datetime, timedelta
import uuid

from quart import Quart, request, jsonify
from quart_schema import QuartSchema, validate_request, validate_querystring

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Quart(__name__)
QuartSchema(app)

# In-memory cache to hold alarms: { alarm_id: {egg_type, status, end_time} }
alarms = {}

# Fixed cooking times in seconds
COOKING_TIMES = {
    "soft": 4 * 60,
    "medium": 7 * 60,
    "hard": 10 * 60,
}

@dataclass
class SetAlarmRequest:
    egg_type: str

@dataclass
class CancelAlarmRequest:
    alarm_id: str

async def alarm_countdown(alarm_id: str):
    try:
        alarm = alarms.get(alarm_id)
        if not alarm or alarm["status"] != "running":
            return

        now = datetime.utcnow()
        end_time = alarm["end_time"]
        wait_seconds = (end_time - now).total_seconds()
        if wait_seconds > 0:
            await asyncio.sleep(wait_seconds)

        alarm["status"] = "finished"
        logger.info(f"Alarm {alarm_id} finished for egg type {alarm['egg_type']}")
        # TODO: Notify user about alarm completion
        logger.info(f"ALARM TRIGGERED: {alarm_id}")

    except Exception as e:
        logger.exception(f"Exception in alarm_countdown for {alarm_id}: {e}")

@app.route("/alarm/set", methods=["POST"])
# Workaround: place validate_request last for POST due to quart-schema issue
@validate_request(SetAlarmRequest)
async def set_alarm(data: SetAlarmRequest):
    egg_type = data.egg_type
    if egg_type not in COOKING_TIMES:
        return jsonify({"status": "error", "message": "Invalid egg_type"}), 400

    alarm_id = str(uuid.uuid4())
    now = datetime.utcnow()
    duration = COOKING_TIMES[egg_type]
    end_time = now + timedelta(seconds=duration)

    alarms[alarm_id] = {
        "egg_type": egg_type,
        "status": "running",
        "requested_at": now,
        "end_time": end_time,
    }

    asyncio.create_task(alarm_countdown(alarm_id))

    return jsonify({
        "status": "success",
        "alarm_id": alarm_id,
        "time_to_alarm_seconds": duration,
    })

@app.route("/alarm/status/<alarm_id>", methods=["GET"])
async def get_alarm_status(alarm_id):
    alarm = alarms.get(alarm_id)
    if not alarm:
        return jsonify({"status": "error", "message": "Alarm not found"}), 404

    now = datetime.utcnow()
    if alarm["status"] == "running":
        time_remaining = max(0, int((alarm["end_time"] - now).total_seconds()))
    else:
        time_remaining = 0

    return jsonify({
        "alarm_id": alarm_id,
        "egg_type": alarm["egg_type"],
        "time_remaining_seconds": time_remaining,
        "status": alarm["status"],
    })

@app.route("/alarm/cancel", methods=["POST"])
# Workaround: place validate_request last for POST due to quart-schema issue
@validate_request(CancelAlarmRequest)
async def cancel_alarm(data: CancelAlarmRequest):
    alarm_id = data.alarm_id
    alarm = alarms.get(alarm_id)
    if not alarm:
        return jsonify({"status": "error", "message": "Alarm not found"}), 404

    if alarm["status"] in ("finished", "cancelled"):
        return jsonify({"status": "error", "message": f"Alarm already {alarm['status']}"}), 400

    alarm["status"] = "cancelled"
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