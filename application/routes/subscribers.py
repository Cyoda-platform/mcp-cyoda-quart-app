"""
Subscriber Routes for Cat Fact Subscription Application

Manages all Subscriber-related API endpoints including CRUD operations
and workflow transitions.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from quart import Blueprint, jsonify
from quart.typing import ResponseReturnValue
from quart_schema import (
    operation_id,
    tag,
    validate,
    validate_querystring,
)

from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

from ..entity.subscriber.version_1.subscriber import Subscriber
from ..models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    SearchRequest,
    SubscriberListResponse,
    SubscriberQueryParams,
    SubscriberResponse,
    SubscriberSearchResponse,
    SubscriberUpdateQueryParams,
    TransitionRequest,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
)


# Module-level service instance to avoid repeated lookups
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()

logger = logging.getLogger(__name__)


# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


subscribers_bp = Blueprint("subscribers", __name__, url_prefix="/api/subscribers")


@subscribers_bp.route("", methods=["POST"])
@tag(["subscribers"])
@operation_id("create_subscriber")
@validate(
    request=Subscriber,
    responses={
        201: (SubscriberResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_subscriber(data: Subscriber) -> ResponseReturnValue:
    """Create a new Subscriber"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=Subscriber.ENTITY_NAME,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        logger.info("Created Subscriber with ID: %s", response.metadata.id)

        # Return created entity directly (thin proxy)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating Subscriber: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Subscriber: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@subscribers_bp.route("/<entity_id>", methods=["GET"])
