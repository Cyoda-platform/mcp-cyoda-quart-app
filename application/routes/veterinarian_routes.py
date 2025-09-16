"""
Veterinarian Routes for Purrfect Pets API.
"""

import logging

from quart import Blueprint, jsonify, request

from application.entity.veterinarian.version_1.veterinarian import Veterinarian

logger = logging.getLogger(__name__)

veterinarian_bp = Blueprint("veterinarians", __name__, url_prefix="/veterinarians")


@veterinarian_bp.route("", methods=["GET"])
async def get_veterinarians():
    """Get all veterinarians with optional filtering."""
    try:
        specialization = request.args.get("specialization")
        is_available = request.args.get("is_available")
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))

        search_conditions = {}
        if specialization:
            search_conditions["specialization"] = specialization
        if is_available is not None:
            search_conditions["is_available"] = is_available.lower() == "true"

        entity_service = _get_entity_service()

        if search_conditions:
            vets = await entity_service.search("Veterinarian", search_conditions)
        else:
            vets = await entity_service.find_all("Veterinarian")

        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_vets = vets[start_idx:end_idx] if vets else []

        vet_data = []
        for vet in paginated_vets:
            vet_dict = vet.dict() if hasattr(vet, "dict") else vet
            vet_response = {
                "technical_id": vet_dict.get("technical_id"),
                "vet_id": vet_dict.get("vet_id"),
                "first_name": vet_dict.get("first_name"),
                "last_name": vet_dict.get("last_name"),
                "email": vet_dict.get("email"),
                "specialization": vet_dict.get("specialization"),
                "is_available": vet_dict.get("is_available"),
                "state": vet_dict.get("state"),
            }
            vet_data.append(vet_response)

        return jsonify(
            {
                "veterinarians": vet_data,
                "total": len(vets) if vets else 0,
                "page": page,
                "limit": limit,
            }
        )

    except Exception as e:
        logger.exception("Failed to get veterinarians")
        return (
            jsonify({"error": "Failed to retrieve veterinarians", "message": str(e)}),
            500,
        )


@veterinarian_bp.route("/<vet_id>", methods=["GET"])
async def get_veterinarian(vet_id: str):
    """Get a specific veterinarian by ID."""
    try:
        entity_service = _get_entity_service()

        try:
            vet = await entity_service.find_by_business_id("Veterinarian", vet_id)
        except:
            vet = await entity_service.get_by_id(vet_id)

        if not vet:
            return jsonify({"error": "Veterinarian not found"}), 404

        vet_dict = vet.dict() if hasattr(vet, "dict") else vet
        return jsonify(vet_dict)

    except Exception as e:
        logger.exception(f"Failed to get veterinarian {vet_id}")
        return (
            jsonify({"error": "Failed to retrieve veterinarian", "message": str(e)}),
            500,
        )


@veterinarian_bp.route("", methods=["POST"])
async def create_veterinarian():
    """Create a new veterinarian."""
    try:
        data = await request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        required_fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "license_number",
        ]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400

        vet = Veterinarian(**data)
        entity_service = _get_entity_service()
        saved_vet = await entity_service.save(vet)

        return (
            jsonify(
                {
                    "technical_id": saved_vet.technical_id,
                    "vet_id": saved_vet.vet_id,
                    "first_name": saved_vet.first_name,
                    "last_name": saved_vet.last_name,
                    "license_number": saved_vet.license_number,
                    "state": saved_vet.state,
                    "message": "Veterinarian hired successfully",
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"error": "Validation error", "message": str(e)}), 400
    except Exception as e:
        logger.exception("Failed to create veterinarian")
        return (
            jsonify({"error": "Failed to create veterinarian", "message": str(e)}),
            500,
        )


@veterinarian_bp.route("/<vet_id>", methods=["PUT"])
async def update_veterinarian(vet_id: str):
    """Update an existing veterinarian."""
    try:
        data = await request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        entity_service = _get_entity_service()

        try:
            vet = await entity_service.find_by_business_id("Veterinarian", vet_id)
        except:
            vet = await entity_service.get_by_id(vet_id)

        if not vet:
            return jsonify({"error": "Veterinarian not found"}), 404

        for key, value in data.items():
            if hasattr(vet, key) and key not in ["vet_id", "technical_id", "entity_id"]:
                setattr(vet, key, value)

        transition = data.get("transition")

        if transition:
            updated_vet = await entity_service.update(vet, transition=transition)
        else:
            updated_vet = await entity_service.update(vet)

        return jsonify(
            {
                "technical_id": updated_vet.technical_id,
                "vet_id": updated_vet.vet_id,
                "state": updated_vet.state,
                "message": "Veterinarian updated successfully",
            }
        )

    except ValueError as e:
        return jsonify({"error": "Validation error", "message": str(e)}), 400
    except Exception as e:
        logger.exception(f"Failed to update veterinarian {vet_id}")
        return (
            jsonify({"error": "Failed to update veterinarian", "message": str(e)}),
            500,
        )


@veterinarian_bp.route("/<vet_id>", methods=["DELETE"])
async def delete_veterinarian(vet_id: str):
    """Delete a veterinarian."""
    try:
        entity_service = _get_entity_service()

        try:
            vet = await entity_service.find_by_business_id("Veterinarian", vet_id)
        except:
            vet = await entity_service.get_by_id(vet_id)

        if not vet:
            return jsonify({"error": "Veterinarian not found"}), 404

        await entity_service.delete(vet.technical_id or vet.entity_id)

        return jsonify({"message": "Veterinarian deleted successfully"})

    except Exception as e:
        logger.exception(f"Failed to delete veterinarian {vet_id}")
        return (
            jsonify({"error": "Failed to delete veterinarian", "message": str(e)}),
            500,
        )


def _get_entity_service():
    """Get entity service instance."""
    from service.services import get_entity_service

    return get_entity_service()
