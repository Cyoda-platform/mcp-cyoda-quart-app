"""
TaskValidationCriterion for Cyoda Client Application

Validates that a Task meets all required business rules before it can
proceed to the processing stage.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.task.version_1.task import Task


class TaskValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Task that checks all business rules
    before the entity can proceed to processing stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="TaskValidationCriterion",
            description="Validates Task business rules and data consistency",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the entity meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be Task)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Task for type-safe operations
            task = cast_entity(entity, Task)

            # Validate required fields
            if (
                not task.title
                or len(task.title.strip()) < 3
                or len(task.title) > 200
            ):
                self.logger.warning(
                    f"Entity {task.technical_id} has invalid title: '{task.title}'"
                )
                return False

            if not task.description or len(task.description) > 1000:
                self.logger.warning(
                    f"Entity {task.technical_id} has invalid description"
                )
                return False

            # Validate priority
            allowed_priorities = ["LOW", "MEDIUM", "HIGH", "URGENT"]
            if task.priority not in allowed_priorities:
                self.logger.warning(
                    f"Entity {task.technical_id} has invalid priority: {task.priority}"
                )
                return False

            # Validate business logic rules
            if task.priority == "URGENT" and not task.assignee:
                self.logger.warning(
                    f"Entity {task.technical_id} URGENT priority tasks must have an assignee"
                )
                return False

            # Validate due date format if provided
            if task.due_date:
                try:
                    # Basic ISO format validation - just check if it can be parsed
                    from datetime import datetime
                    datetime.fromisoformat(task.due_date.replace('Z', '+00:00'))
                except ValueError:
                    self.logger.warning(
                        f"Entity {task.technical_id} has invalid due_date format: {task.due_date}"
                    )
                    return False

            self.logger.info(
                f"Entity {task.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
