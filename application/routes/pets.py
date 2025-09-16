"""Pet routes for Purrfect Pets API."""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from quart import Blueprint, jsonify, request, abort
from quart_schema import validate_request, validate_querystring
from pydantic import BaseModel, Field

from service.services import get_entity_service, get_auth_service
from application.entity.pet.version_1.pet import Pet

logger = logging.getLogger(__name__)

pets_bp = Blueprint('pets', __name__, url_prefix='/api/pets')

ENTITY_VERSION = "1"


class PetQuery(BaseModel):
    """Query parameters for pet filtering."""
    category: Optional[str] = Field(None, description="Filter by category")
    status: Optional[str] = Field(None, description="Filter by availability status")
    minPrice: Optional[float] = Field(None, ge=0, description="Minimum price filter")
    maxPrice: Optional[float] = Field(None, ge=0, description="Maximum price filter")
    page: Optional[int] = Field(0, ge=0, description="Page number for pagination")
    size: Optional[int] = Field(10, ge=1, le=100, description="Page size for pagination")


class PetRequest(BaseModel):
    """Request model for creating/updating pets."""
    name: str = Field(..., description="Pet's name")
    category: str = Field(..., description="Pet category")
    breed: str = Field(..., description="Pet breed")
    age: int = Field(..., ge=0, description="Pet age in years")
    color: str = Field(..., description="Pet's primary color")
    weight: float = Field(..., gt=0, description="Pet weight in kg")
    description: str = Field(..., description="Detailed description")
    price: float = Field(..., gt=0, description="Pet price in USD")
    imageUrl: Optional[str] = Field(None, description="URL to pet's photo")


class PetUpdateRequest(BaseModel):
    """Request model for updating pets."""
    transitionName: Optional[str] = Field(None, description="Workflow transition name")
    name: Optional[str] = Field(None, description="Pet's name")
    category: Optional[str] = Field(None, description="Pet category")
    breed: Optional[str] = Field(None, description="Pet breed")
    age: Optional[int] = Field(None, ge=0, description="Pet age in years")
    color: Optional[str] = Field(None, description="Pet's primary color")
    weight: Optional[float] = Field(None, gt=0, description="Pet weight in kg")
    description: Optional[str] = Field(None, description="Detailed description")
    price: Optional[float] = Field(None, gt=0, description="Pet price in USD")
    imageUrl: Optional[str] = Field(None, description="URL to pet's photo")
    ownerId: Optional[int] = Field(None, description="Owner ID")


def get_services():
    """Get entity service and auth service."""
    return get_entity_service(), get_auth_service()


@pets_bp.route("", methods=["GET"])
@validate_querystring(PetQuery)
async def get_pets():
    """Get all pets with optional filtering."""
    entity_service, cyoda_auth_service = get_services()
    args = PetQuery(**request.args)
    
    try:
        # Get all pets from entity service
        pets_response = await entity_service.find_all("Pet", ENTITY_VERSION)
        pets = pets_response if pets_response else []
        
        # Apply filters
        filtered_pets = []
        for pet_data in pets:
            # Convert to Pet entity for easier filtering
            pet = Pet(**pet_data) if isinstance(pet_data, dict) else pet_data
            
            # Apply category filter
            if args.category and pet.category != args.category:
                continue
                
            # Apply status filter (map to state)
            if args.status:
                status_map = {
                    "AVAILABLE": "available",
                    "PENDING": "pending", 
                    "SOLD": "sold",
                    "RESERVED": "reserved",
                    "UNAVAILABLE": "unavailable"
                }
                expected_state = status_map.get(args.status.upper())
                if expected_state and pet.state != expected_state:
                    continue
            
            # Apply price filters
            if args.minPrice is not None and pet.price < args.minPrice:
                continue
            if args.maxPrice is not None and pet.price > args.maxPrice:
                continue
                
            filtered_pets.append(pet)
        
        # Apply pagination
        total_elements = len(filtered_pets)
        start_idx = args.page * args.size
        end_idx = start_idx + args.size
        paginated_pets = filtered_pets[start_idx:end_idx]
        
        # Convert to response format
        content = []
        for pet in paginated_pets:
            content.append({
                "id": pet.id,
                "name": pet.name,
                "category": pet.category,
                "breed": pet.breed,
                "age": pet.age,
                "color": pet.color,
                "weight": pet.weight,
                "price": pet.price,
                "state": pet.state.upper() if pet.state else "UNKNOWN"
            })
        
        total_pages = (total_elements + args.size - 1) // args.size
        
        response = {
            "content": content,
            "totalElements": total_elements,
            "totalPages": total_pages
        }
        
        logger.info(f"Retrieved {len(content)} pets (page {args.page})")
        return jsonify(response)

    except Exception as e:
        logger.exception(f"Failed to get pets: {e}")
        return jsonify({"error": f"Failed to get pets: {str(e)}"}), 500


@pets_bp.route("/<int:pet_id>", methods=["GET"])
async def get_pet(pet_id: int):
    """Get pet by ID."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Find pet by business ID
        pet_response = await entity_service.find_by_business_id(
            "Pet", str(pet_id), "id", ENTITY_VERSION
        )

        if not pet_response:
            return jsonify({"error": "Pet not found"}), 404

        pet_data = pet_response.entity
        pet = Pet(**pet_data) if isinstance(pet_data, dict) else pet_data

        response = {
            "id": pet.id,
            "name": pet.name,
            "category": pet.category,
            "breed": pet.breed,
            "age": pet.age,
            "color": pet.color,
            "weight": pet.weight,
            "description": pet.description,
            "price": pet.price,
            "imageUrl": pet.imageUrl,
            "ownerId": pet.ownerId,
            "state": pet.state.upper() if pet.state else "UNKNOWN",
            "createdAt": pet.createdAt,
            "updatedAt": pet.updatedAt
        }

        logger.info(f"Retrieved pet {pet_id}")
        return jsonify(response)

    except Exception as e:
        logger.exception(f"Failed to get pet {pet_id}: {e}")
        return jsonify({"error": f"Failed to get pet: {str(e)}"}), 500


@pets_bp.route("", methods=["POST"])
@validate_request(PetRequest)
async def create_pet(data: PetRequest):
    """Create new pet."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Generate unique ID
        pet_id = len(await entity_service.find_all("Pet", ENTITY_VERSION) or []) + 1

        # Create pet entity
        pet_data = {
            "id": pet_id,
            "name": data.name,
            "category": data.category,
            "breed": data.breed,
            "age": data.age,
            "color": data.color,
            "weight": data.weight,
            "description": data.description,
            "price": data.price,
            "imageUrl": data.imageUrl,
            "ownerId": None,
            "state": "initial_state"
        }

        # Save pet
        pet_response = await entity_service.save(pet_data, "Pet", ENTITY_VERSION)

        response = {
            "id": pet_id,
            "name": data.name,
            "state": "AVAILABLE",
            "createdAt": datetime.now(timezone.utc).isoformat()
        }

        logger.info(f"Created pet {pet_id}")
        return jsonify(response), 201

    except Exception as e:
        logger.exception(f"Failed to create pet: {e}")
        return jsonify({"error": f"Failed to create pet: {str(e)}"}), 500
