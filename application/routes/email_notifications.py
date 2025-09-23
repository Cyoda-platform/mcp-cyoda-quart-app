"""
EmailNotification Routes for Cyoda Client Application

Manages all EmailNotification-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from quart import Blueprint, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag

from application.entity.emailnotification.version_1.email_notification import (
    EmailNotification,
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


email_notifications_bp = Blueprint(
    "email_notifications", __name__, url_prefix="/api/email-notifications"
)


@email_notifications_bp.route("", methods=["POST"])
@tag(["email-notifications"])
@operation_id("create_email_notification")
async def create_email_notification() -> ResponseReturnValue:
    """Create new EmailNotification"""
    try:
        data = await request.get_json()

        response = await service.save(
            entity=data,
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        logger.info("Created EmailNotification with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201

    except Exception as e:
        logger.exception("Error creating EmailNotification: %s", str(e))
        return {"error": str(e)}, 500


@email_notifications_bp.route("/<entity_id>", methods=["GET"])
@tag(["email-notifications"])
@operation_id("get_email_notification")
async def get_email_notification(entity_id: str) -> ResponseReturnValue:
    """Get EmailNotification by ID"""
    try:
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        if not response:
            return {"error": "EmailNotification not found"}, 404

        return _to_entity_dict(response.data), 200

    except Exception as e:
        logger.exception("Error getting EmailNotification %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


@email_notifications_bp.route("", methods=["GET"])
@tag(["email-notifications"])
@operation_id("list_email_notifications")
async def list_email_notifications() -> ResponseReturnValue:
    """List all EmailNotifications"""
    try:
        entities = await service.find_all(
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        entity_list = [_to_entity_dict(r.data) for r in entities]
        return {"notifications": entity_list, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error listing EmailNotifications: %s", str(e))
        return {"error": str(e)}, 500


@email_notifications_bp.route("/<entity_id>", methods=["PUT"])
@tag(["email-notifications"])
@operation_id("update_email_notification")
async def update_email_notification(entity_id: str) -> ResponseReturnValue:
    """Update EmailNotification"""
    try:
        data = await request.get_json()
        transition = request.args.get("transition")

        response = await service.update(
            entity_id=entity_id,
            entity=data,
            entity_class=EmailNotification.ENTITY_NAME,
            transition=transition,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        logger.info("Updated EmailNotification %s", entity_id)
        return _to_entity_dict(response.data), 200

    except Exception as e:
        logger.exception("Error updating EmailNotification %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


@email_notifications_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["email-notifications"])
@operation_id("delete_email_notification")
async def delete_email_notification(entity_id: str) -> ResponseReturnValue:
    """Delete EmailNotification"""
    try:
        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        logger.info("Deleted EmailNotification %s", entity_id)
        return {
            "success": True,
            "message": "EmailNotification deleted successfully",
        }, 200

    except Exception as e:
        logger.exception("Error deleting EmailNotification %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


@email_notifications_bp.route("/user/<user_id>", methods=["GET"])
@tag(["email-notifications"])
@operation_id("get_notifications_by_user")
async def get_notifications_by_user(user_id: str) -> ResponseReturnValue:
    """Get all notifications for a specific user"""
    try:
        from common.service.entity_service import SearchConditionRequest

        builder = SearchConditionRequest.builder()
        builder.equals("user_id", user_id)
        condition = builder.build()

        entities = await service.search(
            entity_class=EmailNotification.ENTITY_NAME,
            condition=condition,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        entity_list = [_to_entity_dict(r.data) for r in entities]
        return {"notifications": entity_list, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error getting notifications for user %s: %s", user_id, str(e))
        return {"error": str(e)}, 500


@email_notifications_bp.route("/status/<status>", methods=["GET"])
@tag(["email-notifications"])
@operation_id("get_notifications_by_status")
async def get_notifications_by_status(status: str) -> ResponseReturnValue:
    """Get all notifications with specific delivery status"""
    try:
        from common.service.entity_service import SearchConditionRequest

        builder = SearchConditionRequest.builder()
        builder.equals("delivery_status", status)
        condition = builder.build()

        entities = await service.search(
            entity_class=EmailNotification.ENTITY_NAME,
            condition=condition,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        entity_list = [_to_entity_dict(r.data) for r in entities]
        return {"notifications": entity_list, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error getting notifications by status %s: %s", status, str(e))
        return {"error": str(e)}, 500
