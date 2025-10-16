# entity/task/version_1/task.py

"""
Task Entity for Cyoda Client Application

Represents a task with basic workflow functionality including validation
and processing capabilities for task management.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class Task(CyodaEntity):
    """
    Task represents a work item that can be managed through a workflow.
    
    Inherits from CyodaEntity to get common fields like entity_id, state, etc.
    The state field manages workflow states: initial_state -> created -> validated -> processed -> completed
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Task"
    ENTITY_VERSION: ClassVar[int] = 1

    # Required fields
    title: str = Field(..., description="Title of the task")
    description: str = Field(..., description="Description of the task")
    priority: str = Field(..., description="Priority level of the task")
    
    # Optional fields
    assignee: Optional[str] = Field(
        default=None,
        description="Person assigned to the task"
    )
    due_date: Optional[str] = Field(
        default=None,
        alias="dueDate",
        description="Due date for the task (ISO 8601 format)"
    )
    
    # Timestamps (inherited created_at from CyodaEntity)
    created_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="createdAt",
        description="Timestamp when the task was created (ISO 8601 format)",
    )
    updated_at: Optional[str] = Field(
        default=None,
        alias="updatedAt",
        description="Timestamp when the task was last updated (ISO 8601 format)",
    )

    # Processing-related fields (populated during processing)
    processed_data: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="processedData",
        description="Data that gets populated during processing",
    )
    validation_result: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="validationResult",
        description="Result of validation checks",
    )

    # Validation rules
    ALLOWED_PRIORITIES: ClassVar[List[str]] = [
        "LOW",
        "MEDIUM", 
        "HIGH",
        "URGENT"
    ]

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Title must be non-empty")
        if len(v) < 3:
            raise ValueError("Title must be at least 3 characters long")
        if len(v) > 200:
            raise ValueError("Title must be at most 200 characters long")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description field"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Description must be non-empty")
        if len(v) > 1000:
            raise ValueError("Description must be at most 1000 characters long")
        return v.strip()

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate priority field"""
        if v not in cls.ALLOWED_PRIORITIES:
            raise ValueError(f"Priority must be one of: {cls.ALLOWED_PRIORITIES}")
        return v

    @model_validator(mode="after")
    def validate_business_logic(self) -> "Task":
        """Validate business logic rules"""
        priority = self.priority
        assignee = self.assignee

        # Business rule: URGENT tasks must have an assignee
        if priority == "URGENT" and not assignee:
            raise ValueError("URGENT priority tasks must have an assignee")

        return self

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current time"""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def set_processed_data(self, processed_data: Dict[str, Any]) -> None:
        """Set processed data and update timestamp"""
        self.processed_data = processed_data
        self.update_timestamp()

    def set_validation_result(self, validation_result: Dict[str, Any]) -> None:
        """Set validation result and update timestamp"""
        self.validation_result = validation_result
        self.update_timestamp()

    def is_ready_for_processing(self) -> bool:
        """Check if task is ready for processing (in validated state)"""
        return self.state == "validated"

    def is_processed(self) -> bool:
        """Check if task has been processed"""
        return self.state == "processed" or self.state == "completed"

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        # Add state for API compatibility
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
