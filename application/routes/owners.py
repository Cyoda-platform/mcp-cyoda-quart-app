"""Owner routes for Purrfect Pets API."""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from quart import Blueprint, jsonify, request, abort
from quart_schema import validate_request, validate_querystring
from pydantic import BaseModel, Field

from service.services import get_entity_service, get_auth_service
from application.entity.owner.version_1.owner import Owner

logger = logging.getLogger(__name__)

owners_bp = Blueprint('owners', __name__, url_prefix='/api/owners')

ENTITY_VERSION = "1"


class OwnerQuery(BaseModel):
    """Query parameters for owner filtering."""
    page: Optional[int] = Field(0, ge=0, description="Page number")
    size: Optional[int] = Field(10, ge=1, le=100, description="Page size")
    status: Optional[str] = Field(None, description="Filter by owner status")


class OwnerRequest(BaseModel):
    """Request model for creating owners."""
    firstName: str = Field(..., description="Owner's first name")
    lastName: str = Field(..., description="Owner's last name")
    email: str = Field(..., description="Owner's email address")
    phone: str = Field(..., description="Owner's phone number")
    address: str = Field(..., description="Owner's address")
    city: str = Field(..., description="Owner's city")
    zipCode: str = Field(..., description="Owner's zip code")
    country: str = Field(..., description="Owner's country")
    dateOfBirth: str = Field(..., description="Owner's date of birth (YYYY-MM-DD)")


class OwnerUpdateRequest(BaseModel):
    """Request model for updating owners."""
    transitionName: Optional[str] = Field(None, description="Workflow transition name")
    firstName: Optional[str] = Field(None, description="Owner's first name")
    lastName: Optional[str] = Field(None, description="Owner's last name")
    email: Optional[str] = Field(None, description="Owner's email address")
    phone: Optional[str] = Field(None, description="Owner's phone number")
    address: Optional[str] = Field(None, description="Owner's address")
    city: Optional[str] = Field(None, description="Owner's city")
    zipCode: Optional[str] = Field(None, description="Owner's zip code")
    country: Optional[str] = Field(None, description="Owner's country")
    dateOfBirth: Optional[str] = Field(None, description="Owner's date of birth")


def get_services():
    """Get entity service and auth service."""
    return get_entity_service(), get_auth_service()


@owners_bp.route("", methods=["GET"])
@validate_querystring(OwnerQuery)
async def get_owners():
    """Get all owners with pagination."""
    entity_service, cyoda_auth_service = get_services()
    args = OwnerQuery(**request.args)
    
    try:
        # Get all owners from entity service
        owners_response = await entity_service.find_all("Owner", ENTITY_VERSION)
        owners = owners_response if owners_response else []
        
        # Apply status filter
        filtered_owners = []
        for owner_data in owners:
            owner = Owner(**owner_data) if isinstance(owner_data, dict) else owner_data
            
            # Apply status filter (map to state)
            if args.status:
                status_map = {
                    "ACTIVE": "active",
                    "INACTIVE": "inactive",
                    "SUSPENDED": "suspended",
                    "PENDING_VERIFICATION": "pending_verification"
                }
                expected_state = status_map.get(args.status.upper())
                if expected_state and owner.state != expected_state:
                    continue
                    
            filtered_owners.append(owner)
        
        # Apply pagination
        total_elements = len(filtered_owners)
        start_idx = args.page * args.size
        end_idx = start_idx + args.size
        paginated_owners = filtered_owners[start_idx:end_idx]
        
        # Convert to response format
        content = []
        for owner in paginated_owners:
            content.append({
                "id": owner.id,
                "firstName": owner.firstName,
                "lastName": owner.lastName,
                "email": owner.email,
                "state": owner.state.upper() if owner.state else "UNKNOWN"
            })
        
        response = {
            "content": content,
            "totalElements": total_elements
        }
        
        logger.info(f"Retrieved {len(content)} owners (page {args.page})")
        return jsonify(response)
        
    except Exception as e:
        logger.exception(f"Failed to get owners: {e}")
        return jsonify({"error": f"Failed to get owners: {str(e)}"}), 500


@owners_bp.route("/<int:owner_id>", methods=["GET"])
async def get_owner(owner_id: int):
    """Get owner by ID."""
    entity_service, cyoda_auth_service = get_services()
    
    try:
        # Find owner by business ID
        owner_response = await entity_service.find_by_business_id(
            "Owner", str(owner_id), "id", ENTITY_VERSION
        )
        
        if not owner_response:
            return jsonify({"error": "Owner not found"}), 404
        
        owner_data = owner_response.entity
        owner = Owner(**owner_data) if isinstance(owner_data, dict) else owner_data
        
        response = {
            "id": owner.id,
            "firstName": owner.firstName,
            "lastName": owner.lastName,
            "email": owner.email,
            "phone": owner.phone,
            "address": owner.address,
            "city": owner.city,
            "zipCode": owner.zipCode,
            "country": owner.country,
            "state": owner.state.upper() if owner.state else "UNKNOWN",
            "createdAt": owner.createdAt
        }
        
        logger.info(f"Retrieved owner {owner_id}")
        return jsonify(response)

    except Exception as e:
        logger.exception(f"Failed to get owner {owner_id}: {e}")
        return jsonify({"error": f"Failed to get owner: {str(e)}"}), 500


