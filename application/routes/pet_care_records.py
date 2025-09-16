"""
PetCareRecord Routes for Purrfect Pets API

RESTful API endpoints for pet care record management operations.
Routes are thin proxies to EntityService with minimal business logic.
"""

import logging

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue

from application.entity.petcarerecord.version_1.petcarerecord import PetCareRecord
from services.services import get_entity_service

# Create blueprint for pet care record routes
pet_care_records_bp = Blueprint(
    "pet_care_records", __name__, url_prefix="/api/pet-care-records"
)
logger = logging.getLogger(__name__)


@pet_care_records_bp.route("", methods=["GET"])
async def get_pet_care_records() -> ResponseReturnValue:
    """Get all pet care records with optional filtering."""
    try:
        entity_service = get_entity_service()

        # Get query parameters
        state = request.args.get("state")
        pet_id = request.args.get("pet_id")
        care_type = request.args.get("care_type")
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))

        # Build filter criteria
        filters = {}
        if state:
            filters["state"] = state
        if pet_id:
            filters["pet_id"] = pet_id
        if care_type:
            filters["care_type"] = care_type

        # Get care records from entity service
        response = await entity_service.find_all(
            entity_class=PetCareRecord.ENTITY_NAME,
            entity_version=str(PetCareRecord.ENTITY_VERSION),
            filters=filters,
            limit=limit,
            offset=offset,
        )

        # Convert to API response format
        care_records = []
        for record_data in response.data:
            care_record = PetCareRecord(**record_data)
            care_records.append(care_record.to_api_response())

        return (
            jsonify(
                {
                    "care_records": care_records,
                    "total": len(care_records),
                    "limit": limit,
                    "offset": offset,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error getting pet care records: {str(e)}")
        return jsonify({"error": "Failed to retrieve pet care records"}), 500


@pet_care_records_bp.route("/<record_id>", methods=["GET"])
async def get_pet_care_record(record_id: str) -> ResponseReturnValue:
    """Get a specific pet care record by ID."""
    try:
        entity_service = get_entity_service()

        response = await entity_service.get_by_id(
            entity_id=record_id,
            entity_class=PetCareRecord.ENTITY_NAME,
            entity_version=str(PetCareRecord.ENTITY_VERSION),
        )

        if not response:
            return jsonify({"error": "Pet care record not found"}), 404

        care_record = PetCareRecord(**response.data.model_dump())
        return jsonify(care_record.to_api_response()), 200

    except Exception as e:
        logger.error(f"Error getting pet care record {record_id}: {str(e)}")
        return jsonify({"error": "Failed to retrieve pet care record"}), 500


@pet_care_records_bp.route("", methods=["POST"])
async def create_pet_care_record() -> ResponseReturnValue:
    """Create a new pet care record."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # Create pet care record entity
        care_record = PetCareRecord(**data)

        # Save through entity service with scheduling transition
        response = await entity_service.save(
            entity=care_record.model_dump(by_alias=True),
            entity_class=PetCareRecord.ENTITY_NAME,
            entity_version=str(PetCareRecord.ENTITY_VERSION),
            )

        # Return created care record
        created_record = PetCareRecord(**response.data.model_dump())
        return jsonify(created_record.to_api_response()), 201

    except ValueError as e:
        logger.warning(f"Validation error creating pet care record: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating pet care record: {str(e)}")
        return jsonify({"error": "Failed to create pet care record"}), 500


@pet_care_records_bp.route("/<record_id>", methods=["PUT"])
async def update_pet_care_record(record_id: str) -> ResponseReturnValue:
    """Update an existing pet care record."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # Get transition if provided
        transition = data.pop("transition", None)

        # Update care record through entity service
        response = await entity_service.update(
            entity_id=record_id,
            entity=data,
            entity_class=PetCareRecord.ENTITY_NAME,
            entity_version=str(PetCareRecord.ENTITY_VERSION),
            transition=transition,
        )

        if not response:
            return jsonify({"error": "Pet care record not found"}), 404

        # Return updated care record
        updated_record = PetCareRecord(**response.data.model_dump())
        return jsonify(updated_record.to_api_response()), 200

    except ValueError as e:
        logger.warning(
            f"Validation error updating pet care record {record_id}: {str(e)}"
        )
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating pet care record {record_id}: {str(e)}")
        return jsonify({"error": "Failed to update pet care record"}), 500


@pet_care_records_bp.route("/<record_id>", methods=["DELETE"])
async def delete_pet_care_record(record_id: str) -> ResponseReturnValue:
    """Delete a pet care record."""
    try:
        entity_service = get_entity_service()

        success = await entity_service.delete_by_id(
            entity_id=record_id,
            entity_class=PetCareRecord.ENTITY_NAME,
            entity_version=str(PetCareRecord.ENTITY_VERSION),
        )

        if not success:
            return jsonify({"error": "Pet care record not found"}), 404

        return jsonify({"message": "Pet care record deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Error deleting pet care record {record_id}: {str(e)}")
        return jsonify({"error": "Failed to delete pet care record"}), 500


@pet_care_records_bp.route("/<record_id>/complete", methods=["POST"])
async def complete_care(record_id: str) -> ResponseReturnValue:
    """Mark a pet care record as completed."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()

        care_results = data if data else {}

        # Execute completion transition
        response = await entity_service.execute_transition(
            entity_id=record_id,
            transition="transition_to_completed",
            entity_class=PetCareRecord.ENTITY_NAME,
            entity_version=str(PetCareRecord.ENTITY_VERSION),
        )

        if not response:
            return (
                jsonify({"error": "Pet care record not found or cannot be completed"}),
                404,
            )

        # Return updated care record
        updated_record = PetCareRecord(**response.data.model_dump())
        return jsonify(updated_record.to_api_response()), 200

    except Exception as e:
        logger.error(f"Error completing pet care record {record_id}: {str(e)}")
        return jsonify({"error": "Failed to complete care record"}), 500


@pet_care_records_bp.route("/<record_id>/cancel", methods=["POST"])
async def cancel_care(record_id: str) -> ResponseReturnValue:
    """Cancel a pet care record."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()

        cancellation_reason = (
            data.get("cancellation_reason", "Appointment cancelled")
            if data
            else "Appointment cancelled"
        )
        reschedule_needed = data.get("reschedule_needed", False) if data else False

        # Execute cancellation transition
        response = await entity_service.execute_transition(
            entity_id=record_id,
            transition="transition_to_cancelled",
            entity_class=PetCareRecord.ENTITY_NAME,
            entity_version=str(PetCareRecord.ENTITY_VERSION),
                "reschedule_needed": reschedule_needed,
            },
        )

        if not response:
            return (
                jsonify({"error": "Pet care record not found or cannot be cancelled"}),
                404,
            )

        # Return updated care record
        updated_record = PetCareRecord(**response.data.model_dump())
        return jsonify(updated_record.to_api_response()), 200

    except Exception as e:
        logger.error(f"Error cancelling pet care record {record_id}: {str(e)}")
        return jsonify({"error": "Failed to cancel care record"}), 500
