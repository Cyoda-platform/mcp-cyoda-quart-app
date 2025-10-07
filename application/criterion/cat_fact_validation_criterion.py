"""
CatFact Validation Criterion for Cat Facts Subscription System

Validates that a CatFact meets all required business rules before proceeding
to the processing stage.
"""

import re
from typing import Any

from application.entity.cat_fact.version_1.cat_fact import CatFact
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaCriteriaChecker, CyodaEntity


class CatFactValidationCriterion(CyodaCriteriaChecker):
    """
    Validation criterion for CatFact that checks all business rules
    before the fact can proceed to processing stage.
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
            True if the cat fact meets all criteria, False otherwise
        """
        try:
            self.logger.info(
                f"Validating cat fact {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CatFact for type-safe operations
            cat_fact = cast_entity(entity, CatFact)

            # Validate fact text content
            if not self._is_valid_fact_text(cat_fact.fact_text):
                self.logger.warning(
                    f"Cat fact {cat_fact.technical_id} has invalid fact text"
                )
                return False

            # Validate source API
            if cat_fact.source_api not in cat_fact.ALLOWED_SOURCES:
                self.logger.warning(
                    f"Cat fact {cat_fact.technical_id} has invalid source API: {cat_fact.source_api}"
                )
                return False

            # Validate category if provided
            if (
                cat_fact.category
                and cat_fact.category not in cat_fact.ALLOWED_CATEGORIES
            ):
                self.logger.warning(
                    f"Cat fact {cat_fact.technical_id} has invalid category: {cat_fact.category}"
                )
                return False

            # Validate fact length consistency
            if not self._is_consistent_fact_length(cat_fact):
                self.logger.warning(
                    f"Cat fact {cat_fact.technical_id} has inconsistent fact length"
                )
                return False

            # Validate content quality
            if not self._meets_content_quality_standards(cat_fact.fact_text):
                self.logger.warning(
                    f"Cat fact {cat_fact.technical_id} does not meet content quality standards"
                )
                return False

            # Validate usage metrics are non-negative
            if not self._are_valid_usage_metrics(cat_fact):
                self.logger.warning(
                    f"Cat fact {cat_fact.technical_id} has invalid usage metrics"
                )
                return False

            # Check for inappropriate content
            if self._contains_inappropriate_content(cat_fact.fact_text):
                self.logger.warning(
                    f"Cat fact {cat_fact.technical_id} contains inappropriate content"
                )
                return False

            # Validate validation score if present
            if cat_fact.validation_score is not None and not self._is_valid_score(
                cat_fact.validation_score
            ):
                self.logger.warning(
                    f"Cat fact {cat_fact.technical_id} has invalid validation score: {cat_fact.validation_score}"
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

    def _is_valid_fact_text(self, fact_text: str) -> bool:
        """
        Validate fact text content.

        Args:
            fact_text: The fact text to validate

        Returns:
            True if fact text is valid
        """
        if not fact_text:
            return False

        text = fact_text.strip()

        # Check minimum length
        if len(text) < 10:
            return False

        # Check maximum length
        if len(text) > 1000:
            return False

        # Check for basic sentence structure
        if not self._has_basic_sentence_structure(text):
            return False

        return True

    def _has_basic_sentence_structure(self, text: str) -> bool:
        """
        Check if text has basic sentence structure.

        Args:
            text: Text to check

        Returns:
            True if text has basic sentence structure
        """
        # Should contain at least one letter
        if not re.search(r"[a-zA-Z]", text):
            return False

        # Should not be all uppercase (shouting)
        if text.isupper() and len(text) > 10:
            return False

        # Should not contain excessive punctuation
        punctuation_count = len(re.findall(r"[!?.]", text))
        if punctuation_count > len(text) / 10:  # More than 10% punctuation
            return False

        return True

    def _is_consistent_fact_length(self, cat_fact: CatFact) -> bool:
        """
        Check if fact_length field matches actual text length.

        Args:
            cat_fact: Cat fact to validate

        Returns:
            True if lengths are consistent
        """
        actual_length = len(cat_fact.fact_text) if cat_fact.fact_text else 0
        return cat_fact.fact_length == actual_length

    def _meets_content_quality_standards(self, fact_text: str) -> bool:
        """
        Check if content meets quality standards.

        Args:
            fact_text: Text to check

        Returns:
            True if content meets quality standards
        """
        text = fact_text.strip().lower()

        # Should be cat-related
        cat_keywords = [
            "cat",
            "cats",
            "kitten",
            "kittens",
            "feline",
            "felines",
            "meow",
            "purr",
            "whiskers",
            "paw",
            "paws",
            "tail",
        ]

        if not any(keyword in text for keyword in cat_keywords):
            return False

        # Should not be too generic
        generic_phrases = ["cats are animals", "cats have four legs", "cats are pets"]

        if any(phrase in text for phrase in generic_phrases):
            return False

        # Should have some educational or interesting content
        interesting_indicators = [
            "did you know",
            "fact",
            "research",
            "study",
            "discovered",
            "years",
            "history",
            "behavior",
            "instinct",
            "species",
        ]

        # At least some indication of interesting content OR reasonable length
        has_indicators = any(indicator in text for indicator in interesting_indicators)
        has_reasonable_length = 30 <= len(fact_text) <= 500

        return has_indicators or has_reasonable_length

    def _are_valid_usage_metrics(self, cat_fact: CatFact) -> bool:
        """
        Validate usage metrics are non-negative and logical.

        Args:
            cat_fact: Cat fact to validate

        Returns:
            True if usage metrics are valid
        """
        # Times sent should be non-negative
        if cat_fact.times_sent < 0:
            return False

        # Campaign IDs list length should match or be less than times sent
        # (one fact could be sent in multiple campaigns)
        if len(cat_fact.campaign_ids) > cat_fact.times_sent:
            return False

        return True

    def _contains_inappropriate_content(self, fact_text: str) -> bool:
        """
        Check for inappropriate content.

        Args:
            fact_text: Text to check

        Returns:
            True if content is inappropriate
        """
        text = fact_text.lower()

        # List of inappropriate words/phrases
        inappropriate_terms = [
            "hate",
            "kill",
            "death",
            "violence",
            "abuse",
            "stupid",
            "dumb",
            "idiot",
            "moron",
        ]

        return any(term in text for term in inappropriate_terms)

    def _is_valid_score(self, score: float) -> bool:
        """
        Validate validation score is within valid range.

        Args:
            score: Score to validate

        Returns:
            True if score is valid
        """
        return 0.0 <= score <= 1.0
