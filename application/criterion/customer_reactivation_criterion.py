"""
CustomerReactivationCriterion for Purrfect Pets API

Checks if a suspended customer account can be reactivated.
"""

from typing import Any

from application.entity.customer.version_1.customer import Customer
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class CustomerReactivationCriterion(CyodaCriteriaChecker):
    """
    Criterion that checks if a suspended customer account can be reactivated.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CustomerReactivationCriterion",
            description="Checks if a suspended customer account can be reactivated",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the customer account can be reactivated.

        Args:
            entity: The Customer entity to check
            **kwargs: Additional criteria parameters (reactivation data)

        Returns:
            True if the customer account can be reactivated, False otherwise
        """
        try:
            self.logger.info(
                f"Checking customer reactivation eligibility for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Customer for type-safe operations
            customer = cast_entity(entity, Customer)

            # Check if customer's current state is SUSPENDED
            if not customer.is_suspended():
                self.logger.info(
                    f"Customer {customer.technical_id} is not suspended (current state: {customer.state})"
                )
                return False

            # Get reactivation data from kwargs
            issues_resolved = kwargs.get("issuesResolved") or kwargs.get(
                "issues_resolved"
            )
            has_outstanding_debts = kwargs.get("hasOutstandingDebts") or kwargs.get(
                "has_outstanding_debts"
            )
            agrees_to_terms = kwargs.get("agreesToTerms") or kwargs.get(
                "agrees_to_terms"
            )

            # Check if suspension issues have been resolved
            if not issues_resolved:
                self.logger.info(
                    f"Customer {customer.technical_id} suspension issues not resolved"
                )
                return False

            # Check if customer has outstanding debts
            if has_outstanding_debts:
                self.logger.info(
                    f"Customer {customer.technical_id} has outstanding debts"
                )
                return False

            # Check if customer agrees to updated terms
            if not agrees_to_terms:
                self.logger.info(
                    f"Customer {customer.technical_id} does not agree to updated terms"
                )
                return False

            self.logger.info(
                f"Customer {customer.technical_id} account can be reactivated"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error checking customer reactivation eligibility for {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
