"""
Reporting Routes for Cyoda Client Application

Provides reporting and analytics endpoints as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Protocol, cast

from quart import Blueprint, jsonify
from quart.typing import ResponseReturnValue

from services.services import get_entity_service

logger = logging.getLogger(__name__)

reporting_routes_bp = Blueprint("reporting", __name__, url_prefix="/api/reporting")


# ---- Service typing ---------------------------------------------------------


class _ListedEntity(Protocol):
    def get_id(self) -> str: ...
    def get_state(self) -> str: ...

    data: Dict[str, Any]


class EntityServiceProtocol(Protocol):
    async def find_all(
        self, *, entity_class: str, entity_version: str
    ) -> List[_ListedEntity]: ...


# Services will be accessed through the registry
entity_service: Optional[EntityServiceProtocol] = None


def get_services() -> EntityServiceProtocol:
    """Get services from the registry lazily."""
    global entity_service
    if entity_service is None:
        entity_service = cast(EntityServiceProtocol, get_entity_service())
    return entity_service


# ---- Routes -----------------------------------------------------------------


@reporting_routes_bp.route("/dashboard", methods=["GET"])
async def get_dashboard() -> ResponseReturnValue:
    """Get dashboard statistics."""
    try:
        service = get_services()

        # Get all entities for statistics
        subscribers = await service.find_all(
            entity_class="Subscriber", entity_version="1"
        )
        catfacts = await service.find_all(entity_class="CatFact", entity_version="1")
        emaildeliveries = await service.find_all(
            entity_class="EmailDelivery", entity_version="1"
        )
        interactions = await service.find_all(
            entity_class="Interaction", entity_version="1"
        )
        weeklyschedules = await service.find_all(
            entity_class="WeeklySchedule", entity_version="1"
        )

        # Calculate subscriber statistics
        active_subscribers = sum(
            1 for s in subscribers if s.data.get("isActive", False)
        )
        total_subscribers = len(subscribers)

        # Calculate email delivery statistics
        sent_emails = sum(1 for e in emaildeliveries if e.get_state() == "sent")
        failed_emails = sum(1 for e in emaildeliveries if e.get_state() == "failed")
        total_emails = len(emaildeliveries)

        # Calculate interaction statistics
        interaction_counts: Dict[str, int] = {}
        for interaction in interactions:
            interaction_type = interaction.data.get("interactionType", "UNKNOWN")
            interaction_counts[interaction_type] = (
                interaction_counts.get(interaction_type, 0) + 1
            )

        # Calculate weekly schedule statistics
        completed_schedules = sum(
            1 for w in weeklyschedules if w.get_state() == "completed"
        )
        total_schedules = len(weeklyschedules)

        dashboard_data = {
            "subscribers": {
                "total": total_subscribers,
                "active": active_subscribers,
                "inactive": total_subscribers - active_subscribers,
            },
            "catfacts": {
                "total": len(catfacts),
                "retrieved": sum(1 for c in catfacts if c.get_state() == "retrieved"),
                "scheduled": sum(1 for c in catfacts if c.get_state() == "scheduled"),
                "sent": sum(1 for c in catfacts if c.get_state() == "sent"),
                "archived": sum(1 for c in catfacts if c.get_state() == "archived"),
            },
            "emaildeliveries": {
                "total": total_emails,
                "sent": sent_emails,
                "failed": failed_emails,
                "pending": total_emails - sent_emails - failed_emails,
                "successRate": (
                    (sent_emails / total_emails * 100) if total_emails > 0 else 0
                ),
            },
            "interactions": {"total": len(interactions), "byType": interaction_counts},
            "weeklyschedules": {
                "total": total_schedules,
                "completed": completed_schedules,
                "active": total_schedules - completed_schedules,
            },
        }

        return jsonify(dashboard_data), 200

    except Exception as e:
        logger.exception("Error getting dashboard data: %s", str(e))
        return jsonify({"error": str(e)}), 500


@reporting_routes_bp.route("/subscriber-analytics", methods=["GET"])
async def get_subscriber_analytics() -> ResponseReturnValue:
    """Get subscriber analytics."""
    try:
        service = get_services()

        subscribers = await service.find_all(
            entity_class="Subscriber", entity_version="1"
        )
        interactions = await service.find_all(
            entity_class="Interaction", entity_version="1"
        )

        # Group interactions by subscriber
        subscriber_interactions: Dict[str, List[_ListedEntity]] = {}
        for interaction in interactions:
            subscriber_id = interaction.data.get("subscriberId")
            if subscriber_id and subscriber_id not in subscriber_interactions:
                subscriber_interactions[subscriber_id] = []
            if subscriber_id:
                subscriber_interactions[subscriber_id].append(interaction)

        # Calculate analytics per subscriber
        subscriber_analytics = []
        for subscriber in subscribers:
            subscriber_id = subscriber.get_id()
            subscriber_interactions_list = subscriber_interactions.get(
                subscriber_id, []
            )

            analytics = {
                "subscriberId": subscriber_id,
                "email": subscriber.data.get("email"),
                "isActive": subscriber.data.get("isActive", False),
                "subscriptionDate": subscriber.data.get("subscriptionDate"),
                "totalInteractions": len(subscriber_interactions_list),
                "interactionsByType": {},
            }

            # Count interactions by type
            for interaction in subscriber_interactions_list:
                interaction_type = interaction.data.get("interactionType", "UNKNOWN")
                analytics["interactionsByType"][interaction_type] = (
                    analytics["interactionsByType"].get(interaction_type, 0) + 1
                )

            subscriber_analytics.append(analytics)

        return (
            jsonify(
                {
                    "subscriberAnalytics": subscriber_analytics,
                    "totalSubscribers": len(subscribers),
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error getting subscriber analytics: %s", str(e))
        return jsonify({"error": str(e)}), 500


@reporting_routes_bp.route("/email-performance", methods=["GET"])
async def get_email_performance() -> ResponseReturnValue:
    """Get email delivery performance metrics."""
    try:
        service = get_services()

        emaildeliveries = await service.find_all(
            entity_class="EmailDelivery", entity_version="1"
        )

        # Calculate performance metrics
        total_deliveries = len(emaildeliveries)
        sent_count = 0
        failed_count = 0
        retry_count = 0
        total_attempts = 0

        for delivery in emaildeliveries:
            state = delivery.get_state()
            attempts = delivery.data.get("deliveryAttempts", 0)
            total_attempts += attempts

            if state == "sent":
                sent_count += 1
            elif state == "failed":
                failed_count += 1

            if attempts > 1:
                retry_count += 1

        performance_data = {
            "totalDeliveries": total_deliveries,
            "successfulDeliveries": sent_count,
            "failedDeliveries": failed_count,
            "pendingDeliveries": total_deliveries - sent_count - failed_count,
            "retriedDeliveries": retry_count,
            "totalAttempts": total_attempts,
            "successRate": (
                (sent_count / total_deliveries * 100) if total_deliveries > 0 else 0
            ),
            "failureRate": (
                (failed_count / total_deliveries * 100) if total_deliveries > 0 else 0
            ),
            "averageAttempts": (
                (total_attempts / total_deliveries) if total_deliveries > 0 else 0
            ),
        }

        return jsonify(performance_data), 200

    except Exception as e:
        logger.exception("Error getting email performance: %s", str(e))
        return jsonify({"error": str(e)}), 500


@reporting_routes_bp.route("/weekly-summary", methods=["GET"])
async def get_weekly_summary() -> ResponseReturnValue:
    """Get weekly schedule summary."""
    try:
        service = get_services()

        weeklyschedules = await service.find_all(
            entity_class="WeeklySchedule", entity_version="1"
        )

        weekly_summaries = []
        for schedule in weeklyschedules:
            summary = {
                "id": schedule.get_id(),
                "weekStartDate": schedule.data.get("weekStartDate"),
                "weekEndDate": schedule.data.get("weekEndDate"),
                "scheduledSendDate": schedule.data.get("scheduledSendDate"),
                "catFactId": schedule.data.get("catFactId"),
                "totalSubscribers": schedule.data.get("totalSubscribers", 0),
                "emailsSent": schedule.data.get("emailsSent", 0),
                "emailsFailed": schedule.data.get("emailsFailed", 0),
                "state": schedule.get_state(),
            }

            # Calculate success rate
            total_emails = summary["emailsSent"] + summary["emailsFailed"]
            if total_emails > 0:
                summary["successRate"] = (summary["emailsSent"] / total_emails) * 100
            else:
                summary["successRate"] = 0

            weekly_summaries.append(summary)

        return (
            jsonify(
                {
                    "weeklySummaries": weekly_summaries,
                    "totalWeeks": len(weekly_summaries),
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error getting weekly summary: %s", str(e))
        return jsonify({"error": str(e)}), 500
