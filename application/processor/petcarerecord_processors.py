"""
PetCareRecord Processors for Purrfect Pets API

Handles all pet care record processing workflows.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.petcarerecord.version_1.petcarerecord import PetCareRecord
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CareSchedulingProcessor(CyodaProcessor):
    """Processor for PetCareRecord scheduling."""

    def __init__(self) -> None:
        super().__init__(
            name="CareSchedulingProcessor",
            description="Processes pet care scheduling",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """Process PetCareRecord scheduling."""
        try:
            care_record = cast_entity(entity, PetCareRecord)

            # Validate care type and requirements
            await self._validate_care_requirements(care_record)

            # Schedule care appointment (simulated)
            await self._schedule_care_appointment(care_record)

            # Assign veterinarian or staff
            if not care_record.veterinarian:
                care_record.veterinarian = await self._assign_veterinarian(
                    care_record.care_type
                )

            # Calculate estimated cost
            if care_record.cost <= 0:
                care_record.cost = await self._calculate_estimated_cost(
                    care_record.care_type
                )

            # Send scheduling notification (simulated)
            await self._send_scheduling_notification(care_record)

            self.logger.info(
                f"Care scheduling {care_record.technical_id} processed successfully"
            )
            return care_record

        except Exception as e:
            self.logger.error(f"Error processing care scheduling: {str(e)}")
            raise

    async def _validate_care_requirements(self, care_record: PetCareRecord) -> None:
        """Validate care type and requirements."""
        if care_record.care_type not in PetCareRecord.ALLOWED_CARE_TYPES:
            raise ValueError(f"Invalid care type: {care_record.care_type}")
        self.logger.info(f"Care requirements validated for {care_record.technical_id}")

    async def _schedule_care_appointment(self, care_record: PetCareRecord) -> None:
        """Schedule care appointment (simulated)."""
        self.logger.info(f"Care appointment scheduled for pet {care_record.pet_id}")

    async def _assign_veterinarian(self, care_type: str) -> str:
        """Assign veterinarian or staff based on care type."""
        vet_assignments = {
            "Vaccination": "Dr. Smith",
            "Surgery": "Dr. Johnson",
            "Dental": "Dr. Brown",
            "Checkup": "Vet Tech",
            "Grooming": "Grooming Staff",
            "Emergency": "Emergency Vet",
        }
        return vet_assignments.get(care_type, "General Vet")

    async def _calculate_estimated_cost(self, care_type: str) -> float:
        """Calculate estimated cost based on care type."""
        cost_estimates = {
            "Vaccination": 75.0,
            "Checkup": 50.0,
            "Surgery": 500.0,
            "Dental": 200.0,
            "Grooming": 40.0,
            "Emergency": 150.0,
            "Treatment": 100.0,
            "Spay/Neuter": 300.0,
            "Microchip": 25.0,
        }
        return cost_estimates.get(care_type, 75.0)

    async def _send_scheduling_notification(self, care_record: PetCareRecord) -> None:
        """Send scheduling notification (simulated)."""
        self.logger.info(
            f"Scheduling notification sent for care record {care_record.technical_id}"
        )


class CareCompletionProcessor(CyodaProcessor):
    """Processor for PetCareRecord completion."""

    def __init__(self) -> None:
        super().__init__(
            name="CareCompletionProcessor",
            description="Processes pet care completion",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """Process PetCareRecord completion."""
        try:
            care_record = cast_entity(entity, PetCareRecord)

            # Record care completion details
            care_results = kwargs.get("care_results", {})
            await self._record_completion_details(care_record, care_results)

            # Update pet health records (simulated)
            await self._update_pet_health_records(care_record, care_results)

            # Calculate final cost
            final_cost = care_results.get("final_cost")
            if final_cost:
                care_record.cost = float(final_cost)

            # Schedule follow-up if needed
            if care_results.get("follow_up_needed"):
                await self._schedule_follow_up(care_record, care_results)

            # Generate care report (simulated)
            await self._generate_care_report(care_record)

            self.logger.info(
                f"Care completion {care_record.technical_id} processed successfully"
            )
            return care_record

        except Exception as e:
            self.logger.error(f"Error processing care completion: {str(e)}")
            raise

    async def _record_completion_details(
        self, care_record: PetCareRecord, care_results: dict
    ) -> None:
        """Record care completion details."""
        care_record.add_metadata(
            "completion_date",
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        )
        care_record.add_metadata("care_results", care_results)

        # Update medications if provided
        if care_results.get("medications"):
            care_record.medications = care_results["medications"]

        # Update notes if provided
        if care_results.get("notes"):
            care_record.notes = care_results["notes"]

        # Set next due date if provided
        if care_results.get("next_due_date"):
            care_record.next_due_date = care_results["next_due_date"]

    async def _update_pet_health_records(
        self, care_record: PetCareRecord, care_results: dict
    ) -> None:
        """Update pet health records (simulated)."""
        self.logger.info(f"Pet health records updated for pet {care_record.pet_id}")

    async def _schedule_follow_up(
        self, care_record: PetCareRecord, care_results: dict
    ) -> None:
        """Schedule follow-up if needed (simulated)."""
        follow_up_date = care_results.get("follow_up_date")
        self.logger.info(
            f"Follow-up scheduled for pet {care_record.pet_id} on {follow_up_date}"
        )

    async def _generate_care_report(self, care_record: PetCareRecord) -> None:
        """Generate care report (simulated)."""
        self.logger.info(f"Care report generated for {care_record.technical_id}")


class CareCancellationProcessor(CyodaProcessor):
    """Processor for PetCareRecord cancellation."""

    def __init__(self) -> None:
        super().__init__(
            name="CareCancellationProcessor",
            description="Processes pet care cancellation",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """Process PetCareRecord cancellation."""
        try:
            care_record = cast_entity(entity, PetCareRecord)
            cancellation_reason = kwargs.get(
                "cancellation_reason", "Appointment cancelled"
            )

            # Record cancellation reason
            care_record.add_metadata("cancellation_reason", cancellation_reason)
            care_record.add_metadata(
                "cancellation_date",
                datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            )

            # Cancel scheduled appointment (simulated)
            await self._cancel_scheduled_appointment(care_record)

            # Notify assigned staff (simulated)
            await self._notify_assigned_staff(care_record, cancellation_reason)

            # Reschedule if necessary
            if kwargs.get("reschedule_needed"):
                await self._reschedule_care(care_record)

            self.logger.info(
                f"Care cancellation {care_record.technical_id} processed successfully"
            )
            return care_record

        except Exception as e:
            self.logger.error(f"Error processing care cancellation: {str(e)}")
            raise

    async def _cancel_scheduled_appointment(self, care_record: PetCareRecord) -> None:
        """Cancel scheduled appointment (simulated)."""
        self.logger.info(
            f"Scheduled appointment cancelled for care record {care_record.technical_id}"
        )

    async def _notify_assigned_staff(
        self, care_record: PetCareRecord, reason: str
    ) -> None:
        """Notify assigned staff (simulated)."""
        self.logger.info(
            f"Staff {care_record.veterinarian} notified of cancellation: {reason}"
        )

    async def _reschedule_care(self, care_record: PetCareRecord) -> None:
        """Reschedule care if necessary (simulated)."""
        self.logger.info(f"Care rescheduled for pet {care_record.pet_id}")
