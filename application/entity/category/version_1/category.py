"""
Category Entity for Purrfect Pets API

Represents a category of pets (e.g., Dogs, Cats, Birds).
This is a reference entity without workflow states.
"""

from typing import ClassVar, Optional

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Category(CyodaEntity):
    """
    Category represents a category of pets (e.g., Dogs, Cats, Birds).
    
    This is a reference entity and doesn't have workflow states.
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Category"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    name: str = Field(..., description="Name of the category (e.g., 'Dogs', 'Cats')")
    description: Optional[str] = Field(
        default=None, description="Description of the category"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Category name must be non-empty")
        if len(v) < 2:
            raise ValueError("Category name must be at least 2 characters long")
        if len(v) > 50:
            raise ValueError("Category name must be at most 50 characters long")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description field"""
        if v is not None:
            if len(v) > 200:
                raise ValueError("Category description must be at most 200 characters long")
            return v.strip() if v.strip() else None
        return v

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
