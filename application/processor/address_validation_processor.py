"""
AddressValidationProcessor for Purrfect Pets API

Validates address information according to processors.md specification.
"""

import logging
import re
from typing import Any

from application.entity.address.version_1.address import Address
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class AddressValidationProcessor(CyodaProcessor):
    """Processor for Address validation that validates address information."""

    def __init__(self) -> None:
        super().__init__(
            name="AddressValidationProcessor",
            description="Validates address information",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        try:
            self.logger.info(
                f"Processing validation for Address {getattr(entity, 'technical_id', '<unknown>')}"
            )

            address = cast_entity(entity, Address)

            # Validate street is not empty
            if not address.street or len(address.street.strip()) == 0:
                raise ValueError("Street address is required")

            # Validate city is not empty
            if not address.city or len(address.city.strip()) == 0:
                raise ValueError("City is required")

            # Validate zip code format
            if address.zip_code:
                await self._validate_zip_code_format(address.zip_code)

            # Validate country exists
            if address.country:
                await self._validate_country_exists(address.country)

            # Normalize address format
            address = self._normalize_address_format(address)

            address.update_timestamp()
            self.logger.info(
                f"Address {address.technical_id} validation processed successfully"
            )

            return address

        except Exception as e:
            self.logger.error(f"Error processing address validation: {str(e)}")
            raise

    async def _validate_zip_code_format(self, zip_code: str) -> None:
        """Validate zip code format"""
        # Basic US zip code validation (5 digits or 5+4 format)
        if not re.match(r"^\d{5}(-\d{4})?$", zip_code):
            raise ValueError("Invalid zip code format")

    async def _validate_country_exists(self, country: str) -> None:
        """Validate country exists"""
        # Placeholder - would validate against country list
        valid_countries = ["USA", "Canada", "Mexico", "United States", "US"]
        if country not in valid_countries:
            self.logger.warning(f"Country {country} not in standard list")

    def _normalize_address_format(self, address: Address) -> Address:
        """Normalize address format"""
        if address.street:
            address.street = address.street.title()
        if address.city:
            address.city = address.city.title()
        if address.state:
            address.state = address.state.upper()
        if address.country:
            address.country = address.country.upper()
        return address
