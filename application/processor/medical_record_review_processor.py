"""
Medical Record Review Processor for Purrfect Pets API.
"""

import logging
from datetime import datetime, timezone

from application.entity.medicalrecord.version_1.medicalrecord import \
    MedicalRecord
from common.processor.base import CyodaProcessor
from common.processor.errors import ProcessorError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class MedicalRecordReviewProcessor(CyodaProcessor):
    """Processor to review a medical record."""

    def __init__(
        self, name: str = "MedicalRecordReviewProcessor", description: str = ""
    ):
        super().__init__(
            name=name, description=description or "Review a medical record"
        )

    async def process(self, entity: CyodaEntity, **kwargs) -> CyodaEntity:
        """Process medical record review."""
        try:
            if not isinstance(entity, MedicalRecord):
                raise ProcessorError(
                    self.name, f"Expected MedicalRecord entity, got {type(entity)}"
                )

            record = entity

            # Perform quality review
            await self._perform_quality_review(record)

            # Validate medical accuracy
            await self._validate_medical_accuracy(record)

            # Check follow-up requirements
            await self._check_follow_up_requirements(record)

            # Approve record for archival
            await self._approve_record_for_archival(record)

            # Log review event
            record.add_metadata("review_processor", self.name)
            record.add_metadata(
                "review_timestamp", datetime.now(timezone.utc).isoformat()
            )
            record.add_metadata("reviewed_by", kwargs.get("reviewed_by", "system"))
            record.add_metadata("record_status", "reviewed")

            logger.info(f"Successfully reviewed medical record {record.record_id}")

            return record

        except Exception as e:
            logger.exception(f"Failed to review medical record {entity.entity_id}")
            raise ProcessorError(
                self.name, f"Failed to review medical record: {str(e)}", e
            )

    def can_process(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this processor can handle the entity."""
        return isinstance(entity, MedicalRecord)

    async def _perform_quality_review(self, record: MedicalRecord) -> None:
        """Perform quality review."""
        logger.info(f"Performing quality review for record {record.record_id}")
        # TODO: Implement actual quality review

    async def _validate_medical_accuracy(self, record: MedicalRecord) -> None:
        """Validate medical accuracy."""
        logger.info(f"Validating medical accuracy for record {record.record_id}")
        # TODO: Implement actual accuracy validation

    async def _check_follow_up_requirements(self, record: MedicalRecord) -> None:
        """Check follow-up requirements."""
        logger.info(f"Checking follow-up requirements for record {record.record_id}")
        # TODO: Implement actual follow-up checking

    async def _approve_record_for_archival(self, record: MedicalRecord) -> None:
        """Approve record for archival."""
        logger.info(f"Approving record {record.record_id} for archival")
        record.add_metadata("approved_for_archival", True)
        # TODO: Implement actual approval process
