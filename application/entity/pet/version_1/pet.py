# entity/pet/version_1/pet.py

"""
Pet Entity for Cyoda Petstore Application

Represents a pet in the petstore with all necessary fields for a complete
petstore API implementation following OpenAPI Petstore specification.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Category(CyodaEntity):
    """Category model for pet categorization"""

    id: Optional[int] = Field(default=None, description="Category ID")
    name: str = Field(..., description="Category name")


class Tag(CyodaEntity):
    """Tag model for pet tagging"""

    id: Optional[int] = Field(default=None, description="Tag ID")
    name: str = Field(..., description="Tag name")


class Pet(CyodaEntity):
    """
    Pet entity represents a pet in the petstore with complete functionality
    for inventory management, status tracking, and workflow processing.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> available -> pending -> sold
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Pet"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core pet fields following OpenAPI Petstore specification
    name: str = Field(..., description="Pet name")
    category: Optional[Dict[str, Any]] = Field(
        default=None, description="Pet category information"
    )
    photo_urls: List[str] = Field(
        default_factory=list,
        alias="photoUrls",
        description="List of photo URLs for the pet",
    )
    tags: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="List of tags for the pet"
    )
    status: Optional[str] = Field(
        default="available",
        description="Pet status in the store (available, pending, sold)",
    )

    # Additional fields for enhanced functionality
    breed: Optional[str] = Field(default=None, description="Pet breed")
    age: Optional[int] = Field(default=None, description="Pet age in years")
    price: Optional[float] = Field(default=None, description="Pet price")
    description: Optional[str] = Field(default=None, description="Pet description")

    # Inventory tracking
    inventory_count: Optional[int] = Field(
        default=1,
        alias="inventoryCount",
        description="Number of pets available in inventory",
    )

    # Timestamps (inherited from CyodaEntity but customized)
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the pet was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the pet was last updated (ISO 8601 format)",
    )

    # Processing-related fields (populated during processing)
    processed_data: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="processedData",
        description="Data that gets populated during processing",
    )
    validation_result: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="validationResult",
        description="Result of validation checks",
    )

    # Validation constants
    ALLOWED_STATUSES: ClassVar[List[str]] = ["available", "pending", "sold"]
    ALLOWED_BREEDS: ClassVar[List[str]] = [
        "LABRADOR",
        "GOLDEN_RETRIEVER",
        "GERMAN_SHEPHERD",
        "BULLDOG",
        "POODLE",
        "BEAGLE",
        "ROTTWEILER",
        "YORKSHIRE_TERRIER",
        "DACHSHUND",
        "SIBERIAN_HUSKY",
        "MIXED",
        "OTHER",
    ]

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate pet name field"""
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
        """Validate pet status field"""
        if v is not None and v not in cls.ALLOWED_STATUSES:
            raise ValueError(f"Status must be one of: {cls.ALLOWED_STATUSES}")
        return v

    @field_validator("breed")
    @classmethod
    def validate_breed(cls, v: Optional[str]) -> Optional[str]:
        """Validate pet breed field"""
        if v is not None and v not in cls.ALLOWED_BREEDS:
            raise ValueError(f"Breed must be one of: {cls.ALLOWED_BREEDS}")
        return v

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: Optional[int]) -> Optional[int]:
        """Validate pet age field"""
        if v is not None:
            if v < 0:
                raise ValueError("Pet age cannot be negative")
            if v > 30:
                raise ValueError("Pet age cannot exceed 30 years")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[float]) -> Optional[float]:
        """Validate pet price field"""
        if v is not None:
            if v < 0:
                raise ValueError("Pet price cannot be negative")
            if v > 10000:
                raise ValueError("Pet price cannot exceed $10,000")
        return v

    @field_validator("inventory_count")
    @classmethod
    def validate_inventory_count(cls, v: Optional[int]) -> Optional[int]:
        """Validate inventory count field"""
        if v is not None:
            if v < 0:
                raise ValueError("Inventory count cannot be negative")
            if v > 1000:
                raise ValueError("Inventory count cannot exceed 1000")
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Pet":
        """Validate business logic rules"""
        # Sold pets should have zero inventory
        if self.status == "sold" and self.inventory_count and self.inventory_count > 0:
            raise ValueError("Sold pets cannot have inventory count greater than 0")

        # Pending pets should have limited inventory
        if (
            self.status == "pending"
            and self.inventory_count
            and self.inventory_count > 10
        ):
            raise ValueError("Pending pets cannot have inventory count greater than 10")

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
        return self.status == "available" and (self.inventory_count or 0) > 0

    def is_sold(self) -> bool:
        """Check if pet is sold"""
        return self.status == "sold"

    def update_inventory(self, count: int) -> None:
        """Update inventory count and adjust status if needed"""
        self.inventory_count = max(0, count)
        if self.inventory_count == 0 and self.status == "available":
            self.status = "sold"
        self.update_timestamp()

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
