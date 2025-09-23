"""
ReportEmailProcessor for Product Performance Analysis and Reporting System

Handles email delivery for Report entities, sending performance analysis reports
to specified recipients (victoria.sagdieva@cyoda.com as per requirements).
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from application.entity.report.version_1.report import Report
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ReportEmailProcessor(CyodaProcessor):
    """
    Processor for Report entity that handles email delivery.

    Sends generated reports via email to specified recipients.
    In a production environment, this would integrate with an email service.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportEmailProcessor",
            description="Sends performance analysis reports via email",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Report entity to send email.

        Args:
            entity: The Report entity to process
            **kwargs: Additional processing parameters

        Returns:
            The Report entity with updated email status
        """
        try:
            self.logger.info(
                f"Processing Report email for entity {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Validate report is ready for emailing
            if not report.is_generated():
                raise ValueError("Report must be generated before emailing")

            # Prepare email content
            email_content = self._prepare_email_content(report)

            # Send email (simulated in this implementation)
            success = await self._send_email(
                recipient=report.email_recipient,
                subject=report.get_email_subject_line(),
                content=email_content,
                report=report,
            )

            # Update report status based on email result
            if success:
                report.mark_email_sent()
                self.logger.info(
                    f"Report {report.technical_id} emailed successfully to {report.email_recipient}"
                )
            else:
                report.mark_email_failed()
                self.logger.error(
                    f"Failed to email report {report.technical_id} to {report.email_recipient}"
                )

            return report

        except Exception as e:
            self.logger.error(
                f"Error emailing report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Mark email as failed
            if hasattr(entity, "mark_email_failed"):
                entity.mark_email_failed()
            raise

    def _prepare_email_content(self, report: Report) -> Dict[str, Any]:
        """
        Prepare email content from report data.

        Args:
            report: The Report entity

        Returns:
            Dictionary containing email content
        """
        # Extract key metrics from report data
        report_data = report.report_data or {}
        key_metrics = report_data.get("key_metrics", {})

        # Create HTML email content
        html_content = self._generate_html_content(report, report_data, key_metrics)

        # Create plain text content
        text_content = self._generate_text_content(report, report_data, key_metrics)

        return {
            "html_content": html_content,
            "text_content": text_content,
            "attachments": [],  # Could add CSV/PDF attachments in the future
        }

    def _generate_html_content(
        self, report: Report, report_data: Dict[str, Any], key_metrics: Dict[str, Any]
    ) -> str:
        """Generate HTML email content"""
        overall_score = report_data.get("overall_performance_score", 0.0)
        total_pets = key_metrics.get("total_pets_analyzed", 0)
        total_stores = key_metrics.get("total_stores_analyzed", 0)

        # Get performance tier color
        score_color = self._get_score_color(overall_score)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{report.report_title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .score {{ font-size: 24px; font-weight: bold; color: {score_color}; }}
                .metrics {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .metric {{ text-align: center; padding: 15px; background-color: #e9ecef; border-radius: 5px; }}
                .recommendations {{ background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #6c757d; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report.report_title}</h1>
                <p><strong>Report Period:</strong> {report.report_period}</p>
                <p><strong>Generated:</strong> {report.generated_at}</p>
                <div class="score">Overall Performance Score: {overall_score:.1f}/100</div>
            </div>
            
            <div class="metrics">
                <div class="metric">
                    <h3>{total_pets}</h3>
                    <p>Pets Analyzed</p>
                </div>
                <div class="metric">
                    <h3>{total_stores}</h3>
                    <p>Stores Analyzed</p>
                </div>
                <div class="metric">
                    <h3>{key_metrics.get('average_pet_score', 0.0):.1f}</h3>
                    <p>Avg Pet Score</p>
                </div>
                <div class="metric">
                    <h3>{key_metrics.get('average_store_score', 0.0):.1f}</h3>
                    <p>Avg Store Score</p>
                </div>
            </div>
            
            <h2>Executive Summary</h2>
            <p>{report.summary or 'No summary available.'}</p>
            
            <div class="recommendations">
                <h2>Recommendations</h2>
                <ul>
        """

        for recommendation in report.recommendations:
            html_content += f"<li>{recommendation}</li>"

        html_content += f"""
                </ul>
            </div>
            
            <h2>Detailed Analysis</h2>
            <p>This report analyzed data from the Pet Store API and provides insights into:</p>
            <ul>
                <li>Pet availability and performance metrics</li>
                <li>Store inventory management</li>
                <li>Sales performance trends</li>
                <li>Data completeness and quality</li>
            </ul>
            
            <div class="footer">
                <p>This report was automatically generated by the Product Performance Analysis and Reporting System.</p>
                <p>For questions or support, please contact the development team.</p>
            </div>
        </body>
        </html>
        """

        return html_content

    def _generate_text_content(
        self, report: Report, report_data: Dict[str, Any], key_metrics: Dict[str, Any]
    ) -> str:
        """Generate plain text email content"""
        overall_score = report_data.get("overall_performance_score", 0.0)
        total_pets = key_metrics.get("total_pets_analyzed", 0)
        total_stores = key_metrics.get("total_stores_analyzed", 0)

        text_content = f"""
{report.report_title}
{'=' * len(report.report_title)}

Report Period: {report.report_period}
Generated: {report.generated_at}

OVERALL PERFORMANCE SCORE: {overall_score:.1f}/100

KEY METRICS:
- Pets Analyzed: {total_pets}
- Stores Analyzed: {total_stores}
- Average Pet Score: {key_metrics.get('average_pet_score', 0.0):.1f}/100
- Average Store Score: {key_metrics.get('average_store_score', 0.0):.1f}/100

EXECUTIVE SUMMARY:
{report.summary or 'No summary available.'}

RECOMMENDATIONS:
"""

        for i, recommendation in enumerate(report.recommendations, 1):
            text_content += f"{i}. {recommendation}\n"

        text_content += f"""

DETAILED ANALYSIS:
This report analyzed data from the Pet Store API and provides insights into:
- Pet availability and performance metrics
- Store inventory management
- Sales performance trends
- Data completeness and quality

---
This report was automatically generated by the Product Performance Analysis and Reporting System.
For questions or support, please contact the development team.
        """

        return text_content.strip()

    def _get_score_color(self, score: float) -> str:
        """Get color based on performance score"""
        if score >= 80.0:
            return "#28a745"  # Green
        elif score >= 60.0:
            return "#ffc107"  # Yellow
        else:
            return "#dc3545"  # Red

    async def _send_email(
        self, recipient: str, subject: str, content: Dict[str, Any], report: Report
    ) -> bool:
        """
        Send email to recipient.

        In a production environment, this would integrate with an email service
        like SendGrid, AWS SES, or SMTP server.

        Args:
            recipient: Email recipient
            subject: Email subject
            content: Email content (HTML and text)
            report: Report entity

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Simulate email sending
            self.logger.info(f"Sending email to {recipient}")
            self.logger.info(f"Subject: {subject}")
            self.logger.info(f"Content length: {len(content.get('html_content', ''))}")

            # In a real implementation, you would:
            # 1. Connect to email service
            # 2. Send the email with HTML and text content
            # 3. Handle any errors or retries
            # 4. Return success/failure status

            # For now, we'll simulate success for the demo
            # but log the email details for verification
            self.logger.info(
                "EMAIL SIMULATION - Report would be sent to: victoria.sagdieva@cyoda.com"
            )
            self.logger.info(
                f"EMAIL CONTENT PREVIEW:\n{content.get('text_content', '')[:500]}..."
            )

            # Simulate a small chance of failure for testing
            import random

            if random.random() < 0.05:  # 5% chance of failure
                self.logger.warning("Simulated email delivery failure")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return False
