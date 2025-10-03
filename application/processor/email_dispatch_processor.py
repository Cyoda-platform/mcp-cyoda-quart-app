"""
EmailDispatchProcessor for Pet Store Performance Analysis System

Handles email dispatch of generated reports to the sales team as specified
in functional requirements for automated weekly reporting.
"""

import logging
from typing import Any

from application.entity.report.version_1.report import Report
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class EmailDispatchProcessor(CyodaProcessor):
    """
    Processor for Report entity that handles email dispatch of generated reports
    to the sales team at victoria.sagdieva@cyoda.com.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailDispatchProcessor",
            description="Dispatches generated reports via email to sales team",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process the Report entity to dispatch email to sales team.

        Args:
            entity: The Report entity to email
            **kwargs: Additional processing parameters

        Returns:
            The processed entity with updated email status
        """
        try:
            self.logger.info(
                f"Dispatching email for Report {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Validate report is ready for email
            if not report.is_ready_for_email():
                error_msg = "Report is not ready for email dispatch"
                self.logger.warning(f"Report {report.technical_id}: {error_msg}")
                report.mark_email_failed(error_msg)
                return report

            # Simulate email dispatch (in real implementation, integrate with email service)
            success = await self._send_email(report)

            if success:
                report.mark_email_sent()
                self.logger.info(
                    f"Report {report.technical_id} successfully emailed to {', '.join(report.email_recipients)}"
                )
            else:
                error_msg = "Email service unavailable"
                report.mark_email_failed(error_msg)
                self.logger.error(
                    f"Failed to email Report {report.technical_id}: {error_msg}"
                )

            return report

        except Exception as e:
            self.logger.error(
                f"Error dispatching email for Report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Mark email as failed
            if hasattr(entity, "mark_email_failed"):
                entity.mark_email_failed(str(e))
            raise

    async def _send_email(self, report: Report) -> bool:
        """
        Send email with report content to recipients.

        Args:
            report: The Report entity to email

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # In a real implementation, this would integrate with an email service
            # like SendGrid, AWS SES, or SMTP server

            email_subject = f"Weekly Performance Report - {report.title}"
            email_body = self._generate_email_body(report)

            self.logger.info("Simulating email dispatch:")
            self.logger.info(f"To: {', '.join(report.email_recipients)}")
            self.logger.info(f"Subject: {email_subject}")
            self.logger.info(f"Body length: {len(email_body)} characters")

            # Simulate successful email dispatch
            # In real implementation, replace with actual email service call
            return True

        except Exception as e:
            self.logger.error(f"Error in email service: {str(e)}")
            return False

    def _generate_email_body(self, report: Report) -> str:
        """
        Generate email body content from report data.

        Args:
            report: The Report entity

        Returns:
            Formatted email body content
        """
        body = f"""Dear Sales Team,

Please find below the weekly performance analysis report for the period {report.report_period_start} to {report.report_period_end}.

{report.executive_summary or 'Executive summary not available.'}

KEY METRICS:
- Total Revenue: ${report.total_revenue or 0:,.2f}
- Total Sales Volume: {report.total_sales_volume or 0:,} units
- Average Performance Score: {report.average_performance_score or 0:.1f}/100

TOP PERFORMERS:
"""

        if report.top_performers:
            for i, product in enumerate(report.top_performers[:3], 1):
                body += f"{i}. {product.get('name', 'Unknown')} - Score: {product.get('performanceScore', 0):.1f}\n"
        else:
            body += "No top performers identified.\n"

        body += "\nRESTOCK RECOMMENDATIONS:\n"

        if report.restock_recommendations:
            for product in report.restock_recommendations[:5]:
                priority = product.get("priority", "MEDIUM")
                body += f"- {product.get('name', 'Unknown')} (Priority: {priority})\n"
        else:
            body += "No immediate restocking required.\n"

        body += f"""
For detailed analysis and complete product listings, please access the full report in the system.

Report generated on: {report.generated_at or 'Unknown'}
Products analyzed: {report.products_analyzed or 0}

Best regards,
Automated Performance Analysis System
"""

        return body
