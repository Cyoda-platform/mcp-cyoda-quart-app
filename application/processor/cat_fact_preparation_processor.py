"""
CatFactPreparationProcessor for Cat Fact Subscription Application

Handles the preparation of validated cat facts for use in email campaigns.
Enriches the fact data and performs final quality checks.
"""

import logging
from typing import Any

from application.entity.cat_fact.version_1.cat_fact import CatFact
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CatFactPreparationProcessor(CyodaProcessor):
    """
    Processor for CatFact that handles preparation for email campaigns,
    enriches fact data, and performs final quality assessments.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CatFactPreparationProcessor",
            description="Prepares validated cat facts for use in email campaigns",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the CatFact to prepare it for use in email campaigns.

        Args:
            entity: The CatFact to process (must be in 'validated' state)
            **kwargs: Additional processing parameters

        Returns:
            The processed entity ready for use
        """
        try:
            self.logger.info(
                f"Preparing CatFact {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CatFact for type-safe operations
            cat_fact = cast_entity(entity, CatFact)

            # Calculate quality score if not already set
            if cat_fact.quality_score is None:
                quality_score = self._calculate_quality_score(cat_fact)
                cat_fact.set_quality_score(
                    quality_score, "Auto-calculated during preparation"
                )

            # Ensure fact is marked as appropriate and ready
            if cat_fact.is_appropriate and cat_fact.quality_score is not None and cat_fact.quality_score >= 0.5:
                self.logger.info(
                    f"CatFact {cat_fact.technical_id} prepared successfully with quality score {cat_fact.quality_score}"
                )
            else:
                # Mark as inappropriate if quality is too low
                if cat_fact.quality_score is not None and cat_fact.quality_score < 0.5:
                    cat_fact.mark_inappropriate("Quality score below threshold")
                    self.logger.warning(
                        f"CatFact {cat_fact.technical_id} marked inappropriate due to low quality score"
                    )

            return cat_fact

        except Exception as e:
            self.logger.error(
                f"Error preparing cat fact {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _calculate_quality_score(self, cat_fact: CatFact) -> float:
        """
        Calculate a quality score for the cat fact based on various factors.

        Args:
            cat_fact: The CatFact to score

        Returns:
            Quality score between 0.0 and 1.0
        """
        score = 0.0

        # Length scoring (prefer facts between 50-300 characters)
        length = len(cat_fact.fact_text)
        if 50 <= length <= 300:
            score += 0.4
        elif 30 <= length < 50 or 300 < length <= 500:
            score += 0.2
        elif length < 30 or length > 500:
            score += 0.1

        # Word count scoring (prefer 10-50 words)
        word_count = cat_fact.get_word_count()
        if 10 <= word_count <= 50:
            score += 0.3
        elif 5 <= word_count < 10 or 50 < word_count <= 80:
            score += 0.2
        else:
            score += 0.1

        # Content quality indicators
        fact_lower = cat_fact.fact_text.lower()

        # Positive indicators
        positive_words = ["cat", "cats", "feline", "kitten", "purr", "meow"]
        positive_count = sum(1 for word in positive_words if word in fact_lower)
        score += min(positive_count * 0.05, 0.2)

        # Educational value indicators
        educational_words = ["fact", "actually", "research", "study", "scientists"]
        educational_count = sum(1 for word in educational_words if word in fact_lower)
        score += min(educational_count * 0.03, 0.1)

        # Ensure score is within bounds
        return min(max(score, 0.0), 1.0)
