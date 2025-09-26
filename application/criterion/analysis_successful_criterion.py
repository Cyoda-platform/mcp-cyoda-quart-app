"""
AnalysisSuccessfulCriterion for Cyoda Client Application

Checks if analysis has completed successfully.
Validates that all required analysis results are present as specified in functional requirements.
"""

import logging
from typing import Any

from application.entity.analysis.version_1.analysis import Analysis
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriterion, CyodaEntity


class AnalysisSuccessfulCriterion(CyodaCriterion):
    """
    Criterion for Analysis that checks if analysis completed successfully.
    Validates that all required analysis results are present.
    """

    def __init__(self) -> None:
        super().__init__(
            name="AnalysisSuccessfulCriterion",
            description="Checks if analysis has completed successfully with all required results",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the Analysis entity has completed successfully.

        Args:
            entity: The Analysis entity to check
            **kwargs: Additional parameters

        Returns:
            True if analysis is successful, False otherwise
        """
        try:
            self.logger.info(
                f"Checking analysis success for Analysis {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Analysis for type-safe operations
            analysis = cast_entity(entity, Analysis)

            # Check if all required analysis results are present
            has_sentiment = analysis.sentiment_score is not None
            has_sentiment_label = analysis.sentiment_label is not None
            has_keywords = analysis.keywords is not None
            has_language = analysis.language is not None
            has_toxicity = analysis.toxicity_score is not None

            is_successful = (
                has_sentiment
                and has_sentiment_label
                and has_keywords
                and has_language
                and has_toxicity
            )

            self.logger.info(
                f"Analysis {analysis.technical_id} success check: {is_successful} "
                f"(sentiment: {has_sentiment}, label: {has_sentiment_label}, "
                f"keywords: {has_keywords}, language: {has_language}, toxicity: {has_toxicity})"
            )

            return is_successful

        except Exception as e:
            self.logger.error(
                f"Error checking analysis success for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
