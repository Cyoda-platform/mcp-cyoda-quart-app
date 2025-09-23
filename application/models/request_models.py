"""
Request models for EggAlarm API endpoints.
"""

from typing import Optional

from pydantic import BaseModel, Field

from application.entity.egg_alarm.version_1.egg_alarm import AlarmStatus, EggType


class EggAlarmQueryParams(BaseModel):
    """Query parameters for listing EggAlarms"""

    egg_type: Optional[EggType] = Field(
        default=None, alias="eggType", description="Filter by egg type"
    )
    status: Optional[AlarmStatus] = Field(
        default=None, description="Filter by alarm status"
    )
    state: Optional[str] = Field(default=None, description="Filter by workflow state")
    created_by: Optional[str] = Field(
        default=None, alias="createdBy", description="Filter by creator"
    )
    limit: int = Field(
        default=50, ge=1, le=1000, description="Maximum number of results to return"
    )
    offset: int = Field(default=0, ge=0, description="Number of results to skip")


class EggAlarmUpdateQueryParams(BaseModel):
    """Query parameters for updating EggAlarms"""

    transition: Optional[str] = Field(
        default=None, description="Workflow transition to execute after update"
    )


class SearchRequest(BaseModel):
    """Request model for searching EggAlarms"""

    egg_type: Optional[EggType] = Field(
        default=None, alias="eggType", description="Search by egg type"
    )
    status: Optional[AlarmStatus] = Field(
        default=None, description="Search by alarm status"
    )
    created_by: Optional[str] = Field(
        default=None, alias="createdBy", description="Search by creator"
    )
    state: Optional[str] = Field(default=None, description="Search by workflow state")


class TransitionRequest(BaseModel):
    """Request model for triggering workflow transitions"""

    transition_name: str = Field(
        ..., alias="transitionName", description="Name of the transition to execute"
    )
