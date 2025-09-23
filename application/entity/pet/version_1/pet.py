# entity/pet/version_1/pet.py

"""
Pet Entity for Cyoda Pet Search Application

Represents a pet with search and transformation capabilities as specified 
in functional requirements. Supports data ingestion from external APIs,
transformation to user-friendly format, and filtering by species, status, and category.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class PetCategory(dict):
    """Pet category with id and name"""
    def __init__(self, id: Optional[int] = None, name: Optional[str] = None):
        super().__init__()
        if id is not None:
            self["id"] = id
        if name is not None:
            self["name"] = name


class PetTag(dict):
    """Pet tag with id and name"""
    def __init__(self, id: Optional[int] = None, name: Optional[str] = None):
        super().__init__()
        if id is not None:
            self["id"] = id
        if name is not None:
            self["name"] = name


class Pet(CyodaEntity):
    """
    Pet entity for the Pet Search Application that handles data ingestion,
    transformation, and filtering as specified in functional requirements.

    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> ingested -> transformed -> displayed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Pet"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core pet fields from external API
    pet_id: Optional[int] = Field(
        default=None,
        alias="petId",
        description="External pet ID from the API"
    )
    name: str = Field(..., description="Name of the pet")
    category: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Pet category with id and name"
    )
    photo_urls: List[str] = Field(
        default_factory=list,
        alias="photoUrls",
        description="Array of photo URLs for the pet"
    )
    tags: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Array of tags associated with the pet"
    )
    status: str = Field(
        default="available",
        description="Pet status in the store (available, pending, sold)"
    )

    # Search parameters for data ingestion
    search_species: Optional[str] = Field(
        default=None,
        alias="searchSpecies",
        description="Species filter used for searching (e.g., 'dog', 'cat')"
    )
    search_status: Optional[str] = Field(
        default=None,
        alias="searchStatus",
        description="Status filter used for searching"
    )
    search_category_id: Optional[int] = Field(
        default=None,
        alias="searchCategoryId",
        description="Category ID filter used for searching"
    )

    # Transformation fields - user-friendly format
    display_name: Optional[str] = Field(
        default=None,
        alias="displayName",
        description="User-friendly display name (transformed from 'name')"
    )
    availability_status: Optional[str] = Field(
        default=None,
        alias="availabilityStatus",
        description="User-friendly availability status"
    )
    species: Optional[str] = Field(
        default=None,
        description="Derived species information"
    )
    description: Optional[str] = Field(
        default=None,
        description="Generated description for the pet"
    )

    # Processing metadata
    ingested_at: Optional[str] = Field(
        default=None,
        alias="ingestedAt",
        description="Timestamp when data was ingested from external API"
    )
    transformed_at: Optional[str] = Field(
        default=None,
        alias="transformedAt",
        description="Timestamp when data was transformed to user-friendly format"
    )
    transformation_data: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="transformationData",
        description="Additional transformation metadata"
    )

    # Validation constants
    ALLOWED_STATUSES: ClassVar[List[str]] = ["available", "pending", "sold"]
    ALLOWED_SPECIES: ClassVar[List[str]] = ["dog", "cat", "bird", "fish", "rabbit", "hamster", "other"]

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate pet name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Pet name must be non-empty")
        if len(v) > 100:
            raise ValueError("Pet name must be at most 100 characters long")
        return v.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate pet status"""
        if v not in cls.ALLOWED_STATUSES:
            raise ValueError(f"Status must be one of: {cls.ALLOWED_STATUSES}")
        return v

    @field_validator("species")
    @classmethod
    def validate_species(cls, v: Optional[str]) -> Optional[str]:
        """Validate species if provided"""
        if v is not None and v not in cls.ALLOWED_SPECIES:
            raise ValueError(f"Species must be one of: {cls.ALLOWED_SPECIES}")
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Pet":
        """Validate business logic rules"""
        # Ensure photo_urls is not empty for available pets
        if self.status == "available" and not self.photo_urls:
            raise ValueError("Available pets must have at least one photo URL")
        
        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        current_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        # Note: updated_at is inherited from CyodaEntity

    def set_ingested_data(self, api_data: Dict[str, Any]) -> None:
        """Set data from external API ingestion"""
        self.ingested_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        # Map API data to entity fields
        if "id" in api_data:
            self.pet_id = api_data["id"]
        if "name" in api_data:
            self.name = api_data["name"]
        if "category" in api_data:
            self.category = api_data["category"]
        if "photoUrls" in api_data:
            self.photo_urls = api_data["photoUrls"]
        if "tags" in api_data:
            self.tags = api_data["tags"]
        if "status" in api_data:
            self.status = api_data["status"]

    def set_transformed_data(self, transformation_data: Dict[str, Any]) -> None:
        """Set transformed user-friendly data"""
        self.transformed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self.transformation_data = transformation_data
        
        # Apply transformations
        self.display_name = f"🐾 {self.name}"  # User-friendly name with emoji
        
        # Transform status to user-friendly format
        status_mapping = {
            "available": "✅ Available for Adoption",
            "pending": "⏳ Adoption Pending",
            "sold": "❤️ Already Adopted"
        }
        self.availability_status = status_mapping.get(self.status, self.status)
        
        # Derive species from category or tags
        if self.category and "name" in self.category:
            category_name = self.category["name"].lower()
            if "dog" in category_name:
                self.species = "dog"
            elif "cat" in category_name:
                self.species = "cat"
            elif "bird" in category_name:
                self.species = "bird"
            elif "fish" in category_name:
                self.species = "fish"
            else:
                self.species = "other"
        
        # Generate description
        species_text = self.species or "pet"
        self.description = f"A lovely {species_text} named {self.name} that is {self.availability_status.lower()}"

    def is_ready_for_transformation(self) -> bool:
        """Check if pet data is ready for transformation (in ingested state)"""
        return self.state == "ingested"

    def is_transformed(self) -> bool:
        """Check if pet has been transformed"""
        return self.state == "transformed" or self.state == "displayed"

    def matches_search_criteria(self, species: Optional[str] = None, 
                              status: Optional[str] = None, 
                              category_id: Optional[int] = None) -> bool:
        """Check if pet matches the given search criteria"""
        if species and self.species != species:
            return False
        if status and self.status != status:
            return False
        if category_id and self.category and self.category.get("id") != category_id:
            return False
        return True

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
