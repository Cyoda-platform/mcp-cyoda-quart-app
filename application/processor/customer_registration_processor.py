"""
CustomerRegistrationProcessor for Purrfect Pets API

Registers a new customer and activates their account.
"""

import logging
from datetime import datetime
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.customer.version_1.customer import Customer


class CustomerRegistrationProcessor(CyodaProcessor):
    """
    Processor for Customer registration that registers a new customer and activates their account.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CustomerRegistrationProcessor",
            description="Registers a new customer and activates their account",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Customer registration according to functional requirements.

        Args:
            entity: The Customer entity to process (must be in initial state)
            **kwargs: Additional processing parameters

        Returns:
            The processed customer entity in active state
        """
        try:
            self.logger.info(
                f"Processing Customer registration for {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Customer for type-safe operations
            customer = cast_entity(entity, Customer)

            # Validate customer data (email, name, contact info required)
            self._validate_customer_data(customer)

            # Check email uniqueness (in a real system, this would query the database)
            await self._check_email_uniqueness(customer.email)

            # Validate date of birth (must be 18+ for adoption)
            self._validate_age_requirement(customer.date_of_birth)

            # Validate phone number format (basic validation)
            self._validate_phone_number(customer.phone)

            # Set registration date to current timestamp
            customer.set_registration_date()

            # Log customer registration
            self.logger.info(
                f"Customer {customer.technical_id} ({customer.get_full_name()}) registered successfully"
            )

            return customer

        except Exception as e:
            self.logger.error(
                f"Error processing customer registration {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _validate_customer_data(self, customer: Customer) -> None:
        """
        Validate customer data according to functional requirements.

        Args:
            customer: The Customer entity to validate

        Raises:
            ValueError: If validation fails
        """
        # Email, name, contact info are required (validated by Pydantic model)
        if not customer.email or len(customer.email.strip()) == 0:
            raise ValueError("Customer email is required")
        
        if not customer.first_name or len(customer.first_name.strip()) == 0:
            raise ValueError("Customer first name is required")
        
        if not customer.last_name or len(customer.last_name.strip()) == 0:
            raise ValueError("Customer last name is required")
        
        if not customer.phone or len(customer.phone.strip()) == 0:
            raise ValueError("Customer phone is required")

        self.logger.debug(f"Customer data validation passed for {customer.get_full_name()}")

    async def _check_email_uniqueness(self, email: str) -> None:
        """
        Check email uniqueness (placeholder for real implementation).

        Args:
            email: The email to check

        Raises:
            ValueError: If email is not unique
        """
        # In a real system, you would query the database to check if email exists
        # For this implementation, we'll just log the check
        self.logger.debug(f"Checking email uniqueness for: {email}")
        
        # Placeholder - in real implementation:
        # existing_customer = await entity_service.find_by_business_id(
        #     entity_class=Customer.ENTITY_NAME,
        #     business_id=email,
        #     business_id_field="email"
        # )
        # if existing_customer:
        #     raise ValueError(f"Email {email} is already registered")

    def _validate_age_requirement(self, date_of_birth: str) -> None:
        """
        Validate that customer is 18+ years old.

        Args:
            date_of_birth: Date of birth in YYYY-MM-DD format

        Raises:
            ValueError: If customer is under 18
        """
        try:
            birth_date = datetime.strptime(date_of_birth, "%Y-%m-%d")
            today = datetime.now()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            if age < 18:
                raise ValueError("Customer must be at least 18 years old for adoption")
                
            self.logger.debug(f"Age validation passed: {age} years old")
            
        except ValueError as e:
            if "18 years old" in str(e):
                raise
            raise ValueError(f"Invalid date of birth format: {date_of_birth}")

    def _validate_phone_number(self, phone: str) -> None:
        """
        Validate phone number format (basic validation).

        Args:
            phone: The phone number to validate

        Raises:
            ValueError: If phone number format is invalid
        """
        # Basic validation - remove common formatting and check length
        cleaned_phone = ''.join(filter(str.isdigit, phone))
        
        if len(cleaned_phone) < 10:
            raise ValueError("Phone number must contain at least 10 digits")
        
        if len(cleaned_phone) > 15:
            raise ValueError("Phone number is too long")

        self.logger.debug(f"Phone number validation passed: {phone}")
