"""
Tag Entity for Purrfect Pets API

Represents tags that can be associated with pets for better categorization and search.
This is a reference entity without workflow states.
"""

from typing import ClassVar

from pydantic import ConfigDict, Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Tag(CyodaEntity):
    """
    Tag represents tags that can be associated with pets for better categorization and search.
    
    This is a reference entity and doesn't have workflow states.
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Tag"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields from functional requirements
    name: str = Field(..., description="Name of the tag (e.g., 'friendly', 'trained', 'playful')")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Tag name must be non-empty")
        if len(v) < 2:
            raise ValueError("Tag name must be at least 2 characters long")
        if len(v) > 30:
            raise ValueError("Tag name must be at most 30 characters long")
        return v.strip().lower()  # Normalize to lowercase

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
