"""
AnalysisReportSendProcessor for Cyoda Client Application

Sends the analysis report via email.
"""

import json
import logging
from typing import Any

from application.entity.analysis_report.version_1.analysis_report import AnalysisReport
from application.entity.comment_analysis_request.version_1.comment_analysis_request import (
    CommentAnalysisRequest,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service


class AnalysisReportSendProcessor(CyodaProcessor):
    """
    Processor for sending AnalysisReport via email.
    Formats the report as HTML and sends it to the recipient.
    """

    def __init__(self) -> None:
        super().__init__(
            name="AnalysisReportSendProcessor",
            description="Sends the analysis report via email",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Send the analysis report via email according to functional requirements.

        Args:
            entity: The AnalysisReport in GENERATED state
            **kwargs: Additional processing parameters

        Returns:
            AnalysisReport with email sending attempted
        """
        try:
            self.logger.info(
                f"Sending email for AnalysisReport {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to AnalysisReport for type-safe operations
            report_entity = cast_entity(entity, AnalysisReport)

            # Find the associated CommentAnalysisRequest
            request = await self._find_comment_analysis_request_by_id(
                report_entity.analysis_request_id
            )

            if not request:
                raise Exception(
                    f"CommentAnalysisRequest not found for ID: {report_entity.analysis_request_id}"
                )

            # Format email content
            email_subject = f"Comment Analysis Report for Post {request.post_id}"
            email_body = self._format_report_as_html(report_entity, request)

            # Simulate email sending (in a real implementation, this would use an email service)
            try:
                await self._send_email(
                    to=request.recipient_email, subject=email_subject, body=email_body
                )

                self.logger.info(
                    f"Email sent successfully for AnalysisReport {report_entity.technical_id} to {request.recipient_email}"
                )

            except Exception as e:
                error_msg = f"Failed to send email: {str(e)}"
                self.logger.error(error_msg)
                raise Exception(error_msg)

            return report_entity

        except Exception as e:
            self.logger.error(
                f"Error sending email for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _find_comment_analysis_request_by_id(
        self, request_id: str
    ) -> CommentAnalysisRequest | None:
        """
        Find CommentAnalysisRequest by ID.

        Args:
            request_id: The request ID

        Returns:
            CommentAnalysisRequest entity or None if not found
        """
        entity_service = get_entity_service()

        try:
            # Try to get by technical ID first
            response = await entity_service.get_by_id(
                entity_id=request_id,
                entity_class=CommentAnalysisRequest.ENTITY_NAME,
                entity_version=str(CommentAnalysisRequest.ENTITY_VERSION),
            )

            if response:
                request_data = response.data
                if hasattr(request_data, "model_dump"):
                    request_dict: Dict[str, Any] = request_data.model_dump()
                else:
                    request_dict = request_data

                return CommentAnalysisRequest(**request_dict)

        except Exception as e:
            self.logger.warning(
                f"Failed to find CommentAnalysisRequest by ID {request_id}: {str(e)}"
            )

        return None

    def _format_report_as_html(
        self, report: AnalysisReport, request: CommentAnalysisRequest
    ) -> str:
        """
        Format the analysis report as HTML.

        Args:
            report: The AnalysisReport entity
            request: The CommentAnalysisRequest entity

        Returns:
            HTML formatted email body
        """
        try:
            keywords = json.loads(report.top_keywords)
            keywords_list = ", ".join(keywords[:5])  # Show top 5 keywords
        except (json.JSONDecodeError, TypeError):
            keywords_list = "N/A"

        html_body = f"""
        <html>
        <head>
            <title>Comment Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; }}
                .content {{ margin: 20px 0; }}
                .metric {{ margin: 10px 0; }}
                .metric strong {{ color: #333; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Comment Analysis Report</h1>
                <p>Analysis completed for Post ID: <strong>{request.post_id}</strong></p>
            </div>
            
            <div class="content">
                <h2>Analysis Results</h2>
                
                <div class="metric">
                    <strong>Total Comments Analyzed:</strong> {report.total_comments}
                </div>
                
                <div class="metric">
                    <strong>Average Comment Length:</strong> {report.average_comment_length:.1f} characters
                </div>
                
                <div class="metric">
                    <strong>Most Active Email Domain:</strong> {report.most_active_email_domain}
                </div>
                
                <div class="metric">
                    <strong>Sentiment Analysis:</strong> {report.sentiment_summary}
                </div>
                
                <div class="metric">
                    <strong>Top Keywords:</strong> {keywords_list}
                </div>
                
                <div class="metric">
                    <strong>Report Generated:</strong> {report.generated_at}
                </div>
            </div>
            
            <div class="footer">
                <p><em>This report was automatically generated by the Comment Analysis System.</em></p>
            </div>
        </body>
        </html>
        """

        return html_body

    async def _send_email(self, to: str, subject: str, body: str) -> None:
        """
        Send email (simulated implementation).

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (HTML)
        """
        # In a real implementation, this would integrate with an email service
        # For now, we'll simulate the email sending
        self.logger.info(f"SIMULATED EMAIL SEND:")
        self.logger.info(f"To: {to}")
        self.logger.info(f"Subject: {subject}")
        self.logger.info(f"Body length: {len(body)} characters")

        # Simulate potential email service failures (uncomment to test error handling)
        # import random
        # if random.random() < 0.1:  # 10% chance of failure
        #     raise Exception("Email service temporarily unavailable")

        # Simulate email sending delay
        import asyncio

        await asyncio.sleep(0.1)  # Simulate network delay
