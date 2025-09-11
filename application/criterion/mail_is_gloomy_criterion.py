"""
MailIsGloomyCriterion for Cyoda Client Application

Determines if a mail entity should be processed as a gloomy mail.
"""

from typing import Any

from application.entity.mail import Mail
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class MailIsGloomyCriterion(CyodaCriteriaChecker):
    """
    Criterion that checks if a mail entity is gloomy (isHappy = false).
    Used in workflow transitions to route gloomy mails to the appropriate processor.
    """

    def __init__(self) -> None:
        super().__init__(
            name="MailIsGloomyCriterion",
            description="Checks if a mail entity is gloomy (isHappy = false)",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the mail entity is gloomy.

        Args:
            entity: The CyodaEntity to check (expected to be Mail)
            **kwargs: Additional criteria parameters

        Returns:
            True if the mail is gloomy (isHappy = false), False otherwise
        """
        try:
            self.logger.info(
                f"Checking if mail entity {getattr(entity, 'technical_id', '<unknown>')} is gloomy"
            )

            # Cast the entity to Mail for type-safe operations
            mail_entity = cast_entity(entity, Mail)

            # Check if the mail is gloomy (not happy)
            is_gloomy = not mail_entity.is_happy

            self.logger.info(
                f"Mail entity {mail_entity.technical_id} isGloomy check result: {is_gloomy}"
            )

            return is_gloomy

        except Exception as e:
            self.logger.error(
                f"Error checking if mail entity {getattr(entity, 'technical_id', '<unknown>')} is gloomy: {str(e)}"
            )
            return False
