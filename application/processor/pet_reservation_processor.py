"""
PetReservationProcessor for Purrfect Pets API

Reserves a pet for a potential customer.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.pet.version_1.pet import Pet


class PetReservationProcessor(CyodaProcessor):
    """
    Processor for Pet reservation that reserves a pet for a potential customer.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetReservationProcessor",
            description="Reserves a pet for a potential customer",
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet reservation according to functional requirements.

        Args:
            entity: The Pet entity to reserve
            **kwargs: Additional processing parameters (should contain customerInfo)

        Returns:
            The pet entity with reservation details
        """
        try:
            self.logger.info(
                f"Reserving Pet {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Get customer information from kwargs
            customer_info = kwargs.get("customerInfo", {})
            
            # Validate customer information is complete
            if not self._validate_customer_info(customer_info):
                raise ValueError("Customer information is incomplete")

            # Create reservation record with expiration time (24 hours)
            current_time = datetime.now(timezone.utc)
            expiry_time = current_time + timedelta(hours=24)

            # Set reservation details
            pet.reservedBy = customer_info.get("customerId", customer_info.get("customerEmail"))
            pet.reservationExpiry = expiry_time.isoformat().replace("+00:00", "Z")

            # Update timestamp
            pet.update_timestamp()

            # Log reservation (in real system, would send email)
            self.logger.info(
                f"Pet {pet.technical_id} reserved by {pet.reservedBy} until {pet.reservationExpiry}"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error reserving pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_customer_info(self, customer_info: dict) -> bool:
        """
        Validate that customer information is complete.

        Args:
            customer_info: Customer information dictionary

        Returns:
            True if customer info is valid, False otherwise
        """
        required_fields = ["customerName", "customerEmail", "customerPhone"]
        
        for field in required_fields:
            if not customer_info.get(field):
                self.logger.warning(f"Missing required customer field: {field}")
                return False
        
        # Basic email validation
        email = customer_info.get("customerEmail", "")
        if "@" not in email:
            self.logger.warning(f"Invalid email format: {email}")
            return False
        
        return True
