"""
Email Notifications API Routes for Product Performance Analysis System

REST API endpoints for managing EmailNotification entities including CRUD operations
and email sending triggers as specified in functional requirements.
"""

import logging
from typing import Any, Dict, List, Optional

from quart import Blueprint, jsonify, request
from quart_schema import tag, validate_json, validate_querystring

from application.entity.email_notification.version_1.email_notification import (
    EmailNotification,
)
from services.services import get_entity_service

# Create blueprint for email notification routes
email_notifications_bp = Blueprint(
    "email_notifications", __name__, url_prefix="/api/email-notifications"
)

logger = logging.getLogger(__name__)


@email_notifications_bp.route("/", methods=["POST"])
@tag(["EmailNotifications"])
@validate_json(EmailNotification)
async def create_email_notification(
    json: EmailNotification,
) -> tuple[Dict[str, Any], int]:
    """
    Create a new EmailNotification entity.

    Creates a new email notification that will be processed through the
    email preparation and sending workflow.
    """
    try:
        entity_service = get_entity_service()

        # Convert Pydantic model to dict for EntityService
        notification_dict = json.model_dump(by_alias=True)

        # Save the entity using entity constants
        response = await entity_service.save(
            entity=notification_dict,
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        # Return the created entity with technical ID and state
        result = {
            "id": response.metadata.id,
            "state": response.metadata.state,
            "entity": notification_dict,
        }

        logger.info(f"Created EmailNotification entity with ID: {response.metadata.id}")
        return result, 201

    except Exception as e:
        logger.error(f"Error creating EmailNotification entity: {str(e)}")
        return {"error": "Failed to create email notification", "details": str(e)}, 500


@email_notifications_bp.route("/<entity_id>", methods=["GET"])
@tag(["EmailNotifications"])
async def get_email_notification(entity_id: str) -> tuple[Dict[str, Any], int]:
    """
    Retrieve an EmailNotification entity by ID.

    Returns the email notification entity with current state and delivery status.
    """
    try:
        entity_service = get_entity_service()

        # Get the entity by technical ID
        response = await entity_service.get(
            entity_id=entity_id,
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        if not response or not response.entity:
            return {"error": "Email notification not found"}, 404

        # Return the entity with metadata
        result = {
            "id": response.metadata.id,
            "state": response.metadata.state,
            "entity": response.entity,
        }

        return result, 200

    except Exception as e:
        logger.error(f"Error retrieving EmailNotification entity {entity_id}: {str(e)}")
        return {
            "error": "Failed to retrieve email notification",
            "details": str(e),
        }, 500


@email_notifications_bp.route("/<entity_id>", methods=["PUT"])
@tag(["EmailNotifications"])
@validate_json(EmailNotification)
async def update_email_notification(
    entity_id: str, json: EmailNotification
) -> tuple[Dict[str, Any], int]:
    """
    Update an EmailNotification entity.

    Updates the email notification and optionally triggers reprocessing through
    the email workflow.
    """
    try:
        entity_service = get_entity_service()

        # Get transition from query parameters (optional)
        transition = request.args.get("transition")

        # Convert Pydantic model to dict for EntityService
        notification_dict = json.model_dump(by_alias=True)

        # Update the entity
        if transition:
            response = await entity_service.update_with_transition(
                entity_id=entity_id,
                entity=notification_dict,
                entity_class=EmailNotification.ENTITY_NAME,
                entity_version=str(EmailNotification.ENTITY_VERSION),
                transition=transition,
            )
        else:
            response = await entity_service.update(
                entity_id=entity_id,
                entity=notification_dict,
                entity_class=EmailNotification.ENTITY_NAME,
                entity_version=str(EmailNotification.ENTITY_VERSION),
            )

        # Return the updated entity
        result = {
            "id": response.metadata.id,
            "state": response.metadata.state,
            "entity": response.entity,
        }

        logger.info(f"Updated EmailNotification entity {entity_id}")
        return result, 200

    except Exception as e:
        logger.error(f"Error updating EmailNotification entity {entity_id}: {str(e)}")
        return {"error": "Failed to update email notification", "details": str(e)}, 500


@email_notifications_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["EmailNotifications"])
async def delete_email_notification(entity_id: str) -> tuple[Dict[str, Any], int]:
    """
    Delete an EmailNotification entity.

    Removes the email notification entity from the system.
    """
    try:
        entity_service = get_entity_service()

        # Delete the entity
        await entity_service.delete(
            entity_id=entity_id,
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        logger.info(f"Deleted EmailNotification entity {entity_id}")
        return {"message": "Email notification deleted successfully"}, 200

    except Exception as e:
        logger.error(f"Error deleting EmailNotification entity {entity_id}: {str(e)}")
        return {"error": "Failed to delete email notification", "details": str(e)}, 500


@email_notifications_bp.route("/", methods=["GET"])
@tag(["EmailNotifications"])
async def list_email_notifications() -> tuple[Dict[str, Any], int]:
    """
    List EmailNotification entities with optional filtering.

    Returns a paginated list of email notifications with filtering options.
    """
    try:
        entity_service = get_entity_service()

        # Get query parameters
        page_size = int(request.args.get("page_size", 50))
        page_token = request.args.get("page_token")
        send_status = request.args.get("send_status")
        recipient = request.args.get("recipient")

        # Build search query
        query = {}
        if send_status:
            query["sendStatus"] = send_status
        if recipient:
            query["recipientEmail"] = recipient

        # Search for entities
        response = await entity_service.search(
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
            query=query,
            page_size=page_size,
            page_token=page_token,
        )

        # Format response
        entities = []
        if hasattr(response, "entities") and response.entities:
            for entity_data in response.entities:
                entities.append(
                    {
                        "id": entity_data.metadata.id,
                        "state": entity_data.metadata.state,
                        "entity": entity_data.entity,
                    }
                )

        result = {
            "entities": entities,
            "page_token": getattr(response, "next_page_token", None),
            "total_count": len(entities),
        }

        return result, 200

    except Exception as e:
        logger.error(f"Error listing EmailNotification entities: {str(e)}")
        return {"error": "Failed to list email notifications", "details": str(e)}, 500


@email_notifications_bp.route("/send-weekly-report", methods=["POST"])
@tag(["EmailNotifications"])
async def send_weekly_report() -> tuple[Dict[str, Any], int]:
    """
    Send weekly performance report email notification.

    Creates and sends an email notification with the latest performance report
    to the sales team.
    """
    try:
        entity_service = get_entity_service()

        # Create a new email notification for weekly report
        notification_data = {
            "subject": "Weekly Product Performance Report",
            "recipientEmail": "victoria.sagdieva@cyoda.com",
            "emailBody": "Weekly performance report email preparation pending...",
            "emailFormat": "html",
            "sendStatus": "pending",
            "priority": "normal",
        }

        # Save the new notification entity
        response = await entity_service.save(
            entity=notification_data,
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        result = {
            "id": response.metadata.id,
            "state": response.metadata.state,
            "message": "Weekly report email notification initiated",
            "entity": notification_data,
        }

        logger.info(f"Initiated weekly report email with ID: {response.metadata.id}")
        return result, 201

    except Exception as e:
        logger.error(f"Error sending weekly report email: {str(e)}")
        return {"error": "Failed to send weekly report email", "details": str(e)}, 500


@email_notifications_bp.route("/retry/<entity_id>", methods=["POST"])
@tag(["EmailNotifications"])
async def retry_email_notification(entity_id: str) -> tuple[Dict[str, Any], int]:
    """
    Retry sending a failed email notification.

    Attempts to resend an email notification that previously failed.
    """
    try:
        entity_service = get_entity_service()

        # Get the existing notification
        response = await entity_service.get(
            entity_id=entity_id,
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        if not response or not response.entity:
            return {"error": "Email notification not found"}, 404

        entity = response.entity

        # Check if retry is allowed
        if entity.get("sendStatus") != "failed":
            return {"error": "Email notification is not in failed state"}, 400

        if entity.get("retryCount", 0) >= entity.get("maxRetries", 3):
            return {"error": "Maximum retry attempts exceeded"}, 400

        # Reset status to pending and trigger resend
        entity["sendStatus"] = "pending"
        entity["errorMessage"] = None

        # Update the entity with transition to trigger resending
        updated_response = await entity_service.update_with_transition(
            entity_id=entity_id,
            entity=entity,
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
            transition="send_email",
        )

        result = {
            "id": updated_response.metadata.id,
            "state": updated_response.metadata.state,
            "message": "Email notification retry initiated",
            "entity": updated_response.entity,
        }

        logger.info(f"Initiated retry for EmailNotification {entity_id}")
        return result, 200

    except Exception as e:
        logger.error(f"Error retrying email notification {entity_id}: {str(e)}")
        return {"error": "Failed to retry email notification", "details": str(e)}, 500


@email_notifications_bp.route("/analytics", methods=["GET"])
@tag(["EmailNotifications"])
async def get_email_analytics() -> tuple[Dict[str, Any], int]:
    """
    Get email notification analytics.

    Returns aggregated analytics including delivery rates, open rates,
    and status breakdown.
    """
    try:
        entity_service = get_entity_service()

        # Get all email notifications
        response = await entity_service.search(
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
            query={},
            page_size=1000,
        )

        # Initialize analytics
        analytics = {
            "total_emails": 0,
            "sent_emails": 0,
            "failed_emails": 0,
            "pending_emails": 0,
            "opened_emails": 0,
            "delivery_rate": 0.0,
            "open_rate": 0.0,
            "status_breakdown": {},
            "total_clicks": 0,
            "average_retry_count": 0.0,
        }

        if hasattr(response, "entities") and response.entities:
            total_retries = 0

            for entity_data in response.entities:
                entity = entity_data.entity
                analytics["total_emails"] += 1

                # Status counts
                status = entity.get("sendStatus", "unknown")
                if status not in analytics["status_breakdown"]:
                    analytics["status_breakdown"][status] = 0
                analytics["status_breakdown"][status] += 1

                if status == "sent":
                    analytics["sent_emails"] += 1
                elif status == "failed":
                    analytics["failed_emails"] += 1
                elif status == "pending":
                    analytics["pending_emails"] += 1

                # Open tracking
                if entity.get("emailOpened", False):
                    analytics["opened_emails"] += 1

                # Click tracking
                analytics["total_clicks"] += entity.get("clickCount", 0)

                # Retry tracking
                total_retries += entity.get("retryCount", 0)

            # Calculate rates
            if analytics["total_emails"] > 0:
                analytics["delivery_rate"] = (
                    analytics["sent_emails"] / analytics["total_emails"] * 100
                )
                analytics["average_retry_count"] = (
                    total_retries / analytics["total_emails"]
                )

            if analytics["sent_emails"] > 0:
                analytics["open_rate"] = (
                    analytics["opened_emails"] / analytics["sent_emails"] * 100
                )

        return analytics, 200

    except Exception as e:
        logger.error(f"Error getting email analytics: {str(e)}")
        return {"error": "Failed to get email analytics", "details": str(e)}, 500
