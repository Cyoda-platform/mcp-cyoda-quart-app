"""
CatFactValidationCriterion for Cat Fact Subscription Application

Validates that a CatFact meets all required business rules before it can
proceed to the preparation stage.
"""

from typing import Any

from application.entity.cat_fact.version_1.cat_fact import CatFact
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class CatFactValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for CatFact that checks all business rules
    before the entity can proceed to preparation stage.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CatFactValidationCriterion",
            description="Validates CatFact business rules and content quality",
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

            # Validate required fields
            if not cat_fact.fact or len(cat_fact.fact.strip()) < 10:
                self.logger.warning(
                    f"Cat fact {cat_fact.technical_id} has invalid or too short content"
                )
                return False

            if len(cat_fact.fact) > 1000:
                self.logger.warning(
                    f"Cat fact {cat_fact.technical_id} content is too long"
                )
                return False

            # Validate content quality
            if not self._has_cat_related_content(cat_fact.fact):
                self.logger.warning(
                    f"Cat fact {cat_fact.technical_id} does not appear to be cat-related"
                )
                return False

            # Check for inappropriate content
            if self._contains_inappropriate_content(cat_fact.fact):
                self.logger.warning(
                    f"Cat fact {cat_fact.technical_id} contains inappropriate content"
                )
                return False

            # Validate source information
            if not cat_fact.source_api:
                self.logger.warning(
                    f"Cat fact {cat_fact.technical_id} missing source API information"
                )
                return False

            self.logger.info(
                f"Cat fact {cat_fact.technical_id} passed all validation criteria"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Error validating cat fact {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            return False

    def _has_cat_related_content(self, fact: str) -> bool:
        """
        Check if the fact content is cat-related.

        Args:
            fact: The fact content to check

        Returns:
            True if cat-related, False otherwise
        """
        cat_keywords = [
            "cat",
            "cats",
            "feline",
            "felines",
            "kitten",
            "kittens",
            "meow",
            "purr",
            "whiskers",
            "paw",
            "paws",
            "tail",
        ]

        fact_lower = fact.lower()
        return any(keyword in fact_lower for keyword in cat_keywords)

    def _contains_inappropriate_content(self, fact: str) -> bool:
        """
        Check if the fact contains inappropriate content.

        Args:
            fact: The fact content to check

        Returns:
            True if inappropriate content found, False otherwise
        """
        # Simple inappropriate content detection
        inappropriate_words = [
            "inappropriate",
            "offensive",
            "bad",
            "terrible",
            "awful",
            "hate",
            "violence",
            "death",
            "kill",
        ]

        fact_lower = fact.lower()
        return any(word in fact_lower for word in inappropriate_words)
