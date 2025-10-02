# entity/email_campaign/version_1/email_campaign.py

"""
EmailCampaign Entity for Cat Fact Subscription Application

Represents a weekly email campaign that sends cat facts to subscribers.
Manages campaign scheduling, subscriber lists, and delivery tracking.
"""

from datetime import datetime, timezone
from typing import ClassVar, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class EmailCampaign(CyodaEntity):
    """
    EmailCampaign entity represents a weekly email campaign for sending cat facts.
    
    Manages campaign scheduling, subscriber targeting, and delivery metrics.
    The state field manages workflow states: initial_state -> created -> scheduled -> sent -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "EmailCampaign"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    campaign_name: str = Field(..., alias="campaignName", description="Name of the email campaign")
    
    # Campaign content
    cat_fact_id: str = Field(..., alias="catFactId", description="ID of the cat fact to send")
    subject_line: str = Field(..., alias="subjectLine", description="Email subject line")
    
    # Scheduling
    scheduled_date: str = Field(..., alias="scheduledDate", description="Scheduled delivery date (ISO 8601)")
    
    # Targeting
    target_subscriber_count: int = Field(
        default=0,
        alias="targetSubscriberCount",
        description="Number of subscribers targeted for this campaign"
    )
    
    # Delivery tracking
    emails_sent: int = Field(
        default=0,
        alias="emailsSent",
        description="Number of emails successfully sent"
    )
    emails_failed: int = Field(
        default=0,
        alias="emailsFailed",
        description="Number of emails that failed to send"
    )
    
    # Campaign metadata
    campaign_type: str = Field(
        default="weekly_cat_fact",
        alias="campaignType",
        description="Type of campaign"
    )
    
    # Timestamps
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the campaign was created (ISO 8601 format)"
    )
    sent_at: Optional[str] = Field(
        default=None,
        alias="sentAt",
        description="Timestamp when the campaign was sent (ISO 8601 format)"
    )
    completed_at: Optional[str] = Field(
        default=None,
        alias="completedAt",
        description="Timestamp when the campaign was completed (ISO 8601 format)"
    )
    
    # Performance metrics
    delivery_rate: Optional[float] = Field(
        default=None,
        alias="deliveryRate",
        description="Delivery success rate (0.0 to 1.0)"
    )
    
    # Error tracking
    error_messages: List[str] = Field(
        default_factory=list,
        alias="errorMessages",
        description="List of error messages encountered during delivery"
    )

    @field_validator("campaign_name")
    @classmethod
    def validate_campaign_name(cls, v: str) -> str:
        """Validate campaign name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Campaign name must be non-empty")
        
        if len(v) > 200:
            raise ValueError("Campaign name must be at most 200 characters long")
        
        return v.strip()

    @field_validator("subject_line")
    @classmethod
    def validate_subject_line(cls, v: str) -> str:
        """Validate email subject line"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Subject line must be non-empty")
        
        if len(v) > 150:
            raise ValueError("Subject line must be at most 150 characters long")
        
        return v.strip()

    @field_validator("delivery_rate")
    @classmethod
    def validate_delivery_rate(cls, v: Optional[float]) -> Optional[float]:
        """Validate delivery rate"""
        if v is None:
            return v
        
        if not 0.0 <= v <= 1.0:
            raise ValueError("Delivery rate must be between 0.0 and 1.0")
        
        return v

    def calculate_delivery_rate(self) -> None:
        """Calculate and set the delivery rate"""
        total_attempts = self.emails_sent + self.emails_failed
        if total_attempts > 0:
            self.delivery_rate = self.emails_sent / total_attempts
        else:
            self.delivery_rate = 0.0

    def record_email_sent(self) -> None:
        """Record a successful email send"""
        self.emails_sent += 1
        self.calculate_delivery_rate()

    def record_email_failed(self, error_message: str) -> None:
        """Record a failed email send"""
        self.emails_failed += 1
        if error_message not in self.error_messages:
            self.error_messages.append(error_message)
        self.calculate_delivery_rate()

    def mark_as_sent(self) -> None:
        """Mark the campaign as sent"""
        self.sent_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def mark_as_completed(self) -> None:
        """Mark the campaign as completed"""
        self.completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.calculate_delivery_rate()

    def is_ready_to_send(self) -> bool:
        """Check if the campaign is ready to send"""
        return (
            self.state == "scheduled"
            and bool(self.cat_fact_id.strip()) if self.cat_fact_id else False
            and bool(self.subject_line.strip()) if self.subject_line else False
            and self.target_subscriber_count > 0
        )

    def get_success_rate_percentage(self) -> float:
        """Get delivery success rate as percentage"""
        if self.delivery_rate is not None:
            return self.delivery_rate * 100
        return 0.0

    def get_campaign_summary(self) -> str:
        """Get a summary of the campaign"""
        return f"{self.campaign_name} - {self.emails_sent}/{self.target_subscriber_count} sent"

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
