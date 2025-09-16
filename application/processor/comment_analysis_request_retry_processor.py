"""
CommentAnalysisRequestRetryProcessor for Cyoda Client Application

Resets the request for retry by clearing error state.
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
    Processor for retrying CommentAnalysisRequest.
    Clears error state and prepares for retry.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestRetryProcessor",
            description="Resets the request for retry by clearing error state",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Reset the request for retry according to functional requirements.

        Args:
            entity: The CommentAnalysisRequest in FAILED state
            **kwargs: Additional processing parameters

        Returns:
            CommentAnalysisRequest ready for retry
        """
        try:
            self.logger.info(
                f"Preparing retry for CommentAnalysisRequest {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisRequest for type-safe operations
            request_entity = cast_entity(entity, CommentAnalysisRequest)

            # Clear error state for retry
            request_entity.clear_error()

            self.logger.info(
                f"CommentAnalysisRequest {request_entity.technical_id} prepared for retry"
            )

            return request_entity

        except Exception as e:
            self.logger.error(
                f"Error preparing retry for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
