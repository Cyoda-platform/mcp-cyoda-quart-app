"""
CatFact entity for the cat fact subscription system.
"""
from datetime import datetime
from typing import ClassVar, Optional
from pydantic import Field
from entity.cyoda_entity import CyodaEntity


class CatFact(CyodaEntity):
    """
    Represents a cat fact retrieved from the external API and stored for weekly distribution.
    """
    
    # Entity constants
    ENTITY_NAME: ClassVar[str] = "CatFact"
    ENTITY_VERSION: ClassVar[int] = 1
    
    # Business fields
    id: Optional[int] = Field(default=None, description="Unique identifier for the cat fact")
    fact: str = Field(..., description="The actual cat fact text (required)")
    length: Optional[int] = Field(default=None, description="Length of the fact text")
    retrievedDate: Optional[datetime] = Field(default=None, description="Date and time when the fact was retrieved from API")
    scheduledSendDate: Optional[datetime] = Field(default=None, description="Date and time when this fact is scheduled to be sent")
    apiFactId: Optional[str] = Field(default=None, description="Original ID from the Cat Fact API (if available)")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        
    def __str__(self) -> str:
        """String representation of the cat fact."""
        return f"CatFact(id={self.id}, fact='{self.fact[:50]}...', state={self.state})"
