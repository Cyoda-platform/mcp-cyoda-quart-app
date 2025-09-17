"""
EmailSentSuccessfullyCriterion for Cyoda Client Application

Checks if a Report email has been sent successfully
by verifying the delivery_status field according to workflow requirements.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.report.version_1.report import Report


class EmailSentSuccessfullyCriterion(CyodaCriteriaChecker):
    """
    Criterion that checks if Report email was sent successfully.
    """

    def __init__(self) -> None:
        super().__init__(
            name="email_sent_successfully",
            description="Checks if Report email was sent successfully",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the Report email was sent successfully.

        Args:
            entity: The CyodaEntity to check (expected to be Report)
            **kwargs: Additional criteria parameters

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            self.logger.info(
                f"Checking email send success for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Check if delivery_status is "sent"
            is_sent = report.is_email_sent()

            self.logger.info(
                f"Entity {report.technical_id} email send success check: {is_sent} "
                f"(delivery_status: {report.delivery_status})"
            )
            
            return is_sent

        except Exception as e:
            self.logger.error(
                f"Error checking email send success for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