@tag(["subscribers"])
@operation_id("get_subscriber")
@validate(
    responses={
        200: (SubscriberResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_subscriber(entity_id: str) -> ResponseReturnValue:
    """Get Subscriber by ID"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Subscriber.ENTITY_NAME,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Subscriber not found", "code": "NOT_FOUND"}, 404

        # Thin proxy: return the entity directly
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting Subscriber %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@subscribers_bp.route("", methods=["GET"])
@validate_querystring(SubscriberQueryParams)
@tag(["subscribers"])
@operation_id("list_subscribers")
@validate(
    responses={
        200: (SubscriberListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_subscribers(query_args: SubscriberQueryParams) -> ResponseReturnValue:
    """List Subscribers with optional filtering"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.is_active is not None:
            search_conditions["isActive"] = str(query_args.is_active).lower()

        if query_args.state:
            search_conditions["state"] = query_args.state

        if query_args.subscription_source:
            search_conditions["subscriptionSource"] = query_args.subscription_source

        # Get entities
        if search_conditions:
            # Build search condition request
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=Subscriber.ENTITY_NAME,
                condition=condition,
                entity_version=str(Subscriber.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=Subscriber.ENTITY_NAME,
                entity_version=str(Subscriber.ENTITY_VERSION),
            )

        # Thin proxy: return entities directly
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"entities": paginated_entities, "total": len(entity_list)}), 200

    except Exception as e:
        logger.exception("Error listing Subscribers: %s", str(e))
        return jsonify({"error": str(e)}), 500


@subscribers_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(SubscriberUpdateQueryParams)
@tag(["subscribers"])
@operation_id("update_subscriber")
@validate(
    request=Subscriber,
    responses={
        200: (SubscriberResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_subscriber(
    entity_id: str, data: Subscriber, query_args: SubscriberUpdateQueryParams
) -> ResponseReturnValue:
    """Update Subscriber and optionally trigger workflow transition"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        # Get transition from query parameters
        transition: Optional[str] = query_args.transition

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        # Update the entity
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Subscriber.ENTITY_NAME,
            transition=transition,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        logger.info("Updated Subscriber %s", entity_id)

        # Return updated entity directly (thin proxy)
        return jsonify(_to_entity_dict(response.data)), 200

    except ValueError as e:
        logger.warning("Validation error updating Subscriber %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error updating Subscriber %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@subscribers_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["subscribers"])
@operation_id("delete_subscriber")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_subscriber(entity_id: str) -> ResponseReturnValue:
    """Delete Subscriber"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Subscriber.ENTITY_NAME,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        logger.info("Deleted Subscriber %s", entity_id)

        # Thin proxy: return success message
        response = DeleteResponse(
            success=True,
            message="Subscriber deleted successfully",
            entityId=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting Subscriber %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@subscribers_bp.route("/by-email/<email>", methods=["GET"])
@tag(["subscribers"])
@operation_id("get_subscriber_by_email")
@validate(
    responses={
        200: (SubscriberResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_by_email(email: str) -> ResponseReturnValue:
    """Get Subscriber by email address"""
    try:
        result = await service.find_by_business_id(
            entity_class=Subscriber.ENTITY_NAME,
            business_id=email,
            business_id_field="email",
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        if not result:
            return jsonify({"error": "Subscriber not found"}), 404

        # Thin proxy: return the entity directly
        return jsonify(_to_entity_dict(result.data)), 200

    except Exception as e:
        logger.exception("Error getting Subscriber by email %s: %s", email, str(e))
        return jsonify({"error": str(e)}), 500


@subscribers_bp.route("/<entity_id>/exists", methods=["GET"])
@tag(["subscribers"])
@operation_id("check_subscriber_exists")
@validate(responses={200: (ExistsResponse, None), 500: (ErrorResponse, None)})
async def check_exists(entity_id: str) -> ResponseReturnValue:
    """Check if Subscriber exists by ID"""
    try:
        exists = await service.exists_by_id(
            entity_id=entity_id,
            entity_class=Subscriber.ENTITY_NAME,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        response = ExistsResponse(exists=exists, entityId=entity_id)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception(
            "Error checking Subscriber existence %s: %s", entity_id, str(e)
        )
        return {"error": str(e)}, 500


@subscribers_bp.route("/count", methods=["GET"])
@tag(["subscribers"])
@operation_id("count_subscribers")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_entities() -> ResponseReturnValue:
    """Count total number of Subscribers"""
    try:
        count = await service.count(
            entity_class=Subscriber.ENTITY_NAME,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        response = CountResponse(count=count)
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception("Error counting Subscribers: %s", str(e))
        return jsonify({"error": str(e)}), 500


@subscribers_bp.route("/<entity_id>/transitions", methods=["GET"])
@tag(["subscribers"])
@operation_id("get_subscriber_transitions")
@validate(
    responses={
        200: (TransitionsResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_available_transitions(entity_id: str) -> ResponseReturnValue:
    """Get available workflow transitions for Subscriber"""
    try:
        transitions = await service.get_transitions(
            entity_id=entity_id,
            entity_class=Subscriber.ENTITY_NAME,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        response = TransitionsResponse(
            entityId=entity_id,
            availableTransitions=transitions,
            currentState=None,
        )
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception(
            "Error getting transitions for Subscriber %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


@subscribers_bp.route("/search", methods=["POST"])
@tag(["subscribers"])
@operation_id("search_subscribers")
@validate(
    request=SearchRequest,
    responses={
        200: (SubscriberSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_entities(data: SearchRequest) -> ResponseReturnValue:
    """Search Subscribers using simple field-value search"""
    try:
        # Convert Pydantic model to dict for search
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        # Simple field-value search only
        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=Subscriber.ENTITY_NAME,
            condition=search_request,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        # Thin proxy: return list of entities directly
        entities = [_to_entity_dict(r.data) for r in results]

        return {"entities": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching Subscribers: %s", str(e))
        return {"error": str(e)}, 500


@subscribers_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["subscribers"])
@operation_id("trigger_subscriber_transition")
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
            entity_class=Subscriber.ENTITY_NAME,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        if not current_entity:
            return jsonify({"error": "Subscriber not found"}), 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=Subscriber.ENTITY_NAME,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        logger.info(
            "Executed transition '%s' on Subscriber %s",
            data.transition_name,
            entity_id,
        )

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "message": "Transition executed successfully",
                    "previousState": previous_state,
                    "newState": response.metadata.state,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception(
            "Error executing transition on Subscriber %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500
