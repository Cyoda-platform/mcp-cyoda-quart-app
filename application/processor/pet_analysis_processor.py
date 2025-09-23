"""
PetAnalysisProcessor for Product Performance Analysis and Reporting System

Handles performance analysis for Pet entities, calculating metrics and scores
based on pet data from the Pet Store API.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from application.entity.pet.version_1.pet import Pet
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class PetAnalysisProcessor(CyodaProcessor):
    """
    Processor for Pet entity that handles performance analysis.

    Analyzes pet data and calculates performance metrics including:
    - Availability score
    - Category performance
    - Status distribution analysis
    """

    def __init__(self) -> None:
        super().__init__(
            name="PetAnalysisProcessor",
            description="Analyzes Pet entities and calculates performance metrics",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Pet entity to perform performance analysis.

        Args:
            entity: The Pet entity to analyze
            **kwargs: Additional processing parameters

        Returns:
            The Pet entity with updated analysis data
        """
        try:
            self.logger.info(
                f"Processing Pet analysis for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Pet for type-safe operations
            pet = cast_entity(entity, Pet)

            # Perform performance analysis
            analysis_data = self._analyze_pet_performance(pet)

            # Calculate performance score
            performance_score = self._calculate_performance_score(pet, analysis_data)

            # Update pet with analysis results
            pet.update_analysis_data(analysis_data)
            pet.set_performance_score(performance_score)

            self.logger.info(
                f"Pet {pet.technical_id} analyzed successfully with score: {performance_score}"
            )

            return pet

        except Exception as e:
            self.logger.error(
                f"Error analyzing pet {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _analyze_pet_performance(self, pet: Pet) -> Dict[str, Any]:
        """
        Analyze pet performance based on various factors.

        Args:
            pet: The Pet entity to analyze

        Returns:
            Dictionary containing analysis results
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        analysis_data: Dict[str, Any] = {
            "analyzed_at": current_timestamp,
            "pet_id": pet.pet_id,
            "name": pet.name,
            "category": pet.get_category_name(),
            "status": pet.status,
            "tags": pet.get_tag_names(),
            "photo_count": len(pet.photo_urls) if pet.photo_urls else 0,
        }

        # Analyze availability
        analysis_data["availability_analysis"] = self._analyze_availability(pet)

        # Analyze category performance
        analysis_data["category_analysis"] = self._analyze_category_performance(pet)

        # Analyze completeness
        analysis_data["completeness_analysis"] = self._analyze_data_completeness(pet)

        return analysis_data

    def _analyze_availability(self, pet: Pet) -> Dict[str, Any]:
        """Analyze pet availability status"""
        availability_score = 0.0

        if pet.status == "available":
            availability_score = 100.0
        elif pet.status == "pending":
            availability_score = 50.0
        elif pet.status == "sold":
            availability_score = 0.0
        else:
            availability_score = 25.0  # Unknown status

        return {
            "status": pet.status,
            "is_available": pet.is_available(),
            "availability_score": availability_score,
            "status_category": (
                "high"
                if availability_score >= 75
                else "medium" if availability_score >= 50 else "low"
            ),
        }

    def _analyze_category_performance(self, pet: Pet) -> Dict[str, Any]:
        """Analyze performance based on pet category"""
        category_name = pet.get_category_name()

        # Category performance weights (could be configurable)
        category_weights = {
            "Dogs": 1.0,
            "Cats": 0.9,
            "Birds": 0.8,
            "Fish": 0.7,
            "Reptiles": 0.6,
        }

        category_weight = category_weights.get(category_name, 0.5)
        category_score = category_weight * 100.0

        return {
            "category_name": category_name,
            "category_weight": category_weight,
            "category_score": category_score,
            "category_tier": (
                "premium"
                if category_score >= 80
                else "standard" if category_score >= 60 else "basic"
            ),
        }

    def _analyze_data_completeness(self, pet: Pet) -> Dict[str, Any]:
        """Analyze completeness of pet data"""
        completeness_factors = []
        total_weight = 0.0
        achieved_weight = 0.0

        # Name (required, weight: 20)
        if pet.name:
            completeness_factors.append(
                {"field": "name", "complete": True, "weight": 20}
            )
            achieved_weight += 20
        else:
            completeness_factors.append(
                {"field": "name", "complete": False, "weight": 20}
            )
        total_weight += 20

        # Category (weight: 15)
        if pet.category:
            completeness_factors.append(
                {"field": "category", "complete": True, "weight": 15}
            )
            achieved_weight += 15
        else:
            completeness_factors.append(
                {"field": "category", "complete": False, "weight": 15}
            )
        total_weight += 15

        # Status (weight: 15)
        if pet.status:
            completeness_factors.append(
                {"field": "status", "complete": True, "weight": 15}
            )
            achieved_weight += 15
        else:
            completeness_factors.append(
                {"field": "status", "complete": False, "weight": 15}
            )
        total_weight += 15

        # Photo URLs (weight: 25)
        if pet.photo_urls and len(pet.photo_urls) > 0:
            completeness_factors.append(
                {"field": "photo_urls", "complete": True, "weight": 25}
            )
            achieved_weight += 25
        else:
            completeness_factors.append(
                {"field": "photo_urls", "complete": False, "weight": 25}
            )
        total_weight += 25

        # Tags (weight: 25)
        if pet.tags and len(pet.tags) > 0:
            completeness_factors.append(
                {"field": "tags", "complete": True, "weight": 25}
            )
            achieved_weight += 25
        else:
            completeness_factors.append(
                {"field": "tags", "complete": False, "weight": 25}
            )
        total_weight += 25

        completeness_score = (
            (achieved_weight / total_weight * 100.0) if total_weight > 0 else 0.0
        )

        return {
            "completeness_score": completeness_score,
            "total_weight": total_weight,
            "achieved_weight": achieved_weight,
            "factors": completeness_factors,
            "completeness_tier": (
                "excellent"
                if completeness_score >= 90
                else "good" if completeness_score >= 70 else "needs_improvement"
            ),
        }

    def _calculate_performance_score(
        self, pet: Pet, analysis_data: Dict[str, Any]
    ) -> float:
        """
        Calculate overall performance score for the pet.

        Args:
            pet: The Pet entity
            analysis_data: Analysis results

        Returns:
            Performance score between 0.0 and 100.0
        """
        # Weight factors for different aspects
        availability_weight = 0.4
        category_weight = 0.3
        completeness_weight = 0.3

        # Get scores from analysis
        availability_score = analysis_data.get("availability_analysis", {}).get(
            "availability_score", 0.0
        )
        category_score = analysis_data.get("category_analysis", {}).get(
            "category_score", 0.0
        )
        completeness_score = analysis_data.get("completeness_analysis", {}).get(
            "completeness_score", 0.0
        )

        # Calculate weighted average
        performance_score = (
            availability_score * availability_weight
            + category_score * category_weight
            + completeness_score * completeness_weight
        )

        # Ensure score is within bounds
        return max(0.0, min(100.0, performance_score))
