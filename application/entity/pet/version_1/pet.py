"""Pet entity for Purrfect Pets API."""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from pydantic import Field

from entity.cyoda_entity import CyodaEntity


class Pet(CyodaEntity):
    """Pet entity representing pets available for adoption."""

    ENTITY_NAME: ClassVar[str] = "Pet"
    ENTITY_VERSION: ClassVar[int] = 1

    # Pet-specific fields
    id: Optional[int] = Field(default=None, description="Pet ID")
    name: str = Field(..., description="Pet's name")
    category: str = Field(..., description="Pet category (e.g., Dog, Cat, Bird, Fish)")
    breed: str = Field(..., description="Pet breed")
    age: int = Field(..., ge=0, description="Pet age in years")
    color: str = Field(..., description="Pet's primary color")
    weight: float = Field(..., gt=0, description="Pet weight in kg")
    description: str = Field(..., description="Detailed description of the pet")
    price: float = Field(..., gt=0, description="Pet price in USD")
    imageUrl: Optional[str] = Field(default=None, description="URL to pet's photo")
    ownerId: Optional[int] = Field(default=None, description="Reference to owner")
    createdAt: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Creation timestamp",
    )
    updatedAt: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Last update timestamp",
    )

    def __init__(self, **kwargs):
        """Initialize Pet entity."""
        super().__init__(**kwargs)
        if self.state == "none":
            self.state = "initial_state"
