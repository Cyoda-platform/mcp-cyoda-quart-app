"""
Medical Record Completion Criterion for Purrfect Pets API.

Validates that a medical record is ready for completion.
"""

import logging

from application.entity.medicalrecord.version_1.medicalrecord import \
    MedicalRecord
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class MedicalRecordCompletionCriterion(CyodaCriteriaChecker):
    """Criteria checker to validate medical record completion requirements."""

    def __init__(
        self, name: str = "MedicalRecordCompletionCriterion", description: str = ""
    ):
        super().__init__(
            name=name,
            description=description
            or "Validate that a medical record is ready for completion",
        )

    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if the medical record meets completion criteria."""
        try:
            if not isinstance(entity, MedicalRecord):
                logger.warning(f"Expected MedicalRecord entity, got {type(entity)}")
                return False

            record = entity

            # Check if required fields are present
            if not self._has_required_fields(record):
                logger.info(
                    f"Required fields validation failed for record {record.record_id}"
                )
                return False

            # Check if diagnosis or treatment is provided
            if not self._has_medical_content(record):
                logger.info(
                    f"Medical content validation failed for record {record.record_id}"
                )
                return False

            # Check if visit date is valid
            if not self._is_visit_date_valid(record.visit_date):
                logger.info(
                    f"Visit date validation failed for record {record.record_id}"
                )
                return False

            logger.info(
                f"All completion validations passed for record {record.record_id}"
            )
            return True

        except Exception as e:
            logger.exception(
                f"Failed to check medical record completion criteria for entity {entity.entity_id}"
            )
            raise CriteriaError(
                self.name,
                f"Failed to check medical record completion criteria: {str(e)}",
                e,
            )

    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, MedicalRecord)

    def _has_required_fields(self, record: MedicalRecord) -> bool:
        """Check if required fields are present."""
        required_fields = [record.pet_id, record.vet_id, record.visit_date]
        return all(field for field in required_fields)

    def _has_medical_content(self, record: MedicalRecord) -> bool:
        """Check if diagnosis or treatment is provided."""
        return bool(record.diagnosis and record.diagnosis.strip()) or bool(
            record.treatment and record.treatment.strip()
        )

    def _is_visit_date_valid(self, visit_date: str) -> bool:
        """Check if visit date is valid."""
        if not visit_date:
            return False

        try:
            from datetime import datetime

            datetime.fromisoformat(visit_date.replace("Z", "+00:00"))
            return True
        except ValueError:
            return False
