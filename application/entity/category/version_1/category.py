"""Category entity for Purrfect Pets API."""
from typing import ClassVar, Optional
from pydantic import Field
from datetime import datetime, timezone

from entity.cyoda_entity import CyodaEntity


class Category(CyodaEntity):
    """Category entity representing pet categories."""
    
    ENTITY_NAME: ClassVar[str] = "Category"
    ENTITY_VERSION: ClassVar[int] = 1
    
    # Category-specific fields
    id: Optional[int] = Field(default=None, description="Category ID")
    name: str = Field(..., description="Category name")
    description: str = Field(..., description="Category description")
    imageUrl: Optional[str] = Field(default=None, description="Category image URL")
    isActive: bool = Field(default=True, description="Whether category is active")
    createdAt: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Creation timestamp"
    )
    updatedAt: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Last update timestamp"
    )
    
    def __init__(self, **kwargs):
        """Initialize Category entity."""
        super().__init__(**kwargs)
        if self.state == "none":
            self.state = "initial_state"
