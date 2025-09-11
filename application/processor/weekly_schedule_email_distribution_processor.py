"""
WeeklyScheduleEmailDistributionProcessor for Cyoda Client Application

Distributes emails to all active subscribers.
"""

import logging
from typing import Any, Optional, Protocol, cast

from application.entity.weeklyschedule.version_1.weeklyschedule import WeeklySchedule
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class _EntityService(Protocol):
    async def search(
        self, entity_class: str, condition: Any, entity_version: str = "1"
    ) -> list[Any]: ...

    async def save(
        self, *, entity: dict[str, Any], entity_class: str, entity_version: str
    ) -> Any: ...

    async def execute_transition(
        self, *, entity_id: str, transition: str, entity_class: str, entity_version: str
    ) -> None: ...


class WeeklyScheduleEmailDistributionProcessor(CyodaProcessor):
    """Processor for distributing emails to all active subscribers."""

    def __init__(self) -> None:
        super().__init__(
            name="WeeklyScheduleEmailDistributionProcessor",
            description="Distributes emails to all active subscribers",
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
        """Process email distribution for weekly schedule."""
        try:
            weekly_schedule = cast_entity(entity, WeeklySchedule)

            if weekly_schedule.state != "fact_assigned":
                raise ValueError(
                    f"Weekly schedule must be in fact_assigned state, current: {weekly_schedule.state}"
                )

            if not weekly_schedule.cat_fact_id:
                raise ValueError("Cat fact must be assigned before email distribution")

            # Get active subscribers
            active_subscribers = await self._get_active_subscribers()

            emails_sent = 0
            emails_failed = 0

            # Create email deliveries for all subscribers
            for subscriber in active_subscribers:
                try:
                    await self._create_email_delivery(
                        subscriber, weekly_schedule.cat_fact_id
                    )
                    emails_sent += 1
                except Exception as e:
                    self.logger.error(
                        f"Failed to create email delivery for subscriber {subscriber}: {str(e)}"
                    )
                    emails_failed += 1

            # Update email counts
            weekly_schedule.update_email_counts(emails_sent, emails_failed)

            # Trigger cat fact distribution processor
            if weekly_schedule.cat_fact_id:
                await self._trigger_cat_fact_distribution(weekly_schedule.cat_fact_id)

            self.logger.info(
                f"Email distribution completed: {emails_sent} sent, {emails_failed} failed"
            )
            return weekly_schedule

        except Exception as e:
            self.logger.error(f"Error processing email distribution: {str(e)}")
            raise

    async def _get_active_subscribers(self) -> list[Any]:
        """Get all active subscribers."""
        entity_service = self._get_entity_service()

        try:
            subscribers = await entity_service.search(
                entity_class="Subscriber",
                condition={"isActive": True, "state": "active"},
                entity_version="1",
            )
            return subscribers
        except Exception as e:
            self.logger.error(f"Error getting active subscribers: {str(e)}")
            return []

    async def _create_email_delivery(self, subscriber: Any, cat_fact_id: str) -> None:
        """Create email delivery for subscriber and cat fact."""
        entity_service = self._get_entity_service()

        subscriber_id = (
            subscriber.get_id() if hasattr(subscriber, "get_id") else str(subscriber)
        )

        email_delivery_data = {
            "subscriberId": subscriber_id,
            "catFactId": cat_fact_id,
            "deliveryAttempts": 0,
        }

        await entity_service.save(
            entity=email_delivery_data, entity_class="EmailDelivery", entity_version="1"
        )

    async def _trigger_cat_fact_distribution(self, cat_fact_id: str) -> None:
        """Trigger cat fact distribution processor."""
        entity_service = self._get_entity_service()

        try:
            await entity_service.execute_transition(
                entity_id=cat_fact_id,
                transition="transition_to_sent",
                entity_class="CatFact",
                entity_version="1",
            )
        except Exception as e:
            self.logger.error(f"Failed to trigger cat fact distribution: {str(e)}")
