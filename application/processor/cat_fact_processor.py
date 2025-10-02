"""
Cat Fact Processors for Cat Fact Subscription Application

Handles cat fact preparation and delivery processing.
"""

import logging
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.cat_fact.version_1.cat_fact import CatFact


class CatFactPreparationProcessor(CyodaProcessor):
    """
    Processor for preparing cat facts for delivery.
    Calculates metadata and quality scores.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CatFactPreparationProcessor",
            description="Prepares cat facts for delivery by calculating metadata and quality scores",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process cat fact preparation for delivery.

        Args:
            entity: The CatFact entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed cat fact entity
        """
        try:
            self.logger.info(
                f"Preparing cat fact for delivery {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CatFact for type-safe operations
            cat_fact = cast_entity(entity, CatFact)

            # Calculate fact length
            cat_fact.calculate_fact_length()

            # Calculate a simple quality score based on length and content
            quality_score = self._calculate_quality_score(cat_fact)
            cat_fact.set_quality_score(quality_score)

            # Check if fact is appropriate (simple content filtering)
            if not self._is_appropriate_content(cat_fact):
                cat_fact.mark_inappropriate()
                self.logger.warning(
                    f"Cat fact {cat_fact.technical_id} marked as inappropriate"
                )

            self.logger.info(
                f"Cat fact {cat_fact.technical_id} prepared for delivery with quality score {quality_score}"
            )

            return cat_fact

        except Exception as e:
            self.logger.error(
                f"Error preparing cat fact {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _calculate_quality_score(self, cat_fact: CatFact) -> float:
        """
        Calculate a quality score for the cat fact.
        
        Args:
            cat_fact: The cat fact to score
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        score = 0.5  # Base score
        
        # Length scoring (prefer facts between 50-300 characters)
        if cat_fact.fact_length:
            if 50 <= cat_fact.fact_length <= 300:
                score += 0.3
            elif 30 <= cat_fact.fact_length < 50 or 300 < cat_fact.fact_length <= 500:
                score += 0.1
        
        # Content quality (simple checks)
        fact_lower = cat_fact.fact.lower()
        if "cat" in fact_lower:
            score += 0.2
        
        # Ensure score is within bounds
        return min(1.0, max(0.0, score))

    def _is_appropriate_content(self, cat_fact: CatFact) -> bool:
        """
        Check if the cat fact content is appropriate for email delivery.
        
        Args:
            cat_fact: The cat fact to check
            
        Returns:
            True if appropriate, False otherwise
        """
        # Simple content filtering
        inappropriate_words = ["inappropriate", "offensive", "bad"]
        fact_lower = cat_fact.fact.lower()
        
        for word in inappropriate_words:
            if word in fact_lower:
                return False
        
        return True


class CatFactDeliveryProcessor(CyodaProcessor):
    """
    Processor for marking cat facts as delivered.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CatFactDeliveryProcessor",
            description="Marks cat facts as delivered and updates delivery metadata",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process cat fact delivery marking.

        Args:
            entity: The CatFact entity to process
            **kwargs: Additional processing parameters (should include campaign_id)

        Returns:
            The processed cat fact entity
        """
        try:
            self.logger.info(
                f"Marking cat fact as delivered {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CatFact for type-safe operations
            cat_fact = cast_entity(entity, CatFact)

            # Get campaign ID from kwargs if provided
            campaign_id = kwargs.get("campaign_id", "unknown")

            # Mark as delivered
            cat_fact.mark_as_delivered(campaign_id)

            self.logger.info(
                f"Cat fact {cat_fact.technical_id} marked as delivered for campaign {campaign_id}"
            )

            return cat_fact

        except Exception as e:
            self.logger.error(
                f"Error marking cat fact as delivered {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
