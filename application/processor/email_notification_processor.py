"""
EmailNotificationProcessor for Product Performance Analysis and Reporting System

Handles email delivery of performance reports to the sales team
as specified in functional requirements.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor

from application.entity.report.version_1.report import Report


class EmailNotificationProcessor(CyodaProcessor):
    """
    Processor for sending email notifications with performance reports.
    
    Sends generated reports to the sales team via email with
    formatted content and attachments.
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
        Process the Report entity to send email notification.

        Args:
            entity: The Report entity to email
            **kwargs: Additional processing parameters

        Returns:
            The processed Report entity with email status updated
        """
        try:
            self.logger.info(
                f"Sending email notification for report {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to Report for type-safe operations
            report_entity = cast_entity(entity, Report)
            
            # Validate report is ready for email
            if not report_entity.is_ready_for_email():
                self.logger.warning(f"Report {report_entity.technical_id} is not ready for email")
                return report_entity
            
            # Send email notification
            success = await self._send_email_notification(report_entity)
            
            if success:
                # Mark email as sent
                report_entity.mark_email_sent()
                
                self.logger.info(
                    f"Email notification sent successfully for report {report_entity.title}"
                )
            else:
                self.logger.error(
                    f"Failed to send email notification for report {report_entity.title}"
                )

            return report_entity

        except Exception as e:
            self.logger.error(
                f"Error sending email for report {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            raise

    async def _send_email_notification(self, report: Report) -> bool:
        """
        Send email notification with the report.

        Args:
            report: The Report entity to send

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # For this implementation, we'll simulate email sending
            # In a real implementation, you would configure SMTP settings
            # and use a proper email service
            
            self.logger.info("Simulating email send to sales team...")
            
            # Generate email content
            email_content = self._generate_email_content(report)
            
            # Log email details (simulating send)
            self.logger.info(f"Email Subject: {report.email_subject}")
            self.logger.info(f"Recipients: {', '.join(report.email_recipients or [])}")
            self.logger.info(f"Content Length: {len(email_content)} characters")
            
            # In a real implementation, you would:
            # 1. Configure SMTP settings (Gmail, SendGrid, etc.)
            # 2. Create MIMEMultipart message
            # 3. Add HTML/text content
            # 4. Add any attachments
            # 5. Send via SMTP
            
            # Simulate successful email send
            self._log_email_simulation(report, email_content)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {str(e)}")
            return False

    def _generate_email_content(self, report: Report) -> str:
        """
        Generate HTML email content from the report.

        Args:
            report: The Report entity

        Returns:
            HTML email content
        """
        try:
            # Convert markdown content to HTML-friendly format
            html_content = self._markdown_to_html(report.content or "")
            
            # Create email template
            email_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{report.title}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background-color: #f4f4f4; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .summary {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                    .metrics {{ display: flex; flex-wrap: wrap; gap: 20px; margin: 20px 0; }}
                    .metric {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; flex: 1; min-width: 200px; }}
                    .metric h3 {{ margin: 0 0 10px 0; color: #2c5aa0; }}
                    .footer {{ background-color: #f4f4f4; padding: 20px; text-align: center; font-size: 12px; }}
                    h1, h2, h3 {{ color: #2c5aa0; }}
                    .warning {{ color: #d9534f; font-weight: bold; }}
                    .success {{ color: #5cb85c; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{report.title}</h1>
                    <p>Product Performance Analysis Report</p>
                </div>
                
                <div class="content">
                    <div class="summary">
                        <h2>Executive Summary</h2>
                        <p>{report.summary or 'No summary available.'}</p>
                    </div>
                    
                    <div class="metrics">
                        <div class="metric">
                            <h3>Products Analyzed</h3>
                            <p>{report.total_products_analyzed or 0}</p>
                        </div>
                        <div class="metric">
                            <h3>Total Revenue</h3>
                            <p>${report.total_revenue or 0:,.2f}</p>
                        </div>
                        <div class="metric">
                            <h3>Top Performers</h3>
                            <p>{len(report.top_performing_products or [])}</p>
                        </div>
                        <div class="metric">
                            <h3>Need Restocking</h3>
                            <p class="warning">{len(report.products_needing_restock or [])}</p>
                        </div>
                    </div>
                    
                    <div class="report-content">
                        {html_content}
                    </div>
                </div>
                
                <div class="footer">
                    <p>This report was automatically generated by the Product Performance Analysis System.</p>
                    <p>Report generated on: {report.generated_at}</p>
                </div>
            </body>
            </html>
            """
            
            return email_html
            
        except Exception as e:
            self.logger.error(f"Failed to generate email content: {str(e)}")
            return f"<html><body><h1>Error generating report content</h1><p>{str(e)}</p></body></html>"

    def _markdown_to_html(self, markdown_content: str) -> str:
        """
        Convert basic markdown to HTML.

        Args:
            markdown_content: Markdown content

        Returns:
            HTML content
        """
        if not markdown_content:
            return ""
        
        # Simple markdown to HTML conversion
        html = markdown_content
        
        # Headers
        html = html.replace("### ", "<h3>").replace("\n## ", "</h3>\n<h2>").replace("\n# ", "</h2>\n<h1>")
        html = html.replace("## ", "<h2>").replace("# ", "<h1>")
        
        # Bold text
        html = html.replace("**", "<strong>", 1).replace("**", "</strong>", 1)
        
        # Lists
        lines = html.split('\n')
        in_list = False
        result_lines = []
        
        for line in lines:
            if line.strip().startswith('- '):
                if not in_list:
                    result_lines.append('<ul>')
                    in_list = True
                result_lines.append(f'<li>{line.strip()[2:]}</li>')
            else:
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                result_lines.append(line)
        
        if in_list:
            result_lines.append('</ul>')
        
        # Paragraphs
        html = '\n'.join(result_lines)
        html = html.replace('\n\n', '</p>\n<p>')
        html = f'<p>{html}</p>'
        
        # Clean up empty paragraphs
        html = html.replace('<p></p>', '')
        html = html.replace('<p><h', '<h').replace('</h1></p>', '</h1>')
        html = html.replace('</h2></p>', '</h2>').replace('</h3></p>', '</h3>')
        html = html.replace('<p><ul>', '<ul>').replace('</ul></p>', '</ul>')
        
        return html

    def _log_email_simulation(self, report: Report, email_content: str) -> None:
        """
        Log email simulation details.

        Args:
            report: The Report entity
            email_content: Generated email content
        """
        self.logger.info("=" * 60)
        self.logger.info("EMAIL SIMULATION - REPORT DELIVERY")
        self.logger.info("=" * 60)
        self.logger.info(f"TO: {', '.join(report.email_recipients or [])}")
        self.logger.info(f"SUBJECT: {report.email_subject}")
        self.logger.info(f"REPORT PERIOD: {report.report_period_start} to {report.report_period_end}")
        self.logger.info(f"PRODUCTS ANALYZED: {report.total_products_analyzed}")
        self.logger.info(f"TOTAL REVENUE: ${report.total_revenue or 0:,.2f}")
        self.logger.info(f"INSIGHTS COUNT: {len(report.insights or [])}")
        
        if report.products_needing_restock:
            self.logger.info(f"⚠️  URGENT: {len(report.products_needing_restock)} products need restocking!")
        
        self.logger.info("=" * 60)
        self.logger.info("Email would be sent in production environment")
        self.logger.info("=" * 60)
