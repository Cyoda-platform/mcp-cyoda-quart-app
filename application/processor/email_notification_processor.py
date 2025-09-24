"""
EmailNotificationProcessor for Product Performance Analysis and Reporting System

Handles email delivery of generated performance reports to the sales team.
Sends weekly reports to victoria.sagdieva@cyoda.com with comprehensive analysis.
"""

import logging
from typing import Any, Dict, List, Optional

from application.entity.report.version_1.report import Report
from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor


class EmailNotificationProcessor(CyodaProcessor):
    """
    Processor for Report entity that handles email notification delivery.

    Sends generated performance reports via email to the sales team including:
    - Executive summary in email body
    - Detailed report as PDF attachment
    - Performance insights and recommendations
    - Error handling and retry logic
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailNotificationProcessor",
            description="Sends performance reports via email to the sales team",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Send email notification with the generated report.

        Args:
            entity: The Report entity to send via email
            **kwargs: Additional processing parameters

        Returns:
            The updated Report entity with email delivery status
        """
        try:
            self.logger.info(
                f"Sending email notification for report {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report = cast_entity(entity, Report)

            # Prepare email content
            email_subject = self._generate_email_subject(report)
            email_body = self._generate_email_body(report)

            # Send email (mock implementation)
            success = await self._send_email(
                recipients=report.email_recipients,
                subject=email_subject,
                body=email_body,
                attachment_path=report.file_path,
            )

            if success:
                report.mark_email_sent()
                self.logger.info(
                    f"Email sent successfully for report {report.technical_id} "
                    f"to {len(report.email_recipients)} recipients"
                )
            else:
                report.mark_email_failed()
                self.logger.error(
                    f"Failed to send email for report {report.technical_id}"
                )

            return report

        except Exception as e:
            self.logger.error(
                f"Error sending email for report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )

            # Cast again for error handling
            report = cast_entity(entity, Report)
            report.mark_email_failed()

            raise

    def _generate_email_subject(self, report: Report) -> str:
        """
        Generate email subject line for the report.

        Args:
            report: The Report entity

        Returns:
            Email subject string
        """
        return f"Weekly Product Performance Report - {report.period_start} to {report.period_end}"

    def _generate_email_body(self, report: Report) -> str:
        """
        Generate email body content with executive summary and key insights.

        Args:
            report: The Report entity

        Returns:
            Email body content as HTML string
        """
        # Extract key metrics for email
        total_products = report.total_products_analyzed
        total_revenue = report.total_revenue or 0
        avg_performance = report.average_performance_score or 0
        growth_rate = report.revenue_growth_percentage or 0

        # Count insights
        top_performers_count = len(report.top_performing_products or [])
        underperformers_count = len(report.underperforming_products or [])
        low_stock_count = len(report.low_stock_products or [])

        email_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #f4f4f4; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .metrics {{ background-color: #e8f4f8; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                .alert {{ background-color: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; }}
                .success {{ background-color: #d4edda; padding: 10px; margin: 10px 0; border-left: 4px solid #28a745; }}
                .footer {{ background-color: #f4f4f4; padding: 15px; text-align: center; font-size: 12px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Weekly Product Performance Report</h1>
                <p>Period: {report.period_start} to {report.period_end}</p>
            </div>
            
            <div class="content">
                <h2>Executive Summary</h2>
                <div class="metrics">
                    <h3>Key Metrics</h3>
                    <ul>
                        <li><strong>Total Products Analyzed:</strong> {total_products}</li>
                        <li><strong>Total Revenue:</strong> ${total_revenue:,.2f}</li>
                        <li><strong>Average Performance Score:</strong> {avg_performance:.1f}/100</li>
                        <li><strong>Revenue Growth:</strong> {growth_rate:+.1f}%</li>
                    </ul>
                </div>
                
                <h2>Performance Highlights</h2>
                
                <div class="success">
                    <h3>✅ Top Performers ({top_performers_count} products)</h3>
                    <p>These products are driving strong sales and revenue growth.</p>
                </div>
                
                {self._generate_top_performers_section(report.top_performing_products or [])}
                
                <div class="alert">
                    <h3>⚠️ Attention Required ({underperformers_count} products)</h3>
                    <p>These products need immediate attention to improve performance.</p>
                </div>
                
                {self._generate_underperformers_section(report.underperforming_products or [])}
                
                <div class="alert">
                    <h3>📦 Inventory Alerts ({low_stock_count} products)</h3>
                    <p>These products require restocking to avoid stockouts.</p>
                </div>
                
                {self._generate_low_stock_section(report.low_stock_products or [])}
                
                <h2>Category Performance</h2>
                {self._generate_category_performance_section(report.category_performance or {{}})}
                
                <h2>Recommendations</h2>
                <ul>
                    <li>Focus marketing efforts on top-performing categories</li>
                    <li>Review pricing strategy for underperforming products</li>
                    <li>Prioritize restocking for high-urgency items</li>
                    <li>Consider promotional activities for slow-moving inventory</li>
                </ul>
                
                <p><strong>Detailed Report:</strong> Please find the comprehensive analysis attached as a PDF.</p>
            </div>
            
            <div class="footer">
                <p>This report was automatically generated by the Product Performance Analysis System.</p>
                <p>For questions or support, please contact the system administrator.</p>
            </div>
        </body>
        </html>
        """

        return email_body.strip()

    def _generate_top_performers_section(self, top_performers: List[Dict[str, Any]]) -> str:
        """Generate HTML section for top performing products"""
        if not top_performers:
            return "<p>No top performers identified in this period.</p>"

        html = "<table><tr><th>Product</th><th>Category</th><th>Performance Score</th><th>Revenue</th></tr>"
        for product in top_performers[:3]:  # Show top 3 in email
            html += f"""
            <tr>
                <td>{product['name']}</td>
                <td>{product['category']}</td>
                <td>{product['performance_score']:.1f}/100</td>
                <td>${product['revenue'] or 0:,.2f}</td>
            </tr>
            """
        html += "</table>"
        return html

    def _generate_underperformers_section(self, underperformers: List[Dict[str, Any]]) -> str:
        """Generate HTML section for underperforming products"""
        if not underperformers:
            return "<p>No underperforming products identified.</p>"

        html = "<table><tr><th>Product</th><th>Category</th><th>Performance Score</th><th>Issues</th></tr>"
        for product in underperformers[:3]:  # Show top 3 issues in email
            issues = ", ".join(product.get("issues", []))
            html += f"""
            <tr>
                <td>{product['name']}</td>
                <td>{product['category']}</td>
                <td>{product['performance_score']:.1f}/100</td>
                <td>{issues}</td>
            </tr>
            """
        html += "</table>"
        return html

    def _generate_low_stock_section(self, low_stock: List[Dict[str, Any]]) -> str:
        """Generate HTML section for low stock products"""
        if not low_stock:
            return "<p>All products have adequate stock levels.</p>"

        html = "<table><tr><th>Product</th><th>Category</th><th>Current Stock</th><th>Urgency</th></tr>"
        for product in low_stock[:5]:  # Show top 5 urgent items
            urgency_color = "red" if product["urgency"] == "high" else "orange"
            html += f"""
            <tr>
                <td>{product['name']}</td>
                <td>{product['category']}</td>
                <td>{product['current_stock']}</td>
                <td style="color: {urgency_color}; font-weight: bold;">{product['urgency'].upper()}</td>
            </tr>
            """
        html += "</table>"
        return html

    def _generate_category_performance_section(self, category_performance: Dict[str, Any]) -> str:
        """Generate HTML section for category performance"""
        if not category_performance:
            return "<p>No category performance data available.</p>"

        html = "<table><tr><th>Category</th><th>Products</th><th>Total Revenue</th><th>Avg Performance</th></tr>"
        for category, stats in category_performance.items():
            html += f"""
            <tr>
                <td>{category}</td>
                <td>{stats['total_products']}</td>
                <td>${stats['total_revenue']:,.2f}</td>
                <td>{stats['avg_performance_score']:.1f}/100</td>
            </tr>
            """
        html += "</table>"
        return html

    async def _send_email(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        attachment_path: Optional[str] = None,
    ) -> bool:
        """
        Send email with report content (mock implementation).

        In a real system, this would integrate with an email service like:
        - SMTP server
        - SendGrid
        - AWS SES
        - Azure Communication Services

        Args:
            recipients: List of email addresses
            subject: Email subject line
            body: Email body content (HTML)
            attachment_path: Path to report file attachment

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Mock email sending - in real implementation would use actual email service
            self.logger.info(f"Mock email sent to {recipients}")
            self.logger.info(f"Subject: {subject}")
            self.logger.info(f"Attachment: {attachment_path}")

            # Simulate email sending delay
            import asyncio

            await asyncio.sleep(0.1)

            # Mock success (in real system, would handle actual email service response)
            return True

        except Exception as e:
            self.logger.error(f"Failed to send email: {str(e)}")
            return False
