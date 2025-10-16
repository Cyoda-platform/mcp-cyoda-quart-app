"""
ShipmentTrackingProcessor for Cyoda OMS Application

Handles shipment tracking and status updates
as specified in functional requirements.
"""

import logging
import uuid
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.shipment.version_1.shipment import Shipment


class ShipmentTrackingProcessor(CyodaProcessor):
    """
    Processor for Shipment that handles tracking number generation and status updates.
    Generates tracking numbers and updates shipment status when sent.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ShipmentTrackingProcessor",
            description="Processes Shipment tracking and status updates",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Shipment tracking update.

        Args:
            entity: The Shipment entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed shipment with tracking information
        """
        try:
            self.logger.info(
                f"Processing Shipment tracking {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Shipment for type-safe operations
            shipment = cast_entity(entity, Shipment)

            # Generate tracking number if not already set
            if not shipment.trackingNumber:
                tracking_number = self._generate_tracking_number()
                carrier = "DEMO_CARRIER"
                
                shipment.mark_shipped(tracking_number=tracking_number, carrier=carrier)
                
                self.logger.info(
                    f"Shipment {shipment.shipmentId} marked as shipped with tracking {tracking_number}"
                )
            else:
                # Just update timestamp if tracking already exists
                shipment.update_timestamp()
                
                self.logger.info(
                    f"Shipment {shipment.shipmentId} tracking updated"
                )

            return shipment

        except Exception as e:
            self.logger.error(
                f"Error processing shipment tracking for {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _generate_tracking_number(self) -> str:
        """Generate a demo tracking number"""
        # Generate a simple tracking number for demo purposes
        return f"TRK-{str(uuid.uuid4())[:8].upper()}"
