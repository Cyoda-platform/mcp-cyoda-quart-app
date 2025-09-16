"""
Staff Routes for Purrfect Pets API

RESTful API endpoints for staff management operations.
Routes are thin proxies to EntityService with minimal business logic.
"""

import logging

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue

from application.entity.staff.version_1.staff import Staff
from services.services import get_entity_service

# Create blueprint for staff routes
staff_bp = Blueprint("staff", __name__, url_prefix="/api/staff")
logger = logging.getLogger(__name__)


@staff_bp.route("", methods=["GET"])
async def get_staff() -> ResponseReturnValue:
    """Get all staff members with optional filtering."""
    try:
        entity_service = get_entity_service()

        # Get query parameters
        state = request.args.get("state")
        department = request.args.get("department")
        role = request.args.get("role")
        is_active = request.args.get("is_active")
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))

        # Build filter criteria
        filters = {}
        if state:
            filters["state"] = state
        if department:
            filters["department"] = department
        if role:
            filters["role"] = role
        if is_active is not None:
            is_active_bool = is_active.lower() == "true"

        # Get staff from entity service
        response = await entity_service.get_all(
            entity_class=Staff.ENTITY_NAME,
            entity_version=str(Staff.ENTITY_VERSION),
            filters=filters,
            limit=limit,
            offset=offset,
        )

        # Convert to API response format
        staff_members = []
        for staff_data in response.data:
            staff_member = Staff(**staff_data)
            staff_members.append(staff_member.to_api_response())

        return (
            jsonify(
                {
                    "staff": staff_members,
                    "total": len(staff_members),
                    "limit": limit,
                    "offset": offset,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error getting staff: {str(e)}")
        return jsonify({"error": "Failed to retrieve staff"}), 500


@staff_bp.route("/<staff_id>", methods=["GET"])
async def get_staff_member(staff_id: str) -> ResponseReturnValue:
    """Get a specific staff member by ID."""
    try:
        entity_service = get_entity_service()

        response = await entity_service.get_by_id(
            entity_id=staff_id,
            entity_class=Staff.ENTITY_NAME,
            entity_version=str(Staff.ENTITY_VERSION),
        )

        if not response:
            return jsonify({"error": "Staff member not found"}), 404

        staff_member = Staff(**response.data)
        return jsonify(staff_member.to_api_response()), 200

    except Exception as e:
        logger.error(f"Error getting staff member {staff_id}: {str(e)}")
        return jsonify({"error": "Failed to retrieve staff member"}), 500


@staff_bp.route("", methods=["POST"])
async def create_staff_member() -> ResponseReturnValue:
    """Create a new staff member."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # Create staff entity
        staff_member = Staff(**data)

        # Save through entity service with onboarding transition
        response = await entity_service.save(
            entity=staff_member.model_dump(by_alias=True),
            entity_class=Staff.ENTITY_NAME,
            entity_version=str(Staff.ENTITY_VERSION),
            transition="transition_to_active",
        )

        # Return created staff member
        created_staff = Staff(**response.data)
        return jsonify(created_staff.to_api_response()), 201

    except ValueError as e:
        logger.warning(f"Validation error creating staff member: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating staff member: {str(e)}")
        return jsonify({"error": "Failed to create staff member"}), 500


@staff_bp.route("/<staff_id>", methods=["PUT"])
async def update_staff_member(staff_id: str) -> ResponseReturnValue:
    """Update an existing staff member."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # Get transition if provided
        transition = data.pop("transition", None)

        # Update staff member through entity service
        response = await entity_service.update(
            entity_id=staff_id,
            entity_data=data,
            entity_class=Staff.ENTITY_NAME,
            entity_version=str(Staff.ENTITY_VERSION),
            transition=transition,
        )

        if not response:
            return jsonify({"error": "Staff member not found"}), 404

        # Return updated staff member
        updated_staff = Staff(**response.data)
        return jsonify(updated_staff.to_api_response()), 200

    except ValueError as e:
        logger.warning(f"Validation error updating staff member {staff_id}: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating staff member {staff_id}: {str(e)}")
        return jsonify({"error": "Failed to update staff member"}), 500


@staff_bp.route("/<staff_id>", methods=["DELETE"])
async def delete_staff_member(staff_id: str) -> ResponseReturnValue:
    """Delete a staff member."""
    try:
        entity_service = get_entity_service()

        success = await entity_service.delete(
            entity_id=staff_id,
            entity_class=Staff.ENTITY_NAME,
            entity_version=str(Staff.ENTITY_VERSION),
        )

        if not success:
            return jsonify({"error": "Staff member not found"}), 404

        return jsonify({"message": "Staff member deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Error deleting staff member {staff_id}: {str(e)}")
        return jsonify({"error": "Failed to delete staff member"}), 500


@staff_bp.route("/<staff_id>/leave", methods=["POST"])
async def staff_leave(staff_id: str) -> ResponseReturnValue:
    """Put a staff member on leave."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()

        leave_details = data if data else {}

        # Execute leave transition
        response = await entity_service.execute_transition(
            entity_id=staff_id,
            transition="transition_to_on_leave",
            entity_class=Staff.ENTITY_NAME,
            entity_version=str(Staff.ENTITY_VERSION),
            processor_kwargs={"leave_details": leave_details},
        )

        if not response:
            return (
                jsonify({"error": "Staff member not found or cannot be put on leave"}),
                404,
            )

        # Return updated staff member
        updated_staff = Staff(**response.data)
        return jsonify(updated_staff.to_api_response()), 200

    except Exception as e:
        logger.error(f"Error putting staff member {staff_id} on leave: {str(e)}")
        return jsonify({"error": "Failed to put staff member on leave"}), 500


@staff_bp.route("/<staff_id>/return", methods=["POST"])
async def staff_return(staff_id: str) -> ResponseReturnValue:
    """Return a staff member from leave."""
    try:
        entity_service = get_entity_service()

        # Execute return transition
        response = await entity_service.execute_transition(
            entity_id=staff_id,
            transition="transition_to_active",
            entity_class=Staff.ENTITY_NAME,
            entity_version=str(Staff.ENTITY_VERSION),
        )

        if not response:
            return (
                jsonify(
                    {"error": "Staff member not found or cannot return from leave"}
                ),
                404,
            )

        # Return updated staff member
        updated_staff = Staff(**response.data)
        return jsonify(updated_staff.to_api_response()), 200

    except Exception as e:
        logger.error(f"Error returning staff member {staff_id} from leave: {str(e)}")
        return jsonify({"error": "Failed to return staff member from leave"}), 500
