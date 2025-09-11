"""
MailIsHappyCriterion for Cyoda Client Application

Determines if a mail entity should be processed as a happy mail.
"""

from typing import Any

from application.entity.mail import Mail
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class MailIsHappyCriterion(CyodaCriteriaChecker):
    """
    Criterion that checks if a mail entity is happy (isHappy = true).
    Used in workflow transitions to route happy mails to the appropriate processor.
    """

    def __init__(self) -> None:
        super().__init__(
            name="MailIsHappyCriterion",
            description="Checks if a mail entity is happy (isHappy = true)",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the mail entity is happy.

        Args:
            entity: The CyodaEntity to check (expected to be Mail)
            **kwargs: Additional criteria parameters

        Returns:
            True if the mail is happy (isHappy = true), False otherwise
        """
        try:
            self.logger.info(
                f"Checking if mail entity {getattr(entity, 'technical_id', '<unknown>')} is happy"
            )

            # Cast the entity to Mail for type-safe operations
            mail_entity = cast_entity(entity, Mail)

            # Check if the mail is happy
            is_happy = mail_entity.is_happy

            self.logger.info(
                f"Mail entity {mail_entity.technical_id} isHappy check result: {is_happy}"
            )

            return is_happy

        except Exception as e:
            self.logger.error(
                f"Error checking if mail entity {getattr(entity, 'technical_id', '<unknown>')} is happy: {str(e)}"
            )
            return False
