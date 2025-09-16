"""
CommentAnalysisRequestReportProcessor for Cyoda Client Application

Triggers the report sending process.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from common.service.entity_service import SearchConditionRequest
from application.entity.comment_analysis_request.version_1.comment_analysis_request import CommentAnalysisRequest
from application.entity.analysis_report.version_1.analysis_report import AnalysisReport
from services.services import get_entity_service


class CommentAnalysisRequestReportProcessor(CyodaProcessor):
    """
    Processor for triggering the report sending process.
    Updates the AnalysisReport to SENDING state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestReportProcessor",
            description="Triggers the report sending process",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Trigger the report sending process according to functional requirements.

        Args:
            entity: The CommentAnalysisRequest with associated AnalysisReport
            **kwargs: Additional processing parameters

        Returns:
            The entity (AnalysisReport transitions to SENDING)
        """
        try:
            self.logger.info(
                f"Triggering report sending for CommentAnalysisRequest {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisRequest for type-safe operations
            request_entity = cast_entity(entity, CommentAnalysisRequest)

            # Find the analysis report by request ID
            report = await self._find_analysis_report_by_request_id(
                request_entity.technical_id or request_entity.entity_id or ""
            )

            if not report:
                self.logger.error(f"No analysis report found for request {request_entity.technical_id}")
                raise Exception("Analysis report not found")

            # Update report with transition to SENDING state
            entity_service = get_entity_service()
            
            # Get the report's technical ID
            report_id = report.technical_id or report.entity_id
            if not report_id:
                raise Exception("Report ID not found")

            # Update the report with transition to SENDING
            report_data = report.model_dump(by_alias=True)
            await entity_service.update(
                entity_id=report_id,
                entity=report_data,
                entity_class=AnalysisReport.ENTITY_NAME,
                transition="transition_to_sending",
                entity_version=str(AnalysisReport.ENTITY_VERSION),
            )

            self.logger.info(
                f"Updated AnalysisReport {report_id} to SENDING state for request {request_entity.technical_id}"
            )

            return request_entity

        except Exception as e:
            self.logger.error(
                f"Error triggering report sending for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _find_analysis_report_by_request_id(self, request_id: str) -> AnalysisReport | None:
        """
        Find analysis report by request ID.

        Args:
            request_id: The analysis request ID

        Returns:
            AnalysisReport entity or None if not found
        """
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
        try:
            report_data = results[0].data
            if hasattr(report_data, 'model_dump'):
                report_dict = report_data.model_dump()
            else:
                report_dict = report_data

            return AnalysisReport(**report_dict)
        except Exception as e:
            self.logger.warning(f"Failed to parse analysis report data: {str(e)}")
            return None
