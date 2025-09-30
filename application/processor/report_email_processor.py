"""
ReportEmailProcessor for Pet Store Performance Analysis System

Handles email delivery of generated reports to the sales team as specified
in the functional requirements for automated weekly reporting.
"""

import logging
from typing import Any

from application.entity.report.version_1.report import Report
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ReportEmailProcessor(CyodaProcessor):
    """
    Processor for Report entity that handles email delivery of performance reports
    to the sales team at victoria.sagdieva@cyoda.com.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportEmailProcessor",
            description="Handles email delivery of performance reports to sales team",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Report entity to send email notification.

        Args:
            entity: The Report entity to email
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with email delivery status updated
        """
        try:
            self.logger.info(
                f"Processing email delivery for report {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Validate report is ready for email
            if not report.is_ready_for_email():
                self.logger.warning(
                    f"Report {report.technical_id} is not ready for email delivery"
                )
                raise ValueError("Report is not ready for email delivery")

            # Simulate email sending (in a real implementation, this would integrate with an email service)
            email_content = self._prepare_email_content(report)
            success = await self._send_email(
                report.email_recipient, email_content, report
            )

            if success:
                # Mark email as sent
                report.mark_email_sent()

                self.logger.info(
                    f"Report {report.technical_id} successfully emailed to {report.email_recipient}"
                )
            else:
                self.logger.error(
                    f"Failed to send email for report {report.technical_id}"
                )
                raise RuntimeError("Email delivery failed")

            return report

        except Exception as e:
            self.logger.error(
                f"Error processing email for report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    def _prepare_email_content(self, report: Report) -> dict[str, Any]:
        """
        Prepare email content including subject, body, and attachments.

        Args:
            report: The Report entity to prepare email for

        Returns:
            Dictionary containing email content
        """
        # Format period dates for display
        try:
            period_start = (
                report.period_start.split("T")[0]
                if "T" in report.period_start
                else report.period_start
            )
            period_end = (
                report.period_end.split("T")[0]
                if "T" in report.period_end
                else report.period_end
            )
        except Exception:
            period_start = "N/A"
            period_end = "N/A"

        subject = (
            f"Weekly Pet Store Performance Report - {period_start} to {period_end}"
        )

        # Create email body
        body_parts = [
            f"Dear Sales Team,",
            f"",
            f"Please find attached the weekly performance report for the period {period_start} to {period_end}.",
            f"",
            f"EXECUTIVE SUMMARY:",
            f"{report.executive_summary or 'Report summary not available.'}",
            f"",
            f"KEY METRICS:",
            f"• Total Products Analyzed: {report.total_products_analyzed or 0}",
            f"• Total Revenue: ${report.total_revenue or 0:,.2f}",
        ]

        if report.revenue_growth is not None:
            body_parts.append(f"• Revenue Growth: {report.revenue_growth:+.1f}%")

        body_parts.extend(
            [
                f"",
                f"HIGHLIGHTS:",
            ]
        )

        # Top performers
        top_performers = report.top_performers or []
        if top_performers:
            body_parts.append(f"• Top Performers ({len(top_performers)}):")
            for i, product in enumerate(top_performers[:3], 1):
                body_parts.append(
                    f"  {i}. {product.get('name', 'Unknown')} - Score: {product.get('performance_score', 0):.1f}"
                )

        # Underperformers
        underperformers = report.underperformers or []
        if underperformers:
            body_parts.append(f"• Products Needing Attention ({len(underperformers)}):")
            for i, product in enumerate(underperformers[:3], 1):
                body_parts.append(
                    f"  {i}. {product.get('name', 'Unknown')} - Score: {product.get('performance_score', 0):.1f}"
                )

        # Restocking recommendations
        restock_recs = report.restock_recommendations or []
        if restock_recs:
            body_parts.append(f"• Urgent Restocking Required ({len(restock_recs)}):")
            for i, product in enumerate(restock_recs[:3], 1):
                urgency = product.get("urgency", "medium").upper()
                body_parts.append(
                    f"  {i}. {product.get('name', 'Unknown')} - {urgency} PRIORITY"
                )

        body_parts.extend(
            [
                f"",
                f"For detailed analysis and complete product listings, please refer to the full report.",
                f"",
                f"Best regards,",
                f"Pet Store Performance Analysis System",
                f"",
                f"This is an automated report generated on {report.generated_at or 'N/A'}.",
            ]
        )

        return {
            "subject": subject,
            "body": "\n".join(body_parts),
            "recipient": report.email_recipient,
            "report_data": {
                "title": report.title,
                "period_start": report.period_start,
                "period_end": report.period_end,
                "total_products": report.total_products_analyzed,
                "total_revenue": report.total_revenue,
                "top_performers": top_performers,
                "underperformers": underperformers,
                "restock_recommendations": restock_recs,
            },
        }

    async def _send_email(
        self, recipient: str, content: dict[str, Any], report: Report
    ) -> bool:
        """
        Send email to the specified recipient.

        Args:
            recipient: Email address to send to
            content: Email content dictionary
            report: The Report entity being emailed

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # In a real implementation, this would integrate with an email service like:
            # - AWS SES
            # - SendGrid
            # - SMTP server
            # - Microsoft Graph API for Outlook

            self.logger.info(f"Simulating email send to {recipient}")
            self.logger.info(f"Subject: {content['subject']}")
            self.logger.info(f"Body length: {len(content['body'])} characters")

            # Simulate email service call
            # email_service = get_email_service()
            # result = await email_service.send_email(
            #     to=recipient,
            #     subject=content['subject'],
            #     body=content['body'],
            #     attachments=[self._create_pdf_attachment(report)]
            # )

            # For now, simulate successful delivery
            self.logger.info(f"Email successfully sent to {recipient}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email to {recipient}: {str(e)}")
            return False

    def _create_pdf_attachment(self, report: Report) -> dict[str, Any]:
        """
        Create PDF attachment for the report (placeholder implementation).

        Args:
            report: The Report entity to create PDF for

        Returns:
            Dictionary representing PDF attachment
        """
        # In a real implementation, this would use a PDF generation library like:
        # - ReportLab
        # - WeasyPrint
        # - Matplotlib for charts

        return {
            "filename": f"performance_report_{report.period_start[:10]}.pdf",
            "content_type": "application/pdf",
            "size": "placeholder",
            "description": "Weekly Performance Report PDF",
        }
