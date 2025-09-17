"""
RegisterOwnerProcessor for Purrfect Pets Application

Handles registration of new owners in the system.
Registers new owner and validates basic information.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.owner.version_1.owner import Owner
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class RegisterOwnerProcessor(CyodaProcessor):
    """
    Processor for registering Owner entities.
    Registers new owner and validates basic information.
    """

    def __init__(self) -> None:
        super().__init__(
            name="RegisterOwnerProcessor",
            description="Register new owner and validate basic information",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Register the Owner entity according to functional requirements.

        Args:
            entity: The Owner entity to register
            **kwargs: Additional processing parameters

        Returns:
            The registered owner entity
        """
        try:
            self.logger.info(
                f"Registering Owner {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Owner for type-safe operations
            owner = cast_entity(entity, Owner)

            # Validate owner data for registration
            self._validate_owner_for_registration(owner)

            # Register the owner
            self._register_owner(owner)

            # Send welcome email (simulated)
            self._send_welcome_email(owner)

            self.logger.info(f"Owner {owner.technical_id} registered successfully")

            return owner

        except Exception as e:
            self.logger.error(
                f"Error registering owner {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_owner_for_registration(self, owner: Owner) -> None:
        """
        Validate owner data for registration.

        Args:
            owner: The Owner entity to validate

        Raises:
            ValueError: If validation fails
        """
        # Basic validation - Pydantic handles most field validation
        if not owner.name or len(owner.name.strip()) == 0:
            raise ValueError("Owner name is required")

        if not owner.email:
            raise ValueError("Owner email is required")

        if not owner.phone or len(owner.phone.strip()) == 0:
            raise ValueError("Owner phone is required")

        if not owner.address or len(owner.address.strip()) == 0:
            raise ValueError("Owner address is required")

        if not owner.experience or len(owner.experience.strip()) == 0:
            raise ValueError("Owner experience level is required")

        if not owner.preferences or len(owner.preferences.strip()) == 0:
            raise ValueError("Owner preferences are required")

        self.logger.info(f"Owner data validation passed for {owner.name}")

    def _register_owner(self, owner: Owner) -> None:
        """
        Register the owner according to functional requirements.

        Args:
            owner: The Owner entity to register
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Add registration metadata
        owner.add_metadata("registration_date", current_timestamp)
        owner.add_metadata("status", "registered")
        owner.add_metadata("registered_by", "RegisterOwnerProcessor")

        # Initialize empty lists for relationships if not already set
        if not hasattr(owner, "pet_ids") or owner.pet_ids is None:
            owner.pet_ids = []
        if not hasattr(owner, "adoption_ids") or owner.adoption_ids is None:
            owner.adoption_ids = []

        self.logger.info(f"Owner {owner.name} registered on {current_timestamp}")

    def _send_welcome_email(self, owner: Owner) -> None:
        """
        Send welcome email to the owner (simulated).

        Args:
            owner: The Owner entity to send email to
        """
        # Simulate sending welcome email
        self.logger.info(f"Welcome email sent to {owner.email} for owner {owner.name}")

        # Add metadata to track email sending
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        owner.add_metadata("welcome_email_sent", current_timestamp)
