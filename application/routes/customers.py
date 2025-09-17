"""
Customer Routes for Purrfect Pets API

Manages all Customer-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag, validate, validate_querystring

from application.entity.customer.version_1.customer import Customer
from services.services import get_entity_service

logger = logging.getLogger(__name__)

# Create blueprint
customers_bp = Blueprint("customers", __name__, url_prefix="/api/v1/customers")

# Service proxy
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)

service = _ServiceProxy()

# Request/Response models
class CustomerUpdateQueryParams(BaseModel):
    transition: Optional[str] = Field(default=None, description="Workflow transition to trigger")

class ErrorResponse(BaseModel):
    error: str
    code: Optional[str] = None

class ValidationErrorResponse(BaseModel):
    error: str
    code: str = "VALIDATION_ERROR"

class CustomerResponse(BaseModel):
    data: Customer

def _to_entity_dict(entity_data: Any) -> Dict[str, Any]:
    """Convert entity data to dictionary format"""
    if hasattr(entity_data, 'model_dump'):
        return entity_data.model_dump(by_alias=True)
    elif isinstance(entity_data, dict):
        return entity_data
    else:
        return dict(entity_data)

# CRUD Operations

@customers_bp.route("", methods=["POST"])
@tag(["customers"])
@operation_id("create_customer")
@validate(
    request=Customer,
    responses={
        201: (CustomerResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_customer(data: Customer) -> ResponseReturnValue:
    """Create a new Customer"""
    try:
        entity_data = data.model_dump(by_alias=True)
        response = await service.save(
            entity=entity_data,
            entity_class=Customer.ENTITY_NAME,
            entity_version=str(Customer.ENTITY_VERSION),
        )
        logger.info("Created Customer with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201
    except ValueError as e:
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Customer: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@customers_bp.route("/<entity_id>", methods=["GET"])
@tag(["customers"])
@operation_id("get_customer")
async def get_customer(entity_id: str) -> ResponseReturnValue:
    """Get Customer by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Customer.ENTITY_NAME,
            entity_version=str(Customer.ENTITY_VERSION),
        )
        if not response:
            return {"error": "Customer not found", "code": "NOT_FOUND"}, 404
        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error getting Customer %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@customers_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(CustomerUpdateQueryParams)
@tag(["customers"])
@operation_id("update_customer")
@validate(
    request=Customer,
    responses={
        200: (CustomerResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_customer(entity_id: str, data: Customer, query_args: CustomerUpdateQueryParams) -> ResponseReturnValue:
    """Update Customer and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Customer.ENTITY_NAME,
            transition=transition,
            entity_version=str(Customer.ENTITY_VERSION),
        )
        logger.info("Updated Customer %s", entity_id)
        return jsonify(_to_entity_dict(response.data)), 200
    except ValueError as e:
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating Customer %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

# Specific Customer Operations

@customers_bp.route("/<entity_id>/suspend", methods=["POST"])
@tag(["customers"])
@operation_id("suspend_customer")
async def suspend_customer(entity_id: str) -> ResponseReturnValue:
    """Suspend a customer account"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        request_data = await request.get_json() or {}
        suspension_reason = request_data.get("suspensionReason")
        if not suspension_reason:
            return {"error": "Suspension reason is required", "code": "VALIDATION_ERROR"}, 400
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="suspend",
            entity_class=Customer.ENTITY_NAME,
            entity_version=str(Customer.ENTITY_VERSION),
            parameters={"suspensionReason": suspension_reason},
        )
        logger.info("Suspended Customer %s", entity_id)
        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error suspending Customer %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@customers_bp.route("/<entity_id>/reactivate", methods=["POST"])
@tag(["customers"])
@operation_id("reactivate_customer")
async def reactivate_customer(entity_id: str) -> ResponseReturnValue:
    """Reactivate a suspended customer account"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        request_data = await request.get_json() or {}
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="reactivate",
            entity_class=Customer.ENTITY_NAME,
            entity_version=str(Customer.ENTITY_VERSION),
            parameters=request_data,
        )
        logger.info("Reactivated Customer %s", entity_id)
        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error reactivating Customer %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@customers_bp.route("/<entity_id>/blacklist", methods=["POST"])
@tag(["customers"])
@operation_id("blacklist_customer")
async def blacklist_customer(entity_id: str) -> ResponseReturnValue:
    """Blacklist a customer permanently"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400
        request_data = await request.get_json() or {}
        blacklist_reason = request_data.get("blacklistReason")
        if not blacklist_reason:
            return {"error": "Blacklist reason is required", "code": "VALIDATION_ERROR"}, 400
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="blacklist",
            entity_class=Customer.ENTITY_NAME,
            entity_version=str(Customer.ENTITY_VERSION),
            parameters={"blacklistReason": blacklist_reason},
        )
        logger.info("Blacklisted Customer %s", entity_id)
        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error blacklisting Customer %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
