# entity/email_campaign/version_1/email_campaign.py

"""
EmailCampaign Entity for Cat Facts Subscription System

Represents an email campaign that distributes cat facts to subscribers.
Manages campaign scheduling, delivery tracking, and performance metrics.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class EmailCampaign(CyodaEntity):
    """
    EmailCampaign entity represents an email distribution campaign.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> scheduled -> sending -> completed -> analyzed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "EmailCampaign"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    campaign_name: str = Field(..., description="Name of the email campaign")
    cat_fact_id: str = Field(..., description="ID of the cat fact to send")
    
    # Campaign scheduling
    scheduled_at: Optional[str] = Field(
        default=None,
        description="Timestamp when campaign is scheduled to send (ISO 8601 format)"
    )
    campaign_type: str = Field(
        default="weekly",
        description="Type of campaign: weekly, daily, monthly, special"
    )
    
    # Target audience
    target_subscriber_count: int = Field(
        default=0,
        description="Number of subscribers targeted for this campaign"
    )
    target_criteria: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Criteria for selecting target subscribers"
    )
    
    # Delivery tracking
    emails_sent: int = Field(
        default=0,
        description="Number of emails successfully sent"
    )
    emails_failed: int = Field(
        default=0,
        description="Number of emails that failed to send"
    )
    emails_bounced: int = Field(
        default=0,
        description="Number of emails that bounced"
    )
    
    # Engagement tracking
    emails_opened: int = Field(
        default=0,
        description="Number of emails opened by recipients"
    )
    emails_clicked: int = Field(
        default=0,
        description="Number of emails with link clicks"
    )
    unsubscribes: int = Field(
        default=0,
        description="Number of unsubscribes triggered by this campaign"
    )
    
    # Timestamps
    started_at: Optional[str] = Field(
        default=None,
        description="Timestamp when campaign sending started (ISO 8601 format)"
    )
    completed_at: Optional[str] = Field(
        default=None,
        description="Timestamp when campaign sending completed (ISO 8601 format)"
    )
    
    # Campaign content
    email_subject: Optional[str] = Field(
        default=None,
        description="Subject line for the email"
    )
    email_template: str = Field(
        default="default",
        description="Email template to use for the campaign"
    )
    
    # Error tracking
    error_messages: list[str] = Field(
        default_factory=list,
        description="List of error messages encountered during campaign"
    )
    
    # Validation constants
    ALLOWED_CAMPAIGN_TYPES: ClassVar[list[str]] = [
        "daily",
        "weekly",
        "monthly",
        "special",
        "test"
    ]
    
    ALLOWED_TEMPLATES: ClassVar[list[str]] = [
        "default",
        "minimal",
        "rich",
        "newsletter"
    ]

    @field_validator("campaign_name")
    @classmethod
    def validate_campaign_name(cls, v: str) -> str:
        """Validate campaign name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Campaign name must be non-empty")
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Campaign name must be at least 3 characters long")
        if len(v) > 200:
            raise ValueError("Campaign name must be at most 200 characters long")
        return v

    @field_validator("campaign_type")
    @classmethod
    def validate_campaign_type(cls, v: str) -> str:
        """Validate campaign type field"""
        if v not in cls.ALLOWED_CAMPAIGN_TYPES:
            raise ValueError(f"Campaign type must be one of: {cls.ALLOWED_CAMPAIGN_TYPES}")
        return v

    @field_validator("email_template")
    @classmethod
    def validate_email_template(cls, v: str) -> str:
        """Validate email template field"""
        if v not in cls.ALLOWED_TEMPLATES:
            raise ValueError(f"Email template must be one of: {cls.ALLOWED_TEMPLATES}")
        return v

    @field_validator("email_subject")
    @classmethod
    def validate_email_subject(cls, v: Optional[str]) -> Optional[str]:
        """Validate email subject field"""
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
            if len(v) > 200:
                raise ValueError("Email subject must be at most 200 characters long")
        return v

    def start_campaign(self) -> None:
        """Mark campaign as started"""
        self.started_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def complete_campaign(self) -> None:
        """Mark campaign as completed"""
        self.completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.update_timestamp()

    def record_email_sent(self) -> None:
        """Record a successful email send"""
        self.emails_sent += 1
        self.update_timestamp()

    def record_email_failed(self, error_message: str) -> None:
        """Record a failed email send"""
        self.emails_failed += 1
        if error_message not in self.error_messages:
            self.error_messages.append(error_message)
        self.update_timestamp()

    def record_email_bounced(self) -> None:
        """Record an email bounce"""
        self.emails_bounced += 1
        self.update_timestamp()

    def record_email_opened(self) -> None:
        """Record an email open"""
        self.emails_opened += 1
        self.update_timestamp()

    def record_email_clicked(self) -> None:
        """Record an email click"""
        self.emails_clicked += 1
        self.update_timestamp()

    def record_unsubscribe(self) -> None:
        """Record an unsubscribe from this campaign"""
        self.unsubscribes += 1
        self.update_timestamp()

    def get_delivery_rate(self) -> float:
        """Calculate delivery rate (sent / (sent + failed + bounced))"""
        total_attempts = self.emails_sent + self.emails_failed + self.emails_bounced
        if total_attempts == 0:
            return 0.0
        return self.emails_sent / total_attempts

    def get_open_rate(self) -> float:
        """Calculate open rate (opened / sent)"""
        if self.emails_sent == 0:
            return 0.0
        return self.emails_opened / self.emails_sent

    def get_click_rate(self) -> float:
        """Calculate click rate (clicked / sent)"""
        if self.emails_sent == 0:
            return 0.0
        return self.emails_clicked / self.emails_sent

    def get_click_through_rate(self) -> float:
        """Calculate click-through rate (clicked / opened)"""
        if self.emails_opened == 0:
            return 0.0
        return self.emails_clicked / self.emails_opened

    def get_unsubscribe_rate(self) -> float:
        """Calculate unsubscribe rate (unsubscribes / sent)"""
        if self.emails_sent == 0:
            return 0.0
        return self.unsubscribes / self.emails_sent

    def is_completed(self) -> bool:
        """Check if campaign is completed"""
        return self.completed_at is not None

    def get_duration_minutes(self) -> Optional[float]:
        """Get campaign duration in minutes"""
        if not self.started_at or not self.completed_at:
            return None
        
        start_dt = datetime.fromisoformat(self.started_at.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(self.completed_at.replace("Z", "+00:00"))
        return (end_dt - start_dt).total_seconds() / 60

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get campaign performance summary"""
        return {
            "delivery_rate": self.get_delivery_rate(),
            "open_rate": self.get_open_rate(),
            "click_rate": self.get_click_rate(),
            "click_through_rate": self.get_click_through_rate(),
            "unsubscribe_rate": self.get_unsubscribe_rate(),
            "duration_minutes": self.get_duration_minutes(),
            "total_sent": self.emails_sent,
            "total_failed": self.emails_failed,
            "total_bounced": self.emails_bounced,
            "total_opened": self.emails_opened,
            "total_clicked": self.emails_clicked,
            "total_unsubscribes": self.unsubscribes
        }

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        data["state"] = self.state
        data["is_completed"] = self.is_completed()
        data["performance"] = self.get_performance_summary()
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
