"""
CommentAnalysisReportSendFailedCriterion for Cyoda Client Application

Checks if email sending failed for the report.
Used in transition from GENERATED to FAILED_TO_SEND state.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from application.entity.comment_analysis_report.version_1.comment_analysis_report import (
    CommentAnalysisReport,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class CommentAnalysisReportSendFailedCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if email sending failed for the report.
    Returns True if email service returned failure or exception occurred.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisReportSendFailedCriterion",
            description="Check if email sending failed for the report",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    def _parse_iso_timestamp(self, timestamp_str: str) -> datetime | None:
        """Parse ISO timestamp string to datetime object"""
        try:
            # Handle both Z and +00:00 timezone formats
            if timestamp_str.endswith("Z"):
                timestamp_str = timestamp_str[:-1] + "+00:00"
            return datetime.fromisoformat(timestamp_str)
        except (ValueError, TypeError):
            return None

    async def evaluate(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if email sending failed according to functional requirements.

        Args:
            entity: The CommentAnalysisReport to evaluate
            **kwargs: Additional evaluation parameters

        Returns:
            True if email sending was attempted but failed
        """
        try:
            self.logger.debug(
                f"Evaluating email send failure for CommentAnalysisReport {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisReport for type-safe operations
            report = cast_entity(entity, CommentAnalysisReport)

            # Check if email sending was attempted but failed
            # If sentAt is null and enough time has passed since generation, consider it failed
            if report.sent_at is None and report.generated_at is not None:
                generated_at = self._parse_iso_timestamp(report.generated_at)
                if generated_at:
                    current_time = datetime.now(timezone.utc)
                    time_since_generation = current_time - generated_at

                    # If more than 2 minutes have passed since generation without sending, consider it failed
                    timeout_threshold = timedelta(minutes=2)

                    if time_since_generation > timeout_threshold:
                        self.logger.debug(
                            f"Report {report.technical_id} not sent after {time_since_generation.total_seconds():.0f} seconds - send failed"
                        )
                        return True

            self.logger.debug(
                f"CommentAnalysisReport {report.technical_id}: Email send failure not detected"
            )

            return False

        except Exception as e:
            self.logger.error(
                f"Error evaluating email send failure criterion for report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Return True on error to trigger failure transition
            return True
