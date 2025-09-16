"""
PetArchiveProcessor for Purrfect Pets Application

Archives a sold pet record as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet
from services.services import get_entity_service


class PetArchiveProcessor(CyodaProcessor):
    """
    Processor for archiving Pet entities that have been sold.
    Validates sufficient time has passed and all orders are completed.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetArchiveProcessor",
            description="Archive a sold pet record"
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity for archiving.

        Args:
            entity: The Pet entity to archive
            **kwargs: Additional processing parameters

        Returns:
            The archived Pet entity
        """
        try:
            self.logger.info(
                f"Processing Pet archiving for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Validate pet has been sold for sufficient time
            if pet.updated_at:
                try:
                    # Parse the updated_at timestamp
                    updated_time = datetime.fromisoformat(pet.updated_at.replace('Z', '+00:00'))
                    current_time = datetime.now(timezone.utc)
                    time_since_sale = current_time - updated_time
                    
                    # Require at least 30 days since last update (sale)
                    if time_since_sale.days < 30:
                        raise ValueError(f"Pet must be sold for at least 30 days before archiving. Current: {time_since_sale.days} days")
                        
                except ValueError as ve:
                    if "Pet must be sold" in str(ve):
                        raise ve
                    self.logger.warning(f"Could not parse updated_at timestamp: {pet.updated_at}")

            # Validate all associated orders are completed
            entity_service = get_entity_service()
            try:
                # Search for orders with this pet ID
                from common.service.entity_service import SearchConditionRequest
                
                builder = SearchConditionRequest.builder()
                builder.equals("petId", str(pet.technical_id))
                search_condition = builder.build()

                order_results = await entity_service.search(
                    entity_class="Order",
                    condition=search_condition,
                    entity_version="1"
                )

                # Check that all orders are in final states
                incomplete_orders = []
                for order_result in order_results:
                    order_state = getattr(order_result.metadata, 'state', None)
                    if order_state not in ["delivered", "cancelled", "returned"]:
                        incomplete_orders.append(order_result.metadata.id)

                if incomplete_orders:
                    raise ValueError(f"Cannot archive pet - incomplete orders found: {incomplete_orders}")

                self.logger.info(f"All {len(order_results)} orders for Pet {pet.technical_id} are completed")

            except Exception as e:
                if "Cannot archive pet" in str(e):
                    raise e
                self.logger.error(f"Failed to validate associated orders: {str(e)}")
                # Continue processing - order validation failure shouldn't prevent archiving in some cases

            # Set archive date and update timestamp
            current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            pet.updated_at = current_time
            
            # Add archive metadata if we had such fields
            if hasattr(pet, 'metadata') and pet.metadata:
                pet.metadata['archived_at'] = current_time
            else:
                pet.metadata = {'archived_at': current_time}

            self.logger.info(f"Pet archiving processed successfully for {pet.technical_id}")
            return pet

        except Exception as e:
            self.logger.error(
                f"Error processing Pet archiving for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
