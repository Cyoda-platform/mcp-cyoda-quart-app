"""
StartLeaveProcessor for Cyoda Client Application

Handles putting employees on leave
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.employee.version_1.employee import Employee


class StartLeaveProcessor(CyodaProcessor):
    """
    Processor for putting Employee on leave.
    Transitions employee from active to on_leave state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="StartLeaveProcessor",
            description="Puts employee on temporary leave",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Employee leave start according to functional requirements.

        Args:
            entity: The Employee entity to put on leave
            **kwargs: Additional processing parameters

        Returns:
            The employee on leave
        """
        try:
            self.logger.info(
                f"Starting leave for Employee {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Employee for type-safe operations
            employee = cast_entity(entity, Employee)

            # Put employee on leave (keep is_active as True since they're still employed)
            current_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # Add leave metadata
            employee.add_metadata("leave_started_at", current_timestamp)
            employee.add_metadata("leave_type", kwargs.get("leave_type", "general"))
            employee.add_metadata("leave_reason", kwargs.get("reason", "Personal leave"))
            
            # Expected return date if provided
            if "expected_return_date" in kwargs:
                employee.add_metadata("expected_return_date", kwargs["expected_return_date"])

            # Log employee leave start
            self.logger.info(
                f"Employee {employee.employee_id} started leave successfully"
            )

            return employee

        except Exception as e:
            self.logger.error(
                f"Error starting leave for employee {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
