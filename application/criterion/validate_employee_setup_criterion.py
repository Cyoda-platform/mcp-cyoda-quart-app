"""
ValidateEmployeeSetup Criterion for Cyoda Client Application

Validates that an Employee has required setup before activation
as specified in functional requirements.
"""

from typing import Any

from application.entity.employee.version_1.employee import Employee
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class ValidateEmployeeSetup(CyodaCriteriaChecker):
    """
    Validation criterion for Employee that checks if employee has required setup
    before onboarding can be completed.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ValidateEmployeeSetup",
            description="Validates that employee has required setup for activation",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the employee has required setup for onboarding completion.

        Args:
            entity: The CyodaEntity to validate (expected to be Employee)
            **kwargs: Additional criteria parameters

        Returns:
            True if the employee has required setup, False otherwise
        """
        try:
            self.logger.info(
                f"Validating setup for employee {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Employee for type-safe operations
            employee = cast_entity(entity, Employee)

            # Check if position_id is set
            if not employee.position_id or len(employee.position_id.strip()) == 0:
                self.logger.warning(
                    f"Employee {employee.employee_id} has no position assigned"
                )
                return False

            # Check if hire_date is set
            if not employee.hire_date or len(employee.hire_date.strip()) == 0:
                self.logger.warning(
                    f"Employee {employee.employee_id} has no hire date set"
                )
                return False

            # Validate hire date format
            try:
                from datetime import datetime

                datetime.fromisoformat(employee.hire_date.replace("Z", "+00:00"))
            except ValueError:
                self.logger.warning(
                    f"Employee {employee.employee_id} has invalid hire date format: {employee.hire_date}"
                )
                return False

            # Check if required personal information is complete
            if not employee.first_name or len(employee.first_name.strip()) == 0:
                self.logger.warning(
                    f"Employee {employee.employee_id} has no first name"
                )
                return False

            if not employee.last_name or len(employee.last_name.strip()) == 0:
                self.logger.warning(f"Employee {employee.employee_id} has no last name")
                return False

            if not employee.email or len(employee.email.strip()) == 0:
                self.logger.warning(
                    f"Employee {employee.employee_id} has no email address"
                )
                return False

            self.logger.info(f"Employee {employee.employee_id} passed setup validation")
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating employee setup {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
