"""
PetPaymentCriterion for Purrfect Pets API

Validates that payment has been completed for pet purchase.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.pet.version_1.pet import Pet


class PetPaymentCriterion(CyodaCriteriaChecker):
    """
    Criterion for validating Pet payment completion.
    Checks if payment has been completed for pet purchase.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetPaymentCriterion",
            description="Validates that payment has been completed for pet purchase",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if payment has been completed for the pet.

        Args:
            entity: The CyodaEntity to validate (expected to be Pet)
            **kwargs: Additional criteria parameters

        Returns:
            True if payment is completed successfully, False otherwise
        """
        try:
            self.logger.info(
                f"Validating payment for Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Check if pet is in pending state (reserved)
            if not pet.is_pending():
                self.logger.warning(
                    f"Pet {pet.technical_id} is not in pending state for payment validation"
                )
                return False

            # Verify payment transaction exists (would normally check payment service)
            # For demonstration, we'll check metadata for payment information
            if not pet.metadata:
                self.logger.warning(f"No metadata found for Pet {pet.technical_id}")
                return False

            # Check payment status is completed
            payment_status = pet.metadata.get("payment_status")
            if payment_status != "completed":
                self.logger.warning(
                    f"Payment status for Pet {pet.technical_id} is not completed: {payment_status}"
                )
                return False

            # Validate payment amount matches pet price
            payment_amount = pet.metadata.get("payment_amount")
            if payment_amount is None:
                self.logger.warning(f"No payment amount found for Pet {pet.technical_id}")
                return False

            if abs(float(payment_amount) - pet.price) > 0.01:  # Allow for small floating point differences
                self.logger.warning(
                    f"Payment amount ${payment_amount} does not match pet price ${pet.price} for Pet {pet.technical_id}"
                )
                return False

            # Confirm payment method is valid
            payment_method = pet.metadata.get("payment_method")
            valid_payment_methods = ["credit_card", "debit_card", "paypal", "bank_transfer"]
            if payment_method not in valid_payment_methods:
                self.logger.warning(
                    f"Invalid payment method '{payment_method}' for Pet {pet.technical_id}"
                )
                return False

            self.logger.info(
                f"Payment validation successful for Pet {pet.technical_id}"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating payment for Pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
