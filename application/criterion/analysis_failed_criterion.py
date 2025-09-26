"""
AnalysisFailedCriterion for Cyoda Client Application

Checks if analysis has failed.
Validates that analysis results are missing or incomplete as specified in functional requirements.
"""

import logging
from typing import Any

from application.entity.analysis.version_1.analysis import Analysis
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriterion, CyodaEntity


class AnalysisFailedCriterion(CyodaCriterion):
    """
    Criterion for Analysis that checks if analysis has failed.
    Validates that analysis results are missing or incomplete.
    """

    def __init__(self) -> None:
        super().__init__(
            name="AnalysisFailedCriterion",
            description="Checks if analysis has failed due to missing or incomplete results",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the Analysis entity has failed.

        Args:
            entity: The Analysis entity to check
            **kwargs: Additional parameters

        Returns:
            True if analysis has failed, False otherwise
        """
        try:
            self.logger.info(
                f"Checking analysis failure for Analysis {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Analysis for type-safe operations
            analysis = cast_entity(entity, Analysis)

            # Check if any required analysis results are missing
            missing_sentiment = analysis.sentiment_score is None
            missing_sentiment_label = analysis.sentiment_label is None
            missing_keywords = analysis.keywords is None
            missing_language = analysis.language is None
            missing_toxicity = analysis.toxicity_score is None

            has_failed = (
                missing_sentiment
                or missing_sentiment_label
                or missing_keywords
                or missing_language
                or missing_toxicity
            )

            self.logger.info(
                f"Analysis {analysis.technical_id} failure check: {has_failed} "
                f"(missing sentiment: {missing_sentiment}, missing label: {missing_sentiment_label}, "
                f"missing keywords: {missing_keywords}, missing language: {missing_language}, "
                f"missing toxicity: {missing_toxicity})"
            )

            return has_failed

        except Exception as e:
            self.logger.error(
                f"Error checking analysis failure for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return True  # Assume failure if we can't check properly
