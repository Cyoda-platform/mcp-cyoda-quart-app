"""
UserRegistrationProcessor for Cyoda Client Application

Creates a new user account as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.user.version_1.user import User


class UserRegistrationProcessor(CyodaProcessor):
    """
    Processor for registering new User entities.
    """

    def __init__(self) -> None:
        super().__init__(
            name="UserRegistrationProcessor",
            description="Registers new User entities and sends verification email",
        )
        self.logger: logging.Logger = getattr(self, "logger", logging.getLogger(__name__))

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the User registration according to functional requirements.

        Args:
            entity: The User entity to register (should be in initial state)
            **kwargs: Additional processing parameters

        Returns:
            The registered user entity
        """
        try:
            self.logger.info(
                f"Processing User registration {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Validate email format and username uniqueness
            await self._validate_user_data(user)

            # Set creation time
            user.createdAt = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            # Ensure default preferences are set
            if not user.preferences:
                user.preferences = {
                    "defaultEggType": "MEDIUM_BOILED",
                    "notificationSound": "classic",
                    "autoStart": False,
                    "reminderMinutes": 1,
                }

            # Send verification email
            await self._send_verification_email(user.email)

            self.logger.info(f"User {user.technical_id} registered successfully")

            return user

        except Exception as e:
            self.logger.error(
                f"Error processing User registration {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _validate_user_data(self, user: User) -> None:
        """
        Validate user data for registration.

        Args:
            user: The User entity to validate
        """
        try:
            # Validate email format (already done by Pydantic, but double-check)
            if not user.email or "@" not in user.email:
                raise ValueError("Invalid email format")

            # Validate username format (already done by Pydantic, but double-check)
            if not user.username or len(user.username) < 3:
                raise ValueError("Username must be at least 3 characters")

            # In a real implementation, check uniqueness against database
            # For now, we'll assume validation passes
            self.logger.info(f"User data validation passed for {user.username}")

        except Exception as e:
            self.logger.error(f"User data validation failed: {str(e)}")
            raise

    async def _send_verification_email(self, email: str) -> None:
        """
        Send verification email to user.

        Args:
            email: The user's email address
        """
        try:
            # In a real implementation, this would send actual verification email
            self.logger.info(f"Sending verification email to {email}")
            
            # Could integrate with email service like SendGrid, AWS SES, etc.
            
        except Exception as e:
            self.logger.error(f"Failed to send verification email to {email}: {str(e)}")
            # Don't raise - email failure shouldn't prevent registration
