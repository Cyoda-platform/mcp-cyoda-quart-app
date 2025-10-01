"""
TerminateEmployeeProcessor for Cyoda Client Application

Handles employee termination and cleanup
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.employee.version_1.employee import Employee
from services.services import get_entity_service


class TerminateEmployeeProcessor(CyodaProcessor):
    """
    Processor for terminating Employee and performing cleanup.
    Transitions employee from active to terminated state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="TerminateEmployeeProcessor",
            description="Terminates employee and performs cleanup",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Employee termination according to functional requirements.

        Args:
            entity: The Employee entity to terminate
            **kwargs: Additional processing parameters

        Returns:
            The terminated employee
        """
        try:
            self.logger.info(
                f"Terminating Employee {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Employee for type-safe operations
            employee = cast_entity(entity, Employee)

            # Terminate the employee
            employee.is_active = False
            current_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # Add termination metadata
            employee.add_metadata("terminated_at", current_timestamp)
            employee.add_metadata("termination_reason", kwargs.get("reason", "Employment terminated"))
            employee.add_metadata("termination_type", kwargs.get("termination_type", "voluntary"))
            employee.add_metadata("terminated_by", kwargs.get("terminated_by", "system"))

            # If employee has a user account, deactivate it
            if employee.user_id:
                await self._deactivate_user_account(employee.user_id)

            # Archive employment information
            if employee.hire_date:
                employment_duration = self._calculate_employment_duration(
                    employee.hire_date, 
                    current_timestamp
                )
                employee.add_metadata("employment_duration_days", employment_duration)

            # Log employee termination
            self.logger.info(
                f"Employee {employee.employee_id} terminated successfully"
            )

            return employee

        except Exception as e:
            self.logger.error(
                f"Error terminating employee {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _deactivate_user_account(self, user_id: str) -> None:
        """
        Deactivate the associated user account.
        
        Args:
            user_id: The user ID to deactivate
        """
        try:
            entity_service = get_entity_service()
            
            # Note: In a real implementation, you would:
            # 1. Get the user entity
            # 2. Trigger the deactivate_user transition
            
            self.logger.info(f"Would deactivate user account: {user_id}")
            
            # This is where you would implement the actual user deactivation:
            # await entity_service.execute_transition(
            #     entity_id=user_id,
            #     transition="deactivate_user",
            #     entity_class="User"
            # )

        except Exception as e:
            self.logger.error(f"Error deactivating user account {user_id}: {str(e)}")
            # Don't raise here - employee termination can still complete

    def _calculate_employment_duration(self, hire_date: str, termination_date: str) -> int:
        """
        Calculate employment duration in days.
        
        Args:
            hire_date: Hire date in ISO format
            termination_date: Termination date in ISO format
            
        Returns:
            Duration in days
        """
        try:
            start = datetime.fromisoformat(hire_date.replace("Z", "+00:00"))
            end = datetime.fromisoformat(termination_date.replace("Z", "+00:00"))
            return (end - start).days
        except Exception as e:
            self.logger.warning(f"Could not calculate employment duration: {str(e)}")
            return 0
