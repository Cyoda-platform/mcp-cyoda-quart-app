"""
ReportEmailProcessor for Pet Store Performance Analysis System

Handles creating email notifications for generated reports to be sent
to the sales team as specified in functional requirements.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from application.entity.email_notification import EmailNotification
from application.entity.report import Report
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class ReportEmailProcessor(CyodaProcessor):
    """
    Processor for Report entity that creates email notifications
    for sending reports to the sales team.
    """

    def __init__(self) -> None:
        super().__init__(
            name="ReportEmailProcessor",
            description="Creates email notifications for generated reports",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Create email notification for the generated report.

        Args:
            entity: The Report entity to process (must be in 'generated' state)
            **kwargs: Additional processing parameters

        Returns:
            The report entity marked as emailed
        """
        try:
            self.logger.info(
                f"Creating email notification for Report {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Create email notification entity
            email_notification = await self._create_email_notification(report)

            # Mark report as emailed
            recipients = ["victoria.sagdieva@cyoda.com"]  # As specified in requirements
            report.set_emailed(recipients)

            self.logger.info(
                f"Email notification created for Report {report.technical_id}"
            )

            return report

        except Exception as e:
            self.logger.error(
                f"Error creating email notification for report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _create_email_notification(self, report: Report) -> EmailNotification:
        """
        Create an EmailNotification entity for the report.

        Args:
            report: The Report entity to create email notification for

        Returns:
            Created EmailNotification entity
        """
        entity_service = get_entity_service()

        # Generate email subject
        subject = self._generate_email_subject(report)

        # Generate email content
        content = self._generate_email_content(report)

        # Create EmailNotification entity
        email_notification = EmailNotification(
            recipient_email="victoria.sagdieva@cyoda.com",
            subject=subject,
            content=content,
            email_type=(
                "WEEKLY_REPORT"
                if report.report_type == "WEEKLY_SUMMARY"
                else "REPORT_NOTIFICATION"
            ),
            priority="NORMAL",
            report_id=report.technical_id or report.entity_id,
            report_title=report.title,
            status="PENDING",
        )

        # Convert to dict for EntityService
        email_data = email_notification.model_dump(by_alias=True)

        # Save the email notification
        response = await entity_service.save(
            entity=email_data,
            entity_class=EmailNotification.ENTITY_NAME,
            entity_version=str(EmailNotification.ENTITY_VERSION),
        )

        created_email_id = response.metadata.id

        self.logger.info(
            f"Created EmailNotification {created_email_id} for report {report.technical_id}"
        )

        return cast_entity(response.data, EmailNotification)

    def _generate_email_subject(self, report: Report) -> str:
        """
        Generate email subject line for the report.

        Args:
            report: The Report entity

        Returns:
            Email subject string
        """
        # Get current date for subject
        current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        if report.report_type == "WEEKLY_SUMMARY":
            return f"Weekly Pet Store Performance Report - {current_date}"
        elif report.report_type == "MONTHLY_ANALYSIS":
            return f"Monthly Pet Store Analysis Report - {current_date}"
        else:
            return f"Pet Store Performance Report: {report.title} - {current_date}"

    def _generate_email_content(self, report: Report) -> str:
        """
        Generate email content for the report.

        Args:
            report: The Report entity

        Returns:
            Email content as HTML string
        """
        # Get summary information
        summary = report.get_report_summary()

        # Generate email body
        email_lines = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<style>",
            "body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }",
            ".header { background-color: #f4f4f4; padding: 20px; border-radius: 5px; }",
            ".summary { background-color: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0; }",
            ".highlight { background-color: #fff3cd; padding: 10px; border-radius: 3px; margin: 10px 0; }",
            ".footer { font-size: 12px; color: #666; margin-top: 30px; }",
            "table { border-collapse: collapse; width: 100%; margin: 15px 0; }",
            "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "th { background-color: #f2f2f2; }",
            "</style>",
            "</head>",
            "<body>",
            "",
            '<div class="header">',
            f"<h2>{report.title}</h2>",
            f"<p><strong>Report Type:</strong> {report.report_type}</p>",
            f"<p><strong>Generated:</strong> {report.generated_at}</p>",
            f"<p><strong>Data Period:</strong> {summary['data_period']['start']} to {summary['data_period']['end']}</p>",
            "</div>",
            "",
            "<h3>Executive Summary</h3>",
            self._generate_email_summary_section(report),
            "",
            "<h3>Key Metrics</h3>",
            self._generate_email_metrics_section(report),
            "",
            "<h3>Product Highlights</h3>",
            self._generate_email_highlights_section(report),
            "",
            "<h3>Action Items</h3>",
            self._generate_email_action_items(report),
            "",
            '<div class="footer">',
            "<p>This report was automatically generated by the Pet Store Performance Analysis System.</p>",
            "<p>For detailed analysis, please refer to the full report attached or contact the system administrator.</p>",
            f"<p>Report ID: {report.technical_id or report.entity_id}</p>",
            "</div>",
            "",
            "</body>",
            "</html>",
        ]

        return "\n".join(email_lines)

    def _generate_email_summary_section(self, report: Report) -> str:
        """Generate summary section for email."""
        if not report.insights:
            return '<div class="summary">No summary data available.</div>'

        insights = report.insights

        summary_lines = [
            '<div class="summary">',
            f"<p><strong>Total Products Analyzed:</strong> {insights.get('total_products_analyzed', 'N/A')}</p>",
            f"<p><strong>Total Revenue:</strong> ${insights.get('total_revenue', 0):,.2f}</p>",
            f"<p><strong>Total Sales Volume:</strong> {insights.get('total_sales_volume', 0):,} units</p>",
            f"<p><strong>Average Performance Score:</strong> {insights.get('average_performance_score', 0):.1f}/100</p>",
            "</div>",
        ]

        return "\n".join(summary_lines)

    def _generate_email_metrics_section(self, report: Report) -> str:
        """Generate metrics section for email."""
        if not report.insights:
            return "<p>No metrics data available.</p>"

        insights = report.insights

        metrics_lines = [
            "<table>",
            "<tr><th>Metric</th><th>Value</th></tr>",
            f"<tr><td>High Performers (Score ≥ 70)</td><td>{insights.get('high_performers_count', 0)} products</td></tr>",
            f"<tr><td>Low Performers (Score ≤ 30)</td><td>{insights.get('low_performers_count', 0)} products</td></tr>",
            f"<tr><td>Out of Stock Products</td><td>{insights.get('out_of_stock_count', 0)} products</td></tr>",
            f"<tr><td>Categories Analyzed</td><td>{insights.get('categories_analyzed', 0)} categories</td></tr>",
            f"<tr><td>Top Performing Category</td><td>{insights.get('top_category', 'N/A')}</td></tr>",
            "</table>",
        ]

        return "\n".join(metrics_lines)

    def _generate_email_highlights_section(self, report: Report) -> str:
        """Generate highlights section for email."""
        if not report.product_highlights:
            return "<p>No product highlights available.</p>"

        highlights_lines = [
            "<table>",
            "<tr><th>Type</th><th>Product</th><th>Category</th><th>Performance Score</th><th>Revenue</th></tr>",
        ]

        for highlight in report.product_highlights[:5]:  # Limit to top 5
            highlights_lines.append(
                f"<tr>"
                f"<td>{highlight.get('type', 'N/A').replace('_', ' ').title()}</td>"
                f"<td>{highlight.get('product_name', 'N/A')}</td>"
                f"<td>{highlight.get('category', 'N/A')}</td>"
                f"<td>{highlight.get('performance_score', 0):.1f}</td>"
                f"<td>${highlight.get('revenue', 0):.2f}</td>"
                f"</tr>"
            )

        highlights_lines.append("</table>")
        return "\n".join(highlights_lines)

    def _generate_email_action_items(self, report: Report) -> str:
        """Generate action items section for email."""
        if not report.insights:
            return "<p>No action items identified.</p>"

        insights = report.insights
        action_items = []

        # Out of stock items
        out_of_stock = insights.get("out_of_stock_count", 0)
        if out_of_stock > 0:
            action_items.append(
                f"🚨 <strong>Immediate Action:</strong> {out_of_stock} products are out of stock and need restocking"
            )

        # Low performers
        low_performers = insights.get("low_performers_count", 0)
        if low_performers > 0:
            action_items.append(
                f"📊 <strong>Review Required:</strong> {low_performers} products need strategy review"
            )

        # High performers
        high_performers = insights.get("high_performers_count", 0)
        if high_performers > 0:
            action_items.append(
                f"✅ <strong>Opportunity:</strong> Consider expanding inventory for {high_performers} high-performing products"
            )

        if not action_items:
            action_items.append(
                "✅ No immediate action items identified - continue monitoring performance"
            )

        action_lines = ['<div class="highlight">']
        for item in action_items:
            action_lines.append(f"<p>{item}</p>")
        action_lines.append("</div>")

        return "\n".join(action_lines)
