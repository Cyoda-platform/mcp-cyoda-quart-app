"""
MailIsHappyCriterion for Cyoda Client Application

Determines if a mail entity should be processed as a happy mail based on the isHappy field.
"""

from typing import Any

from application.entity.mail import Mail
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class MailIsHappyCriterion(CyodaCriteriaChecker):
    """
    Criterion that determines if a mail entity should be processed as a happy mail.
    """

    def __init__(self) -> None:
        super().__init__(
            name="MailIsHappyCriterion",
            description="Determines if a mail entity should be processed as a happy mail based on the isHappy field",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the mail entity should be processed as a happy mail.

        Args:
            entity: The CyodaEntity to check (expected to be Mail)
            **kwargs: Additional criteria parameters

        Returns:
            True if the mail is marked as happy, False otherwise
        """
        try:
            self.logger.info(
                f"Checking if Mail entity {getattr(entity, 'technical_id', '<unknown>')} is happy"
            )

            # Cast the entity to Mail for type-safe operations
            mail_entity = cast_entity(entity, Mail)

            # Check if mail.isHappy equals true
            is_happy = mail_entity.is_happy is True

            self.logger.info(
                f"Mail entity {mail_entity.technical_id} isHappy check result: {is_happy}"
            )

            return is_happy

        except Exception as e:
            self.logger.error(
                f"Error checking Mail entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
