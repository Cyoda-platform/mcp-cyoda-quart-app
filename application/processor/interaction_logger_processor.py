"""
InteractionLoggerProcessor for Pet Hamster Workflow

Logs successful petting interactions and updates the hamster's interaction history
for future reference and behavior analysis.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from application.entity.pet_hamster.version_1.pet_hamster import PetHamster
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class InteractionLoggerProcessor(CyodaProcessor):
    """
    Processor that logs successful petting interactions and updates
    the hamster's interaction history and statistics.
    """

    def __init__(self) -> None:
        super().__init__(
            name="InteractionLoggerProcessor",
            description="Logs petting interactions and updates interaction history",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Log the petting interaction and update interaction statistics.

        Args:
            entity: The PetHamster entity that was petted
            **kwargs: Additional processing parameters

        Returns:
            The entity with updated interaction history and statistics
        """
        try:
            self.logger.info(
                f"Logging interaction for PetHamster {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to PetHamster for type-safe operations
            pet_hamster = cast_entity(entity, PetHamster)

            # Log the interaction
            interaction_data = self._log_interaction(pet_hamster)

            # Update interaction statistics
            pet_hamster.increment_interaction_count()
            pet_hamster.last_interaction_result = interaction_data["interaction_result"]
            pet_hamster.last_handled_at = interaction_data["interaction_timestamp"]

            # Update location back to cage after interaction
            pet_hamster.current_location = "cage"

            # Store the full interaction log data
            pet_hamster.set_interaction_log_data(interaction_data)

            self.logger.info(
                f"Interaction logged for PetHamster {pet_hamster.technical_id}. "
                f"Total interactions: {pet_hamster.interaction_count}, "
                f"Result: {pet_hamster.last_interaction_result}"
            )

            return pet_hamster

        except Exception as e:
            self.logger.error(
                f"Error logging interaction for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _log_interaction(self, hamster: PetHamster) -> Dict[str, Any]:
        """
        Log the petting interaction with detailed information.

        In a real implementation, this would:
        - Record interaction duration
        - Log handler information
        - Store video/photo evidence
        - Update behavioral patterns

        Args:
            hamster: The PetHamster entity that was petted

        Returns:
            Dictionary containing interaction log data
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        interaction_id = str(uuid.uuid4())

        # Simulate interaction details
        # In reality, this would come from sensors, timers, and user input
        interaction_duration_seconds = 30 + (
            15 * (hamster.interaction_count or 0) % 60
        )  # Longer interactions for experienced hamsters

        # Determine interaction result based on hamster's mood and experience
        interaction_success_rate = 0.9  # Base success rate
        if hamster.mood == "calm":
            interaction_success_rate = 0.95
        elif hamster.mood in ["agitated", "hiding"]:
            interaction_success_rate = 0.7

        # More experienced hamsters have better success rates
        if hamster.interaction_count and hamster.interaction_count > 3:
            interaction_success_rate = min(0.98, interaction_success_rate + 0.05)

        import random

        interaction_successful = random.random() < interaction_success_rate

        if interaction_successful:
            interaction_result = "success"
            hamster_response = "enjoyed_petting"
        else:
            # Determine type of unsuccessful interaction
            failure_types = ["bite", "escape", "stress_signs"]
            interaction_result = random.choice(failure_types)
            hamster_response = "showed_discomfort"

        # Generate interaction metrics
        interaction_metrics = {
            "duration_seconds": interaction_duration_seconds,
            "strokes_count": max(1, interaction_duration_seconds // 3),
            "hamster_response": hamster_response,
            "stress_indicators": (
                []
                if interaction_successful
                else ["rapid_breathing", "attempts_to_escape"]
            ),
            "handler_technique_score": random.uniform(0.7, 1.0),
        }

        # Generate behavioral observations
        behavioral_observations = []
        if interaction_successful:
            observations = [
                "Hamster remained calm throughout interaction",
                "Showed signs of enjoyment (relaxed posture)",
                "No stress indicators observed",
                "Responded positively to gentle strokes",
            ]
            behavioral_observations = random.sample(observations, random.randint(2, 4))
        else:
            observations = [
                "Hamster showed signs of stress",
                "Attempted to escape during handling",
                "Displayed defensive behavior",
                "Required careful monitoring",
            ]
            behavioral_observations = random.sample(observations, random.randint(1, 3))

        # Create comprehensive interaction log
        interaction_data = {
            "interaction_id": interaction_id,
            "interaction_timestamp": current_timestamp,
            "interaction_result": interaction_result,
            "interaction_successful": interaction_successful,
            "interaction_metrics": interaction_metrics,
            "behavioral_observations": behavioral_observations,
            "pre_interaction_mood": hamster.mood,
            "pre_interaction_activity": hamster.activity_level,
            "environmental_conditions": {
                "location": "safe_handling_area",
                "temperature_celsius": random.uniform(20, 24),
                "noise_level": "low",
                "lighting": "adequate",
            },
            "handler_information": {
                "experience_level": "intermediate",
                "technique_used": "gentle_stroking",
                "safety_equipment": ["clean_hands", "calm_demeanor"],
            },
            "post_interaction_assessment": {
                "hamster_stress_level": "low" if interaction_successful else "medium",
                "recovery_time_needed": (
                    "none" if interaction_successful else "5_minutes"
                ),
                "recommendations": self._generate_recommendations(
                    interaction_successful, hamster
                ),
            },
        }

        self.logger.debug(f"Interaction log data: {interaction_data}")

        return interaction_data

    def _generate_recommendations(
        self, successful: bool, hamster: PetHamster
    ) -> list[str]:
        """
        Generate recommendations based on interaction outcome.

        Args:
            successful: Whether the interaction was successful
            hamster: The PetHamster entity

        Returns:
            List of recommendations for future interactions
        """
        recommendations = []

        if successful:
            recommendations.extend(
                [
                    "Continue with current handling technique",
                    "Hamster is comfortable with interactions",
                    "Can gradually increase interaction duration",
                ]
            )

            if hamster.interaction_count and hamster.interaction_count > 5:
                recommendations.append("Hamster is well-socialized and enjoys handling")
        else:
            recommendations.extend(
                [
                    "Allow more time between interactions",
                    "Ensure hamster is in calm mood before next attempt",
                    "Consider shorter interaction duration",
                    "Monitor for stress indicators more closely",
                ]
            )

            if hamster.mood != "calm":
                recommendations.append(
                    "Wait for hamster to be in calm mood before next interaction"
                )

        return recommendations
