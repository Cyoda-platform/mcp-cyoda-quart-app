"""
EmailNotificationPreparationProcessor for Product Performance Analysis System

Handles preparation of email notifications for weekly performance reports
as specified in functional requirements.
"""

import logging
import os
from typing import Any

from application.entity.email_notification.version_1.email_notification import (
    EmailNotification,
)
from application.entity.performance_report.version_1.performance_report import (
    PerformanceReport,
)
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor
from services.services import get_entity_service


class EmailNotificationPreparationProcessor(CyodaProcessor):
    """
    Processor for preparing email notifications.

    Prepares email content, attaches performance reports, and sets up
    email notifications for delivery to the sales team.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailNotificationPreparationProcessor",
            description="Prepares email notifications with performance report attachments",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Prepare the email notification with report attachment.

        Args:
            entity: The EmailNotification entity to prepare
            **kwargs: Additional processing parameters

        Returns:
            The prepared entity with email content and attachments
        """
        try:
            self.logger.info(
                f"Starting email preparation for EmailNotification {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailNotification for type-safe operations
            email_notification = cast_entity(entity, EmailNotification)

            # Find the latest finalized performance report
            latest_report = await self._find_latest_performance_report()

            if latest_report:
                # Prepare email content based on the report
                await self._prepare_email_content(email_notification, latest_report)

                # Attach the report file
                await self._attach_report_file(email_notification, latest_report)

                self.logger.info(
                    f"Prepared email notification with report attachment: {latest_report.report_title}"
                )
            else:
                # Prepare a notification about missing report
                await self._prepare_fallback_email(email_notification)

                self.logger.warning(
                    "No finalized performance report found, prepared fallback email"
                )

            return email_notification

        except Exception as e:
            self.logger.error(
                f"Error preparing email for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _find_latest_performance_report(self) -> PerformanceReport:
        """
        Find the latest finalized performance report.

        Returns:
            The latest PerformanceReport entity or None if not found
        """
        try:
            entity_service = get_entity_service()

            # Search for finalized PerformanceReport entities
            search_response = await entity_service.search(
                entity_class=PerformanceReport.ENTITY_NAME,
                entity_version=str(PerformanceReport.ENTITY_VERSION),
                query={},
                page_size=100,
            )

            latest_report = None
            latest_timestamp = None

            if hasattr(search_response, "entities") and search_response.entities:
                for entity_data in search_response.entities:
                    try:
                        report = PerformanceReport(**entity_data.entity)

                        # Check if report is finalized and has a generation timestamp
                        if (
                            report.report_status == "finalized"
                            and report.generation_timestamp
                            and (
                                latest_timestamp is None
                                or report.generation_timestamp > latest_timestamp
                            )
                        ):
                            latest_report = report
                            latest_timestamp = report.generation_timestamp

                    except Exception as e:
                        self.logger.warning(
                            f"Failed to parse performance report: {str(e)}"
                        )
                        continue

            if latest_report:
                self.logger.info(
                    f"Found latest performance report: {latest_report.report_title}"
                )
            else:
                self.logger.warning("No finalized performance reports found")

            return latest_report

        except Exception as e:
            self.logger.error(f"Error finding latest performance report: {str(e)}")
            return None

    async def _prepare_email_content(
        self, email_notification: EmailNotification, report: PerformanceReport
    ) -> None:
        """
        Prepare email content based on the performance report.

        Args:
            email_notification: The EmailNotification entity to update
            report: The PerformanceReport to base content on
        """
        # Generate email subject
        email_notification.subject = (
            f"Weekly Product Performance Report - {report.report_period_end[:10]}"
        )

        # Set recipient
        email_notification.recipient_email = "victoria.sagdieva@cyoda.com"

        # Generate email body with report summary
        summary_stats = f"""
        • Total Products Analyzed: {report.total_products_analyzed:,}
        • Total Revenue: ${report.total_revenue:,.2f}
        • Total Sales Volume: {report.total_sales_volume:,} units
        • High-Performing Products: {len(report.highest_selling_products)}
        • Items Requiring Restock: {len(report.items_requiring_restock)}
        • Slow-Moving Items: {len(report.slow_moving_inventory)}
        """

        # Get top 3 recommendations
        top_recommendations = report.recommendations[:3]
        recommendations_text = ""
        if top_recommendations:
            recommendations_text = "\n".join(
                [f"• {rec}" for rec in top_recommendations]
            )
        else:
            recommendations_text = "• Continue monitoring product performance trends"

        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2e7d32; border-bottom: 2px solid #4CAF50; padding-bottom: 10px;">
                    Weekly Product Performance Report
                </h2>
                
                <p>Dear Sales Team,</p>
                
                <p>Please find attached the weekly product performance analysis report for the period 
                <strong>{report.report_period_start[:10]} to {report.report_period_end[:10]}</strong>.</p>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #2e7d32; margin-top: 0;">Key Highlights:</h3>
                    <div style="font-family: monospace; white-space: pre-line;">{summary_stats}</div>
                </div>
                
                <h3 style="color: #2e7d32;">Top Recommendations:</h3>
                <div style="background-color: #e8f5e8; padding: 15px; border-left: 4px solid #4CAF50; margin: 15px 0;">
                    <div style="white-space: pre-line;">{recommendations_text}</div>
                </div>
                
                <p>The detailed report is attached as an HTML file for your review. It includes:</p>
                <ul>
                    <li>Comprehensive sales trend analysis</li>
                    <li>Inventory status and restocking recommendations</li>
                    <li>Category performance breakdown</li>
                    <li>Business insights and actionable recommendations</li>
                </ul>
                
                <p>Please review the attached report and let us know if you have any questions or need additional analysis.</p>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                    <p style="color: #666; font-size: 0.9em;">
                        Best regards,<br>
                        <strong>Product Performance Analysis System</strong><br>
                        Automated Weekly Reporting
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        email_notification.email_body = email_body
        email_notification.email_format = "html"

        # Set report reference
        email_notification.report_id = report.technical_id or report.entity_id

        self.logger.info(f"Prepared email content for report: {report.report_title}")

    async def _attach_report_file(
        self, email_notification: EmailNotification, report: PerformanceReport
    ) -> None:
        """
        Attach the performance report file to the email.

        Args:
            email_notification: The EmailNotification entity to update
            report: The PerformanceReport with file information
        """
        if report.report_file_path and os.path.exists(report.report_file_path):
            # Get file information
            file_size = os.path.getsize(report.report_file_path)
            file_name = os.path.basename(report.report_file_path)

            # Attach the file to the email notification
            email_notification.attach_report(
                report_id=report.technical_id or report.entity_id or "unknown",
                file_path=report.report_file_path,
                file_name=file_name,
                file_size=file_size,
            )

            self.logger.info(f"Attached report file: {file_name} ({file_size} bytes)")
        else:
            self.logger.warning(f"Report file not found: {report.report_file_path}")

    async def _prepare_fallback_email(
        self, email_notification: EmailNotification
    ) -> None:
        """
        Prepare a fallback email when no performance report is available.

        Args:
            email_notification: The EmailNotification entity to update
        """
        email_notification.subject = (
            "Weekly Product Performance Report - System Notification"
        )
        email_notification.recipient_email = "victoria.sagdieva@cyoda.com"

        email_body = """
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #d32f2f; border-bottom: 2px solid #f44336; padding-bottom: 10px;">
                    Weekly Product Performance Report - System Notification
                </h2>
                
                <p>Dear Sales Team,</p>
                
                <div style="background-color: #ffebee; padding: 15px; border-left: 4px solid #f44336; margin: 20px 0;">
                    <p><strong>Notice:</strong> The weekly product performance report could not be generated at this time.</p>
                </div>
                
                <p>This may be due to:</p>
                <ul>
                    <li>Insufficient product data for analysis</li>
                    <li>System maintenance or updates</li>
                    <li>Data extraction issues from the Pet Store API</li>
                </ul>
                
                <p>Our technical team has been notified and is working to resolve the issue. 
                You should receive the report once the system is fully operational.</p>
                
                <p>If you need immediate access to product performance data, please contact the technical support team.</p>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                    <p style="color: #666; font-size: 0.9em;">
                        Best regards,<br>
                        <strong>Product Performance Analysis System</strong><br>
                        Automated Weekly Reporting
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        email_notification.email_body = email_body
        email_notification.email_format = "html"

        self.logger.info("Prepared fallback email notification")
