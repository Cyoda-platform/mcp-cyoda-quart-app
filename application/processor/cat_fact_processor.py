"""
CatFact Processor for Cat Facts Subscription System

Handles cat fact processing, quality validation, and preparation for distribution.
"""

import logging
import re
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from application.entity.cat_fact.version_1.cat_fact import CatFact


class CatFactProcessor(CyodaProcessor):
    """
    Processor for processing and validating cat facts.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CatFactProcessor",
            description="Processes cat facts, validates quality, and prepares them for distribution",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process cat fact by validating quality and preparing for distribution.

        Args:
            entity: The CatFact entity to process
            **kwargs: Additional processing parameters

        Returns:
            The processed cat fact entity
        """
        try:
            self.logger.info(
                f"Processing cat fact {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CatFact for type-safe operations
            cat_fact = cast_entity(entity, CatFact)

            # Validate and score the fact quality
            quality_score = await self._validate_fact_quality(cat_fact)
            
            # Update the fact with validation results
            cat_fact.validate_fact(quality_score)

            # Clean and enhance the fact text
            cat_fact.fact_text = self._clean_fact_text(cat_fact.fact_text)

            # Update fact length after cleaning
            cat_fact.fact_length = len(cat_fact.fact_text)

            self.logger.info(
                f"Cat fact {cat_fact.technical_id} processed with quality score: {quality_score}"
            )

            return cat_fact

        except Exception as e:
            self.logger.error(
                f"Error processing cat fact {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _validate_fact_quality(self, cat_fact: CatFact) -> float:
        """
        Validate the quality of a cat fact and return a score.

        Args:
            cat_fact: The cat fact to validate

        Returns:
            Quality score between 0.0 and 1.0
        """
        score = 0.0
        
        # Length check (10-500 characters is ideal)
        length = len(cat_fact.fact_text.strip())
        if 50 <= length <= 300:
            score += 0.3
        elif 30 <= length <= 500:
            score += 0.2
        elif 10 <= length <= 30:
            score += 0.1

        # Grammar and readability check
        if self._has_good_grammar(cat_fact.fact_text):
            score += 0.2

        # Content relevance check
        if self._is_cat_related(cat_fact.fact_text):
            score += 0.3

        # Uniqueness check (simple duplicate detection)
        if self._is_unique_content(cat_fact.fact_text):
            score += 0.1

        # Educational value check
        if self._has_educational_value(cat_fact.fact_text):
            score += 0.1

        # Ensure score is within bounds
        return min(1.0, max(0.0, score))

    def _has_good_grammar(self, text: str) -> bool:
        """
        Simple grammar check for the fact text.

        Args:
            text: The text to check

        Returns:
            True if text appears to have good grammar
        """
        # Basic checks for good grammar
        text = text.strip()
        
        # Should start with capital letter
        if not text[0].isupper():
            return False
            
        # Should end with proper punctuation
        if not text.endswith(('.', '!', '?')):
            return False
            
        # Should not have multiple consecutive spaces
        if '  ' in text:
            return False
            
        # Should not have obvious typos (very basic check)
        common_typos = ['teh', 'adn', 'hte', 'taht', 'thier']
        text_lower = text.lower()
        for typo in common_typos:
            if typo in text_lower:
                return False
                
        return True

    def _is_cat_related(self, text: str) -> bool:
        """
        Check if the text is related to cats.

        Args:
            text: The text to check

        Returns:
            True if text is cat-related
        """
        cat_keywords = [
            'cat', 'cats', 'kitten', 'kittens', 'feline', 'felines',
            'meow', 'purr', 'whiskers', 'paw', 'paws', 'tail',
            'domestic cat', 'house cat', 'tabby', 'calico', 'siamese',
            'persian', 'maine coon', 'bengal', 'ragdoll', 'british shorthair'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in cat_keywords)

    def _is_unique_content(self, text: str) -> bool:
        """
        Simple uniqueness check for the fact text.

        Args:
            text: The text to check

        Returns:
            True if content appears unique
        """
        # In a real implementation, this would check against a database
        # For now, we'll do basic checks for common/generic content
        
        generic_phrases = [
            'cats are animals',
            'cats have four legs',
            'cats are pets',
            'cats meow'
        ]
        
        text_lower = text.lower()
        return not any(phrase in text_lower for phrase in generic_phrases)

    def _has_educational_value(self, text: str) -> bool:
        """
        Check if the fact has educational value.

        Args:
            text: The text to check

        Returns:
            True if text has educational value
        """
        educational_indicators = [
            'did you know', 'fact', 'research', 'study', 'scientists',
            'discovered', 'found', 'years', 'history', 'ancient',
            'behavior', 'instinct', 'evolution', 'species', 'breed'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in educational_indicators)

    def _clean_fact_text(self, text: str) -> str:
        """
        Clean and enhance the fact text.

        Args:
            text: The text to clean

        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Ensure proper sentence ending
        if not text.endswith(('.', '!', '?')):
            text += '.'
            
        # Capitalize first letter
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
            
        return text
