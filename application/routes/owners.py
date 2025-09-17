"""
Owner Routes for Purrfect Pets Application

Manages all Owner-related API endpoints including CRUD operations
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
from application.entity.owner.version_1.owner import Owner
from application.models import (
    OwnerQueryParams,
    OwnerUpdateQueryParams,
    OwnerResponse,
    OwnerListResponse,
    OwnerSearchResponse,
    CountResponse,
    DeleteResponse,
    ExistsResponse,
    TransitionResponse,
    TransitionsResponse,
    SearchRequest,
    TransitionRequest,
    ErrorResponse,
    ValidationErrorResponse,
)

logger = logging.getLogger(__name__)


class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()


def _to_entity_dict(data: Any) -> Dict[str, Any]:
    """Helper to normalize entity data from service."""
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


owners_bp = Blueprint("owners", __name__, url_prefix="/api/owners")


@owners_bp.route("", methods=["POST"])
@tag(["owners"])
@operation_id("create_owner")
@validate(
    request=Owner,
    responses={
        201: (OwnerResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_owner(data: Owner) -> ResponseReturnValue:
    """Create a new owner with comprehensive validation"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=Owner.ENTITY_NAME,
            entity_version=str(Owner.ENTITY_VERSION),
        )

        logger.info("Created Owner with ID: %s", response.metadata.id)

        # Return created entity directly (thin proxy)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating Owner: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Owner: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@owners_bp.route("/<entity_id>", methods=["GET"])
@tag(["owners"])
@operation_id("get_owner")
@validate(
    responses={
        200: (OwnerResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_owner(entity_id: str) -> ResponseReturnValue:
    """Get Owner by ID with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Owner.ENTITY_NAME,
            entity_version=str(Owner.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Owner not found", "code": "NOT_FOUND"}, 404

        # Thin proxy: return the entity directly
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting Owner %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@owners_bp.route("", methods=["GET"])
@validate_querystring(OwnerQueryParams)
@tag(["owners"])
@operation_id("list_owners")
@validate(
    responses={
        200: (OwnerListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_owners(query_args: OwnerQueryParams) -> ResponseReturnValue:
    """List Owners with optional filtering and validation"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.experience:
            search_conditions["experience"] = query_args.experience

        if query_args.state:
            search_conditions["state"] = query_args.state

        # Get entities
        if search_conditions:
            # Build search condition request
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=Owner.ENTITY_NAME,
                condition=condition,
                entity_version=str(Owner.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=Owner.ENTITY_NAME,
                entity_version=str(Owner.ENTITY_VERSION),
            )

        # Thin proxy: return entities directly
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"owners": paginated_entities, "total": len(entity_list)}), 200

    except Exception as e:
        logger.exception("Error listing Owners: %s", str(e))
        return jsonify({"error": str(e)}), 500


@owners_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(OwnerUpdateQueryParams)
@tag(["owners"])
@operation_id("update_owner")
@validate(
    request=Owner,
    responses={
        200: (OwnerResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_owner(
    entity_id: str, data: Owner, query_args: OwnerUpdateQueryParams
) -> ResponseReturnValue:
    """Update Owner and optionally trigger workflow transition with validation"""
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
            entity_class=Owner.ENTITY_NAME,
            transition=transition,
            entity_version=str(Owner.ENTITY_VERSION),
        )

        logger.info("Updated Owner %s", entity_id)

        # Return updated entity directly (thin proxy)
        return jsonify(_to_entity_dict(response.data)), 200

    except ValueError as e:
        logger.warning("Validation error updating Owner %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error updating Owner %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@owners_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["owners"])
@operation_id("delete_owner")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_owner(entity_id: str) -> ResponseReturnValue:
    """Delete Owner with validation"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return (
                jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}),
                400,
            )

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Owner.ENTITY_NAME,
            entity_version=str(Owner.ENTITY_VERSION),
        )

        logger.info("Deleted Owner %s", entity_id)

        # Thin proxy: return success message
        response = DeleteResponse(
            success=True,
            message="Owner deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting Owner %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
