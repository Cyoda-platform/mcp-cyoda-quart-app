"""
AdoptionReturnProcessor for Purrfect Pets API

Processes the return of an adopted pet.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.adoption.version_1.adoption import Adoption


class AdoptionReturnProcessor(CyodaProcessor):
    """
    Processor for Adoption return that processes the return of an adopted pet.
    """

    def __init__(self) -> None:
        super().__init__(
            name="AdoptionReturnProcessor",
            description="Processes the return of an adopted pet",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Adoption return according to functional requirements.

        Args:
            entity: The Adoption entity to process (must be completed or follow-up completed)
            **kwargs: Additional processing parameters (return reason, return date)

        Returns:
            The processed adoption entity in returned state
        """
        try:
            self.logger.info(
                f"Processing Adoption return for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Adoption for type-safe operations
            adoption = cast_entity(entity, Adoption)

            # Get return information from kwargs
            return_reason = kwargs.get("returnReason") or kwargs.get("return_reason")
            return_date = kwargs.get("returnDate") or kwargs.get("return_date")
            staff_member = kwargs.get("staffMember") or kwargs.get("staff_member")

            # Validate adoption can be returned
            if adoption.is_returned():
                raise ValueError("Adoption is already returned")

            # Validate return reason is provided
            if not return_reason:
                raise ValueError("Return reason is required")

            # Set return date and reason
            adoption.return_reason = return_reason
            adoption.set_return_date()

            # Validate return reason
            self._validate_return_reason(return_reason)

            # Process pet return (in a real system)
            # This would update the pet status and make it available again
            self.logger.info(
                f"Would update pet {adoption.pet_id} status to available after return"
            )

            # Process refund if applicable (in a real system)
            # This would calculate and process any refund based on return policy
            self.logger.info(
                f"Would process refund calculation for adoption {adoption.technical_id}"
            )

            # Create return documentation (in a real system)
            # This would create return forms, health certificates, etc.
            self.logger.info(
                f"Would create return documentation for adoption {adoption.technical_id}"
            )

            # Notify relevant staff (in a real system)
            self.logger.info(
                f"Would notify relevant staff of pet return for adoption {adoption.technical_id}"
            )

            # Log return activity
            return_info = f"Pet returned. Reason: {return_reason}"
            if staff_member:
                return_info += f" (Processed by: {staff_member})"
            
            self.logger.info(
                f"Adoption {adoption.technical_id} - {return_info}"
            )

            return adoption

        except Exception as e:
            self.logger.error(
                f"Error processing adoption return {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_return_reason(self, return_reason: str) -> None:
        """
        Validate return reason.

        Args:
            return_reason: The return reason to validate

        Raises:
            ValueError: If return reason is invalid
        """
        if not return_reason or len(return_reason.strip()) == 0:
            raise ValueError("Return reason must be non-empty")

        if len(return_reason.strip()) > 1000:
            raise ValueError("Return reason must be at most 1000 characters")

        # Common return reasons (in a real system, these might be predefined categories)
        common_reasons = [
            "allergies",
            "behavioral_issues",
            "housing_change",
            "financial_hardship",
            "family_circumstances",
            "pet_health_issues",
            "incompatibility",
            "other"
        ]

        # Log if reason matches common categories
        reason_lower = return_reason.lower()
        for common_reason in common_reasons:
            if common_reason.replace("_", " ") in reason_lower:
                self.logger.debug(f"Return reason categorized as: {common_reason}")
                break

        self.logger.debug(f"Return reason validation passed: {return_reason}")
