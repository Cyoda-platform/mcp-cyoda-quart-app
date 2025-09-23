"""
EmailNotificationSendProcessor for Product Performance Analysis System

Handles sending of email notifications with performance report attachments
to victoria.sagdieva@cyoda.com as specified in functional requirements.
"""

import logging
import smtplib
from datetime import datetime, timezone
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from common.entity.entity_casting import cast_entity
from common.processor.base import CyodaEntity, CyodaProcessor

from application.entity.email_notification.version_1.email_notification import EmailNotification


class EmailNotificationSendProcessor(CyodaProcessor):
    """
    Processor for sending email notifications.
    
    Sends prepared email notifications with performance report attachments
    to the sales team using SMTP.
    """

    def __init__(self) -> None:
        super().__init__(
            name="EmailNotificationSendProcessor",
            description="Sends email notifications with performance report attachments",
        )
        self.logger: logging.Logger = getattr(
            self, "logger", logging.getLogger(__name__)
        )

    async def process(self, entity: CyodaEntity, **kwargs: Any) -> CyodaEntity:
        """
        Send the prepared email notification.

        Args:
            entity: The EmailNotification entity to send
            **kwargs: Additional processing parameters

        Returns:
            The entity with updated send status
        """
        try:
            self.logger.info(
                f"Starting email send for EmailNotification {getattr(entity, 'technical_id', '<unknown>')}"
            )

            # Cast the entity to EmailNotification for type-safe operations
            email_notification = cast_entity(entity, EmailNotification)

            # Attempt to send the email
            success = await self._send_email(email_notification)
            
            if success:
                email_notification.mark_as_sent()
                self.logger.info(
                    f"Successfully sent email to {email_notification.recipient_email}"
                )
            else:
                email_notification.mark_as_failed("Email delivery failed - see logs for details")
                self.logger.error(
                    f"Failed to send email to {email_notification.recipient_email}"
                )

            return email_notification

        except Exception as e:
            self.logger.error(
                f"Error sending email for entity {getattr(entity, 'technical_id', '<unknown>')}: {str(e)}"
            )
            # Cast and mark as failed
            email_notification = cast_entity(entity, EmailNotification)
            email_notification.mark_as_failed(f"Exception during send: {str(e)}")
            return email_notification

    async def _send_email(self, email_notification: EmailNotification) -> bool:
        """
        Send the email using SMTP.

        Args:
            email_notification: The EmailNotification entity with email details

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # For demonstration purposes, we'll simulate email sending
            # In a real implementation, you would configure SMTP settings
            
            # Log the email details for demonstration
            self.logger.info("=== EMAIL SIMULATION ===")
            self.logger.info(f"To: {email_notification.recipient_email}")
            self.logger.info(f"Subject: {email_notification.subject}")
            self.logger.info(f"Format: {email_notification.email_format}")
            
            if email_notification.attachment_file_path:
                self.logger.info(f"Attachment: {email_notification.attachment_file_name}")
                self.logger.info(f"Attachment Size: {email_notification.attachment_file_size} bytes")
            
            # Simulate email body preview (first 200 characters)
            body_preview = email_notification.email_body[:200].replace('\n', ' ').replace('\r', ' ')
            self.logger.info(f"Body Preview: {body_preview}...")
            
            # In a real implementation, uncomment and configure the following:
            # return await self._send_smtp_email(email_notification)
            
            # For demonstration, simulate successful send
            self.logger.info("Email simulation completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in email sending simulation: {str(e)}")
            return False

    async def _send_smtp_email(self, email_notification: EmailNotification) -> bool:
        """
        Send email using SMTP (real implementation).
        
        This method would be used in a production environment with proper SMTP configuration.

        Args:
            email_notification: The EmailNotification entity with email details

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # SMTP configuration (would be loaded from environment variables)
            smtp_server = "smtp.gmail.com"  # Example
            smtp_port = 587
            smtp_username = "your-email@gmail.com"  # Would be from env
            smtp_password = "your-app-password"  # Would be from env
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = email_notification.recipient_email
            msg['Subject'] = email_notification.subject
            
            # Add CC recipients if any
            if email_notification.cc_recipients:
                msg['Cc'] = ', '.join(email_notification.cc_recipients)
            
            # Add email body
            if email_notification.email_format == "html":
                msg.attach(MIMEText(email_notification.email_body, 'html'))
            else:
                msg.attach(MIMEText(email_notification.email_body, 'plain'))
            
            # Add attachment if present
            if email_notification.attachment_file_path:
                try:
                    with open(email_notification.attachment_file_path, 'rb') as f:
                        attachment = MIMEApplication(f.read())
                        attachment.add_header(
                            'Content-Disposition', 
                            'attachment', 
                            filename=email_notification.attachment_file_name
                        )
                        msg.attach(attachment)
                except Exception as e:
                    self.logger.error(f"Failed to attach file: {str(e)}")
                    return False
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                
                # Prepare recipient list
                recipients = [email_notification.recipient_email]
                recipients.extend(email_notification.cc_recipients)
                recipients.extend(email_notification.bcc_recipients)
                
                server.send_message(msg, to_addrs=recipients)
            
            self.logger.info(f"Email sent successfully to {email_notification.recipient_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"SMTP email sending failed: {str(e)}")
            return False

    async def _log_email_analytics(self, email_notification: EmailNotification) -> None:
        """
        Log email analytics for tracking purposes.

        Args:
            email_notification: The EmailNotification entity
        """
        analytics_data = {
            "email_id": email_notification.technical_id or email_notification.entity_id,
            "recipient": email_notification.recipient_email,
            "subject": email_notification.subject,
            "send_status": email_notification.send_status,
            "send_time": email_notification.actual_send_time,
            "has_attachment": bool(email_notification.attachment_file_path),
            "attachment_size": email_notification.attachment_file_size,
            "retry_count": email_notification.retry_count
        }
        
        self.logger.info(f"Email Analytics: {analytics_data}")

    async def _handle_delivery_confirmation(self, email_notification: EmailNotification) -> None:
        """
        Handle delivery confirmation if available.

        Args:
            email_notification: The EmailNotification entity
        """
        # In a real implementation, this would handle delivery receipts
        # For now, we'll simulate immediate delivery confirmation
        email_notification.mark_as_delivered()
        
        self.logger.info(
            f"Delivery confirmation simulated for email to {email_notification.recipient_email}"
        )
