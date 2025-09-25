"""
Pet API Models for Purrfect Pets API

Request and response models for Pet-related API endpoints.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Request Models
class PetQueryParams(BaseModel):
    """Query parameters for listing pets"""

    species: Optional[str] = Field(None, description="Filter by species")
    breed: Optional[str] = Field(None, description="Filter by breed")
    size: Optional[str] = Field(None, description="Filter by size")
    gender: Optional[str] = Field(None, description="Filter by gender")
    adoption_status: Optional[str] = Field(
        None, alias="adoptionStatus", description="Filter by adoption status"
    )
    health_status: Optional[str] = Field(
        None, alias="healthStatus", description="Filter by health status"
    )
    min_age: Optional[int] = Field(
        None, alias="minAge", description="Minimum age in months"
    )
    max_age: Optional[int] = Field(
        None, alias="maxAge", description="Maximum age in months"
    )
    min_price: Optional[Decimal] = Field(
        None, alias="minPrice", description="Minimum price"
    )
    max_price: Optional[Decimal] = Field(
        None, alias="maxPrice", description="Maximum price"
    )
    state: Optional[str] = Field(None, description="Filter by workflow state")
    offset: int = Field(0, description="Pagination offset")
    limit: int = Field(50, description="Pagination limit")


class PetUpdateQueryParams(BaseModel):
    """Query parameters for updating pets"""

    transition: Optional[str] = Field(
        None, description="Workflow transition to trigger"
    )


class PetSearchRequest(BaseModel):
    """Request model for pet search"""

    species: Optional[str] = Field(None, description="Pet species")
    breed: Optional[str] = Field(None, description="Pet breed")
    size: Optional[str] = Field(None, description="Pet size")
    gender: Optional[str] = Field(None, description="Pet gender")
    adoption_status: Optional[str] = Field(
        None, alias="adoptionStatus", description="Adoption status"
    )
    health_status: Optional[str] = Field(
        None, alias="healthStatus", description="Health status"
    )
    color: Optional[str] = Field(None, description="Pet color")


class TransitionRequest(BaseModel):
    """Request model for triggering workflow transitions"""

    transition_name: str = Field(
        ..., alias="transitionName", description="Name of transition to trigger"
    )


# Response Models
class PetResponse(BaseModel):
    """Response model for single pet"""

    # Make all fields optional to handle partial responses
    id: Optional[str] = Field(None, description="Pet technical ID")
    entity_id: Optional[str] = Field(
        None, alias="entityId", description="Pet entity ID"
    )
    name: Optional[str] = Field(None, description="Pet name")
    species: Optional[str] = Field(None, description="Pet species")
    breed: Optional[str] = Field(None, description="Pet breed")
    age_months: Optional[int] = Field(
        None, alias="ageMonths", description="Pet age in months"
    )
    age_display: Optional[str] = Field(
        None, alias="ageDisplay", description="Human-readable age"
    )
    color: Optional[str] = Field(None, description="Pet color")
    size: Optional[str] = Field(None, description="Pet size")
    gender: Optional[str] = Field(None, description="Pet gender")
    price: Optional[Decimal] = Field(None, description="Adoption fee")
    description: Optional[str] = Field(None, description="Pet description")
    health_status: Optional[str] = Field(
        None, alias="healthStatus", description="Health status"
    )
    vaccination_status: Optional[str] = Field(
        None, alias="vaccinationStatus", description="Vaccination status"
    )
    adoption_status: Optional[str] = Field(
        None, alias="adoptionStatus", description="Adoption status"
    )
    special_needs: Optional[str] = Field(
        None, alias="specialNeeds", description="Special needs"
    )
    arrival_date: Optional[str] = Field(
        None, alias="arrivalDate", description="Arrival date"
    )
    state: Optional[str] = Field(None, description="Workflow state")
    available_for_adoption: Optional[bool] = Field(
        None, alias="availableForAdoption", description="Available for adoption"
    )
    created_at: Optional[str] = Field(
        None, alias="createdAt", description="Creation timestamp"
    )
    updated_at: Optional[str] = Field(
        None, alias="updatedAt", description="Update timestamp"
    )


class PetListResponse(BaseModel):
    """Response model for pet list"""

    pets: List[PetResponse] = Field(..., description="List of pets")
    total: int = Field(..., description="Total number of pets")


class PetSearchResponse(BaseModel):
    """Response model for pet search"""

    pets: List[PetResponse] = Field(..., description="List of matching pets")
    total: int = Field(..., description="Total number of matching pets")


class DeleteResponse(BaseModel):
    """Response model for delete operations"""

    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Success message")
    entity_id: str = Field(..., alias="entityId", description="ID of deleted entity")


class ExistsResponse(BaseModel):
    """Response model for existence checks"""

    exists: bool = Field(..., description="Whether entity exists")
    entity_id: str = Field(..., alias="entityId", description="Entity ID checked")


class CountResponse(BaseModel):
    """Response model for count operations"""

    count: int = Field(..., description="Total count")


class TransitionResponse(BaseModel):
    """Response model for workflow transitions"""

    id: str = Field(..., description="Entity ID")
    message: str = Field(..., description="Success message")
    previous_state: Optional[str] = Field(
        None, alias="previousState", description="Previous workflow state"
    )
    new_state: Optional[str] = Field(
        None, alias="newState", description="New workflow state"
    )


class TransitionsResponse(BaseModel):
    """Response model for available transitions"""

    entity_id: str = Field(..., alias="entityId", description="Entity ID")
    available_transitions: List[str] = Field(
        ..., alias="availableTransitions", description="Available transitions"
    )
    current_state: Optional[str] = Field(
        None, alias="currentState", description="Current workflow state"
    )


# Error Response Models
class ErrorResponse(BaseModel):
    """Generic error response"""

    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class ValidationErrorResponse(BaseModel):
    """Validation error response"""

    error: str = Field(..., description="Validation error message")
    code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )


# Statistics Response Models
class PetStatisticsResponse(BaseModel):
    """Response model for pet statistics"""

    total_pets: int = Field(..., alias="totalPets", description="Total number of pets")
    available_pets: int = Field(
        ..., alias="availablePets", description="Number of available pets"
    )
    reserved_pets: int = Field(
        ..., alias="reservedPets", description="Number of reserved pets"
    )
    adopted_pets: int = Field(
        ..., alias="adoptedPets", description="Number of adopted pets"
    )
    by_species: Dict[str, int] = Field(
        ..., alias="bySpecies", description="Count by species"
    )
    by_size: Dict[str, int] = Field(..., alias="bySize", description="Count by size")
    by_health_status: Dict[str, int] = Field(
        ..., alias="byHealthStatus", description="Count by health status"
    )
    average_age_months: float = Field(
        ..., alias="averageAgeMonths", description="Average age in months"
    )
    average_price: float = Field(
        ..., alias="averagePrice", description="Average adoption fee"
    )


# Adoption-specific Models
class ReservationRequest(BaseModel):
    """Request model for pet reservation"""

    adopter_name: str = Field(
        ..., alias="adopterName", description="Name of potential adopter"
    )
    adopter_email: str = Field(
        ..., alias="adopterEmail", description="Email of potential adopter"
    )
    adopter_phone: Optional[str] = Field(
        None, alias="adopterPhone", description="Phone of potential adopter"
    )
    notes: Optional[str] = Field(None, description="Additional notes")


class AdoptionRequest(BaseModel):
    """Request model for pet adoption"""

    adopter_name: str = Field(..., alias="adopterName", description="Name of adopter")
    adopter_email: str = Field(
        ..., alias="adopterEmail", description="Email of adopter"
    )
    adopter_phone: Optional[str] = Field(
        None, alias="adopterPhone", description="Phone of adopter"
    )
    adoption_fee_paid: Decimal = Field(
        ..., alias="adoptionFeePaid", description="Adoption fee paid"
    )
    notes: Optional[str] = Field(None, description="Additional notes")


class HealthUpdateRequest(BaseModel):
    """Request model for health status updates"""

    health_status: str = Field(
        ..., alias="healthStatus", description="New health status"
    )
    vaccination_status: Optional[str] = Field(
        None, alias="vaccinationStatus", description="New vaccination status"
    )
    notes: Optional[str] = Field(None, description="Health update notes")
