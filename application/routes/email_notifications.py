"""
EmailNotification Routes for Pet Store Performance Analysis System

Manages all EmailNotification-related API endpoints including CRUD operations
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

from common.service.entity_service import (
    SearchConditionRequest,
)
from services.services import get_entity_service

# Imported for entity constants / typing
from ..entity.email_notification import EmailNotification
from ..models import (
    CountResponse,
    DeleteResponse,
    EmailNotificationListResponse,
    EmailNotificationQueryParams,
    EmailNotificationResponse,
    EmailNotificationSearchResponse,
    EmailNotificationUpdateQueryParams,
    ErrorResponse,
    ExistsResponse,
    SearchRequest,
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


# Helper to normalize entity data from service (Pydantic model or dict)
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


email_notifications_bp = Blueprint(
    "email_notifications", __name__, url_prefix="/api/email-notifications"
)

# ---- Routes -----------------------------------------------------------------


@email_notifications_bp.route("", methods=["POST"])
@tag(["email_notifications"])
@operation_id("create_email_notification")
@validate(
    request=EmailNotification,
    responses={
        201: (EmailNotificationResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_email_notification(
    data: EmailNotification,
) -> ResponseReturnValue:
    """Create a new EmailNotification with comprehensive validation"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        logger.info("Created EmailNotification with ID: %s", response.metadata.id)

        # Return created entity directly (thin proxy)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating EmailNotification: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating EmailNotification: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@email_notifications_bp.route("/<entity_id>", methods=["GET"])
