"""
Owner Routes for Purrfect Pets API.
"""
import logging
from quart import Blueprint, request, jsonify

from application.entity.owner.version_1.owner import Owner

logger = logging.getLogger(__name__)

owner_bp = Blueprint('owners', __name__, url_prefix='/owners')


@owner_bp.route('', methods=['GET'])
async def get_owners():
    """Get all owners with optional filtering."""
    try:
        # Get query parameters
        email = request.args.get('email')
        city = request.args.get('city')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        # Build search conditions
        search_conditions = {}
        if email:
            search_conditions['email'] = email
        if city:
            search_conditions['city'] = city
        
        entity_service = _get_entity_service()
        
        if search_conditions:
            owners = await entity_service.search("Owner", search_conditions)
        else:
            owners = await entity_service.find_all("Owner")
        
        # Apply pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_owners = owners[start_idx:end_idx] if owners else []
        
        # Convert to response format
        owner_data = []
        for owner in paginated_owners:
            owner_dict = owner.dict() if hasattr(owner, 'dict') else owner
            owner_response = {
                'technical_id': owner_dict.get('technical_id'),
                'owner_id': owner_dict.get('owner_id'),
                'first_name': owner_dict.get('first_name'),
                'last_name': owner_dict.get('last_name'),
                'email': owner_dict.get('email'),
                'phone': owner_dict.get('phone'),
                'state': owner_dict.get('state')
            }
            owner_data.append(owner_response)
        
        return jsonify({
            'owners': owner_data,
            'total': len(owners) if owners else 0,
            'page': page,
            'limit': limit
        })
        
    except Exception as e:
        logger.exception("Failed to get owners")
        return jsonify({'error': 'Failed to retrieve owners', 'message': str(e)}), 500


@owner_bp.route('/<owner_id>', methods=['GET'])
async def get_owner(owner_id: str):
    """Get a specific owner by ID."""
    try:
        entity_service = _get_entity_service()
        
        try:
            owner = await entity_service.find_by_business_id("Owner", owner_id)
        except:
            owner = await entity_service.get_by_id(owner_id)
        
        if not owner:
            return jsonify({'error': 'Owner not found'}), 404
        
        owner_dict = owner.dict() if hasattr(owner, 'dict') else owner
        return jsonify(owner_dict)
        
    except Exception as e:
        logger.exception(f"Failed to get owner {owner_id}")
        return jsonify({'error': 'Failed to retrieve owner', 'message': str(e)}), 500


@owner_bp.route('', methods=['POST'])
async def create_owner():
    """Create a new owner."""
    try:
        data = await request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        required_fields = ['first_name', 'last_name', 'email', 'phone']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        owner = Owner(**data)
        entity_service = _get_entity_service()
        saved_owner = await entity_service.save(owner)
        
        return jsonify({
            'technical_id': saved_owner.technical_id,
            'owner_id': saved_owner.owner_id,
            'first_name': saved_owner.first_name,
            'last_name': saved_owner.last_name,
            'email': saved_owner.email,
            'state': saved_owner.state,
            'message': 'Owner registered successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': 'Validation error', 'message': str(e)}), 400
    except Exception as e:
        logger.exception("Failed to create owner")
        return jsonify({'error': 'Failed to create owner', 'message': str(e)}), 500


@owner_bp.route('/<owner_id>', methods=['PUT'])
async def update_owner(owner_id: str):
    """Update an existing owner."""
    try:
        data = await request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        entity_service = _get_entity_service()
        
        try:
            owner = await entity_service.find_by_business_id("Owner", owner_id)
        except:
            owner = await entity_service.get_by_id(owner_id)
        
        if not owner:
            return jsonify({'error': 'Owner not found'}), 404
        
        for key, value in data.items():
            if hasattr(owner, key) and key not in ['owner_id', 'technical_id', 'entity_id']:
                setattr(owner, key, value)
        
        transition = data.get('transition')
        
        if transition:
            updated_owner = await entity_service.update(owner, transition=transition)
        else:
            updated_owner = await entity_service.update(owner)
        
        return jsonify({
            'technical_id': updated_owner.technical_id,
            'owner_id': updated_owner.owner_id,
            'state': updated_owner.state,
            'message': 'Owner updated successfully'
        })
        
    except ValueError as e:
        return jsonify({'error': 'Validation error', 'message': str(e)}), 400
    except Exception as e:
        logger.exception(f"Failed to update owner {owner_id}")
        return jsonify({'error': 'Failed to update owner', 'message': str(e)}), 500


@owner_bp.route('/<owner_id>', methods=['DELETE'])
async def delete_owner(owner_id: str):
    """Delete an owner."""
    try:
        entity_service = _get_entity_service()
        
        try:
            owner = await entity_service.find_by_business_id("Owner", owner_id)
        except:
            owner = await entity_service.get_by_id(owner_id)
        
        if not owner:
            return jsonify({'error': 'Owner not found'}), 404
        
        await entity_service.delete(owner.technical_id or owner.entity_id)
        
        return jsonify({'message': 'Owner deleted successfully'})
        
    except Exception as e:
        logger.exception(f"Failed to delete owner {owner_id}")
        return jsonify({'error': 'Failed to delete owner', 'message': str(e)}), 500


def _get_entity_service():
    """Get entity service instance."""
    from service.services import get_entity_service
    return get_entity_service()
