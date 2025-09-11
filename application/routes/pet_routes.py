"""
Pet Routes for Purrfect Pets API

Manages all Pet-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

import logging
from typing import Any, Dict, List, Optional, Protocol, cast

from pydantic import BaseModel, Field
from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import validate_querystring, validate_request

from services.services import get_entity_service

logger = logging.getLogger(__name__)

pets_bp = Blueprint("pets", __name__, url_prefix="/pets")


# ---- Service typing ---------------------------------------------------------


class _EntityMetadata(Protocol):
    id: str
    state: str


class _SavedEntity(Protocol):
    metadata: _EntityMetadata
    data: Dict[str, Any]


class _ListedEntity(Protocol):
    def get_id(self) -> str: ...
    def get_state(self) -> str: ...

    data: Dict[str, Any]


class EntityServiceProtocol(Protocol):
    async def save(
        self, *, entity: Dict[str, Any], entity_class: str, entity_version: str
    ) -> _SavedEntity: ...

    async def get_by_id(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> Optional[_SavedEntity]: ...

    async def find_all(
        self, *, entity_class: str, entity_version: str
    ) -> List[_ListedEntity]: ...

    async def update(
        self,
        *,
        entity_id: str,
        entity: Dict[str, Any],
        entity_class: str,
        transition: Optional[str],
        entity_version: str,
    ) -> _SavedEntity: ...

    async def execute_transition(
        self,
        *,
        entity_id: str,
        transition: str,
        entity_class: str,
        entity_version: str,
    ) -> _SavedEntity: ...


entity_service: Optional[EntityServiceProtocol] = None


def get_services() -> EntityServiceProtocol:
    """Get services from the registry lazily."""
    global entity_service
    if entity_service is None:
        entity_service = cast(EntityServiceProtocol, get_entity_service())
    return entity_service


# ---- Request/Query Models ---------------------------------------------------


class PetQueryParams(BaseModel):
    """Query parameters for Pet listing"""

    status: Optional[str] = Field(default=None, description="Filter by pet status")
    category: Optional[int] = Field(default=None, description="Filter by category ID")
    tags: Optional[str] = Field(
        default=None, description="Filter by tag names (comma-separated)"
    )
    page: int = Field(default=0, description="Page number")
    size: int = Field(default=20, description="Page size")


class CategoryRequest(BaseModel):
    """Category reference in requests"""

    id: int = Field(..., description="Category ID")


class TagRequest(BaseModel):
    """Tag reference in requests"""

    id: int = Field(..., description="Tag ID")


class PetCreateRequest(BaseModel):
    """Request model for creating a Pet"""

    name: str = Field(..., description="Name of the pet")
    category: CategoryRequest = Field(..., description="Category the pet belongs to")
    photo_urls: List[str] = Field(
        ..., alias="photoUrls", description="List of photo URLs"
    )
    tags: Optional[List[TagRequest]] = Field(default=None, description="List of tags")
    description: Optional[str] = Field(
        default=None, description="Description of the pet"
    )
    price: Optional[float] = Field(default=None, description="Price of the pet")
    birth_date: Optional[str] = Field(
        default=None, alias="birthDate", description="Birth date"
    )
    breed: Optional[str] = Field(default=None, description="Breed of the pet")
    weight: Optional[float] = Field(default=None, description="Weight in kg")
    vaccinated: Optional[bool] = Field(default=None, description="Vaccination status")
    neutered: Optional[bool] = Field(default=None, description="Neutered/spayed status")


class PetUpdateRequest(BaseModel):
    """Request model for updating a Pet"""

    name: Optional[str] = Field(default=None, description="Name of the pet")
    description: Optional[str] = Field(default=None, description="Description")
    price: Optional[float] = Field(default=None, description="Price of the pet")


# ---- Routes -----------------------------------------------------------------


@pets_bp.route("", methods=["GET"])
@validate_querystring(PetQueryParams)
async def get_pets(query_args: PetQueryParams) -> ResponseReturnValue:
    """Get all pets with optional filtering"""
    try:
        service = get_services()

        # Get all pets (filtering would be implemented with search conditions)
        entities = await service.find_all(entity_class="Pet", entity_version="1")

        # Convert to API response format
        pets = []
        for entity in entities:
            pet_data = {
                "id": entity.get_id(),
                "name": entity.data.get("name"),
                "category": entity.data.get("category"),
                "photoUrls": entity.data.get("photoUrls", []),
                "tags": entity.data.get("tags", []),
                "status": _map_state_to_status(entity.get_state()),
                "price": entity.data.get("price"),
            }
            pets.append(pet_data)

        # Apply pagination
        start = query_args.page * query_args.size
        end = start + query_args.size
        paginated_pets = pets[start:end]

        return (
            jsonify(
                {
                    "content": paginated_pets,
                    "totalElements": len(pets),
                    "totalPages": (len(pets) + query_args.size - 1) // query_args.size,
                    "size": query_args.size,
                    "number": query_args.page,
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error getting pets: %s", str(e))
        return jsonify({"error": str(e)}), 500


@pets_bp.route("/<pet_id>", methods=["GET"])
async def get_pet(pet_id: str) -> ResponseReturnValue:
    """Get pet by ID"""
    try:
        service = get_services()

        response = await service.get_by_id(
            entity_id=pet_id, entity_class="Pet", entity_version="1"
        )

        if not response:
            return jsonify({"error": "Pet not found"}), 404

        # Convert to API response format
        pet_data = dict(response.data)
        pet_data["id"] = response.metadata.id
        pet_data["status"] = _map_state_to_status(response.metadata.state)

        return jsonify(pet_data), 200

    except Exception as e:
        logger.exception("Error getting pet %s: %s", pet_id, str(e))
        return jsonify({"error": str(e)}), 500


@pets_bp.route("", methods=["POST"])
@validate_request(PetCreateRequest)
async def create_pet(data: PetCreateRequest) -> ResponseReturnValue:
    """Add a new pet"""
    try:
        service = get_services()

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data, entity_class="Pet", entity_version="1"
        )

        logger.info("Created Pet with ID: %s", response.metadata.id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "name": entity_data.get("name"),
                    "status": _map_state_to_status(response.metadata.state),
                    "message": "Pet created successfully",
                }
            ),
            201,
        )

    except Exception as e:
        logger.exception("Error creating pet: %s", str(e))
        return jsonify({"error": str(e)}), 500


@pets_bp.route("/<pet_id>", methods=["PUT"])
@validate_request(PetUpdateRequest)
async def update_pet(pet_id: str, data: PetUpdateRequest) -> ResponseReturnValue:
    """Update an existing pet"""
    try:
        service = get_services()

        # Get transition from query parameter
        transition: Optional[str] = request.args.get("transitionName")

        # Convert request to entity data (exclude None values)
        entity_data: Dict[str, Any] = {
            k: v for k, v in data.model_dump(exclude_none=True).items()
        }

        # Update the entity
        response = await service.update(
            entity_id=pet_id,
            entity=entity_data,
            entity_class="Pet",
            transition=transition,
            entity_version="1",
        )

        logger.info("Updated Pet %s", pet_id)

        result = {
            "id": response.metadata.id,
            "name": entity_data.get("name", ""),
            "status": _map_state_to_status(response.metadata.state),
            "message": "Pet updated successfully",
        }

        return jsonify(result), 200

    except Exception as e:
        logger.exception("Error updating pet %s: %s", pet_id, str(e))
        return jsonify({"error": str(e)}), 500


@pets_bp.route("/<pet_id>", methods=["DELETE"])
async def delete_pet(pet_id: str) -> ResponseReturnValue:
    """Delete a pet (mark as unavailable)"""
    try:
        service = get_services()

        # Get transition from query parameter
        transition: Optional[str] = request.args.get("transitionName")

        if transition != "markUnavailable":
            return jsonify({"error": "transitionName=markUnavailable is required"}), 400

        # Execute transition to mark as unavailable
        await service.execute_transition(
            entity_id=pet_id,
            transition="transition_to_unavailable",
            entity_class="Pet",
            entity_version="1",
        )

        logger.info("Marked Pet %s as unavailable", pet_id)

        return jsonify({"message": "Pet marked as unavailable successfully"}), 200

    except Exception as e:
        logger.exception("Error deleting pet %s: %s", pet_id, str(e))
        return jsonify({"error": str(e)}), 500


def _map_state_to_status(state: str) -> str:
    """Map entity state to API status"""
    state_mapping = {
        "available": "AVAILABLE",
        "pending": "PENDING",
        "reserved": "RESERVED",
        "sold": "SOLD",
        "unavailable": "UNAVAILABLE",
    }
    return state_mapping.get(state, "UNKNOWN")
