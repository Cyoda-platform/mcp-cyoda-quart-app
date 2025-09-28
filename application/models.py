"""
API Models for Cyoda Client Application

Defines Pydantic models for API requests and responses.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Base response models
class ErrorResponse(BaseModel):
    error: str
    code: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    error: str
    code: str = "VALIDATION_ERROR"


class DeleteResponse(BaseModel):
    success: bool
    message: str
    entity_id: str = Field(alias="entityId")


class ExistsResponse(BaseModel):
    exists: bool
    entity_id: str = Field(alias="entityId")


class CountResponse(BaseModel):
    count: int


# Comment-related models
class CommentResponse(BaseModel):
    """Response model for Comment entity"""
    pass  # Will use Comment entity directly


class CommentListResponse(BaseModel):
    comments: List[Dict[str, Any]]
    total: int


class CommentSearchResponse(BaseModel):
    comments: List[Dict[str, Any]]
    total: int


class CommentQueryParams(BaseModel):
    post_id: Optional[int] = Field(None, alias="postId")
    sentiment_label: Optional[str] = Field(None, alias="sentimentLabel")
    state: Optional[str] = None
    offset: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)


class CommentUpdateQueryParams(BaseModel):
    transition: Optional[str] = None


# CommentAnalysisReport-related models
class ReportResponse(BaseModel):
    """Response model for CommentAnalysisReport entity"""
    pass  # Will use CommentAnalysisReport entity directly


class ReportListResponse(BaseModel):
    reports: List[Dict[str, Any]]
    total: int


class ReportSearchResponse(BaseModel):
    reports: List[Dict[str, Any]]
    total: int


class ReportQueryParams(BaseModel):
    post_id: Optional[int] = Field(None, alias="postId")
    email_sent: Optional[bool] = Field(None, alias="emailSent")
    state: Optional[str] = None
    offset: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)


class ReportUpdateQueryParams(BaseModel):
    transition: Optional[str] = None


# Search and transition models
class SearchRequest(BaseModel):
    """Generic search request model"""
    pass  # Will be populated with search fields dynamically


class TransitionRequest(BaseModel):
    transition_name: str = Field(alias="transitionName")


class TransitionResponse(BaseModel):
    id: str
    message: str
    previous_state: Optional[str] = Field(None, alias="previousState")
    new_state: Optional[str] = Field(None, alias="newState")


class TransitionsResponse(BaseModel):
    entity_id: str = Field(alias="entityId")
    available_transitions: List[str] = Field(alias="availableTransitions")
    current_state: Optional[str] = Field(None, alias="currentState")


# JSONPlaceholder API models
class JSONPlaceholderComment(BaseModel):
    """Model for comments from JSONPlaceholder API"""
    postId: int
    id: int
    name: str
    email: str
    body: str


class CommentIngestionRequest(BaseModel):
    """Request model for ingesting comments from JSONPlaceholder API"""
    post_id: int = Field(alias="postId")
    recipient_email: str = Field(alias="recipientEmail")


class CommentIngestionResponse(BaseModel):
    """Response model for comment ingestion"""
    success: bool
    message: str
    post_id: int = Field(alias="postId")
    comments_ingested: int = Field(alias="commentsIngested")
    report_id: Optional[str] = Field(None, alias="reportId")
