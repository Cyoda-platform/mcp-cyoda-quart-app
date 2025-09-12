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

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from example_application.entity.example_entity import ExampleEntity
from example_application.entity.other_entity import (  # noqa: F401  # Imported for clarity; referenced by name in service calls
    OtherEntity,
)
from services.services import get_entity_service


class ExampleEntityProcessor(CyodaProcessor):
    """
    Processor for ExampleEntity that handles main business logic,
    enriches entity data, and creates/updates related OtherEntity instances.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ExampleEntityProcessor",
            description="Processes ExampleEntity instances, enriches data and creates related OtherEntity instances",
        )
        # Ensure logger attribute is present for type-checkers/readers.
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the ExampleEntity according to functional requirements.

        Args:
            entity: The ExampleEntity to process (must be in 'validated' state)
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with enriched data
        """
        try:
            self.logger.info(
                f"Processing ExampleEntity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to ExampleEntity for type-safe operations
            example_entity = cast_entity(entity, ExampleEntity)

            # Enrich entity with processed data
            processed_data = self._create_processed_data(example_entity)
            example_entity.processed_data = processed_data

            # Create or update related OtherEntity instances
            await self._create_related_other_entities(example_entity)

            # Log processing completion
            self.logger.info(f"ExampleEntity {example_entity.technical_id} processed successfully")

            return example_entity

        except Exception as e:
            self.logger.error(
                f"Error processing entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _create_processed_data(self, entity: ExampleEntity) -> Dict[str, Any]:
        """
        Create processed data according to functional requirements.

        Args:
            entity: The ExampleEntity to process

        Returns:
            Dictionary containing processed data
        """
        current_timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        processing_id = str(uuid.uuid4())

        # Create processed data without numeric calculations
        processed_data: Dict[str, Any] = {
            "processed_at": current_timestamp,
            "enriched_category": entity.category.upper() + "_PROCESSED",
            "processing_id": processing_id,
            "processing_status": "COMPLETED",
        }

        return processed_data

    async def _create_related_other_entities(self, entity: ExampleEntity) -> None:
        """
        Create related OtherEntity instances according to functional requirements.

        Args:
            entity: The processed ExampleEntity
        """
        entity_service = get_entity_service()

        # Note: processing_id is available in processed_data but not needed for simplified OtherEntity creation

        # Create 3 related OtherEntity instances as specified
        for i in range(1, 4):
            try:
                # Determine priority based on business rules
                priority = self._determine_priority(entity.category, i)

                # Create OtherEntity using direct Pydantic model construction
                other_entity = OtherEntity(
                    title=f"{entity.name}_Related_{i}",
                    content=f"Generated from {entity.name} processing",
                    priority=priority,
                    sourceEntityId=entity.technical_id or entity.entity_id or "unknown",
                    lastUpdatedBy="ExampleEntityProcessor",
                )

                # Convert Pydantic model to dict for EntityService.save()
                other_entity_data = other_entity.model_dump(by_alias=True)

                # Save the new OtherEntity using entity constants
                response = await entity_service.save(
                    entity=other_entity_data,
                    entity_class=OtherEntity.ENTITY_NAME,
                    entity_version=str(OtherEntity.ENTITY_VERSION),
                )

                # Get the technical ID of the created entity
                created_entity_id = response.metadata.id

                self.logger.info(
                    f"Created OtherEntity {created_entity_id} (index {i}) - workflow will handle state transitions automatically"
                )

            except Exception as e:
                self.logger.error(
                    f"Failed to create OtherEntity {i} for ExampleEntity {entity.technical_id}: {str(e)}"
                )
                # Continue with other entities even if one fails
                continue

    def _determine_priority(self, category: str, index: int) -> str:
        """
        Determine priority based on business rules from functional requirements.

        Args:
            category: The category from ExampleEntity
            index: The index of the OtherEntity being created (1-3)

        Returns:
            Priority level: HIGH, MEDIUM, or LOW
        """
        if category == "ELECTRONICS" and index == 1:
            return "HIGH"
        elif category in ["ELECTRONICS", "CLOTHING"]:
            return "MEDIUM"
        else:
            return "LOW"
