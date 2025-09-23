"""
WeatherStation Routes for Weather Data Application

Manages all WeatherStation-related API endpoints including CRUD operations
and workflow transitions.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from quart import Blueprint
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
async def list_weather_stations(
    query_args: WeatherStationQueryParams,
) -> ResponseReturnValue:
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
        logger.warning(
            "Validation error updating WeatherStation %s: %s", entity_id, str(e)
        )
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


# Additional endpoints


@weather_stations_bp.route("/by-station-id/<station_id>", methods=["GET"])
@tag(["weather-stations"])
@operation_id("get_weather_station_by_station_id")
@validate(
    responses={
        200: (WeatherStationResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_by_station_id(station_id: str) -> ResponseReturnValue:
    """Get WeatherStation by station ID"""
    try:
        result = await service.find_by_business_id(
            entity_class=WeatherStation.ENTITY_NAME,
            business_id=station_id,
            business_id_field="station_id",
            entity_version=str(WeatherStation.ENTITY_VERSION),
        )

        if not result:
            return {"error": "WeatherStation not found"}, 404

        return _to_entity_dict(result.data), 200

    except Exception as e:
        logger.exception(
            "Error getting WeatherStation by station ID %s: %s", station_id, str(e)
        )
        return {"error": str(e)}, 500


@weather_stations_bp.route("/<entity_id>/exists", methods=["GET"])
@tag(["weather-stations"])
@operation_id("check_weather_station_exists")
@validate(responses={200: (ExistsResponse, None), 500: (ErrorResponse, None)})
async def check_exists(entity_id: str) -> ResponseReturnValue:
    """Check if WeatherStation exists by ID"""
    try:
        exists = await service.exists_by_id(
            entity_id=entity_id,
            entity_class=WeatherStation.ENTITY_NAME,
            entity_version=str(WeatherStation.ENTITY_VERSION),
        )

        response = ExistsResponse(exists=exists, entity_id=entity_id)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception(
            "Error checking WeatherStation existence %s: %s", entity_id, str(e)
        )
        return {"error": str(e)}, 500


@weather_stations_bp.route("/count", methods=["GET"])
@tag(["weather-stations"])
@operation_id("count_weather_stations")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_entities() -> ResponseReturnValue:
    """Count total number of WeatherStations"""
    try:
        count = await service.count(
            entity_class=WeatherStation.ENTITY_NAME,
            entity_version=str(WeatherStation.ENTITY_VERSION),
        )

        response = CountResponse(count=count)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception("Error counting WeatherStations: %s", str(e))
        return {"error": str(e)}, 500


@weather_stations_bp.route("/<entity_id>/transitions", methods=["GET"])
@tag(["weather-stations"])
@operation_id("get_weather_station_transitions")
@validate(
    responses={
        200: (TransitionsResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_available_transitions(entity_id: str) -> ResponseReturnValue:
    """Get available workflow transitions for WeatherStation"""
    try:
        transitions = await service.get_transitions(
            entity_id=entity_id,
            entity_class=WeatherStation.ENTITY_NAME,
            entity_version=str(WeatherStation.ENTITY_VERSION),
        )

        response = TransitionsResponse(
            entity_id=entity_id,
            available_transitions=transitions,
            current_state=None,
        )
        return response.model_dump(), 200

    except Exception as e:
        logger.exception(
            "Error getting transitions for WeatherStation %s: %s", entity_id, str(e)
        )
        return {"error": str(e)}, 500


@weather_stations_bp.route("/search", methods=["POST"])
@tag(["weather-stations"])
@operation_id("search_weather_stations")
@validate(
    request=WeatherSearchRequest,
    responses={
        200: (WeatherStationListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_entities(data: WeatherSearchRequest) -> ResponseReturnValue:
    """Search WeatherStations using field-value search"""
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
            entity_class=WeatherStation.ENTITY_NAME,
            condition=search_request,
            entity_version=str(WeatherStation.ENTITY_VERSION),
        )

        # Return list of entities
        entities = [_to_entity_dict(r.data) for r in results]

        return {"stations": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching WeatherStations: %s", str(e))
        return {"error": str(e)}, 500


@weather_stations_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["weather-stations"])
@operation_id("trigger_weather_station_transition")
@validate(
    request=TransitionRequest,
    responses={
        200: (TransitionResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def trigger_transition(
    entity_id: str, data: TransitionRequest
) -> ResponseReturnValue:
    """Trigger a specific workflow transition"""
    try:
        # Get current entity state
        current_entity = await service.get_by_id(
            entity_id=entity_id,
            entity_class=WeatherStation.ENTITY_NAME,
            entity_version=str(WeatherStation.ENTITY_VERSION),
        )

        if not current_entity:
            return {"error": "WeatherStation not found"}, 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=WeatherStation.ENTITY_NAME,
            entity_version=str(WeatherStation.ENTITY_VERSION),
        )

        logger.info(
            "Executed transition '%s' on WeatherStation %s",
            data.transition_name,
            entity_id,
        )

        return {
            "id": response.metadata.id,
            "message": "Transition executed successfully",
            "previous_state": previous_state,
            "new_state": response.metadata.state,
        }, 200

    except Exception as e:
        logger.exception(
            "Error executing transition on WeatherStation %s: %s", entity_id, str(e)
        )
        return {"error": str(e)}, 500
