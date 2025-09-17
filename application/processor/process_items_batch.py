"""
ProcessItemsBatch Processor for HNItemCollection

Processes items in batches, creating individual HNItem entities
and tracking processing progress.
"""

import logging
from typing import Any, Dict, List

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.hnitemcollection.version_1.hnitemcollection import (
    HNItemCollection,
)
from application.entity.hnitem.version_1.hnitem import HNItem
from services.services import get_entity_service


class ProcessItemsBatch(CyodaProcessor):
    """
    Processor for batch processing HNItemCollection items.
    Creates individual HNItem entities and tracks processing progress.
    """

    def __init__(self) -> None:
        super().__init__(
            name="process_items_batch",
            description="Processes HNItemCollection items in batches",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the HNItemCollection items in batches.

        Args:
            entity: The HNItemCollection to process
            **kwargs: Additional processing parameters

        Returns:
            The collection with updated processing status
        """
        try:
            self.logger.info(
                f"Processing HNItemCollection batch {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HNItemCollection for type-safe operations
            collection = cast_entity(entity, HNItemCollection)

            # Start processing
            collection.start_processing()

            # Process items based on collection type
            if collection.collection_type == "array":
                await self._process_array_items(collection)
            elif collection.collection_type == "file_upload":
                await self._process_file_upload_items(collection)
            elif collection.collection_type == "firebase_pull":
                await self._process_firebase_pull_items(collection)

            self.logger.info(
                f"HNItemCollection {collection.technical_id} batch processing completed. "
                f"Processed: {collection.processed_items}, Failed: {collection.failed_items}"
            )

            return collection

        except Exception as e:
            self.logger.error(
                f"Error processing HNItemCollection batch {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Add processing error
            if hasattr(entity, "add_processing_error"):
                entity.add_processing_error(
                    {
                        "type": "batch_processing_error",
                        "message": f"Batch processing error: {str(e)}",
                        "timestamp": (
                            entity.processing_started_at
                            if hasattr(entity, "processing_started_at")
                            else None
                        ),
                    }
                )
            raise

    async def _process_array_items(self, collection: HNItemCollection) -> None:
        """Process items from array collection."""
        if not collection.items:
            return

        entity_service = get_entity_service()
        batch_size = collection.batch_size or 100

        for i in range(0, len(collection.items), batch_size):
            batch = collection.items[i : i + batch_size]
            await self._process_batch(batch, collection, entity_service)

    async def _process_file_upload_items(self, collection: HNItemCollection) -> None:
        """Process items from file upload collection."""
        # For file uploads, items should already be parsed into collection.items
        # during the validation phase or earlier
        if collection.items:
            await self._process_array_items(collection)
        else:
            collection.add_processing_error(
                {
                    "type": "file_processing_error",
                    "message": "No items found in file upload collection",
                    "timestamp": collection.processing_started_at,
                }
            )

    async def _process_firebase_pull_items(self, collection: HNItemCollection) -> None:
        """Process items from Firebase pull collection."""
        # In a real implementation, this would pull data from Firebase API
        # For now, we'll simulate processing if items are already present
        if collection.items:
            await self._process_array_items(collection)
        else:
            # Simulate Firebase API call
            self.logger.info(
                f"Would pull data from Firebase endpoint: {collection.firebase_endpoint}"
            )
            collection.add_processing_error(
                {
                    "type": "firebase_pull_error",
                    "message": "Firebase pull not implemented in this simulation",
                    "timestamp": collection.processing_started_at,
                }
            )

    async def _process_batch(
        self,
        batch: List[Dict[str, Any]],
        collection: HNItemCollection,
        entity_service: Any,
    ) -> None:
        """Process a single batch of items."""
        for item_data in batch:
            try:
                # Create HNItem entity from the data
                hn_item = HNItem(**item_data)

                # Convert to dict for EntityService.save()
                hn_item_data = hn_item.model_dump(by_alias=True, exclude_none=True)

                # Save the HNItem entity
                response = await entity_service.save(
                    entity=hn_item_data,
                    entity_class=HNItem.ENTITY_NAME,
                    entity_version=str(HNItem.ENTITY_VERSION),
                )

                # Increment processed count
                collection.increment_processed()

                self.logger.debug(
                    f"Created HNItem {response.metadata.id} from collection item {item_data.get('id', 'unknown')}"
                )

            except Exception as e:
                # Add error and increment failed count
                collection.add_processing_error(
                    {
                        "type": "item_processing_error",
                        "message": f"Failed to process item {item_data.get('id', 'unknown')}: {str(e)}",
                        "item_data": item_data,
                        "timestamp": collection.processing_started_at,
                    }
                )

                self.logger.warning(
                    f"Failed to process item {item_data.get('id', 'unknown')}: {str(e)}"
                )
