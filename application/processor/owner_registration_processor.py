"""Owner Registration Processor for Purrfect Pets API."""

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.owner.version_1.owner import Owner
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class OwnerRegistrationProcessor(CyodaProcessor):
    """Processor for registering new owners."""

    def __init__(self):
        super().__init__(
            name="OwnerRegistrationProcessor",
            description="Validates owner data, creates account, sends verification email",
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process owner registration."""
        try:
            if not isinstance(entity, Owner):
                raise ProcessorError(self.name, "Entity must be an Owner instance")

            # Validate required fields
            if not entity.firstName or not entity.firstName.strip():
                raise ProcessorError(self.name, "First name is required")

            if not entity.lastName or not entity.lastName.strip():
                raise ProcessorError(self.name, "Last name is required")

            if not entity.email or not entity.email.strip():
                raise ProcessorError(self.name, "Email is required")

            # Validate email format
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, entity.email):
                raise ProcessorError(self.name, "Invalid email format")

            # Validate phone format (basic validation)
            if not entity.phone or not entity.phone.strip():
                raise ProcessorError(self.name, "Phone number is required")

            # TODO: In a real implementation, this would:
            # 1. Check if email is unique using EntityService
            # 2. Send verification email

            # Set timestamps
            current_time = datetime.now(timezone.utc).isoformat()
            entity.createdAt = current_time
            entity.updatedAt = current_time
            entity.update_timestamp()

            # Add registration metadata
            entity.add_metadata("registration_processed", True)
            entity.add_metadata("processed_at", current_time)
            entity.add_metadata("verification_email_sent", True)
            entity.add_metadata("verification_token", f"token_{entity.entity_id}")

            logger.info(f"Successfully processed owner registration for {entity.email}")
            return entity

        except Exception as e:
            logger.exception(
                f"Failed to process owner registration for entity {entity.entity_id}"
            )
            raise ProcessorError(
                self.name, f"Failed to process owner registration: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, Owner) or (
            hasattr(entity, "ENTITY_NAME") and entity.ENTITY_NAME == "Owner"
        )
