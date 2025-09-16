"""
Appointment Routes for Purrfect Pets API.
"""

import logging

from quart import Blueprint, jsonify, request

from application.entity.appointment.version_1.appointment import Appointment

logger = logging.getLogger(__name__)

appointment_bp = Blueprint("appointments", __name__, url_prefix="/appointments")


@appointment_bp.route("", methods=["GET"])
async def get_appointments():
    """Get all appointments with optional filtering."""
    try:
        pet_id = request.args.get("pet_id")
        owner_id = request.args.get("owner_id")
        vet_id = request.args.get("vet_id")
        appointment_type = request.args.get("appointment_type")
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))

        search_conditions = {}
        if pet_id:
            search_conditions["pet_id"] = pet_id
        if owner_id:
            search_conditions["owner_id"] = owner_id
        if vet_id:
            search_conditions["vet_id"] = vet_id
        if appointment_type:
            search_conditions["appointment_type"] = appointment_type

        entity_service = _get_entity_service()

        if search_conditions:
            appointments = await entity_service.search("Appointment", search_conditions)
        else:
            appointments = await entity_service.find_all("Appointment")

        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_appointments = appointments[start_idx:end_idx] if appointments else []

        appointment_data = []
        for appointment in paginated_appointments:
            appointment_dict = (
                appointment.dict() if hasattr(appointment, "dict") else appointment
            )
            appointment_response = {
                "technical_id": appointment_dict.get("technical_id"),
                "appointment_id": appointment_dict.get("appointment_id"),
                "pet_id": appointment_dict.get("pet_id"),
                "owner_id": appointment_dict.get("owner_id"),
                "vet_id": appointment_dict.get("vet_id"),
                "appointment_date": appointment_dict.get("appointment_date"),
                "appointment_type": appointment_dict.get("appointment_type"),
                "duration_minutes": appointment_dict.get("duration_minutes"),
                "state": appointment_dict.get("state"),
            }
            appointment_data.append(appointment_response)

        return jsonify(
            {
                "appointments": appointment_data,
                "total": len(appointments) if appointments else 0,
                "page": page,
                "limit": limit,
            }
        )

    except Exception as e:
        logger.exception("Failed to get appointments")
        return (
            jsonify({"error": "Failed to retrieve appointments", "message": str(e)}),
            500,
        )


@appointment_bp.route("/<appointment_id>", methods=["GET"])
async def get_appointment(appointment_id: str):
    """Get a specific appointment by ID."""
    try:
        entity_service = _get_entity_service()

        try:
            appointment = await entity_service.find_by_business_id(
                "Appointment", appointment_id
            )
        except:
            appointment = await entity_service.get_by_id(appointment_id)

        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404

        appointment_dict = (
            appointment.dict() if hasattr(appointment, "dict") else appointment
        )
        return jsonify(appointment_dict)

    except Exception as e:
        logger.exception(f"Failed to get appointment {appointment_id}")
        return (
            jsonify({"error": "Failed to retrieve appointment", "message": str(e)}),
            500,
        )


@appointment_bp.route("", methods=["POST"])
async def create_appointment():
    """Create a new appointment."""
    try:
        data = await request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        required_fields = [
            "pet_id",
            "owner_id",
            "vet_id",
            "appointment_date",
            "duration_minutes",
            "appointment_type",
        ]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400

        appointment = Appointment(**data)
        entity_service = _get_entity_service()
        saved_appointment = await entity_service.save(appointment)

        return (
            jsonify(
                {
                    "technical_id": saved_appointment.technical_id,
                    "appointment_id": saved_appointment.appointment_id,
                    "pet_id": saved_appointment.pet_id,
                    "vet_id": saved_appointment.vet_id,
                    "appointment_date": saved_appointment.appointment_date,
                    "state": saved_appointment.state,
                    "message": "Appointment scheduled successfully",
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"error": "Validation error", "message": str(e)}), 400
    except Exception as e:
        logger.exception("Failed to create appointment")
        return (
            jsonify({"error": "Failed to create appointment", "message": str(e)}),
            500,
        )


@appointment_bp.route("/<appointment_id>", methods=["PUT"])
async def update_appointment(appointment_id: str):
    """Update an existing appointment."""
    try:
        data = await request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        entity_service = _get_entity_service()

        try:
            appointment = await entity_service.find_by_business_id(
                "Appointment", appointment_id
            )
        except:
            appointment = await entity_service.get_by_id(appointment_id)

        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404

        for key, value in data.items():
            if hasattr(appointment, key) and key not in [
                "appointment_id",
                "technical_id",
                "entity_id",
            ]:
                setattr(appointment, key, value)

        transition = data.get("transition")

        if transition:
            updated_appointment = await entity_service.update(
                appointment, transition=transition
            )
        else:
            updated_appointment = await entity_service.update(appointment)

        return jsonify(
            {
                "technical_id": updated_appointment.technical_id,
                "appointment_id": updated_appointment.appointment_id,
                "state": updated_appointment.state,
                "message": "Appointment updated successfully",
            }
        )

    except ValueError as e:
        return jsonify({"error": "Validation error", "message": str(e)}), 400
    except Exception as e:
        logger.exception(f"Failed to update appointment {appointment_id}")
        return (
            jsonify({"error": "Failed to update appointment", "message": str(e)}),
            500,
        )


@appointment_bp.route("/<appointment_id>", methods=["DELETE"])
async def delete_appointment(appointment_id: str):
    """Delete an appointment."""
    try:
        entity_service = _get_entity_service()

        try:
            appointment = await entity_service.find_by_business_id(
                "Appointment", appointment_id
            )
        except:
            appointment = await entity_service.get_by_id(appointment_id)

        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404

        await entity_service.delete(appointment.technical_id or appointment.entity_id)

        return jsonify({"message": "Appointment deleted successfully"})

    except Exception as e:
        logger.exception(f"Failed to delete appointment {appointment_id}")
        return (
            jsonify({"error": "Failed to delete appointment", "message": str(e)}),
            500,
        )


def _get_entity_service():
    """Get entity service instance."""
    from service.services import get_entity_service

    return get_entity_service()
