"""
Request Models for Pet Store Performance Analysis System API endpoints.

Provides comprehensive validation models for all API operations including
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


class ValidationErrorResponse(BaseModel):
    """Validation error response model."""

    error: str = Field(..., description="Validation error message")
    field_errors: Optional[Dict[str, List[str]]] = Field(
        default=None, description="Field-specific validation errors"
    )
    code: str = Field(default="VALIDATION_ERROR", description="Error code")


# Product specific models
class ProductQueryParams(BaseModel):
    """Query parameters for Product endpoints."""

    category: Optional[str] = Field(
        default=None, description="Filter by category", pattern=r"^[A-Z_]+$"
    )
    stock_status: Optional[str] = Field(
        default=None, alias="stockStatus", description="Filter by stock status"
    )
    state: Optional[str] = Field(
        default=None, description="Filter by workflow state", pattern=r"^[a-z_]+$"
    )
    min_performance_score: Optional[float] = Field(
        default=None,
        alias="minPerformanceScore",
        description="Minimum performance score",
        ge=0,
        le=100,
    )
    max_performance_score: Optional[float] = Field(
        default=None,
        alias="maxPerformanceScore",
        description="Maximum performance score",
        ge=0,
        le=100,
    )
    limit: int = Field(default=50, description="Number of results", ge=1, le=1000)
    offset: int = Field(default=0, description="Pagination offset", ge=0)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed_categories = [
            "DOGS",
            "CATS",
            "BIRDS",
            "FISH",
            "REPTILES",
            "SMALL_PETS",
            "ACCESSORIES",
            "FOOD",
            "TOYS",
            "HEALTH",
        ]
        if v not in allowed_categories:
            raise ValueError(f"Category must be one of: {allowed_categories}")
        return v

    @field_validator("stock_status")
    @classmethod
    def validate_stock_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed_statuses = [
            "IN_STOCK",
            "LOW_STOCK",
            "OUT_OF_STOCK",
            "RESTOCK_NEEDED",
            "UNKNOWN",
        ]
        if v not in allowed_statuses:
            raise ValueError(f"Stock status must be one of: {allowed_statuses}")
        return v


class ProductUpdateQueryParams(BaseModel):
    """Query parameters for Product update operations."""

    transition: Optional[str] = Field(
        default=None, description="Workflow transition to trigger", pattern=r"^[a-z_]+$"
    )


# Report specific models
class ReportQueryParams(BaseModel):
    """Query parameters for Report endpoints."""

    report_type: Optional[str] = Field(
        default=None, alias="reportType", description="Filter by report type"
    )
    email_sent: Optional[bool] = Field(
        default=None, alias="emailSent", description="Filter by email sent status"
    )
    state: Optional[str] = Field(
        default=None, description="Filter by workflow state", pattern=r"^[a-z_]+$"
    )
    generated_after: Optional[str] = Field(
        default=None,
        alias="generatedAfter",
        description="Filter reports generated after this date",
    )
    limit: int = Field(default=50, description="Number of results", ge=1, le=1000)
    offset: int = Field(default=0, description="Pagination offset", ge=0)

    @field_validator("report_type")
    @classmethod
    def validate_report_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed_types = [
            "WEEKLY_SUMMARY",
            "MONTHLY_ANALYSIS",
            "CUSTOM",
            "PERFORMANCE_ANALYSIS",
            "INVENTORY_REPORT",
        ]
        if v not in allowed_types:
            raise ValueError(f"Report type must be one of: {allowed_types}")
        return v


class ReportUpdateQueryParams(BaseModel):
    """Query parameters for Report update operations."""

    transition: Optional[str] = Field(
        default=None, description="Workflow transition to trigger", pattern=r"^[a-z_]+$"
    )


# EmailNotification specific models
class EmailNotificationQueryParams(BaseModel):
    """Query parameters for EmailNotification endpoints."""

    recipient_email: Optional[str] = Field(
        default=None, alias="recipientEmail", description="Filter by recipient email"
    )
    email_type: Optional[str] = Field(
        default=None, alias="emailType", description="Filter by email type"
    )
    status: Optional[str] = Field(default=None, description="Filter by email status")
    priority: Optional[str] = Field(default=None, description="Filter by priority")
    state: Optional[str] = Field(
        default=None, description="Filter by workflow state", pattern=r"^[a-z_]+$"
    )
    report_id: Optional[str] = Field(
        default=None, alias="reportId", description="Filter by associated report ID"
    )
    limit: int = Field(default=50, description="Number of results", ge=1, le=1000)
    offset: int = Field(default=0, description="Pagination offset", ge=0)

    @field_validator("email_type")
    @classmethod
    def validate_email_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed_types = [
            "REPORT_NOTIFICATION",
            "ALERT",
            "SUMMARY",
            "WEEKLY_REPORT",
            "MONTHLY_REPORT",
        ]
        if v not in allowed_types:
            raise ValueError(f"Email type must be one of: {allowed_types}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed_statuses = ["PENDING", "SENT", "FAILED", "DELIVERED", "CANCELLED"]
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {allowed_statuses}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed_priorities = ["LOW", "NORMAL", "HIGH", "URGENT"]
        if v not in allowed_priorities:
            raise ValueError(f"Priority must be one of: {allowed_priorities}")
        return v


class EmailNotificationUpdateQueryParams(BaseModel):
    """Query parameters for EmailNotification update operations."""

    transition: Optional[str] = Field(
        default=None, description="Workflow transition to trigger", pattern=r"^[a-z_]+$"
    )


# Common request models
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
        allowed_transitions = [
            "create",
            "validate",
            "extract_data",
            "analyze",
            "generate",
            "email",
            "send",
            "complete",
        ]
        if v not in allowed_transitions:
            raise ValueError(f"Transition must be one of: {allowed_transitions}")
        return v


class SearchRequest(BaseModel):
    """Request model for entity search operations."""

    # Product search fields
    name: Optional[str] = Field(default=None, description="Filter by product name")
    category: Optional[str] = Field(default=None, description="Filter by category")
    stock_status: Optional[str] = Field(
        default=None, alias="stockStatus", description="Filter by stock status"
    )
    min_performance_score: Optional[float] = Field(
        default=None,
        alias="minPerformanceScore",
        description="Minimum performance score",
    )

    # Report search fields
    title: Optional[str] = Field(default=None, description="Filter by report title")
    report_type: Optional[str] = Field(
        default=None, alias="reportType", description="Filter by report type"
    )
    email_sent: Optional[bool] = Field(
        default=None, alias="emailSent", description="Filter by email sent status"
    )

    # EmailNotification search fields
    recipient_email: Optional[str] = Field(
        default=None, alias="recipientEmail", description="Filter by recipient email"
    )
    email_type: Optional[str] = Field(
        default=None, alias="emailType", description="Filter by email type"
    )
    status: Optional[str] = Field(default=None, description="Filter by status")

    # Common fields
    state: Optional[str] = Field(default=None, description="Filter by workflow state")


# Bulk operation models
class BulkProductAnalysisRequest(BaseModel):
    """Request model for bulk product analysis operations."""

    product_ids: List[str] = Field(
        ..., alias="productIds", description="List of product IDs to analyze"
    )
    force_reanalysis: bool = Field(
        default=False,
        alias="forceReanalysis",
        description="Force re-analysis of already analyzed products",
    )

    @field_validator("product_ids")
    @classmethod
    def validate_product_ids(cls, v: List[str]) -> List[str]:
        if not v or len(v) == 0:
            raise ValueError("Product IDs list cannot be empty")
        if len(v) > 100:
            raise ValueError("Cannot analyze more than 100 products at once")
        return v


class BulkReportGenerationRequest(BaseModel):
    """Request model for bulk report generation operations."""

    report_type: str = Field(
        ..., alias="reportType", description="Type of reports to generate"
    )
    data_period_start: str = Field(
        ..., alias="dataPeriodStart", description="Start date for report data period"
    )
    data_period_end: str = Field(
        ..., alias="dataPeriodEnd", description="End date for report data period"
    )
    email_recipients: List[str] = Field(
        ..., alias="emailRecipients", description="List of email recipients"
    )

    @field_validator("report_type")
    @classmethod
    def validate_report_type(cls, v: str) -> str:
        allowed_types = [
            "WEEKLY_SUMMARY",
            "MONTHLY_ANALYSIS",
            "CUSTOM",
            "PERFORMANCE_ANALYSIS",
            "INVENTORY_REPORT",
        ]
        if v not in allowed_types:
            raise ValueError(f"Report type must be one of: {allowed_types}")
        return v

    @field_validator("email_recipients")
    @classmethod
    def validate_email_recipients(cls, v: List[str]) -> List[str]:
        if not v or len(v) == 0:
            raise ValueError("Email recipients list cannot be empty")
        for email in v:
            if not email or "@" not in email:
                raise ValueError(f"Invalid email address: {email}")
        return v
