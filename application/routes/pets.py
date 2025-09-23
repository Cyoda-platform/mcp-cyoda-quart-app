"""
Pet Routes for Product Performance Analysis and Reporting System

Manages all Pet-related API endpoints including CRUD operations
and workflow transitions following the thin proxy pattern.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag, validate, validate_querystring
from pydantic import BaseModel, Field

from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service
from application.entity.pet.version_1.pet import Pet


# Request/Response models
class PetQueryParams(BaseModel):
    """Query parameters for listing pets"""
    status: Optional[str] = Field(None, description="Filter by pet status")
    category: Optional[str] = Field(None, description="Filter by category name")
    limit: int = Field(50, ge=1, le=1000, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")


class PetUpdateQueryParams(BaseModel):
    """Query parameters for updating pets"""
    transition: Optional[str] = Field(None, description="Workflow transition to trigger")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class DeleteResponse(BaseModel):
    """Delete response model"""
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Success message")
    entity_id: str = Field(..., description="ID of deleted entity")


logger = logging.getLogger(__name__)

# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


pets_bp = Blueprint("pets", __name__, url_prefix="/api/pets")


@pets_bp.route("", methods=["POST"])
@tag(["pets"])
@operation_id("create_pet")
@validate(
    request=Pet,
    responses={
        201: (Pet, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_pet(data: Pet) -> ResponseReturnValue:
    """Create a new Pet entity"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        service = get_entity_service()
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
        200: (Pet, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_pet(entity_id: str) -> ResponseReturnValue:
    """Get Pet by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        service = get_entity_service()
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Pet not found", "code": "NOT_FOUND"}, 404

        # Thin proxy: return the entity directly
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting Pet %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@pets_bp.route("", methods=["GET"])
@validate_querystring(PetQueryParams)
@tag(["pets"])
@operation_id("list_pets")
@validate(
    responses={
        200: (Dict[str, Any], None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_pets(query_args: PetQueryParams) -> ResponseReturnValue:
    """List Pets with optional filtering"""
    try:
        service = get_entity_service()
        
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.status:
            search_conditions["status"] = query_args.status

        if query_args.category:
            search_conditions["category.name"] = query_args.category

        # Get entities
        if search_conditions:
            # Build search condition request
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=Pet.ENTITY_NAME,
                condition=condition,
                entity_version=str(Pet.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=Pet.ENTITY_NAME,
                entity_version=str(Pet.ENTITY_VERSION),
            )

        # Thin proxy: return entities directly
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return {"pets": paginated_entities, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error listing Pets: %s", str(e))
        return {"error": str(e)}, 500


@pets_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(PetUpdateQueryParams)
@tag(["pets"])
@operation_id("update_pet")
@validate(
    request=Pet,
    responses={
        200: (Pet, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_pet(
    entity_id: str, data: Pet, query_args: PetUpdateQueryParams
) -> ResponseReturnValue:
    """Update Pet and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        # Get transition from query parameters
        transition: Optional[str] = query_args.transition

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        # Update the entity
        service = get_entity_service()
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Pet.ENTITY_NAME,
            transition=transition,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info("Updated Pet %s", entity_id)

        # Return updated entity directly (thin proxy)
        return _to_entity_dict(response.data), 200

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
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_pet(entity_id: str) -> ResponseReturnValue:
    """Delete Pet"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        service = get_entity_service()
        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        logger.info("Deleted Pet %s", entity_id)

        # Thin proxy: return success message
        response = DeleteResponse(
            success=True,
            message="Pet deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting Pet %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@pets_bp.route("/<entity_id>/transitions", methods=["GET"])
@tag(["pets"])
@operation_id("get_pet_transitions")
@validate(
    responses={
        200: (Dict[str, Any], None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_available_transitions(entity_id: str) -> ResponseReturnValue:
    """Get available workflow transitions for Pet"""
    try:
        service = get_entity_service()
        transitions = await service.get_transitions(
            entity_id=entity_id,
            entity_class=Pet.ENTITY_NAME,
            entity_version=str(Pet.ENTITY_VERSION),
        )

        return {
            "entity_id": entity_id,
            "available_transitions": transitions,
        }, 200

    except Exception as e:
        logger.exception("Error getting transitions for Pet %s: %s", entity_id, str(e))
        return {"error": str(e)}, 500


@pets_bp.route("/sync-from-api", methods=["POST"])
@tag(["pets"])
@operation_id("sync_pets_from_api")
@validate(
    responses={
        200: (Dict[str, Any], None),
        500: (ErrorResponse, None),
    }
)
async def sync_pets_from_api() -> ResponseReturnValue:
    """Sync pets from Pet Store API"""
    try:
        import httpx

        service = get_entity_service()

        # Fetch pets from Pet Store API
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get available pets
            response = await client.get("https://petstore.swagger.io/v2/pet/findByStatus?status=available")
            available_pets = response.json() if response.status_code == 200 else []

            # Get pending pets
            response = await client.get("https://petstore.swagger.io/v2/pet/findByStatus?status=pending")
            pending_pets = response.json() if response.status_code == 200 else []

            # Get sold pets
            response = await client.get("https://petstore.swagger.io/v2/pet/findByStatus?status=sold")
            sold_pets = response.json() if response.status_code == 200 else []

        all_pets = available_pets + pending_pets + sold_pets
        created_count = 0

        for pet_data in all_pets:
            try:
                # Convert Pet Store API format to our Pet entity format
                pet_entity_data = {
                    "petId": pet_data.get("id"),
                    "name": pet_data.get("name", "Unknown"),
                    "category": pet_data.get("category"),
                    "photoUrls": pet_data.get("photoUrls", []),
                    "tags": pet_data.get("tags", []),
                    "status": pet_data.get("status"),
                }

                # Create Pet entity
                await service.save(
                    entity=pet_entity_data,
                    entity_class=Pet.ENTITY_NAME,
                    entity_version=str(Pet.ENTITY_VERSION),
                )
                created_count += 1

            except Exception as e:
                logger.warning(f"Failed to create pet {pet_data.get('id', 'unknown')}: {str(e)}")
                continue

        return {
            "message": f"Successfully synced {created_count} pets from Pet Store API",
            "total_fetched": len(all_pets),
            "created": created_count,
        }, 200

    except Exception as e:
        logger.exception("Error syncing pets from API: %s", str(e))
        return {"error": str(e), "code": "SYNC_ERROR"}, 500
