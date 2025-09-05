"""
Nobel laureate management routes.

This module contains routes for managing Nobel Prize laureate data.
"""

import logging
from dataclasses import dataclass
from typing import Optional

import httpx
from quart import Blueprint, jsonify, request, abort
from quart_schema import validate_querystring

from service.services import get_entity_service, get_auth_service
from common.config.config import ENTITY_VERSION

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

laureates_bp = Blueprint('laureates', __name__, url_prefix='/laureates')

# Services will be accessed through the registry
entity_service = None
cyoda_auth_service = None

NOBEL_API_URL = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/nobel-prize-laureates/records?limit=100"


@dataclass
class LaureateQuery:
    year: Optional[str]
    category: Optional[str]


def get_services():
    """Get services from the registry lazily."""
    global entity_service, cyoda_auth_service
    if entity_service is None:
        entity_service = get_entity_service()
    if cyoda_auth_service is None:
        cyoda_auth_service = get_auth_service()
    return entity_service, cyoda_auth_service


def validate_laureate(raw: dict) -> Optional[dict]:
    """Validate and transform laureate data from the Nobel API."""
    fields = raw.get("record", {}).get("fields", {})
    
    if not fields.get("fullname"):
        return None
    
    return {
        "fullname": fields.get("fullname"),
        "year": fields.get("year"),
        "category": fields.get("category"),
        "motivation": fields.get("motivation"),
        "birth_date": fields.get("birth_date"),
        "birth_country": fields.get("birth_country"),
        "gender": fields.get("gender"),
        "organization_name": fields.get("organization_name"),
        "organization_country": fields.get("organization_country"),
        "prize_share": fields.get("prize_share"),
        "id": fields.get("id")
    }


async def fetch_laureates_from_api():
    """Fetch laureates from the Nobel Prize API."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(NOBEL_API_URL)
            response.raise_for_status()
            data = response.json()
            
            laureates = []
            for result in data.get("results", []):
                laureate = validate_laureate(result)
                if laureate:
                    laureates.append(laureate)
            
            return laureates
    except Exception as e:
        logger.exception(f"Failed to fetch laureates from API: {e}")
        return []


async def notify_subscribers_about_laureate(entity: dict):
    """Notify subscribers about a new laureate (placeholder implementation)."""
    try:
        # This would typically notify subscribers about new laureate data
        # Implementation depends on your notification system
        logger.info(f"Would notify subscribers about laureate: {entity.get('fullname')}")
        entity.setdefault("notification_sent", True)
    except Exception as e:
        logger.exception(f"Failed to notify subscribers: {e}")
        entity.setdefault("notification_error", str(e))

    return entity


@laureates_bp.route("", methods=["GET"])
@validate_querystring(LaureateQuery)
async def get_laureates():
    """Get laureates with optional filtering by year and category."""
    entity_service, cyoda_auth_service = get_services()

    args = LaureateQuery(**request.args)
    
    try:
        # Try to get from entity service first
        laureates = await entity_service.get_items("laureate", ENTITY_VERSION)
        
        # If no laureates in storage, fetch from API
        if not laureates:
            laureates = await fetch_laureates_from_api()
            
        # Apply filters
        if args.year:
            laureates = [l for l in laureates if str(l.get("year")) == args.year]
        if args.category:
            laureates = [l for l in laureates if l.get("category") == args.category]
            
        logger.info(f"Retrieved {len(laureates)} laureates")
        return jsonify(laureates)
        
    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to retrieve laureates")


@laureates_bp.route("/<string:technical_id>", methods=["GET"])
async def get_laureate(technical_id):
    """Get a specific laureate by technical ID."""
    entity_service, cyoda_auth_service = get_services()

    try:
        laureate = await entity_service.get_item(
            technical_id, "laureate", ENTITY_VERSION
        )
        logger.info(f"Retrieved laureate {technical_id}")
    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to retrieve laureate")
    
    if not laureate:
        abort(404, description="Laureate not found")
    
    return jsonify(laureate)


@laureates_bp.route("", methods=["POST"])
async def create_laureate():
    """Create a new laureate entry."""
    entity_service, cyoda_auth_service = get_services()

    try:
        data = await request.get_json()
        if not data:
            abort(400, description="Request body is required")

        # Validate required fields
        if not data.get("fullname"):
            abort(400, description="fullname is required")

        # Add metadata
        import uuid
        from datetime import datetime, timezone
        
        laureate_id = str(uuid.uuid4())
        laureate_data = {
            **data,
            "id": laureate_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        # Notify subscribers
        laureate_data = await notify_subscribers_about_laureate(laureate_data)

        # Save to entity service
        await entity_service.save_item(
            laureate_data, "laureate", laureate_id, ENTITY_VERSION
        )
        
        logger.info(f"Created laureate {laureate_id}")
        return jsonify(laureate_data), 201

    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to create laureate")


@laureates_bp.route("/<string:technical_id>", methods=["PUT"])
async def update_laureate(technical_id):
    """Update an existing laureate."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Check if laureate exists
        existing_laureate = await entity_service.get_item(
            technical_id, "laureate", ENTITY_VERSION
        )
        if not existing_laureate:
            abort(404, description="Laureate not found")

        # Get update data
        data = await request.get_json()
        if not data:
            abort(400, description="Request body is required")

        # Update the laureate
        updated_laureate = {**existing_laureate, **data}
        updated_laureate["updated_at"] = datetime.now(timezone.utc).isoformat()

        await entity_service.save_item(
            updated_laureate, "laureate", technical_id, ENTITY_VERSION
        )
        
        logger.info(f"Updated laureate {technical_id}")
        return jsonify(updated_laureate)

    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to update laureate")


@laureates_bp.route("/<string:technical_id>", methods=["DELETE"])
async def delete_laureate(technical_id):
    """Delete a laureate."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Check if laureate exists
        laureate = await entity_service.get_item(
            technical_id, "laureate", ENTITY_VERSION
        )
        if not laureate:
            abort(404, description="Laureate not found")

        # Delete laureate (implementation depends on your entity service)
        # await entity_service.delete_item(technical_id, "laureate", ENTITY_VERSION)
        
        logger.info(f"Deleted laureate {technical_id}")
        return jsonify({"message": f"Laureate {technical_id} deleted successfully"}), 200

    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to delete laureate")


@laureates_bp.route("/sync", methods=["POST"])
async def sync_laureates():
    """Sync laureates from the Nobel Prize API."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Fetch from API
        api_laureates = await fetch_laureates_from_api()
        
        if not api_laureates:
            return jsonify({"message": "No laureates fetched from API"}), 200

        # Save each laureate
        saved_count = 0
        for laureate_data in api_laureates:
            try:
                laureate_id = str(uuid.uuid4())
                laureate_data["id"] = laureate_id
                laureate_data["synced_at"] = datetime.now(timezone.utc).isoformat()
                
                await entity_service.save_item(
                    laureate_data, "laureate", laureate_id, ENTITY_VERSION
                )
                saved_count += 1
            except Exception as e:
                logger.warning(f"Failed to save laureate {laureate_data.get('fullname')}: {e}")

        logger.info(f"Synced {saved_count} laureates from API")
        return jsonify({
            "message": f"Successfully synced {saved_count} laureates",
            "total_fetched": len(api_laureates),
            "saved_count": saved_count
        }), 200

    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to sync laureates")
