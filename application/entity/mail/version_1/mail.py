"""
Mail Entity for Cyoda Client Application

Represents an email that can be either happy or gloomy in nature.
It contains information about the happiness state and the list of recipients.
"""

from typing import ClassVar, List

from pydantic import Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Mail(CyodaEntity):
    """
    Mail entity represents an email that can be either happy or gloomy in nature.
    It contains information about the happiness state and the list of recipients.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> pending -> happy_sent/gloomy_sent -> [*]
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Mail"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    is_happy: bool = Field(
        ...,
        alias="isHappy",
        description="Indicates whether the mail content is happy (true) or gloomy (false)",
    )
    mail_list: List[str] = Field(
        ..., alias="mailList", description="List of email addresses to send the mail to"
    )

    @field_validator("mail_list")
    @classmethod
    def validate_mail_list(cls, v: List[str]) -> List[str]:
        """Validate that mail list is not empty and contains valid email addresses"""
        if not v:
            raise ValueError("mailList cannot be empty")

        # Basic email validation
        import re

        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

        for email in v:
            if not email or not isinstance(email, str):
                raise ValueError("All email addresses must be non-empty strings")
            if not email_pattern.match(email.strip()):
                raise ValueError(f"Invalid email address: {email}")

        return [email.strip() for email in v]

    def is_happy_mail(self) -> bool:
        """Check if this is a happy mail"""
        return self.is_happy

    def is_gloomy_mail(self) -> bool:
        """Check if this is a gloomy mail"""
        return not self.is_happy

    def get_recipient_count(self) -> int:
        """Get the number of recipients"""
        return len(self.mail_list)