@owners_bp.route("", methods=["POST"])
@validate_request(OwnerRequest)
async def create_owner(data: OwnerRequest):
    """Create new owner."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Generate unique ID
        owner_id = len(await entity_service.find_all("Owner", ENTITY_VERSION) or []) + 1

        # Create owner entity
        owner_data = {
            "id": owner_id,
            "firstName": data.firstName,
            "lastName": data.lastName,
            "email": data.email,
            "phone": data.phone,
            "address": data.address,
            "city": data.city,
            "zipCode": data.zipCode,
            "country": data.country,
            "dateOfBirth": data.dateOfBirth,
            "state": "initial_state"
        }

        # Save owner
        owner_response = await entity_service.save(owner_data, "Owner", ENTITY_VERSION)

        response = {
            "id": owner_id,
            "firstName": data.firstName,
            "lastName": data.lastName,
            "email": data.email,
            "state": "PENDING_VERIFICATION",
            "createdAt": datetime.now(timezone.utc).isoformat()
        }

        logger.info(f"Created owner {owner_id}")
        return jsonify(response), 201

    except Exception as e:
        logger.exception(f"Failed to create owner: {e}")
        return jsonify({"error": f"Failed to create owner: {str(e)}"}), 500


@owners_bp.route("/<int:owner_id>", methods=["PUT"])
@validate_request(OwnerUpdateRequest)
async def update_owner(owner_id: int, data: OwnerUpdateRequest):
    """Update owner."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Find existing owner
        owner_response = await entity_service.find_by_business_id(
            "Owner", str(owner_id), "id", ENTITY_VERSION
        )

        if not owner_response:
            return jsonify({"error": "Owner not found"}), 404

        # Update fields if provided
        update_data = {}
        if data.firstName is not None:
            update_data["firstName"] = data.firstName
        if data.lastName is not None:
            update_data["lastName"] = data.lastName
        if data.email is not None:
            update_data["email"] = data.email
        if data.phone is not None:
            update_data["phone"] = data.phone
        if data.address is not None:
            update_data["address"] = data.address
        if data.city is not None:
            update_data["city"] = data.city
        if data.zipCode is not None:
            update_data["zipCode"] = data.zipCode
        if data.country is not None:
            update_data["country"] = data.country
        if data.dateOfBirth is not None:
            update_data["dateOfBirth"] = data.dateOfBirth

        # Add timestamp
        update_data["updatedAt"] = datetime.now(timezone.utc).isoformat()

        # Update with transition if provided
        transition = data.transitionName
        if transition:
            # Map transition names to workflow transitions
            transition_map = {
                "VERIFY": "transition_to_active",
                "DEACTIVATE": "transition_to_inactive",
                "ACTIVATE": "transition_to_active",
                "SUSPEND": "transition_to_suspended",
                "REINSTATE": "transition_to_active"
            }
            workflow_transition = transition_map.get(transition)
        else:
            workflow_transition = None

        # Update owner
        updated_response = await entity_service.update(
            owner_response.metadata.id,
            update_data,
            "Owner",
            workflow_transition,
            ENTITY_VERSION
        )

        # Get updated state
        updated_owner_data = updated_response.entity
        updated_owner = Owner(**updated_owner_data) if isinstance(updated_owner_data, dict) else updated_owner_data

        response = {
            "id": owner_id,
            "firstName": updated_owner.firstName,
            "lastName": updated_owner.lastName,
            "state": updated_owner.state.upper() if updated_owner.state else "UNKNOWN",
            "updatedAt": updated_owner.updatedAt
        }

        logger.info(f"Updated owner {owner_id}")
        return jsonify(response)

    except Exception as e:
        logger.exception(f"Failed to update owner {owner_id}: {e}")
        return jsonify({"error": f"Failed to update owner: {str(e)}"}), 500


@owners_bp.route("/<int:owner_id>", methods=["DELETE"])
async def delete_owner(owner_id: int):
    """Delete owner (deactivate)."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Find existing owner
        owner_response = await entity_service.find_by_business_id(
            "Owner", str(owner_id), "id", ENTITY_VERSION
        )

        if not owner_response:
            return jsonify({"error": "Owner not found"}), 404

        # Deactivate by updating state
        delete_data = {
            "updatedAt": datetime.now(timezone.utc).isoformat()
        }

        await entity_service.update(
            owner_response.metadata.id,
            delete_data,
            "Owner",
            "transition_to_inactive",  # Deactivate transition
            ENTITY_VERSION
        )

        response = {"message": "Owner deleted successfully"}

        logger.info(f"Deleted owner {owner_id}")
        return jsonify(response)

    except Exception as e:
        logger.exception(f"Failed to delete owner {owner_id}: {e}")
        return jsonify({"error": f"Failed to delete owner: {str(e)}"}), 500
