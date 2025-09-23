"""
CatFactValidationCriterion for Cat Fact Subscription Application

Validates that a CatFact meets all required business rules before it can
proceed to the preparation stage as specified in functional requirements.
"""

from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity
from application.entity.cat_fact.version_1.cat_fact import CatFact


class CatFactValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for CatFact that checks all business rules
    before the entity can proceed to preparation stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CatFactValidationCriterion",
            description="Validates CatFact content quality and appropriateness",
        )

    async def check(self, entity: CyodaEntity, **kwargs: Any) -> bool:
        """
        Check if the cat fact meets all validation criteria.

        Args:
            entity: The CyodaEntity to validate (expected to be CatFact)
            **kwargs: Additional criteria parameters

        Returns:
            True if the entity meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating cat fact {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CatFact for type-safe operations
            cat_fact = cast_entity(entity, CatFact)

            # Validate fact text length
            if not cat_fact.fact_text or len(cat_fact.fact_text.strip()) < 10:
                self.logger.warning(
                    f"CatFact {cat_fact.technical_id} has fact text too short: '{cat_fact.fact_text}'"
                )
                return False

            if len(cat_fact.fact_text) > 1000:
                self.logger.warning(
                    f"CatFact {cat_fact.technical_id} has fact text too long: {len(cat_fact.fact_text)} characters"
                )
                return False

            # Check for inappropriate content (basic filtering)
            inappropriate_words = ["inappropriate", "offensive", "bad", "terrible"]
            fact_lower = cat_fact.fact_text.lower()
            
            for word in inappropriate_words:
                if word in fact_lower:
                    self.logger.warning(
                        f"CatFact {cat_fact.technical_id} contains potentially inappropriate content"
                    )
                    return False

            # Validate source
            if not cat_fact.source or len(cat_fact.source.strip()) == 0:
                self.logger.warning(
                    f"CatFact {cat_fact.technical_id} has empty source"
                )
                return False

            # Check if fact is marked as appropriate
            if not cat_fact.is_appropriate:
                self.logger.warning(
                    f"CatFact {cat_fact.technical_id} is marked as inappropriate"
                )
                return False

            # Validate quality score if present
            if cat_fact.quality_score is not None:
                if not (0.0 <= cat_fact.quality_score <= 1.0):
                    self.logger.warning(
                        f"CatFact {cat_fact.technical_id} has invalid quality score: {cat_fact.quality_score}"
                    )
                    return False
                
                # Require minimum quality score
                if cat_fact.quality_score < 0.5:
                    self.logger.warning(
                        f"CatFact {cat_fact.technical_id} quality score too low: {cat_fact.quality_score}"
                    )
                    return False

            self.logger.info(
                f"CatFact {cat_fact.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating cat fact {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False
