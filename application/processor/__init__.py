"""Application processors module."""

from .mail_send_gloomy_mail_processor import MailSendGloomyMailProcessor
from .mail_send_happy_mail_processor import MailSendHappyMailProcessor

__all__ = ["MailSendHappyMailProcessor", "MailSendGloomyMailProcessor"]
