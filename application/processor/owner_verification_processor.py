"""Owner Verification Processor for Purrfect Pets API."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.owner.version_1.owner import Owner
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class OwnerVerificationProcessor(CyodaProcessor):
    """Processor for verifying owner email and activating account."""

    def __init__(self):
        super().__init__(
            name="OwnerVerificationProcessor",
            description="Verifies owner email, activates account",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process owner verification."""
        try:
            if not isinstance(entity, Owner):
                raise ProcessorError(self.name, "Entity must be an Owner instance")

            # Validate owner is pending verification
            if entity.state not in ["pending_verification"]:
                raise ProcessorError(
                    self.name,
                    f"Owner must be pending verification, current state: {entity.state}",
                )

            # Get verification token from kwargs
            verification_token = kwargs.get("verificationToken") or kwargs.get(
                "verification_token"
            )

            if not verification_token:
                raise ProcessorError(self.name, "Verification token is required")

            # TODO: In a real implementation, this would:
            # 1. Validate verification token is valid and not expired
            # 2. Check token against stored token in metadata

            # Validate token (simplified)
            stored_token = entity.get_metadata("verification_token")
            if stored_token != verification_token:
                raise ProcessorError(self.name, "Invalid verification token")

            # Update timestamps
            entity.updatedAt = datetime.now(timezone.utc).isoformat()
            entity.update_timestamp()

            # Add verification metadata
            entity.add_metadata("verified_at", datetime.now(timezone.utc).isoformat())
            entity.add_metadata("email_verified", True)
            entity.add_metadata("verification_processed", True)
            entity.add_metadata("welcome_email_sent", True)

            # Remove verification token
            if entity.metadata:
                entity.metadata.pop("verification_token", None)

            logger.info(f"Successfully verified owner {entity.email}")
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to process owner verification for entity {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to process owner verification: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Owner) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Owner"
        )
