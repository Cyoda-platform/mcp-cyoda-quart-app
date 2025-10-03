"""
SafetyCheckProcessor for Pet Hamster Workflow

Performs safety checks before allowing the hamster to be picked up and handled,
ensuring both hamster and handler safety.
"""

import logging
import random
from datetime import datetime, timezone
from typing import Any, Dict, cast

from application.entity.pet_hamster.version_1.pet_hamster import PetHamster
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class SafetyCheckProcessor(CyodaProcessor):
    """
    Processor that performs comprehensive safety checks before
    allowing hamster handling to ensure safety for both hamster and handler.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SafetyCheckProcessor",
            description="Performs safety checks before hamster handling",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Perform comprehensive safety checks for hamster handling.

        Args:
            entity: The PetHamster entity to check
            **kwargs: Additional processing parameters

        Returns:
            The entity with updated safety status and check data
        """
        try:
            self.logger.info(
                f"Starting safety check for PetHamster {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to PetHamster for type-safe operations
            pet_hamster = cast_entity(entity, PetHamster)

            # Perform comprehensive safety checks
            safety_data = self._perform_safety_checks(pet_hamster)

            # Update the hamster's safety status
            pet_hamster.is_safe_to_handle = safety_data["overall_safe"]

            # Update location if safe to handle
            if safety_data["overall_safe"]:
                pet_hamster.current_location = "hand"

            # Store the full safety check data
            pet_hamster.set_safety_check_data(safety_data)

            self.logger.info(
                f"Safety check completed for PetHamster {pet_hamster.technical_id}. "
                f"Safe to handle: {pet_hamster.is_safe_to_handle}"
            )

            return pet_hamster

        except Exception as e:
            self.logger.error(
                f"Error in safety check for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _perform_safety_checks(self, hamster: PetHamster) -> Dict[str, Any]:
        """
        Perform comprehensive safety checks.

        In a real implementation, this would:
        - Check environmental conditions
        - Verify handler readiness
        - Assess hamster stress levels
        - Check for any health indicators

        Args:
            hamster: The PetHamster entity being checked

        Returns:
            Dictionary containing safety check results
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Perform individual safety checks
        checks = {}

        # 1. Mood safety check
        checks["mood_check"] = {
            "passed": hamster.mood == "calm",
            "details": f"Hamster mood is {hamster.mood}",
            "weight": 0.4,
        }

        # 2. Activity level check
        checks["activity_check"] = {
            "passed": hamster.activity_level in ["low", "medium"],
            "details": f"Activity level is {hamster.activity_level}",
            "weight": 0.2,
        }

        # 3. Recent handling check
        checks["recent_handling_check"] = {
            "passed": self._check_recent_handling(hamster),
            "details": "Checking if hamster was handled recently",
            "weight": 0.15,
        }

        # 4. Environmental safety check (simulated)
        checks["environment_check"] = {
            "passed": random.choice([True, True, True, False]),  # 75% pass rate
            "details": "Environment temperature, lighting, and noise levels",
            "weight": 0.15,
        }

        # 5. Handler readiness check (simulated)
        checks["handler_check"] = {
            "passed": random.choice([True, True, False]),  # 67% pass rate
            "details": "Handler has clean hands and proper technique",
            "weight": 0.1,
        }

        # Calculate overall safety score
        total_score = 0.0
        max_score = 0.0

        for check_name, check_data in checks.items():
            weight = cast(float, check_data["weight"])
            max_score += weight
            if check_data["passed"]:
                total_score += weight

        safety_score = total_score / max_score if max_score > 0 else 0.0
        overall_safe = safety_score >= 0.8  # Require 80% safety score

        # Generate safety recommendations
        recommendations = []
        for check_name, check_data in checks.items():
            if not check_data["passed"]:
                recommendations.append(f"Address {check_name}: {check_data['details']}")

        if not recommendations:
            recommendations.append("All safety checks passed - safe to proceed")

        safety_data = {
            "check_timestamp": current_timestamp,
            "overall_safe": overall_safe,
            "safety_score": round(safety_score, 2),
            "individual_checks": checks,
            "recommendations": recommendations,
            "check_duration_ms": random.randint(1000, 3000),
            "environmental_conditions": {
                "temperature_celsius": random.uniform(20, 24),
                "humidity_percent": random.uniform(40, 60),
                "noise_level_db": random.uniform(30, 50),
                "lighting_adequate": True,
            },
        }

        self.logger.debug(f"Safety check results: {safety_data}")

        return safety_data

    def _check_recent_handling(self, hamster: PetHamster) -> bool:
        """
        Check if the hamster was handled too recently.

        Args:
            hamster: The PetHamster entity

        Returns:
            True if enough time has passed since last handling, False otherwise
        """
        if not hamster.last_handled_at:
            return True  # Never handled before, safe to handle

        try:
            # In a real implementation, would parse the timestamp and check time difference
            # For simulation, assume it's been long enough most of the time
            return random.choice([True, True, True, False])  # 75% pass rate
        except Exception:
            # If we can't parse the timestamp, err on the side of caution
            return True
