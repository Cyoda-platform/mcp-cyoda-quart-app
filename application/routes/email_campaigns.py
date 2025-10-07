"""
EmailCampaign Routes for Cat Facts Subscription System

Manages all EmailCampaign-related API endpoints including CRUD operations
and campaign management.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from quart import Blueprint, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag

from application.entity.email_campaign.version_1.email_campaign import EmailCampaign
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

logger = logging.getLogger(__name__)


# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


email_campaigns_bp = Blueprint(
    "email_campaigns", __name__, url_prefix="/api/email-campaigns"
)


@email_campaigns_bp.route("", methods=["POST"])
@tag(["email-campaigns"])
@operation_id("create_email_campaign")
async def create_email_campaign() -> ResponseReturnValue:
    """Create a new email campaign"""
    try:
        data = await request.get_json()
        if not data:
            return {"error": "Request body is required", "code": "MISSING_BODY"}, 400

        # Create EmailCampaign instance for validation
        campaign = EmailCampaign(**data)
        entity_data = campaign.model_dump(by_alias=True)

        # Save the entity
        service = get_entity_service()
        response = await service.save(
            entity=entity_data,
            entity_class=EmailCampaign.ENTITY_NAME,
            entity_version=str(EmailCampaign.ENTITY_VERSION),
        )

        logger.info("Created EmailCampaign with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating EmailCampaign: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating EmailCampaign: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@email_campaigns_bp.route("/<entity_id>", methods=["GET"])
@tag(["email-campaigns"])
@operation_id("get_email_campaign")
async def get_email_campaign(entity_id: str) -> ResponseReturnValue:
    """Get email campaign by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        service = get_entity_service()
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=EmailCampaign.ENTITY_NAME,
            entity_version=str(EmailCampaign.ENTITY_VERSION),
        )

        if not response:
            return {"error": "EmailCampaign not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200

    except Exception as e:
        logger.exception("Error getting EmailCampaign %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@email_campaigns_bp.route("", methods=["GET"])
@tag(["email-campaigns"])
@operation_id("list_email_campaigns")
async def list_email_campaigns() -> ResponseReturnValue:
    """List all email campaigns with optional filtering"""
    try:
        # Get query parameters
        campaign_type = request.args.get("campaign_type")
        email_template = request.args.get("email_template")
        state = request.args.get("state")

        service = get_entity_service()

        # Build search conditions if filters provided
        if campaign_type or email_template or state:
            builder = SearchConditionRequest.builder()

            if campaign_type:
                builder.equals("campaign_type", campaign_type)
            if email_template:
                builder.equals("email_template", email_template)
            if state:
                builder.equals("state", state)

            condition = builder.build()
            entities = await service.search(
                entity_class=EmailCampaign.ENTITY_NAME,
                condition=condition,
                entity_version=str(EmailCampaign.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=EmailCampaign.ENTITY_NAME,
                entity_version=str(EmailCampaign.ENTITY_VERSION),
            )

        entity_list = [_to_entity_dict(r.data) for r in entities]
        return {"email_campaigns": entity_list, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error listing EmailCampaigns: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@email_campaigns_bp.route("/<entity_id>", methods=["PUT"])
@tag(["email-campaigns"])
@operation_id("update_email_campaign")
async def update_email_campaign(entity_id: str) -> ResponseReturnValue:
    """Update email campaign and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        data = await request.get_json()
        if not data:
            return {"error": "Request body is required", "code": "MISSING_BODY"}, 400

        # Get transition from query parameters
        transition = request.args.get("transition")

        # Create EmailCampaign instance for validation
        campaign = EmailCampaign(**data)
        entity_data = campaign.model_dump(by_alias=True)

        # Update the entity
        service = get_entity_service()
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=EmailCampaign.ENTITY_NAME,
            transition=transition,
            entity_version=str(EmailCampaign.ENTITY_VERSION),
        )

        logger.info("Updated EmailCampaign %s", entity_id)
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning(
            "Validation error updating EmailCampaign %s: %s", entity_id, str(e)
        )
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating EmailCampaign %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@email_campaigns_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["email-campaigns"])
@operation_id("delete_email_campaign")
async def delete_email_campaign(entity_id: str) -> ResponseReturnValue:
    """Delete email campaign"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        service = get_entity_service()
        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=EmailCampaign.ENTITY_NAME,
            entity_version=str(EmailCampaign.ENTITY_VERSION),
        )

        logger.info("Deleted EmailCampaign %s", entity_id)
        return {
            "success": True,
            "message": "EmailCampaign deleted successfully",
            "entity_id": entity_id,
        }, 200

    except Exception as e:
        logger.exception("Error deleting EmailCampaign %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@email_campaigns_bp.route("/<entity_id>/start", methods=["POST"])
@tag(["email-campaigns"])
@operation_id("start_email_campaign")
async def start_email_campaign(entity_id: str) -> ResponseReturnValue:
    """Start sending an email campaign"""
    try:
        service = get_entity_service()

        # Execute start_sending transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="start_sending",
            entity_class=EmailCampaign.ENTITY_NAME,
            entity_version=str(EmailCampaign.ENTITY_VERSION),
        )

        logger.info("Started EmailCampaign %s", entity_id)
        return {
            "success": True,
            "message": "Email campaign started successfully",
            "entity_id": entity_id,
            "new_state": response.metadata.state,
        }, 200

    except Exception as e:
        logger.exception("Error starting EmailCampaign %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@email_campaigns_bp.route("/<entity_id>/cancel", methods=["POST"])
@tag(["email-campaigns"])
@operation_id("cancel_email_campaign")
async def cancel_email_campaign(entity_id: str) -> ResponseReturnValue:
    """Cancel an email campaign"""
    try:
        service = get_entity_service()

        # Execute cancel transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="cancel",
            entity_class=EmailCampaign.ENTITY_NAME,
            entity_version=str(EmailCampaign.ENTITY_VERSION),
        )

        logger.info("Cancelled EmailCampaign %s", entity_id)
        return {
            "success": True,
            "message": "Email campaign cancelled successfully",
            "entity_id": entity_id,
            "new_state": response.metadata.state,
        }, 200

    except Exception as e:
        logger.exception("Error cancelling EmailCampaign %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@email_campaigns_bp.route("/stats", methods=["GET"])
@tag(["email-campaigns"])
@operation_id("get_email_campaign_stats")
async def get_email_campaign_stats() -> ResponseReturnValue:
    """Get email campaign statistics"""
    try:
        service = get_entity_service()

        # Get all email campaigns
        entities = await service.find_all(
            entity_class=EmailCampaign.ENTITY_NAME,
            entity_version=str(EmailCampaign.ENTITY_VERSION),
        )

        # Calculate statistics
        stats: Dict[str, Any] = {
            "total_campaigns": len(entities),
            "by_type": {},
            "by_state": {},
            "by_template": {},
            "performance": {
                "total_emails_sent": 0,
                "total_emails_opened": 0,
                "total_emails_clicked": 0,
                "total_unsubscribes": 0,
                "average_delivery_rate": 0.0,
                "average_open_rate": 0.0,
                "average_click_rate": 0.0,
            },
        }

        total_delivery_rate = 0.0
        total_open_rate = 0.0
        total_click_rate = 0.0
        completed_campaigns = 0

        from common.entity.entity_casting import cast_entity

        for entity_response in entities:
            campaign = cast_entity(entity_response.data, EmailCampaign)

            # Count by type
            campaign_type = campaign.campaign_type
            stats["by_type"][campaign_type] = stats["by_type"].get(campaign_type, 0) + 1

            # Count by state
            state = campaign.state or "unknown"
            stats["by_state"][state] = stats["by_state"].get(state, 0) + 1

            # Count by template
            template = campaign.email_template
            stats["by_template"][template] = stats["by_template"].get(template, 0) + 1

            # Aggregate performance metrics
            stats["performance"]["total_emails_sent"] += campaign.emails_sent
            stats["performance"]["total_emails_opened"] += campaign.emails_opened
            stats["performance"]["total_emails_clicked"] += campaign.emails_clicked
            stats["performance"]["total_unsubscribes"] += campaign.unsubscribes

            # Calculate rates for completed campaigns
            if campaign.is_completed():
                total_delivery_rate += campaign.get_delivery_rate()
                total_open_rate += campaign.get_open_rate()
                total_click_rate += campaign.get_click_rate()
                completed_campaigns += 1

        # Calculate average rates
        if completed_campaigns > 0:
            stats["performance"]["average_delivery_rate"] = (
                total_delivery_rate / completed_campaigns
            )
            stats["performance"]["average_open_rate"] = (
                total_open_rate / completed_campaigns
            )
            stats["performance"]["average_click_rate"] = (
                total_click_rate / completed_campaigns
            )

        return stats, 200

    except Exception as e:
        logger.exception("Error getting email campaign stats: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
