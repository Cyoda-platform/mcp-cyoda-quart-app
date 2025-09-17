"""
AdoptionApplication Routes for Purrfect Pets API

Manages all AdoptionApplication-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag, validate, validate_querystring

from application.entity.adoption_application.version_1.adoption_application import AdoptionApplication
from services.services import get_entity_service

logger = logging.getLogger(__name__)

# Create blueprint
adoption_applications_bp = Blueprint("adoption_applications", __name__, url_prefix="/api/v1/adoption-applications")

# Service proxy
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)

service = _ServiceProxy()

# Request/Response models
class AdoptionApplicationUpdateQueryParams(BaseModel):
    transition: Optional[str] = Field(default=None, description="Workflow transition to trigger")

class ErrorResponse(BaseModel):
    error: str
    code: Optional[str] = None

class ValidationErrorResponse(BaseModel):
    error: str
    code: str = "VALIDATION_ERROR"

class AdoptionApplicationResponse(BaseModel):
    data: AdoptionApplication

def _to_entity_dict(entity_data: Any) -> Dict[str, Any]:
    """Convert entity data to dictionary format"""
    if hasattr(entity_data, 'model_dump'):
        return entity_data.model_dump(by_alias=True)
    elif isinstance(entity_data, dict):
        return entity_data
    else:
        return dict(entity_data)

# CRUD Operations

@adoption_applications_bp.route("", methods=["POST"])
@tag(["adoption-applications"])
@operation_id("create_adoption_application")
@validate(
    request=AdoptionApplication,
    responses={
        201: (AdoptionApplicationResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_adoption_application(data: AdoptionApplication) -> ResponseReturnValue:
    """Create a new AdoptionApplication"""
    try:
        entity_data = data.model_dump(by_alias=True)
        response = await service.save(
            entity=entity_data,
            entity_class=AdoptionApplication.ENTITY_NAME,
            entity_version=str(AdoptionApplication.ENTITY_VERSION),
        )
        logger.info("Created AdoptionApplication with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201
    except ValueError as e:
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating AdoptionApplication: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@adoption_applications_bp.route("/<entity_id>", methods=["GET"])
@tag(["adoption-applications"])
@operation_id("get_adoption_application")
async def get_adoption_application(entity_id: str) -> ResponseReturnValue:
    """Get AdoptionApplication by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=AdoptionApplication.ENTITY_NAME,
            entity_version=str(AdoptionApplication.ENTITY_VERSION),
        )
        if not response:
            return {"error": "AdoptionApplication not found", "code": "NOT_FOUND"}, 404
        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error getting AdoptionApplication %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@adoption_applications_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(AdoptionApplicationUpdateQueryParams)
@tag(["adoption-applications"])
@operation_id("update_adoption_application")
@validate(
    request=AdoptionApplication,
    responses={
        200: (AdoptionApplicationResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_adoption_application(entity_id: str, data: AdoptionApplication, query_args: AdoptionApplicationUpdateQueryParams) -> ResponseReturnValue:
    """Update AdoptionApplication and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=AdoptionApplication.ENTITY_NAME,
            transition=transition,
            entity_version=str(AdoptionApplication.ENTITY_VERSION),
        )
        logger.info("Updated AdoptionApplication %s", entity_id)
        return jsonify(_to_entity_dict(response.data)), 200
    except ValueError as e:
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating AdoptionApplication %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

# Specific AdoptionApplication Operations

@adoption_applications_bp.route("/<entity_id>/start-review", methods=["POST"])
@tag(["adoption-applications"])
@operation_id("start_application_review")
async def start_review(entity_id: str) -> ResponseReturnValue:
    """Start review of an adoption application"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        request_data = await request.get_json() or {}
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="start_review",
            entity_class=AdoptionApplication.ENTITY_NAME,
            entity_version=str(AdoptionApplication.ENTITY_VERSION),
            parameters=request_data,
        )
        logger.info("Started review for AdoptionApplication %s", entity_id)
        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error starting review for AdoptionApplication %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@adoption_applications_bp.route("/<entity_id>/approve", methods=["POST"])
@tag(["adoption-applications"])
@operation_id("approve_application")
async def approve_application(entity_id: str) -> ResponseReturnValue:
    """Approve an adoption application"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        request_data = await request.get_json() or {}
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="approve",
            entity_class=AdoptionApplication.ENTITY_NAME,
            entity_version=str(AdoptionApplication.ENTITY_VERSION),
            parameters=request_data,
        )
        logger.info("Approved AdoptionApplication %s", entity_id)
        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error approving AdoptionApplication %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@adoption_applications_bp.route("/<entity_id>/reject", methods=["POST"])
@tag(["adoption-applications"])
@operation_id("reject_application")
async def reject_application(entity_id: str) -> ResponseReturnValue:
    """Reject an adoption application"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        request_data = await request.get_json() or {}
        rejection_reason = request_data.get("rejectionReason")
        if not rejection_reason:
            return {"error": "Rejection reason is required", "code": "VALIDATION_ERROR"}, 400
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="reject",
            entity_class=AdoptionApplication.ENTITY_NAME,
            entity_version=str(AdoptionApplication.ENTITY_VERSION),
            parameters={"rejectionReason": rejection_reason},
        )
        logger.info("Rejected AdoptionApplication %s", entity_id)
        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error rejecting AdoptionApplication %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@adoption_applications_bp.route("/<entity_id>/expire", methods=["POST"])
@tag(["adoption-applications"])
@operation_id("expire_application")
async def expire_application(entity_id: str) -> ResponseReturnValue:
    """Expire an adoption application"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        request_data = await request.get_json() or {}
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="expire",
            entity_class=AdoptionApplication.ENTITY_NAME,
            entity_version=str(AdoptionApplication.ENTITY_VERSION),
            parameters=request_data,
        )
        logger.info("Expired AdoptionApplication %s", entity_id)
        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error expiring AdoptionApplication %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
