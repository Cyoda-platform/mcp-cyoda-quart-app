"""
Booking Routes for Restful Booker API Integration

Manages all Booking-related API endpoints including CRUD operations,
filtering, and data retrieval from Restful Booker API as specified
in functional requirements.
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
from ..entity.booking.version_1.booking import Booking
from ..models import (
    BookingListResponse,
    BookingQueryParams,
    BookingResponse,
    BookingSearchResponse,
    BookingUpdateQueryParams,
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    SearchRequest,
    TransitionRequest,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
)

logger = logging.getLogger(__name__)


# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


bookings_bp = Blueprint("bookings", __name__, url_prefix="/api/bookings")


@bookings_bp.route("", methods=["POST"])
@tag(["bookings"])
@operation_id("create_booking")
@validate(
    request=Booking,
    responses={
        201: (BookingResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_booking(data: Booking) -> ResponseReturnValue:
    """Create a new Booking entity"""
    try:
        entity_service = get_entity_service()

        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await entity_service.save(
            entity=entity_data,
            entity_class=Booking.ENTITY_NAME,
            entity_version=str(Booking.ENTITY_VERSION),
        )

        logger.info("Created Booking with ID: %s", response.metadata.id)

        # Return created entity directly (thin proxy)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating Booking: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Booking: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@bookings_bp.route("/<entity_id>", methods=["GET"])
@tag(["bookings"])
@operation_id("get_booking")
@validate(
    responses={
        200: (BookingResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_booking(entity_id: str) -> ResponseReturnValue:
    """Get Booking by ID"""
    try:
        entity_service = get_entity_service()

        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await entity_service.get_by_id(
            entity_id=entity_id,
            entity_class=Booking.ENTITY_NAME,
            entity_version=str(Booking.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Booking not found", "code": "NOT_FOUND"}, 404

        # Thin proxy: return the entity directly
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting Booking %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@bookings_bp.route("", methods=["GET"])
@validate_querystring(BookingQueryParams)
@tag(["bookings"])
@operation_id("list_bookings")
@validate(
    responses={
        200: (BookingListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_bookings(query_args: BookingQueryParams) -> ResponseReturnValue:
    """List Bookings with optional filtering"""
    try:
        entity_service = get_entity_service()

        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.firstname:
            search_conditions["firstname"] = query_args.firstname

        if query_args.lastname:
            search_conditions["lastname"] = query_args.lastname

        if query_args.depositpaid is not None:
            search_conditions["depositpaid"] = str(query_args.depositpaid).lower()

        if query_args.state:
            search_conditions["state"] = query_args.state

        # Get entities
        if search_conditions:
            # Build search condition request
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await entity_service.search(
                entity_class=Booking.ENTITY_NAME,
                condition=condition,
                entity_version=str(Booking.ENTITY_VERSION),
            )
        else:
            entities = await entity_service.find_all(
                entity_class=Booking.ENTITY_NAME,
                entity_version=str(Booking.ENTITY_VERSION),
            )

        # Convert to list and apply additional filters
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply price and date filters (not supported by search conditions)
        if (
            query_args.min_price is not None
            or query_args.max_price is not None
            or query_args.start_date
            or query_args.end_date
        ):
            filtered_list = []
            for entity_data in entity_list:
                try:
                    booking = Booking(**entity_data)
                    filter_criteria = {}

                    if query_args.min_price is not None:
                        filter_criteria["min_price"] = query_args.min_price
                    if query_args.max_price is not None:
                        filter_criteria["max_price"] = query_args.max_price
                    if query_args.start_date:
                        filter_criteria["start_date"] = query_args.start_date
                    if query_args.end_date:
                        filter_criteria["end_date"] = query_args.end_date

                    if booking.matches_filter_criteria(**filter_criteria):
                        filtered_list.append(entity_data)
                except Exception as e:
                    logger.warning(f"Error filtering booking: {str(e)}")
                    continue
            entity_list = filtered_list

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"entities": paginated_entities, "total": len(entity_list)}), 200

    except Exception as e:
        logger.exception("Error listing Bookings: %s", str(e))
        return jsonify({"error": str(e)}), 500


@bookings_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(BookingUpdateQueryParams)
@tag(["bookings"])
@operation_id("update_booking")
@validate(
    request=Booking,
    responses={
        200: (BookingResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_booking(
    entity_id: str, data: Booking, query_args: BookingUpdateQueryParams
) -> ResponseReturnValue:
    """Update Booking and optionally trigger workflow transition"""
    try:
        entity_service = get_entity_service()

        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        # Get transition from query parameters
        transition: Optional[str] = query_args.transition

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        # Update the entity
        response = await entity_service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Booking.ENTITY_NAME,
            transition=transition,
            entity_version=str(Booking.ENTITY_VERSION),
        )

        logger.info("Updated Booking %s", entity_id)

        # Return updated entity directly (thin proxy)
        return jsonify(_to_entity_dict(response.data)), 200

    except ValueError as e:
        logger.warning("Validation error updating Booking %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error updating Booking %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@bookings_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["bookings"])
@operation_id("delete_booking")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_booking(entity_id: str) -> ResponseReturnValue:
    """Delete Booking"""
    try:
        entity_service = get_entity_service()

        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await entity_service.delete_by_id(
            entity_id=entity_id,
            entity_class=Booking.ENTITY_NAME,
            entity_version=str(Booking.ENTITY_VERSION),
        )

        logger.info("Deleted Booking %s", entity_id)

        # Thin proxy: return success message
        response = DeleteResponse(
            success=True,
            message="Booking deleted successfully",
            entityId=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting Booking %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


# Additional endpoints for booking operations


@bookings_bp.route("/search", methods=["POST"])
@tag(["bookings"])
@operation_id("search_bookings")
@validate(
    request=SearchRequest,
    responses={
        200: (BookingSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_bookings(data: SearchRequest) -> ResponseReturnValue:
    """Search Bookings using field-value search"""
    try:
        entity_service = get_entity_service()

        # Convert Pydantic model to dict for search
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        # Simple field-value search
        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await entity_service.search(
            entity_class=Booking.ENTITY_NAME,
            condition=search_request,
            entity_version=str(Booking.ENTITY_VERSION),
        )

        # Thin proxy: return list of entities directly
        entities = [_to_entity_dict(r.data) for r in results]

        return {"entities": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching Bookings: %s", str(e))
        return {"error": str(e)}, 500


@bookings_bp.route("/count", methods=["GET"])
@tag(["bookings"])
@operation_id("count_bookings")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_bookings() -> ResponseReturnValue:
    """Count total number of Bookings"""
    try:
        entity_service = get_entity_service()

        count = await entity_service.count(
            entity_class=Booking.ENTITY_NAME,
            entity_version=str(Booking.ENTITY_VERSION),
        )

        response = CountResponse(count=count, entityType="Booking")
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception("Error counting Bookings: %s", str(e))
        return jsonify({"error": str(e)}), 500


@bookings_bp.route("/<entity_id>/exists", methods=["GET"])
@tag(["bookings"])
@operation_id("check_booking_exists")
@validate(responses={200: (ExistsResponse, None), 500: (ErrorResponse, None)})
async def check_booking_exists(entity_id: str) -> ResponseReturnValue:
    """Check if Booking exists by ID"""
    try:
        entity_service = get_entity_service()

        exists = await entity_service.exists_by_id(
            entity_id=entity_id,
            entity_class=Booking.ENTITY_NAME,
            entity_version=str(Booking.ENTITY_VERSION),
        )

        response = ExistsResponse(exists=exists, entityId=entity_id)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception("Error checking Booking existence %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


@bookings_bp.route("/<entity_id>/transitions", methods=["GET"])
@tag(["bookings"])
@operation_id("get_booking_transitions")
@validate(
    responses={
        200: (TransitionsResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_booking_transitions(entity_id: str) -> ResponseReturnValue:
    """Get available workflow transitions for Booking"""
    try:
        entity_service = get_entity_service()

        transitions = await entity_service.get_transitions(
            entity_id=entity_id,
            entity_class=Booking.ENTITY_NAME,
            entity_version=str(Booking.ENTITY_VERSION),
        )

        response = TransitionsResponse(
            entityId=entity_id,
            availableTransitions=transitions,
            currentState=None,  # Could be enhanced to get current state
        )
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception(
            "Error getting transitions for Booking %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


@bookings_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["bookings"])
@operation_id("trigger_booking_transition")
@validate(
    request=TransitionRequest,
    responses={
        200: (TransitionResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def trigger_booking_transition(
    entity_id: str, data: TransitionRequest
) -> ResponseReturnValue:
    """Trigger a specific workflow transition"""
    try:
        entity_service = get_entity_service()

        # Get current entity state
        current_entity = await entity_service.get_by_id(
            entity_id=entity_id,
            entity_class=Booking.ENTITY_NAME,
            entity_version=str(Booking.ENTITY_VERSION),
        )

        if not current_entity:
            return jsonify({"error": "Booking not found"}), 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await entity_service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=Booking.ENTITY_NAME,
            entity_version=str(Booking.ENTITY_VERSION),
        )

        logger.info(
            "Executed transition '%s' on Booking %s", data.transition_name, entity_id
        )

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "message": "Transition executed successfully",
                    "previousState": previous_state,
                    "newState": response.metadata.state,
                    "transitionName": data.transition_name,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception(
            "Error executing transition on Booking %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500
