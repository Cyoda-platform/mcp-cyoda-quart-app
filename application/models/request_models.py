"""
Request Models for Pet API endpoints.

Provides comprehensive validation models for all Pet API operations including
query parameters, request bodies, and validation schemas.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional error details"
    )
    code: Optional[str] = Field(default=None, description="Error code")


class SuccessResponse(BaseModel):
    """Standard success response model."""

    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")


class PetQueryParams(BaseModel):
    """Query parameters for Pet endpoints."""

    status: Optional[str] = Field(
        default=None, description="Filter by pet status", pattern=r"^[a-z]+$"
    )
    breed: Optional[str] = Field(
        default=None, description="Filter by pet breed", pattern=r"^[A-Z_]+$"
    )
    category: Optional[str] = Field(
        default=None, description="Filter by category name"
    )
    state: Optional[str] = Field(
        default=None, description="Filter by workflow state", pattern=r"^[a-z_]+$"
    )
    min_price: Optional[float] = Field(
        default=None, alias="minPrice", description="Minimum price filter", ge=0
    )
    max_price: Optional[float] = Field(
        default=None, alias="maxPrice", description="Maximum price filter", ge=0
    )
    limit: int = Field(default=50, description="Number of results", ge=1, le=1000)
    offset: int = Field(default=0, description="Pagination offset", ge=0)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed_statuses = ["available", "pending", "sold"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {allowed_statuses}")
        return v

    @field_validator("breed")
    @classmethod
    def validate_breed(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed_breeds = [
            "LABRADOR", "GOLDEN_RETRIEVER", "GERMAN_SHEPHERD", "BULLDOG", "POODLE",
            "BEAGLE", "ROTTWEILER", "YORKSHIRE_TERRIER", "DACHSHUND", "SIBERIAN_HUSKY",
            "MIXED", "OTHER"
        ]
        if v not in allowed_breeds:
            raise ValueError(f"Breed must be one of: {allowed_breeds}")
        return v


class PetUpdateQueryParams(BaseModel):
    """Query parameters for Pet update operations."""

    transition: Optional[str] = Field(
        default=None, description="Workflow transition to trigger", pattern=r"^[a-z_]+$"
    )


class TransitionRequest(BaseModel):
    """Request model for triggering workflow transitions."""

    transition_name: str = Field(
        ...,
        alias="transitionName",
        description="Name of the transition to execute",
        pattern=r"^[a-z_]+$",
    )

    @field_validator("transition_name")
    @classmethod
    def validate_transition_name(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("Transition name cannot be empty")
        allowed_transitions = [
            "create", "validate", "process", "reserve", "sell", "cancel_reservation",
            "restock", "make_available"
        ]
        if v not in allowed_transitions:
            raise ValueError(f"Transition must be one of: {allowed_transitions}")
        return v


class SearchRequest(BaseModel):
    """Request model for Pet search operations."""

    name: Optional[str] = Field(default=None, description="Pet name to search for")
    status: Optional[str] = Field(default=None, description="Pet status to search for")
    breed: Optional[str] = Field(default=None, description="Pet breed to search for")
    category: Optional[str] = Field(default=None, description="Category name to search for")
    min_price: Optional[float] = Field(
        default=None, alias="minPrice", description="Minimum price", ge=0
    )
    max_price: Optional[float] = Field(
        default=None, alias="maxPrice", description="Maximum price", ge=0
    )
    tags: Optional[List[str]] = Field(
        default=None, description="Tags to search for"
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed_statuses = ["available", "pending", "sold"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {allowed_statuses}")
        return v

    @field_validator("breed")
    @classmethod
    def validate_breed(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed_breeds = [
            "LABRADOR", "GOLDEN_RETRIEVER", "GERMAN_SHEPHERD", "BULLDOG", "POODLE",
            "BEAGLE", "ROTTWEILER", "YORKSHIRE_TERRIER", "DACHSHUND", "SIBERIAN_HUSKY",
            "MIXED", "OTHER"
        ]
        if v not in allowed_breeds:
            raise ValueError(f"Breed must be one of: {allowed_breeds}")
        return v
