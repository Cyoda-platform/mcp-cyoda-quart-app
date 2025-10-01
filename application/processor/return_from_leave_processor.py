"""
ReturnFromLeaveProcessor for Cyoda Client Application

Handles employee return from leave
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.employee.version_1.employee import Employee
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ReturnFromLeaveProcessor(CyodaProcessor):
    """
    Processor for returning Employee from leave.
    Transitions employee from on_leave back to active state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReturnFromLeaveProcessor",
            description="Returns employee from leave to active status",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Employee return from leave according to functional requirements.

        Args:
            entity: The Employee entity returning from leave
            **kwargs: Additional processing parameters

        Returns:
            The active employee
        """
        try:
            self.logger.info(
                f"Processing return from leave for Employee {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Employee for type-safe operations
            employee = cast_entity(entity, Employee)

            # Return employee to active status
            current_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            # Add return metadata
            employee.add_metadata("returned_from_leave_at", current_timestamp)
            employee.add_metadata(
                "return_processed_by", kwargs.get("processed_by", "system")
            )

            # Archive previous leave information
            if employee.metadata and "leave_started_at" in employee.metadata:
                leave_start = employee.metadata.get("leave_started_at")
                if leave_start:
                    leave_duration = self._calculate_leave_duration(
                        leave_start, current_timestamp
                    )
                    employee.add_metadata("last_leave_duration_days", leave_duration)
                    employee.add_metadata("previous_leave_archived", leave_start)

            # Log employee return
            self.logger.info(
                f"Employee {employee.employee_id} returned from leave successfully"
            )

            return employee

        except Exception as e:
            self.logger.error(
                f"Error processing return from leave for employee {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _calculate_leave_duration(self, start_date: str, end_date: str) -> int:
        """
        Calculate leave duration in days.

        Args:
            start_date: Leave start date in ISO format
            end_date: Leave end date in ISO format

        Returns:
            Duration in days
        """
        try:
            start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            return (end - start).days
        except Exception as e:
            self.logger.warning(f"Could not calculate leave duration: {str(e)}")
            return 0
