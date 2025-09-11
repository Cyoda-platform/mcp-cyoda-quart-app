"""
CommentAnalysisRequestRetryProcessor for Cyoda Client Application

Resets request for retry by clearing error state.
Prepares failed requests for reprocessing.
"""

import logging
from typing import Any

from application.entity.comment_analysis_request.version_1.comment_analysis_request import (
    CommentAnalysisRequest,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CommentAnalysisRequestRetryProcessor(CyodaProcessor):
    """
    Processor for resetting failed requests for retry.
    Clears error state and prepares for reprocessing.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestRetryProcessor",
            description="Reset request for retry by clearing error state",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Reset request for retry according to functional requirements.

        Args:
            entity: The CommentAnalysisRequest in FAILED state
            **kwargs: Additional processing parameters

        Returns:
            The request entity ready for retry
        """
        try:
            self.logger.info(
                f"Resetting CommentAnalysisRequest {getattr(entity, 'technical_id', '<unknown>')} for retry"
            )

            # Cast the entity to CommentAnalysisRequest for type-safe operations
            request = cast_entity(entity, CommentAnalysisRequest)

            # Clear error state for retry
            request.clear_error()  # This sets errorMessage = None and completedAt = None

            self.logger.info(
                f"CommentAnalysisRequest {request.technical_id} reset for retry - error state cleared"
            )

            return request

        except Exception as e:
            self.logger.error(
                f"Error resetting request {getattr(entity, 'technical_id', '<unknown>')} for retry: {str(e)}"
            )
            raise
