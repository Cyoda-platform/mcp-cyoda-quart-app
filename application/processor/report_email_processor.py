"""
ReportEmailProcessor for Pet Store Performance Analysis System

Handles email dispatch of performance reports to victoria.sagdieva@cyoda.com
including email formatting, attachment preparation, and delivery tracking
as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from application.entity.report.version_1.report import Report
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class ReportEmailProcessor(CyodaProcessor):
    """
    Processor for Report entity that handles email dispatch to the sales team,
    formats email content, and tracks delivery status.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportEmailProcessor",
            description="Handles email dispatch of performance reports to sales team",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Process report for email dispatch to victoria.sagdieva@cyoda.com.

        Args:
            entity: The Report entity to email
            **kwargs: Additional processing parameters

        Returns:
            The processed report with email status updated
        """
        try:
            self.logger.info(
                f"Processing report for email dispatch: {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Validate report is ready for email
            if not report.is_ready_for_email():
                self.logger.warning(
                    f"Report {report.technical_id} is not ready for email dispatch"
                )
                report.mark_email_failed("Report data incomplete or email already sent")
                return report

            # Format email content
            email_content = self._format_email_content(report)

            # Simulate email dispatch (in real implementation, integrate with email service)
            success = await self._dispatch_email(report, email_content)

            if success:
                report.mark_email_sent()
                self.logger.info(
                    f"Report {report.technical_id} successfully emailed to {report.recipient_email}"
                )
            else:
                report.mark_email_failed("Email service unavailable")
                self.logger.error(f"Failed to email report {report.technical_id}")

            return report

        except Exception as e:
            self.logger.error(
                f"Error processing report for email {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Mark email as failed
            if hasattr(entity, "mark_email_failed"):
                entity.mark_email_failed(str(e))
            raise

    def _format_email_content(self, report: Report) -> Dict[str, Any]:
        """
        Format email content including subject, body, and attachments.

        Args:
            report: The Report entity

        Returns:
            Formatted email content
        """
        # Email subject
        period_start = (
            report.report_period_start[:10] if report.report_period_start else "Unknown"
        )
        subject = f"Weekly Pet Store Performance Report - {period_start}"

        # Email body with executive summary
        body_parts = [
            "Dear Sales Team,",
            "",
            f"Please find attached the weekly performance report for the period {report.report_period_start[:10]} to {report.report_period_end[:10]}.",
            "",
            "EXECUTIVE SUMMARY:",
            "=" * 50,
            report.executive_summary or "Report summary not available",
            "",
            "KEY METRICS:",
            f"• Total Products Analyzed: {report.total_products_analyzed or 0}",
            f"• Total Revenue: ${report.total_revenue or 0:.2f}",
            f"• High Performers: {len(report.top_performing_products or [])}",
            f"• Underperformers: {len(report.underperforming_products or [])}",
            f"• Low Stock Items: {len(report.low_stock_items or [])}",
            "",
        ]

        # Add top performing products
        if report.top_performing_products:
            body_parts.extend(["TOP PERFORMING PRODUCTS:", "-" * 30])
            for i, product in enumerate(report.top_performing_products[:5], 1):
                body_parts.append(
                    f"{i}. {product.get('name', 'Unknown')} - "
                    f"Sales: {product.get('sales_volume', 0)}, "
                    f"Revenue: ${product.get('revenue', 0):.2f}"
                )
            body_parts.append("")

        # Add low stock alerts
        if report.low_stock_items:
            body_parts.extend(["RESTOCKING REQUIRED:", "-" * 25])
            for product in report.low_stock_items[:5]:
                body_parts.append(
                    f"• {product.get('name', 'Unknown')} - "
                    f"Stock: {product.get('inventory_level', 0)} units"
                )
            body_parts.append("")

        # Add footer
        body_parts.extend(
            [
                "For detailed analysis and complete data, please refer to the attached report.",
                "",
                "This report was generated automatically by the Pet Store Performance Analysis System.",
                f"Generated on: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
                "",
                "Best regards,",
                "Pet Store Performance Analysis System",
            ]
        )

        email_body = "\n".join(body_parts)

        return {
            "subject": subject,
            "body": email_body,
            "recipient": report.recipient_email,
            "attachments": self._prepare_attachments(report),
        }

    def _prepare_attachments(self, report: Report) -> List[Dict[str, Any]]:
        """
        Prepare email attachments including detailed report data.

        Args:
            report: The Report entity

        Returns:
            List of attachment data
        """
        # In a real implementation, this would generate PDF or Excel attachments
        # For now, we'll prepare the data structure for attachments

        attachments = []

        # Main report attachment (would be PDF in real implementation)
        if report.report_data:
            attachments.append(
                {
                    "filename": f"performance_report_{report.report_period_start[:10]}.json",
                    "content_type": "application/json",
                    "data": report.report_data,
                    "description": "Detailed performance report data",
                }
            )

        # Top performers CSV (would be actual CSV in real implementation)
        if report.top_performing_products:
            attachments.append(
                {
                    "filename": f"top_performers_{report.report_period_start[:10]}.csv",
                    "content_type": "text/csv",
                    "data": str(report.top_performing_products),
                    "description": "Top performing products data",
                }
            )

        # Low stock items CSV
        if report.low_stock_items:
            attachments.append(
                {
                    "filename": f"low_stock_items_{report.report_period_start[:10]}.csv",
                    "content_type": "text/csv",
                    "data": str(report.low_stock_items),
                    "description": "Products requiring restocking",
                }
            )

        return attachments

    async def _dispatch_email(
        self, report: Report, email_content: Dict[str, Any]
    ) -> bool:
        """
        Dispatch email to recipient (simulated implementation).

        Args:
            report: The Report entity
            email_content: Formatted email content

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # Simulate email dispatch
            # In a real implementation, this would integrate with:
            # - SMTP server
            # - Email service provider (SendGrid, AWS SES, etc.)
            # - Corporate email system

            self.logger.info(
                "Simulating email dispatch to %s", email_content['recipient']
            )
            self.logger.info(f"Subject: {email_content['subject']}")
            self.logger.info(f"Attachments: {len(email_content['attachments'])}")

            # Simulate processing time
            import asyncio

            await asyncio.sleep(0.1)

            # Simulate success (in real implementation, check actual email service response)
            return True

        except Exception as e:
            self.logger.error(f"Email dispatch failed: {str(e)}")
            return False
