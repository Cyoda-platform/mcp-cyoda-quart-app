"""
PetHamsterMoodCriterion for Pet Hamster Workflow

Validates that a pet hamster is in the appropriate mood for safe interaction
and handling based on comprehensive behavioral analysis.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.pet_hamster.version_1.pet_hamster import PetHamster


class PetHamsterMoodCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for PetHamster that checks mood and behavioral
    indicators to ensure the hamster is ready for safe interaction.
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetHamsterMoodCriterion",
            description="Validates pet hamster mood and readiness for interaction",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the hamster is in an appropriate mood for interaction.

        Args:
            entity: The CyodaEntity to validate (expected to be PetHamster)
            **kwargs: Additional criteria parameters

        Returns:
            True if the hamster is ready for interaction, False otherwise
        """
        try:
            self.logger.info(
                f"Validating mood for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to PetHamster for type-safe operations
            pet_hamster = cast_entity(entity, PetHamster)

            # Primary mood check - must be calm for safe interaction
            if pet_hamster.mood != "calm":
                self.logger.warning(
                    f"PetHamster {pet_hamster.technical_id} is not in calm mood: {pet_hamster.mood}"
                )
                return False

            # Additional safety checks for comprehensive validation
            
            # Check activity level - should not be too high
            if pet_hamster.activity_level == "high":
                self.logger.warning(
                    f"PetHamster {pet_hamster.technical_id} has high activity level, not suitable for handling"
                )
                return False

            # Check if camera analysis data is available and recent
            if pet_hamster.camera_analysis_data:
                confidence_score = pet_hamster.camera_analysis_data.get("confidence_score", 0)
                if confidence_score < 0.7:
                    self.logger.warning(
                        f"PetHamster {pet_hamster.technical_id} mood analysis has low confidence: {confidence_score}"
                    )
                    return False

            # Check behavioral indicators if available
            if pet_hamster.camera_analysis_data and "behavioral_indicators" in pet_hamster.camera_analysis_data:
                indicators = pet_hamster.camera_analysis_data["behavioral_indicators"]
                
                # Check if posture is relaxed
                if not indicators.get("posture_relaxed", True):
                    self.logger.warning(
                        f"PetHamster {pet_hamster.technical_id} does not have relaxed posture"
                    )
                    return False
                
                # Check breathing rate
                if indicators.get("breathing_rate") == "elevated":
                    self.logger.warning(
                        f"PetHamster {pet_hamster.technical_id} has elevated breathing rate"
                    )
                    return False

            # All checks passed
            self.logger.info(
                f"PetHamster {pet_hamster.technical_id} passed all mood validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating mood for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
