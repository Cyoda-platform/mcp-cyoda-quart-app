"""
CommentAnalysisRequestCompleteProcessor for Cyoda Client Application

Marks the analysis request as completed.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.comment_analysis_request.version_1.comment_analysis_request import CommentAnalysisRequest


class CommentAnalysisRequestCompleteProcessor(CyodaProcessor):
    """
    Processor for marking CommentAnalysisRequest as completed.
    Sets the completedAt timestamp.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestCompleteProcessor",
            description="Marks the analysis request as completed",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Mark the analysis request as completed according to functional requirements.

        Args:
            entity: The CommentAnalysisRequest with successfully sent report
            **kwargs: Additional processing parameters

        Returns:
            Updated CommentAnalysisRequest with completedAt timestamp
        """
        try:
            self.logger.info(
                f"Completing CommentAnalysisRequest {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisRequest for type-safe operations
            request_entity = cast_entity(entity, CommentAnalysisRequest)

            # Set completedAt to current timestamp
            request_entity.set_completed()

            self.logger.info(
                f"CommentAnalysisRequest {request_entity.technical_id} marked as completed"
            )

            return request_entity

        except Exception as e:
            self.logger.error(
                f"Error completing entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
