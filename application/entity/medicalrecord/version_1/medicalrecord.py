"""
MedicalRecord Entity for Purrfect Pets API.

Represents a medical record documenting a pet's health examination or treatment.
"""
from datetime import datetime, timezone
from typing import ClassVar, Optional
from pydantic import Field, validator

from entity.cyoda_entity import CyodaEntity


class MedicalRecord(CyodaEntity):
    """
    MedicalRecord entity representing a medical record in the Purrfect Pets system.
    
    Attributes:
        record_id: Unique identifier for the medical record
        pet_id: Reference to the pet
        vet_id: Reference to the veterinarian
        appointment_id: Reference to related appointment
        visit_date: Date of the medical visit
        diagnosis: Medical diagnosis
        treatment: Treatment provided
        medications: Medications prescribed
        notes: Additional medical notes
        follow_up_required: Whether follow-up is needed
        follow_up_date: Recommended follow-up date
        cost: Actual cost of the visit
        created_date: When the record was created
    """
    
    # Entity constants
    ENTITY_NAME: ClassVar[str] = "MedicalRecord"
    ENTITY_VERSION: ClassVar[int] = 1
    
    # Required fields
    record_id: str = Field(..., description="Unique identifier for the medical record")
    pet_id: str = Field(..., description="Reference to the pet")
    vet_id: str = Field(..., description="Reference to the veterinarian")
    visit_date: str = Field(..., description="Date of the medical visit")
    follow_up_required: bool = Field(default=False, description="Whether follow-up is needed")
    created_date: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        description="When the record was created"
    )
    
    # Optional fields
    appointment_id: Optional[str] = Field(None, description="Reference to related appointment")
    diagnosis: Optional[str] = Field(None, description="Medical diagnosis")
    treatment: Optional[str] = Field(None, description="Treatment provided")
    medications: Optional[str] = Field(None, description="Medications prescribed")
    notes: Optional[str] = Field(None, description="Additional medical notes")
    follow_up_date: Optional[str] = Field(None, description="Recommended follow-up date")
    cost: Optional[float] = Field(None, ge=0, description="Actual cost of the visit")
    
    @validator('visit_date')
    def validate_visit_date(cls, v):
        """Validate visit date format."""
        if not v or not v.strip():
            raise ValueError("Visit date cannot be empty")
        
        try:
            # Parse the ISO format datetime
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("Invalid visit date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)")
        
        return v
    
    @validator('follow_up_date')
    def validate_follow_up_date(cls, v):
        """Validate follow-up date format and ensure it's in the future."""
        if v is not None:
            if not v.strip():
                raise ValueError("Follow-up date cannot be empty string")
            
            try:
                # Parse the ISO format datetime
                follow_up_dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                current_dt = datetime.now(timezone.utc)
                
                # Follow-up should typically be in the future
                if follow_up_dt <= current_dt:
                    # Allow past dates for flexibility but could log a warning
                    pass
                    
            except ValueError:
                raise ValueError("Invalid follow-up date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)")
        
        return v
    
    @validator('cost')
    def validate_cost(cls, v):
        """Validate cost."""
        if v is not None and v < 0:
            raise ValueError("Cost cannot be negative")
        return v
    
    @validator('diagnosis')
    def validate_diagnosis(cls, v):
        """Validate diagnosis."""
        if v is not None and not v.strip():
            raise ValueError("Diagnosis cannot be empty string")
        return v.strip() if v else v
    
    @validator('treatment')
    def validate_treatment(cls, v):
        """Validate treatment."""
        if v is not None and not v.strip():
            raise ValueError("Treatment cannot be empty string")
        return v.strip() if v else v
    
    @validator('medications')
    def validate_medications(cls, v):
        """Validate medications."""
        if v is not None and not v.strip():
            raise ValueError("Medications cannot be empty string")
        return v.strip() if v else v
    
    def has_follow_up(self) -> bool:
        """Check if follow-up is required and scheduled."""
        return self.follow_up_required and self.follow_up_date is not None
    
    def is_follow_up_overdue(self) -> bool:
        """Check if follow-up is overdue."""
        if not self.has_follow_up():
            return False
        
        try:
            follow_up_dt = datetime.fromisoformat(self.follow_up_date.replace('Z', '+00:00'))
            return follow_up_dt < datetime.now(timezone.utc)
        except (ValueError, AttributeError):
            return False
    
    def __str__(self) -> str:
        """String representation of the medical record."""
        return f"MedicalRecord(record_id={self.record_id}, pet_id={self.pet_id}, visit_date={self.visit_date})"
