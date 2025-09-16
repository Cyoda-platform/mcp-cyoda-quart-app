"""
Medical Record Routes for Purrfect Pets API.
"""
import logging
from quart import Blueprint, request, jsonify

from application.entity.medicalrecord.version_1.medicalrecord import MedicalRecord

logger = logging.getLogger(__name__)

medical_record_bp = Blueprint('medical_records', __name__, url_prefix='/medical-records')


@medical_record_bp.route('', methods=['GET'])
async def get_medical_records():
    """Get all medical records with optional filtering."""
    try:
        pet_id = request.args.get('pet_id')
        vet_id = request.args.get('vet_id')
        appointment_id = request.args.get('appointment_id')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        search_conditions = {}
        if pet_id:
            search_conditions['pet_id'] = pet_id
        if vet_id:
            search_conditions['vet_id'] = vet_id
        if appointment_id:
            search_conditions['appointment_id'] = appointment_id
        
        entity_service = _get_entity_service()
        
        if search_conditions:
            records = await entity_service.search("MedicalRecord", search_conditions)
        else:
            records = await entity_service.find_all("MedicalRecord")
        
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_records = records[start_idx:end_idx] if records else []
        
        record_data = []
        for record in paginated_records:
            record_dict = record.dict() if hasattr(record, 'dict') else record
            record_response = {
                'technical_id': record_dict.get('technical_id'),
                'record_id': record_dict.get('record_id'),
                'pet_id': record_dict.get('pet_id'),
                'vet_id': record_dict.get('vet_id'),
                'appointment_id': record_dict.get('appointment_id'),
                'visit_date': record_dict.get('visit_date'),
                'diagnosis': record_dict.get('diagnosis'),
                'treatment': record_dict.get('treatment'),
                'follow_up_required': record_dict.get('follow_up_required'),
                'state': record_dict.get('state')
            }
            record_data.append(record_response)
        
        return jsonify({
            'medical_records': record_data,
            'total': len(records) if records else 0,
            'page': page,
            'limit': limit
        })
        
    except Exception as e:
        logger.exception("Failed to get medical records")
        return jsonify({'error': 'Failed to retrieve medical records', 'message': str(e)}), 500


@medical_record_bp.route('/<record_id>', methods=['GET'])
async def get_medical_record(record_id: str):
    """Get a specific medical record by ID."""
    try:
        entity_service = _get_entity_service()
        
        try:
            record = await entity_service.find_by_business_id("MedicalRecord", record_id)
        except:
            record = await entity_service.get_by_id(record_id)
        
        if not record:
            return jsonify({'error': 'Medical record not found'}), 404
        
        record_dict = record.dict() if hasattr(record, 'dict') else record
        return jsonify(record_dict)
        
    except Exception as e:
        logger.exception(f"Failed to get medical record {record_id}")
        return jsonify({'error': 'Failed to retrieve medical record', 'message': str(e)}), 500


@medical_record_bp.route('', methods=['POST'])
async def create_medical_record():
    """Create a new medical record."""
    try:
        data = await request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        required_fields = ['pet_id', 'vet_id', 'visit_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        record = MedicalRecord(**data)
        entity_service = _get_entity_service()
        saved_record = await entity_service.save(record)
        
        return jsonify({
            'technical_id': saved_record.technical_id,
            'record_id': saved_record.record_id,
            'pet_id': saved_record.pet_id,
            'vet_id': saved_record.vet_id,
            'visit_date': saved_record.visit_date,
            'state': saved_record.state,
            'message': 'Medical record created successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': 'Validation error', 'message': str(e)}), 400
    except Exception as e:
        logger.exception("Failed to create medical record")
        return jsonify({'error': 'Failed to create medical record', 'message': str(e)}), 500


@medical_record_bp.route('/<record_id>', methods=['PUT'])
async def update_medical_record(record_id: str):
    """Update an existing medical record."""
    try:
        data = await request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        entity_service = _get_entity_service()
        
        try:
            record = await entity_service.find_by_business_id("MedicalRecord", record_id)
        except:
            record = await entity_service.get_by_id(record_id)
        
        if not record:
            return jsonify({'error': 'Medical record not found'}), 404
        
        for key, value in data.items():
            if hasattr(record, key) and key not in ['record_id', 'technical_id', 'entity_id']:
                setattr(record, key, value)
        
        transition = data.get('transition')
        
        if transition:
            updated_record = await entity_service.update(record, transition=transition)
        else:
            updated_record = await entity_service.update(record)
        
        return jsonify({
            'technical_id': updated_record.technical_id,
            'record_id': updated_record.record_id,
            'state': updated_record.state,
            'message': 'Medical record updated successfully'
        })
        
    except ValueError as e:
        return jsonify({'error': 'Validation error', 'message': str(e)}), 400
    except Exception as e:
        logger.exception(f"Failed to update medical record {record_id}")
        return jsonify({'error': 'Failed to update medical record', 'message': str(e)}), 500


@medical_record_bp.route('/<record_id>', methods=['DELETE'])
async def delete_medical_record(record_id: str):
    """Delete a medical record."""
    try:
        entity_service = _get_entity_service()
        
        try:
            record = await entity_service.find_by_business_id("MedicalRecord", record_id)
        except:
            record = await entity_service.get_by_id(record_id)
        
        if not record:
            return jsonify({'error': 'Medical record not found'}), 404
        
        await entity_service.delete(record.technical_id or record.entity_id)
        
        return jsonify({'message': 'Medical record deleted successfully'})
        
    except Exception as e:
        logger.exception(f"Failed to delete medical record {record_id}")
        return jsonify({'error': 'Failed to delete medical record', 'message': str(e)}), 500


def _get_entity_service():
    """Get entity service instance."""
    from service.services import get_entity_service
    return get_entity_service()
