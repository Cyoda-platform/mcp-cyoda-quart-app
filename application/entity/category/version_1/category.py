"""
Category Entity for Purrfect Pets API

Represents a category of pets (e.g., Dogs, Cats, Birds) as specified
in functional requirements.
"""

from typing import ClassVar, Optional

from pydantic import Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Category(CyodaEntity):
    """
    Category entity represents a category of pets.

    State Management:
    - Entity state is managed internally via entity.meta.state
    - States: ACTIVE, INACTIVE
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Category"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    id: Optional[int] = Field(None, description="Unique identifier for the category")
    name: str = Field(..., description="Name of the category (required)")

    # Optional fields
    description: Optional[str] = Field(None, description="Description of the category")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Category name is required and cannot be empty")
        return v.strip()

    def is_active(self) -> bool:
        """Check if category is active"""
        return self.state == "active"

    def get_status(self) -> str:
        """Get category status based on state"""
        state_mapping = {"active": "ACTIVE", "inactive": "INACTIVE"}
        return state_mapping.get(self.state, "UNKNOWN")
