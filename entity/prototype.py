```python
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx
from quart import Quart, jsonify, request
from quart_schema import QuartSchema

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Quart(__name__)
QuartSchema(app)

# Constants for boiling times in seconds
BOILING_TIMES = {
    "soft": 4 * 60,
    "medium": 7 * 60,
    "hard": 10 * 60,
}

# In-memory cache to simulate persistence; keys: "alarm"
# alarm structure:
# {
#   "egg_type": str,
#   "end_time": datetime,
#   "status": str,  # "running", "ringing", "cancelled", "stopped"
# }
cache = {}

# A lock to synchronize cache access in async context
lock = asyncio.Lock()


async def alarm_countdown(egg_type: str, end_time: datetime):
    try:
        while True:
            now = datetime.utcnow()
            remaining = (end_time - now).total_seconds()
            if remaining <= 0:
                async with lock:
                    alarm = cache.get("alarm")
                    if alarm and alarm["egg_type"] == egg_type and alarm["status"] == "running":
                        alarm["status"] = "ringing"
                logger.info(f"Alarm for {egg_type} egg is ringing now.")
                # TODO: Could integrate with external notification APIs here if needed.
                # For prototype, just mark as ringing and stop.
                await asyncio.sleep(5)  # simulate ringing duration
                async with lock:
                    alarm = cache.get("alarm")
                    if alarm and alarm["egg_type"] == egg_type and alarm["status"] == "ringing":
                        alarm["status"] = "stopped"
                        logger.info(f"Alarm for {egg_type} egg stopped automatically after ringing.")
                break
            await asyncio.sleep(min(remaining, 1))
    except Exception as e:
        logger.exception("Exception in alarm countdown: %s", e)
        async with lock:
            alarm = cache.get("alarm")
            if alarm and alarm["egg_type"] == egg_type:
                alarm["status"] = "stopped"


@app.route("/alarm/set", methods=["POST"])
async def set_alarm():
    data = await request.get_json(force=True)
    egg_type = data.get("egg_type")
    if egg_type not in BOILING_TIMES:
        return jsonify({"status": "error", "message": "Invalid egg_type"}), 400

    boiling_seconds = BOILING_TIMES[egg_type]
    end_time = datetime.utcnow() + timedelta(seconds=boiling_seconds)
    async with lock:
        # Cancel existing alarm if any
        if "alarm" in cache and cache["alarm"]["status"] in ("running", "ringing"):
            cache["alarm"]["status"] = "cancelled"
        # Set new alarm
        cache["alarm"] = {
            "egg_type": egg_type,
            "end_time": end_time,
            "status": "running",
            "set_at": datetime.utcnow(),
        }

    # Fire and forget countdown task
    asyncio.create_task(alarm_countdown(egg_type, end_time))

    message = f"Alarm set for {egg_type}-boiled egg, {boiling_seconds // 60} minutes"
    logger.info(message)
    return jsonify({"status": "success", "message": message})


@app.route("/alarm/remaining", methods=["GET"])
async def get_remaining():
    async with lock:
        alarm = cache.get("alarm")

    if not alarm or alarm["status"] not in ("running", "ringing"):
        return jsonify({"remaining_seconds": 0, "message": "No active alarm"})

    now = datetime.utcnow()
    remaining = max(0, int((alarm["end_time"] - now).total_seconds()))

    return jsonify({"remaining_seconds": remaining})


@app.route("/alarm/cancel", methods=["POST"])
async def cancel_alarm():
    async with lock:
        alarm = cache.get("alarm")
        if not alarm or alarm["status"] not in ("running", "ringing"):
            return jsonify({"status": "error", "message": "No active alarm to cancel"}), 400
        alarm["status"] = "cancelled"

    logger.info("Alarm cancelled by user request.")
    return jsonify({"status": "success", "message": "Alarm cancelled"})


if __name__ == "__main__":
    app.run(use_reloader=False, debug=True, host="0.0.0.0", port=8000, threaded=True)
```
