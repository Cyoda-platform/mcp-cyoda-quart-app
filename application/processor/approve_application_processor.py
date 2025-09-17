"""
ApproveApplicationProcessor for Purrfect Pets Application

Handles approval of pending adoption applications.
Approves adoption applications for completion.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.adoption.version_1.adoption import Adoption
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class ApproveApplicationProcessor(CyodaProcessor):
    """
    Processor for approving Adoption applications.
    Approves pending adoption applications for completion.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ApproveApplicationProcessor",
            description="Approve adoption application for completion",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Approve the Adoption application according to functional requirements.

        Args:
            entity: The Adoption entity to approve
            **kwargs: Additional processing parameters

        Returns:
            The approved adoption application
        """
        try:
            self.logger.info(
                f"Approving adoption application {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Adoption for type-safe operations
            adoption = cast_entity(entity, Adoption)

            # Validate adoption can be approved
            self._validate_adoption_for_approval(adoption)

            # Approve the application
            self._approve_adoption_application(adoption)

            # Notify owner of approval (simulated)
            await self._notify_owner_approval(adoption)

            self.logger.info(
                f"Adoption application {adoption.technical_id} approved successfully"
            )

            return adoption

        except Exception as e:
            self.logger.error(
                f"Error approving adoption application {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_adoption_for_approval(self, adoption: Adoption) -> None:
        """
        Validate that adoption application can be approved.

        Args:
            adoption: The Adoption entity to validate

        Raises:
            ValueError: If adoption cannot be approved
        """
        if not adoption.is_pending():
            raise ValueError(
                f"Adoption application is not pending (current state: {adoption.state})"
            )

        # Validate required fields are present
        if not adoption.pet_id or len(adoption.pet_id.strip()) == 0:
            raise ValueError("Pet ID is required for approval")

        if not adoption.owner_id or len(adoption.owner_id.strip()) == 0:
            raise ValueError("Owner ID is required for approval")

        self.logger.info("Adoption application validation passed for approval")

    def _approve_adoption_application(self, adoption: Adoption) -> None:
        """
        Approve the adoption application according to functional requirements.

        Args:
            adoption: The Adoption entity to approve
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Add approval metadata
        adoption.add_metadata("approval_date", current_timestamp)
        adoption.add_metadata("status", "approved")
        adoption.add_metadata("approved_by", "ApproveApplicationProcessor")

        self.logger.info(
            f"Adoption application for pet {adoption.pet_id} approved on {current_timestamp}"
        )

    async def _notify_owner_approval(self, adoption: Adoption) -> None:
        """
        Notify owner about adoption approval (simulated).

        Args:
            adoption: The Adoption entity to notify about
        """
        try:
            entity_service = get_entity_service()

            # Get the owner entity to get email
            owner_response = await entity_service.get_by_id(
                entity_id=adoption.owner_id, entity_class="Owner", entity_version="1"
            )

            if owner_response and owner_response.data:
                owner_data = owner_response.data
                owner_email = getattr(owner_data, "email", "unknown@example.com")
                owner_name = getattr(owner_data, "name", "Unknown Owner")

                # Simulate sending approval notification email
                self.logger.info(
                    f"Approval notification email sent to {owner_email} for owner {owner_name}"
                )

                # Add metadata to track notification
                current_timestamp = (
                    datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                )
                adoption.add_metadata("owner_approval_notified", current_timestamp)
            else:
                self.logger.warning(
                    f"Owner {adoption.owner_id} not found for approval notification"
                )

        except Exception as e:
            self.logger.error(
                f"Failed to notify owner {adoption.owner_id} of approval: {str(e)}"
            )
            # Don't raise exception as the approval itself is valid
