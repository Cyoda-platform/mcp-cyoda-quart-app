"""
CommentAnalysisRequestReportProcessor for Cyoda Client Application

Creates and generates analysis report from analyzed comments.
Initializes the CommentAnalysisReport entity with basic data.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Protocol, cast, runtime_checkable

from application.entity.comment_analysis_request.version_1.comment_analysis_request import (
    CommentAnalysisRequest,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


@runtime_checkable
class _HasId(Protocol):
    id: str


@runtime_checkable
class _HasMetadata(Protocol):
    metadata: _HasId


class _EntityService(Protocol):
    async def save(
        self, *, entity: Dict[str, Any], entity_class: str, entity_version: str
    ) -> _HasMetadata: ...

    async def execute_transition(
        self, *, entity_id: str, transition: str, entity_class: str, entity_version: str
    ) -> None: ...


class CommentAnalysisRequestReportProcessor(CyodaProcessor):
    """
    Processor for creating and generating analysis report.
    Creates CommentAnalysisReport entity with basic structure.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestReportProcessor",
            description="Create and generate analysis report",
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
        Create and generate analysis report according to functional requirements.

        Args:
            entity: The CommentAnalysisRequest in ANALYZING state
            **kwargs: Additional processing parameters

        Returns:
            The request entity with associated CommentAnalysisReport created
        """
        try:
            self.logger.info(
                f"Creating report for CommentAnalysisRequest {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisRequest for type-safe operations
            request = cast_entity(entity, CommentAnalysisRequest)

            # Create CommentAnalysisReport entity
            entity_service = self._get_entity_service()

            # Create basic report data structure
            # The actual report generation will be handled by CommentAnalysisReportGenerateProcessor
            report_data: Dict[str, Any] = {
                "analysisRequestId": request.technical_id,
                "totalComments": 0,  # Will be populated by generate processor
                "positiveComments": 0,
                "negativeComments": 0,
                "neutralComments": 0,
                "averageWordCount": 0.0,
                "topCommenterEmail": "unknown@example.com",  # Will be populated by generate processor
                "reportContent": "Report generation in progress...",  # Will be populated by generate processor
                "generatedAt": datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
            }

            # Save the new CommentAnalysisReport entity
            response = await entity_service.save(
                entity=report_data,
                entity_class="CommentAnalysisReport",
                entity_version="1",
            )

            # Execute transition to GENERATED state
            await entity_service.execute_transition(
                entity_id=response.metadata.id,
                transition="transition_to_generated",
                entity_class="CommentAnalysisReport",
                entity_version="1",
            )

            self.logger.info(
                f"Created CommentAnalysisReport {response.metadata.id} for request {request.technical_id}"
            )

            return request

        except Exception as e:
            self.logger.error(
                f"Error creating report for request {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
