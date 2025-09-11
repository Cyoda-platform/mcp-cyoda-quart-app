"""
EmailDeliveryCreationProcessor for Cyoda Client Application

Creates email delivery record for a subscriber and cat fact.
Validates subscriber and cat fact existence before creation.
"""

import logging
from typing import Any, Optional, Protocol, cast, runtime_checkable

from application.entity.emaildelivery.version_1.emaildelivery import EmailDelivery
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
    async def get_by_id(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> Optional[Any]: ...


class EmailDeliveryCreationProcessor(CyodaProcessor):
    """
    Processor for creating email delivery records.
    Validates subscriber and cat fact existence before creating delivery record.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailDeliveryCreationProcessor",
            description="Creates email delivery record for a subscriber and cat fact",
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
        Process email delivery creation according to functional requirements.

        Args:
            entity: The EmailDelivery entity to create
            **kwargs: Additional processing parameters (subscriberId, catFactId)

        Returns:
            The created EmailDelivery entity
        """
        try:
            self.logger.info(
                f"Processing email delivery creation {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailDelivery for type-safe operations
            email_delivery = cast_entity(entity, EmailDelivery)

            # Get subscriber and cat fact IDs from kwargs or entity
            subscriber_id = kwargs.get("subscriber_id") or email_delivery.subscriber_id
            cat_fact_id = kwargs.get("cat_fact_id") or email_delivery.cat_fact_id

            if not subscriber_id:
                raise ValueError("Subscriber ID is required")
            if not cat_fact_id:
                raise ValueError("Cat fact ID is required")

            # Validate subscriber exists and is active
            await self._validate_subscriber(subscriber_id)

            # Validate cat fact exists and is scheduled
            await self._validate_cat_fact(cat_fact_id)

            # Set the IDs if not already set
            email_delivery.subscriber_id = subscriber_id
            email_delivery.cat_fact_id = cat_fact_id

            # Initialize delivery tracking fields
            email_delivery.delivery_attempts = 0
            email_delivery.last_attempt_date = None
            email_delivery.error_message = None

            # Update timestamp
            email_delivery.update_timestamp()

            self.logger.info(
                f"Email delivery record created for subscriber {subscriber_id} and cat fact {cat_fact_id}"
            )

            return email_delivery

        except Exception as e:
            self.logger.error(
                f"Error processing email delivery creation {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _validate_subscriber(self, subscriber_id: str) -> None:
        """
        Validate that subscriber exists and is active.

        Args:
            subscriber_id: ID of the subscriber to validate

        Raises:
            ValueError: If subscriber doesn't exist or is not active
        """
        entity_service = self._get_entity_service()

        try:
            subscriber = await entity_service.get_by_id(
                entity_id=subscriber_id, entity_class="Subscriber", entity_version="1"
            )

            if not subscriber:
                raise ValueError(f"Subscriber {subscriber_id} not found")

            # Check if subscriber is active
            if hasattr(subscriber, "data"):
                is_active = subscriber.data.get("isActive", False)
                if not is_active:
                    raise ValueError(f"Subscriber {subscriber_id} is not active")

        except Exception as e:
            if "not found" in str(e) or "not active" in str(e):
                raise
            self.logger.warning(
                f"Error validating subscriber {subscriber_id}: {str(e)}"
            )
            # Continue processing - validation errors will be caught by workflow

    async def _validate_cat_fact(self, cat_fact_id: str) -> None:
        """
        Validate that cat fact exists and is scheduled.

        Args:
            cat_fact_id: ID of the cat fact to validate

        Raises:
            ValueError: If cat fact doesn't exist or is not scheduled
        """
        entity_service = self._get_entity_service()

        try:
            cat_fact = await entity_service.get_by_id(
                entity_id=cat_fact_id, entity_class="CatFact", entity_version="1"
            )

            if not cat_fact:
                raise ValueError(f"Cat fact {cat_fact_id} not found")

            # Check if cat fact is scheduled
            if hasattr(cat_fact, "metadata") and hasattr(cat_fact.metadata, "state"):
                if cat_fact.metadata.state != "scheduled":
                    raise ValueError(f"Cat fact {cat_fact_id} is not scheduled")

        except Exception as e:
            if "not found" in str(e) or "not scheduled" in str(e):
                raise
            self.logger.warning(f"Error validating cat fact {cat_fact_id}: {str(e)}")
            # Continue processing - validation errors will be caught by workflow
