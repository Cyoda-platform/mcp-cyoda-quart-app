"""
Request Models for Comment Analysis API endpoints.

Provides comprehensive validation models for all API operations including
query parameters, request bodies, and response schemas.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

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


# CommentAnalysisRequest specific models
class CommentAnalysisRequestQueryParams(BaseModel):
    """Query parameters for CommentAnalysisRequest endpoints."""

    state: Optional[str] = Field(
        default=None, description="Filter by state", pattern=r"^[a-z_]+$"
    )
    post_id: Optional[int] = Field(
        default=None, alias="postId", description="Filter by post ID", ge=1
    )
    page: int = Field(default=0, description="Page number for pagination", ge=0)
    size: int = Field(default=20, description="Page size for pagination", ge=1, le=100)

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed_states = [
            "pending",
            "fetching_comments",
            "analyzing",
            "sending_report",
            "completed",
            "failed",
        ]
        if v not in allowed_states:
            raise ValueError(f"State must be one of: {allowed_states}")
        return v


class CommentAnalysisRequestUpdateQueryParams(BaseModel):
    """Query parameters for CommentAnalysisRequest update operations."""

    transition: Optional[str] = Field(
        default=None, description="Workflow transition to trigger", pattern=r"^[a-z_]+$"
    )


# Comment specific models
class CommentQueryParams(BaseModel):
    """Query parameters for Comment endpoints."""

    analysis_request_id: Optional[str] = Field(
        default=None,
        alias="analysisRequestId",
        description="Filter by analysis request ID",
    )
    post_id: Optional[int] = Field(
        default=None, alias="postId", description="Filter by post ID", ge=1
    )
    page: int = Field(default=0, description="Page number for pagination", ge=0)
    size: int = Field(default=50, description="Page size for pagination", ge=1, le=100)


# AnalysisReport specific models
class AnalysisReportQueryParams(BaseModel):
    """Query parameters for AnalysisReport endpoints."""

    analysis_request_id: Optional[str] = Field(
        default=None,
        alias="analysisRequestId",
        description="Filter by analysis request ID",
    )
    state: Optional[str] = Field(
        default=None, description="Filter by state", pattern=r"^[a-z_]+$"
    )
    page: int = Field(default=0, description="Page number for pagination", ge=0)
    size: int = Field(default=20, description="Page size for pagination", ge=1, le=100)

    @field_validator("state")
    @classmethod
    def validate_state(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed_states = ["generated", "sending", "sent", "failed"]
        if v not in allowed_states:
            raise ValueError(f"State must be one of: {allowed_states}")
        return v


class AnalysisReportUpdateQueryParams(BaseModel):
    """Query parameters for AnalysisReport update operations."""

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
        # Allow common transition patterns - validation logic below
        # Basic validation - in real implementation, this would be more comprehensive
        if (
            not v.startswith("transition_")
            and not v.endswith("_retry")
            and "failed_to_" not in v
        ):
            raise ValueError("Invalid transition name format")
        return v


class SearchRequest(BaseModel):
    """Request model for search operations."""

    query: Dict[str, Any] = Field(..., description="Search query parameters")
    limit: int = Field(default=50, description="Number of results", ge=1, le=1000)
    offset: int = Field(default=0, description="Pagination offset", ge=0)

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(v, dict):
            raise ValueError("Query must be a dictionary")
        return v
