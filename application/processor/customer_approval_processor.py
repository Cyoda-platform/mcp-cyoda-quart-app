"""
CustomerApprovalProcessor for Purrfect Pets API

Handles customer approval process for pet adoptions.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.customer.version_1.customer import Customer


class CustomerApprovalProcessor(CyodaProcessor):
    """
    Processor for Customer approval.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CustomerApprovalProcessor",
            description="Processes customer approval for pet adoptions",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process Customer approval according to functional requirements.

        Args:
            entity: The Customer entity to approve
            **kwargs: Additional processing parameters

        Returns:
            The processed customer entity
        """
        try:
            self.logger.info(
                f"Processing Customer approval {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Customer for type-safe operations
            customer = cast_entity(entity, Customer)

            # 1. Review customer eligibility criteria
            await self._review_eligibility_criteria(customer)

            # 2. Check adoption history (if any)
            await self._check_adoption_history(customer)

            # 3. Validate housing suitability
            await self._validate_housing_suitability(customer)

            # 4. Approve customer for adoptions
            customer.add_metadata(
                "approval_date",
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            )
            customer.add_metadata("approved_by", "System")

            # 5. Send approval notification (simulated)
            await self._send_approval_notification(customer)

            # 6. Grant adoption privileges
            customer.add_metadata("adoption_privileges", True)
            customer.add_metadata("max_concurrent_applications", 3)

            # 7. Update customer state to APPROVED (handled by workflow transition)
            self.logger.info(
                f"Customer approval {customer.technical_id} processed successfully"
            )

            return customer

        except Exception as e:
            self.logger.error(
                f"Error processing customer approval {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _review_eligibility_criteria(self, customer: Customer) -> None:
        """
        Review customer eligibility criteria.

        Args:
            customer: The customer entity
        """
        # Check basic eligibility requirements
        if customer.housing_type in ["Apartment"] and not customer.has_yard:
            self.logger.info(
                f"Customer {customer.technical_id} approved despite no yard (apartment living)"
            )

        self.logger.info(
            f"Eligibility criteria reviewed for customer {customer.technical_id}"
        )

    async def _check_adoption_history(self, customer: Customer) -> None:
        """
        Check adoption history.

        Args:
            customer: The customer entity
        """
        # In a real implementation, this would check previous adoptions
        adoption_history = customer.get_metadata("adoption_history", [])
        self.logger.info(
            f"Adoption history checked for customer {customer.technical_id}: {len(adoption_history)} previous adoptions"
        )

    async def _validate_housing_suitability(self, customer: Customer) -> None:
        """
        Validate housing suitability.

        Args:
            customer: The customer entity
        """
        # Basic housing validation
        suitable_housing = customer.housing_type in [
            "House",
            "Condo",
            "Townhouse",
            "Apartment",
        ]
        if not suitable_housing:
            raise ValueError(
                f"Housing type {customer.housing_type} may not be suitable for pet adoption"
            )

        self.logger.info(
            f"Housing suitability validated for customer {customer.technical_id}"
        )

    async def _send_approval_notification(self, customer: Customer) -> None:
        """
        Send approval notification.

        Args:
            customer: The customer entity
        """
        # In a real implementation, this would send an email
        self.logger.info(
            f"Approval notification sent to {customer.email} for customer {customer.get_full_name()}"
        )
