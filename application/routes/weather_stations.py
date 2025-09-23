"""
WeatherStation Routes for Weather Data Application

Manages all WeatherStation-related API endpoints including CRUD operations
and workflow transitions.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import (
    operation_id,
    tag,
    validate,
    validate_querystring,
)

from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

# Import entity and models
from ..entity.weather_station.version_1.weather_station import WeatherStation
from ..models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    TransitionRequest,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
    WeatherSearchRequest,
    WeatherStationListResponse,
    WeatherStationQueryParams,
    WeatherStationResponse,
    WeatherStationUpdateQueryParams,
)

# Module-level service proxy
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)

service = _ServiceProxy()
logger = logging.getLogger(__name__)

# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data

weather_stations_bp = Blueprint(
    "weather_stations", __name__, url_prefix="/api/weather-stations"
)


@weather_stations_bp.route("", methods=["POST"])
@tag(["weather-stations"])
@operation_id("create_weather_station")
@validate(
    request=WeatherStation,
    responses={
        201: (WeatherStationResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_weather_station(data: WeatherStation) -> ResponseReturnValue:
    """Create a new WeatherStation"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=WeatherStation.ENTITY_NAME,
            entity_version=str(WeatherStation.ENTITY_VERSION),
        )

        logger.info("Created WeatherStation with ID: %s", response.metadata.id)

        # Return created entity
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating WeatherStation: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating WeatherStation: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@weather_stations_bp.route("/<entity_id>", methods=["GET"])
@tag(["weather-stations"])
@operation_id("get_weather_station")
@validate(
    responses={
        200: (WeatherStationResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_weather_station(entity_id: str) -> ResponseReturnValue:
    """Get WeatherStation by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=WeatherStation.ENTITY_NAME,
            entity_version=str(WeatherStation.ENTITY_VERSION),
        )

        if not response:
            return {"error": "WeatherStation not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting WeatherStation %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@weather_stations_bp.route("", methods=["GET"])
@validate_querystring(WeatherStationQueryParams)
@tag(["weather-stations"])
@operation_id("list_weather_stations")
@validate(
    responses={
        200: (WeatherStationListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_weather_stations(query_args: WeatherStationQueryParams) -> ResponseReturnValue:
    """List WeatherStations with optional filtering"""
    try:
        # Build search conditions
        search_conditions: Dict[str, str] = {}

        if query_args.province:
            search_conditions["province"] = query_args.province

        if query_args.is_active is not None:
            search_conditions["isActive"] = str(query_args.is_active).lower()

        if query_args.state:
            search_conditions["state"] = query_args.state

        # Get entities
        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=WeatherStation.ENTITY_NAME,
                condition=condition,
                entity_version=str(WeatherStation.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=WeatherStation.ENTITY_NAME,
                entity_version=str(WeatherStation.ENTITY_VERSION),
            )

        # Convert to response format
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return {"stations": paginated_entities, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error listing WeatherStations: %s", str(e))
        return {"error": str(e)}, 500


@weather_stations_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(WeatherStationUpdateQueryParams)
@tag(["weather-stations"])
@operation_id("update_weather_station")
@validate(
    request=WeatherStation,
    responses={
        200: (WeatherStationResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_weather_station(
    entity_id: str, data: WeatherStation, query_args: WeatherStationUpdateQueryParams
) -> ResponseReturnValue:
    """Update WeatherStation and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        # Get transition from query parameters
        transition: Optional[str] = query_args.transition

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        # Update the entity
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=WeatherStation.ENTITY_NAME,
            transition=transition,
            entity_version=str(WeatherStation.ENTITY_VERSION),
        )

        logger.info("Updated WeatherStation %s", entity_id)

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Validation error updating WeatherStation %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating WeatherStation %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@weather_stations_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["weather-stations"])
@operation_id("delete_weather_station")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_weather_station(entity_id: str) -> ResponseReturnValue:
    """Delete WeatherStation"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=WeatherStation.ENTITY_NAME,
            entity_version=str(WeatherStation.ENTITY_VERSION),
        )

        logger.info("Deleted WeatherStation %s", entity_id)

        response = DeleteResponse(
            success=True,
            message="WeatherStation deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting WeatherStation %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
