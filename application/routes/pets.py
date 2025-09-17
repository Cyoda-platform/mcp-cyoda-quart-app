"""
Pet Routes for Purrfect Pets API

Manages all Pet-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag, validate, validate_querystring

from application.entity.pet.version_1.pet import Pet
from services.services import get_entity_service

logger = logging.getLogger(__name__)

# Create blueprint
pets_bp = Blueprint("pets", __name__, url_prefix="/api/v1/pets")

# Service proxy
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)

service = _ServiceProxy()

# Request/Response models
class PetUpdateQueryParams(BaseModel):
    transition: Optional[str] = Field(default=None, description="Workflow transition to trigger")

class TransitionRequest(BaseModel):
    transition_name: str = Field(..., description="Name of the transition to trigger")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Transition parameters")

class ErrorResponse(BaseModel):
    error: str
    code: Optional[str] = None

class ValidationErrorResponse(BaseModel):
    error: str
    code: str = "VALIDATION_ERROR"

class DeleteResponse(BaseModel):
    deleted: bool
    entity_id: str

class ExistsResponse(BaseModel):
    exists: bool
    entity_id: str

class CountResponse(BaseModel):
    count: int

class PetResponse(BaseModel):
    data: Pet

class PetListResponse(BaseModel):
    data: list[Pet]
    total: int

def _to_entity_dict(entity_data: Any) -> Dict[str, Any]:
    """Convert entity data to dictionary format"""
    if hasattr(entity_data, 'model_dump'):
        return entity_data.model_dump(by_alias=True)
    elif isinstance(entity_data, dict):
        return entity_data
    else:
        return dict(entity_data)

# CRUD Operations

@pets_bp.route("", methods=["POST"])
@tag(["pets"])
@operation_id("create_pet")
@validate(
    request=Pet,
    responses={
        201: (PetResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_pet(data: Pet) -> ResponseReturnValue:
    """Create a new Pet"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info("Created Pet with ID: %s", response.metadata.id)

        # Return created entity directly (thin proxy)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating Pet: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Pet: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@pets_bp.route("/<entity_id>", methods=["GET"])
