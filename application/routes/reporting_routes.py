"""
Reporting routes for the cat fact subscription system.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import BaseModel
from quart import Blueprint, jsonify, request
from quart_schema import validate_querystring

from common.config.config import ENTITY_VERSION
from service.services import get_auth_service, get_entity_service

logger = logging.getLogger(__name__)

reporting_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


class EmailDeliveryReportQuery(BaseModel):
    """Query parameters for email delivery statistics."""

    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None


def get_services():
    """Get services from the registry lazily."""
    return get_entity_service(), get_auth_service()


@reporting_bp.route("/subscribers", methods=["GET"])
async def get_subscriber_statistics():
    """Get subscriber statistics."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Get all subscribers
        subscribers = await entity_service.find_all("subscriber", ENTITY_VERSION)

        # Calculate statistics
        total_subscribers = len(subscribers)
        active_subscribers = sum(
            1 for s in subscribers if s.data.get("isActive") and s.state == "active"
        )
        pending_subscribers = sum(1 for s in subscribers if s.state == "pending")
        unsubscribed_subscribers = sum(
            1 for s in subscribers if s.state == "unsubscribed"
        )
        bounced_subscribers = sum(1 for s in subscribers if s.state == "bounced")

        # Calculate recent subscriptions
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        subscriptions_this_week = 0
        subscriptions_this_month = 0

        for subscriber in subscribers:
            subscription_date_str = subscriber.data.get("subscriptionDate")
            if subscription_date_str:
                try:
                    subscription_date = datetime.fromisoformat(
                        subscription_date_str.replace("Z", "+00:00")
                    )
                    if subscription_date >= week_ago:
                        subscriptions_this_week += 1
                    if subscription_date >= month_ago:
                        subscriptions_this_month += 1
                except (ValueError, AttributeError):
                    continue

        result = {
            "totalSubscribers": total_subscribers,
            "activeSubscribers": active_subscribers,
            "pendingSubscribers": pending_subscribers,
            "unsubscribedSubscribers": unsubscribed_subscribers,
            "bouncedSubscribers": bounced_subscribers,
            "subscriptionsThisWeek": subscriptions_this_week,
            "subscriptionsThisMonth": subscriptions_this_month,
        }

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Failed to get subscriber statistics: {e}")
        return jsonify({"error": "Failed to get subscriber statistics"}), 500


@reporting_bp.route("/email-deliveries", methods=["GET"])
@validate_querystring(EmailDeliveryReportQuery)
async def get_email_delivery_statistics():
    """Get email delivery statistics."""
    entity_service, cyoda_auth_service = get_services()

    args = EmailDeliveryReportQuery(**request.args)

    try:
        # Get all email deliveries
        deliveries = await entity_service.find_all("emaildelivery", ENTITY_VERSION)

        # Filter by date range if provided
        if args.startDate or args.endDate:
            filtered_deliveries = []
            for delivery in deliveries:
                sent_date_str = delivery.data.get("sentDate")
                if sent_date_str:
                    try:
                        sent_date = datetime.fromisoformat(
                            sent_date_str.replace("Z", "+00:00")
                        )
                        if args.startDate and sent_date < args.startDate:
                            continue
                        if args.endDate and sent_date > args.endDate:
                            continue
                        filtered_deliveries.append(delivery)
                    except (ValueError, AttributeError):
                        continue
            deliveries = filtered_deliveries

        # Calculate statistics
        total_emails_sent = len(deliveries)
        successful_deliveries = sum(
            1 for d in deliveries if d.state in ["delivered", "opened"]
        )
        failed_deliveries = sum(
            1 for d in deliveries if d.state in ["failed", "bounced"]
        )
        emails_opened = sum(1 for d in deliveries if d.data.get("opened"))

        # Calculate rates
        open_rate = (
            (emails_opened / total_emails_sent * 100) if total_emails_sent > 0 else 0
        )
        bounce_rate = (
            (failed_deliveries / total_emails_sent * 100)
            if total_emails_sent > 0
            else 0
        )
        delivery_rate = (
            (successful_deliveries / total_emails_sent * 100)
            if total_emails_sent > 0
            else 0
        )

        result = {
            "totalEmailsSent": total_emails_sent,
            "successfulDeliveries": successful_deliveries,
            "failedDeliveries": failed_deliveries,
            "emailsOpened": emails_opened,
            "openRate": round(open_rate, 1),
            "bounceRate": round(bounce_rate, 1),
            "deliveryRate": round(delivery_rate, 1),
        }

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Failed to get email delivery statistics: {e}")
        return jsonify({"error": "Failed to get email delivery statistics"}), 500


@reporting_bp.route("/cat-facts", methods=["GET"])
async def get_catfact_statistics():
    """Get cat fact distribution statistics."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Get all cat facts
        catfacts = await entity_service.find_all("catfact", ENTITY_VERSION)

        # Calculate statistics
        total_facts_retrieved = len(catfacts)
        facts_distributed = sum(
            1 for cf in catfacts if cf.state in ["sent", "archived"]
        )

        # Calculate average fact length
        fact_lengths = [
            cf.data.get("length", 0) for cf in catfacts if cf.data.get("length")
        ]
        average_fact_length = (
            sum(fact_lengths) // len(fact_lengths) if fact_lengths else 0
        )

        # Find last distribution date and next scheduled
        last_distribution_date = None
        next_scheduled_distribution = None

        for catfact in catfacts:
            # Check for last distribution
            distributed_at = catfact.data.get("metadata", {}).get("distributed_at")
            if distributed_at:
                try:
                    dist_date = datetime.fromisoformat(
                        distributed_at.replace("Z", "+00:00")
                    )
                    if not last_distribution_date or dist_date > last_distribution_date:
                        last_distribution_date = dist_date
                except (ValueError, AttributeError):
                    continue

            # Check for next scheduled
            scheduled_date_str = catfact.data.get("scheduledSendDate")
            if scheduled_date_str and catfact.state == "scheduled":
                try:
                    scheduled_date = datetime.fromisoformat(
                        scheduled_date_str.replace("Z", "+00:00")
                    )
                    if (
                        not next_scheduled_distribution
                        or scheduled_date < next_scheduled_distribution
                    ):
                        next_scheduled_distribution = scheduled_date
                except (ValueError, AttributeError):
                    continue

        result = {
            "totalFactsRetrieved": total_facts_retrieved,
            "factsDistributed": facts_distributed,
            "averageFactLength": average_fact_length,
            "lastDistributionDate": (
                last_distribution_date.isoformat() if last_distribution_date else None
            ),
            "nextScheduledDistribution": (
                next_scheduled_distribution.isoformat()
                if next_scheduled_distribution
                else None
            ),
        }

        return jsonify(result)

    except Exception as e:
        logger.exception(f"Failed to get cat fact statistics: {e}")
        return jsonify({"error": "Failed to get cat fact statistics"}), 500
