"""
Mail entity model for email processing.
"""
from typing import List, Optional
from pydantic import Field, validator
from ..cyoda_entity import CyodaEntity


class MailEntity(CyodaEntity):
    """Mail entity model for email processing"""
    
    # Mail-specific fields
    is_happy: bool = Field(..., description="Whether this is a happy or gloomy mail")
    mail_list: List[str] = Field(..., description="List of email addresses to send to")
    
    # Processing fields
    status: Optional[str] = Field(default="queued", description="Mail processing status")
    requested_at: Optional[str] = Field(default=None, description="When the mail was requested")
    started_at: Optional[str] = Field(default=None, description="When processing started")
    completed_at: Optional[str] = Field(default=None, description="When processing completed")
    error_message: Optional[str] = Field(default=None, description="Error message if processing failed")
    
    @validator('mail_list')
    def validate_mail_list(cls, v):
        if not v:
            raise ValueError('mail_list cannot be empty')
        return v
