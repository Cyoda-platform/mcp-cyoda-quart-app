"""
Pet Entity for Purrfect Pets API

Represents pets available in the Purrfect Pets store with comprehensive
validation and workflow state management.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Pet(CyodaEntity):
    """
    Pet entity represents pets available in the Purrfect Pets store.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> available -> pending -> sold
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Pet"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    name: str = Field(..., description="Pet's name (e.g., 'Fluffy', 'Buddy')")
    photoUrls: List[str] = Field(
        ..., 
        alias="photoUrls",
        description="URLs to pet photos",
        min_length=1
    )

    # Optional fields
    category: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Pet category with id and name (e.g., {'id': 1, 'name': 'Dogs'})"
    )
    tags: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Tags for categorization with id and name"
    )
    breed: Optional[str] = Field(
        default=None,
        description="Pet breed information"
    )
    age: Optional[int] = Field(
        default=None,
        description="Pet age in months",
        ge=0
    )
    price: Optional[float] = Field(
        default=None,
        description="Pet price in USD",
        ge=0.0
    )

    # Processing-related fields (populated during processing)
    dateAdded: Optional[str] = Field(
        default=None,
        alias="dateAdded",
        description="Date when pet was added to the system"
    )
    viewCount: Optional[int] = Field(
        default=0,
        alias="viewCount",
        description="Number of times pet has been viewed"
    )
    reservedAt: Optional[str] = Field(
        default=None,
        alias="reservedAt",
        description="Timestamp when pet was reserved"
    )
    reservationExpiry: Optional[str] = Field(
        default=None,
        alias="reservationExpiry",
        description="Timestamp when reservation expires"
    )
    soldAt: Optional[str] = Field(
        default=None,
        alias="soldAt",
        description="Timestamp when pet was sold"
    )
    soldPrice: Optional[float] = Field(
        default=None,
        alias="soldPrice",
        description="Final sale price"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field according to criteria requirements"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet name must be non-empty")
        if len(v.strip()) < 2:
            raise ValueError("Pet name must be at least 2 characters long")
        if len(v.strip()) > 100:
            raise ValueError("Pet name must be at most 100 characters long")
        return v.strip()

    @field_validator("photoUrls")
    @classmethod
    def validate_photo_urls(cls, v: List[str]) -> List[str]:
        """Validate photo URLs"""
        if not v or len(v) == 0:
            raise ValueError("At least one photo URL is required")
        
        for url in v:
            if not url or len(url.strip()) == 0:
                raise ValueError("Photo URLs cannot be empty")
            # Basic URL validation
            if not (url.startswith("http://") or url.startswith("https://")):
                raise ValueError("Photo URLs must be valid HTTP/HTTPS URLs")
        
        return [url.strip() for url in v]

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate category structure"""
        if v is None:
            return v
        
        if not isinstance(v, dict):
            raise ValueError("Category must be a dictionary")
        
        if "id" not in v or "name" not in v:
            raise ValueError("Category must have 'id' and 'name' fields")
        
        if not isinstance(v["id"], int) or v["id"] <= 0:
            raise ValueError("Category id must be a positive integer")
        
        if not isinstance(v["name"], str) or len(v["name"].strip()) == 0:
            raise ValueError("Category name must be a non-empty string")
        
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[List[Dict[str, Any]]]) -> Optional[List[Dict[str, Any]]]:
        """Validate tags structure"""
        if v is None:
            return []
        
        for tag in v:
            if not isinstance(tag, dict):
                raise ValueError("Each tag must be a dictionary")
            
            if "id" not in tag or "name" not in tag:
                raise ValueError("Each tag must have 'id' and 'name' fields")
            
            if not isinstance(tag["id"], int) or tag["id"] <= 0:
                raise ValueError("Tag id must be a positive integer")
            
            if not isinstance(tag["name"], str) or len(tag["name"].strip()) == 0:
                raise ValueError("Tag name must be a non-empty string")
        
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[float]) -> Optional[float]:
        """Validate price field"""
        if v is not None and v < 0:
            raise ValueError("Pet price cannot be negative")
        return v

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: Optional[int]) -> Optional[int]:
        """Validate age field"""
        if v is not None and v < 0:
            raise ValueError("Pet age cannot be negative")
        if v is not None and v > 300:  # 25 years in months
            raise ValueError("Pet age seems unrealistic (max 300 months)")
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Pet":
        """Validate business logic rules"""
        # Ensure required fields for certain states
        if self.state == "pending" and not self.reservedAt:
            # This will be set by the processor, so we don't enforce it here
            pass
        
        if self.state == "sold" and not self.soldAt:
            # This will be set by the processor, so we don't enforce it here
            pass
        
        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def is_available(self) -> bool:
        """Check if pet is available for purchase"""
        return self.state == "available"

    def is_reserved(self) -> bool:
        """Check if pet is reserved/pending"""
        return self.state == "pending"

    def is_sold(self) -> bool:
        """Check if pet has been sold"""
        return self.state == "sold"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
