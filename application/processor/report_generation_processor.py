"""
ReportGenerationProcessor for Booking Data Analysis

Generates reports summarizing booking data including total revenue,
average booking price, and number of bookings within specific date ranges
as specified in functional requirements.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from application.entity.booking.version_1.booking import Booking
from application.entity.report.version_1.report import (
    DateRangeStats,
    Report,
    ReportSummary,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class ReportGenerationProcessor(CyodaProcessor):
    """
    Processor for generating comprehensive booking reports.
    Creates reports with summary statistics, date range analysis, and filtering results.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportGenerationProcessor",
            description="Generates comprehensive booking reports with statistics and analysis",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Generate a comprehensive booking report.

        Args:
            entity: The Report entity to process
            **kwargs: Additional processing parameters including report criteria

        Returns:
            The processed report entity with generated data
        """
        try:
            self.logger.info(
                f"Generating report for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report_entity = cast_entity(entity, Report)

            # Get all booking data
            all_bookings = await self._get_all_bookings()
            self.logger.info(
                f"Retrieved {len(all_bookings)} bookings for report generation"
            )

            # Apply filters if specified
            filtered_bookings = await self._apply_report_filters(
                all_bookings, report_entity.filter_criteria
            )

            # Generate summary statistics
            summary = self._generate_summary_statistics(filtered_bookings)
            report_entity.summary = summary
            report_entity.booking_count = len(filtered_bookings)

            # Generate date range statistics if requested
            if report_entity.report_type in ["date_range", "custom"]:
                date_range_stats = await self._generate_date_range_statistics(
                    filtered_bookings
                )
                report_entity.date_range_stats = date_range_stats

            # Update report metadata
            report_entity.generated_at = (
                datetime.now().isoformat().replace("+00:00", "Z")
            )
            report_entity.generated_by = "ReportGenerationProcessor"

            self.logger.info(
                f"Report generation completed for entity {report_entity.technical_id}. "
                f"Analyzed {len(filtered_bookings)} bookings."
            )

            return report_entity

        except Exception as e:
            self.logger.error(
                f"Error generating report for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _get_all_bookings(self) -> List[Booking]:
        """Retrieve all booking entities from the system"""
        try:
            entity_service = get_entity_service()

            booking_responses = await entity_service.find_all(
                entity_class=Booking.ENTITY_NAME,
                entity_version=str(Booking.ENTITY_VERSION),
            )

            bookings: List[Booking] = []
            for response in booking_responses:
                try:
                    booking_data = response.data
                    if isinstance(booking_data, dict):
                        booking = Booking(**booking_data)
                        bookings.append(booking)
                    elif isinstance(booking_data, Booking):
                        # If it's already a Booking object
                        bookings.append(booking_data)
                except Exception as e:
                    self.logger.warning(f"Error parsing booking data: {str(e)}")
                    continue

            return bookings

        except Exception as e:
            self.logger.error(f"Error retrieving bookings: {str(e)}")
            return []

    async def _apply_report_filters(
        self, bookings: List[Booking], filter_criteria: Dict[str, Any] | None
    ) -> List[Booking]:
        """Apply filtering criteria to bookings"""
        if not filter_criteria:
            return bookings

        filtered_bookings = []
        for booking in bookings:
            try:
                if booking.matches_filter_criteria(**filter_criteria):
                    filtered_bookings.append(booking)
            except Exception as e:
                self.logger.warning(
                    f"Error applying filter to booking {booking.booking_id}: {str(e)}"
                )
                continue

        self.logger.info(
            f"Filtered {len(bookings)} bookings down to {len(filtered_bookings)} based on criteria"
        )
        return filtered_bookings

    def _generate_summary_statistics(self, bookings: List[Booking]) -> ReportSummary:
        """Generate summary statistics for the bookings"""
        if not bookings:
            return ReportSummary(
                totalBookings=0,
                totalRevenue=0.0,
                averageBookingPrice=0.0,
                averageNightsPerBooking=0.0,
                depositPaidCount=0,
                depositPaidPercentage=0.0,
            )

        total_bookings = len(bookings)
        total_revenue = sum(booking.totalprice for booking in bookings)
        average_booking_price = (
            total_revenue / total_bookings if total_bookings > 0 else 0.0
        )

        # Calculate average nights per booking
        total_nights = 0
        bookings_with_nights = 0
        for booking in bookings:
            if booking.nights_count and booking.nights_count > 0:
                total_nights += booking.nights_count
                bookings_with_nights += 1

        average_nights_per_booking = (
            total_nights / bookings_with_nights if bookings_with_nights > 0 else 0.0
        )

        # Calculate deposit statistics
        deposit_paid_count = sum(1 for booking in bookings if booking.depositpaid)
        deposit_paid_percentage = (
            (deposit_paid_count / total_bookings * 100) if total_bookings > 0 else 0.0
        )

        return ReportSummary(
            totalBookings=total_bookings,
            totalRevenue=round(total_revenue, 2),
            averageBookingPrice=round(average_booking_price, 2),
            averageNightsPerBooking=round(average_nights_per_booking, 2),
            depositPaidCount=deposit_paid_count,
            depositPaidPercentage=round(deposit_paid_percentage, 2),
        )

    async def _generate_date_range_statistics(
        self, bookings: List[Booking]
    ) -> List[DateRangeStats]:
        """Generate statistics broken down by date ranges"""
        try:
            # Group bookings by month for the last 12 months
            date_ranges = []
            current_date = datetime.now()

            for i in range(12):
                # Calculate start and end of month
                month_start = current_date.replace(day=1) - timedelta(days=i * 30)
                month_end = month_start + timedelta(days=30)

                start_date_str = month_start.strftime("%Y-%m-%d")
                end_date_str = month_end.strftime("%Y-%m-%d")

                # Filter bookings for this date range
                range_bookings = [
                    booking
                    for booking in bookings
                    if booking.is_within_date_range(start_date_str, end_date_str)
                ]

                if range_bookings:  # Only include ranges with bookings
                    booking_count = len(range_bookings)
                    revenue = sum(booking.totalprice for booking in range_bookings)
                    average_price = (
                        revenue / booking_count if booking_count > 0 else 0.0
                    )

                    date_range_stat = DateRangeStats(
                        startDate=start_date_str,
                        endDate=end_date_str,
                        bookingCount=booking_count,
                        revenue=round(revenue, 2),
                        averagePrice=round(average_price, 2),
                    )

                    date_ranges.append(date_range_stat)

            # Sort by start date (most recent first)
            date_ranges.sort(key=lambda x: x.start_date, reverse=True)

            return date_ranges[:6]  # Return last 6 months with data

        except Exception as e:
            self.logger.error(f"Error generating date range statistics: {str(e)}")
            return []

    def _analyze_booking_patterns(self, bookings: List[Booking]) -> Dict[str, Any]:
        """Analyze booking patterns for additional insights"""
        try:
            patterns = {
                "peak_months": [],
                "average_stay_duration": 0.0,
                "most_common_additional_needs": [],
                "price_distribution": {
                    "low": 0,  # < $100
                    "medium": 0,  # $100-$300
                    "high": 0,  # > $300
                },
            }

            if not bookings:
                return patterns

            # Analyze months
            month_counts: Dict[str, int] = {}
            total_nights = 0
            nights_count = 0
            additional_needs: Dict[str, int] = {}

            for booking in bookings:
                try:
                    # Month analysis
                    if booking.bookingdates and booking.bookingdates.checkin:
                        checkin_date = datetime.strptime(
                            booking.bookingdates.checkin, "%Y-%m-%d"
                        )
                        month = checkin_date.strftime("%B")
                        month_counts[month] = month_counts.get(month, 0) + 1

                    # Nights analysis
                    if booking.nights_count and booking.nights_count > 0:
                        total_nights += booking.nights_count
                        nights_count += 1

                    # Additional needs analysis
                    if booking.additionalneeds:
                        need = booking.additionalneeds.lower().strip()
                        additional_needs[need] = additional_needs.get(need, 0) + 1

                    # Price distribution
                    if booking.totalprice < 100:
                        patterns["price_distribution"]["low"] = (
                            patterns["price_distribution"].get("low", 0) + 1
                        )
                    elif booking.totalprice <= 300:
                        patterns["price_distribution"]["medium"] = (
                            patterns["price_distribution"].get("medium", 0) + 1
                        )
                    else:
                        patterns["price_distribution"]["high"] = (
                            patterns["price_distribution"].get("high", 0) + 1
                        )

                except Exception as e:
                    self.logger.warning(f"Error analyzing booking pattern: {str(e)}")
                    continue

            # Find peak months (top 3)
            if month_counts:
                sorted_months = sorted(
                    month_counts.items(), key=lambda x: x[1], reverse=True
                )
                patterns["peak_months"] = [month for month, count in sorted_months[:3]]

            # Calculate average stay duration
            if nights_count > 0:
                patterns["average_stay_duration"] = round(
                    total_nights / nights_count, 2
                )

            # Find most common additional needs (top 3)
            if additional_needs:
                sorted_needs = sorted(
                    additional_needs.items(), key=lambda x: x[1], reverse=True
                )
                patterns["most_common_additional_needs"] = [
                    need for need, count in sorted_needs[:3]
                ]

            return patterns

        except Exception as e:
            self.logger.error(f"Error analyzing booking patterns: {str(e)}")
            return {}
