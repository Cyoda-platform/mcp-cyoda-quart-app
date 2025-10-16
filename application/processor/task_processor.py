"""
TaskProcessor for Cyoda Client Application

Handles the main business logic for processing Task instances.
It enriches the task data and performs task-specific operations.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from application.entity.task.version_1.task import Task
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class TaskProcessor(CyodaProcessor):
    """
    Processor for Task that handles main business logic and enriches task data.
    """

    def __init__(self) -> None:
        super().__init__(
            name="TaskProcessor",
            description="Processes Task instances and enriches data",
        )
        # Ensure logger attribute is present for type-checkers/readers.
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Task according to business requirements.

        Args:
            entity: The Task to process (must be in 'validated' state)
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with enriched data
        """
        try:
            self.logger.info(
                f"Processing Task {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Task for type-safe operations
            task = cast_entity(entity, Task)

            # Enrich task with processed data
            processed_data = self._create_processed_data(task)
            task.processed_data = processed_data

            # Update task timestamp
            task.update_timestamp()

            # Log processing completion
            self.logger.info(f"Task {task.technical_id} processed successfully")

            return task

        except Exception as e:
            self.logger.error(
                f"Error processing entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _create_processed_data(self, task: Task) -> Dict[str, Any]:
        """
        Create processed data for the task.

        Args:
            task: The Task to process

        Returns:
            Dictionary containing processed data
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        processing_id = str(uuid.uuid4())

        # Create processed data based on task properties
        processed_data: Dict[str, Any] = {
            "processed_at": current_timestamp,
            "processing_id": processing_id,
            "processing_status": "COMPLETED",
            "priority_level": self._calculate_priority_level(task.priority),
            "estimated_effort": self._estimate_effort(task.priority, task.description),
        }

        # Add assignee-specific processing if assignee exists
        if task.assignee:
            processed_data["assignee_notified"] = True
            processed_data["notification_sent_at"] = current_timestamp

        return processed_data

    def _calculate_priority_level(self, priority: str) -> int:
        """
        Calculate numeric priority level based on priority string.

        Args:
            priority: Priority string (LOW, MEDIUM, HIGH, URGENT)

        Returns:
            Numeric priority level (1-4)
        """
        priority_mapping = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "URGENT": 4}
        return priority_mapping.get(priority, 2)

    def _estimate_effort(self, priority: str, description: str) -> str:
        """
        Estimate effort required based on priority and description length.

        Args:
            priority: Task priority
            description: Task description

        Returns:
            Effort estimate string
        """
        base_effort = {
            "LOW": "1-2 hours",
            "MEDIUM": "2-4 hours",
            "HIGH": "4-8 hours",
            "URGENT": "1-2 hours",  # Urgent tasks are typically quick fixes
        }

        # Adjust based on description length
        if len(description) > 500:
            return f"{base_effort.get(priority, '2-4 hours')} (complex)"
        elif len(description) < 100:
            return f"{base_effort.get(priority, '2-4 hours')} (simple)"
        else:
            return base_effort.get(priority, "2-4 hours")
