"""
ValidateCommentProcessor for Cyoda Client Application

Handles the validation of comment data integrity and format.
Validates comment data as specified in functional requirements.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.comment.version_1.comment import Comment


class ValidateCommentProcessor(CyodaProcessor):
    """
    Processor for Comment that handles validation of comment data.
    Validates comment data integrity and format according to business rules.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ValidateCommentProcessor",
            description="Validates comment data integrity and format",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Comment entity for validation.

        Args:
            entity: The Comment entity to validate
            **kwargs: Additional processing parameters

        Returns:
            The validated entity
        """
        try:
            self.logger.info(
                f"Validating Comment {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Comment for type-safe operations
            comment = cast_entity(entity, Comment)

            # Perform validation checks
            validation_errors = []
            
            # Validate content
            if not comment.content or len(comment.content.strip()) == 0:
                validation_errors.append("Comment content is empty")
            elif len(comment.content) < 5:
                validation_errors.append("Comment content is too short (minimum 5 characters)")
            elif len(comment.content) > 10000:
                validation_errors.append("Comment content is too long (maximum 10000 characters)")
            
            # Validate author
            if not comment.author or len(comment.author.strip()) == 0:
                validation_errors.append("Comment author is missing")
            elif len(comment.author) > 100:
                validation_errors.append("Comment author name is too long")
            
            # Validate timestamp format
            if not comment.timestamp:
                validation_errors.append("Comment timestamp is missing")
            else:
                try:
                    from datetime import datetime
                    datetime.fromisoformat(comment.timestamp.replace('Z', '+00:00'))
                except ValueError:
                    validation_errors.append("Comment timestamp format is invalid")
            
            # Validate source API
            if not comment.source_api or len(comment.source_api.strip()) == 0:
                validation_errors.append("Source API is missing")
            
            # Validate external ID
            if not comment.external_id or len(comment.external_id.strip()) == 0:
                validation_errors.append("External ID is missing")
            
            # Check for profanity or inappropriate content (basic check)
            if self._contains_inappropriate_content(comment.content):
                validation_errors.append("Comment contains inappropriate content")
            
            # If there are validation errors, raise an exception
            if validation_errors:
                error_message = f"Validation failed: {'; '.join(validation_errors)}"
                self.logger.error(f"Comment validation failed: {error_message}")
                raise ValueError(error_message)
            
            # Set validation status to validated
            comment.set_validation_status("validated")

            self.logger.info(
                f"Comment {comment.technical_id} validated successfully"
            )

            return comment

        except Exception as e:
            self.logger.error(
                f"Error validating comment {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _contains_inappropriate_content(self, content: str) -> bool:
        """
        Basic check for inappropriate content.
        
        In a real implementation, this would use more sophisticated content filtering.
        
        Args:
            content: The comment content to check
            
        Returns:
            True if inappropriate content is detected, False otherwise
        """
        # Basic profanity filter (simplified for demo)
        inappropriate_words = [
            "spam", "scam", "fake", "bot", "malware", "virus"
        ]
        
        content_lower = content.lower()
        for word in inappropriate_words:
            if word in content_lower:
                return True
        
        # Check for excessive caps (potential spam)
        if len(content) > 20 and content.isupper():
            return True
        
        # Check for excessive repetition
        words = content.split()
        if len(words) > 5:
            unique_words = set(words)
            if len(unique_words) / len(words) < 0.3:  # Less than 30% unique words
                return True
        
        return False
