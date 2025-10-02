"""
Request models for Cat Fact Subscription Application.

Provides request and query parameter models for API validation.
"""

from typing import Optional

from pydantic import BaseModel, Field


class SubscriberQueryParams(BaseModel):
    """Query parameters for listing subscribers"""

    is_active: Optional[bool] = Field(default=None, alias="isActive")
    state: Optional[str] = Field(default=None)
    subscription_source: Optional[str] = Field(default=None, alias="subscriptionSource")
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=1000)


class SubscriberUpdateQueryParams(BaseModel):
    """Query parameters for updating subscribers"""

    transition: Optional[str] = Field(default=None)


class CatFactQueryParams(BaseModel):
    """Query parameters for listing cat facts"""

    is_used_for_delivery: Optional[bool] = Field(
        default=None, alias="isUsedForDelivery"
    )
    is_appropriate: Optional[bool] = Field(default=None, alias="isAppropriate")
    state: Optional[str] = Field(default=None)
    source_api: Optional[str] = Field(default=None, alias="sourceApi")
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=1000)


class CatFactUpdateQueryParams(BaseModel):
    """Query parameters for updating cat facts"""

    transition: Optional[str] = Field(default=None)


class EmailCampaignQueryParams(BaseModel):
    """Query parameters for listing email campaigns"""

    campaign_type: Optional[str] = Field(default=None, alias="campaignType")
    state: Optional[str] = Field(default=None)
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=1000)


class EmailCampaignUpdateQueryParams(BaseModel):
    """Query parameters for updating email campaigns"""

    transition: Optional[str] = Field(default=None)


class SearchRequest(BaseModel):
    """Generic search request model"""

    email: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    category: Optional[str] = Field(default=None)
    state: Optional[str] = Field(default=None)


class TransitionRequest(BaseModel):
    """Request model for triggering workflow transitions"""

    transition_name: str = Field(..., alias="transitionName")


class ErrorResponse(BaseModel):
    """Error response model"""

    error: str
    code: Optional[str] = None


class SuccessResponse(BaseModel):
    """Success response model"""

    success: bool = True
    message: str
