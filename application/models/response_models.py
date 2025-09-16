"""
Response models for Application API endpoints.

Provides Pydantic models for response validation and documentation.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ValidationErrorResponse(BaseModel):
    """Response model for validation errors."""
    
    error: str = Field(..., description="Error message")
    code: str = Field(default="VALIDATION_ERROR", description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class DeleteResponse(BaseModel):
    """Response model for delete operations."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Success message")
    entity_id: str = Field(..., description="ID of the deleted entity")


class ExistsResponse(BaseModel):
    """Response model for existence checks."""
    
    exists: bool = Field(..., description="Whether the entity exists")
    entity_id: str = Field(..., description="ID of the entity checked")


class CountResponse(BaseModel):
    """Response model for count operations."""
    
    count: int = Field(..., description="Number of entities")


class TransitionResponse(BaseModel):
    """Response model for workflow transitions."""
    
    id: str = Field(..., description="Entity ID")
    message: str = Field(..., description="Transition result message")
    previousState: Optional[str] = Field(None, description="Previous entity state")
    newState: Optional[str] = Field(None, description="New entity state")


class TransitionsResponse(BaseModel):
    """Response model for available transitions."""
    
    entity_id: str = Field(..., description="Entity ID")
    available_transitions: List[str] = Field(..., description="List of available transitions")
    current_state: Optional[str] = Field(None, description="Current entity state")


# EggAlarm response models
class EggAlarmResponse(BaseModel):
    """Response model for single EggAlarm."""
    
    id: str = Field(..., description="Alarm ID")
    userId: str = Field(..., description="User ID")
    eggType: str = Field(..., description="Egg type")
    duration: int = Field(..., description="Duration in seconds")
    title: Optional[str] = Field(None, description="Alarm title")
    state: str = Field(..., description="Current state")
    isActive: bool = Field(..., description="Whether alarm is active")
    createdAt: str = Field(..., description="Creation timestamp")
    scheduledTime: Optional[str] = Field(None, description="Scheduled time")


class EggAlarmListResponse(BaseModel):
    """Response model for EggAlarm list."""
    
    alarms: List[Dict[str, Any]] = Field(..., description="List of alarms")
    total: int = Field(..., description="Total number of alarms")


class EggAlarmSearchResponse(BaseModel):
    """Response model for EggAlarm search."""
    
    alarms: List[Dict[str, Any]] = Field(..., description="List of matching alarms")
    total: int = Field(..., description="Total number of matching alarms")


# User response models
class UserResponse(BaseModel):
    """Response model for single User."""
    
    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    state: str = Field(..., description="Current state")
    createdAt: str = Field(..., description="Creation timestamp")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")


class UserListResponse(BaseModel):
    """Response model for User list."""
    
    users: List[Dict[str, Any]] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")


class UserSearchResponse(BaseModel):
    """Response model for User search."""
    
    users: List[Dict[str, Any]] = Field(..., description="List of matching users")
    total: int = Field(..., description="Total number of matching users")
