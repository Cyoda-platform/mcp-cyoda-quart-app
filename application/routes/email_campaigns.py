"""
EmailCampaign Routes for Cat Fact Subscription Application

Manages all EmailCampaign-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
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

from ..entity.email_campaign.version_1.email_campaign import EmailCampaign
from ..models import (
    CountResponse,
    DeleteResponse,
    EmailCampaignListResponse,
    EmailCampaignQueryParams,
    EmailCampaignResponse,
    EmailCampaignSearchRequest,
    EmailCampaignSearchResponse,
    EmailCampaignUpdateQueryParams,
    ErrorResponse,
    ExistsResponse,
    TransitionResponse,
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


email_campaigns_bp = Blueprint(
    "email_campaigns", __name__, url_prefix="/api/email-campaigns"
)


@email_campaigns_bp.route("", methods=["POST"])
@tag(["email-campaigns"])
@operation_id("create_email_campaign")
@validate(
    request=EmailCampaign,
    responses={
        201: (EmailCampaignResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_email_campaign(data: EmailCampaign) -> ResponseReturnValue:
    """Create a new EmailCampaign with comprehensive validation"""
    try:
        entity_data = data.model_dump(by_alias=True)

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
@validate(
    responses={
        200: (EmailCampaignResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_email_campaign(entity_id: str) -> ResponseReturnValue:
    """Get EmailCampaign by ID with validation"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=EmailCampaign.ENTITY_NAME,
            entity_version=str(EmailCampaign.ENTITY_VERSION),
        )

        if not response:
            return {"error": "EmailCampaign not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting EmailCampaign %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@email_campaigns_bp.route("", methods=["GET"])
@validate_querystring(EmailCampaignQueryParams)
@tag(["email-campaigns"])
@operation_id("list_email_campaigns")
@validate(
    responses={
        200: (EmailCampaignListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_email_campaigns(
    query_args: EmailCampaignQueryParams,
) -> ResponseReturnValue:
    """List EmailCampaigns with optional filtering and validation"""
    try:
        search_conditions: Dict[str, str] = {}

        if query_args.status:
            search_conditions["status"] = query_args.status

        if query_args.campaign_date:
            search_conditions["campaignDate"] = query_args.campaign_date

        if query_args.state:
            search_conditions["state"] = query_args.state

        # Get entities
        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
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

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"entities": paginated_entities, "total": len(entity_list)}), 200

    except Exception as e:
        logger.exception("Error listing EmailCampaigns: %s", str(e))
        return jsonify({"error": str(e)}), 500


@email_campaigns_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(EmailCampaignUpdateQueryParams)
@tag(["email-campaigns"])
@operation_id("update_email_campaign")
@validate(
    request=EmailCampaign,
    responses={
        200: (EmailCampaignResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_email_campaign(
    entity_id: str, data: EmailCampaign, query_args: EmailCampaignUpdateQueryParams
) -> ResponseReturnValue:
    """Update EmailCampaign and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=EmailCampaign.ENTITY_NAME,
            transition=transition,
            entity_version=str(EmailCampaign.ENTITY_VERSION),
        )

        logger.info("Updated EmailCampaign %s", entity_id)
        return jsonify(_to_entity_dict(response.data)), 200

    except ValueError as e:
        logger.warning(
            "Validation error updating EmailCampaign %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error updating EmailCampaign %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@email_campaigns_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["email-campaigns"])
@operation_id("delete_email_campaign")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_email_campaign(entity_id: str) -> ResponseReturnValue:
    """Delete EmailCampaign with validation"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=EmailCampaign.ENTITY_NAME,
            entity_version=str(EmailCampaign.ENTITY_VERSION),
        )

        logger.info("Deleted EmailCampaign %s", entity_id)

        response = DeleteResponse(
            success=True,
            message="EmailCampaign deleted successfully",
            entityId=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting EmailCampaign %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@email_campaigns_bp.route("/<entity_id>/send", methods=["POST"])
@tag(["email-campaigns"])
@operation_id("send_email_campaign")
@validate(
    responses={
        200: (TransitionResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def send_campaign(entity_id: str) -> ResponseReturnValue:
    """Trigger sending of an email campaign"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        # Get current campaign state
        current_campaign = await service.get_by_id(
            entity_id=entity_id,
            entity_class=EmailCampaign.ENTITY_NAME,
            entity_version=str(EmailCampaign.ENTITY_VERSION),
        )

        if not current_campaign:
            return jsonify({"error": "EmailCampaign not found"}), 404

        previous_state = current_campaign.metadata.state

        # Execute the send transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="send",
            entity_class=EmailCampaign.ENTITY_NAME,
            entity_version=str(EmailCampaign.ENTITY_VERSION),
        )

        logger.info("Triggered send transition on EmailCampaign %s", entity_id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "message": "Campaign sending initiated successfully",
                    "previousState": previous_state,
                    "newState": response.metadata.state,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error sending EmailCampaign %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@email_campaigns_bp.route("/<entity_id>/exists", methods=["GET"])
@tag(["email-campaigns"])
@operation_id("check_email_campaign_exists")
@validate(responses={200: (ExistsResponse, None), 500: (ErrorResponse, None)})
async def check_exists(entity_id: str) -> ResponseReturnValue:
    """Check if EmailCampaign exists by ID"""
    try:
        exists = await service.exists_by_id(
            entity_id=entity_id,
            entity_class=EmailCampaign.ENTITY_NAME,
            entity_version=str(EmailCampaign.ENTITY_VERSION),
        )

        response = ExistsResponse(exists=exists, entityId=entity_id)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception(
            "Error checking EmailCampaign existence %s: %s", entity_id, str(e)
        )
        return {"error": str(e)}, 500


@email_campaigns_bp.route("/count", methods=["GET"])
@tag(["email-campaigns"])
@operation_id("count_email_campaigns")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_entities() -> ResponseReturnValue:
    """Count total number of EmailCampaigns"""
    try:
        count = await service.count(
            entity_class=EmailCampaign.ENTITY_NAME,
            entity_version=str(EmailCampaign.ENTITY_VERSION),
        )

        response = CountResponse(count=count)
        return jsonify(response.model_dump()), 200

    except Exception as e:
        logger.exception("Error counting EmailCampaigns: %s", str(e))
        return jsonify({"error": str(e)}), 500


@email_campaigns_bp.route("/search", methods=["POST"])
@tag(["email-campaigns"])
@operation_id("search_email_campaigns")
@validate(
    request=EmailCampaignSearchRequest,
    responses={
        200: (EmailCampaignSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_entities(data: EmailCampaignSearchRequest) -> ResponseReturnValue:
    """Search EmailCampaigns using field-value search"""
    try:
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=EmailCampaign.ENTITY_NAME,
            condition=search_request,
            entity_version=str(EmailCampaign.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"entities": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching EmailCampaigns: %s", str(e))
        return {"error": str(e)}, 500
