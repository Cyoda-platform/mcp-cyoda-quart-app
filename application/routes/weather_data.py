"""
WeatherData Routes for Cyoda Client Application

Manages all WeatherData-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from quart import Blueprint, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag

from application.entity.weatherdata.version_1.weather_data import WeatherData
from services.services import get_entity_service


# Module-level service instance to avoid repeated lookups
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()
logger = logging.getLogger(__name__)


# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


weather_data_bp = Blueprint("weather_data", __name__, url_prefix="/api/weather-data")


@weather_data_bp.route("", methods=["POST"])
@tag(["weather-data"])
@operation_id("create_weather_data")
async def create_weather_data() -> ResponseReturnValue:
    """Create new WeatherData"""
    try:
        data = await request.get_json()

        response = await service.save(
            entity=data,
            entity_class=WeatherData.ENTITY_NAME,
            entity_version=str(WeatherData.ENTITY_VERSION),
        )

        logger.info("Created WeatherData with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201

    except Exception as e:
        logger.exception("Error creating WeatherData: %s", str(e))
        return {"error": str(e)}, 500


@weather_data_bp.route("/<entity_id>", methods=["GET"])
@tag(["weather-data"])
@operation_id("get_weather_data")
async def get_weather_data(entity_id: str) -> ResponseReturnValue:
    """Get WeatherData by ID"""
    try:
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=WeatherData.ENTITY_NAME,
            entity_version=str(WeatherData.ENTITY_VERSION),
        )

        if not response:
            return {"error": "WeatherData not found"}, 404

        return _to_entity_dict(response.data), 200

    except Exception as e:
        logger.exception("Error getting WeatherData %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


@weather_data_bp.route("", methods=["GET"])
@tag(["weather-data"])
@operation_id("list_weather_data")
async def list_weather_data() -> ResponseReturnValue:
    """List all WeatherData"""
    try:
        entities = await service.find_all(
            entity_class=WeatherData.ENTITY_NAME,
            entity_version=str(WeatherData.ENTITY_VERSION),
        )

        entity_list = [_to_entity_dict(r.data) for r in entities]
        return {"weather_data": entity_list, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error listing WeatherData: %s", str(e))
        return {"error": str(e)}, 500


@weather_data_bp.route("/<entity_id>", methods=["PUT"])
@tag(["weather-data"])
@operation_id("update_weather_data")
async def update_weather_data(entity_id: str) -> ResponseReturnValue:
    """Update WeatherData"""
    try:
        data = await request.get_json()
        transition = request.args.get("transition")

        response = await service.update(
            entity_id=entity_id,
            entity=data,
            entity_class=WeatherData.ENTITY_NAME,
            transition=transition,
            entity_version=str(WeatherData.ENTITY_VERSION),
        )

        logger.info("Updated WeatherData %s", entity_id)
        return _to_entity_dict(response.data), 200

    except Exception as e:
        logger.exception("Error updating WeatherData %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


@weather_data_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["weather-data"])
@operation_id("delete_weather_data")
async def delete_weather_data(entity_id: str) -> ResponseReturnValue:
    """Delete WeatherData"""
    try:
        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=WeatherData.ENTITY_NAME,
            entity_version=str(WeatherData.ENTITY_VERSION),
        )

        logger.info("Deleted WeatherData %s", entity_id)
        return {"success": True, "message": "WeatherData deleted successfully"}, 200

    except Exception as e:
        logger.exception("Error deleting WeatherData %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


@weather_data_bp.route("/subscription/<subscription_id>", methods=["GET"])
@tag(["weather-data"])
@operation_id("get_weather_data_by_subscription")
async def get_weather_data_by_subscription(subscription_id: str) -> ResponseReturnValue:
    """Get all weather data for a specific subscription"""
    try:
        from common.service.entity_service import SearchConditionRequest

        builder = SearchConditionRequest.builder()
        builder.equals("subscription_id", subscription_id)
        condition = builder.build()

        entities = await service.search(
            entity_class=WeatherData.ENTITY_NAME,
            condition=condition,
            entity_version=str(WeatherData.ENTITY_VERSION),
        )

        entity_list = [_to_entity_dict(r.data) for r in entities]
        return {"weather_data": entity_list, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception(
            "Error getting weather data for subscription %s: %s",
            subscription_id,
            str(e),
        )
        return {"error": str(e)}, 500
