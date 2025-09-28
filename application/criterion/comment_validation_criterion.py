"""
CommentValidationCriterion for Cyoda Client Application

Validates that a Comment entity meets all required business rules before it can
proceed to the analysis stage.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.comment.version_1.comment import Comment


class CommentValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Comment entity that checks all business rules
    before the entity can proceed to analysis stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentValidationCriterion",
            description="Validates Comment business rules and data consistency",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the comment meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be Comment)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating comment {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Comment for type-safe operations
            comment = cast_entity(entity, Comment)

            # Validate required fields
            if not comment.body or len(comment.body.strip()) == 0:
                self.logger.warning(
                    f"Comment {comment.technical_id} has empty body"
                )
                return False

            if len(comment.body) > 5000:
                self.logger.warning(
                    f"Comment {comment.technical_id} body too long: {len(comment.body)} characters"
                )
                return False

            # Validate email format
            if not comment.email or "@" not in comment.email:
                self.logger.warning(
                    f"Comment {comment.technical_id} has invalid email: {comment.email}"
                )
                return False

            # Validate name field
            if not comment.name or len(comment.name.strip()) == 0:
                self.logger.warning(
                    f"Comment {comment.technical_id} has empty name"
                )
                return False

            # Validate post_id and comment_id are positive
            if comment.post_id <= 0:
                self.logger.warning(
                    f"Comment {comment.technical_id} has invalid post_id: {comment.post_id}"
                )
                return False

            if comment.comment_id <= 0:
                self.logger.warning(
                    f"Comment {comment.technical_id} has invalid comment_id: {comment.comment_id}"
                )
                return False

            self.logger.info(
                f"Comment {comment.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating comment {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
