"""
OtherEntity Routes for Cyoda Client Application

Manages all OtherEntity-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

import logging
from typing import Any, Dict, Optional, Tuple

from pydantic import BaseModel, Field
from quart import Blueprint, Response, jsonify, request
from quart_schema import validate_querystring, validate_request

from common.service.entity_service import (
    CYODA_OPERATOR_MAPPING,
    EntityService,
    LogicalOperator,
    SearchConditionRequest,
    SearchConditionRequestBuilder,
    SearchOperator,
)
from services.services import get_entity_service

logger = logging.getLogger(__name__)

other_entities_bp = Blueprint(
    "other_entities", __name__, url_prefix="/api/other-entities"
)

# Services will be accessed through the registry
entity_service: Optional[EntityService] = None


def get_services() -> EntityService:
    """Get services from the registry lazily."""
    global entity_service
    if entity_service is None:
        entity_service = get_entity_service()
    return entity_service


class OtherEntityQueryParams(BaseModel):
    """Query parameters for OtherEntity listing"""

    source_entity_id: Optional[str] = Field(
        default=None, alias="sourceEntityId", description="Filter by source entity ID"
    )
    priority: Optional[str] = Field(
        default=None, description="Filter by priority level"
    )
    state: Optional[str] = Field(default=None, description="Filter by workflow state")
    limit: int = Field(default=50, description="Number of results")
    offset: int = Field(default=0, description="Pagination offset")


class OtherEntityCreateRequest(BaseModel):
    """Request model for creating an OtherEntity"""

    title: str = Field(..., description="Title of the other entity")
    content: str = Field(..., description="Content or data of the entity")
    priority: str = Field(..., description="Priority level (LOW, MEDIUM, HIGH)")
    source_entity_id: Optional[str] = Field(
        default=None,
        alias="sourceEntityId",
        description="Reference to the ExampleEntity",
    )
    last_updated_by: Optional[str] = Field(
        default=None,
        alias="lastUpdatedBy",
        description="Identifier of the entity that last updated this one",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata"
    )


class OtherEntityUpdateRequest(BaseModel):
    """Request model for updating an OtherEntity"""

    title: Optional[str] = Field(default=None, description="Title of the other entity")
    content: Optional[str] = Field(
        default=None, description="Content or data of the entity"
    )
    priority: Optional[str] = Field(
        default=None, description="Priority level (LOW, MEDIUM, HIGH)"
    )
    last_updated_by: Optional[str] = Field(
        default=None,
        alias="lastUpdatedBy",
        description="Identifier of the entity that last updated this one",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata"
    )
    transition: Optional[str] = Field(
        default=None, description="Workflow transition to trigger"
    )


@other_entities_bp.route("", methods=["POST"])
@validate_request(OtherEntityCreateRequest)
async def create_other_entity(json: OtherEntityCreateRequest) -> Tuple[Response, int]:
    """Create a new OtherEntity"""
    try:
        service = get_services()

        # Convert request to entity data
        entity_data = json.dict(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data, entity_class="OtherEntity", entity_version="1"
        )

        logger.info(f"Created OtherEntity with ID: {response.metadata.id}")

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "message": "OtherEntity created successfully",
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Error creating OtherEntity: {str(e)}")
        return jsonify({"error": str(e)}), 500


@other_entities_bp.route("/<entity_id>", methods=["GET"])
async def get_other_entity(entity_id: str) -> Tuple[Response, int]:
    """Get OtherEntity by ID"""
    try:
        service = get_services()

        response = await service.get_by_id(
            entity_id=entity_id, entity_class="OtherEntity", entity_version="1"
        )

        if not response:
            return jsonify({"error": "OtherEntity not found"}), 404

        # Convert to API response format
        entity_data = response.data
        entity_data["id"] = response.metadata.id
        entity_data["state"] = response.metadata.state

        return jsonify(entity_data), 200

    except Exception as e:
        logger.error(f"Error getting OtherEntity {entity_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500


@other_entities_bp.route("", methods=["GET"])
@validate_querystring(OtherEntityQueryParams)
async def list_other_entities(
    query_args: OtherEntityQueryParams,
) -> Tuple[Response, int]:
    """List OtherEntities with optional filtering"""
    try:
        service = get_services()

        # Build search conditions based on query parameters
        search_conditions = {}

        if query_args.source_entity_id:
            search_conditions["sourceEntityId"] = query_args.source_entity_id

        if query_args.priority:
            search_conditions["priority"] = query_args.priority

        if query_args.state:
            search_conditions["state"] = query_args.state

        # Get entities
        if search_conditions:
            # Build SearchConditionRequest from the search conditions
            condition_builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                condition_builder.equals(field, value)
            condition = condition_builder.build()

            entities = await service.search(
                entity_class="OtherEntity",
                condition=condition,
                entity_version="1",
            )
        else:
            entities = await service.find_all(
                entity_class="OtherEntity", entity_version="1"
            )

        # Convert to API response format
        entity_list = []
        for entity in entities:
            entity_data = {
                "id": entity.get_id(),
                "title": entity.data.get("title"),
                "priority": entity.data.get("priority"),
                "state": entity.get_state(),
            }
            entity_list.append(entity_data)

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"entities": paginated_entities, "total": len(entity_list)}), 200

    except Exception as e:
        logger.error(f"Error listing OtherEntities: {str(e)}")
        return jsonify({"error": str(e)}), 500


@other_entities_bp.route("/<entity_id>", methods=["PUT"])
@validate_request(OtherEntityUpdateRequest)
async def update_other_entity(
    entity_id: str, json: OtherEntityUpdateRequest
) -> Tuple[Response, int]:
    """Update OtherEntity and optionally trigger workflow transition"""
    try:
        service = get_services()

        # Get transition from request body or query parameter
        transition = json.transition or request.args.get("transition")

        # Convert request to entity data (exclude None values)
        entity_data = {
            k: v
            for k, v in json.dict(by_alias=True, exclude_none=True).items()
            if k != "transition"
        }

        # Update the entity
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class="OtherEntity",
            transition=transition,
            entity_version="1",
        )

        logger.info(f"Updated OtherEntity {entity_id}")

        result = {
            "id": response.metadata.id,
            "message": "OtherEntity updated successfully",
        }

        if transition:
            result["newState"] = response.metadata.state or "unknown"

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error updating OtherEntity {entity_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500


@other_entities_bp.route("/<entity_id>", methods=["DELETE"])
async def delete_other_entity(entity_id: str) -> Tuple[Response, int]:
    """Delete OtherEntity"""
    try:
        service = get_services()

        await service.delete_by_id(
            entity_id=entity_id, entity_class="OtherEntity", entity_version="1"
        )

        logger.info(f"Deleted OtherEntity {entity_id}")

        return jsonify({"message": "OtherEntity deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Error deleting OtherEntity {entity_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ---- Additional Entity Service Endpoints ----------------------------------------


@other_entities_bp.route("/by-business-id/<business_id>", methods=["GET"])
async def get_by_business_id(business_id: str) -> Tuple[Response, int]:
    """Get OtherEntity by business ID"""
    try:
        service = get_entity_service()
        business_id_field = request.args.get("field", "title")  # Default to title field

        result = await service.find_by_business_id(
            entity_class="OtherEntity",
            business_id=business_id,
            business_id_field=business_id_field,
            entity_version="1",
        )

        if not result:
            return jsonify({"error": "OtherEntity not found"}), 404

        entity_data = {
            "id": result.get_id(),
            "data": result.data,
            "state": result.metadata.state,
            "created_at": result.metadata.created_at,
            "updated_at": result.metadata.updated_at,
        }

        return jsonify(entity_data), 200

    except Exception as e:
        logger.error(
            f"Error getting OtherEntity by business ID {business_id}: {str(e)}"
        )
        return jsonify({"error": str(e)}), 500


@other_entities_bp.route("/<entity_id>/exists", methods=["GET"])
async def check_exists(entity_id: str) -> Tuple[Response, int]:
    """Check if OtherEntity exists by ID"""
    try:
        service = get_entity_service()

        exists = await service.exists_by_id(
            entity_id=entity_id, entity_class="OtherEntity", entity_version="1"
        )

        return jsonify({"exists": exists, "entity_id": entity_id}), 200

    except Exception as e:
        logger.error(f"Error checking OtherEntity existence {entity_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500


@other_entities_bp.route("/count", methods=["GET"])
async def count_entities() -> Tuple[Response, int]:
    """Count OtherEntities"""
    try:
        service = get_entity_service()

        count = await service.count(entity_class="OtherEntity", entity_version="1")

        return jsonify({"count": count}), 200

    except Exception as e:
        logger.error(f"Error counting OtherEntities: {str(e)}")
        return jsonify({"error": str(e)}), 500


@other_entities_bp.route("/<entity_id>/transitions", methods=["GET"])
async def get_available_transitions(entity_id: str) -> Tuple[Response, int]:
    """Get available transitions for OtherEntity"""
    try:
        service = get_entity_service()

        transitions = await service.get_transitions(
            entity_id=entity_id, entity_class="OtherEntity", entity_version="1"
        )

        return jsonify({"transitions": transitions, "entity_id": entity_id}), 200

    except Exception as e:
        logger.error(f"Error getting transitions for OtherEntity {entity_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ---- Search Endpoints -----------------------------------------------------------


@other_entities_bp.route("/search", methods=["POST"])
async def search_entities() -> Tuple[Response, int]:
    """Search OtherEntities using Cyoda search format"""
    try:
        service = get_entity_service()
        search_data = await request.get_json()

        if not search_data:
            return jsonify({"error": "Search conditions required"}), 400

        # Convert Cyoda search format to SearchConditionRequest
        builder = SearchConditionRequest.builder()

        # Check if this is a Cyoda-style search condition
        if isinstance(search_data, dict) and search_data.get("type") == "group":
            # Handle complex Cyoda search structure (multiple conditions)
            operator = search_data.get("operator", "AND").upper()
            if operator == "AND":
                builder.operator(LogicalOperator.AND)
            elif operator == "OR":
                builder.operator(LogicalOperator.OR)

            conditions = search_data.get("conditions", [])
            for condition in conditions:
                _process_cyoda_condition(condition, builder)

        elif isinstance(search_data, dict) and search_data.get("type") in [
            "simple",
            "lifecycle",
        ]:
            # Handle single Cyoda condition (not wrapped in group)
            _process_cyoda_condition(search_data, builder)

        else:
            # Handle simple field-value pairs (backward compatibility)
            for field, value in search_data.items():
                builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class="OtherEntity", condition=search_request, entity_version="1"
        )

        # Convert to simple format for API response
        entities = [
            {
                "id": r.get_id(),
                "data": r.data,
                "state": r.metadata.state,
                "created_at": r.metadata.created_at,
                "updated_at": r.metadata.updated_at,
            }
            for r in results
        ]

        return (
            jsonify(
                {
                    "entities": entities,
                    "total": len(entities),
                    "search_conditions": search_data,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error searching OtherEntities: {str(e)}")
        return jsonify({"error": str(e)}), 500


@other_entities_bp.route("/find-all", methods=["GET"])
async def find_all_entities() -> Tuple[Response, int]:
    """Find all OtherEntities"""
    try:
        service = get_entity_service()

        results = await service.find_all(entity_class="OtherEntity", entity_version="1")

        return jsonify({"entities": results, "total": len(results)}), 200

    except Exception as e:
        logger.error(f"Error finding all OtherEntities: {str(e)}")
        return jsonify({"error": str(e)}), 500


def _process_cyoda_condition(
    condition: Dict[str, Any], builder: SearchConditionRequestBuilder
) -> None:
    """Process a single Cyoda condition and add it to the builder."""
    condition_type = condition.get("type")

    if condition_type == "lifecycle":
        # Handle lifecycle conditions (entity state)
        field = condition.get("field", "state")
        operator_type = condition.get("operatorType", "EQUALS")
        value = condition.get("value")

        # Map Cyoda operators to internal operators using enum mapping
        search_operator = CYODA_OPERATOR_MAPPING.get(
            operator_type, SearchOperator.EQUALS
        )
        builder.add_condition(field, search_operator, value)

    elif condition_type == "simple":
        # Handle simple JSON path conditions
        json_path = condition.get("jsonPath", "")
        operator_type = condition.get("operatorType", "EQUALS")
        value = condition.get("value")

        # Convert JSON path to field name (remove $. prefix)
        field = json_path.replace("$.", "") if json_path.startswith("$.") else json_path

        # Map Cyoda operators to internal operators using enum mapping
        search_operator = CYODA_OPERATOR_MAPPING.get(
            operator_type, SearchOperator.EQUALS
        )
        builder.add_condition(field, search_operator, value)
