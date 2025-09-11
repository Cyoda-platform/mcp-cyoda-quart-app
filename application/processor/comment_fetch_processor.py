"""
CommentFetchProcessor for Cyoda Client Application

Processes and validates fetched comment data.
Ensures comment data integrity and calculates word count.
"""

import logging
from typing import Any

from application.entity.comment.version_1.comment import Comment
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CommentFetchProcessor(CyodaProcessor):
    """
    Processor for processing and validating fetched comment data.
    Ensures data integrity and calculates metrics.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentFetchProcessor",
            description="Process and validate fetched comment data",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Comment entity according to functional requirements.

        Args:
            entity: The Comment entity with basic data from API
            **kwargs: Additional processing parameters

        Returns:
            The comment entity ready for analysis
        """
        try:
            self.logger.info(
                f"Processing Comment {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Comment for type-safe operations
            comment = cast_entity(entity, Comment)

            # Validate comment.email is valid email format (already done by Pydantic validator)
            if not comment.email or "@" not in comment.email:
                raise ValueError("Comment email must be a valid email format")

            # Validate comment.body is not null or empty (already done by Pydantic validator)
            if not comment.body or len(comment.body.strip()) == 0:
                raise ValueError("Comment body must be non-empty")

            # If comment.wordCount is null, calculate it
            if comment.word_count is None:
                comment.set_word_count()
                self.logger.debug(
                    f"Calculated word count for Comment {comment.technical_id}: {comment.word_count}"
                )

            # Update timestamp
            comment.update_timestamp()

            self.logger.info(
                f"Comment {comment.technical_id} processed successfully - word count: {comment.word_count}"
            )

            return comment

        except Exception as e:
            self.logger.error(
                f"Error processing Comment {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
