"""
Response Models for Pet Store Performance Analysis System API endpoints.

Provides comprehensive response schemas for all API operations with proper
validation and documentation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Product Response Models
class ProductResponse(BaseModel):
    """Response model for Product operations."""

    entity_id: str = Field(..., description="Entity ID")
    technical_id: Optional[str] = Field(
        default=None, description="Technical ID from Cyoda"
    )
    name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    pet_store_id: Optional[str] = Field(
        default=None, alias="petStoreId", description="Pet Store API ID"
    )
    sales_volume: Optional[int] = Field(
        default=None, alias="salesVolume", description="Total units sold"
    )
    revenue: Optional[float] = Field(
        default=None, description="Total revenue generated"
    )
    inventory_level: Optional[int] = Field(
        default=None, alias="inventoryLevel", description="Current stock level"
    )
    stock_status: Optional[str] = Field(
        default=None, alias="stockStatus", description="Stock status"
    )
    performance_score: Optional[float] = Field(
        default=None, alias="performanceScore", description="Performance score (0-100)"
    )
    trend_analysis: Optional[Dict[str, Any]] = Field(
        default=None, alias="trendAnalysis", description="Trend analysis data"
    )
    state: str = Field(..., description="Current workflow state")
    created_at: Optional[str] = Field(
        default=None, alias="createdAt", description="Creation timestamp"
    )
    updated_at: Optional[str] = Field(
        default=None, alias="updatedAt", description="Last update timestamp"
    )
    data_extracted_at: Optional[str] = Field(
        default=None, alias="dataExtractedAt", description="Data extraction timestamp"
    )
    analyzed_at: Optional[str] = Field(
        default=None, alias="analyzedAt", description="Analysis completion timestamp"
    )


class ProductListResponse(BaseModel):
    """Response model for Product list operations."""

    entities: List[Dict[str, Any]] = Field(..., description="List of Product objects")
    total: int = Field(..., description="Total number of products")
    limit: Optional[int] = Field(default=None, description="Applied limit")
    offset: Optional[int] = Field(default=None, description="Applied offset")


class ProductSearchResponse(BaseModel):
    """Response model for Product search operations."""

    entities: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of matching products")
    query: Optional[Dict[str, Any]] = Field(
        default=None, description="Applied search query"
    )


# Report Response Models
class ReportResponse(BaseModel):
    """Response model for Report operations."""

    entity_id: str = Field(..., description="Entity ID")
    technical_id: Optional[str] = Field(
        default=None, description="Technical ID from Cyoda"
    )
    title: str = Field(..., description="Report title")
    report_type: str = Field(..., alias="reportType", description="Type of report")
    content: Optional[str] = Field(default=None, description="Generated report content")
    data_period_start: Optional[str] = Field(
        default=None, alias="dataPeriodStart", description="Data period start date"
    )
    data_period_end: Optional[str] = Field(
        default=None, alias="dataPeriodEnd", description="Data period end date"
    )
    generated_by: Optional[str] = Field(
        default=None, alias="generatedBy", description="Report generator"
    )
    insights: Optional[Dict[str, Any]] = Field(
        default=None, description="Key insights and findings"
    )
    summary_metrics: Optional[Dict[str, Any]] = Field(
        default=None, alias="summaryMetrics", description="Summary performance metrics"
    )
    product_highlights: Optional[List[Dict[str, Any]]] = Field(
        default=None, alias="productHighlights", description="Highlighted products"
    )
    email_recipients: Optional[List[str]] = Field(
        default=None, alias="emailRecipients", description="Email recipients"
    )
    email_sent: Optional[bool] = Field(
        default=None, alias="emailSent", description="Email sent status"
    )
    state: str = Field(..., description="Current workflow state")
    created_at: Optional[str] = Field(
        default=None, alias="createdAt", description="Creation timestamp"
    )
    updated_at: Optional[str] = Field(
        default=None, alias="updatedAt", description="Last update timestamp"
    )
    generated_at: Optional[str] = Field(
        default=None, alias="generatedAt", description="Generation timestamp"
    )
    emailed_at: Optional[str] = Field(
        default=None, alias="emailedAt", description="Email sent timestamp"
    )


class ReportListResponse(BaseModel):
    """Response model for Report list operations."""

    entities: List[Dict[str, Any]] = Field(..., description="List of Report objects")
    total: int = Field(..., description="Total number of reports")
    limit: Optional[int] = Field(default=None, description="Applied limit")
    offset: Optional[int] = Field(default=None, description="Applied offset")


class ReportSearchResponse(BaseModel):
    """Response model for Report search operations."""

    entities: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of matching reports")
    query: Optional[Dict[str, Any]] = Field(
        default=None, description="Applied search query"
    )


# EmailNotification Response Models
class EmailNotificationResponse(BaseModel):
    """Response model for EmailNotification operations."""

    entity_id: str = Field(..., description="Entity ID")
    technical_id: Optional[str] = Field(
        default=None, description="Technical ID from Cyoda"
    )
    recipient_email: str = Field(
        ..., alias="recipientEmail", description="Recipient email address"
    )
    subject: str = Field(..., description="Email subject")
    content: Optional[str] = Field(default=None, description="Email content")
    sender_email: Optional[str] = Field(
        default=None, alias="senderEmail", description="Sender email address"
    )
    email_type: str = Field(
        ..., alias="emailType", description="Type of email notification"
    )
    priority: str = Field(..., description="Email priority")
    report_id: Optional[str] = Field(
        default=None, alias="reportId", description="Associated report ID"
    )
    report_title: Optional[str] = Field(
        default=None, alias="reportTitle", description="Associated report title"
    )
    status: str = Field(..., description="Email status")
    delivery_attempts: int = Field(
        ..., alias="deliveryAttempts", description="Number of delivery attempts"
    )
    error_message: Optional[str] = Field(
        default=None, alias="errorMessage", description="Error message if failed"
    )
    state: str = Field(..., description="Current workflow state")
    created_at: Optional[str] = Field(
        default=None, alias="createdAt", description="Creation timestamp"
    )
    updated_at: Optional[str] = Field(
        default=None, alias="updatedAt", description="Last update timestamp"
    )
    scheduled_at: Optional[str] = Field(
        default=None, alias="scheduledAt", description="Scheduled send timestamp"
    )
    sent_at: Optional[str] = Field(
        default=None, alias="sentAt", description="Actual send timestamp"
    )
    delivered_at: Optional[str] = Field(
        default=None, alias="deliveredAt", description="Delivery confirmation timestamp"
    )


class EmailNotificationListResponse(BaseModel):
    """Response model for EmailNotification list operations."""

    entities: List[Dict[str, Any]] = Field(
        ..., description="List of EmailNotification objects"
    )
    total: int = Field(..., description="Total number of email notifications")
    limit: Optional[int] = Field(default=None, description="Applied limit")
    offset: Optional[int] = Field(default=None, description="Applied offset")


class EmailNotificationSearchResponse(BaseModel):
    """Response model for EmailNotification search operations."""

    entities: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of matching email notifications")
    query: Optional[Dict[str, Any]] = Field(
        default=None, description="Applied search query"
    )


# Workflow Response Models
class TransitionResponse(BaseModel):
    """Response model for workflow transition operations."""

    entity_id: str = Field(..., description="Entity ID")
    transition_name: str = Field(
        ..., alias="transitionName", description="Executed transition"
    )
    previous_state: str = Field(
        ..., alias="previousState", description="Previous workflow state"
    )
    current_state: str = Field(
        ..., alias="currentState", description="Current workflow state"
    )
    success: bool = Field(..., description="Transition success status")
    message: Optional[str] = Field(
        default=None, description="Transition result message"
    )
    timestamp: Optional[str] = Field(default=None, description="Transition timestamp")


class TransitionsResponse(BaseModel):
    """Response model for available transitions"""

    entity_id: str = Field(..., description="ID of the entity")
    available_transitions: List[str] = Field(
        ..., description="List of available transition names"
    )
    current_state: Optional[str] = Field(None, description="Current entity state")


# Common Response Models
class DeleteResponse(BaseModel):
    """Response model for entity deletion operations"""

    success: bool = Field(..., description="Whether the deletion was successful")
    message: str = Field(..., description="Deletion result message")
    entity_id: str = Field(..., description="ID of the deleted entity")


class ExistsResponse(BaseModel):
    """Response model for entity existence check"""

    exists: bool = Field(..., description="Whether the entity exists")
    entity_id: str = Field(..., description="ID of the checked entity")


class CountResponse(BaseModel):
    """Response model for entity count operations"""

    count: int = Field(..., description="Total number of entities")


# Analytics Response Models
class PerformanceAnalyticsResponse(BaseModel):
    """Response model for performance analytics operations."""

    total_products: int = Field(..., description="Total number of products analyzed")
    average_performance_score: float = Field(
        ..., description="Average performance score across all products"
    )
    high_performers: int = Field(..., description="Number of high-performing products")
    low_performers: int = Field(..., description="Number of low-performing products")
    out_of_stock: int = Field(..., description="Number of out-of-stock products")
    total_revenue: float = Field(..., description="Total revenue across all products")
    total_sales_volume: int = Field(..., description="Total sales volume")
    category_breakdown: Dict[str, Dict[str, Any]] = Field(
        ..., description="Performance breakdown by category"
    )
    top_performers: List[Dict[str, Any]] = Field(
        ..., description="Top performing products"
    )
    analysis_timestamp: str = Field(..., description="Analysis timestamp")


class ReportSummaryResponse(BaseModel):
    """Response model for report summary operations."""

    total_reports: int = Field(..., description="Total number of reports")
    reports_by_type: Dict[str, int] = Field(..., description="Report count by type")
    recent_reports: List[Dict[str, Any]] = Field(
        ..., description="Recently generated reports"
    )
    email_delivery_stats: Dict[str, int] = Field(
        ..., description="Email delivery statistics"
    )
    summary_timestamp: str = Field(..., description="Summary generation timestamp")
