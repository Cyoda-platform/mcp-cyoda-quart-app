# entity/mail/version_1/mail.py

"""
Mail Entity for Cyoda Client Application

Represents an email message that can be either happy or gloomy in nature.
It contains information about the happiness state and the list of recipients.
"""

from typing import Any, ClassVar, Dict, List

from pydantic import Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Mail(CyodaEntity):
    """
    Mail entity represents an email message that can be either happy or gloomy.

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
        """Validate mail list contains valid email addresses"""
        if not v or len(v) == 0:
            raise ValueError("Mail list must not be empty")

        # Basic email validation
        import re

        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

        for email in v:
            if not email or not isinstance(email, str):
                raise ValueError("All email addresses must be non-empty strings")
            if not email_pattern.match(email.strip()):
                raise ValueError(f"Invalid email address format: {email}")

        return [email.strip() for email in v]

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        return data

    class Config:
        """Pydantic configuration"""

        populate_by_name = True
        use_enum_values = True
        validate_assignment = True
        extra = "allow"
