"""
InteractionValidationCriterion for Cyoda Client Application

Validates interaction data before recording.
"""

import logging
from typing import Any, Optional, Protocol, cast

from application.entity.interaction.version_1.interaction import Interaction
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from services.services import get_entity_service


class _EntityService(Protocol):
    async def get_by_id(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> Optional[Any]: ...


class InteractionValidationCriterion(CyodaCriteriaChecker):
    """Criterion for validating interaction data before recording."""

    def __init__(self) -> None:
        super().__init__(
            name="InteractionValidationCriterion",
            description="Validates interaction data before recording",
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
        """Check if the interaction data is valid."""
        try:
            interaction = cast_entity(entity, Interaction)

            # Check if subscriber exists
            if not await self._subscriber_exists(interaction.subscriber_id):
                self.logger.warning(
                    f"Subscriber not found: {interaction.subscriber_id}"
                )
                return False

            # Check if subscriber is active (except for unsubscribe interactions)
            if interaction.interaction_type != "UNSUBSCRIBE":
                if not await self._is_subscriber_active(interaction.subscriber_id):
                    self.logger.warning("Subscriber is not active")
                    return False

            # Validate interaction type
            if interaction.interaction_type not in interaction.VALID_INTERACTION_TYPES:
                self.logger.warning(
                    f"Invalid interaction type: {interaction.interaction_type}"
                )
                return False

            # Validate email delivery if provided
            if interaction.email_delivery_id:
                if not await self._validate_email_delivery(
                    interaction.email_delivery_id, interaction.subscriber_id
                ):
                    self.logger.warning("Email delivery validation failed")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating interaction: {str(e)}")
            return False

    async def _subscriber_exists(self, subscriber_id: str) -> bool:
        """Check if subscriber exists."""
        entity_service = self._get_entity_service()

        try:
            subscriber = await entity_service.get_by_id(
                entity_id=subscriber_id, entity_class="Subscriber", entity_version="1"
            )
            return subscriber is not None
        except Exception:
            return False

    async def _is_subscriber_active(self, subscriber_id: str) -> bool:
        """Check if subscriber is active."""
        entity_service = self._get_entity_service()

        try:
            subscriber = await entity_service.get_by_id(
                entity_id=subscriber_id, entity_class="Subscriber", entity_version="1"
            )

            if not subscriber or not hasattr(subscriber, "data"):
                return False

            return subscriber.data.get("isActive", False)
        except Exception:
            return False

    async def _validate_email_delivery(
        self, email_delivery_id: str, subscriber_id: str
    ) -> bool:
        """Validate email delivery exists and belongs to subscriber."""
        entity_service = self._get_entity_service()

        try:
            email_delivery = await entity_service.get_by_id(
                entity_id=email_delivery_id,
                entity_class="EmailDelivery",
                entity_version="1",
            )

            if not email_delivery or not hasattr(email_delivery, "data"):
                return False

            return email_delivery.data.get("subscriberId") == subscriber_id
        except Exception:
            return False
