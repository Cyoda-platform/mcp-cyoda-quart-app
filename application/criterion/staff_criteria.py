"""
Staff Criteria for Purrfect Pets API

Validation criteria for staff-related business rules and workflows.
"""

import logging
from datetime import datetime
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.staff.version_1.staff import Staff


class SuspensionReviewCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for reviewing staff suspensions.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SuspensionReviewCriterion",
            description="Validates staff suspension review and potential reinstatement",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if staff suspension can be reviewed for reinstatement.

        Args:
            entity: The Staff entity to validate
            **kwargs: Additional criteria parameters

        Returns:
            True if suspension can be reviewed, False otherwise
        """
        try:
            self.logger.info(
                f"Validating staff suspension review {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Staff for type-safe operations
            staff = cast_entity(entity, Staff)

            # Staff must be suspended
            if not staff.is_suspended():
                self.logger.warning(
                    f"Staff {staff.technical_id} is not suspended: {staff.state}"
                )
                return False

            # Check suspension duration
            if not self._validate_suspension_duration(staff):
                return False

            # Check suspension reason severity
            if not self._validate_suspension_reason(staff):
                return False

            # Check for any pending disciplinary actions
            if not self._check_pending_actions(staff):
                return False

            # Validate employment history
            if not self._validate_employment_history(staff):
                return False

            # Check for completion of required training/counseling
            if not self._check_required_training(staff):
                return False

            self.logger.info(
                f"Staff {staff.technical_id} passed suspension review validation"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating staff suspension review {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_suspension_duration(self, staff: Staff) -> bool:
        """Validate suspension duration."""
        suspension_date_str = staff.get_metadata("suspension_date")
        if not suspension_date_str:
            self.logger.warning(
                f"Staff {staff.technical_id} - no suspension date found"
            )
            return False

        try:
            suspension_date = datetime.strptime(suspension_date_str, "%Y-%m-%d")
            days_suspended = (datetime.now() - suspension_date).days

            # Minimum suspension period based on reason
            suspension_reason = staff.get_metadata("suspension_reason", "").lower()
            min_days = 7  # Default minimum

            if "misconduct" in suspension_reason:
                min_days = 14
            elif "violation" in suspension_reason:
                min_days = 30
            elif "safety" in suspension_reason:
                min_days = 21

            if days_suspended < min_days:
                self.logger.warning(
                    f"Staff {staff.technical_id} - insufficient suspension duration: {days_suspended} < {min_days} days"
                )
                return False

            # Maximum suspension period (beyond which termination should be considered)
            if days_suspended > 180:
                self.logger.warning(
                    f"Staff {staff.technical_id} - suspension too long: {days_suspended} days"
                )
                return False

            return True

        except ValueError:
            self.logger.warning(
                f"Staff {staff.technical_id} - invalid suspension date format"
            )
            return False

    def _validate_suspension_reason(self, staff: Staff) -> bool:
        """Validate suspension reason severity."""
        suspension_reason = staff.get_metadata("suspension_reason", "").lower()

        # Serious violations that may not be eligible for reinstatement
        serious_violations = [
            "theft",
            "fraud",
            "harassment",
            "violence",
            "abuse",
            "criminal",
            "illegal",
            "safety violation",
        ]

        for violation in serious_violations:
            if violation in suspension_reason:
                self.logger.warning(
                    f"Staff {staff.technical_id} - serious violation: {violation}"
                )
                return False

        return True

    def _check_pending_actions(self, staff: Staff) -> bool:
        """Check for any pending disciplinary actions."""
        pending_actions = staff.get_metadata("pending_disciplinary_actions", [])
        if pending_actions:
            self.logger.warning(
                f"Staff {staff.technical_id} - has pending disciplinary actions: {pending_actions}"
            )
            return False

        # Check for pending investigations
        pending_investigations = staff.get_metadata("pending_investigations", [])
        if pending_investigations:
            self.logger.warning(
                f"Staff {staff.technical_id} - has pending investigations: {pending_investigations}"
            )
            return False

        return True

    def _validate_employment_history(self, staff: Staff) -> bool:
        """Validate employment history."""
        # Check employment duration
        try:
            hire_date = datetime.strptime(staff.hire_date, "%Y-%m-%d")
            employment_days = (datetime.now() - hire_date).days

            # Staff with very short employment history may need additional review
            if employment_days < 90:
                self.logger.info(
                    f"Staff {staff.technical_id} - short employment history: {employment_days} days"
                )
                # This is informational, not a failure

            # Check previous disciplinary actions
            disciplinary_history = staff.get_metadata("disciplinary_history", [])
            if len(disciplinary_history) > 2:
                self.logger.warning(
                    f"Staff {staff.technical_id} - extensive disciplinary history: {len(disciplinary_history)} actions"
                )
                return False

            return True

        except ValueError:
            self.logger.warning(
                f"Staff {staff.technical_id} - invalid hire date format"
            )
            return False

    def _check_required_training(self, staff: Staff) -> bool:
        """Check for completion of required training/counseling."""
        # Check if required training was completed during suspension
        required_training = staff.get_metadata("required_training_completed", False)
        if not required_training:
            self.logger.warning(
                f"Staff {staff.technical_id} - required training not completed"
            )
            return False

        # Check for counseling completion if required
        suspension_reason = staff.get_metadata("suspension_reason", "").lower()
        if "counseling" in suspension_reason or "training" in suspension_reason:
            counseling_completed = staff.get_metadata("counseling_completed", False)
            if not counseling_completed:
                self.logger.warning(
                    f"Staff {staff.technical_id} - required counseling not completed"
                )
                return False

        return True
