"""
ValidUserCriterion for Purrfect Pets API

Validates that a User entity meets all required business rules before it can
proceed to email verification as specified in the User workflow requirements.
"""

import re
from typing import Any

from application.entity.user.version_1.user import User
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class ValidUserCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for User entities that checks all business rules
    before the entity can proceed to email verification.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ValidUserCriterion",
            description="Validates User business rules and data consistency before email verification",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the user entity meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be User)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating user entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Validate required fields
            if not self._validate_required_fields(user):
                return False

            # Validate business rules
            if not self._validate_business_rules(user):
                return False

            # Validate data consistency
            if not self._validate_data_consistency(user):
                return False

            self.logger.info(
                f"User entity {user.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating user entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _validate_required_fields(self, user: User) -> bool:
        """
        Validate that all required fields are present and valid.

        Args:
            user: The User entity to validate

        Returns:
            True if all required fields are valid, False otherwise
        """
        # Validate username
        if not user.username or len(user.username.strip()) == 0:
            self.logger.warning(
                f"User {user.technical_id} has invalid username: '{user.username}'"
            )
            return False

        # Validate email
        if not user.email or len(user.email.strip()) == 0:
            self.logger.warning(
                f"User {user.technical_id} has invalid email: '{user.email}'"
            )
            return False

        # Validate password (if provided)
        if user.password and len(user.password) < 8:
            self.logger.warning(
                f"User {user.technical_id} has password that is too short"
            )
            return False

        self.logger.debug(f"Required fields validated for user {user.technical_id}")
        return True

    def _validate_business_rules(self, user: User) -> bool:
        """
        Validate business rules for the user.

        Args:
            user: The User entity to validate

        Returns:
            True if business rules are satisfied, False otherwise
        """
        # Validate username format
        if not self._is_valid_username(user.username):
            self.logger.warning(
                f"User {user.technical_id} has invalid username format: '{user.username}'"
            )
            return False

        # Validate email format
        if not self._is_valid_email(user.email):
            self.logger.warning(
                f"User {user.technical_id} has invalid email format: '{user.email}'"
            )
            return False

        # Validate phone format if provided
        if user.phone and not self._is_valid_phone(user.phone):
            self.logger.warning(
                f"User {user.technical_id} has invalid phone format: '{user.phone}'"
            )
            return False

        # Validate name fields if provided
        if user.firstName and not self._is_valid_name(user.firstName):
            self.logger.warning(
                f"User {user.technical_id} has invalid first name: '{user.firstName}'"
            )
            return False

        if user.lastName and not self._is_valid_name(user.lastName):
            self.logger.warning(
                f"User {user.technical_id} has invalid last name: '{user.lastName}'"
            )
            return False

        self.logger.debug(f"Business rules validated for user {user.technical_id}")
        return True

    def _is_valid_username(self, username: str) -> bool:
        """Validate username format"""
        if len(username) < 3 or len(username) > 50:
            return False
        return bool(re.match(r"^[a-zA-Z0-9_-]+$", username))

    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(email_pattern, email))

    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        # Remove formatting characters
        cleaned_phone = re.sub(r"[^\d+]", "", phone)
        return bool(re.match(r"^\+?[1-9]\d{9,14}$", cleaned_phone))

    def _is_valid_name(self, name: str) -> bool:
        """Validate name format"""
        if len(name) > 100:
            return False
        return bool(re.match(r"^[a-zA-Z\s'-]+$", name))

    def _validate_data_consistency(self, user: User) -> bool:
        """
        Validate data consistency and state-specific requirements.

        Args:
            user: The User entity to validate

        Returns:
            True if data is consistent, False otherwise
        """
        # For registered users, ensure registration details are set
        if user.state == "registered":
            if not user.registeredAt:
                self.logger.warning(
                    f"User {user.technical_id} is registered but has no registration timestamp"
                )
                # Don't fail validation as this might be set by the processor
                pass

            if not user.emailVerificationToken:
                self.logger.warning(
                    f"User {user.technical_id} is registered but has no verification token"
                )
                # Don't fail validation as this might be set by the processor
                pass

        # For active users, ensure email is verified
        if user.state == "active":
            if not user.emailVerified:
                self.logger.warning(
                    f"User {user.technical_id} is active but email is not verified"
                )
                # Don't fail validation as this might be set by the processor
                pass

            if not user.activatedAt:
                self.logger.warning(
                    f"User {user.technical_id} is active but has no activation timestamp"
                )
                # Don't fail validation as this might be set by the processor
                pass

        # Validate preferences structure if provided
        if user.preferences:
            if not isinstance(user.preferences, dict):
                self.logger.warning(
                    f"User {user.technical_id} has invalid preferences structure"
                )
                return False

        self.logger.debug(f"Data consistency validated for user {user.technical_id}")
        return True
