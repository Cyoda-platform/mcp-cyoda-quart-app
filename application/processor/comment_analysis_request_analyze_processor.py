"""
CommentAnalysisRequestAnalyzeProcessor for Cyoda Client Application

Analyzes the fetched comments and creates an AnalysisReport.
"""

import json
import logging
import re
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List

from application.entity.analysis_report.version_1.analysis_report import AnalysisReport
from application.entity.comment.version_1.comment import Comment
from application.entity.comment_analysis_request.version_1.comment_analysis_request import (
    CommentAnalysisRequest,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service


class CommentAnalysisRequestAnalyzeProcessor(CyodaProcessor):
    """
    Processor for analyzing comments and creating AnalysisReport.
    Performs sentiment analysis and keyword extraction.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisRequestAnalyzeProcessor",
            description="Analyzes fetched comments and creates an AnalysisReport",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Analyze comments and create AnalysisReport according to functional requirements.

        Args:
            entity: The CommentAnalysisRequest with associated Comment entities
            **kwargs: Additional processing parameters

        Returns:
            The entity with associated AnalysisReport created (AnalysisReport transitions to GENERATED)
        """
        try:
            self.logger.info(
                f"Analyzing comments for CommentAnalysisRequest {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisRequest for type-safe operations
            request_entity = cast_entity(entity, CommentAnalysisRequest)

            # Find comments by analysis request ID
            comments = await self._find_comments_by_request_id(
                request_entity.technical_id or request_entity.entity_id or ""
            )

            if not comments:
                self.logger.warning(
                    f"No comments found for request {request_entity.technical_id}"
                )
                return request_entity

            # Create analysis report
            report = await self._create_analysis_report(request_entity, comments)

            # Save the report with transition to GENERATED state
            entity_service = get_entity_service()
            report_data: Dict[str, Any] = report.model_dump(by_alias=True)

            response = await entity_service.save(
                entity=report_data,
                entity_class=AnalysisReport.ENTITY_NAME,
                entity_version=str(AnalysisReport.ENTITY_VERSION),
            )

            created_report_id = response.metadata.id
            self.logger.info(
                f"Created AnalysisReport {created_report_id} for request {request_entity.technical_id}"
            )

            return request_entity

        except Exception as e:
            self.logger.error(
                f"Error analyzing comments for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _find_comments_by_request_id(self, request_id: str) -> List[Comment]:
        """
        Find comments by analysis request ID.

        Args:
            request_id: The analysis request ID

        Returns:
            List of Comment entities
        """
        entity_service = get_entity_service()

        # Build search condition
        builder = SearchConditionRequest.builder()
        builder.equals("analysisRequestId", request_id)
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
                comment_data = result.data
                if hasattr(comment_data, "model_dump"):
                    comment_dict: Dict[str, Any] = comment_data.model_dump()
                else:
                    comment_dict = comment_data

                comment = Comment(**comment_dict)
                comments.append(comment)
            except Exception as e:
                self.logger.warning(f"Failed to parse comment data: {str(e)}")
                continue

        return comments

    async def _create_analysis_report(
        self, request_entity: CommentAnalysisRequest, comments: List[Comment]
    ) -> AnalysisReport:
        """
        Create analysis report from comments.

        Args:
            request_entity: The CommentAnalysisRequest
            comments: List of Comment entities

        Returns:
            AnalysisReport entity
        """
        current_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )

        # Calculate total comments
        total_comments = len(comments)

        # Calculate average comment length
        total_length = sum(len(comment.body) for comment in comments)
        average_length = total_length / total_comments if total_comments > 0 else 0.0

        # Find most active email domain
        email_domains: Counter[str] = Counter()
        for comment in comments:
            domain = comment.get_email_domain()
            if domain:
                email_domains[domain] += 1

        most_active_domain = (
            email_domains.most_common(1)[0][0] if email_domains else "unknown"
        )

        # Extract keywords and get top 10
        keywords: Counter[str] = Counter()
        for comment in comments:
            words = self._extract_keywords(comment.body)
            for word in words:
                keywords[word] += 1

        top_keywords = [word for word, _ in keywords.most_common(10)]
        top_keywords_json = json.dumps(top_keywords)

        # Simple sentiment analysis
        sentiment_summary = self._analyze_sentiment(comments)

        # Create AnalysisReport
        report = AnalysisReport(
            analysisRequestId=request_entity.technical_id
            or request_entity.entity_id
            or "",
            totalComments=total_comments,
            averageCommentLength=round(average_length, 2),
            mostActiveEmailDomain=most_active_domain,
            sentimentSummary=sentiment_summary,
            topKeywords=top_keywords_json,
            generatedAt=current_timestamp,
        )

        return report

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text.

        Args:
            text: The text to extract keywords from

        Returns:
            List of keywords
        """
        # Simple keyword extraction: lowercase, remove punctuation, filter short words
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())

        # Filter out common stop words
        stop_words = {
            "the",
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
            "from",
            "up",
            "about",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
            "among",
            "this",
            "that",
            "these",
            "those",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
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
            "must",
            "can",
            "shall",
            "not",
            "no",
            "yes",
        }

        keywords = [word for word in words if word not in stop_words]
        return keywords

    def _analyze_sentiment(self, comments: List[Comment]) -> str:
        """
        Simple sentiment analysis of comments.

        Args:
            comments: List of Comment entities

        Returns:
            Sentiment summary string
        """
        positive_words = {
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
            "marvelous",
        }

        negative_words = {
            "bad",
            "terrible",
            "awful",
            "horrible",
            "hate",
            "dislike",
            "angry",
            "frustrated",
            "disappointed",
            "sad",
            "upset",
            "annoyed",
            "disgusted",
            "worst",
            "pathetic",
            "useless",
            "stupid",
            "ridiculous",
        }

        positive_count = 0
        negative_count = 0
        total_words = 0

        for comment in comments:
            words = comment.body.lower().split()
            total_words += len(words)

            for word in words:
                clean_word = re.sub(r"[^\w]", "", word)
                if clean_word in positive_words:
                    positive_count += 1
                elif clean_word in negative_words:
                    negative_count += 1

        if positive_count > negative_count * 1.5:
            return "Mostly positive sentiment with optimistic tone"
        elif negative_count > positive_count * 1.5:
            return "Mostly negative sentiment with critical tone"
        else:
            return "Mixed sentiment with mostly neutral tone"
