"""
CommentAnalysisRequestFailProcessor for Cyoda Client Application

Handles failure scenarios and sets error message.
"""

import logging
from typing import Any

from application.entity.comment_analysis_request.version_1.comment_analysis_request import (
    CommentAnalysisRequest,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CommentAnalysisRequestFailProcessor(CyodaProcessor):
    """
    Processor for handling CommentAnalysisRequest failures.
    Sets error message and logs failure details.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestFailProcessor",
            description="Handles failure scenarios and sets error message",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Handle failure scenarios according to functional requirements.

        Args:
            entity: The CommentAnalysisRequest with error information
            **kwargs: Additional processing parameters

        Returns:
            Updated CommentAnalysisRequest with error details
        """
        try:
            self.logger.info(
                f"Handling failure for CommentAnalysisRequest {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisRequest for type-safe operations
            request_entity = cast_entity(entity, CommentAnalysisRequest)

            # Set error message if not already set
            if not request_entity.error_message:
                request_entity.set_error("Unknown error occurred")

            # Log error details
            self.logger.error(
                f"CommentAnalysisRequest {request_entity.technical_id} failed: {request_entity.error_message}"
            )

            return request_entity

        except Exception as e:
            self.logger.error(
                f"Error handling failure for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
