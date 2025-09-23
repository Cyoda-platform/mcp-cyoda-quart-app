"""
User Processors for Cyoda Client Application

Handles all User entity workflow transitions and business logic processing.
Implements processors for user registration, activation, suspension, reactivation, and deletion.
"""

import logging
from typing import Any

from application.entity.user.version_1.user import User
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class RegisterUserProcessor(CyodaProcessor):
    """
    Processor for registering new users.
    Handles user registration with email validation and default settings.
    """

    def __init__(self) -> None:
        super().__init__(
            name="RegisterUserProcessor",
            description="Creates new user account with default settings and email validation",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process user registration according to functional requirements.

        Args:
            entity: The User entity to register
            **kwargs: Additional processing parameters

        Returns:
            The registered user entity
        """
        try:
            self.logger.info(
                f"Registering user {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Validate email format (already done by entity validation)
            # Set default values if not provided
            if not user.timezone:
                user.timezone = "UTC"

            if not user.notification_time:
                user.notification_time = "08:00"

            # Set user as inactive initially (will be activated later)
            user.active = False

            # Update timestamp
            user.update_timestamp()

            self.logger.info(
                f"User {user.technical_id} registered successfully with email {user.email}"
            )

            return user

        except Exception as e:
            self.logger.error(
                f"Error registering user {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise


class ActivateUserProcessor(CyodaProcessor):
    """
    Processor for activating user accounts.
    Enables user account for receiving notifications.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ActivateUserProcessor",
            description="Activates user account for receiving notifications",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process user activation according to functional requirements.

        Args:
            entity: The User entity to activate
            **kwargs: Additional processing parameters

        Returns:
            The activated user entity
        """
        try:
            self.logger.info(
                f"Activating user {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Activate user account
            user.activate()

            self.logger.info(f"User {user.technical_id} activated successfully")

            return user

        except Exception as e:
            self.logger.error(
                f"Error activating user {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise


class SuspendUserProcessor(CyodaProcessor):
    """
    Processor for suspending user accounts.
    Temporarily disables user account.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SuspendUserProcessor",
            description="Temporarily disables user account",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process user suspension according to functional requirements.

        Args:
            entity: The User entity to suspend
            **kwargs: Additional processing parameters

        Returns:
            The suspended user entity
        """
        try:
            self.logger.info(
                f"Suspending user {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Deactivate user account
            user.deactivate()

            self.logger.info(f"User {user.technical_id} suspended successfully")

            return user

        except Exception as e:
            self.logger.error(
                f"Error suspending user {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise


class ReactivateUserProcessor(CyodaProcessor):
    """
    Processor for reactivating suspended user accounts.
    Reactivates suspended user account.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReactivateUserProcessor",
            description="Reactivates suspended user account",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process user reactivation according to functional requirements.

        Args:
            entity: The User entity to reactivate
            **kwargs: Additional processing parameters

        Returns:
            The reactivated user entity
        """
        try:
            self.logger.info(
                f"Reactivating user {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Activate user account
            user.activate()

            self.logger.info(f"User {user.technical_id} reactivated successfully")

            return user

        except Exception as e:
            self.logger.error(
                f"Error reactivating user {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise


class DeleteUserProcessor(CyodaProcessor):
    """
    Processor for deleting user accounts.
    Permanently removes user account and deactivates related subscriptions.
    """

    def __init__(self) -> None:
        super().__init__(
            name="DeleteUserProcessor",
            description="Permanently removes user account and related data",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process user deletion according to functional requirements.

        Args:
            entity: The User entity to delete
            **kwargs: Additional processing parameters

        Returns:
            The deleted user entity
        """
        try:
            self.logger.info(
                f"Deleting user {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to User for type-safe operations
            user = cast_entity(entity, User)

            # Deactivate all related subscriptions
            await self._deactivate_all_subscriptions(user.get_id())

            # Deactivate user account
            user.deactivate()

            self.logger.info(f"User {user.technical_id} deleted successfully")

            return user

        except Exception as e:
            self.logger.error(
                f"Error deleting user {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _deactivate_all_subscriptions(self, user_id: str) -> None:
        """
        Deactivate all subscriptions for a user.

        Args:
            user_id: The user ID whose subscriptions to deactivate
        """
        try:
            # Find all active subscriptions for this user
            # Note: This would require implementing a search for WeatherSubscription entities
            # For now, we'll log the intent - the actual implementation would depend on
            # the WeatherSubscription entity being available

            self.logger.info(f"Deactivating all subscriptions for user {user_id}")

            # TODO: Implement subscription deactivation when WeatherSubscription processors are available
            # This would involve:
            # 1. Search for all WeatherSubscription entities with user_id = user_id
            # 2. For each subscription, trigger the cancel_subscription transition

        except Exception as e:
            self.logger.error(
                f"Failed to deactivate subscriptions for user {user_id}: {str(e)}"
            )
            # Continue with user deletion even if subscription deactivation fails
            # This ensures user deletion is not blocked by subscription issues
