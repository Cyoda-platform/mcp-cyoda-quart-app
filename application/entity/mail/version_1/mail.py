"""
Mail Entity for Cyoda Client Application

Represents an email message that can be either happy or gloomy in nature.
It contains the content type indicator and the list of recipients.
"""

import re
from typing import ClassVar, List

from pydantic import Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Mail(CyodaEntity):
    """
    Mail entity represents an email message that can be either happy or gloomy.

    The Mail entity uses the internal `entity.meta.state` to track its workflow state.
    The state is managed automatically by the system based on workflow transitions
    and cannot be directly modified by processors.
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Mail"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    isHappy: bool = Field(
        ...,
        description="Indicates whether the mail content is happy (true) or gloomy (false)",
    )
    mailList: List[str] = Field(
        ..., description="List of email addresses to send the mail to"
    )

    @field_validator("mailList")
    @classmethod
    def validate_mail_list(cls, v: List[str]) -> List[str]:
        """Validate that mailList is not empty and contains valid email addresses"""
        if not v:
            raise ValueError("mailList cannot be empty")

        # Email validation regex pattern
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

        for email in v:
            if not isinstance(email, str):
                raise ValueError(f"Email address must be a string, got {type(email)}")

            if not email.strip():
                raise ValueError("Email address cannot be empty or whitespace")

            if not email_pattern.match(email.strip()):
                raise ValueError(f"Invalid email address format: {email}")

        # Return cleaned email list (stripped of whitespace)
        return [email.strip() for email in v]

    @field_validator("isHappy")
    @classmethod
    def validate_is_happy(cls, v: bool) -> bool:
        """Validate that isHappy is a boolean value"""
        if not isinstance(v, bool):
            raise ValueError("isHappy must be a boolean value")
        return v
