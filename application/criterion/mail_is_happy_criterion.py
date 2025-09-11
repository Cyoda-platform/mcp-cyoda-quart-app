"""
MailIsHappyCriterion for Cyoda Client Application

Determines if a mail entity should be processed as a happy mail by checking the isHappy field.
"""

from typing import Any

from application.entity.mail import Mail
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class MailIsHappyCriterion(CyodaCriteriaChecker):
    """
    Criterion that determines if a mail entity should be processed as a happy mail.

    Used in the workflow transition from PENDING to HAPPY_SENT to ensure only
    happy mails are processed by the MailSendHappyMailProcessor.
    """

    def __init__(self) -> None:
        super().__init__(
            name="MailIsHappyCriterion",
            description="Determines if a mail entity should be processed as a happy mail",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the mail entity should be processed as a happy mail.

        Args:
            entity: The CyodaEntity to check (expected to be Mail)
            **kwargs: Additional criteria parameters

        Returns:
            True if the mail is marked as happy (isHappy=true), False otherwise
        """
        try:
            self.logger.info(
                f"Checking if entity {getattr(entity, 'technical_id', '<unknown>')} is a happy mail"
            )

            # Cast the entity to Mail for type-safe operations
            mail_entity = cast_entity(entity, Mail)

            # Validate that isHappy field is present and is a boolean
            if not hasattr(mail_entity, "isHappy"):
                self.logger.warning(
                    f"Entity {mail_entity.technical_id} does not have isHappy field"
                )
                return False

            if not isinstance(mail_entity.isHappy, bool):
                self.logger.warning(
                    f"Entity {mail_entity.technical_id} has invalid isHappy field type: {type(mail_entity.isHappy)}"
                )
                return False

            # Check if mail.isHappy equals true
            is_happy = mail_entity.isHappy is True

            self.logger.info(
                f"Entity {mail_entity.technical_id} happy mail check result: {is_happy}"
            )

            return is_happy

        except Exception as e:
            self.logger.error(
                f"Error checking happy mail criteria for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
