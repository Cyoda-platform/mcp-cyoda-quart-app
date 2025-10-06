"""
BookingDataRetrievalProcessor for Restful Booker API Integration

Handles retrieval of booking data from the Restful Booker API
(https://restful-booker.herokuapp.com/apidoc/index.html) as specified
in functional requirements.
"""

import logging
from typing import Any, Dict, List

import httpx
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.booking.version_1.booking import Booking
from services.services import get_entity_service


class BookingDataRetrievalProcessor(CyodaProcessor):
    """
    Processor for retrieving booking data from Restful Booker API.
    Fetches all bookings and creates individual Booking entities.
    """

    RESTFUL_BOOKER_BASE_URL = "https://restful-booker.herokuapp.com"

    def __init__(self) -> None:
        super().__init__(
            name="BookingDataRetrievalProcessor",
            description="Retrieves booking data from Restful Booker API and creates Booking entities",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Retrieve booking data from Restful Booker API.

        Args:
            entity: The Booking entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with retrieved data
        """
        try:
            self.logger.info(
                f"Starting booking data retrieval for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Booking for type-safe operations
            booking_entity = cast_entity(entity, Booking)

            # Retrieve all booking IDs first
            booking_ids = await self._get_all_booking_ids()
            self.logger.info(f"Retrieved {len(booking_ids)} booking IDs from API")

            # If this is a specific booking request, process only that booking
            if booking_entity.booking_id:
                await self._retrieve_specific_booking(booking_entity)
            else:
                # Otherwise, retrieve all bookings and create entities for them
                await self._retrieve_all_bookings(booking_ids)

            self.logger.info(
                f"Booking data retrieval completed for entity {booking_entity.technical_id}"
            )

            return booking_entity

        except Exception as e:
            self.logger.error(
                f"Error retrieving booking data for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _get_all_booking_ids(self) -> List[int]:
        """Retrieve all booking IDs from the API"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.RESTFUL_BOOKER_BASE_URL}/booking")
                
                if response.status_code == 200:
                    booking_data = response.json()
                    # API returns list of {"bookingid": int} objects
                    return [item["bookingid"] for item in booking_data if "bookingid" in item]
                else:
                    self.logger.warning(f"Failed to retrieve booking IDs: {response.status_code}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error retrieving booking IDs: {str(e)}")
            return []

    async def _retrieve_specific_booking(self, booking_entity: Booking) -> None:
        """Retrieve data for a specific booking"""
        try:
            booking_data = await self._get_booking_by_id(booking_entity.booking_id)
            if booking_data:
                self._update_booking_entity_from_api_data(booking_entity, booking_data)
            else:
                self.logger.warning(f"No data found for booking ID {booking_entity.booking_id}")
                
        except Exception as e:
            self.logger.error(f"Error retrieving specific booking {booking_entity.booking_id}: {str(e)}")
            raise

    async def _retrieve_all_bookings(self, booking_ids: List[int]) -> None:
        """Retrieve all bookings and create entities for them"""
        entity_service = get_entity_service()
        
        # Limit to first 50 bookings to avoid overwhelming the system
        limited_ids = booking_ids[:50]
        self.logger.info(f"Processing first {len(limited_ids)} bookings")
        
        for booking_id in limited_ids:
            try:
                booking_data = await self._get_booking_by_id(booking_id)
                if booking_data:
                    # Create new Booking entity
                    new_booking = self._create_booking_from_api_data(booking_data)
                    
                    # Save the new booking entity
                    await entity_service.save(
                        entity=new_booking.model_dump(by_alias=True),
                        entity_class=Booking.ENTITY_NAME,
                        entity_version=str(Booking.ENTITY_VERSION),
                    )
                    
                    self.logger.info(f"Created booking entity for booking ID {booking_id}")
                    
            except Exception as e:
                self.logger.error(f"Error processing booking ID {booking_id}: {str(e)}")
                # Continue with other bookings even if one fails
                continue

    async def _get_booking_by_id(self, booking_id: int) -> Dict[str, Any] | None:
        """Retrieve a specific booking by ID"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.RESTFUL_BOOKER_BASE_URL}/booking/{booking_id}")
                
                if response.status_code == 200:
                    return response.json()
                else:
                    self.logger.warning(f"Failed to retrieve booking {booking_id}: {response.status_code}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error retrieving booking {booking_id}: {str(e)}")
            return None

    def _create_booking_from_api_data(self, api_data: Dict[str, Any]) -> Booking:
        """Create a Booking entity from API response data"""
        # Extract booking dates
        booking_dates_data = api_data.get("bookingdates", {})
        
        # Create Booking entity
        booking = Booking(
            booking_id=None,  # Will be set by the API response structure
            firstname=api_data.get("firstname", ""),
            lastname=api_data.get("lastname", ""),
            totalprice=api_data.get("totalprice", 0),
            depositpaid=api_data.get("depositpaid", False),
            bookingdates={
                "checkin": booking_dates_data.get("checkin", ""),
                "checkout": booking_dates_data.get("checkout", "")
            },
            additionalneeds=api_data.get("additionalneeds")
        )
        
        return booking

    def _update_booking_entity_from_api_data(self, booking_entity: Booking, api_data: Dict[str, Any]) -> None:
        """Update existing booking entity with API data"""
        booking_entity.firstname = api_data.get("firstname", booking_entity.firstname)
        booking_entity.lastname = api_data.get("lastname", booking_entity.lastname)
        booking_entity.totalprice = api_data.get("totalprice", booking_entity.totalprice)
        booking_entity.depositpaid = api_data.get("depositpaid", booking_entity.depositpaid)
        booking_entity.additionalneeds = api_data.get("additionalneeds", booking_entity.additionalneeds)
        
        # Update booking dates
        booking_dates_data = api_data.get("bookingdates", {})
        if booking_dates_data:
            booking_entity.bookingdates.checkin = booking_dates_data.get("checkin", booking_entity.bookingdates.checkin)
            booking_entity.bookingdates.checkout = booking_dates_data.get("checkout", booking_entity.bookingdates.checkout)
