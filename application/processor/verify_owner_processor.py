"""
VerifyOwnerProcessor for Purrfect Pets Application

Handles verification of owner eligibility for pet adoption.
Verifies owner documents and enables adoption capability.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.owner.version_1.owner import Owner


class VerifyOwnerProcessor(CyodaProcessor):
    """
    Processor for verifying Owner entities.
    Verifies owner eligibility for adoption based on provided documents.
    """

    def __init__(self) -> None:
        super().__init__(
            name="VerifyOwnerProcessor",
            description="Verify owner eligibility for pet adoption",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Verify the Owner entity according to functional requirements.

        Args:
            entity: The Owner entity to verify
            **kwargs: Additional processing parameters

        Returns:
            The verified owner entity
        """
        try:
            self.logger.info(
                f"Verifying Owner {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Owner for type-safe operations
            owner = cast_entity(entity, Owner)

            # Validate owner can be verified
            self._validate_owner_for_verification(owner)

            # Verify the owner
            self._verify_owner(owner)

            # Send verification confirmation (simulated)
            self._send_verification_confirmation(owner)

            self.logger.info(
                f"Owner {owner.technical_id} verified successfully"
            )

            return owner

        except Exception as e:
            self.logger.error(
                f"Error verifying owner {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_owner_for_verification(self, owner: Owner) -> None:
        """
        Validate that owner can be verified.

        Args:
            owner: The Owner entity to validate

        Raises:
            ValueError: If owner cannot be verified
        """
        if not owner.is_registered():
            raise ValueError(f"Owner {owner.name} is not registered (current state: {owner.state})")

        # Check if verification documents are provided
        if not owner.has_verification_documents():
            raise ValueError(f"Owner {owner.name} has not provided verification documents")

        self.logger.info(f"Owner {owner.name} validation passed for verification")

    def _verify_owner(self, owner: Owner) -> None:
        """
        Verify the owner according to functional requirements.

        Args:
            owner: The Owner entity to verify
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Add verification metadata
        owner.add_metadata("verification_date", current_timestamp)
        owner.add_metadata("status", "verified")
        owner.add_metadata("can_adopt", True)
        owner.add_metadata("verified_by", "VerifyOwnerProcessor")

        self.logger.info(
            f"Owner {owner.name} verified on {current_timestamp}"
        )

    def _send_verification_confirmation(self, owner: Owner) -> None:
        """
        Send verification confirmation email to the owner (simulated).

        Args:
            owner: The Owner entity to send confirmation to
        """
        # Simulate sending verification confirmation email
        self.logger.info(
            f"Verification confirmation email sent to {owner.email} for owner {owner.name}"
        )
        
        # Add metadata to track email sending
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        owner.add_metadata("verification_email_sent", current_timestamp)
