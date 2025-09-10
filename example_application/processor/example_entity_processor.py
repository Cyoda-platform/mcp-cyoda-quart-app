"""
ExampleEntityProcessor for Cyoda Client Application

Handles the main business logic for processing ExampleEntity instances.
It enriches the entity data, performs calculations, and updates related
OtherEntity instances as specified in functional requirements.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Protocol, cast, runtime_checkable

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from example_application.entity.example_entity import ExampleEntity
from example_application.entity.other_entity import (  # noqa: F401  # Imported for clarity; referenced by name in service calls
    OtherEntity,
)
from services.services import get_entity_service


@runtime_checkable
class _HasId(Protocol):
    id: str


@runtime_checkable
class _HasMetadata(Protocol):
    metadata: _HasId


class _EntityService(Protocol):
    async def save(
        self, *, entity: Dict[str, Any], entity_class: str, entity_version: str
    ) -> _HasMetadata: ...

    async def execute_transition(
        self, *, entity_id: str, transition: str, entity_class: str, entity_version: str
    ) -> None: ...


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
        self.entity_service: Optional[_EntityService] = None
        # Ensure logger attribute is present for type-checkers/readers.
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    def _get_entity_service(self) -> _EntityService:
        """Get entity service lazily"""
        if self.entity_service is None:
            self.entity_service = cast(_EntityService, get_entity_service())
        return self.entity_service

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
            self.logger.info(
                f"ExampleEntity {example_entity.technical_id} processed successfully"
            )

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
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        processing_id = str(uuid.uuid4())

        processed_data: Dict[str, Any] = {
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

        # Safely extract processing_id from processed_data (might be Optional in the entity model)
        processing_id: str
        pd = getattr(entity, "processed_data", None)
        if isinstance(pd, dict):
            pid = pd.get("processing_id")
            processing_id = str(pid) if pid is not None else str(uuid.uuid4())
        else:
            processing_id = str(uuid.uuid4())

        # Create 3 related OtherEntity instances as specified
        for i in range(1, 4):
            try:
                # Determine priority based on business rules
                priority = self._determine_priority(entity.value, i)

                now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

                # Create OtherEntity data
                other_entity_data: Dict[str, Any] = {
                    "title": f"{entity.name}_Related_{i}",
                    "content": f"Generated from {entity.name} processing",
                    "priority": priority,
                    "sourceEntityId": entity.technical_id,
                    "lastUpdatedBy": "ExampleEntityProcessor",
                    "createdAt": now_iso,
                    "updatedAt": now_iso,
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

                self.logger.info(
                    f"Created OtherEntity {created_entity_id} (index {i}) - workflow will handle state transitions automatically"
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
