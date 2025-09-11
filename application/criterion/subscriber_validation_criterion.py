"""
SubscriberValidationCriterion for Cyoda Client Application

Validates subscriber data during registration and updates.
"""

import logging
import re
from typing import Any, Optional, Protocol, cast

from application.entity.subscriber.version_1.subscriber import Subscriber
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from services.services import get_entity_service


class _EntityService(Protocol):
    async def search(
        self, entity_class: str, condition: Any, entity_version: str = "1"
    ) -> list[Any]: ...


class SubscriberValidationCriterion(CyodaCriteriaChecker):
    """
    Criterion for validating subscriber data during registration and updates.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SubscriberValidationCriterion",
            description="Validates subscriber data during registration and updates",
        )
        self.entity_service: Optional[_EntityService] = None
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    def _get_entity_service(self) -> _EntityService:
        """Get entity service lazily"""
        if self.entity_service is None:
            self.entity_service = cast(_EntityService, get_entity_service())
        return self.entity_service

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the subscriber meets all validation criteria.

        Args:
            entity: The Subscriber entity to validate
            **kwargs: Additional criteria parameters

        Returns:
            True if the subscriber data is valid, False otherwise
        """
        try:
            self.logger.info(
                f"Validating subscriber {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Subscriber for type-safe operations
            subscriber = cast_entity(entity, Subscriber)

            # Check if email is required and valid format
            if not subscriber.email or len(subscriber.email.strip()) == 0:
                self.logger.warning("Email is required")
                return False

            if not self._is_valid_email_format(subscriber.email):
                self.logger.warning(f"Invalid email format: {subscriber.email}")
                return False

            # For new registrations, check email uniqueness
            if not subscriber.get_id() or subscriber.get_id() == "":
                if await self._is_email_already_subscribed(subscriber.email):
                    self.logger.warning(
                        f"Email is already subscribed: {subscriber.email}"
                    )
                    return False

            # Validate first name if provided
            if subscriber.first_name and not self._is_valid_name(subscriber.first_name):
                self.logger.warning(
                    f"First name contains special characters: {subscriber.first_name}"
                )
                return False

            # Validate last name if provided
            if subscriber.last_name and not self._is_valid_name(subscriber.last_name):
                self.logger.warning(
                    f"Last name contains special characters: {subscriber.last_name}"
                )
                return False

            self.logger.info(
                f"Subscriber {subscriber.email} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error validating subscriber: {str(e)}")
            return False

    def _is_valid_email_format(self, email: str) -> bool:
        """Validate email format using regex."""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(email_pattern, email) is not None

    def _is_valid_name(self, name: str) -> bool:
        """Check if name contains only allowed characters."""
        # Allow only letters, spaces, hyphens, and apostrophes
        allowed_pattern = r"^[a-zA-Z\s\'-]+$"
        return re.match(allowed_pattern, name) is not None

    async def _is_email_already_subscribed(self, email: str) -> bool:
        """Check if email is already subscribed and active."""
        entity_service = self._get_entity_service()

        try:
            existing_subscribers = await entity_service.search(
                entity_class="Subscriber",
                condition={"email": email.lower()},
                entity_version="1",
            )

            # Check if any existing subscriber is active
            for subscriber in existing_subscribers:
                if hasattr(subscriber, "data"):
                    is_active = subscriber.data.get("isActive", False)
                    state = getattr(subscriber, "get_state", lambda: "unknown")()
                    if is_active and state == "active":
                        return True

            return False

        except Exception as e:
            self.logger.warning(f"Error checking email uniqueness: {str(e)}")
            return False  # Allow registration if we can't check
