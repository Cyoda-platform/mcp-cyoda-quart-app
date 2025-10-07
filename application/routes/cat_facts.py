"""
CatFact Routes for Cat Facts Subscription System

Manages all CatFact-related API endpoints including CRUD operations
and fact management.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag

from application.entity.cat_fact.version_1.cat_fact import CatFact
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

logger = logging.getLogger(__name__)


# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


cat_facts_bp = Blueprint("cat_facts", __name__, url_prefix="/api/cat-facts")


@cat_facts_bp.route("", methods=["POST"])
@tag(["cat-facts"])
@operation_id("create_cat_fact")
async def create_cat_fact() -> ResponseReturnValue:
    """Create a new cat fact"""
    try:
        data = await request.get_json()
        if not data:
            return {"error": "Request body is required", "code": "MISSING_BODY"}, 400

        # Create CatFact instance for validation
        cat_fact = CatFact(**data)
        entity_data = cat_fact.model_dump(by_alias=True)

        # Save the entity
        service = get_entity_service()
        response = await service.save(
            entity=entity_data,
            entity_class=CatFact.ENTITY_NAME,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        logger.info("Created CatFact with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating CatFact: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating CatFact: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@cat_facts_bp.route("/<entity_id>", methods=["GET"])
@tag(["cat-facts"])
@operation_id("get_cat_fact")
async def get_cat_fact(entity_id: str) -> ResponseReturnValue:
    """Get cat fact by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        service = get_entity_service()
        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=CatFact.ENTITY_NAME,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        if not response:
            return {"error": "CatFact not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200

    except Exception as e:
        logger.exception("Error getting CatFact %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@cat_facts_bp.route("", methods=["GET"])
@tag(["cat-facts"])
@operation_id("list_cat_facts")
async def list_cat_facts() -> ResponseReturnValue:
    """List all cat facts with optional filtering"""
    try:
        # Get query parameters
        source_api = request.args.get("source_api")
        category = request.args.get("category")
        is_validated = request.args.get("is_validated")
        ready_for_sending = request.args.get("ready_for_sending")

        service = get_entity_service()

        # Build search conditions if filters provided
        if source_api or category or is_validated:
            builder = SearchConditionRequest.builder()

            if source_api:
                builder.equals("source_api", source_api)
            if category:
                builder.equals("category", category)
            if is_validated:
                builder.equals("is_validated", is_validated.lower() == "true")

            condition = builder.build()
            entities = await service.search(
                entity_class=CatFact.ENTITY_NAME,
                condition=condition,
                entity_version=str(CatFact.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=CatFact.ENTITY_NAME,
                entity_version=str(CatFact.ENTITY_VERSION),
            )

        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Filter for ready_for_sending if requested
        if ready_for_sending and ready_for_sending.lower() == "true":
            from common.entity.entity_casting import cast_entity

            filtered_list = []
            for entity_dict in entity_list:
                cat_fact = cast_entity(CatFact(**entity_dict), CatFact)
                if cat_fact.is_ready_for_sending():
                    filtered_list.append(entity_dict)
            entity_list = filtered_list

        return {"cat_facts": entity_list, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error listing CatFacts: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@cat_facts_bp.route("/<entity_id>", methods=["PUT"])
@tag(["cat-facts"])
@operation_id("update_cat_fact")
async def update_cat_fact(entity_id: str) -> ResponseReturnValue:
    """Update cat fact and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        data = await request.get_json()
        if not data:
            return {"error": "Request body is required", "code": "MISSING_BODY"}, 400

        # Get transition from query parameters
        transition = request.args.get("transition")

        # Create CatFact instance for validation
        cat_fact = CatFact(**data)
        entity_data = cat_fact.model_dump(by_alias=True)

        # Update the entity
        service = get_entity_service()
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=CatFact.ENTITY_NAME,
            transition=transition,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        logger.info("Updated CatFact %s", entity_id)
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Validation error updating CatFact %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating CatFact %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@cat_facts_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["cat-facts"])
@operation_id("delete_cat_fact")
async def delete_cat_fact(entity_id: str) -> ResponseReturnValue:
    """Delete cat fact"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        service = get_entity_service()
        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=CatFact.ENTITY_NAME,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        logger.info("Deleted CatFact %s", entity_id)
        return {
            "success": True,
            "message": "CatFact deleted successfully",
            "entity_id": entity_id,
        }, 200

    except Exception as e:
        logger.exception("Error deleting CatFact %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@cat_facts_bp.route("/ready", methods=["GET"])
@tag(["cat-facts"])
@operation_id("get_ready_cat_facts")
async def get_ready_cat_facts() -> ResponseReturnValue:
    """Get cat facts that are ready for sending"""
    try:
        service = get_entity_service()

        # Get all cat facts
        entities = await service.find_all(
            entity_class=CatFact.ENTITY_NAME,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        # Filter for ready facts
        from common.entity.entity_casting import cast_entity

        ready_facts = []
        for entity_response in entities:
            cat_fact = cast_entity(entity_response.data, CatFact)
            if cat_fact.is_ready_for_sending():
                ready_facts.append(_to_entity_dict(entity_response.data))

        return {"cat_facts": ready_facts, "total": len(ready_facts)}, 200

    except Exception as e:
        logger.exception("Error getting ready CatFacts: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@cat_facts_bp.route("/random", methods=["GET"])
@tag(["cat-facts"])
@operation_id("get_random_cat_fact")
async def get_random_cat_fact() -> ResponseReturnValue:
    """Get a random cat fact that's ready for sending"""
    try:
        import random

        service = get_entity_service()

        # Get all ready cat facts
        entities = await service.find_all(
            entity_class=CatFact.ENTITY_NAME,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        # Filter for ready facts
        from common.entity.entity_casting import cast_entity

        ready_facts = []
        for entity_response in entities:
            cat_fact = cast_entity(entity_response.data, CatFact)
            if cat_fact.is_ready_for_sending():
                ready_facts.append(entity_response.data)

        if not ready_facts:
            return {"error": "No ready cat facts available", "code": "NO_FACTS"}, 404

        # Select random fact
        random_fact = random.choice(ready_facts)
        return _to_entity_dict(random_fact), 200

    except Exception as e:
        logger.exception("Error getting random CatFact: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@cat_facts_bp.route("/stats", methods=["GET"])
@tag(["cat-facts"])
@operation_id("get_cat_fact_stats")
async def get_cat_fact_stats() -> ResponseReturnValue:
    """Get cat fact statistics"""
    try:
        service = get_entity_service()

        # Get all cat facts
        entities = await service.find_all(
            entity_class=CatFact.ENTITY_NAME,
            entity_version=str(CatFact.ENTITY_VERSION),
        )

        # Calculate statistics
        stats = {
            "total_facts": len(entities),
            "by_source": {},
            "by_category": {},
            "by_validation_status": {"validated": 0, "unvalidated": 0},
            "by_usage": {
                "unused": 0,
                "used_once": 0,
                "low_usage": 0,
                "medium_usage": 0,
                "high_usage": 0,
            },
            "ready_for_sending": 0,
            "average_length": 0,
            "total_times_sent": 0,
        }

        total_length = 0
        from common.entity.entity_casting import cast_entity

        for entity_response in entities:
            cat_fact = cast_entity(entity_response.data, CatFact)

            # Count by source
            source = cat_fact.source_api
            stats["by_source"][source] = stats["by_source"].get(source, 0) + 1

            # Count by category
            category = cat_fact.category or "unknown"
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

            # Count by validation status
            if cat_fact.is_validated:
                stats["by_validation_status"]["validated"] += 1
            else:
                stats["by_validation_status"]["unvalidated"] += 1

            # Count by usage frequency
            usage = cat_fact.get_usage_frequency()
            stats["by_usage"][usage] += 1

            # Count ready for sending
            if cat_fact.is_ready_for_sending():
                stats["ready_for_sending"] += 1

            # Aggregate metrics
            total_length += cat_fact.fact_length
            stats["total_times_sent"] += cat_fact.times_sent

        # Calculate averages
        if len(entities) > 0:
            stats["average_length"] = total_length / len(entities)

        return stats, 200

    except Exception as e:
        logger.exception("Error getting cat fact stats: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
