"""
InteractionRecordingProcessor for Cyoda Client Application

Records user interaction with cat fact emails.
Validates interaction data and creates interaction record.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Optional, Protocol, cast

from application.entity.interaction.version_1.interaction import Interaction
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class _EntityService(Protocol):
    async def get_by_id(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> Optional[Any]: ...


class InteractionRecordingProcessor(CyodaProcessor):
    """
    Processor for recording user interactions with cat fact emails.
    Validates interaction data and creates interaction records.
    """

    def __init__(self) -> None:
        super().__init__(
            name="InteractionRecordingProcessor",
            description="Records user interaction with cat fact emails",
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
        Process interaction recording according to functional requirements.

        Args:
            entity: The Interaction entity to record
            **kwargs: Additional interaction data

        Returns:
            The recorded Interaction entity
        """
        try:
            self.logger.info(
                f"Processing interaction recording {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Interaction for type-safe operations
            interaction = cast_entity(entity, Interaction)

            # Validate subscriber exists
            await self._validate_subscriber(interaction.subscriber_id)

            # Validate email delivery if provided
            if interaction.email_delivery_id:
                await self._validate_email_delivery(
                    interaction.email_delivery_id, interaction.subscriber_id
                )

            # Set interaction date if not already set
            if not interaction.interaction_date:
                interaction.interaction_date = (
                    datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                )

            # Update timestamp
            interaction.update_timestamp()

            self.logger.info(
                f"Interaction recorded: {interaction.interaction_type} for subscriber {interaction.subscriber_id}"
            )

            return interaction

        except Exception as e:
            self.logger.error(
                f"Error processing interaction recording {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _validate_subscriber(self, subscriber_id: str) -> None:
        """
        Validate that subscriber exists.

        Args:
            subscriber_id: ID of the subscriber to validate

        Raises:
            ValueError: If subscriber doesn't exist
        """
        entity_service = self._get_entity_service()

        try:
            subscriber = await entity_service.get_by_id(
                entity_id=subscriber_id, entity_class="Subscriber", entity_version="1"
            )

            if not subscriber:
                raise ValueError(f"Subscriber {subscriber_id} not found")

        except Exception as e:
            if "not found" in str(e):
                raise
            self.logger.warning(
                f"Error validating subscriber {subscriber_id}: {str(e)}"
            )

    async def _validate_email_delivery(
        self, email_delivery_id: str, subscriber_id: str
    ) -> None:
        """
        Validate that email delivery exists and belongs to subscriber.

        Args:
            email_delivery_id: ID of the email delivery to validate
            subscriber_id: ID of the subscriber

        Raises:
            ValueError: If email delivery doesn't exist or doesn't belong to subscriber
        """
        entity_service = self._get_entity_service()

        try:
            email_delivery = await entity_service.get_by_id(
                entity_id=email_delivery_id,
                entity_class="EmailDelivery",
                entity_version="1",
            )

            if not email_delivery:
                raise ValueError(f"Email delivery {email_delivery_id} not found")

            # Check if email delivery belongs to this subscriber
            if hasattr(email_delivery, "data"):
                delivery_subscriber_id = email_delivery.data.get("subscriberId")
                if delivery_subscriber_id != subscriber_id:
                    raise ValueError(
                        "Email delivery does not belong to this subscriber"
                    )

        except Exception as e:
            if "not found" in str(e) or "does not belong" in str(e):
                raise
            self.logger.warning(
                f"Error validating email delivery {email_delivery_id}: {str(e)}"
            )
