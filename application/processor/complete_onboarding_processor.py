"""
CompleteOnboardingProcessor for Cyoda Client Application

Handles the completion of employee onboarding
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.employee.version_1.employee import Employee
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class CompleteOnboardingProcessor(CyodaProcessor):
    """
    Processor for completing Employee onboarding.
    Transitions employee from onboarding to active state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CompleteOnboardingProcessor",
            description="Completes employee onboarding and activates employee",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Employee onboarding completion according to functional requirements.

        Args:
            entity: The Employee entity to activate
            **kwargs: Additional processing parameters

        Returns:
            The activated employee
        """
        try:
            self.logger.info(
                f"Completing onboarding for Employee {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Employee for type-safe operations
            employee = cast_entity(entity, Employee)

            # Activate the employee
            employee.is_active = True
            current_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            # Add onboarding completion metadata
            employee.add_metadata("onboarding_completed_at", current_timestamp)
            employee.add_metadata(
                "onboarding_completed_by", kwargs.get("completed_by", "system")
            )

            # If employee has a user account, activate it
            if employee.user_id:
                await self._activate_user_account(employee.user_id)

            # Log employee activation
            self.logger.info(
                f"Employee {employee.employee_id} onboarding completed successfully"
            )

            return employee

        except Exception as e:
            self.logger.error(
                f"Error completing onboarding for employee {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _activate_user_account(self, user_id: str) -> None:
        """
        Activate the associated user account.

        Args:
            user_id: The user ID to activate
        """
        try:
            entity_service = get_entity_service()

            # Note: In a real implementation, you would:
            # 1. Get the user entity
            # 2. Trigger the activate_user transition

            self.logger.info(f"Would activate user account: {user_id}")

            # This is where you would implement the actual user activation:
            # await entity_service.execute_transition(
            #     entity_id=user_id,
            #     transition="activate_user",
            #     entity_class="User"
            # )

        except Exception as e:
            self.logger.error(f"Error activating user account {user_id}: {str(e)}")
            # Don't raise here - employee onboarding can still complete
