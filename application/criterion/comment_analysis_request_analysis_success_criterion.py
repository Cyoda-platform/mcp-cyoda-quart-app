"""
CommentAnalysisRequestAnalysisSuccessCriterion for Cyoda Client Application

Checks if comment analysis was completed successfully.
"""

from typing import Any, Dict

from application.entity.analysis_report.version_1.analysis_report import AnalysisReport
from application.entity.comment_analysis_request.version_1.comment_analysis_request import (
    CommentAnalysisRequest,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service


class CommentAnalysisRequestAnalysisSuccessCriterion(CyodaCriteriaChecker):
    """
    Criterion to check if comment analysis was completed successfully.
    Condition: Analysis report exists and is properly generated.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestAnalysisSuccessCriterion",
            description="Checks if comment analysis was completed successfully",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if comment analysis was completed successfully according to functional requirements.

        Args:
            entity: The CyodaEntity to check (expected to be CommentAnalysisRequest)
            **kwargs: Additional criteria parameters

        Returns:
            True if analysis report exists and is properly generated, False otherwise
        """
        try:
            self.logger.info(
                f"Checking analysis success for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisRequest for type-safe operations
            request_entity = cast_entity(entity, CommentAnalysisRequest)

            # Check if error message is set
            if request_entity.error_message is not None:
                self.logger.info(
                    f"Entity {request_entity.technical_id} has error message: {request_entity.error_message}"
                )
                return False

            # Find analysis report by request ID
            report = await self._find_analysis_report_by_request_id(
                request_entity.technical_id or request_entity.entity_id or ""
            )

            if report is None:
                self.logger.info(
                    f"Entity {request_entity.technical_id} has no analysis report"
                )
                return False

            # Check if report is properly generated
            if report.total_comments <= 0:
                self.logger.info(
                    f"Entity {request_entity.technical_id} has invalid total comments: {report.total_comments}"
                )
                return False

            if report.generated_at is None:
                self.logger.info(
                    f"Entity {request_entity.technical_id} has no generated_at timestamp"
                )
                return False

            self.logger.info(
                f"Entity {request_entity.technical_id} has valid analysis report - analysis successful"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error checking analysis success for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    async def _find_analysis_report_by_request_id(
        self, request_id: str
    ) -> AnalysisReport | None:
        """
        Find analysis report by request ID.

        Args:
            request_id: The analysis request ID

        Returns:
            AnalysisReport entity or None if not found
        """
        try:
            entity_service = get_entity_service()

            # Build search condition
            builder = SearchConditionRequest.builder()
            builder.equals("analysisRequestId", request_id)
            condition = builder.build()

            # Search for analysis report
            results = await entity_service.search(
                entity_class=AnalysisReport.ENTITY_NAME,
                condition=condition,
                entity_version=str(AnalysisReport.ENTITY_VERSION),
            )

            if not results:
                return None

            # Convert first result to AnalysisReport entity
            report_data = results[0].data
            if hasattr(report_data, "model_dump"):
                report_dict: Dict[str, Any] = report_data.model_dump()
            else:
                # If it's already a dict, use it directly
                report_dict = (
                    dict(report_data)
                    if not isinstance(report_data, dict)
                    else report_data
                )

            return AnalysisReport(**report_dict)

        except Exception as e:
            self.logger.warning(
                f"Failed to find analysis report for request {request_id}: {str(e)}"
            )
            return None
