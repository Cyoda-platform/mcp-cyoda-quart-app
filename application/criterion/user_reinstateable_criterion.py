"""
UserReinstateableCriterion for Purrfect Pets API

Validates that a suspended user can be reinstated.
"""

from datetime import datetime, timezone
from typing import Any

from application.entity.user.version_1.user import User
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class UserReinstateableCriterion(CyodaCriteriaChecker):
    """
    Criterion for validating User reinstatement eligibility.
    Checks if suspended user can be reinstated.
    """

    def __init__(self) -> None:
        super().__init__(
            name="UserReinstateableCriterion",
            description="Validates that a suspended user can be reinstated",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the suspended user can be reinstated.

        Args:
            entity: The CyodaEntity to validate (expected to be User)
            **kwargs: Additional criteria parameters

        Returns:
            True if user can be reinstated, False otherwise
        """
        try:
            self.logger.info(
                f"Validating reinstatement eligibility for User {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Check if user is in suspended state
            if not user.is_suspended():
                self.logger.warning(
                    f"User {user.technical_id} is not in suspended state"
                )
                return False

            # Check metadata for suspension information
            if not user.metadata:
                self.logger.warning(f"No metadata found for User {user.technical_id}")
                return False

            # Verify suspension reason allows reinstatement
            suspension_reason = user.metadata.get("suspension_reason", "")
            non_reinstateable_reasons = [
                "fraud",
                "permanent_ban",
                "legal_violation",
                "repeated_violations",
            ]

            if any(
                reason in suspension_reason.lower()
                for reason in non_reinstateable_reasons
            ):
                self.logger.warning(
                    f"Suspension reason '{suspension_reason}' does not allow reinstatement for User {user.technical_id}"
                )
                return False

            # Check if suspension period has been served (minimum 7 days)
            suspension_date_str = user.metadata.get("suspension_date")
            if suspension_date_str:
                try:
                    suspension_date = datetime.fromisoformat(
                        suspension_date_str.replace("Z", "+00:00")
                    )
                    current_date = datetime.now(timezone.utc)
                    days_suspended = (current_date - suspension_date).days

                    if days_suspended < 7:
                        self.logger.warning(
                            f"User {user.technical_id} has only been suspended for {days_suspended} days (minimum 7 required)"
                        )
                        return False
                except ValueError:
                    self.logger.warning(
                        f"Invalid suspension date format for User {user.technical_id}"
                    )
                    return False

            # Validate no pending violations exist
            pending_violations = user.metadata.get("pending_violations", [])
            if pending_violations:
                self.logger.warning(
                    f"User {user.technical_id} has pending violations: {pending_violations}"
                )
                return False

            # Confirm user has completed required actions (if any)
            required_actions = user.metadata.get("required_actions", [])
            completed_actions = user.metadata.get("completed_actions", [])

            for action in required_actions:
                if action not in completed_actions:
                    self.logger.warning(
                        f"User {user.technical_id} has not completed required action: {action}"
                    )
                    return False

            self.logger.info(
                f"Reinstatement validation successful for User {user.technical_id}"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating reinstatement for User {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
