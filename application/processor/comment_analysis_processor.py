"""
CommentAnalysisProcessor for Cyoda Client Application

Analyzes individual comments for sentiment, keywords, and other metrics.
Performs natural language processing on comment text and updates the comment entity.
"""

import logging
import re
from typing import Any, List

from application.entity.comment.version_1.comment import Comment
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class CommentAnalysisProcessor(CyodaProcessor):
    """
    Processor for analyzing Comment entities with sentiment analysis,
    keyword extraction, and text metrics.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisProcessor",
            description="Analyzes comment sentiment, extracts keywords, and calculates text metrics",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Analyze the Comment entity for sentiment and content metrics.

        Args:
            entity: The Comment entity to analyze
            **kwargs: Additional processing parameters

        Returns:
            The analyzed comment with sentiment and keyword data
        """
        try:
            self.logger.info(
                f"Analyzing Comment {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Comment for type-safe operations
            comment = cast_entity(entity, Comment)

            # Perform sentiment analysis
            sentiment_score, sentiment_label = self._analyze_sentiment(comment.body)

            # Extract keywords
            keywords = self._extract_keywords(comment.body)

            # Calculate word count
            word_count = self._count_words(comment.body)

            # Set analysis results
            comment.set_analysis_results(
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label,
                word_count=word_count,
                keywords=keywords,
                analysis_version="1.0",
            )

            self.logger.info(
                f"Comment {comment.technical_id} analyzed: sentiment={sentiment_label} "
                f"({sentiment_score:.2f}), words={word_count}, keywords={len(keywords)}"
            )

            return comment

        except Exception as e:
            self.logger.error(
                f"Error analyzing comment {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _analyze_sentiment(self, text: str) -> tuple[float, str]:
        """
        Simple sentiment analysis based on keyword matching.
        In a real implementation, this would use a proper NLP library.

        Args:
            text: The text to analyze

        Returns:
            Tuple of (sentiment_score, sentiment_label)
        """
        # Simple keyword-based sentiment analysis
        positive_words = [
            "good",
            "great",
            "excellent",
            "amazing",
            "wonderful",
            "fantastic",
            "love",
            "like",
            "enjoy",
            "happy",
            "pleased",
            "satisfied",
            "perfect",
            "awesome",
            "brilliant",
            "outstanding",
            "superb",
            "magnificent",
        ]

        negative_words = [
            "bad",
            "terrible",
            "awful",
            "horrible",
            "hate",
            "dislike",
            "angry",
            "frustrated",
            "disappointed",
            "annoyed",
            "upset",
            "sad",
            "poor",
            "worst",
            "disgusting",
            "pathetic",
            "useless",
            "stupid",
            "ridiculous",
        ]

        # Convert to lowercase for matching
        text_lower = text.lower()

        # Count positive and negative words
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        # Calculate sentiment score
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            sentiment_score = 0.0
            sentiment_label = "NEUTRAL"
        else:
            sentiment_score = (positive_count - negative_count) / total_sentiment_words

            if sentiment_score > 0.1:
                sentiment_label = "POSITIVE"
            elif sentiment_score < -0.1:
                sentiment_label = "NEGATIVE"
            else:
                sentiment_label = "NEUTRAL"

        # Normalize score to -1.0 to 1.0 range
        sentiment_score = max(-1.0, min(1.0, sentiment_score))

        return sentiment_score, sentiment_label

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from the comment text.
        Simple implementation based on word frequency and filtering.

        Args:
            text: The text to extract keywords from

        Returns:
            List of extracted keywords
        """
        # Remove punctuation and convert to lowercase
        cleaned_text = re.sub(r"[^\w\s]", " ", text.lower())

        # Split into words
        words = cleaned_text.split()

        # Filter out common stop words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
            "my",
            "your",
            "his",
            "her",
            "its",
            "our",
            "their",
            "not",
            "no",
            "yes",
        }

        # Filter words: remove stop words, short words, and duplicates
        keywords = []
        seen = set()
        for word in words:
            if (
                len(word) >= 3
                and word not in stop_words
                and word not in seen
                and word.isalpha()
            ):
                keywords.append(word)
                seen.add(word)

        # Return top 10 keywords
        return keywords[:10]

    def _count_words(self, text: str) -> int:
        """
        Count the number of words in the text.

        Args:
            text: The text to count words in

        Returns:
            Number of words
        """
        # Simple word count by splitting on whitespace
        words = text.split()
        return len([word for word in words if word.strip()])
