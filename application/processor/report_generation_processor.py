"""
ReportGenerationProcessor for Cyoda Client Application

Generates analysis reports by aggregating data from analyzed comments
for a specific post and calculating summary statistics.
"""

import logging
from collections import Counter
from typing import Any, List

from application.entity.comment.version_1.comment import Comment
from application.entity.comment_analysis_report.version_1.comment_analysis_report import (
    CommentAnalysisReport,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service


class ReportGenerationProcessor(CyodaProcessor):
    """
    Processor for generating CommentAnalysisReport entities by aggregating
    analysis results from all analyzed comments for a specific post.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportGenerationProcessor",
            description="Generates analysis reports by aggregating comment analysis data",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Generate analysis report by aggregating comment data for the post.

        Args:
            entity: The CommentAnalysisReport entity to populate
            **kwargs: Additional processing parameters

        Returns:
            The report with aggregated analysis results
        """
        try:
            self.logger.info(
                f"Generating report for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisReport for type-safe operations
            report = cast_entity(entity, CommentAnalysisReport)

            # Get all analyzed comments for this post
            analyzed_comments = await self._get_analyzed_comments(report.post_id)

            if not analyzed_comments:
                self.logger.warning(
                    f"No analyzed comments found for post {report.post_id}"
                )
                # Set empty results
                report.set_analysis_results(
                    total_comments=0,
                    positive_comments=0,
                    negative_comments=0,
                    neutral_comments=0,
                    average_sentiment_score=0.0,
                    most_common_keywords=[],
                    average_word_count=0.0,
                )
            else:
                # Calculate aggregated statistics
                stats = self._calculate_statistics(analyzed_comments)

                # Set analysis results
                report.set_analysis_results(
                    total_comments=stats["total_comments"],
                    positive_comments=stats["positive_comments"],
                    negative_comments=stats["negative_comments"],
                    neutral_comments=stats["neutral_comments"],
                    average_sentiment_score=stats["average_sentiment_score"],
                    most_common_keywords=stats["most_common_keywords"],
                    average_word_count=stats["average_word_count"],
                )

            self.logger.info(
                f"Report generated for post {report.post_id}: "
                f"{report.total_comments} comments analyzed"
            )

            return report

        except Exception as e:
            self.logger.error(
                f"Error generating report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _get_analyzed_comments(self, post_id: int) -> List[Comment]:
        """
        Retrieve all analyzed comments for a specific post.

        Args:
            post_id: The post ID to get comments for

        Returns:
            List of analyzed Comment entities
        """
        entity_service = get_entity_service()

        try:
            # Build search condition for analyzed comments of this post
            builder = SearchConditionRequest.builder()
            builder.equals("postId", str(post_id))
            builder.equals("state", "analyzed")  # Only get analyzed comments
            condition = builder.build()

            # Search for comments
            results = await entity_service.search(
                entity_class=Comment.ENTITY_NAME,
                condition=condition,
                entity_version=str(Comment.ENTITY_VERSION),
            )

            # Convert results to Comment entities
            comments = []
            for result in results:
                try:
                    # Create Comment from the result data
                    if hasattr(result.data, "model_dump"):
                        comment_data = result.data.model_dump()
                        if isinstance(comment_data, dict):
                            comment = Comment(**comment_data)
                        else:
                            continue
                    else:
                        # result.data is already a CyodaEntity, try to cast it
                        comment = cast_entity(result.data, Comment)
                    comments.append(comment)
                except Exception as e:
                    self.logger.warning(
                        f"Failed to convert comment result to entity: {str(e)}"
                    )
                    continue

            self.logger.info(
                f"Found {len(comments)} analyzed comments for post {post_id}"
            )
            return comments

        except Exception as e:
            self.logger.error(f"Error retrieving comments for post {post_id}: {str(e)}")
            return []

    def _calculate_statistics(self, comments: List[Comment]) -> dict[str, Any]:
        """
        Calculate aggregated statistics from analyzed comments.

        Args:
            comments: List of analyzed Comment entities

        Returns:
            Dictionary containing calculated statistics
        """
        total_comments = len(comments)

        # Count sentiment labels
        positive_comments = sum(1 for c in comments if c.sentiment_label == "POSITIVE")
        negative_comments = sum(1 for c in comments if c.sentiment_label == "NEGATIVE")
        neutral_comments = sum(1 for c in comments if c.sentiment_label == "NEUTRAL")

        # Calculate average sentiment score
        sentiment_scores = [
            c.sentiment_score for c in comments if c.sentiment_score is not None
        ]
        average_sentiment_score = (
            sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
        )

        # Calculate average word count
        word_counts = [c.word_count for c in comments if c.word_count is not None]
        average_word_count = sum(word_counts) / len(word_counts) if word_counts else 0.0

        # Find most common keywords
        all_keywords = []
        for comment in comments:
            if comment.contains_keywords:
                all_keywords.extend(comment.contains_keywords)

        # Get top 10 most common keywords
        keyword_counter = Counter(all_keywords)
        most_common_keywords = [
            keyword for keyword, _ in keyword_counter.most_common(10)
        ]

        return {
            "total_comments": total_comments,
            "positive_comments": positive_comments,
            "negative_comments": negative_comments,
            "neutral_comments": neutral_comments,
            "average_sentiment_score": round(average_sentiment_score, 3),
            "most_common_keywords": most_common_keywords,
            "average_word_count": round(average_word_count, 1),
        }