@tag(["pets"])
@operation_id("get_pet")
@validate(
    responses={
        200: (PetResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_pet(entity_id: str) -> ResponseReturnValue:
    """Get Pet by ID"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Pet not found", "code": "NOT_FOUND"}, 404

        # Thin proxy: return the entity directly
        return _to_entity_dict(response.data), 200

    except Exception as e:
        logger.exception("Error getting Pet %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@pets_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(PetUpdateQueryParams)
@tag(["pets"])
@operation_id("update_pet")
@validate(
    request=Pet,
    responses={
        200: (PetResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_pet(
    entity_id: str, data: Pet, query_args: PetUpdateQueryParams
) -> ResponseReturnValue:
    """Update Pet and optionally trigger workflow transition"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400

        # Get transition from query parameters
        transition: Optional[str] = query_args.transition

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        # Update the entity
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Pet.ENTITY_NAME,
            transition=transition,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info("Updated Pet %s", entity_id)

        # Return updated entity directly (thin proxy)
        return jsonify(_to_entity_dict(response.data)), 200

    except ValueError as e:
        logger.warning("Validation error updating Pet %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating Pet %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@pets_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["pets"])
@operation_id("delete_pet")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_pet(entity_id: str) -> ResponseReturnValue:
    """Delete Pet by ID"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400

        # Check if entity exists first
        exists = await service.exists_by_id(
            entity_id=entity_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        if not exists:
            return {"error": "Pet not found", "code": "NOT_FOUND"}, 404

        # Delete the entity
        await service.delete(
            entity_id=entity_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info("Deleted Pet %s", entity_id)

        return {"deleted": True, "entity_id": entity_id}, 200

    except Exception as e:
        logger.exception("Error deleting Pet %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@pets_bp.route("", methods=["GET"])
@tag(["pets"])
@operation_id("list_pets")
@validate(
    responses={
        200: (PetListResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_pets() -> ResponseReturnValue:
    """List all Pets with optional pagination"""
    try:
        # Get pagination parameters
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 50))
        
        # Calculate offset
        offset = (page - 1) * limit

        # Get entities with pagination
        response = await service.get_all(
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
            limit=limit,
            offset=offset,
        )

        # Get total count
        total = await service.count(
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        # Convert entities to dict format
        entities = [_to_entity_dict(entity.data) for entity in response]

        return {"data": entities, "total": total}, 200

    except Exception as e:
        logger.exception("Error listing Pets: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

# Specific Pet Operations

@pets_bp.route("/<entity_id>/reserve", methods=["POST"])
@tag(["pets"])
@operation_id("reserve_pet")
@validate(
    responses={
        200: (PetResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def reserve_pet(entity_id: str) -> ResponseReturnValue:
    """Reserve a pet for adoption"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400

        # Get request parameters
        request_data = await request.get_json() or {}
        customer_id = request_data.get("customerId")
        application_id = request_data.get("applicationId")

        if not customer_id:
            return {"error": "Customer ID is required", "code": "VALIDATION_ERROR"}, 400
        if not application_id:
            return {"error": "Application ID is required", "code": "VALIDATION_ERROR"}, 400

        # Execute transition with parameters
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="reserve",
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
            parameters={
                "customerId": customer_id,
                "applicationId": application_id,
            },
        )

        logger.info("Reserved Pet %s for customer %s", entity_id, customer_id)

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Validation error reserving Pet %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error reserving Pet %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@pets_bp.route("/<entity_id>/adopt", methods=["POST"])
@tag(["pets"])
@operation_id("adopt_pet")
@validate(
    responses={
        200: (PetResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def adopt_pet(entity_id: str) -> ResponseReturnValue:
    """Complete adoption of a reserved pet"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400

        # Get adoption details from request
        adoption_details = await request.get_json() or {}

        # Execute transition with adoption details
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="adopt",
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
            parameters={"adoptionDetails": adoption_details},
        )

        logger.info("Adopted Pet %s", entity_id)

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Validation error adopting Pet %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error adopting Pet %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@pets_bp.route("/<entity_id>/medical-hold", methods=["POST"])
@tag(["pets"])
@operation_id("place_pet_medical_hold")
@validate(
    responses={
        200: (PetResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def place_medical_hold(entity_id: str) -> ResponseReturnValue:
    """Place pet on medical hold"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400

        # Get medical hold details from request
        request_data = await request.get_json() or {}
        medical_notes = request_data.get("medicalNotes")
        expected_duration = request_data.get("expectedDuration")

        if not medical_notes:
            return {"error": "Medical notes are required", "code": "VALIDATION_ERROR"}, 400

        # Execute transition with medical hold details
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="medical_hold",
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
            parameters={
                "medicalNotes": medical_notes,
                "expectedDuration": expected_duration,
            },
        )

        logger.info("Placed Pet %s on medical hold", entity_id)

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Validation error placing Pet %s on medical hold: %s", entity_id, str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error placing Pet %s on medical hold: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500

@pets_bp.route("/<entity_id>/medical-clearance", methods=["POST"])
@tag(["pets"])
@operation_id("clear_pet_medical_hold")
@validate(
    responses={
        200: (PetResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def clear_medical_hold(entity_id: str) -> ResponseReturnValue:
    """Clear pet from medical hold"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return jsonify({"error": "Entity ID is required", "code": "INVALID_ID"}), 400

        # Get clearance details from request
        request_data = await request.get_json() or {}
        clearance_notes = request_data.get("clearanceNotes")
        veterinarian_approval = request_data.get("veterinarianApproval")
        treatment_complete = request_data.get("treatmentComplete")

        if not veterinarian_approval:
            return {"error": "Veterinarian approval is required", "code": "VALIDATION_ERROR"}, 400
        if not treatment_complete:
            return {"error": "Treatment must be completed", "code": "VALIDATION_ERROR"}, 400

        # Execute transition with clearance details
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="medical_clearance",
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
            parameters={
                "clearanceNotes": clearance_notes,
                "veterinarianApproval": veterinarian_approval,
                "treatmentComplete": treatment_complete,
            },
        )

        logger.info("Cleared Pet %s from medical hold", entity_id)

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Validation error clearing Pet %s from medical hold: %s", entity_id, str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error clearing Pet %s from medical hold: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
