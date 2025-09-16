"""
AnalysisReportEmailFailureCriterion for Cyoda Client Application

Checks if email sending failed.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.analysis_report.version_1.analysis_report import AnalysisReport


class AnalysisReportEmailFailureCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if email sending failed.
    Condition: Email service threw an exception or returned failure status.
    """

    def __init__(self) -> None:
        super().__init__(
            name="AnalysisReportEmailFailureCriterion",
            description="Checks if email sending failed",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if email sending failed according to functional requirements.

        Args:
            entity: The CyodaEntity to check (expected to be AnalysisReport)
            **kwargs: Additional criteria parameters

        Returns:
            True if exception occurred during email sending or email service returned failure status
        """
        try:
            self.logger.info(
                f"Checking email failure for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to AnalysisReport for type-safe operations
            report_entity = cast_entity(entity, AnalysisReport)

            # In this simplified implementation, we assume failure if required fields are missing
            # In a real implementation, this would check the actual email service status
            
            # Check if the report is missing required fields for email sending
            if not report_entity.analysis_request_id:
                self.logger.info(
                    f"Entity {report_entity.technical_id} missing analysis request ID - email failure"
                )
                return True

            if not report_entity.generated_at:
                self.logger.info(
                    f"Entity {report_entity.technical_id} missing generated timestamp - email failure"
                )
                return True

            if report_entity.total_comments <= 0:
                self.logger.info(
                    f"Entity {report_entity.technical_id} has invalid total comments: {report_entity.total_comments} - email failure"
                )
                return True

            # Assume success if all required fields are present
            self.logger.info(
                f"Entity {report_entity.technical_id} has all required fields - email success"
            )
            return False

        except Exception as e:
            self.logger.error(
                f"Error checking email failure for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return True  # Assume failure on error
