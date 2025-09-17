"""
StoreHnItemProcessor for Cyoda Client Application

Stores validated HN items in the database and manages relationships.
"""

import logging
from typing import Any

from application.entity.hnitem.version_1.hnitem import HnItem
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class StoreHnItemProcessor(CyodaProcessor):
    """
    Processor for storing validated HN items in the database.
    """

    def __init__(self) -> None:
        super().__init__(
            name="store_hn_item_processor",
            description="Stores validated HN items in the database and manages relationships",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Store the validated HN item in the database.

        Args:
            entity: The validated HnItem
            **kwargs: Additional processing parameters

        Returns:
            The entity with storage information
        """
        try:
            self.logger.info(
                f"Storing HnItem {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HnItem for type-safe operations
            hn_item = cast_entity(entity, HnItem)

            # Attempt to store the item
            try:
                # Check if item already exists
                existing_item = await self._find_existing_item(hn_item)

                if existing_item:
                    # Update existing item
                    await self._update_existing_item(hn_item, existing_item)
                    hn_item.set_storage_result("success", "updated")
                    self.logger.info(f"Updated existing HnItem {hn_item.id}")
                else:
                    # Create new item - the item is already being stored by the workflow
                    hn_item.set_storage_result("success", "created")
                    self.logger.info(f"Created new HnItem {hn_item.id}")

                # Update relationships (this is informational, actual relationships are managed by Cyoda)
                await self._update_relationships(hn_item)

            except Exception as e:
                # Handle storage failure
                error_msg = str(e)
                hn_item.set_storage_result("failed", error=error_msg)
                self.logger.error(f"Failed to store HnItem {hn_item.id}: {error_msg}")

            return hn_item

        except Exception as e:
            self.logger.error(
                f"Error storing HnItem {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _find_existing_item(self, item: HnItem) -> Any:
        """Find existing item by HN ID"""
        try:
            entity_service = get_entity_service()
            from common.service.entity_service import SearchConditionRequest

            builder = SearchConditionRequest.builder()
            builder.equals("id", str(item.id))
            condition = builder.build()

            results = await entity_service.search(
                entity_class=HnItem.ENTITY_NAME,
                condition=condition,
                entity_version=str(HnItem.ENTITY_VERSION),
            )

            return results[0] if results else None

        except Exception as e:
            self.logger.warning(f"Error finding existing item {item.id}: {str(e)}")
            return None

    async def _update_existing_item(self, new_item: HnItem, existing_item: Any) -> None:
        """Update existing item with new data"""
        try:
            entity_service = get_entity_service()

            # Get the technical ID of the existing item
            existing_id = existing_item.metadata.id

            # Convert new item to dict for update
            update_data = new_item.model_dump(by_alias=True)

            # Update the existing item
            await entity_service.update(
                entity_id=existing_id,
                entity=update_data,
                entity_class=HnItem.ENTITY_NAME,
                entity_version=str(HnItem.ENTITY_VERSION),
            )

            self.logger.info(
                f"Updated existing item {existing_id} with HN ID {new_item.id}"
            )

        except Exception as e:
            self.logger.error(f"Error updating existing item {new_item.id}: {str(e)}")
            raise

    async def _update_relationships(self, item: HnItem) -> None:
        """Update parent-child and other relationships (informational)"""
        try:
            # Log relationship information for monitoring
            if item.parent:
                self.logger.info(f"Item {item.id} has parent {item.parent}")

            if item.kids:
                self.logger.info(
                    f"Item {item.id} has {len(item.kids)} children: {item.kids}"
                )

            if item.poll:
                self.logger.info(f"Poll option {item.id} belongs to poll {item.poll}")

            if item.parts:
                self.logger.info(
                    f"Poll {item.id} has {len(item.parts)} options: {item.parts}"
                )

        except Exception as e:
            self.logger.warning(
                f"Error updating relationships for item {item.id}: {str(e)}"
            )
            # Don't fail the storage for relationship update errors
