"""
ProcessCollectionProcessor for Cyoda Client Application

Processes all items in an HNItemCollection as specified in workflow requirements.
"""

import logging
from typing import Any, Dict

from application.entity.hnitem.version_1.hnitem import HNItem
from application.entity.hnitemcollection.version_1.hnitemcollection import (
    HNItemCollection,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class ProcessCollectionProcessor(CyodaProcessor):
    """
    Processor for processing all items in an HNItemCollection.

    Validates, creates, and indexes individual HN items from the collection.
    """

    def __init__(self) -> None:
        super().__init__(
            name="process_collection",
            description="Processes all items in the collection",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process all items in the HNItemCollection according to functional requirements.

        Args:
            entity: The HNItemCollection to process
            **kwargs: Additional processing parameters

        Returns:
            The updated collection with processing results
        """
        try:
            self.logger.info(
                f"Processing HNItemCollection {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to HNItemCollection for type-safe operations
            collection = cast_entity(entity, HNItemCollection)

            # Start processing
            collection.start_processing()

            # Get entity service for creating HNItems
            entity_service = get_entity_service()

            # Process each item in the collection
            if collection.items:
                for item_data in collection.items:
                    try:
                        # Create HNItem from data
                        hn_item = await self._create_hn_item(item_data, entity_service)

                        if hn_item:
                            collection.increment_processed()
                            self.logger.info(
                                f"Successfully processed HN item {item_data.get('id', 'unknown')}"
                            )
                        else:
                            collection.increment_failed(
                                {
                                    "item_id": item_data.get("id", "unknown"),
                                    "error": "Failed to create HN item",
                                    "item_data": item_data,
                                }
                            )

                    except Exception as item_error:
                        self.logger.error(
                            f"Error processing item {item_data.get('id', 'unknown')}: {str(item_error)}"
                        )
                        collection.increment_failed(
                            {
                                "item_id": item_data.get("id", "unknown"),
                                "error": str(item_error),
                                "item_data": item_data,
                            }
                        )

            # Complete processing
            collection.complete_processing()

            # Update metadata with processing summary
            if not collection.metadata:
                collection.metadata = {}
            collection.metadata["processing_completed"] = True
            collection.metadata["processing_summary"] = (
                collection.get_processing_summary()
            )

            self.logger.info(
                f"HNItemCollection {collection.technical_id} processing completed. "
                f"Processed: {collection.processed_items}, Failed: {collection.failed_items}"
            )

            return collection

        except Exception as e:
            self.logger.error(
                f"Error processing HNItemCollection {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _create_hn_item(
        self, item_data: Dict[str, Any], entity_service: Any
    ) -> bool:
        """
        Create an HNItem from item data.

        Args:
            item_data: Dictionary containing HN item data
            entity_service: Entity service for saving items

        Returns:
            True if item was created successfully, False otherwise
        """
        try:
            # Validate required fields
            if "id" not in item_data:
                self.logger.warning("Item data missing required 'id' field")
                return False

            if "type" not in item_data:
                self.logger.warning(
                    f"Item {item_data['id']} missing required 'type' field"
                )
                return False

            # Create HNItem instance
            hn_item = HNItem(**item_data)

            # Convert to dict for entity service
            hn_item_data = hn_item.model_dump(by_alias=True)

            # Save the HNItem
            response = await entity_service.save(
                entity=hn_item_data,
                entity_class=HNItem.ENTITY_NAME,
                entity_version=str(HNItem.ENTITY_VERSION),
            )

            if response and response.metadata:
                self.logger.info(f"Created HNItem with ID: {response.metadata.id}")
                return True
            else:
                self.logger.warning(
                    f"Failed to create HNItem for item {item_data['id']}"
                )
                return False

        except Exception as e:
            self.logger.error(f"Error creating HNItem from data {item_data}: {str(e)}")
            return False
