"""
EmailSendingFailedCriterion for Cyoda Client Application

Checks if email sending has failed.
Validates that email was not sent successfully as specified in functional requirements.
"""

import logging
from typing import Any

from application.entity.report.version_1.report import Report
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriterion, CyodaEntity


class EmailSendingFailedCriterion(CyodaCriterion):
    """
    Criterion for Report that checks if email sending has failed.
    Validates that email_sent_at timestamp is missing and status is not "sent".
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailSendingFailedCriterion",
            description="Checks if email sending has failed due to missing sent timestamp or incorrect status",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the Report entity email sending has failed.

        Args:
            entity: The Report entity to check
            **kwargs: Additional parameters

        Returns:
            True if email sending has failed, False otherwise
        """
        try:
            self.logger.info(
                f"Checking email sending failure for Report {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Check if email_sent_at timestamp is missing
            missing_sent_at = report.email_sent_at is None

            # Check if status is not "sent"
            status_not_sent = report.status != "sent"

            # Email sending has failed if both conditions are true
            has_failed = missing_sent_at and status_not_sent

            self.logger.info(
                f"Report {report.technical_id} email sending failure check: {has_failed} "
                f"(missing sent_at: {missing_sent_at}, status not sent: {status_not_sent}, "
                f"current status: {report.status})"
            )

            return has_failed

        except Exception as e:
            self.logger.error(
                f"Error checking email sending failure for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return True  # Assume failure if we can't check properly
