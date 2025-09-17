"""
Response models for Purrfect Pets Application API.

Defines Pydantic models for response validation and documentation.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PetResponse(BaseModel):
    """Response model for a single pet."""
    
    id: str = Field(..., description="Pet ID")
    name: str = Field(..., description="Pet name")
    species: str = Field(..., description="Pet species")
    breed: str = Field(..., description="Pet breed")
    age: int = Field(..., description="Pet age")
    description: str = Field(..., description="Pet description")
    medical_history: str = Field(..., description="Pet medical history")
    adoption_fee: float = Field(..., description="Adoption fee")
    owner_id: Optional[str] = Field(None, description="Owner ID if adopted")
    adoption_id: Optional[str] = Field(None, description="Adoption ID if in process")
    state: str = Field(..., description="Current workflow state")


class PetListResponse(BaseModel):
    """Response model for a list of pets."""
    
    pets: List[Dict[str, Any]] = Field(..., description="List of pets")
    total: int = Field(..., description="Total number of pets")


class PetSearchResponse(BaseModel):
    """Response model for pet search results."""
    
    pets: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")


class OwnerResponse(BaseModel):
    """Response model for a single owner."""
    
    id: str = Field(..., description="Owner ID")
    name: str = Field(..., description="Owner name")
    email: str = Field(..., description="Owner email")
    phone: str = Field(..., description="Owner phone")
    address: str = Field(..., description="Owner address")
    experience: str = Field(..., description="Experience level")
    preferences: str = Field(..., description="Pet preferences")
    verification_documents: Optional[str] = Field(None, description="Verification documents")
    pet_ids: List[str] = Field(..., description="List of adopted pets")
    adoption_ids: List[str] = Field(..., description="List of adoptions")
    state: str = Field(..., description="Current workflow state")


class OwnerListResponse(BaseModel):
    """Response model for a list of owners."""
    
    owners: List[Dict[str, Any]] = Field(..., description="List of owners")
    total: int = Field(..., description="Total number of owners")


class OwnerSearchResponse(BaseModel):
    """Response model for owner search results."""
    
    owners: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")


class AdoptionResponse(BaseModel):
    """Response model for a single adoption."""
    
    id: str = Field(..., description="Adoption ID")
    pet_id: str = Field(..., description="Pet ID")
    owner_id: str = Field(..., description="Owner ID")
    application_date: str = Field(..., description="Application date")
    adoption_date: Optional[str] = Field(None, description="Adoption completion date")
    notes: str = Field(..., description="Adoption notes")
    fee_paid: float = Field(..., description="Fee paid")
    contract_signed: bool = Field(..., description="Contract signed status")
    state: str = Field(..., description="Current workflow state")


class AdoptionListResponse(BaseModel):
    """Response model for a list of adoptions."""
    
    adoptions: List[Dict[str, Any]] = Field(..., description="List of adoptions")
    total: int = Field(..., description="Total number of adoptions")


class AdoptionSearchResponse(BaseModel):
    """Response model for adoption search results."""
    
    adoptions: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")


class CountResponse(BaseModel):
    """Response model for count operations."""
    
    count: int = Field(..., description="Total count")


class DeleteResponse(BaseModel):
    """Response model for delete operations."""
    
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Success message")
    entity_id: str = Field(..., description="ID of deleted entity")


class ExistsResponse(BaseModel):
    """Response model for existence checks."""
    
    exists: bool = Field(..., description="Whether entity exists")
    entity_id: str = Field(..., description="Entity ID checked")


class TransitionResponse(BaseModel):
    """Response model for workflow transitions."""
    
    id: str = Field(..., description="Entity ID")
    message: str = Field(..., description="Transition result message")
    previousState: str = Field(..., description="Previous workflow state")
    newState: str = Field(..., description="New workflow state")


class TransitionsResponse(BaseModel):
    """Response model for available transitions."""
    
    entity_id: str = Field(..., description="Entity ID")
    available_transitions: List[str] = Field(..., description="Available transitions")
    current_state: Optional[str] = Field(None, description="Current state")


class ErrorResponse(BaseModel):
    """Response model for errors."""
    
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class ValidationErrorResponse(BaseModel):
    """Response model for validation errors."""
    
    error: str = Field(..., description="Validation error message")
    code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
