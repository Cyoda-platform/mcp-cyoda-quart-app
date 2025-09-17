"""
CustomerReactivationProcessor for Purrfect Pets API

Reactivates a suspended customer account.
"""

import logging
from typing import Any, Dict

from application.entity.customer.version_1.customer import Customer
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CustomerReactivationProcessor(CyodaProcessor):
    """
    Processor for Customer reactivation that reactivates a suspended customer account.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CustomerReactivationProcessor",
            description="Reactivates a suspended customer account",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Customer reactivation according to functional requirements.

        Args:
            entity: The Customer entity to process (must be suspended)
            **kwargs: Additional processing parameters (reactivation notes)

        Returns:
            The processed customer entity in active state
        """
        try:
            self.logger.info(
                f"Processing Customer reactivation for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Customer for type-safe operations
            customer = cast_entity(entity, Customer)

            # Get reactivation information from kwargs
            reactivation_notes = kwargs.get("reactivationNotes") or kwargs.get(
                "reactivation_notes"
            )

            # Validate customer is currently suspended
            if not customer.is_suspended():
                raise ValueError("Customer must be suspended to reactivate")

            # Validate suspension issues have been resolved (placeholder)
            # In a real system, this would check various conditions
            self._validate_reactivation_eligibility(customer, kwargs)

            # Update suspension record with reactivation date
            # In a real system, you would update the CustomerSuspension entity
            reactivation_info = f"Account reactivated"
            if reactivation_notes:
                reactivation_info += f": {reactivation_notes}"

            # Notify customer of reactivation (in a real system)
            # This would send an email or other notification to the customer
            self.logger.info(
                f"Would notify customer {customer.email} of account reactivation"
            )

            # Log reactivation activity
            self.logger.info(
                f"Customer {customer.technical_id} ({customer.get_full_name()}) reactivated. {reactivation_info}"
            )

            return customer

        except Exception as e:
            self.logger.error(
                f"Error processing customer reactivation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_reactivation_eligibility(
        self, customer: Customer, kwargs: Dict[str, Any]
    ) -> None:
        """
        Validate that customer is eligible for reactivation.

        Args:
            customer: The Customer entity
            kwargs: Additional parameters for validation

        Raises:
            ValueError: If customer is not eligible for reactivation
        """
        # Check if suspension issues have been resolved
        issues_resolved = kwargs.get("issuesResolved") or kwargs.get("issues_resolved")
        if not issues_resolved:
            raise ValueError("Suspension issues must be resolved before reactivation")

        # Check for outstanding debts (placeholder)
        has_outstanding_debts = kwargs.get("hasOutstandingDebts") or kwargs.get(
            "has_outstanding_debts"
        )
        if has_outstanding_debts:
            raise ValueError(
                "Customer must resolve outstanding debts before reactivation"
            )

        # Check if customer agrees to terms (placeholder)
        agrees_to_terms = kwargs.get("agreesToTerms") or kwargs.get("agrees_to_terms")
        if not agrees_to_terms:
            raise ValueError("Customer must agree to updated terms before reactivation")

        self.logger.debug(
            f"Reactivation eligibility validation passed for customer {customer.technical_id}"
        )
