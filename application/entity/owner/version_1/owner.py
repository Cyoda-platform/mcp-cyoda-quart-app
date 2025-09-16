"""Owner entity for Purrfect Pets API."""
from typing import ClassVar, Optional
from pydantic import Field, EmailStr
from datetime import datetime, timezone

from entity.cyoda_entity import CyodaEntity


class Owner(CyodaEntity):
    """Owner entity representing pet owners."""
    
    ENTITY_NAME: ClassVar[str] = "Owner"
    ENTITY_VERSION: ClassVar[int] = 1
    
    # Owner-specific fields
    id: Optional[int] = Field(default=None, description="Owner ID")
    firstName: str = Field(..., description="Owner's first name")
    lastName: str = Field(..., description="Owner's last name")
    email: str = Field(..., description="Owner's email address")
    phone: str = Field(..., description="Owner's phone number")
    address: str = Field(..., description="Owner's address")
    city: str = Field(..., description="Owner's city")
    zipCode: str = Field(..., description="Owner's zip code")
    country: str = Field(..., description="Owner's country")
    dateOfBirth: str = Field(..., description="Owner's date of birth (YYYY-MM-DD)")
    createdAt: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Creation timestamp"
    )
    updatedAt: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Last update timestamp"
    )
    
    def __init__(self, **kwargs):
        """Initialize Owner entity."""
        super().__init__(**kwargs)
        if self.state == "none":
            self.state = "initial_state"
