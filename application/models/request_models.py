"""
Request models for Purrfect Pets Application API.

Defines Pydantic models for request validation and documentation.
"""

from typing import Optional

from pydantic import BaseModel, Field


class PetQueryParams(BaseModel):
    """Query parameters for listing pets."""
    
    species: Optional[str] = Field(None, description="Filter by pet species")
    breed: Optional[str] = Field(None, description="Filter by pet breed")
    age_min: Optional[int] = Field(None, description="Minimum age filter", ge=0)
    age_max: Optional[int] = Field(None, description="Maximum age filter", ge=0)
    state: Optional[str] = Field(None, description="Filter by workflow state")
    offset: int = Field(0, description="Number of items to skip", ge=0)
    limit: int = Field(50, description="Maximum number of items to return", ge=1, le=100)


class PetUpdateQueryParams(BaseModel):
    """Query parameters for updating pets."""
    
    transition: Optional[str] = Field(None, description="Workflow transition to execute")


class OwnerQueryParams(BaseModel):
    """Query parameters for listing owners."""
    
    experience: Optional[str] = Field(None, description="Filter by experience level")
    state: Optional[str] = Field(None, description="Filter by workflow state")
    offset: int = Field(0, description="Number of items to skip", ge=0)
    limit: int = Field(50, description="Maximum number of items to return", ge=1, le=100)


class OwnerUpdateQueryParams(BaseModel):
    """Query parameters for updating owners."""
    
    transition: Optional[str] = Field(None, description="Workflow transition to execute")


class AdoptionQueryParams(BaseModel):
    """Query parameters for listing adoptions."""
    
    pet_id: Optional[str] = Field(None, description="Filter by pet ID")
    owner_id: Optional[str] = Field(None, description="Filter by owner ID")
    state: Optional[str] = Field(None, description="Filter by workflow state")
    offset: int = Field(0, description="Number of items to skip", ge=0)
    limit: int = Field(50, description="Maximum number of items to return", ge=1, le=100)


class AdoptionUpdateQueryParams(BaseModel):
    """Query parameters for updating adoptions."""
    
    transition: Optional[str] = Field(None, description="Workflow transition to execute")


class SearchRequest(BaseModel):
    """Generic search request model."""
    
    name: Optional[str] = Field(None, description="Search by name")
    species: Optional[str] = Field(None, description="Search by species")
    breed: Optional[str] = Field(None, description="Search by breed")
    experience: Optional[str] = Field(None, description="Search by experience")
    state: Optional[str] = Field(None, description="Search by state")


class TransitionRequest(BaseModel):
    """Request model for triggering workflow transitions."""
    
    transition_name: str = Field(..., description="Name of the transition to execute")
