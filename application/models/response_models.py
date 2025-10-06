"""
Response Models for Booking and Report API endpoints.

Provides comprehensive response models for all API operations including
entity responses, list responses, and operation results.
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


class ValidationErrorResponse(BaseModel):
    """Validation error response model."""

    error: str = Field(..., description="Validation error message")
    code: str = Field(default="VALIDATION_ERROR", description="Error code")
    field_errors: Optional[Dict[str, List[str]]] = Field(
        default=None, alias="fieldErrors", description="Field-specific errors"
    )


class SuccessResponse(BaseModel):
    """Standard success response model."""

    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")


class BookingResponse(BaseModel):
    """Response model for single booking operations."""

    id: str = Field(..., description="Technical ID")
    booking_id: Optional[int] = Field(
        default=None, alias="bookingId", description="External booking ID"
    )
    firstname: str = Field(..., description="Guest first name")
    lastname: str = Field(..., description="Guest last name")
    totalprice: int = Field(..., description="Total price")
    depositpaid: bool = Field(..., description="Deposit payment status")
    bookingdates: Dict[str, str] = Field(
        ..., description="Check-in and check-out dates"
    )
    additionalneeds: Optional[str] = Field(default=None, description="Additional needs")
    state: str = Field(..., description="Current workflow state")
    retrieved_at: Optional[str] = Field(
        default=None, alias="retrievedAt", description="Retrieval timestamp"
    )
    nights_count: Optional[int] = Field(
        default=None, alias="nightsCount", description="Number of nights"
    )
    price_per_night: Optional[float] = Field(
        default=None, alias="pricePerNight", description="Price per night"
    )


class BookingListResponse(BaseModel):
    """Response model for booking list operations."""

    entities: List[Dict[str, Any]] = Field(..., description="List of booking entities")
    total: int = Field(..., description="Total number of bookings")
    limit: Optional[int] = Field(default=None, description="Applied limit")
    offset: Optional[int] = Field(default=None, description="Applied offset")


class BookingSearchResponse(BaseModel):
    """Response model for booking search operations."""

    entities: List[Dict[str, Any]] = Field(
        ..., description="List of matching booking entities"
    )
    total: int = Field(..., description="Total number of matches")
    search_criteria: Optional[Dict[str, Any]] = Field(
        default=None, alias="searchCriteria", description="Applied search criteria"
    )


class ReportResponse(BaseModel):
    """Response model for single report operations."""

    id: str = Field(..., description="Technical ID")
    title: str = Field(..., description="Report title")
    description: Optional[str] = Field(default=None, description="Report description")
    report_type: str = Field(..., alias="reportType", description="Report type")
    display_format: str = Field(
        ..., alias="displayFormat", description="Display format"
    )
    generated_at: str = Field(
        ..., alias="generatedAt", description="Generation timestamp"
    )
    generated_by: str = Field(..., alias="generatedBy", description="Generator")
    booking_count: int = Field(
        ..., alias="bookingCount", description="Number of bookings analyzed"
    )
    summary: Optional[Dict[str, Any]] = Field(
        default=None, description="Report summary statistics"
    )
    date_range_stats: Optional[List[Dict[str, Any]]] = Field(
        default=None, alias="dateRangeStats", description="Date range statistics"
    )
    filter_criteria: Optional[Dict[str, Any]] = Field(
        default=None, alias="filterCriteria", description="Applied filter criteria"
    )
    state: str = Field(..., description="Current workflow state")


class ReportListResponse(BaseModel):
    """Response model for report list operations."""

    entities: List[Dict[str, Any]] = Field(..., description="List of report entities")
    total: int = Field(..., description="Total number of reports")
    limit: Optional[int] = Field(default=None, description="Applied limit")
    offset: Optional[int] = Field(default=None, description="Applied offset")


class ReportSearchResponse(BaseModel):
    """Response model for report search operations."""

    entities: List[Dict[str, Any]] = Field(
        ..., description="List of matching report entities"
    )
    total: int = Field(..., description="Total number of matches")
    search_criteria: Optional[Dict[str, Any]] = Field(
        default=None, alias="searchCriteria", description="Applied search criteria"
    )


class CountResponse(BaseModel):
    """Response model for count operations."""

    count: int = Field(..., description="Total count")
    entity_type: Optional[str] = Field(
        default=None, alias="entityType", description="Type of entity counted"
    )


class ExistsResponse(BaseModel):
    """Response model for existence checks."""

    exists: bool = Field(..., description="Whether the entity exists")
    entity_id: str = Field(
        ..., alias="entityId", description="Entity ID that was checked"
    )


class DeleteResponse(BaseModel):
    """Response model for delete operations."""

    success: bool = Field(..., description="Whether the deletion was successful")
    message: str = Field(..., description="Deletion result message")
    entity_id: str = Field(
        ..., alias="entityId", description="ID of the deleted entity"
    )


class TransitionResponse(BaseModel):
    """Response model for workflow transitions."""

    id: str = Field(..., description="Entity ID")
    message: str = Field(..., description="Transition result message")
    previous_state: str = Field(
        ..., alias="previousState", description="Previous workflow state"
    )
    new_state: str = Field(..., alias="newState", description="New workflow state")
    transition_name: str = Field(
        ..., alias="transitionName", description="Name of the executed transition"
    )


class TransitionsResponse(BaseModel):
    """Response model for available transitions."""

    entity_id: str = Field(..., alias="entityId", description="Entity ID")
    current_state: Optional[str] = Field(
        default=None, alias="currentState", description="Current workflow state"
    )
    available_transitions: List[str] = Field(
        ..., alias="availableTransitions", description="List of available transitions"
    )


class BulkOperationResponse(BaseModel):
    """Response model for bulk operations."""

    total_processed: int = Field(
        ..., alias="totalProcessed", description="Total number of entities processed"
    )
    successful: int = Field(..., description="Number of successful operations")
    failed: int = Field(..., description="Number of failed operations")
    errors: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="List of errors for failed operations"
    )
    operation: str = Field(..., description="Operation that was performed")


class ReportDisplayResponse(BaseModel):
    """Response model for report display data."""

    title: str = Field(..., description="Report title")
    description: Optional[str] = Field(default=None, description="Report description")
    generated_at: str = Field(
        ..., alias="generatedAt", description="Generation timestamp"
    )
    summary: Dict[str, Any] = Field(..., description="Summary statistics")
    booking_count: int = Field(
        ..., alias="bookingCount", description="Number of bookings analyzed"
    )
    revenue_by_deposit: Dict[str, float] = Field(
        ..., alias="revenueByDeposit", description="Revenue breakdown by deposit status"
    )
    date_ranges: Optional[List[Dict[str, Any]]] = Field(
        default=None, alias="dateRanges", description="Date range statistics"
    )
    filters_applied: Optional[Dict[str, Any]] = Field(
        default=None, alias="filtersApplied", description="Applied filter criteria"
    )


class BookingStatsResponse(BaseModel):
    """Response model for booking statistics."""

    total_bookings: int = Field(
        ..., alias="totalBookings", description="Total number of bookings"
    )
    total_revenue: float = Field(..., alias="totalRevenue", description="Total revenue")
    average_booking_price: float = Field(
        ..., alias="averageBookingPrice", description="Average booking price"
    )
    deposit_paid_percentage: float = Field(
        ..., alias="depositPaidPercentage", description="Percentage with deposit paid"
    )
    average_nights_per_booking: float = Field(
        ..., alias="averageNightsPerBooking", description="Average nights per booking"
    )
    date_range: Optional[Dict[str, str]] = Field(
        default=None, alias="dateRange", description="Date range for statistics"
    )
