"""
ActivateUserProcessor for Purrfect Pets API

Handles the activation of user accounts when they transition from registered to active,
verifying email tokens and sending welcome emails as specified in the User workflow.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from application.entity.user.version_1.user import User
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ActivateUserProcessor(CyodaProcessor):
    """
    Processor for activating User entities when they transition from registered to active.
    Verifies email tokens, marks email as verified, and sends welcome emails.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ActivateUserProcessor",
            description="Activate user account after email verification",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the User entity for activation.

        Args:
            entity: The User entity to activate (must be in 'registered' state)
            **kwargs: Additional processing parameters

        Returns:
            The activated user entity with verified email
        """
        try:
            self.logger.info(
                f"Activating User {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Verify email token (if provided in kwargs)
            self._verify_email_token(user, kwargs)

            # Set activation details
            self._set_activation_details(user)

            # Clear verification token
            self._clear_verification_token(user)

            # Send welcome email
            await self._send_welcome_email(user)

            # Log activation completion
            self.logger.info(
                f"User {user.technical_id} activated successfully with email {user.email}"
            )

            return user

        except Exception as e:
            self.logger.error(
                f"Error activating user {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _verify_email_token(self, user: User, kwargs: Dict[str, Any]) -> None:
        """
        Verify the email verification token.

        Args:
            user: The User entity to verify token for
            kwargs: Additional parameters that may contain the verification token

        Raises:
            ValueError: If token verification fails
        """
        # Get verification token from kwargs if provided
        provided_token = kwargs.get("verification_token")

        if provided_token:
            # Verify the token matches
            if not user.emailVerificationToken:
                raise ValueError("No verification token found for user")

            if provided_token != user.emailVerificationToken:
                raise ValueError("Invalid verification token")

            self.logger.debug("Email verification token validated successfully")
        else:
            # If no token provided, assume verification is being done administratively
            self.logger.info(
                "Email verification performed without token (administrative activation)"
            )

        # In production:
        # - Check token expiration
        # - Validate token format and security
        # - Rate limit verification attempts
        # - Log verification attempts for security

    def _set_activation_details(self, user: User) -> None:
        """
        Set activation timestamp and email verification status.

        Args:
            user: The User entity to set activation details for
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Mark email as verified
        user.emailVerified = True

        # Set activation timestamp
        user.activatedAt = current_timestamp

        # Update timestamp
        user.update_timestamp()

        self.logger.debug(
            f"Activation details set: emailVerified={user.emailVerified}, "
            f"activatedAt={user.activatedAt}"
        )

    def _clear_verification_token(self, user: User) -> None:
        """
        Clear the email verification token for security.

        Args:
            user: The User entity to clear token for
        """
        # Clear the verification token as it's no longer needed
        user.emailVerificationToken = None

        self.logger.debug("Email verification token cleared")

        # In production:
        # - Invalidate all pending verification tokens for this user
        # - Log token usage for audit purposes
        # - Clean up expired tokens from database

    async def _send_welcome_email(self, user: User) -> None:
        """
        Send welcome email to the activated user (simulated).

        Args:
            user: The User entity to send welcome email to
        """
        # In a real implementation, this would send actual welcome emails
        welcome_message = (
            f"Welcome to Purrfect Pets, {user.firstName or user.username}! "
            f"Your account has been successfully activated. "
            f"You can now browse and purchase pets from our store."
        )

        self.logger.info(
            f"WELCOME EMAIL: Sending welcome email to {user.email}. "
            f"Message: {welcome_message}"
        )

        # Could integrate with email services:
        # - SendGrid, Mailgun, AWS SES, etc.
        # - Welcome email templates with personalization
        # - Onboarding email sequences
        # - User preference settings
        # - Marketing opt-in/opt-out handling
        # - Email analytics and tracking
