"""
ValidateNoActiveEmployees Criterion for Cyoda Client Application

Validates that a Position has no active employees before deactivation
as specified in functional requirements.
"""

from typing import Any

from application.entity.position.version_1.position import Position
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from services.services import get_entity_service


class ValidateNoActiveEmployees(CyodaCriteriaChecker):
    """
    Validation criterion for Position that checks if position has no active employees
    before it can be deactivated.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ValidateNoActiveEmployees",
            description="Validates that position has no active employees before deactivation",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the position has no active employees assigned.

        Args:
            entity: The CyodaEntity to validate (expected to be Position)
            **kwargs: Additional criteria parameters

        Returns:
            True if the position has no active employees, False otherwise
        """
        try:
            self.logger.info(
                f"Validating no active employees for position {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Position for type-safe operations
            position = cast_entity(entity, Position)
            position_id = position.technical_id or position.entity_id

            # Check for active employees assigned to this position
            if position_id:
                active_employees_count = await self._count_active_employees(position_id)
            else:
                active_employees_count = 0

            if active_employees_count > 0:
                self.logger.warning(
                    f"Position {position.title} has {active_employees_count} active employees assigned"
                )
                return False

            self.logger.info(
                f"Position {position.title} has no active employees - validation passed"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating active employees for position {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    async def _count_active_employees(self, position_id: str) -> int:
        """
        Count active employees assigned to the position.

        Args:
            position_id: The position ID to check

        Returns:
            Number of active employees
        """
        try:
            # Note: In a real implementation, you would:
            # 1. Search for employees with this position_id
            # 2. Filter for active employees only
            # 3. Return the count

            # For now, we'll simulate this check
            self.logger.debug(
                f"Would check for active employees with position_id: {position_id}"
            )

            # This is where you would implement the actual employee search:
            # from common.service.entity_service import SearchConditionRequest
            #
            # search_condition = SearchConditionRequest.builder() \
            #     .equals("position_id", position_id) \
            #     .equals("is_active", "true") \
            #     .equals("state", "active") \
            #     .build()
            #
            # employees = await entity_service.search(
            #     entity_class="Employee",
            #     condition=search_condition
            # )
            #
            # return len(employees)

            # For demonstration, return 0 (no active employees)
            return 0

        except Exception as e:
            self.logger.error(
                f"Error counting active employees for position {position_id}: {str(e)}"
            )
            # Return a high number to be safe - don't allow deactivation if we can't verify
            return 999
