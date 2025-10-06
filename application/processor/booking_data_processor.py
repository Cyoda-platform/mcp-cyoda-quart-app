"""
BookingDataProcessor for Restful Booker API Integration

Handles processing and filtering of booking data based on criteria like
booking dates, total price, and deposit paid status as specified in
functional requirements.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from application.entity.booking.version_1.booking import Booking
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class BookingDataProcessor(CyodaProcessor):
    """
    Processor for filtering and processing booking data.
    Applies filters based on criteria like dates, price, and deposit status.
    """

    def __init__(self) -> None:
        super().__init__(
            name="BookingDataProcessor",
            description="Processes and filters booking data based on specified criteria",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process and filter booking data based on criteria.

        Args:
            entity: The Booking entity to process
            **kwargs: Additional processing parameters including filter criteria

        Returns:
            The processed entity with filtering results
        """
        try:
            self.logger.info(
                f"Processing booking data for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Booking for type-safe operations
            booking_entity = cast_entity(entity, Booking)

            # Extract filter criteria from kwargs or entity metadata
            filter_criteria = kwargs.get("filter_criteria", {})

            # Apply data processing and enrichment
            await self._enrich_booking_data(booking_entity)

            # Apply filtering logic if criteria are provided
            if filter_criteria:
                await self._apply_filters(booking_entity, filter_criteria)

            # Update related entities or create reports if needed
            await self._update_related_entities(booking_entity)

            self.logger.info(
                f"Booking data processing completed for entity {booking_entity.technical_id}"
            )

            return booking_entity

        except Exception as e:
            self.logger.error(
                f"Error processing booking data for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _enrich_booking_data(self, booking_entity: Booking) -> None:
        """Enrich booking data with calculated fields and metadata"""
        try:
            # Calculate derived fields (already handled in model validator)
            # But we can add additional processing here

            # Add processing timestamp
            booking_entity.retrieved_at = (
                datetime.now().isoformat().replace("+00:00", "Z")
            )

            # Calculate additional metrics
            if booking_entity.bookingdates and booking_entity.nights_count:
                # Add seasonal pricing indicator
                checkin_date = datetime.strptime(
                    booking_entity.bookingdates.checkin, "%Y-%m-%d"
                )
                month = checkin_date.month

                # Simple seasonal classification
                if month in [12, 1, 2]:  # Winter
                    season = "winter"
                elif month in [3, 4, 5]:  # Spring
                    season = "spring"
                elif month in [6, 7, 8]:  # Summer
                    season = "summer"
                else:  # Fall
                    season = "fall"

                # Store season in additional metadata (if entity supports it)
                if hasattr(booking_entity, "metadata") and booking_entity.metadata:
                    booking_entity.metadata["season"] = season

            self.logger.info(
                f"Enriched booking data for booking {booking_entity.booking_id}"
            )

        except Exception as e:
            self.logger.error(f"Error enriching booking data: {str(e)}")
            # Don't raise - enrichment is optional

    async def _apply_filters(
        self, booking_entity: Booking, filter_criteria: Dict[str, Any]
    ) -> None:
        """Apply filtering logic based on criteria"""
        try:
            # Check if booking matches filter criteria
            matches_filter = booking_entity.matches_filter_criteria(**filter_criteria)

            if not matches_filter:
                self.logger.info(
                    f"Booking {booking_entity.booking_id} does not match filter criteria: {filter_criteria}"
                )
                # Mark entity as filtered out (could use metadata or state)
                if hasattr(booking_entity, "metadata") and booking_entity.metadata:
                    booking_entity.metadata["filtered_out"] = True
                    booking_entity.metadata["filter_reason"] = "Does not match criteria"
            else:
                self.logger.info(
                    f"Booking {booking_entity.booking_id} matches filter criteria"
                )
                if hasattr(booking_entity, "metadata") and booking_entity.metadata:
                    booking_entity.metadata["filtered_out"] = False

        except Exception as e:
            self.logger.error(f"Error applying filters: {str(e)}")
            raise

    async def _update_related_entities(self, booking_entity: Booking) -> None:
        """Update or create related entities based on booking data"""
        try:
            entity_service = get_entity_service()

            # Check if we should trigger report generation
            # This could be based on certain conditions or thresholds

            # For now, we'll just log that processing is complete
            # In a real implementation, you might:
            # 1. Update aggregated statistics
            # 2. Trigger report generation for date ranges
            # 3. Update customer profiles
            # 4. Send notifications for high-value bookings

            if booking_entity.totalprice > 500:  # High-value booking
                self.logger.info(
                    f"High-value booking detected: {booking_entity.booking_id} - ${booking_entity.totalprice}"
                )

            if not booking_entity.depositpaid:
                self.logger.info(
                    f"Booking {booking_entity.booking_id} has unpaid deposit - may need follow-up"
                )

        except Exception as e:
            self.logger.error(f"Error updating related entities: {str(e)}")
            # Don't raise - this is optional processing

    async def _get_bookings_in_date_range(
        self, start_date: str, end_date: str
    ) -> List[Booking]:
        """Helper method to get all bookings in a date range"""
        try:
            entity_service = get_entity_service()

            # Get all booking entities
            booking_responses = await entity_service.find_all(
                entity_class=Booking.ENTITY_NAME,
                entity_version=str(Booking.ENTITY_VERSION),
            )

            # Filter by date range
            filtered_bookings: List[Booking] = []
            for response in booking_responses:
                booking_data = response.data
                if isinstance(booking_data, dict):
                    # Create Booking instance to use filtering methods
                    booking = Booking(**booking_data)
                    if booking.is_within_date_range(start_date, end_date):
                        filtered_bookings.append(booking)

            return filtered_bookings

        except Exception as e:
            self.logger.error(f"Error getting bookings in date range: {str(e)}")
            return []

    def _calculate_booking_statistics(self, bookings: List[Booking]) -> Dict[str, Any]:
        """Calculate statistics for a list of bookings"""
        if not bookings:
            return {
                "total_bookings": 0,
                "total_revenue": 0.0,
                "average_price": 0.0,
                "deposit_paid_count": 0,
                "deposit_paid_percentage": 0.0,
            }

        total_bookings = len(bookings)
        total_revenue = sum(booking.totalprice for booking in bookings)
        average_price = total_revenue / total_bookings if total_bookings > 0 else 0.0
        deposit_paid_count = sum(1 for booking in bookings if booking.depositpaid)
        deposit_paid_percentage = (
            (deposit_paid_count / total_bookings * 100) if total_bookings > 0 else 0.0
        )

        return {
            "total_bookings": total_bookings,
            "total_revenue": round(total_revenue, 2),
            "average_price": round(average_price, 2),
            "deposit_paid_count": deposit_paid_count,
            "deposit_paid_percentage": round(deposit_paid_percentage, 2),
        }
