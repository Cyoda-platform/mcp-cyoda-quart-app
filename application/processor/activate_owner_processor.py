"""
ActivateOwnerProcessor for Purrfect Pets Application

Handles activation of verified owners for adoption activities.
Activates owners when they start the adoption process.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.owner.version_1.owner import Owner


class ActivateOwnerProcessor(CyodaProcessor):
    """
    Processor for activating Owner entities.
    Activates verified owners for adoption activities.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ActivateOwnerProcessor",
            description="Activate owner for adoption activities",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Activate the Owner entity according to functional requirements.

        Args:
            entity: The Owner entity to activate
            **kwargs: Additional processing parameters

        Returns:
            The activated owner entity
        """
        try:
            self.logger.info(
                f"Activating Owner {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Owner for type-safe operations
            owner = cast_entity(entity, Owner)

            # Validate owner can be activated
            self._validate_owner_for_activation(owner)

            # Activate the owner
            self._activate_owner(owner)

            self.logger.info(
                f"Owner {owner.technical_id} activated successfully"
            )

            return owner

        except Exception as e:
            self.logger.error(
                f"Error activating owner {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_owner_for_activation(self, owner: Owner) -> None:
        """
        Validate that owner can be activated.

        Args:
            owner: The Owner entity to validate

        Raises:
            ValueError: If owner cannot be activated
        """
        if not owner.is_verified():
            raise ValueError(f"Owner {owner.name} is not verified (current state: {owner.state})")

        self.logger.info(f"Owner {owner.name} validation passed for activation")

    def _activate_owner(self, owner: Owner) -> None:
        """
        Activate the owner according to functional requirements.

        Args:
            owner: The Owner entity to activate
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Add activation metadata
        owner.add_metadata("activation_date", current_timestamp)
        owner.add_metadata("status", "active")
        owner.add_metadata("activated_by", "ActivateOwnerProcessor")

        self.logger.info(
            f"Owner {owner.name} activated on {current_timestamp}"
        )
