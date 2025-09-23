"""
Subscriber Routes for Cat Fact Subscription Application

Manages all Subscriber-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
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

from ..entity.subscriber.version_1.subscriber import Subscriber
from ..models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    ExistsResponse,
    ResponseErrorResponse,
    SubscriberListResponse,
    SubscriberQueryParams,
    SubscriberResponse,
    SubscriberSearchRequest,
    SubscriberSearchResponse,
    SubscriberUpdateQueryParams,
    TransitionRequest,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
)

# Module-level service proxy
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)

service = _ServiceProxy()
logger = logging.getLogger(__name__)

# Helper to normalize entity data
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data

subscribers_bp = Blueprint(
    "subscribers", __name__, url_prefix="/api/subscribers"
)

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
    """Create a new Subscriber with comprehensive validation"""
    try:
        entity_data = data.model_dump(by_alias=True)

        response = await service.save(
            entity=entity_data,
            entity_class=Subscriber.ENTITY_NAME,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        logger.info("Created Subscriber with ID: %s", response.metadata.id)
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
    """Get Subscriber by ID with validation"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Subscriber.ENTITY_NAME,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Subscriber not found", "code": "NOT_FOUND"}, 404

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
    """List Subscribers with optional filtering and validation"""
    try:
        search_conditions: Dict[str, str] = {}

        if query_args.subscription_status:
            search_conditions["subscriptionStatus"] = query_args.subscription_status

        if query_args.state:
            search_conditions["state"] = query_args.state

        # Get entities
        if search_conditions:
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
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Subscriber.ENTITY_NAME,
            transition=transition,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        logger.info("Updated Subscriber %s", entity_id)
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
    """Delete Subscriber with validation"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Subscriber.ENTITY_NAME,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        logger.info("Deleted Subscriber %s", entity_id)

        response = DeleteResponse(
            success=True,
            message="Subscriber deleted successfully",
            entity_id=entity_id,
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

        response = ExistsResponse(exists=exists, entity_id=entity_id)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception("Error checking Subscriber existence %s: %s", entity_id, str(e))
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


@subscribers_bp.route("/search", methods=["POST"])
@tag(["subscribers"])
@operation_id("search_subscribers")
@validate(
    request=SubscriberSearchRequest,
    responses={
        200: (SubscriberSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_entities(data: SubscriberSearchRequest) -> ResponseReturnValue:
    """Search Subscribers using field-value search"""
    try:
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=Subscriber.ENTITY_NAME,
            condition=search_request,
            entity_version=str(Subscriber.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"entities": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching Subscribers: %s", str(e))
        return {"error": str(e)}, 500
