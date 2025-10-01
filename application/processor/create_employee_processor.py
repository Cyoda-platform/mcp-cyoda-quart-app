"""
CreateEmployeeProcessor for Cyoda Client Application

Handles the creation of employee records
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.employee.version_1.employee import Employee
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CreateEmployeeProcessor(CyodaProcessor):
    """
    Processor for creating Employee records.
    Initializes employee in onboarding state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CreateEmployeeProcessor",
            description="Creates employee record in onboarding state",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Employee creation according to functional requirements.

        Args:
            entity: The Employee entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed employee in onboarding state
        """
        try:
            self.logger.info(
                f"Creating Employee {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Employee for type-safe operations
            employee = cast_entity(entity, Employee)

            # Set employee as inactive during onboarding
            employee.is_active = False
            current_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            # Update timestamps
            if not employee.created_at:
                employee.created_at = current_timestamp

            # Validate position exists (in real implementation, you would check with entity service)
            self._validate_position_exists(employee.position_id)

            # Generate or validate employee ID
            self._validate_employee_id(employee)

            # Log employee creation
            self.logger.info(
                f"Employee {employee.employee_id} created successfully for position {employee.position_id}"
            )

            return employee

        except Exception as e:
            self.logger.error(
                f"Error creating employee {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_position_exists(self, position_id: str) -> None:
        """
        Validate that the position exists.

        Args:
            position_id: The position ID to validate
        """
        # In a real implementation, you would query the entity service to check if position exists
        if not position_id or len(position_id.strip()) == 0:
            raise ValueError("Position ID is required")

        self.logger.debug(f"Position validation passed for: {position_id}")

    def _validate_employee_id(self, employee: Employee) -> None:
        """
        Validate or generate employee ID.

        Args:
            employee: The employee entity
        """
        if not employee.employee_id or len(employee.employee_id.strip()) == 0:
            raise ValueError("Employee ID is required")

        # Ensure employee ID is uppercase
        employee.employee_id = employee.employee_id.upper()

        self.logger.debug(f"Employee ID validated: {employee.employee_id}")
