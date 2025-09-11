"""
CommentAnalyzeProcessor for Cyoda Client Application

Analyzes comment sentiment and extracts metrics.
Implements simple sentiment analysis based on keyword detection.
"""

import logging
from typing import Any

from application.entity.comment.version_1.comment import Comment
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CommentAnalyzeProcessor(CyodaProcessor):
    """
    Processor for analyzing comment sentiment and extracting metrics.
    Implements basic sentiment analysis using keyword detection.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalyzeProcessor",
            description="Analyze comment sentiment and extract metrics",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

        # Simple sentiment analysis keywords
        self.positive_keywords = {
            "good",
            "great",
            "excellent",
            "amazing",
            "wonderful",
            "fantastic",
            "awesome",
            "love",
            "like",
            "best",
            "perfect",
            "brilliant",
            "outstanding",
            "superb",
            "happy",
            "pleased",
            "satisfied",
            "delighted",
            "impressed",
            "recommend",
            "beautiful",
            "nice",
            "cool",
            "fun",
            "enjoy",
            "enjoyed",
        }

        self.negative_keywords = {
            "bad",
            "terrible",
            "awful",
            "horrible",
            "worst",
            "hate",
            "dislike",
            "poor",
            "disappointing",
            "frustrated",
            "angry",
            "annoyed",
            "upset",
            "useless",
            "broken",
            "failed",
            "wrong",
            "problem",
            "issue",
            "error",
            "stupid",
            "ridiculous",
            "waste",
            "regret",
            "disappointed",
            "sad",
        }

    def _analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of the given text using keyword detection.

        Args:
            text: The text to analyze

        Returns:
            Sentiment: POSITIVE, NEGATIVE, or NEUTRAL
        """
        if not text:
            return "NEUTRAL"

        # Convert to lowercase for analysis
        text_lower = text.lower()

        # Count positive and negative keywords
        positive_count = sum(
            1 for keyword in self.positive_keywords if keyword in text_lower
        )
        negative_count = sum(
            1 for keyword in self.negative_keywords if keyword in text_lower
        )

        # Determine sentiment based on keyword counts
        if positive_count > negative_count:
            return "POSITIVE"
        elif negative_count > positive_count:
            return "NEGATIVE"
        else:
            return "NEUTRAL"

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Analyze the Comment entity according to functional requirements.

        Args:
            entity: The Comment in FETCHED state
            **kwargs: Additional processing parameters

        Returns:
            The comment entity with sentiment analysis completed
        """
        try:
            self.logger.info(
                f"Analyzing Comment {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Comment for type-safe operations
            comment = cast_entity(entity, Comment)

            # Analyze sentiment of the comment body
            sentiment = self._analyze_sentiment(comment.body)
            comment.set_sentiment(sentiment)

            self.logger.info(
                f"Comment {comment.technical_id} analyzed successfully - sentiment: {sentiment}"
            )

            return comment

        except Exception as e:
            self.logger.error(
                f"Error analyzing Comment {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
