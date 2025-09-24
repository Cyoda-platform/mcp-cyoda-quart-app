"""
RegisterUserProcessor for Purrfect Pets API

Handles the registration of new users when they transition from initial_state to registered,
validating uniqueness, encrypting passwords, and sending verification emails as specified
in the User workflow.
"""

import hashlib
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from application.entity.user.version_1.user import User
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class RegisterUserProcessor(CyodaProcessor):
    """
    Processor for registering User entities when they transition from initial_state to registered.
    Validates uniqueness, encrypts passwords, and sends verification emails.
    """

    def __init__(self) -> None:
        super().__init__(
            name="RegisterUserProcessor",
            description="Register new user account and send verification email",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the User entity for registration.

        Args:
            entity: The User entity to register (must be in 'initial_state')
            **kwargs: Additional processing parameters

        Returns:
            The registered user entity awaiting verification
        """
        try:
            self.logger.info(
                f"Registering User {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Validate unique username and email (simulated)
            await self._validate_unique_username(user)
            await self._validate_unique_email(user)

            # Encrypt password
            self._encrypt_password(user)

            # Set registration details
            self._set_registration_details(user)

            # Generate email verification token
            self._generate_email_verification_token(user)

            # Send verification email
            await self._send_verification_email(user)

            # Log registration completion
            self.logger.info(
                f"User {user.technical_id} registered successfully with username {user.username}"
            )

            return user

        except Exception as e:
            self.logger.error(
                f"Error registering user {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _validate_unique_username(self, user: User) -> None:
        """
        Validate that the username is unique (simulated).

        Args:
            user: The User entity to validate

        Raises:
            ValueError: If username is not unique
        """
        # In a real implementation, this would check the database
        # For now, we simulate the validation

        # Simulate some reserved usernames
        reserved_usernames = {"admin", "root", "system", "test", "demo"}

        if user.username.lower() in reserved_usernames:
            raise ValueError(
                f"Username '{user.username}' is reserved and cannot be used"
            )

        self.logger.debug(f"Username '{user.username}' is available")

        # Could integrate with user management systems:
        # - Query database for existing usernames
        # - Check against external identity providers
        # - Validate against business rules

    async def _validate_unique_email(self, user: User) -> None:
        """
        Validate that the email is unique (simulated).

        Args:
            user: The User entity to validate

        Raises:
            ValueError: If email is not unique
        """
        # In a real implementation, this would check the database
        # For now, we simulate the validation

        # Simulate some reserved email domains
        reserved_domains = {"example.com", "test.com", "localhost"}
        email_domain = user.email.split("@")[1].lower() if "@" in user.email else ""

        if email_domain in reserved_domains:
            raise ValueError(
                f"Email domain '{email_domain}' is not allowed for registration"
            )

        self.logger.debug(f"Email '{user.email}' is available")

        # Could integrate with user management systems:
        # - Query database for existing emails
        # - Check against external identity providers
        # - Validate email deliverability

    def _encrypt_password(self, user: User) -> None:
        """
        Encrypt the user's password.

        Args:
            user: The User entity to encrypt password for
        """
        if not user.password:
            # Generate a temporary password if none provided
            user.password = str(uuid.uuid4())[:12]
            self.logger.info("Generated temporary password for user")

        # Simple password hashing (in production, use bcrypt, scrypt, or Argon2)
        salt = str(uuid.uuid4())[:8]
        password_hash = hashlib.sha256(f"{user.password}{salt}".encode()).hexdigest()

        # Store the hashed password (in real implementation, store salt separately)
        user.password = f"{salt}:{password_hash}"

        self.logger.debug("Password encrypted successfully")

        # In production, use proper password hashing:
        # - bcrypt, scrypt, or Argon2
        # - Proper salt generation and storage
        # - Password strength validation
        # - Password history tracking

    def _set_registration_details(self, user: User) -> None:
        """
        Set registration timestamp and details.

        Args:
            user: The User entity to set registration details for
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Set registration timestamp
        user.registeredAt = current_timestamp

        # Initialize email verification status
        user.emailVerified = False

        # Update timestamp
        user.update_timestamp()

        self.logger.debug(f"Registration details set: registeredAt={user.registeredAt}")

    def _generate_email_verification_token(self, user: User) -> None:
        """
        Generate email verification token.

        Args:
            user: The User entity to generate token for
        """
        # Generate a secure verification token
        verification_token = str(uuid.uuid4()).replace("-", "")
        user.emailVerificationToken = verification_token

        self.logger.debug("Email verification token generated")

        # In production:
        # - Use cryptographically secure token generation
        # - Set token expiration time
        # - Store token securely with proper indexing

    async def _send_verification_email(self, user: User) -> None:
        """
        Send email verification email (simulated).

        Args:
            user: The User entity to send verification email to
        """
        # In a real implementation, this would send actual emails
        verification_url = (
            f"https://purrfectpets.com/verify?token={user.emailVerificationToken}"
        )

        self.logger.info(
            f"VERIFICATION EMAIL: Sending verification email to {user.email}. "
            f"Verification URL: {verification_url}"
        )

        # Could integrate with email services:
        # - SendGrid, Mailgun, AWS SES, etc.
        # - HTML email templates
        # - Email delivery tracking
        # - Bounce and complaint handling
        # - Resend verification logic
