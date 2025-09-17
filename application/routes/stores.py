"""
Store Routes for Purrfect Pets API

Manages all Store-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag, validate, validate_querystring

from application.entity.store.version_1.store import Store
from services.services import get_entity_service

logger = logging.getLogger(__name__)

# Create blueprint
stores_bp = Blueprint("stores", __name__, url_prefix="/api/v1/stores")

# Service proxy
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)

service = _ServiceProxy()

# Request/Response models
class StoreUpdateQueryParams(BaseModel):
    transition: Optional[str] = Field(default=None, description="Workflow transition to trigger")

class ErrorResponse(BaseModel):
    error: str
    code: Optional[str] = None

class ValidationErrorResponse(BaseModel):
    error: str
    code: str = "VALIDATION_ERROR"

class StoreResponse(BaseModel):
    data: Store

def _to_entity_dict(entity_data: Any) -> Dict[str, Any]:
    """Convert entity data to dictionary format"""
    if hasattr(entity_data, 'model_dump'):
        return entity_data.model_dump(by_alias=True)
    elif isinstance(entity_data, dict):
        return entity_data
    else:
        return dict(entity_data)

# CRUD Operations

@stores_bp.route("", methods=["POST"])
@tag(["stores"])
@operation_id("create_store")
@validate(
    request=Store,
    responses={
        201: (StoreResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_store(data: Store) -> ResponseReturnValue:
    """Create a new Store"""
    try:
        entity_data = data.model_dump(by_alias=True)
        response = await service.save(
            entity=entity_data,
            entity_class=Store.ENTITY_NAME,
            entity_version=str(Store.ENTITY_VERSION),
        )
        logger.info("Created Store with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201
    except ValueError as e:
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Store: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@stores_bp.route("/<entity_id>", methods=["GET"])
@tag(["stores"])
@operation_id("get_store")
async def get_store(entity_id: str) -> ResponseReturnValue:
    """Get Store by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Store.ENTITY_NAME,
            entity_version=str(Store.ENTITY_VERSION),
        )
        if not response:
            return {"error": "Store not found", "code": "NOT_FOUND"}, 404
        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error getting Store %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@stores_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(StoreUpdateQueryParams)
@tag(["stores"])
@operation_id("update_store")
@validate(
    request=Store,
    responses={
        200: (StoreResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_store(entity_id: str, data: Store, query_args: StoreUpdateQueryParams) -> ResponseReturnValue:
    """Update Store and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Store.ENTITY_NAME,
            transition=transition,
            entity_version=str(Store.ENTITY_VERSION),
        )
        logger.info("Updated Store %s", entity_id)
        return jsonify(_to_entity_dict(response.data)), 200
    except ValueError as e:
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating Store %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

# Specific Store Operations

@stores_bp.route("/<entity_id>/close-temporarily", methods=["POST"])
@tag(["stores"])
@operation_id("close_store_temporarily")
async def close_temporarily(entity_id: str) -> ResponseReturnValue:
    """Temporarily close a store"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        request_data = await request.get_json() or {}
        closure_reason = request_data.get("closureReason")
        if not closure_reason:
            return {"error": "Closure reason is required", "code": "VALIDATION_ERROR"}, 400
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="close_temporarily",
            entity_class=Store.ENTITY_NAME,
            entity_version=str(Store.ENTITY_VERSION),
            parameters={"closureReason": closure_reason},
        )
        logger.info("Temporarily closed Store %s", entity_id)
        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error closing Store %s temporarily: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@stores_bp.route("/<entity_id>/reopen", methods=["POST"])
@tag(["stores"])
@operation_id("reopen_store")
async def reopen_store(entity_id: str) -> ResponseReturnValue:
    """Reopen a temporarily closed store"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        request_data = await request.get_json() or {}
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="reopen",
            entity_class=Store.ENTITY_NAME,
            entity_version=str(Store.ENTITY_VERSION),
            parameters=request_data,
        )
        logger.info("Reopened Store %s", entity_id)
        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error reopening Store %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
