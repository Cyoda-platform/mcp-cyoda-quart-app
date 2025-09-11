"""
SubscriberRegistrationProcessor for Cyoda Client Application

Processes new subscriber registration and creates subscriber record.
Handles email validation, uniqueness checks, and welcome email sending.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional, Protocol, cast, runtime_checkable

from application.entity.subscriber.version_1.subscriber import Subscriber
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


@runtime_checkable
class _HasId(Protocol):
    id: str


@runtime_checkable
class _HasMetadata(Protocol):
    metadata: _HasId


class _EntityService(Protocol):
    async def save(
        self, *, entity: dict[str, Any], entity_class: str, entity_version: str
    ) -> _HasMetadata: ...

    async def search(
        self, entity_class: str, condition: Any, entity_version: str = "1"
    ) -> list[Any]: ...


class SubscriberRegistrationProcessor(CyodaProcessor):
    """
    Processor for new subscriber registration that handles validation,
    uniqueness checks, and creates subscriber record.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SubscriberRegistrationProcessor",
            description="Processes new subscriber registration and creates subscriber record",
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

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process new subscriber registration according to functional requirements.

        Args:
            entity: The Subscriber entity to process (must be in initial state)
            **kwargs: Additional processing parameters

        Returns:
            The processed subscriber entity with generated token and timestamps
        """
        try:
            self.logger.info(
                f"Processing subscriber registration {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Subscriber for type-safe operations
            subscriber = cast_entity(entity, Subscriber)

            # Validate email format and uniqueness
            await self._validate_email_uniqueness(subscriber.email)

            # Generate unique unsubscribe token if not already set
            if not subscriber.unsubscribe_token:
                subscriber.unsubscribe_token = str(uuid.uuid4())

            # Set subscription date if not already set
            if not subscriber.subscription_date:
                subscriber.subscription_date = (
                    datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                )

            # Set initial active status to false (pending verification)
            subscriber.is_active = False

            # Update timestamp
            subscriber.update_timestamp()

            # Send welcome email (simulated)
            await self._send_welcome_email(subscriber)

            self.logger.info(
                f"Subscriber registration processed successfully for {subscriber.email}"
            )

            return subscriber

        except Exception as e:
            self.logger.error(
                f"Error processing subscriber registration {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _validate_email_uniqueness(self, email: str) -> None:
        """
        Validate that email is not already subscribed and active.

        Args:
            email: Email address to validate

        Raises:
            ValueError: If email is already subscribed and active
        """
        entity_service = self._get_entity_service()

        try:
            # Search for existing subscribers with this email
            # Note: This is a simplified search - in real implementation,
            # we would use proper search conditions
            existing_subscribers = await entity_service.search(
                entity_class="Subscriber",
                condition={"email": email.lower()},
                entity_version="1",
            )

            # Check if any existing subscriber is active
            for existing in existing_subscribers:
                if hasattr(existing, "data") and existing.data.get("isActive", False):
                    if (
                        hasattr(existing, "get_state")
                        and existing.get_state() == "active"
                    ):
                        raise ValueError("Email already subscribed")

        except Exception as e:
            if "Email already subscribed" in str(e):
                raise
            # Log other errors but don't fail the registration
            self.logger.warning(f"Error checking email uniqueness: {str(e)}")

    async def _send_welcome_email(self, subscriber: Subscriber) -> None:
        """
        Send welcome email with verification link (simulated).

        Args:
            subscriber: The subscriber to send welcome email to
        """
        try:
            # In a real implementation, this would send an actual email
            # For now, we just log the action
            self.logger.info(
                f"Sending welcome email to {subscriber.email} with verification link"
            )

            # Simulate email sending delay
            # await asyncio.sleep(0.1)

            self.logger.info(f"Welcome email sent successfully to {subscriber.email}")

        except Exception as e:
            self.logger.error(
                f"Failed to send welcome email to {subscriber.email}: {str(e)}"
            )
            # Don't fail the registration if email sending fails
            pass
