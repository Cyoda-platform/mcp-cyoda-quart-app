"""
BookingValidationCriterion for Restful Booker API Integration

Validates that a Booking entity meets all required business rules before it can
proceed to data retrieval and processing stages as specified in functional requirements.
"""

from typing import Any

from application.entity.booking.version_1.booking import Booking
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class BookingValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for Booking entity that checks all business rules
    before the entity can proceed to data retrieval and processing stages.
    """

    def __init__(self) -> None:
        super().__init__(
            name="BookingValidationCriterion",
            description="Validates Booking entity business rules and data consistency",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the booking entity meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be Booking)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating booking entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Booking for type-safe operations
            booking_entity = cast_entity(entity, Booking)

            # State is managed by Cyoda workflow engine - no manual state checks needed

            # Validate required fields
            if (
                not booking_entity.firstname
                or len(booking_entity.firstname.strip()) < 1
            ):
                self.logger.warning(
                    f"Booking {booking_entity.technical_id} has invalid firstname: '{booking_entity.firstname}'"
                )
                return False

            if not booking_entity.lastname or len(booking_entity.lastname.strip()) < 1:
                self.logger.warning(
                    f"Booking {booking_entity.technical_id} has invalid lastname: '{booking_entity.lastname}'"
                )
                return False

            # Validate total price
            if booking_entity.totalprice < 0:
                self.logger.warning(
                    f"Booking {booking_entity.technical_id} has negative total price: {booking_entity.totalprice}"
                )
                return False

            # Validate booking dates if present
            if booking_entity.bookingdates:
                if (
                    not booking_entity.bookingdates.checkin
                    or not booking_entity.bookingdates.checkout
                ):
                    self.logger.warning(
                        f"Booking {booking_entity.technical_id} has incomplete booking dates"
                    )
                    return False

                # Validate date format and logic
                try:
                    from datetime import datetime

                    checkin_date = datetime.strptime(
                        booking_entity.bookingdates.checkin, "%Y-%m-%d"
                    )
                    checkout_date = datetime.strptime(
                        booking_entity.bookingdates.checkout, "%Y-%m-%d"
                    )

                    if checkout_date <= checkin_date:
                        self.logger.warning(
                            f"Booking {booking_entity.technical_id} has invalid date range: "
                            f"checkout ({booking_entity.bookingdates.checkout}) must be after "
                            f"checkin ({booking_entity.bookingdates.checkin})"
                        )
                        return False

                except ValueError as e:
                    self.logger.warning(
                        f"Booking {booking_entity.technical_id} has invalid date format: {str(e)}"
                    )
                    return False

            # Validate business logic rules
            # High-value bookings should have deposit paid
            if booking_entity.totalprice > 1000 and not booking_entity.depositpaid:
                self.logger.warning(
                    f"Booking {booking_entity.technical_id} is high-value (${booking_entity.totalprice}) "
                    f"but deposit is not paid - this may need review"
                )
                # This is a warning, not a validation failure
                # return False

            # Validate name fields are reasonable
            if (
                len(booking_entity.firstname) > 100
                or len(booking_entity.lastname) > 100
            ):
                self.logger.warning(
                    f"Booking {booking_entity.technical_id} has unusually long name fields"
                )
                return False

            # Validate additional needs if present
            if (
                booking_entity.additionalneeds
                and len(booking_entity.additionalneeds) > 500
            ):
                self.logger.warning(
                    f"Booking {booking_entity.technical_id} has excessively long additional needs"
                )
                return False

            self.logger.info(
                f"Booking {booking_entity.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating booking entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
