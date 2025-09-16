"""
AdoptionApplication Processors for Purrfect Pets API

Handles all adoption application processing workflows.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.adoptionapplication.version_1.adoptionapplication import (
    AdoptionApplication,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ApplicationSubmissionProcessor(CyodaProcessor):
    """Processor for AdoptionApplication submission."""

    def __init__(self) -> None:
        super().__init__(
            name="ApplicationSubmissionProcessor",
            description="Processes adoption application submissions",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """Process AdoptionApplication submission."""
        try:
            application = cast_entity(entity, AdoptionApplication)

            # Set submission timestamp
            if not application.application_date:
                application.application_date = (
                    datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                )

            # Calculate application fee (if not set)
            if application.application_fee <= 0:
                application.application_fee = 50.0  # Default fee

            # Send submission confirmation (simulated)
            await self._send_submission_confirmation(application)

            # Notify adoption staff (simulated)
            await self._notify_adoption_staff(application)

            self.logger.info(
                f"Application submission {application.technical_id} processed successfully"
            )
            return application

        except Exception as e:
            self.logger.error(f"Error processing application submission: {str(e)}")
            raise

    async def _send_submission_confirmation(
        self, application: AdoptionApplication
    ) -> None:
        """Send submission confirmation (simulated)."""
        self.logger.info(
            f"Submission confirmation sent for application {application.technical_id}"
        )

    async def _notify_adoption_staff(self, application: AdoptionApplication) -> None:
        """Notify adoption staff (simulated)."""
        self.logger.info(
            f"Adoption staff notified of new application {application.technical_id}"
        )


class ApplicationReviewStartProcessor(CyodaProcessor):
    """Processor for starting AdoptionApplication review."""

    def __init__(self) -> None:
        super().__init__(
            name="ApplicationReviewStartProcessor",
            description="Processes adoption application review start",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """Process AdoptionApplication review start."""
        try:
            application = cast_entity(entity, AdoptionApplication)
            reviewer_id = kwargs.get("reviewer_id")

            # Assign reviewer
            if reviewer_id:
                application.reviewer_id = int(reviewer_id)

            # Set review start timestamp
            application.review_date = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            # Send review notification to customer (simulated)
            await self._send_review_notification(application)

            self.logger.info(
                f"Application review start {application.technical_id} processed successfully"
            )
            return application

        except Exception as e:
            self.logger.error(f"Error processing application review start: {str(e)}")
            raise

    async def _send_review_notification(self, application: AdoptionApplication) -> None:
        """Send review notification to customer (simulated)."""
        self.logger.info(
            f"Review notification sent for application {application.technical_id}"
        )


class ApplicationApprovalProcessor(CyodaProcessor):
    """Processor for AdoptionApplication approval."""

    def __init__(self) -> None:
        super().__init__(
            name="ApplicationApprovalProcessor",
            description="Processes adoption application approvals",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """Process AdoptionApplication approval."""
        try:
            application = cast_entity(entity, AdoptionApplication)

            # Set approval timestamp
            application.review_date = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            # Generate approval documentation (simulated)
            await self._generate_approval_documentation(application)

            # Reserve pet for customer (simulated)
            await self._reserve_pet_for_customer(application)

            # Send approval notification (simulated)
            await self._send_approval_notification(application)

            # Schedule adoption appointment (simulated)
            await self._schedule_adoption_appointment(application)

            self.logger.info(
                f"Application approval {application.technical_id} processed successfully"
            )
            return application

        except Exception as e:
            self.logger.error(f"Error processing application approval: {str(e)}")
            raise

    async def _generate_approval_documentation(
        self, application: AdoptionApplication
    ) -> None:
        """Generate approval documentation (simulated)."""
        self.logger.info(
            f"Approval documentation generated for application {application.technical_id}"
        )

    async def _reserve_pet_for_customer(self, application: AdoptionApplication) -> None:
        """Reserve pet for customer (simulated)."""
        self.logger.info(
            f"Pet {application.pet_id} reserved for customer {application.customer_id}"
        )

    async def _send_approval_notification(
        self, application: AdoptionApplication
    ) -> None:
        """Send approval notification (simulated)."""
        self.logger.info(
            f"Approval notification sent for application {application.technical_id}"
        )

    async def _schedule_adoption_appointment(
        self, application: AdoptionApplication
    ) -> None:
        """Schedule adoption appointment (simulated)."""
        self.logger.info(
            f"Adoption appointment scheduled for application {application.technical_id}"
        )


class ApplicationRejectionProcessor(CyodaProcessor):
    """Processor for AdoptionApplication rejection."""

    def __init__(self) -> None:
        super().__init__(
            name="ApplicationRejectionProcessor",
            description="Processes adoption application rejections",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """Process AdoptionApplication rejection."""
        try:
            application = cast_entity(entity, AdoptionApplication)
            rejection_reason = kwargs.get(
                "rejection_reason", "Application did not meet requirements"
            )

            # Record rejection details
            application.rejection_reason = rejection_reason
            application.review_date = (
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            )

            # Send rejection notification with reason (simulated)
            await self._send_rejection_notification(application, rejection_reason)

            self.logger.info(
                f"Application rejection {application.technical_id} processed successfully"
            )
            return application

        except Exception as e:
            self.logger.error(f"Error processing application rejection: {str(e)}")
            raise

    async def _send_rejection_notification(
        self, application: AdoptionApplication, reason: str
    ) -> None:
        """Send rejection notification with reason (simulated)."""
        self.logger.info(
            f"Rejection notification sent for application {application.technical_id}: {reason}"
        )


class ApplicationWithdrawalProcessor(CyodaProcessor):
    """Processor for AdoptionApplication withdrawal."""

    def __init__(self) -> None:
        super().__init__(
            name="ApplicationWithdrawalProcessor",
            description="Processes adoption application withdrawals",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """Process AdoptionApplication withdrawal."""
        try:
            application = cast_entity(entity, AdoptionApplication)
            withdrawal_reason = kwargs.get(
                "withdrawal_reason", "Customer withdrew application"
            )

            # Record withdrawal timestamp
            application.add_metadata(
                "withdrawal_date",
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            )
            application.add_metadata("withdrawal_reason", withdrawal_reason)

            # Cancel review process if active (simulated)
            await self._cancel_review_process(application)

            # Send withdrawal confirmation (simulated)
            await self._send_withdrawal_confirmation(application)

            self.logger.info(
                f"Application withdrawal {application.technical_id} processed successfully"
            )
            return application

        except Exception as e:
            self.logger.error(f"Error processing application withdrawal: {str(e)}")
            raise

    async def _cancel_review_process(self, application: AdoptionApplication) -> None:
        """Cancel review process if active (simulated)."""
        self.logger.info(
            f"Review process cancelled for application {application.technical_id}"
        )

    async def _send_withdrawal_confirmation(
        self, application: AdoptionApplication
    ) -> None:
        """Send withdrawal confirmation (simulated)."""
        self.logger.info(
            f"Withdrawal confirmation sent for application {application.technical_id}"
        )
