"""
InteractionProcessingProcessor for Cyoda Client Application

Processes interaction for analytics and reporting.
May trigger other entity transitions (e.g., unsubscribe).
"""

import logging
from typing import Any, Optional, Protocol, cast

from application.entity.interaction.version_1.interaction import Interaction
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class _EntityService(Protocol):
    async def execute_transition(
        self, *, entity_id: str, transition: str, entity_class: str, entity_version: str
    ) -> None: ...


class InteractionProcessingProcessor(CyodaProcessor):
    """
    Processor for processing interactions for analytics and reporting.
    May trigger other entity transitions based on interaction type.
    """

    def __init__(self) -> None:
        super().__init__(
            name="InteractionProcessingProcessor",
            description="Processes interaction for analytics and reporting",
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
        Process interaction for analytics according to functional requirements.

        Args:
            entity: The Interaction entity to process (must be in recorded state)
            **kwargs: Additional processing parameters

        Returns:
            The processed Interaction entity
        """
        try:
            self.logger.info(
                f"Processing interaction {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Interaction for type-safe operations
            interaction = cast_entity(entity, Interaction)

            # Validate interaction is in recorded state
            if interaction.state != "recorded":
                raise ValueError(
                    f"Interaction must be in recorded state, current state: {interaction.state}"
                )

            # Process based on interaction type
            await self._process_by_type(interaction)

            # Update analytics data (simulated)
            await self._update_analytics(interaction)

            # Update timestamp
            interaction.update_timestamp()

            self.logger.info(
                f"Interaction processed: {interaction.interaction_type} for subscriber {interaction.subscriber_id}"
            )

            return interaction

        except Exception as e:
            self.logger.error(
                f"Error processing interaction {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _process_by_type(self, interaction: Interaction) -> None:
        """
        Process interaction based on its type.

        Args:
            interaction: The interaction to process
        """
        if interaction.is_unsubscribe_interaction():
            await self._trigger_unsubscribe(interaction.subscriber_id)
        elif interaction.is_bounce() or interaction.is_complaint():
            await self._handle_negative_interaction(interaction)
        else:
            # For EMAIL_OPEN, LINK_CLICK, etc., just log for analytics
            self.logger.info(
                f"Positive interaction recorded: {interaction.interaction_type}"
            )

    async def _trigger_unsubscribe(self, subscriber_id: str) -> None:
        """
        Trigger unsubscribe process for subscriber.

        Args:
            subscriber_id: ID of the subscriber to unsubscribe
        """
        try:
            entity_service = self._get_entity_service()

            # Trigger unsubscribe transition on subscriber
            await entity_service.execute_transition(
                entity_id=subscriber_id,
                transition="transition_to_unsubscribed",
                entity_class="Subscriber",
                entity_version="1",
            )

            self.logger.info(f"Triggered unsubscribe for subscriber {subscriber_id}")

        except Exception as e:
            self.logger.error(
                f"Failed to trigger unsubscribe for subscriber {subscriber_id}: {str(e)}"
            )
            # Don't fail the interaction processing if unsubscribe fails

    async def _handle_negative_interaction(self, interaction: Interaction) -> None:
        """
        Handle negative interactions like bounces and complaints.

        Args:
            interaction: The negative interaction
        """
        self.logger.warning(
            f"Negative interaction recorded: {interaction.interaction_type} for subscriber {interaction.subscriber_id}"
        )

        # In a real implementation, this might:
        # - Update subscriber reputation score
        # - Temporarily suspend sending to this subscriber
        # - Alert administrators for complaints
        # For now, we just log the event

    async def _update_analytics(self, interaction: Interaction) -> None:
        """
        Update analytics data based on interaction (simulated).

        Args:
            interaction: The interaction to record in analytics
        """
        try:
            # In a real implementation, this would update analytics database
            # For now, we simulate by logging
            self.logger.info(
                f"Analytics updated: {interaction.interaction_type} "
                f"from IP {interaction.ip_address or 'unknown'} "
                f"at {interaction.interaction_date}"
            )

        except Exception as e:
            self.logger.error(f"Failed to update analytics: {str(e)}")
            # Don't fail processing if analytics update fails
