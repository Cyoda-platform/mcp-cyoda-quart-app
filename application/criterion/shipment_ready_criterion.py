"""
ShipmentReadyCriterion for Cyoda OMS Application

Validates that a Shipment is ready to be sent (all items picked)
as specified in functional requirements.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.shipment.version_1.shipment import Shipment


class ShipmentReadyCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Shipment that checks if all items are picked
    and the shipment is ready to be sent.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ShipmentReadyCriterion",
            description="Validates that Shipment is ready to be sent (all items picked)",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the shipment is ready to be sent.

        Args:
            entity: The CyodaEntity to validate (expected to be Shipment)
            **kwargs: Additional criteria parameters

        Returns:
            True if the shipment is ready to be sent, False otherwise
        """
        try:
            self.logger.info(
                f"Validating shipment readiness {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Shipment for type-safe operations
            shipment = cast_entity(entity, Shipment)

            # Check if all items are fully picked
            if not shipment.is_fully_picked():
                self.logger.warning(
                    f"Shipment {shipment.technical_id} is not fully picked"
                )
                return False

            # Validate that there are line items
            if not shipment.lines:
                self.logger.warning(
                    f"Shipment {shipment.technical_id} has no line items"
                )
                return False

            self.logger.info(
                f"Shipment {shipment.technical_id} is ready to be sent"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating shipment readiness {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
