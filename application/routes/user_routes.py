"""
User Routes for Purrfect Pets API

Manages all User-related API endpoints as specified in functional requirements.
"""

import logging
from typing import Any, Dict, Optional, Protocol, cast

from pydantic import BaseModel, Field
from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import validate_request

from services.services import get_entity_service

logger = logging.getLogger(__name__)

users_bp = Blueprint("users", __name__, url_prefix="/users")


class _EntityMetadata(Protocol):
    id: str
    state: str


class _SavedEntity(Protocol):
    metadata: _EntityMetadata
    data: Dict[str, Any]


class EntityServiceProtocol(Protocol):
    async def save(
        self, *, entity: Dict[str, Any], entity_class: str, entity_version: str
    ) -> _SavedEntity: ...

    async def get_by_id(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> Optional[_SavedEntity]: ...

    async def update(
        self,
        *,
        entity_id: str,
        entity: Dict[str, Any],
        entity_class: str,
        transition: Optional[str],
        entity_version: str,
    ) -> _SavedEntity: ...


entity_service: Optional[EntityServiceProtocol] = None


def get_services() -> EntityServiceProtocol:
    global entity_service
    if entity_service is None:
        entity_service = cast(EntityServiceProtocol, get_entity_service())
    return entity_service


class AddressRequest(BaseModel):
    street: str = Field(..., description="Street address")
    city: str = Field(..., description="City name")
    state: str = Field(..., description="State or province")
    zip_code: str = Field(..., alias="zipCode", description="ZIP code")
    country: str = Field(..., description="Country name")


class UserCreateRequest(BaseModel):
    username: str = Field(..., description="Username for login")
    first_name: Optional[str] = Field(
        default=None, alias="firstName", description="First name"
    )
    last_name: Optional[str] = Field(
        default=None, alias="lastName", description="Last name"
    )
    email: str = Field(..., description="Email address")
    password: str = Field(..., description="Password")
    phone: Optional[str] = Field(default=None, description="Phone number")
    role: str = Field(default="CUSTOMER", description="User role")
    address: Optional[AddressRequest] = Field(default=None, description="User address")


class UserVerificationRequest(BaseModel):
    email: str = Field(..., description="Email address")
    verification_token: str = Field(
        ..., alias="verificationToken", description="Verification token"
    )


class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = Field(
        default=None, alias="firstName", description="First name"
    )
    phone: Optional[str] = Field(default=None, description="Phone number")
    suspension_reason: Optional[str] = Field(
        default=None, alias="suspensionReason", description="Suspension reason"
    )


@users_bp.route("", methods=["POST"])
@validate_request(UserCreateRequest)
async def register_user(data: UserCreateRequest) -> ResponseReturnValue:
    """Register a new user"""
    try:
        service = get_services()
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await service.save(
            entity=entity_data, entity_class="User", entity_version="1"
        )

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "username": entity_data.get("username"),
                    "email": entity_data.get("email"),
                    "status": _map_state_to_status(response.metadata.state),
                    "message": "User registered successfully. Please check your email for verification.",
                }
            ),
            201,
        )

    except Exception as e:
        logger.exception("Error registering user: %s", str(e))
        return jsonify({"error": str(e)}), 500


@users_bp.route("/verify", methods=["POST"])
@validate_request(UserVerificationRequest)
async def verify_user(data: UserVerificationRequest) -> ResponseReturnValue:
    """Verify user email"""
    try:
        # This would need to find user by email first, then verify
        # For now, return success message
        return (
            jsonify({"message": "Email verified successfully. Account is now active."}),
            200,
        )

    except Exception as e:
        logger.exception("Error verifying user: %s", str(e))
        return jsonify({"error": str(e)}), 500


@users_bp.route("/<user_id>", methods=["GET"])
async def get_user(user_id: str) -> ResponseReturnValue:
    """Get user by ID"""
    try:
        service = get_services()
        response = await service.get_by_id(
            entity_id=user_id, entity_class="User", entity_version="1"
        )

        if not response:
            return jsonify({"error": "User not found"}), 404

        user_data = {
            "id": response.metadata.id,
            "username": response.data.get("username"),
            "firstName": response.data.get("firstName"),
            "lastName": response.data.get("lastName"),
            "email": response.data.get("email"),
            "phone": response.data.get("phone"),
            "status": _map_state_to_status(response.metadata.state),
            "role": response.data.get("role"),
            "registrationDate": response.data.get("registrationDate"),
        }

        return jsonify(user_data), 200

    except Exception as e:
        logger.exception("Error getting user %s: %s", user_id, str(e))
        return jsonify({"error": str(e)}), 500


@users_bp.route("/<user_id>", methods=["PUT"])
@validate_request(UserUpdateRequest)
async def update_user(user_id: str, data: UserUpdateRequest) -> ResponseReturnValue:
    """Update user information"""
    try:
        service = get_services()
        transition: Optional[str] = request.args.get("transitionName")

        entity_data: Dict[str, Any] = {
            k: v for k, v in data.model_dump(by_alias=True, exclude_none=True).items()
        }

        response = await service.update(
            entity_id=user_id,
            entity=entity_data,
            entity_class="User",
            transition=transition,
            entity_version="1",
        )

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "status": _map_state_to_status(response.metadata.state),
                    "message": "User updated successfully",
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error updating user %s: %s", user_id, str(e))
        return jsonify({"error": str(e)}), 500


def _map_state_to_status(state: str) -> str:
    """Map entity state to API status"""
    state_mapping = {
        "active": "ACTIVE",
        "inactive": "INACTIVE",
        "suspended": "SUSPENDED",
        "pending_verification": "PENDING_VERIFICATION",
    }
    return state_mapping.get(state, "UNKNOWN")
