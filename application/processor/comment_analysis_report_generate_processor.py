"""
CommentAnalysisReportGenerateProcessor for Cyoda Client Application

Generates comprehensive analysis report from analyzed comments.
Calculates statistics and creates formatted report content.
"""

import logging
from collections import Counter
from typing import Any, Dict, List, Optional, Protocol, cast, runtime_checkable

from application.entity.comment_analysis_report.version_1.comment_analysis_report import (
    CommentAnalysisReport,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


@runtime_checkable
class _HasId(Protocol):
    id: str


@runtime_checkable
class _HasMetadata(Protocol):
    metadata: _HasId


class _ListedEntity(Protocol):
    def get_id(self) -> str: ...
    def get_state(self) -> str: ...

    data: Dict[str, Any]


class _EntityService(Protocol):
    async def search(
        self,
        entity_class: str,
        condition: Any,
        entity_version: str = "1",
    ) -> List[_ListedEntity]: ...


class CommentAnalysisReportGenerateProcessor(CyodaProcessor):
    """
    Processor for generating comprehensive analysis report from analyzed comments.
    Calculates statistics and creates formatted report content.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CommentAnalysisReportGenerateProcessor",
            description="Generate comprehensive analysis report from analyzed comments",
        )
        self.entity_service: Optional[_EntityService] = None
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    def _get_entity_service(self) -> _EntityService:
        """Get entity service lazily"""
        if self.entity_service is None:
            self.entity_service = cast(_EntityService, get_entity_service())
        return self.entity_service

    def _generate_report_text(self, report: CommentAnalysisReport, post_id: int) -> str:
        """Generate formatted report text content"""
        percentages = report.get_sentiment_percentages()

        report_text = f"""Comment Analysis Report

Post ID: {post_id}
Analysis Date: {report.generated_at}

=== SUMMARY ===
Total Comments Analyzed: {report.total_comments}
Average Word Count: {report.average_word_count:.1f}
Most Active Commenter: {report.top_commenter_email}

=== SENTIMENT ANALYSIS ===
Positive Comments: {report.positive_comments} ({percentages['positive']}%)
Negative Comments: {report.negative_comments} ({percentages['negative']}%)
Neutral Comments: {report.neutral_comments} ({percentages['neutral']}%)

=== INSIGHTS ===
"""

        # Add insights based on the data
        if report.total_comments == 0:
            report_text += "No comments were found for analysis.\n"
        else:
            if percentages["positive"] > 60:
                report_text += "Overall sentiment is predominantly positive.\n"
            elif percentages["negative"] > 60:
                report_text += "Overall sentiment is predominantly negative.\n"
            else:
                report_text += "Sentiment is mixed with no clear dominant trend.\n"

            if report.average_word_count > 50:
                report_text += "Comments are generally detailed and lengthy.\n"
            elif report.average_word_count < 20:
                report_text += "Comments are generally brief and concise.\n"
            else:
                report_text += "Comments are of moderate length.\n"

        report_text += "\n=== END OF REPORT ===\n"
        return report_text

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Generate comprehensive analysis report according to functional requirements.

        Args:
            entity: The CommentAnalysisReport with analysisRequestId
            **kwargs: Additional processing parameters

        Returns:
            The report entity with complete report content
        """
        try:
            self.logger.info(
                f"Generating report for CommentAnalysisReport {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to CommentAnalysisReport for type-safe operations
            report = cast_entity(entity, CommentAnalysisReport)

            # Find comments by analysisRequestId
            entity_service = self._get_entity_service()

            # Build search condition to find comments for this request
            from common.service.entity_service import SearchConditionRequest

            condition = (
                SearchConditionRequest.builder()
                .equals("analysisRequestId", str(report.analysis_request_id))
                .build()
            )

            comments = await entity_service.search(
                entity_class="Comment",
                condition=condition,
                entity_version="1",
            )

            # Calculate statistics
            total_comments = len(comments)
            positive_comments = 0
            negative_comments = 0
            neutral_comments = 0
            total_word_count = 0
            email_counts: Counter[str] = Counter()

            for comment in comments:
                comment_data = comment.data

                # Count sentiments
                sentiment = comment_data.get("sentiment", "NEUTRAL")
                if sentiment == "POSITIVE":
                    positive_comments += 1
                elif sentiment == "NEGATIVE":
                    negative_comments += 1
                else:
                    neutral_comments += 1

                # Sum word counts
                word_count = comment_data.get("wordCount", 0)
                if isinstance(word_count, (int, float)):
                    total_word_count += int(word_count)

                # Count emails
                email = comment_data.get("email", "")
                if email:
                    email_counts[email] += 1

            # Calculate average word count
            average_word_count = (
                total_word_count / total_comments if total_comments > 0 else 0.0
            )

            # Find top commenter email
            top_commenter_email = (
                email_counts.most_common(1)[0][0]
                if email_counts
                else "unknown@example.com"
            )

            # Update report with calculated data
            report.total_comments = total_comments
            report.positive_comments = positive_comments
            report.negative_comments = negative_comments
            report.neutral_comments = neutral_comments
            report.average_word_count = average_word_count
            report.top_commenter_email = top_commenter_email

            # Get post ID for report (from first comment or analysis request)
            post_id = 0
            if comments:
                post_id = comments[0].data.get("postId", 0)

            # Generate report content
            report.report_content = self._generate_report_text(report, post_id)

            # Update timestamp
            report.update_timestamp()

            self.logger.info(
                f"Report {report.technical_id} generated successfully - {total_comments} comments analyzed"
            )

            return report

        except Exception as e:
            self.logger.error(
                f"Error generating report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise
