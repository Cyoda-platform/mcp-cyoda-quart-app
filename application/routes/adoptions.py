"""
Adoption Routes for Purrfect Pets API

Manages all Adoption-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag, validate, validate_querystring

from application.entity.adoption.version_1.adoption import Adoption
from services.services import get_entity_service

logger = logging.getLogger(__name__)

# Create blueprint
adoptions_bp = Blueprint("adoptions", __name__, url_prefix="/api/v1/adoptions")

# Service proxy
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)

service = _ServiceProxy()

# Request/Response models
class AdoptionUpdateQueryParams(BaseModel):
    transition: Optional[str] = Field(default=None, description="Workflow transition to trigger")

class ErrorResponse(BaseModel):
    error: str
    code: Optional[str] = None

class ValidationErrorResponse(BaseModel):
    error: str
    code: str = "VALIDATION_ERROR"

class AdoptionResponse(BaseModel):
    data: Adoption

def _to_entity_dict(entity_data: Any) -> Dict[str, Any]:
    """Convert entity data to dictionary format"""
    if hasattr(entity_data, 'model_dump'):
        return entity_data.model_dump(by_alias=True)
    elif isinstance(entity_data, dict):
        return entity_data
    else:
        return dict(entity_data)

# CRUD Operations

@adoptions_bp.route("", methods=["POST"])
@tag(["adoptions"])
@operation_id("create_adoption")
@validate(
    request=Adoption,
    responses={
        201: (AdoptionResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_adoption(data: Adoption) -> ResponseReturnValue:
    """Create a new Adoption"""
    try:
        entity_data = data.model_dump(by_alias=True)
        response = await service.save(
            entity=entity_data,
            entity_class=Adoption.ENTITY_NAME,
            entity_version=str(Adoption.ENTITY_VERSION),
        )
        logger.info("Created Adoption with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201
    except ValueError as e:
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Adoption: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@adoptions_bp.route("/<entity_id>", methods=["GET"])
@tag(["adoptions"])
@operation_id("get_adoption")
async def get_adoption(entity_id: str) -> ResponseReturnValue:
    """Get Adoption by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Adoption.ENTITY_NAME,
            entity_version=str(Adoption.ENTITY_VERSION),
        )
        if not response:
            return {"error": "Adoption not found", "code": "NOT_FOUND"}, 404
        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error getting Adoption %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@adoptions_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(AdoptionUpdateQueryParams)
@tag(["adoptions"])
@operation_id("update_adoption")
@validate(request=Adoption)
async def update_adoption(entity_id: str, data: Adoption, query_args: AdoptionUpdateQueryParams) -> ResponseReturnValue:
    """Update Adoption and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Adoption.ENTITY_NAME,
            transition=transition,
            entity_version=str(Adoption.ENTITY_VERSION),
        )
        logger.info("Updated Adoption %s", entity_id)
        return jsonify(_to_entity_dict(response.data)), 200
    except ValueError as e:
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating Adoption %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

# Specific Adoption Operations

@adoptions_bp.route("/<entity_id>/schedule-followup", methods=["POST"])
@tag(["adoptions"])
@operation_id("schedule_followup")
async def schedule_followup(entity_id: str) -> ResponseReturnValue:
    """Schedule follow-up for an adoption"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        request_data = await request.get_json() or {}
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="schedule_followup",
            entity_class=Adoption.ENTITY_NAME,
            entity_version=str(Adoption.ENTITY_VERSION),
            parameters=request_data,
        )
        logger.info("Scheduled follow-up for Adoption %s", entity_id)
        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error scheduling follow-up for Adoption %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@adoptions_bp.route("/<entity_id>/complete-followup", methods=["POST"])
@tag(["adoptions"])
@operation_id("complete_followup")
async def complete_followup(entity_id: str) -> ResponseReturnValue:
    """Complete follow-up for an adoption"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        request_data = await request.get_json() or {}
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="complete_followup",
            entity_class=Adoption.ENTITY_NAME,
            entity_version=str(Adoption.ENTITY_VERSION),
            parameters=request_data,
        )
        logger.info("Completed follow-up for Adoption %s", entity_id)
        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error completing follow-up for Adoption %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@adoptions_bp.route("/<entity_id>/return", methods=["POST"])
@tag(["adoptions"])
@operation_id("return_adoption")
async def return_adoption(entity_id: str) -> ResponseReturnValue:
    """Process return of an adopted pet"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        request_data = await request.get_json() or {}
        return_reason = request_data.get("returnReason")
        if not return_reason:
            return {"error": "Return reason is required", "code": "VALIDATION_ERROR"}, 400
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="return",
            entity_class=Adoption.ENTITY_NAME,
            entity_version=str(Adoption.ENTITY_VERSION),
            parameters={"returnReason": return_reason},
        )
        logger.info("Processed return for Adoption %s", entity_id)
        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error processing return for Adoption %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
