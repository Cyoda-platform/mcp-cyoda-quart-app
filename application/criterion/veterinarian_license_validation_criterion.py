"""
Veterinarian License Validation Criterion for Purrfect Pets API.

Validates veterinarian's license and credentials.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from application.entity.veterinarian.version_1.veterinarian import Veterinarian
from common.processor.base import CyodaCriteriaChecker
from common.processor.errors import CriteriaError
from entity.cyoda_entity import CyodaEntity

logger = logging.getLogger(__name__)


class VeterinarianLicenseValidationCriterion(CyodaCriteriaChecker):
    """Criteria checker to validate veterinarian's license and credentials."""

    def __init__(
        self,
        name: str = "VeterinarianLicenseValidationCriterion",
        description: str = "",
    ):
        super().__init__(
            name=name,
            description=description
            or "Validate veterinarian's license and credentials",
        )

    async def check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if the veterinarian meets license validation criteria."""
        try:
            if not isinstance(entity, Veterinarian):
                logger.warning(f"Expected Veterinarian entity, got {type(entity)}")
                return False

            vet = entity

            # License number format validation
            if not self._validate_license_format(vet.license_number):
                logger.info(f"License format validation failed for vet {vet.vet_id}")
                return False

            # License active status check
            if not await self._check_license_active(vet.license_number):
                logger.info(f"License active check failed for vet {vet.vet_id}")
                return False

            # License expiry check
            if not await self._check_license_not_expired(vet.license_number):
                logger.info(f"License expiry check failed for vet {vet.vet_id}")
                return False

            # License suspension/revocation check
            if not await self._check_license_not_suspended(vet.license_number):
                logger.info(f"License suspension check failed for vet {vet.vet_id}")
                return False

            # Name matching check
            if not await self._check_name_matches_license(vet):
                logger.info(f"Name matching check failed for vet {vet.vet_id}")
                return False

            # Specialization validation
            if not await self._validate_specialization_credentials(vet.specialization):
                logger.info(f"Specialization validation failed for vet {vet.vet_id}")
                return False

            logger.info(f"All license validations passed for vet {vet.vet_id}")
            return True

        except Exception as e:
            logger.exception(
                f"Failed to check veterinarian license validation criteria for entity {entity.entity_id}"
            )
            raise CriteriaError(
                self.name,
                f"Failed to check veterinarian license validation criteria: {str(e)}",
                e,
            )

    def can_check(self, entity: CyodaEntity, **kwargs) -> bool:
        """Check if this criteria checker can evaluate the entity."""
        return isinstance(entity, Veterinarian)

    def _validate_license_format(self, license_number: str) -> bool:
        """Validate license number format for the jurisdiction."""
        if not license_number or not license_number.strip():
            return False

        # Basic format validation - alphanumeric with possible hyphens/spaces
        # This would be jurisdiction-specific in a real implementation
        license_pattern = r"^[A-Za-z0-9\s\-]{5,20}$"
        return bool(re.match(license_pattern, license_number.strip()))

    async def _check_license_active(self, license_number: str) -> bool:
        """Check if license is currently active."""
        # TODO: Implement actual license authority API check
        logger.debug(f"Mock validation: License {license_number} is active")
        return True

    async def _check_license_not_expired(self, license_number: str) -> bool:
        """Check if license is not expired."""
        # TODO: Implement actual license expiry check
        # This would typically involve checking with the veterinary licensing authority
        logger.debug(f"Mock validation: License {license_number} is not expired")
        return True

    async def _check_license_not_suspended(self, license_number: str) -> bool:
        """Check if license is not suspended or revoked."""
        # TODO: Implement actual license status check
        # This would check disciplinary actions, suspensions, revocations
        logger.debug(f"Mock validation: License {license_number} is not suspended")
        return True

    async def _check_name_matches_license(self, vet: Veterinarian) -> bool:
        """Check if veterinarian's name matches license records."""
        # TODO: Implement actual name matching with license authority
        # This would verify the name on file matches the license
        full_name = f"{vet.first_name} {vet.last_name}"
        logger.debug(
            f"Mock validation: Name {full_name} matches license {vet.license_number}"
        )
        return True

    async def _validate_specialization_credentials(
        self, specialization: Optional[str]
    ) -> bool:
        """Validate specialization credentials if provided."""
        if not specialization:
            return True  # Specialization is optional

        # TODO: Implement actual specialization credential validation
        # This would check board certifications, additional training, etc.
        logger.debug(
            f"Mock validation: Specialization {specialization} credentials are valid"
        )
        return True
