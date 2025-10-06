# entity/booking/version_1/booking.py

"""
Booking Entity for Restful Booker API Integration

Represents booking data retrieved from the Restful Booker API
(https://restful-booker.herokuapp.com/apidoc/index.html) with fields for
filtering and report generation as specified in functional requirements.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from common.entity.cyoda_entity import CyodaEntity


class BookingDates(CyodaEntity):
    """Nested model for booking check-in and check-out dates"""
    checkin: str = Field(..., description="Check-in date in YYYY-MM-DD format")
    checkout: str = Field(..., description="Check-out date in YYYY-MM-DD format")

    @field_validator("checkin", "checkout")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date format is YYYY-MM-DD"""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")


class Booking(CyodaEntity):
    """
    Booking entity represents booking data from the Restful Booker API.
    
    Used for retrieving, filtering, and generating reports on booking data
    including total revenue, average prices, and booking counts within date ranges.
    """

    # Entity constants
    ENTITY_NAME: ClassVar[str] = "Booking"
    ENTITY_VERSION: ClassVar[int] = 1

    # Core booking fields from Restful Booker API
    booking_id: Optional[int] = Field(
        default=None,
        alias="bookingId", 
        description="External booking ID from Restful Booker API"
    )
    firstname: str = Field(..., description="Guest first name")
    lastname: str = Field(..., description="Guest last name")
    totalprice: int = Field(..., description="Total price of the booking")
    depositpaid: bool = Field(..., description="Whether deposit has been paid")
    bookingdates: BookingDates = Field(..., description="Check-in and check-out dates")
    additionalneeds: Optional[str] = Field(
        default=None,
        description="Additional needs or requests"
    )

    # Processing and filtering fields
    retrieved_at: Optional[str] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        alias="retrievedAt",
        description="Timestamp when booking was retrieved from API"
    )
    
    # Report generation fields
    nights_count: Optional[int] = Field(
        default=None,
        alias="nightsCount",
        description="Number of nights calculated from booking dates"
    )
    price_per_night: Optional[float] = Field(
        default=None,
        alias="pricePerNight", 
        description="Price per night calculated from total price and nights"
    )

    @field_validator("firstname", "lastname")
    @classmethod
    def validate_name_fields(cls, v: str) -> str:
        """Validate name fields are non-empty and reasonable length"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Name fields must be non-empty")
        if len(v) > 100:
            raise ValueError("Name fields must be at most 100 characters")
        return v.strip()

    @field_validator("totalprice")
    @classmethod
    def validate_total_price(cls, v: int) -> int:
        """Validate total price is positive"""
        if v < 0:
            raise ValueError("Total price must be non-negative")
        return v

    @model_validator(mode="after")
    def calculate_derived_fields(self) -> "Booking":
        """Calculate derived fields like nights count and price per night"""
        if self.bookingdates:
            try:
                checkin_date = datetime.strptime(self.bookingdates.checkin, "%Y-%m-%d")
                checkout_date = datetime.strptime(self.bookingdates.checkout, "%Y-%m-%d")
                
                # Calculate nights count
                nights = (checkout_date - checkin_date).days
                if nights > 0:
                    self.nights_count = nights
                    self.price_per_night = round(self.totalprice / nights, 2)
                else:
                    self.nights_count = 0
                    self.price_per_night = 0.0
                    
            except (ValueError, AttributeError):
                # If date parsing fails, leave derived fields as None
                pass
                
        return self

    def is_within_date_range(self, start_date: str, end_date: str) -> bool:
        """Check if booking falls within specified date range"""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            checkin = datetime.strptime(self.bookingdates.checkin, "%Y-%m-%d")
            
            return start <= checkin <= end
        except (ValueError, AttributeError):
            return False

    def matches_filter_criteria(self, **criteria) -> bool:
        """Check if booking matches given filter criteria"""
        if "depositpaid" in criteria and self.depositpaid != criteria["depositpaid"]:
            return False
            
        if "min_price" in criteria and self.totalprice < criteria["min_price"]:
            return False
            
        if "max_price" in criteria and self.totalprice > criteria["max_price"]:
            return False
            
        if "start_date" in criteria and "end_date" in criteria:
            if not self.is_within_date_range(criteria["start_date"], criteria["end_date"]):
                return False
                
        return True

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format"""
        data = self.model_dump(by_alias=True)
        data["state"] = self.state
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        extra="allow",
    )
