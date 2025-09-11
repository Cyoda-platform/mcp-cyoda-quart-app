"""
EmailRetryCriterion for Cyoda Client Application

Checks if a failed email delivery can be retried.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Optional, Protocol, cast

from application.entity.emaildelivery.version_1.emaildelivery import EmailDelivery
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from services.services import get_entity_service


class _EntityService(Protocol):
    async def get_by_id(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> Optional[Any]: ...


class EmailRetryCriterion(CyodaCriteriaChecker):
    """Criterion for validating if a failed email delivery can be retried."""

    def __init__(self) -> None:
        super().__init__(
            name="EmailRetryCriterion",
            description="Checks if a failed email delivery can be retried",
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
        """Check if the email delivery can be retried."""
        try:
            email_delivery = cast_entity(entity, EmailDelivery)

            # Check if email delivery is in FAILED state
            if email_delivery.state != "failed":
                self.logger.warning(
                    f"Email delivery must be in FAILED state, current: {email_delivery.state}"
                )
                return False

            # Check if delivery attempts is less than 3
            if email_delivery.delivery_attempts >= 3:
                self.logger.warning(
                    f"Maximum retry attempts (3) exceeded: {email_delivery.delivery_attempts}"
                )
                return False

            # Check if at least 30 minutes have passed since last attempt
            if not email_delivery.last_attempt_date:
                self.logger.warning("No previous attempt date found")
                return False

            if not self._has_enough_time_passed(email_delivery.last_attempt_date):
                self.logger.warning("Must wait at least 30 minutes before retry")
                return False

            # Check if subscriber is still active
            if not await self._is_subscriber_active(email_delivery.subscriber_id):
                self.logger.warning("Subscriber is no longer active")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error validating email retry: {str(e)}")
            return False

    def _has_enough_time_passed(self, last_attempt_date: str) -> bool:
        """Check if at least 30 minutes have passed since last attempt."""
        try:
            last_attempt = datetime.fromisoformat(
                last_attempt_date.replace("Z", "+00:00")
            )
            now = datetime.now(timezone.utc)
            minutes_passed = (now - last_attempt).total_seconds() / 60
            return minutes_passed >= 30
        except Exception:
            return False

    async def _is_subscriber_active(self, subscriber_id: str) -> bool:
        """Check if subscriber is still active."""
        entity_service = self._get_entity_service()

        try:
            subscriber = await entity_service.get_by_id(
                entity_id=subscriber_id, entity_class="Subscriber", entity_version="1"
            )

            if not subscriber:
                return False

            if hasattr(subscriber, "data"):
                return subscriber.data.get("isActive", False)

            return False

        except Exception as e:
            self.logger.warning(f"Error checking subscriber status: {str(e)}")
            return False
