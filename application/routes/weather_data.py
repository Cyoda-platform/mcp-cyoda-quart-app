"""
WeatherData Routes for Weather Data Application

Manages all WeatherData-related API endpoints including CRUD operations
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
from ..entity.weather_data.version_1.weather_data import WeatherData
from ..models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    TransitionRequest,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
    WeatherDataListResponse,
    WeatherDataQueryParams,
    WeatherDataResponse,
    WeatherDataUpdateQueryParams,
    WeatherSearchRequest,
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

weather_data_bp = Blueprint(
    "weather_data", __name__, url_prefix="/api/weather-data"
)


@weather_data_bp.route("", methods=["POST"])
@tag(["weather-data"])
@operation_id("create_weather_data")
@validate(
    request=WeatherData,
    responses={
        201: (WeatherDataResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_weather_data(data: WeatherData) -> ResponseReturnValue:
    """Create a new WeatherData record"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=WeatherData.ENTITY_NAME,
            entity_version=str(WeatherData.ENTITY_VERSION),
        )

        logger.info("Created WeatherData with ID: %s", response.metadata.id)

        # Return created entity
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating WeatherData: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating WeatherData: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@weather_data_bp.route("/<entity_id>", methods=["GET"])
@tag(["weather-data"])
@operation_id("get_weather_data")
@validate(
    responses={
        200: (WeatherDataResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_weather_data(entity_id: str) -> ResponseReturnValue:
    """Get WeatherData by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=WeatherData.ENTITY_NAME,
            entity_version=str(WeatherData.ENTITY_VERSION),
        )

        if not response:
            return {"error": "WeatherData not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting WeatherData %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@weather_data_bp.route("", methods=["GET"])
@validate_querystring(WeatherDataQueryParams)
@tag(["weather-data"])
@operation_id("list_weather_data")
@validate(
    responses={
        200: (WeatherDataListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_weather_data(query_args: WeatherDataQueryParams) -> ResponseReturnValue:
    """List WeatherData with optional filtering"""
    try:
        # Build search conditions
        search_conditions: Dict[str, str] = {}

        if query_args.station_id:
            search_conditions["stationId"] = query_args.station_id

        if query_args.observation_date:
            search_conditions["observationDate"] = query_args.observation_date

        if query_args.observation_type:
            search_conditions["observationType"] = query_args.observation_type

        if query_args.state:
            search_conditions["state"] = query_args.state

        # Get entities
        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=WeatherData.ENTITY_NAME,
                condition=condition,
                entity_version=str(WeatherData.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=WeatherData.ENTITY_NAME,
                entity_version=str(WeatherData.ENTITY_VERSION),
            )

        # Convert to response format
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return {"weather_data": paginated_entities, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error listing WeatherData: %s", str(e))
        return {"error": str(e)}, 500


@weather_data_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(WeatherDataUpdateQueryParams)
@tag(["weather-data"])
@operation_id("update_weather_data")
@validate(
    request=WeatherData,
    responses={
        200: (WeatherDataResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_weather_data(
    entity_id: str, data: WeatherData, query_args: WeatherDataUpdateQueryParams
) -> ResponseReturnValue:
    """Update WeatherData and optionally trigger workflow transition"""
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
            entity_class=WeatherData.ENTITY_NAME,
            transition=transition,
            entity_version=str(WeatherData.ENTITY_VERSION),
        )

        logger.info("Updated WeatherData %s", entity_id)

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Validation error updating WeatherData %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating WeatherData %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@weather_data_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["weather-data"])
@operation_id("delete_weather_data")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_weather_data(entity_id: str) -> ResponseReturnValue:
    """Delete WeatherData"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=WeatherData.ENTITY_NAME,
            entity_version=str(WeatherData.ENTITY_VERSION),
        )

        logger.info("Deleted WeatherData %s", entity_id)

        response = DeleteResponse(
            success=True,
            message="WeatherData deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting WeatherData %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
