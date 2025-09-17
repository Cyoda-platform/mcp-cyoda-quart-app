"""
EmailSendFailedCriterion for Cyoda Client Application

Checks if a Report email sending has failed
by verifying the delivery_status field according to workflow requirements.
"""

from typing import Any

from application.entity.report.version_1.report import Report
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class EmailSendFailedCriterion(CyodaCriteriaChecker):
    """
    Criterion that checks if Report email sending failed.
    """

    def __init__(self) -> None:
        super().__init__(
            name="email_send_failed",
            description="Checks if Report email sending failed",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the Report email sending failed.

        Args:
            entity: The CyodaEntity to check (expected to be Report)
            **kwargs: Additional criteria parameters

        Returns:
            True if email sending failed, False otherwise
        """
        try:
            self.logger.info(
                f"Checking email send failure for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Check if delivery_status is "failed"
            is_failed = report.is_email_failed()

            self.logger.info(
                f"Entity {report.technical_id} email send failure check: {is_failed} "
                f"(delivery_status: {report.delivery_status})"
            )

            return is_failed

        except Exception as e:
            self.logger.error(
                f"Error checking email send failure for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
