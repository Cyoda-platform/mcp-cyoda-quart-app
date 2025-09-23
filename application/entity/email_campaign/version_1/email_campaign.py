# entity/email_campaign/version_1/email_campaign.py

"""
EmailCampaign Entity for Cat Fact Subscription Application

Represents weekly email campaigns that send cat facts to subscribers.
Manages campaign details, delivery status, and reporting metrics.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class EmailCampaign(CyodaEntity):
    """
    EmailCampaign represents a weekly email campaign that sends cat facts to subscribers.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> created -> sending -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "EmailCampaign"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    campaign_name: str = Field(..., alias="campaignName", description="Name of the email campaign")
    campaign_date: str = Field(..., alias="campaignDate", description="Date of the campaign (YYYY-MM-DD)")
    
    # Cat fact reference
    cat_fact_id: str = Field(..., alias="catFactId", description="ID of the cat fact to send")
    cat_fact_text: Optional[str] = Field(
        default=None,
        alias="catFactText", 
        description="Cached cat fact text for quick access"
    )
    
    # Campaign status and metrics
    status: str = Field(default="created", description="Campaign status: created, sending, completed, failed")
    
    # Subscriber metrics
    total_subscribers: int = Field(
        default=0,
        alias="totalSubscribers",
        description="Total number of active subscribers at campaign time"
    )
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
    emails_opened: int = Field(
        default=0,
        alias="emailsOpened",
        description="Number of emails opened by recipients"
    )
    emails_clicked: int = Field(
        default=0,
        alias="emailsClicked",
        description="Number of emails with link clicks"
    )
    
    # Timestamps
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when campaign was created (ISO 8601 format)"
    )
    started_at: Optional[str] = Field(
        default=None,
        alias="startedAt",
        description="Timestamp when campaign sending started"
    )
    completed_at: Optional[str] = Field(
        default=None,
        alias="completedAt",
        description="Timestamp when campaign was completed"
    )
    
    # Configuration
    email_subject: str = Field(
        default="Your Weekly Cat Fact! 🐱",
        alias="emailSubject",
        description="Subject line for the campaign emails"
    )
    email_template: str = Field(
        default="default",
        alias="emailTemplate",
        description="Email template to use for the campaign"
    )
    
    # Error tracking
    error_messages: List[str] = Field(
        default_factory=list,
        alias="errorMessages",
        description="List of error messages encountered during campaign"
    )
    
    # Reporting data
    delivery_rate: Optional[float] = Field(
        default=None,
        alias="deliveryRate",
        description="Percentage of emails successfully delivered"
    )
    open_rate: Optional[float] = Field(
        default=None,
        alias="openRate",
        description="Percentage of emails opened"
    )
    click_rate: Optional[float] = Field(
        default=None,
        alias="clickRate",
        description="Percentage of emails with clicks"
    )

    # Validation constants
    ALLOWED_STATUSES: ClassVar[List[str]] = [
        "created",
        "sending", 
        "completed",
        "failed"
    ]

    @field_validator("campaign_name")
    @classmethod
    def validate_campaign_name(cls, v: str) -> str:
        """Validate campaign name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Campaign name must be non-empty")
        
        if len(v) > 200:
            raise ValueError("Campaign name must be at most 200 characters long")
            
        return v.strip()

    @field_validator("campaign_date")
    @classmethod
    def validate_campaign_date(cls, v: str) -> str:
        """Validate campaign date format (YYYY-MM-DD)"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Campaign date must be non-empty")
        
        try:
            # Validate date format
            datetime.strptime(v, "%Y-%m-%d")
            return v.strip()
        except ValueError:
            raise ValueError("Campaign date must be in YYYY-MM-DD format")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate campaign status"""
        if v not in cls.ALLOWED_STATUSES:
            raise ValueError(f"Status must be one of: {cls.ALLOWED_STATUSES}")
        return v

    def start_campaign(self) -> None:
        """Mark campaign as started"""
        self.status = "sending"
        self.started_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def complete_campaign(self) -> None:
        """Mark campaign as completed and calculate metrics"""
        self.status = "completed"
        self.completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self._calculate_metrics()

    def fail_campaign(self, error_message: str) -> None:
        """Mark campaign as failed"""
        self.status = "failed"
        self.error_messages.append(error_message)
        self.completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def update_email_stats(self, sent: int = 0, failed: int = 0, opened: int = 0, clicked: int = 0) -> None:
        """Update email statistics"""
        self.emails_sent += sent
        self.emails_failed += failed
        self.emails_opened += opened
        self.emails_clicked += clicked
        self._calculate_metrics()

    def _calculate_metrics(self) -> None:
        """Calculate delivery, open, and click rates"""
        total_attempted = self.emails_sent + self.emails_failed
        
        if total_attempted > 0:
            self.delivery_rate = (self.emails_sent / total_attempted) * 100
        
        if self.emails_sent > 0:
            self.open_rate = (self.emails_opened / self.emails_sent) * 100
            self.click_rate = (self.emails_clicked / self.emails_sent) * 100

    def add_error(self, error_message: str) -> None:
        """Add an error message to the campaign"""
        self.error_messages.append(error_message)

    def is_completed(self) -> bool:
        """Check if campaign is completed"""
        return self.status in ["completed", "failed"]

    def get_success_rate(self) -> float:
        """Get overall success rate of the campaign"""
        if self.total_subscribers == 0:
            return 0.0
        return (self.emails_sent / self.total_subscribers) * 100

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        data["state"] = self.state
        data["successRate"] = self.get_success_rate()
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
