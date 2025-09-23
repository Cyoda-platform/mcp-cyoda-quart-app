"""
WeatherSubscription Routes for Cyoda Client Application

Manages all WeatherSubscription-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from quart import Blueprint, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag

from application.entity.weathersubscription.version_1.weather_subscription import (
    WeatherSubscription,
)
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


weather_subscriptions_bp = Blueprint(
    "weather_subscriptions", __name__, url_prefix="/api/weather-subscriptions"
)


@weather_subscriptions_bp.route("", methods=["POST"])
@tag(["weather-subscriptions"])
@operation_id("create_weather_subscription")
async def create_weather_subscription() -> ResponseReturnValue:
    """Create a new WeatherSubscription"""
    try:
        data = await request.get_json()

        # Save the entity
        response = await service.save(
            entity=data,
            entity_class=WeatherSubscription.ENTITY_NAME,
            entity_version=str(WeatherSubscription.ENTITY_VERSION),
        )

        logger.info("Created WeatherSubscription with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201

    except Exception as e:
        logger.exception("Error creating WeatherSubscription: %s", str(e))
        return {"error": str(e)}, 500


@weather_subscriptions_bp.route("/<entity_id>", methods=["GET"])
@tag(["weather-subscriptions"])
@operation_id("get_weather_subscription")
async def get_weather_subscription(entity_id: str) -> ResponseReturnValue:
    """Get WeatherSubscription by ID"""
    try:
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=WeatherSubscription.ENTITY_NAME,
            entity_version=str(WeatherSubscription.ENTITY_VERSION),
        )

        if not response:
            return {"error": "WeatherSubscription not found"}, 404

        return _to_entity_dict(response.data), 200

    except Exception as e:
        logger.exception("Error getting WeatherSubscription %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


@weather_subscriptions_bp.route("", methods=["GET"])
@tag(["weather-subscriptions"])
@operation_id("list_weather_subscriptions")
async def list_weather_subscriptions() -> ResponseReturnValue:
    """List all WeatherSubscriptions"""
    try:
        entities = await service.find_all(
            entity_class=WeatherSubscription.ENTITY_NAME,
            entity_version=str(WeatherSubscription.ENTITY_VERSION),
        )

        entity_list = [_to_entity_dict(r.data) for r in entities]
        return {"subscriptions": entity_list, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error listing WeatherSubscriptions: %s", str(e))
        return {"error": str(e)}, 500


@weather_subscriptions_bp.route("/<entity_id>", methods=["PUT"])
@tag(["weather-subscriptions"])
@operation_id("update_weather_subscription")
async def update_weather_subscription(entity_id: str) -> ResponseReturnValue:
    """Update WeatherSubscription"""
    try:
        data = await request.get_json()
        transition = request.args.get("transition")

        response = await service.update(
            entity_id=entity_id,
            entity=data,
            entity_class=WeatherSubscription.ENTITY_NAME,
            transition=transition,
            entity_version=str(WeatherSubscription.ENTITY_VERSION),
        )

        logger.info("Updated WeatherSubscription %s", entity_id)
        return _to_entity_dict(response.data), 200

    except Exception as e:
        logger.exception("Error updating WeatherSubscription %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


@weather_subscriptions_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["weather-subscriptions"])
@operation_id("delete_weather_subscription")
async def delete_weather_subscription(entity_id: str) -> ResponseReturnValue:
    """Delete WeatherSubscription"""
    try:
        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=WeatherSubscription.ENTITY_NAME,
            entity_version=str(WeatherSubscription.ENTITY_VERSION),
        )

        logger.info("Deleted WeatherSubscription %s", entity_id)
        return {
            "success": True,
            "message": "WeatherSubscription deleted successfully",
        }, 200

    except Exception as e:
        logger.exception("Error deleting WeatherSubscription %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


@weather_subscriptions_bp.route("/user/<user_id>", methods=["GET"])
@tag(["weather-subscriptions"])
@operation_id("get_subscriptions_by_user")
async def get_subscriptions_by_user(user_id: str) -> ResponseReturnValue:
    """Get all subscriptions for a specific user"""
    try:
        from common.service.entity_service import SearchConditionRequest

        builder = SearchConditionRequest.builder()
        builder.equals("user_id", user_id)
        condition = builder.build()

        entities = await service.search(
            entity_class=WeatherSubscription.ENTITY_NAME,
            condition=condition,
            entity_version=str(WeatherSubscription.ENTITY_VERSION),
        )

        entity_list = [_to_entity_dict(r.data) for r in entities]
        return {"subscriptions": entity_list, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error getting subscriptions for user %s: %s", user_id, str(e))
        return {"error": str(e)}, 500
