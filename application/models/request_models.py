"""
Request models for Cat Fact Subscription Application API.

Provides Pydantic models for request validation and query parameters.
"""

from typing import Optional

from pydantic import BaseModel, Field


class EntityIdParam(BaseModel):
    """Entity ID parameter model"""
    entity_id: str = Field(..., description="Entity ID")


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class SuccessResponse(BaseModel):
    """Standard success response model"""
    success: bool = Field(True, description="Success status")
    message: str = Field(..., description="Success message")


class TransitionRequest(BaseModel):
    """Request model for workflow transitions"""
    transition_name: str = Field(..., alias="transitionName", description="Name of the transition to execute")


class SearchRequest(BaseModel):
    """Generic search request model"""
    name: Optional[str] = Field(None, description="Search by name")
    category: Optional[str] = Field(None, description="Search by category")
    status: Optional[str] = Field(None, description="Search by status")


# Subscriber-specific models
class SubscriberQueryParams(BaseModel):
    """Query parameters for subscriber listing"""
    subscription_status: Optional[str] = Field(None, alias="subscriptionStatus", description="Filter by subscription status")
    state: Optional[str] = Field(None, description="Filter by workflow state")
    offset: int = Field(0, description="Pagination offset")
    limit: int = Field(50, description="Pagination limit")


class SubscriberUpdateQueryParams(BaseModel):
    """Query parameters for subscriber updates"""
    transition: Optional[str] = Field(None, description="Workflow transition to execute")


class SubscriberSearchRequest(BaseModel):
    """Search request for subscribers"""
    email: Optional[str] = Field(None, description="Search by email")
    subscription_status: Optional[str] = Field(None, alias="subscriptionStatus", description="Search by subscription status")
    first_name: Optional[str] = Field(None, alias="firstName", description="Search by first name")
    last_name: Optional[str] = Field(None, alias="lastName", description="Search by last name")


# CatFact-specific models
class CatFactQueryParams(BaseModel):
    """Query parameters for cat fact listing"""
    source: Optional[str] = Field(None, description="Filter by source")
    is_used: Optional[bool] = Field(None, alias="isUsed", description="Filter by usage status")
    is_appropriate: Optional[bool] = Field(None, alias="isAppropriate", description="Filter by appropriateness")
    state: Optional[str] = Field(None, description="Filter by workflow state")
    offset: int = Field(0, description="Pagination offset")
    limit: int = Field(50, description="Pagination limit")


class CatFactUpdateQueryParams(BaseModel):
    """Query parameters for cat fact updates"""
    transition: Optional[str] = Field(None, description="Workflow transition to execute")


class CatFactSearchRequest(BaseModel):
    """Search request for cat facts"""
    fact_text: Optional[str] = Field(None, alias="factText", description="Search in fact text")
    source: Optional[str] = Field(None, description="Search by source")
    is_used: Optional[bool] = Field(None, alias="isUsed", description="Search by usage status")
    is_appropriate: Optional[bool] = Field(None, alias="isAppropriate", description="Search by appropriateness")


# EmailCampaign-specific models
class EmailCampaignQueryParams(BaseModel):
    """Query parameters for email campaign listing"""
    status: Optional[str] = Field(None, description="Filter by campaign status")
    campaign_date: Optional[str] = Field(None, alias="campaignDate", description="Filter by campaign date")
    state: Optional[str] = Field(None, description="Filter by workflow state")
    offset: int = Field(0, description="Pagination offset")
    limit: int = Field(50, description="Pagination limit")


class EmailCampaignUpdateQueryParams(BaseModel):
    """Query parameters for email campaign updates"""
    transition: Optional[str] = Field(None, description="Workflow transition to execute")


class EmailCampaignSearchRequest(BaseModel):
    """Search request for email campaigns"""
    campaign_name: Optional[str] = Field(None, alias="campaignName", description="Search by campaign name")
    status: Optional[str] = Field(None, description="Search by status")
    campaign_date: Optional[str] = Field(None, alias="campaignDate", description="Search by campaign date")
    cat_fact_id: Optional[str] = Field(None, alias="catFactId", description="Search by cat fact ID")
