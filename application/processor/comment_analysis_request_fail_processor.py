"""
CommentAnalysisRequestFailProcessor for Cyoda Client Application

Handles failure scenarios and sets error message.
Provides consistent error handling across the workflow.
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
    Processor for handling failure scenarios.
    Sets appropriate error messages when processing fails.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestFailProcessor",
            description="Handle failure scenarios and set error message",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Handle failure scenarios according to functional requirements.

        Args:
            entity: The CommentAnalysisRequest in any state that failed
            **kwargs: Additional processing parameters

        Returns:
            The request entity with error details set
        """
        try:
            self.logger.info(
                f"Handling failure for CommentAnalysisRequest {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisRequest for type-safe operations
            request = cast_entity(entity, CommentAnalysisRequest)

            # If errorMessage is null or empty, set a default error message
            if not request.error_message or len(request.error_message.strip()) == 0:
                current_state = request.state or "unknown"
                error_message = f"Process failed at {current_state} state"
                request.set_error(error_message)

                self.logger.warning(
                    f"Set default error message for request {request.technical_id}: {error_message}"
                )
            else:
                # Error message already exists, just update timestamp
                request.update_timestamp()

                self.logger.info(
                    f"Existing error message for request {request.technical_id}: {request.error_message}"
                )

            return request

        except Exception as e:
            self.logger.error(
                f"Error handling failure for request {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
