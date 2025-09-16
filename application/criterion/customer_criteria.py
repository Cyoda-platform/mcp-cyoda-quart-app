"""
Customer Criteria for Purrfect Pets API

Validation criteria for customer-related business rules and workflows.
"""

import logging
import re
from datetime import datetime
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.customer.version_1.customer import Customer


class CustomerDataValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for checking customer data completeness and validity.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CustomerDataValidationCriterion",
            description="Validates customer data completeness and validity",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if customer data is complete and valid.

        Args:
            entity: The Customer entity to validate
            **kwargs: Additional criteria parameters

        Returns:
            True if customer data is valid, False otherwise
        """
        try:
            self.logger.info(
                f"Validating customer data {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Customer for type-safe operations
            customer = cast_entity(entity, Customer)

            # Validate required personal information
            if not self._validate_personal_info(customer):
                return False

            # Validate contact information
            if not self._validate_contact_info(customer):
                return False

            # Validate address information
            if not self._validate_address_info(customer):
                return False

            # Validate housing information
            if not self._validate_housing_info(customer):
                return False

            # Validate age requirement (18+)
            if not self._validate_age_requirement(customer):
                return False

            self.logger.info(f"Customer {customer.technical_id} passed data validation")
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating customer data {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_personal_info(self, customer: Customer) -> bool:
        """Validate personal information."""
        if not customer.first_name or len(customer.first_name.strip()) < 2:
            self.logger.warning(
                f"Invalid first name for customer {customer.technical_id}"
            )
            return False

        if not customer.last_name or len(customer.last_name.strip()) < 2:
            self.logger.warning(
                f"Invalid last name for customer {customer.technical_id}"
            )
            return False

        if not customer.occupation or len(customer.occupation.strip()) < 2:
            self.logger.warning(
                f"Invalid occupation for customer {customer.technical_id}"
            )
            return False

        return True

    def _validate_contact_info(self, customer: Customer) -> bool:
        """Validate contact information."""
        # Email validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, customer.email):
            self.logger.warning(
                f"Invalid email format for customer {customer.technical_id}"
            )
            return False

        # Phone validation
        cleaned_phone = re.sub(r"[^\d]", "", customer.phone)
        if len(cleaned_phone) < 10:
            self.logger.warning(
                f"Invalid phone number for customer {customer.technical_id}"
            )
            return False

        return True

    def _validate_address_info(self, customer: Customer) -> bool:
        """Validate address information."""
        if not customer.address or len(customer.address.strip()) < 5:
            self.logger.warning(f"Invalid address for customer {customer.technical_id}")
            return False

        if not customer.city or len(customer.city.strip()) < 2:
            self.logger.warning(f"Invalid city for customer {customer.technical_id}")
            return False

        if not customer.zip_code or len(customer.zip_code.strip()) < 5:
            self.logger.warning(
                f"Invalid zip code for customer {customer.technical_id}"
            )
            return False

        return True

    def _validate_housing_info(self, customer: Customer) -> bool:
        """Validate housing information."""
        if customer.housing_type not in Customer.ALLOWED_HOUSING_TYPES:
            self.logger.warning(
                f"Invalid housing type for customer {customer.technical_id}"
            )
            return False

        if customer.pet_experience not in Customer.ALLOWED_PET_EXPERIENCE:
            self.logger.warning(
                f"Invalid pet experience for customer {customer.technical_id}"
            )
            return False

        return True

    def _validate_age_requirement(self, customer: Customer) -> bool:
        """Validate age requirement (18+)."""
        try:
            birth_date = datetime.strptime(customer.date_of_birth, "%Y-%m-%d")
            today = datetime.now()
            age = (
                today.year
                - birth_date.year
                - ((today.month, today.day) < (birth_date.month, birth_date.day))
            )

            if age < 18:
                self.logger.warning(
                    f"Customer {customer.technical_id} is under 18 years old"
                )
                return False

            return True

        except ValueError:
            self.logger.warning(
                f"Invalid date of birth format for customer {customer.technical_id}"
            )
            return False


class CustomerEligibilityCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for checking customer eligibility for pet adoption.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CustomerEligibilityCriterion",
            description="Validates customer eligibility for pet adoption",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if customer is eligible for pet adoption.

        Args:
            entity: The Customer entity to validate
            **kwargs: Additional criteria parameters

        Returns:
            True if customer is eligible, False otherwise
        """
        try:
            self.logger.info(
                f"Validating customer eligibility {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Customer for type-safe operations
            customer = cast_entity(entity, Customer)

            # Customer must be verified
            if not customer.is_verified():
                self.logger.warning(
                    f"Customer {customer.technical_id} is not verified: {customer.state}"
                )
                return False

            # Check adoption privileges
            adoption_privileges = customer.get_metadata("adoption_privileges", True)
            if not adoption_privileges:
                self.logger.warning(
                    f"Customer {customer.technical_id} does not have adoption privileges"
                )
                return False

            # Check for any active suspensions
            if customer.is_suspended():
                self.logger.warning(
                    f"Customer {customer.technical_id} is currently suspended"
                )
                return False

            # Check maximum concurrent applications
            max_applications = customer.get_metadata("max_concurrent_applications", 3)
            current_applications = customer.get_metadata("application_count", 0)

            if current_applications >= max_applications:
                self.logger.warning(
                    f"Customer {customer.technical_id} has reached maximum concurrent applications: {current_applications}/{max_applications}"
                )
                return False

            # Validate housing suitability for pets
            if not self._validate_housing_suitability(customer):
                return False

            self.logger.info(
                f"Customer {customer.technical_id} passed eligibility validation"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating customer eligibility {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_housing_suitability(self, customer: Customer) -> bool:
        """Validate housing suitability for pets."""
        # Basic housing validation
        if customer.housing_type == "Mobile Home" and not customer.has_yard:
            self.logger.warning(
                f"Customer {customer.technical_id} has mobile home without yard - may not be suitable for larger pets"
            )
            # This is a warning, not a failure - still allow adoption but flag for review

        # Check pet experience level
        if customer.pet_experience == "Beginner" and customer.has_other_pets:
            self.logger.info(
                f"Customer {customer.technical_id} is beginner but has other pets - good sign"
            )

        return True


class SuspensionReviewCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for reviewing customer suspensions.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SuspensionReviewCriterion",
            description="Validates customer suspension review and potential reinstatement",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if customer suspension can be reviewed for reinstatement.

        Args:
            entity: The Customer entity to validate
            **kwargs: Additional criteria parameters

        Returns:
            True if suspension can be reviewed, False otherwise
        """
        try:
            self.logger.info(
                f"Validating suspension review {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Customer for type-safe operations
            customer = cast_entity(entity, Customer)

            # Customer must be suspended
            if not customer.is_suspended():
                self.logger.warning(
                    f"Customer {customer.technical_id} is not suspended: {customer.state}"
                )
                return False

            # Check suspension duration
            suspension_date = customer.get_metadata("suspension_date")
            if suspension_date:
                # In a real implementation, check if enough time has passed
                self.logger.info(
                    f"Customer {customer.technical_id} suspended on {suspension_date}"
                )

            # Check suspension reason severity
            suspension_reason = customer.get_metadata("suspension_reason", "")
            if (
                "fraud" in suspension_reason.lower()
                or "abuse" in suspension_reason.lower()
            ):
                self.logger.warning(
                    f"Customer {customer.technical_id} suspended for serious violation: {suspension_reason}"
                )
                return False

            # Check for any pending issues
            pending_issues = customer.get_metadata("pending_issues", [])
            if pending_issues:
                self.logger.warning(
                    f"Customer {customer.technical_id} has pending issues: {pending_issues}"
                )
                return False

            self.logger.info(
                f"Customer {customer.technical_id} passed suspension review validation"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating suspension review {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
