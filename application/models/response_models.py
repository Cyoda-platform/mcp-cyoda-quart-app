"""
Response Models for Comment Analysis API endpoints.

Provides comprehensive response schemas for all API operations with proper
validation and documentation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional error details"
    )
    code: Optional[str] = Field(default=None, description="Error code")
    timestamp: Optional[str] = Field(default=None, description="Error timestamp")


class ValidationErrorResponse(BaseModel):
    """Validation error response model."""

    error: str = Field(..., description="Validation error message")
    field_errors: Optional[Dict[str, List[str]]] = Field(
        default=None, description="Field-specific validation errors"
    )
    code: str = Field(default="VALIDATION_ERROR", description="Error code")


class SuccessResponse(BaseModel):
    """Standard success response model."""

    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")


# CommentAnalysisRequest Response Models
class CommentAnalysisRequestResponse(BaseModel):
    """Response model for CommentAnalysisRequest operations."""

    id: str = Field(..., description="Entity ID")
    post_id: int = Field(..., alias="postId", description="Post ID")
    recipient_email: str = Field(
        ..., alias="recipientEmail", description="Recipient email"
    )
    requested_at: Optional[str] = Field(
        default=None, alias="requestedAt", description="Request timestamp"
    )
    completed_at: Optional[str] = Field(
        default=None, alias="completedAt", description="Completion timestamp"
    )
    error_message: Optional[str] = Field(
        default=None, alias="errorMessage", description="Error message"
    )
    state: str = Field(..., description="Current workflow state")


class CommentAnalysisRequestListResponse(BaseModel):
    """Response model for CommentAnalysisRequest list operations."""

    content: List[CommentAnalysisRequestResponse] = Field(
        ..., description="List of requests"
    )
    total_elements: int = Field(
        ..., alias="totalElements", description="Total number of elements"
    )
    total_pages: int = Field(
        ..., alias="totalPages", description="Total number of pages"
    )
    size: int = Field(..., description="Page size")
    number: int = Field(..., description="Current page number")


class CommentAnalysisRequestSearchResponse(BaseModel):
    """Response model for CommentAnalysisRequest search operations."""

    entities: List[CommentAnalysisRequestResponse] = Field(
        ..., description="Search results"
    )
    total: int = Field(..., description="Total number of results")


# Comment Response Models
class CommentResponse(BaseModel):
    """Response model for Comment operations."""

    id: int = Field(..., description="Comment ID")
    post_id: int = Field(..., alias="postId", description="Post ID")
    name: str = Field(..., description="Comment name/title")
    email: str = Field(..., description="Author email")
    body: str = Field(..., description="Comment body")
    analysis_request_id: Optional[str] = Field(
        default=None, alias="analysisRequestId", description="Analysis request ID"
    )
    fetched_at: Optional[str] = Field(
        default=None, alias="fetchedAt", description="Fetch timestamp"
    )
    state: Optional[str] = Field(default=None, description="Entity state")


class CommentListResponse(BaseModel):
    """Response model for Comment list operations."""

    content: List[CommentResponse] = Field(..., description="List of comments")
    total_elements: int = Field(
        ..., alias="totalElements", description="Total number of elements"
    )
    total_pages: int = Field(
        ..., alias="totalPages", description="Total number of pages"
    )
    size: int = Field(..., description="Page size")
    number: int = Field(..., description="Current page number")


# AnalysisReport Response Models
class AnalysisReportResponse(BaseModel):
    """Response model for AnalysisReport operations."""

    id: str = Field(..., description="Report ID")
    analysis_request_id: str = Field(
        ..., alias="analysisRequestId", description="Analysis request ID"
    )
    total_comments: int = Field(
        ..., alias="totalComments", description="Total comments analyzed"
    )
    average_comment_length: float = Field(
        ..., alias="averageCommentLength", description="Average comment length"
    )
    most_active_email_domain: str = Field(
        ..., alias="mostActiveEmailDomain", description="Most active email domain"
    )
    sentiment_summary: str = Field(
        ..., alias="sentimentSummary", description="Sentiment summary"
    )
    top_keywords: str = Field(..., alias="topKeywords", description="Top keywords JSON")
    generated_at: Optional[str] = Field(
        default=None, alias="generatedAt", description="Generation timestamp"
    )
    email_sent_at: Optional[str] = Field(
        default=None, alias="emailSentAt", description="Email sent timestamp"
    )
    state: str = Field(..., description="Current workflow state")


class AnalysisReportListResponse(BaseModel):
    """Response model for AnalysisReport list operations."""

    content: List[AnalysisReportResponse] = Field(..., description="List of reports")
    total_elements: int = Field(
        ..., alias="totalElements", description="Total number of elements"
    )
    total_pages: int = Field(
        ..., alias="totalPages", description="Total number of pages"
    )
    size: int = Field(..., description="Page size")
    number: int = Field(..., description="Current page number")


# Common Response Models
class DeleteResponse(BaseModel):
    """Response model for delete operations."""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Success message")
    entity_id: str = Field(..., alias="entityId", description="Deleted entity ID")


class ExistsResponse(BaseModel):
    """Response model for existence check operations."""

    exists: bool = Field(..., description="Entity existence status")
    entity_id: str = Field(..., alias="entityId", description="Checked entity ID")


class CountResponse(BaseModel):
    """Response model for count operations."""

    count: int = Field(..., description="Total count")


class TransitionResponse(BaseModel):
    """Response model for transition operations."""

    id: str = Field(..., description="Entity ID")
    message: str = Field(..., description="Transition message")
    previous_state: Optional[str] = Field(
        default=None, alias="previousState", description="Previous state"
    )
    new_state: str = Field(..., alias="newState", description="New state")


class TransitionsResponse(BaseModel):
    """Response model for available transitions."""

    entity_id: str = Field(..., alias="entityId", description="Entity ID")
    available_transitions: List[str] = Field(
        ..., alias="availableTransitions", description="Available transitions"
    )
    current_state: Optional[str] = Field(
        default=None, alias="currentState", description="Current state"
    )
