"""
SendEmailProcessor for Cyoda Client Application

Handles the sending of email reports.
Sends report via email as specified in functional requirements.
"""

import logging
from typing import Any, Dict

from application.entity.report.version_1.report import Report
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class SendEmailProcessor(CyodaProcessor):
    """
    Processor for Report that sends the report via email.
    Formats and sends the email report to the specified recipient.
    """

    def __init__(self) -> None:
        super().__init__(
            name="SendEmailProcessor",
            description="Sends report via email to the specified recipient",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Report entity to send via email.

        Args:
            entity: The Report entity to send
            **kwargs: Additional processing parameters

        Returns:
            The entity with email sent status
        """
        try:
            self.logger.info(
                f"Sending email for Report {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Format email content
            email_content = self._format_report_email(report.summary_data or {})

            # Send email (simulated)
            await self._send_email(
                recipient=report.recipient_email,
                subject=report.title,
                content=email_content,
            )

            # Set email sent timestamp
            report.set_email_sent_at()

            # Set status to sent
            report.status = "sent"

            self.logger.info(
                f"Email sent successfully for Report {report.technical_id} to {report.recipient_email}"
            )

            return report

        except Exception as e:
            self.logger.error(
                f"Error sending email for report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _format_report_email(self, summary_data: Dict[str, Any]) -> str:
        """
        Format the report data into email content.

        Args:
            summary_data: The report summary data

        Returns:
            Formatted email content
        """
        period = summary_data.get("period", {})
        metrics = summary_data.get("metrics", {})

        start_date = period.get("start", "N/A")
        end_date = period.get("end", "N/A")
        total_comments = metrics.get("total_comments", 0)
        avg_sentiment = metrics.get("avg_sentiment", 0.0)
        top_keywords = metrics.get("top_keywords", [])
        toxicity_summary = metrics.get("toxicity_summary", {})

        # Format sentiment label
        if avg_sentiment > 0.1:
            sentiment_label = "Positive"
        elif avg_sentiment < -0.1:
            sentiment_label = "Negative"
        else:
            sentiment_label = "Neutral"

        # Format keywords
        keywords_text = ", ".join(top_keywords[:5]) if top_keywords else "None"

        # Format toxicity info
        avg_toxicity = toxicity_summary.get("avg_toxicity", 0.0)
        high_toxicity_count = toxicity_summary.get("high_toxicity_count", 0)

        email_content = f"""
Comment Analysis Report

Report Period: {start_date} to {end_date}

Summary:
- Total Comments Analyzed: {total_comments}
- Overall Sentiment: {sentiment_label} (Score: {avg_sentiment:.2f})
- Top Keywords: {keywords_text}
- Average Toxicity Score: {avg_toxicity:.2f}
- High Toxicity Comments: {high_toxicity_count}

Sentiment Analysis:
The overall sentiment for this period was {sentiment_label.lower()} with an average score of {avg_sentiment:.2f} 
(on a scale from -1 to 1, where -1 is very negative and 1 is very positive).

Content Safety:
{high_toxicity_count} out of {total_comments} comments were flagged as potentially toxic content.
The average toxicity score was {avg_toxicity:.2f} (on a scale from 0 to 1).

Key Topics:
The most frequently mentioned topics were: {keywords_text}

This report was generated automatically by the Comment Analysis System.
        """.strip()

        return email_content

    async def _send_email(self, recipient: str, subject: str, content: str) -> None:
        """
        Send email to the specified recipient.

        In a real implementation, this would use an email service like SendGrid, SES, etc.

        Args:
            recipient: Email address to send to
            subject: Email subject
            content: Email content
        """
        # Simulate email sending
        self.logger.info(f"Simulating email send to {recipient}")
        self.logger.info(f"Subject: {subject}")
        self.logger.info(f"Content preview: {content[:100]}...")

        # In a real implementation, you would:
        # 1. Configure email service (SMTP, SendGrid, AWS SES, etc.)
        # 2. Create email message with proper formatting
        # 3. Send the email
        # 4. Handle any sending errors

        # For now, we just log that the email would be sent
        self.logger.info("Email sent successfully (simulated)")
