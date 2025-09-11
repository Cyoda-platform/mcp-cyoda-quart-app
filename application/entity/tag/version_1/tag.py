"""
Tag Entity for Purrfect Pets API

Represents tags for categorizing pets (e.g., friendly, trained, hypoallergenic)
as specified in functional requirements.
"""

from typing import ClassVar, Optional

from pydantic import Field, field_validator

from common.entity.cyoda_entity import CyodaEntity


class Tag(CyodaEntity):
    """
    Tag entity represents tags for categorizing pets.

    State Management:
    - Entity state is managed internally via entity.meta.state
    - States: ACTIVE, INACTIVE
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Tag"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    id: Optional[int] = Field(None, description="Unique identifier for the tag")
    name: str = Field(..., description="Name of the tag (required)")

    # Optional fields
    color: Optional[str] = Field(None, description="Color code for the tag display")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Tag name is required and cannot be empty")
        return v.strip()

    def is_active(self) -> bool:
        """Check if tag is active"""
        return self.state == "active"

    def get_status(self) -> str:
        """Get tag status based on state"""
        state_mapping = {"active": "ACTIVE", "inactive": "INACTIVE"}
        return state_mapping.get(self.state, "UNKNOWN")
