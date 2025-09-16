"""
CommentAnalysisRequestInitProcessor for Cyoda Client Application

Initializes the comment analysis request and validates input data.
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
    Processor for initializing CommentAnalysisRequest.
    Validates input data and sets initial timestamps.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestInitProcessor",
            description="Initializes comment analysis request and validates input data",
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
            The initialized entity with validated data and timestamps
        """
        try:
            self.logger.info(
                f"Initializing CommentAnalysisRequest {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisRequest for type-safe operations
            request_entity = cast_entity(entity, CommentAnalysisRequest)

            # Validate postId is positive integer (already validated by Pydantic)
            if request_entity.post_id <= 0:
                raise ValueError("Post ID must be a positive integer")

            # Validate recipientEmail is valid email format (already validated by Pydantic)
            if (
                not request_entity.recipient_email
                or "@" not in request_entity.recipient_email
            ):
                raise ValueError("Recipient email must be a valid email format")

            # Set requestedAt to current timestamp
            current_timestamp = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )
            request_entity.requested_at = current_timestamp

            # Set completedAt to null
            request_entity.completed_at = None

            # Set errorMessage to null
            request_entity.error_message = None

            # Update the entity timestamp
            request_entity.update_timestamp()

            self.logger.info(
                f"CommentAnalysisRequest {request_entity.technical_id} initialized successfully"
            )

            return request_entity

        except Exception as e:
            self.logger.error(
                f"Error initializing entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
