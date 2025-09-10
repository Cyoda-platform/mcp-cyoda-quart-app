"""
ExampleEntityProcessor for Cyoda Client Application

Handles the main business logic for processing ExampleEntity instances.
It enriches the entity data, performs calculations, and updates related
OtherEntity instances as specified in functional requirements.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from common.processor.base import CyodaProcessor
from entity.example_entity import ExampleEntity
from entity.other_entity import OtherEntity
from service.services import get_entity_service


class ExampleEntityProcessor(CyodaProcessor):
    """
    Processor for ExampleEntity that handles main business logic,
    enriches entity data, and creates/updates related OtherEntity instances.
    """

    def __init__(self):
        super().__init__(
            name="ExampleEntityProcessor",
            description="Processes ExampleEntity instances, enriches data and creates related OtherEntity instances",
        )
        self.entity_service = None

    def _get_entity_service(self):
        """Get entity service lazily"""
        if self.entity_service is None:
            self.entity_service = get_entity_service()
        return self.entity_service

    async def process(self, entity: ExampleEntity, **kwargs) -> ExampleEntity:
        """
        Process the ExampleEntity according to functional requirements.

        Args:
            entity: The ExampleEntity to process (must be in 'validated' state)
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with enriched data
        """
        try:
            self.logger.info(f"Processing ExampleEntity {entity.technical_id}")

            # Enrich entity with processed data
            processed_data = self._create_processed_data(entity)
            entity.processed_data = processed_data

            # Create or update related OtherEntity instances
            await self._create_related_other_entities(entity)

            # Log processing completion
            self.logger.info(f"ExampleEntity {entity.technical_id} processed successfully")

            return entity

        except Exception as e:
            self.logger.error(f"Error processing entity {entity.technical_id}: {str(e)}")
            raise

    def _create_processed_data(self, entity: ExampleEntity) -> Dict[str, Any]:
        """
        Create processed data according to functional requirements.

        Args:
            entity: The ExampleEntity to process

        Returns:
            Dictionary containing processed data
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        processing_id = str(uuid.uuid4())

        processed_data = {
            "processed_at": current_timestamp,
            "calculated_value": entity.value * 2.5,
            "enriched_category": entity.category.upper() + "_PROCESSED",
            "processing_id": processing_id,
        }

        return processed_data

    async def _create_related_other_entities(self, entity: ExampleEntity) -> None:
        """
        Create related OtherEntity instances according to functional requirements.

        Args:
            entity: The processed ExampleEntity
        """
        entity_service = self._get_entity_service()
        processing_id = entity.processed_data.get("processing_id") if hasattr(entity, 'processed_data') else str(uuid.uuid4())

        # Create 3 related OtherEntity instances as specified
        for i in range(1, 4):
            try:
                # Determine priority based on business rules
                priority = self._determine_priority(entity.value, i)

                # Create OtherEntity data
                other_entity_data = {
                    "title": f"{entity.name}_Related_{i}",
                    "content": f"Generated from {entity.name} processing",
                    "priority": priority,
                    "sourceEntityId": entity.technical_id,
                    "lastUpdatedBy": "ExampleEntityProcessor",
                    "createdAt": datetime.now(timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z"),
                    "updatedAt": datetime.now(timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z"),
                    "metadata": {
                        "sourceProcessingId": processing_id,
                        "generatedIndex": i,
                        "sourceCategory": entity.category,
                    },
                }

                # Save the new OtherEntity
                response = await entity_service.save(
                    entity=other_entity_data,
                    entity_class="OtherEntity",
                    entity_version="1",
                )

                # Get the technical ID of the created entity
                created_entity_id = response.metadata.id

                # Transition the OtherEntity to active state using manual transition
                await entity_service.execute_transition(
                    entity_id=created_entity_id,
                    transition="transition_to_active",
                    entity_class="OtherEntity",
                    entity_version="1",
                )

                self.logger.info(
                    f"Created and activated OtherEntity {created_entity_id} (index {i})"
                )

            except Exception as e:
                self.logger.error(
                    f"Failed to create OtherEntity {i} for ExampleEntity {entity.technical_id}: {str(e)}"
                )
                # Continue with other entities even if one fails
                continue

    def _determine_priority(self, value: float, index: int) -> str:
        """
        Determine priority based on business rules from functional requirements.

        Args:
            value: The value from ExampleEntity
            index: The index of the OtherEntity being created (1-3)

        Returns:
            Priority level: HIGH, MEDIUM, or LOW
        """
        if value > 100 and index == 1:
            return "HIGH"
        elif value > 50:
            return "MEDIUM"
        else:
            return "LOW"
