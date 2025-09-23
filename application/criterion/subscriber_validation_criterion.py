"""
SubscriberValidationCriterion for Cat Fact Subscription Application

Validates that a Subscriber meets all required business rules before it can
proceed to the active state as specified in functional requirements.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.subscriber.version_1.subscriber import Subscriber


class SubscriberValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Subscriber that checks all business rules
    before the entity can proceed to active state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SubscriberValidationCriterion",
            description="Validates Subscriber business rules and email format",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the subscriber meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be Subscriber)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating subscriber {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Subscriber for type-safe operations
            subscriber = cast_entity(entity, Subscriber)

            # Validate email format
            if not subscriber.email or "@" not in subscriber.email:
                self.logger.warning(
                    f"Subscriber {subscriber.technical_id} has invalid email: '{subscriber.email}'"
                )
                return False

            # Check email length
            if len(subscriber.email) > 254:
                self.logger.warning(
                    f"Subscriber {subscriber.technical_id} email too long: {len(subscriber.email)} characters"
                )
                return False

            # Validate subscription status
            if subscriber.subscription_status not in ["active", "paused", "cancelled"]:
                self.logger.warning(
                    f"Subscriber {subscriber.technical_id} has invalid subscription status: {subscriber.subscription_status}"
                )
                return False

            # Validate preferred time format if provided
            if subscriber.preferred_time:
                try:
                    parts = subscriber.preferred_time.split(":")
                    if len(parts) != 2:
                        raise ValueError("Invalid time format")
                    
                    hour, minute = int(parts[0]), int(parts[1])
                    if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                        raise ValueError("Invalid time values")
                        
                except (ValueError, IndexError):
                    self.logger.warning(
                        f"Subscriber {subscriber.technical_id} has invalid preferred time: {subscriber.preferred_time}"
                    )
                    return False

            self.logger.info(
                f"Subscriber {subscriber.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating subscriber {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