@tag(["email_notifications"])
@operation_id("get_email_notification")
@validate(
    responses={
        200: (EmailNotificationResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_email_notification(entity_id: str) -> ResponseReturnValue:
    """Get EmailNotification by ID with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        if not response:
            return {"error": "EmailNotification not found", "code": "NOT_FOUND"}, 404

        # Thin proxy: return the entity directly
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting EmailNotification %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@email_notifications_bp.route("", methods=["GET"])
@validate_querystring(EmailNotificationQueryParams)
@tag(["email_notifications"])
@operation_id("list_email_notifications")
@validate(
    responses={
        200: (EmailNotificationListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_email_notifications(
    query_args: EmailNotificationQueryParams,
) -> ResponseReturnValue:
    """List EmailNotifications with optional filtering and validation"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.recipient_email:
            search_conditions["recipientEmail"] = query_args.recipient_email

        if query_args.email_type:
            search_conditions["emailType"] = query_args.email_type

        if query_args.status:
            search_conditions["status"] = query_args.status

        if query_args.priority:
            search_conditions["priority"] = query_args.priority

        if query_args.state:
            search_conditions["state"] = query_args.state

        if query_args.report_id:
            search_conditions["reportId"] = query_args.report_id

        # Get entities
        if search_conditions:
            # Build search condition request
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=EmailNotification.ENTITY_NAME,
                condition=condition,
                entity_version=str(EmailNotification.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=EmailNotification.ENTITY_NAME,
                entity_version=str(EmailNotification.ENTITY_VERSION),
            )

        # Thin proxy: return entities directly
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"entities": paginated_entities, "total": len(entity_list)}), 200

    except Exception as e:
        logger.exception("Error listing EmailNotifications: %s", str(e))
        return jsonify({"error": str(e)}), 500


@email_notifications_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(EmailNotificationUpdateQueryParams)
@tag(["email_notifications"])
@operation_id("update_email_notification")
@validate(
    request=EmailNotification,
    responses={
        200: (EmailNotificationResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_email_notification(
    entity_id: str,
    data: EmailNotification,
    query_args: EmailNotificationUpdateQueryParams,
) -> ResponseReturnValue:
    """Update EmailNotification and optionally trigger workflow transition with validation"""
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
            entity_class=EmailNotification.ENTITY_NAME,
            transition=transition,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        logger.info("Updated EmailNotification %s", entity_id)

        # Return updated entity directly (thin proxy)
        return jsonify(_to_entity_dict(response.data)), 200

    except ValueError as e:
        logger.warning(
            "Validation error updating EmailNotification %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error updating EmailNotification %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@email_notifications_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["email_notifications"])
@operation_id("delete_email_notification")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_email_notification(entity_id: str) -> ResponseReturnValue:
    """Delete EmailNotification with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        logger.info("Deleted EmailNotification %s", entity_id)

        # Thin proxy: return success message
        response = DeleteResponse(
            success=True,
            message="EmailNotification deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting EmailNotification %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


# ---- Additional Entity Service Endpoints ----------------------------------------


@email_notifications_bp.route("/by-business-id/<business_id>", methods=["GET"])
@tag(["email_notifications"])
@operation_id("get_email_notification_by_business_id")
@validate(
    responses={
        200: (EmailNotificationResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_by_business_id(business_id: str) -> ResponseReturnValue:
    """Get EmailNotification by business ID (subject field by default)"""
    try:
        business_id_field = request.args.get(
            "field", "subject"
        )  # Default to subject field

        result = await service.find_by_business_id(
            entity_class=EmailNotification.ENTITY_NAME,
            business_id=business_id,
            business_id_field=business_id_field,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        if not result:
            return jsonify({"error": "EmailNotification not found"}), 404

        # Thin proxy: return the entity directly
        return jsonify(_to_entity_dict(result.data)), 200

    except Exception as e:
        logger.exception(
            "Error getting EmailNotification by business ID %s: %s", business_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


@email_notifications_bp.route("/<entity_id>/exists", methods=["GET"])
@tag(["email_notifications"])
@operation_id("check_email_notification_exists")
@validate(responses={200: (ExistsResponse, None), 500: (ErrorResponse, None)})
async def check_exists(entity_id: str) -> ResponseReturnValue:
    """Check if EmailNotification exists by ID"""
    try:
        exists = await service.exists_by_id(
            entity_id=entity_id,
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        response = ExistsResponse(exists=exists, entity_id=entity_id)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception(
            "Error checking EmailNotification existence %s: %s", entity_id, str(e)
        )
        return {"error": str(e)}, 500


@email_notifications_bp.route("/count", methods=["GET"])
@tag(["email_notifications"])
@operation_id("count_email_notifications")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_entities() -> ResponseReturnValue:
    """Count total number of EmailNotifications"""
    try:
        count = await service.count(
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        response = CountResponse(count=count)
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception("Error counting EmailNotifications: %s", str(e))
        return jsonify({"error": str(e)}), 500


@email_notifications_bp.route("/<entity_id>/transitions", methods=["GET"])
@tag(["email_notifications"])
@operation_id("get_email_notification_transitions")
@validate(
    responses={
        200: (TransitionsResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_available_transitions(entity_id: str) -> ResponseReturnValue:
    """Get available workflow transitions for EmailNotification"""
    try:
        transitions = await service.get_transitions(
            entity_id=entity_id,
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        response = TransitionsResponse(
            entity_id=entity_id,
            available_transitions=transitions,
            current_state=None,  # Could be enhanced to get current state
        )
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception(
            "Error getting transitions for EmailNotification %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


# ---- Search Endpoints -----------------------------------------------------------


@email_notifications_bp.route("/search", methods=["POST"])
@tag(["email_notifications"])
@operation_id("search_email_notifications")
@validate(
    request=SearchRequest,
    responses={
        200: (EmailNotificationSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_entities(data: SearchRequest) -> ResponseReturnValue:
    """Search EmailNotifications using simple field-value search with validation"""
    try:
        # Convert Pydantic model to dict for search
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        # KISS: Simple field-value search only
        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=EmailNotification.ENTITY_NAME,
            condition=search_request,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        # Thin proxy: return list of entities directly
        entities = [_to_entity_dict(r.data) for r in results]

        return {"entities": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching EmailNotifications: %s", str(e))
        return {"error": str(e)}, 500


@email_notifications_bp.route("/find-all", methods=["GET"])
@tag(["email_notifications"])
@operation_id("find_all_email_notifications")
@validate(
    responses={200: (EmailNotificationListResponse, None), 500: (ErrorResponse, None)}
)
async def find_all_entities() -> ResponseReturnValue:
    """Find all EmailNotifications without filtering"""
    try:
        results = await service.find_all(
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"entities": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error finding all EmailNotifications: %s", str(e))
        return {"error": str(e)}, 500


@email_notifications_bp.route("/<entity_id>/transitions", methods=["POST"])
@tag(["email_notifications"])
@operation_id("trigger_email_notification_transition")
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
    """Trigger a specific workflow transition with validation"""
    try:
        # Get current entity state
        current_entity = await service.get_by_id(
            entity_id=entity_id,
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        if not current_entity:
            return jsonify({"error": "EmailNotification not found"}), 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        logger.info(
            "Executed transition '%s' on EmailNotification %s",
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
            "Error executing transition on EmailNotification %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500
