"""
ReportEmailProcessor for Pet Store Performance Analysis System

Handles email delivery of generated performance reports to the sales team
as specified in functional requirements.
"""

import logging
from typing import Any

from application.entity.report.version_1.report import Report
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ReportEmailProcessor(CyodaProcessor):
    """
    Processor for Report entities that handles email delivery of performance
    reports to the sales team (victoria.sagdieva@cyoda.com).
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportEmailProcessor",
            description="Sends generated performance reports via email to the sales team",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Report entity to send it via email.

        Args:
            entity: The Report entity to email (must be in 'generated' state)
            **kwargs: Additional processing parameters

        Returns:
            The report with updated email status
        """
        try:
            self.logger.info(
                f"Sending Report {getattr(entity, 'technical_id', '<unknown>')} via email"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Simulate email sending (in a real implementation, this would use an email service)
            success = await self._send_email(report)

            if success:
                report.mark_email_sent()
                self.logger.info(
                    f"Report {report.technical_id} sent successfully to {len(report.email_recipients)} recipients"
                )
            else:
                report.mark_email_failed()
                self.logger.error(f"Failed to send Report {report.technical_id}")

            return report

        except Exception as e:
            self.logger.error(
                f"Error sending Report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Mark as failed and re-raise
            if hasattr(entity, "mark_email_failed"):
                entity.mark_email_failed()
            raise

    async def _send_email(self, report: Report) -> bool:
        """
        Send the report via email (simulated implementation).

        In a real implementation, this would integrate with an email service
        like SendGrid, AWS SES, or SMTP server.

        Args:
            report: The Report entity to send

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # Prepare email content
            subject = f"{report.report_title} - {report.report_period_start} to {report.report_period_end}"

            # Create email body with executive summary
            email_body = self._create_email_body(report)

            # Log the email details (in real implementation, this would send actual email)
            self.logger.info("EMAIL SIMULATION - Sending report:")
            self.logger.info(f"To: {', '.join(report.email_recipients)}")
            self.logger.info(f"Subject: {subject}")
            self.logger.info(f"Body length: {len(email_body)} characters")
            self.logger.info(f"Report format: {report.report_format}")

            if report.report_content:
                self.logger.info(
                    f"Attachment: Report content ({len(report.report_content)} characters)"
                )

            # Simulate email sending delay and success
            import asyncio

            await asyncio.sleep(0.1)  # Simulate network delay

            # In a real implementation, you would:
            # 1. Connect to email service (SMTP, SendGrid, etc.)
            # 2. Create email with HTML body and/or PDF attachment
            # 3. Send to all recipients
            # 4. Handle delivery confirmations and failures

            # For now, simulate success
            return True

        except Exception as e:
            self.logger.error(f"Error in email sending simulation: {str(e)}")
            return False

    def _create_email_body(self, report: Report) -> str:
        """
        Create the email body content.

        Args:
            report: The Report entity

        Returns:
            Email body content as HTML string
        """
        body_parts = [
            "<html><body>",
            "<h2>Pet Store Performance Analysis Report</h2>",
            "<p>Dear Sales Team,</p>",
            f"<p>Please find attached the weekly performance analysis report for the period "
            f"{report.report_period_start} to {report.report_period_end}.</p>",
        ]

        # Add executive summary if available
        if report.executive_summary:
            body_parts.extend(
                [
                    "<h3>Executive Summary</h3>",
                    f"<pre>{report.executive_summary}</pre>",
                ]
            )

        # Add key highlights
        body_parts.append("<h3>Key Highlights</h3>")
        body_parts.append("<ul>")

        if report.high_performers:
            body_parts.append(
                f"<li><strong>High Performers:</strong> {len(report.high_performers)} products showing excellent performance</li>"
            )

        if report.underperformers:
            body_parts.append(
                f"<li><strong>Attention Needed:</strong> {len(report.underperformers)} products requiring review</li>"
            )

        if report.restock_recommendations:
            body_parts.append(
                f"<li><strong>Restocking Required:</strong> {len(report.restock_recommendations)} products need inventory replenishment</li>"
            )

        if report.total_revenue:
            body_parts.append(
                f"<li><strong>Total Revenue:</strong> ${report.total_revenue:,.2f}</li>"
            )

        if report.total_sales_volume:
            body_parts.append(
                f"<li><strong>Total Units Sold:</strong> {report.total_sales_volume:,}</li>"
            )

        body_parts.append("</ul>")

        # Add trending categories if available
        if report.trending_categories:
            body_parts.extend(
                [
                    "<h3>Trending Categories</h3>",
                    f"<p>{', '.join(report.trending_categories)}</p>",
                ]
            )

        # Add declining categories if available
        if report.declining_categories:
            body_parts.extend(
                [
                    "<h3>Categories Needing Attention</h3>",
                    f"<p>{', '.join(report.declining_categories)}</p>",
                ]
            )

        # Footer
        body_parts.extend(
            [
                "<hr>",
                "<p>This report was automatically generated by the Pet Store Performance Analysis System.</p>",
                f"<p>Generated on: {report.generated_at}</p>",
                "<p>For questions or support, please contact the system administrator.</p>",
                "</body></html>",
            ]
        )

        return "\n".join(body_parts)

    def _create_pdf_attachment(self, report: Report) -> bytes:
        """
        Create a PDF attachment from the report content.

        This is a placeholder for PDF generation functionality.
        In a real implementation, you would use a library like:
        - weasyprint
        - reportlab
        - pdfkit

        Args:
            report: The Report entity

        Returns:
            PDF content as bytes
        """
        # Placeholder implementation
        # In reality, you would convert the HTML content to PDF
        pdf_content = f"""
        PDF Report: {report.report_title}
        Period: {report.report_period_start} to {report.report_period_end}

        {report.executive_summary or 'No summary available'}

        Generated: {report.generated_at}
        """

        return pdf_content.encode("utf-8")
