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


# Additional endpoints

@weather_data_bp.route("/by-station/<station_id>", methods=["GET"])
@validate_querystring(WeatherDataQueryParams)
@tag(["weather-data"])
@operation_id("get_weather_data_by_station")
@validate(
    responses={
        200: (WeatherDataListResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_by_station(station_id: str, query_args: WeatherDataQueryParams) -> ResponseReturnValue:
    """Get WeatherData records for a specific station"""
    try:
        builder = SearchConditionRequest.builder()
        builder.equals("stationId", station_id)

        # Add additional filters if provided
        if query_args.observation_date:
            builder.equals("observationDate", query_args.observation_date)
        if query_args.observation_type:
            builder.equals("observationType", query_args.observation_type)
        if query_args.state:
            builder.equals("state", query_args.state)

        condition = builder.build()
        results = await service.search(
            entity_class=WeatherData.ENTITY_NAME,
            condition=condition,
            entity_version=str(WeatherData.ENTITY_VERSION),
        )

        # Convert to response format
        entity_list = [_to_entity_dict(r.data) for r in results]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return {"weather_data": paginated_entities, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error getting WeatherData by station %s: %s", station_id, str(e))
        return {"error": str(e)}, 500


@weather_data_bp.route("/<entity_id>/exists", methods=["GET"])
@tag(["weather-data"])
@operation_id("check_weather_data_exists")
@validate(responses={200: (ExistsResponse, None), 500: (ErrorResponse, None)})
async def check_exists(entity_id: str) -> ResponseReturnValue:
    """Check if WeatherData exists by ID"""
    try:
        exists = await service.exists_by_id(
            entity_id=entity_id,
            entity_class=WeatherData.ENTITY_NAME,
            entity_version=str(WeatherData.ENTITY_VERSION),
        )

        response = ExistsResponse(exists=exists, entity_id=entity_id)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception("Error checking WeatherData existence %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


@weather_data_bp.route("/count", methods=["GET"])
@tag(["weather-data"])
@operation_id("count_weather_data")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_entities() -> ResponseReturnValue:
    """Count total number of WeatherData records"""
    try:
        count = await service.count(
            entity_class=WeatherData.ENTITY_NAME,
            entity_version=str(WeatherData.ENTITY_VERSION),
        )

        response = CountResponse(count=count)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception("Error counting WeatherData: %s", str(e))
        return {"error": str(e)}, 500


@weather_data_bp.route("/<entity_id>/transitions", methods=["GET"])
@tag(["weather-data"])
@operation_id("get_weather_data_transitions")
@validate(
    responses={
        200: (TransitionsResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_available_transitions(entity_id: str) -> ResponseReturnValue:
    """Get available workflow transitions for WeatherData"""
    try:
        transitions = await service.get_transitions(
            entity_id=entity_id,
            entity_class=WeatherData.ENTITY_NAME,
            entity_version=str(WeatherData.ENTITY_VERSION),
        )

        response = TransitionsResponse(
            entity_id=entity_id,
            available_transitions=transitions,
            current_state=None,
        )
        return response.model_dump(), 200

    except Exception as e:
        logger.exception("Error getting transitions for WeatherData %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


@weather_data_bp.route("/search", methods=["POST"])
@tag(["weather-data"])
@operation_id("search_weather_data")
@validate(
    request=WeatherSearchRequest,
    responses={
        200: (WeatherDataListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_entities(data: WeatherSearchRequest) -> ResponseReturnValue:
    """Search WeatherData using field-value search"""
    try:
        # Convert Pydantic model to dict for search
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        # Simple field-value search
        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=WeatherData.ENTITY_NAME,
            condition=search_request,
            entity_version=str(WeatherData.ENTITY_VERSION),
        )

        # Return list of entities
        entities = [_to_entity_dict(r.data) for r in results]

        return {"weather_data": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching WeatherData: %s", str(e))
        return {"error": str(e)}, 500


@weather_data_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["weather-data"])
@operation_id("trigger_weather_data_transition")
@validate(
    request=TransitionRequest,
    responses={
        200: (TransitionResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def trigger_transition(entity_id: str, data: TransitionRequest) -> ResponseReturnValue:
    """Trigger a specific workflow transition"""
    try:
        # Get current entity state
        current_entity = await service.get_by_id(
            entity_id=entity_id,
            entity_class=WeatherData.ENTITY_NAME,
            entity_version=str(WeatherData.ENTITY_VERSION),
        )

        if not current_entity:
            return {"error": "WeatherData not found"}, 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=WeatherData.ENTITY_NAME,
            entity_version=str(WeatherData.ENTITY_VERSION),
        )

        logger.info("Executed transition '%s' on WeatherData %s", data.transition_name, entity_id)

        return {
            "id": response.metadata.id,
            "message": "Transition executed successfully",
            "previous_state": previous_state,
            "new_state": response.metadata.state,
        }, 200

    except Exception as e:
        logger.exception("Error executing transition on WeatherData %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500
