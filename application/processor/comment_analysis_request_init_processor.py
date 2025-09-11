"""
CommentAnalysisRequestInitProcessor for Cyoda Client Application

Initializes the analysis request and validates input data.
Sets timestamps and prepares the request for processing.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.comment_analysis_request.version_1.comment_analysis_request import (
    CommentAnalysisRequest,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CommentAnalysisRequestInitProcessor(CyodaProcessor):
    """
    Processor for initializing CommentAnalysisRequest entities.
    Validates input data and sets initial timestamps.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestInitProcessor",
            description="Initialize the analysis request and validate input data",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Initialize the CommentAnalysisRequest according to functional requirements.

        Args:
            entity: The CommentAnalysisRequest to initialize
            **kwargs: Additional processing parameters

        Returns:
            The initialized entity with timestamps set
        """
        try:
            self.logger.info(
                f"Initializing CommentAnalysisRequest {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisRequest for type-safe operations
            request = cast_entity(entity, CommentAnalysisRequest)

            # Validate postId is positive integer (already done by Pydantic validator)
            if request.post_id <= 0:
                raise ValueError("Post ID must be a positive integer")

            # Validate requestedBy is valid email format (already done by Pydantic validator)
            if not request.requested_by or "@" not in request.requested_by:
                raise ValueError("Requested by must be a valid email format")

            # Set createdAt to current timestamp if not already set
            if not request.created_at:
                request.created_at = (
                    datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                )

            # Set completedAt to null (ensure it's cleared)
            request.completed_at = None

            # Set errorMessage to null (ensure it's cleared)
            request.error_message = None

            # Update timestamp
            request.update_timestamp()

            self.logger.info(
                f"CommentAnalysisRequest {request.technical_id} initialized successfully for post {request.post_id}"
            )

            return request

        except Exception as e:
            self.logger.error(
                f"Error initializing CommentAnalysisRequest {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
