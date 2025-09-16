"""
Pet Routes for Purrfect Pets API.

Provides RESTful endpoints for managing pets.
"""
import logging
from typing import Dict, Any, Optional
from quart import Blueprint, request, jsonify

from application.entity.pet.version_1.pet import Pet
from common.service.entity_service import EntityService

logger = logging.getLogger(__name__)

# Create blueprint
pet_bp = Blueprint('pets', __name__, url_prefix='/pets')


@pet_bp.route('', methods=['GET'])
async def get_pets():
    """Get all pets with optional filtering."""
    try:
        # Get query parameters
        species = request.args.get('species')
        owner_id = request.args.get('owner_id')
        is_active = request.args.get('is_active')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # Build search conditions
        search_conditions = {}
        if species:
            search_conditions['species'] = species
        if owner_id:
            search_conditions['owner_id'] = owner_id
        if is_active is not None:
            search_conditions['is_active'] = is_active.lower() == 'true'
        
        # Get entity service
        entity_service = _get_entity_service()
        
        # Search pets
        if search_conditions:
            pets = await entity_service.search("Pet", search_conditions)
        else:
            pets = await entity_service.find_all("Pet")
        
        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_pets = pets[start_idx:end_idx] if pets else []
        
        # Convert to response format
        pet_data = []
        for pet in paginated_pets:
            pet_dict = pet.dict() if hasattr(pet, 'dict') else pet
            # Use technical IDs for performance
            pet_response = {
                'technical_id': pet_dict.get('technical_id'),
                'pet_id': pet_dict.get('pet_id'),
                'name': pet_dict.get('name'),
                'species': pet_dict.get('species'),
                'breed': pet_dict.get('breed'),
                'age': pet_dict.get('age'),
                'owner_id': pet_dict.get('owner_id'),
                'state': pet_dict.get('state')
            }
            pet_data.append(pet_response)
        
        return jsonify({
            'pets': pet_data,
            'total': len(pets) if pets else 0,
            'page': page,
            'limit': limit
        })
        
    except Exception as e:
        logger.exception("Failed to get pets")
        return jsonify({'error': 'Failed to retrieve pets', 'message': str(e)}), 500


@pet_bp.route('/<pet_id>', methods=['GET'])
async def get_pet(pet_id: str):
    """Get a specific pet by ID."""
    try:
        entity_service = _get_entity_service()
        
        # Try to get by business ID first, then by technical ID
        try:
            pet = await entity_service.find_by_business_id("Pet", pet_id)
        except:
            pet = await entity_service.get_by_id(pet_id)
        
        if not pet:
            return jsonify({'error': 'Pet not found'}), 404
        
        # Convert to response format
        pet_dict = pet.dict() if hasattr(pet, 'dict') else pet
        return jsonify(pet_dict)
        
    except Exception as e:
        logger.exception(f"Failed to get pet {pet_id}")
        return jsonify({'error': 'Failed to retrieve pet', 'message': str(e)}), 500


@pet_bp.route('', methods=['POST'])
async def create_pet():
    """Create a new pet."""
    try:
        data = await request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Validate required fields
        required_fields = ['name', 'species', 'owner_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create pet entity
        pet = Pet(**data)
        
        # Get entity service
        entity_service = _get_entity_service()
        
        # Save pet (triggers workflow: initial → registered → active)
        saved_pet = await entity_service.save(pet)
        
        # Return response with technical ID
        return jsonify({
            'technical_id': saved_pet.technical_id,
            'pet_id': saved_pet.pet_id,
            'name': saved_pet.name,
            'species': saved_pet.species,
            'state': saved_pet.state,
            'message': 'Pet registered and activated successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': 'Validation error', 'message': str(e)}), 400
    except Exception as e:
        logger.exception("Failed to create pet")
        return jsonify({'error': 'Failed to create pet', 'message': str(e)}), 500


@pet_bp.route('/<pet_id>', methods=['PUT'])
async def update_pet(pet_id: str):
    """Update an existing pet."""
    try:
        data = await request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        entity_service = _get_entity_service()
        
        # Get existing pet
        try:
            pet = await entity_service.find_by_business_id("Pet", pet_id)
        except:
            pet = await entity_service.get_by_id(pet_id)
        
        if not pet:
            return jsonify({'error': 'Pet not found'}), 404
        
        # Update pet fields
        for key, value in data.items():
            if hasattr(pet, key) and key not in ['pet_id', 'technical_id', 'entity_id']:
                setattr(pet, key, value)
        
        # Get transition from request
        transition = data.get('transition')
        
        # Update pet (transition must be manual if provided)
        if transition:
            updated_pet = await entity_service.update(pet, transition=transition)
        else:
            updated_pet = await entity_service.update(pet)
        
        return jsonify({
            'technical_id': updated_pet.technical_id,
            'pet_id': updated_pet.pet_id,
            'state': updated_pet.state,
            'message': 'Pet updated successfully'
        })
        
    except ValueError as e:
        return jsonify({'error': 'Validation error', 'message': str(e)}), 400
    except Exception as e:
        logger.exception(f"Failed to update pet {pet_id}")
        return jsonify({'error': 'Failed to update pet', 'message': str(e)}), 500


@pet_bp.route('/<pet_id>', methods=['DELETE'])
async def delete_pet(pet_id: str):
    """Delete a pet."""
    try:
        entity_service = _get_entity_service()
        
        # Get existing pet
        try:
            pet = await entity_service.find_by_business_id("Pet", pet_id)
        except:
            pet = await entity_service.get_by_id(pet_id)
        
        if not pet:
            return jsonify({'error': 'Pet not found'}), 404
        
        # Delete pet
        await entity_service.delete(pet.technical_id or pet.entity_id)
        
        return jsonify({'message': 'Pet deleted successfully'})
        
    except Exception as e:
        logger.exception(f"Failed to delete pet {pet_id}")
        return jsonify({'error': 'Failed to delete pet', 'message': str(e)}), 500


def _get_entity_service() -> EntityService:
    """Get entity service instance."""
    from service.services import get_entity_service
    return get_entity_service()
