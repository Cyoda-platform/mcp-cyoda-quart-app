"""
AdoptionApplication Routes for Purrfect Pets API

RESTful API endpoints for adoption application management operations.
Routes are thin proxies to EntityService with minimal business logic.
"""

import logging

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue

from application.entity.adoptionapplication.version_1.adoptionapplication import (
    AdoptionApplication,
)
from services.services import get_entity_service

# Create blueprint for adoption application routes
adoption_applications_bp = Blueprint(
    "adoption_applications", __name__, url_prefix="/api/adoption-applications"
)
logger = logging.getLogger(__name__)


@adoption_applications_bp.route("", methods=["GET"])
async def get_adoption_applications() -> ResponseReturnValue:
    """Get all adoption applications with optional filtering."""
    try:
        entity_service = get_entity_service()

        # Get query parameters
        state = request.args.get("state")
        customer_id = request.args.get("customer_id")
        pet_id = request.args.get("pet_id")
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))

        # Build filter criteria
        filters = {}
        if state:
            filters["state"] = state
        if customer_id:
            filters["customer_id"] = customer_id
        if pet_id:
            filters["pet_id"] = pet_id

        # Get applications from entity service
        response = await entity_service.get_all(
            entity_class=AdoptionApplication.ENTITY_NAME,
            entity_version=str(AdoptionApplication.ENTITY_VERSION),
            filters=filters,
            limit=limit,
            offset=offset,
        )

        # Convert to API response format
        applications = []
        for app_data in response.data:
            application = AdoptionApplication(**app_data)
            applications.append(application.to_api_response())

        return (
            jsonify(
                {
                    "applications": applications,
                    "total": len(applications),
                    "limit": limit,
                    "offset": offset,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error getting adoption applications: {str(e)}")
        return jsonify({"error": "Failed to retrieve adoption applications"}), 500


@adoption_applications_bp.route("/<application_id>", methods=["GET"])
async def get_adoption_application(application_id: str) -> ResponseReturnValue:
    """Get a specific adoption application by ID."""
    try:
        entity_service = get_entity_service()

        response = await entity_service.get_by_id(
            entity_id=application_id,
            entity_class=AdoptionApplication.ENTITY_NAME,
            entity_version=str(AdoptionApplication.ENTITY_VERSION),
        )

        if not response:
            return jsonify({"error": "Adoption application not found"}), 404

        application = AdoptionApplication(**response.data)
        return jsonify(application.to_api_response()), 200

    except Exception as e:
        logger.error(f"Error getting adoption application {application_id}: {str(e)}")
        return jsonify({"error": "Failed to retrieve adoption application"}), 500


@adoption_applications_bp.route("", methods=["POST"])
async def create_adoption_application() -> ResponseReturnValue:
    """Create a new adoption application."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # Create adoption application entity
        application = AdoptionApplication(**data)

        # Save through entity service with submission transition
        response = await entity_service.save(
            entity=application.model_dump(by_alias=True),
            entity_class=AdoptionApplication.ENTITY_NAME,
            entity_version=str(AdoptionApplication.ENTITY_VERSION),
            transition="transition_to_submitted",
        )

        # Return created application
        created_application = AdoptionApplication(**response.data)
        return jsonify(created_application.to_api_response()), 201

    except ValueError as e:
        logger.warning(f"Validation error creating adoption application: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating adoption application: {str(e)}")
        return jsonify({"error": "Failed to create adoption application"}), 500


@adoption_applications_bp.route("/<application_id>", methods=["PUT"])
async def update_adoption_application(application_id: str) -> ResponseReturnValue:
    """Update an existing adoption application."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # Get transition if provided
        transition = data.pop("transition", None)

        # Update application through entity service
        response = await entity_service.update(
            entity_id=application_id,
            entity_data=data,
            entity_class=AdoptionApplication.ENTITY_NAME,
            entity_version=str(AdoptionApplication.ENTITY_VERSION),
            transition=transition,
        )

        if not response:
            return jsonify({"error": "Adoption application not found"}), 404

        # Return updated application
        updated_application = AdoptionApplication(**response.data)
        return jsonify(updated_application.to_api_response()), 200

    except ValueError as e:
        logger.warning(
            f"Validation error updating adoption application {application_id}: {str(e)}"
        )
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating adoption application {application_id}: {str(e)}")
        return jsonify({"error": "Failed to update adoption application"}), 500


@adoption_applications_bp.route("/<application_id>", methods=["DELETE"])
async def delete_adoption_application(application_id: str) -> ResponseReturnValue:
    """Delete an adoption application."""
    try:
        entity_service = get_entity_service()

        success = await entity_service.delete(
            entity_id=application_id,
            entity_class=AdoptionApplication.ENTITY_NAME,
            entity_version=str(AdoptionApplication.ENTITY_VERSION),
        )

        if not success:
            return jsonify({"error": "Adoption application not found"}), 404

        return jsonify({"message": "Adoption application deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Error deleting adoption application {application_id}: {str(e)}")
        return jsonify({"error": "Failed to delete adoption application"}), 500


@adoption_applications_bp.route("/<application_id>/start-review", methods=["POST"])
async def start_review(application_id: str) -> ResponseReturnValue:
    """Start review of an adoption application."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()

        reviewer_id = data.get("reviewer_id") if data else None

        # Execute start review transition
        response = await entity_service.execute_transition(
            entity_id=application_id,
            transition="transition_to_under_review",
            entity_class=AdoptionApplication.ENTITY_NAME,
            entity_version=str(AdoptionApplication.ENTITY_VERSION),
            processor_kwargs={"reviewer_id": reviewer_id},
        )

        if not response:
            return (
                jsonify(
                    {"error": "Adoption application not found or cannot start review"}
                ),
                404,
            )

        # Return updated application
        updated_application = AdoptionApplication(**response.data)
        return jsonify(updated_application.to_api_response()), 200

    except Exception as e:
        logger.error(
            f"Error starting review for adoption application {application_id}: {str(e)}"
        )
        return jsonify({"error": "Failed to start review"}), 500


@adoption_applications_bp.route("/<application_id>/approve", methods=["POST"])
async def approve_application(application_id: str) -> ResponseReturnValue:
    """Approve an adoption application."""
    try:
        entity_service = get_entity_service()

        # Execute approval transition
        response = await entity_service.execute_transition(
            entity_id=application_id,
            transition="transition_to_approved",
            entity_class=AdoptionApplication.ENTITY_NAME,
            entity_version=str(AdoptionApplication.ENTITY_VERSION),
        )

        if not response:
            return (
                jsonify(
                    {"error": "Adoption application not found or cannot be approved"}
                ),
                404,
            )

        # Return updated application
        updated_application = AdoptionApplication(**response.data)
        return jsonify(updated_application.to_api_response()), 200

    except Exception as e:
        logger.error(f"Error approving adoption application {application_id}: {str(e)}")
        return jsonify({"error": "Failed to approve application"}), 500


@adoption_applications_bp.route("/<application_id>/reject", methods=["POST"])
async def reject_application(application_id: str) -> ResponseReturnValue:
    """Reject an adoption application."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()

        rejection_reason = (
            data.get("rejection_reason", "Application did not meet requirements")
            if data
            else "Application did not meet requirements"
        )

        # Execute rejection transition
        response = await entity_service.execute_transition(
            entity_id=application_id,
            transition="transition_to_rejected",
            entity_class=AdoptionApplication.ENTITY_NAME,
            entity_version=str(AdoptionApplication.ENTITY_VERSION),
            processor_kwargs={"rejection_reason": rejection_reason},
        )

        if not response:
            return (
                jsonify(
                    {"error": "Adoption application not found or cannot be rejected"}
                ),
                404,
            )

        # Return updated application
        updated_application = AdoptionApplication(**response.data)
        return jsonify(updated_application.to_api_response()), 200

    except Exception as e:
        logger.error(f"Error rejecting adoption application {application_id}: {str(e)}")
        return jsonify({"error": "Failed to reject application"}), 500


@adoption_applications_bp.route("/<application_id>/withdraw", methods=["POST"])
async def withdraw_application(application_id: str) -> ResponseReturnValue:
    """Withdraw an adoption application."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()

        withdrawal_reason = (
            data.get("withdrawal_reason", "Customer withdrew application")
            if data
            else "Customer withdrew application"
        )

        # Execute withdrawal transition
        response = await entity_service.execute_transition(
            entity_id=application_id,
            transition="transition_to_withdrawn",
            entity_class=AdoptionApplication.ENTITY_NAME,
            entity_version=str(AdoptionApplication.ENTITY_VERSION),
            processor_kwargs={"withdrawal_reason": withdrawal_reason},
        )

        if not response:
            return (
                jsonify(
                    {"error": "Adoption application not found or cannot be withdrawn"}
                ),
                404,
            )

        # Return updated application
        updated_application = AdoptionApplication(**response.data)
        return jsonify(updated_application.to_api_response()), 200

    except Exception as e:
        logger.error(
            f"Error withdrawing adoption application {application_id}: {str(e)}"
        )
        return jsonify({"error": "Failed to withdraw application"}), 500
