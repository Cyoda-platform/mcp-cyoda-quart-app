"""
Pet Entity for Purrfect Pets API Application

Represents a pet in the pet store with all necessary fields for pet management
including name, category, photos, tags, and status as specified in Petstore API.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Pet(CyodaEntity):
    """
    Pet entity represents a pet in the pet store.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> created -> validated -> processed -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Pet"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from Petstore API
    name: str = Field(..., description="Name of the pet")
    photo_urls: List[str] = Field(
        default_factory=list,
        alias="photoUrls",
        description="List of photo URLs for the pet"
    )

    # Optional fields
    category_name: Optional[str] = Field(
        default=None,
        alias="categoryName",
        description="Category name for the pet"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Tags associated with the pet"
    )
    status: Optional[str] = Field(
        default="available",
        description="Pet status in the store"
    )

    # Additional fields for enhanced functionality
    breed: Optional[str] = Field(
        default=None,
        description="Breed of the pet"
    )
    age: Optional[int] = Field(
        default=None,
        description="Age of the pet in years"
    )
    description: Optional[str] = Field(
        default=None,
        description="Description of the pet"
    )
    price: Optional[float] = Field(
        default=None,
        description="Price of the pet"
    )

    # Processing-related fields
    processed_data: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="processedData",
        description="Data populated during processing"
    )
    validation_result: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="validationResult",
        description="Result of validation checks"
    )

    # Validation constants
    ALLOWED_STATUSES: ClassVar[List[str]] = ["available", "pending", "sold"]
    ALLOWED_CATEGORIES: ClassVar[List[str]] = [
        "Dogs", "Cats", "Birds", "Fish", "Reptiles", "Small Animals", "Other"
    ]

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate pet name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet name must be non-empty")
        if len(v) < 2:
            raise ValueError("Pet name must be at least 2 characters long")
        if len(v) > 50:
            raise ValueError("Pet name must be at most 50 characters long")
        return v.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate pet status"""
        if v is not None and v not in cls.ALLOWED_STATUSES:
            raise ValueError(f"Status must be one of: {cls.ALLOWED_STATUSES}")
        return v

    @field_validator("category_name")
    @classmethod
    def validate_category_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate category name"""
        if v is not None and v not in cls.ALLOWED_CATEGORIES:
            raise ValueError(f"Category must be one of: {cls.ALLOWED_CATEGORIES}")
        return v

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: Optional[int]) -> Optional[int]:
        """Validate pet age"""
        if v is not None:
            if v < 0:
                raise ValueError("Age cannot be negative")
            if v > 30:
                raise ValueError("Age cannot exceed 30 years")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[float]) -> Optional[float]:
        """Validate pet price"""
        if v is not None:
            if v < 0:
                raise ValueError("Price cannot be negative")
            if v > 100000:
                raise ValueError("Price cannot exceed $100,000")
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Pet":
        """Validate business logic rules"""
        # Ensure at least one photo URL for pets that are available
        if self.status == "available" and not self.photo_urls:
            raise ValueError("Available pets must have at least one photo")
        
        # Validate photo URLs format (basic check)
        for url in self.photo_urls:
            if not url.startswith(("http://", "https://")):
                raise ValueError("Photo URLs must be valid HTTP/HTTPS URLs")
        
        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_processed_data(self, processed_data: Dict[str, Any]) -> None:
        """Set processed data and update timestamp"""
        self.processed_data = processed_data
        self.update_timestamp()

    def set_validation_result(self, validation_result: Dict[str, Any]) -> None:
        """Set validation result and update timestamp"""
        self.validation_result = validation_result
        self.update_timestamp()

    def is_available(self) -> bool:
        """Check if pet is available for purchase"""
        return self.status == "available"

    def is_sold(self) -> bool:
        """Check if pet is sold"""
        return self.status == "sold"

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
