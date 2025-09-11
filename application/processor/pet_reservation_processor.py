"""
PetReservationProcessor for Purrfect Pets API

Reserves pet for customer or order according to processors.md specification.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class PetReservationProcessor(CyodaProcessor):
    """
    Processor for Pet reservation that handles pet reservation for customers or orders.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetReservationProcessor",
            description="Reserves pet for customer or order",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity reservation according to functional requirements.

        Args:
            entity: The Pet entity to reserve
            **kwargs: Additional processing parameters including reservation_data

        Returns:
            The reserved pet entity
        """
        try:
            self.logger.info(
                f"Reserving Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Validate pet is in AVAILABLE state
            if pet.state != "available":
                raise ValueError(
                    f"Pet must be in AVAILABLE state to reserve, current state: {pet.state}"
                )

            # Get reservation data from kwargs
            reservation_data = kwargs.get("reservation_data", {})

            # Create reservation record
            current_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            if reservation_data.get("order_id"):
                # Create reservation record with order ID
                reservation_info = {
                    "type": "order_reservation",
                    "order_id": reservation_data["order_id"],
                    "reserved_at": current_timestamp,
                    "reserved_by": "system",
                }
                self.logger.info(
                    f"Created order reservation for pet {pet.technical_id} with order {reservation_data['order_id']}"
                )
            else:
                # Create customer reservation with customer ID
                customer_id = reservation_data.get("customer_id", "unknown")
                reservation_info = {
                    "type": "customer_reservation",
                    "customer_id": customer_id,
                    "reserved_at": current_timestamp,
                    "expires_at": self._calculate_expiry_time(current_timestamp),
                    "reserved_by": customer_id,
                }
                self.logger.info(
                    f"Created customer reservation for pet {pet.technical_id} with customer {customer_id}"
                )

            # Add reservation info to pet metadata
            if pet.metadata is None:
                pet.metadata = {}
            pet.metadata["reservation"] = reservation_info

            # Log reservation activity
            activity_log = {
                "action": "reservation_created",
                "timestamp": current_timestamp,
                "details": reservation_info,
            }

            if "activity_log" not in pet.metadata:
                pet.metadata["activity_log"] = []
            pet.metadata["activity_log"].append(activity_log)

            # Update timestamp
            pet.update_timestamp()

            self.logger.info(f"Pet {pet.technical_id} reserved successfully")

            return pet

        except Exception as e:
            self.logger.error(
                f"Error reserving pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _calculate_expiry_time(self, current_time: str) -> str:
        """Calculate reservation expiry time (24 hours from now)"""
        current_dt = datetime.fromisoformat(current_time.replace("Z", "+00:00"))
        expiry_dt = current_dt.replace(hour=current_dt.hour + 24)
        return expiry_dt.isoformat().replace("+00:00", "Z")
