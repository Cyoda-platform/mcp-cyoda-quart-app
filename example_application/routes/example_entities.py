"""
ExampleEntity Routes for Cyoda Client Application

Manages all ExampleEntity-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Protocol, cast

from pydantic import BaseModel, Field
from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import validate_querystring, validate_request

from common.service.entity_service import (
    CYODA_OPERATOR_MAPPING,
    LogicalOperator,
    SearchConditionRequest,
    SearchConditionRequestBuilder,
    SearchOperator,
)
from services.services import get_entity_service

# Imported for possible external references / type hints
from ..entity.example_entity import ExampleEntity  # noqa: F401

logger = logging.getLogger(__name__)

example_entities_bp = Blueprint(
    "example_entities", __name__, url_prefix="/api/example-entities"
)


# ---- Service typing ---------------------------------------------------------


class _EntityMetadata(Protocol):
    id: str
    state: str


class _SavedEntity(Protocol):
    metadata: _EntityMetadata
    data: Dict[str, Any]


class _ListedEntity(Protocol):
    def get_id(self) -> str: ...

    def get_state(self) -> str: ...

    data: Dict[str, Any]


class EntityServiceProtocol(Protocol):
    async def save(
        self, *, entity: Dict[str, Any], entity_class: str, entity_version: str
    ) -> _SavedEntity: ...

    async def get_by_id(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> Optional[_SavedEntity]: ...

    async def search(
        self,
        entity_class: str,
        condition: SearchConditionRequest,
        entity_version: str = "1",
    ) -> List[_ListedEntity]: ...

    async def find_all(
        self, *, entity_class: str, entity_version: str
    ) -> List[_ListedEntity]: ...

    async def update(
        self,
        *,
        entity_id: str,
        entity: Dict[str, Any],
        entity_class: str,
        transition: Optional[str],
        entity_version: str,
    ) -> _SavedEntity: ...

    async def delete_by_id(
        self, *, entity_id: str, entity_class: str, entity_version: str
    ) -> None: ...

    async def execute_transition(
        self,
        *,
        entity_id: str,
        transition: str,
        entity_class: str,
        entity_version: str,
    ) -> _SavedEntity: ...


# Services will be accessed through the registry
entity_service: Optional[EntityServiceProtocol] = None


def get_services() -> EntityServiceProtocol:
    """Get services from the registry lazily."""
    global entity_service
    if entity_service is None:
        # get_entity_service() is likely untyped, so cast to our protocol
        entity_service = cast(EntityServiceProtocol, get_entity_service())
    return entity_service


# ---- Request/Query Models ---------------------------------------------------


class ExampleEntityQueryParams(BaseModel):
    """Query parameters for ExampleEntity listing"""

    category: Optional[str] = Field(default=None, description="Filter by category")
    is_active: Optional[bool] = Field(
        default=None, alias="isActive", description="Filter by active status"
    )
    state: Optional[str] = Field(default=None, description="Filter by workflow state")
    limit: int = Field(default=50, description="Number of results")
    offset: int = Field(default=0, description="Pagination offset")


class ExampleEntityCreateRequest(BaseModel):
    """Request model for creating an ExampleEntity"""

    name: str = Field(..., description="Name of the example entity")
    description: str = Field(..., description="Description of the entity")
    value: float = Field(..., description="Numeric value associated with the entity")
    category: str = Field(..., description="Category classification for the entity")
    is_active: bool = Field(
        ..., alias="isActive", description="Flag indicating if the entity is active"
    )


class ExampleEntityUpdateRequest(BaseModel):
    """Request model for updating an ExampleEntity"""

    name: Optional[str] = Field(default=None, description="Name of the example entity")
    description: Optional[str] = Field(
        default=None, description="Description of the entity"
    )
    value: Optional[float] = Field(
        default=None, description="Numeric value associated with the entity"
    )
    category: Optional[str] = Field(
        default=None, description="Category classification for the entity"
    )
    is_active: Optional[bool] = Field(
        default=None,
        alias="isActive",
        description="Flag indicating if the entity is active",
    )
    transition: Optional[str] = Field(
        default=None, description="Workflow transition to trigger"
    )


class TransitionRequest(BaseModel):
    """Request model for triggering workflow transitions"""

    transition_name: str = Field(
        ..., alias="transitionName", description="Name of the transition to execute"
    )


# ---- Routes -----------------------------------------------------------------


@example_entities_bp.route("", methods=["POST"])
@validate_request(ExampleEntityCreateRequest)
async def create_example_entity(
    data: ExampleEntityCreateRequest,
) -> ResponseReturnValue:
    """Create a new ExampleEntity"""
    try:
        service = get_services()

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data, entity_class="ExampleEntity", entity_version="1"
        )

        logger.info("Created ExampleEntity with ID: %s", response.metadata.id)

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "message": "ExampleEntity created successfully",
                }
            ),
            201,
        )

    except Exception as e:  # pragma: no cover - keep robust error handling
        logger.exception("Error creating ExampleEntity: %s", str(e))
        return jsonify({"error": str(e)}), 500


@example_entities_bp.route("/<entity_id>", methods=["GET"])
async def get_example_entity(entity_id: str) -> ResponseReturnValue:
    """Get ExampleEntity by ID"""
    try:
        service = get_services()

        response = await service.get_by_id(
            entity_id=entity_id, entity_class="ExampleEntity", entity_version="1"
        )

        if not response:
            return jsonify({"error": "ExampleEntity not found"}), 404

        # Convert to API response format
        entity_data: Dict[str, Any] = dict(response.data)
        entity_data["id"] = response.metadata.id
        entity_data["state"] = response.metadata.state

        return jsonify(entity_data), 200

    except Exception as e:  # pragma: no cover
        logger.exception("Error getting ExampleEntity %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@example_entities_bp.route("", methods=["GET"])
@validate_querystring(ExampleEntityQueryParams)
async def list_example_entities(
    query_args: ExampleEntityQueryParams,
) -> ResponseReturnValue:
    """List ExampleEntities with optional filtering"""
    try:
        service = get_services()

        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.category:
            search_conditions["category"] = query_args.category

        if query_args.is_active is not None:
            search_conditions["isActive"] = str(query_args.is_active).lower()

        if query_args.state:
            search_conditions["state"] = query_args.state

        # Get entities
        if search_conditions:
            # Build search condition request
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class="ExampleEntity",
                condition=condition,
                entity_version="1",
            )
        else:
            entities = await service.find_all(
                entity_class="ExampleEntity", entity_version="1"
            )

        # Convert to API response format
        entity_list: List[Dict[str, Any]] = []
        for entity in entities:
            entity_data = {
                "id": entity.get_id(),
                "name": entity.data.get("name"),
                "state": entity.get_state(),
            }
            entity_list.append(entity_data)

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"entities": paginated_entities, "total": len(entity_list)}), 200

    except Exception as e:  # pragma: no cover
        logger.exception("Error listing ExampleEntities: %s", str(e))
        return jsonify({"error": str(e)}), 500


@example_entities_bp.route("/<entity_id>", methods=["PUT"])
@validate_request(ExampleEntityUpdateRequest)
async def update_example_entity(
    entity_id: str, data: ExampleEntityUpdateRequest
) -> ResponseReturnValue:
    """Update ExampleEntity and optionally trigger workflow transition"""
    try:
        service = get_services()

        # Get transition from request body or query parameter
        transition: Optional[str] = data.transition or request.args.get("transition")

        # Convert request to entity data (exclude None values)
        entity_data: Dict[str, Any] = {
            k: v
            for k, v in data.model_dump(by_alias=True, exclude_none=True).items()
            if k != "transition"
        }

        # Update the entity
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class="ExampleEntity",
            transition=transition,
            entity_version="1",
        )

        logger.info("Updated ExampleEntity %s", entity_id)

        result: Dict[str, Any] = {
            "id": response.metadata.id,
            "message": "ExampleEntity updated successfully",
        }

        if transition:
            result["newState"] = response.metadata.state

        return jsonify(result), 200

    except Exception as e:  # pragma: no cover
        logger.exception("Error updating ExampleEntity %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


@example_entities_bp.route("/<entity_id>", methods=["DELETE"])
async def delete_example_entity(entity_id: str) -> ResponseReturnValue:
    """Delete ExampleEntity"""
    try:
        service = get_services()

        await service.delete_by_id(
            entity_id=entity_id, entity_class="ExampleEntity", entity_version="1"
        )

        logger.info("Deleted ExampleEntity %s", entity_id)

        return jsonify({"message": "ExampleEntity deleted successfully"}), 200

    except Exception as e:  # pragma: no cover
        logger.exception("Error deleting ExampleEntity %s: %s", entity_id, str(e))
        return jsonify({"error": str(e)}), 500


# ---- Additional Entity Service Endpoints ----------------------------------------


@example_entities_bp.route("/by-business-id/<business_id>", methods=["GET"])
async def get_by_business_id(business_id: str) -> ResponseReturnValue:
    """Get ExampleEntity by business ID"""
    try:
        service = get_entity_service()
        business_id_field = request.args.get("field", "name")  # Default to name field

        result = await service.find_by_business_id(
            entity_class="ExampleEntity",
            business_id=business_id,
            business_id_field=business_id_field,
            entity_version="1",
        )

        if not result:
            return jsonify({"error": "ExampleEntity not found"}), 404

        entity_data = {
            "id": result.get_id(),
            "data": result.data,
            "state": result.metadata.state,
            "created_at": result.metadata.created_at,
            "updated_at": result.metadata.updated_at,
        }

        return jsonify(entity_data), 200

    except Exception as e:
        logger.exception(
            "Error getting ExampleEntity by business ID %s: %s", business_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


@example_entities_bp.route("/<entity_id>/exists", methods=["GET"])
async def check_exists(entity_id: str) -> ResponseReturnValue:
    """Check if ExampleEntity exists by ID"""
    try:
        service = get_entity_service()

        exists = await service.exists_by_id(
            entity_id=entity_id, entity_class="ExampleEntity", entity_version="1"
        )

        return jsonify({"exists": exists, "entity_id": entity_id}), 200

    except Exception as e:
        logger.exception(
            "Error checking ExampleEntity existence %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


@example_entities_bp.route("/count", methods=["GET"])
async def count_entities() -> ResponseReturnValue:
    """Count ExampleEntities"""
    try:
        service = get_entity_service()

        count = await service.count(entity_class="ExampleEntity", entity_version="1")

        return jsonify({"count": count}), 200

    except Exception as e:
        logger.exception("Error counting ExampleEntities: %s", str(e))
        return jsonify({"error": str(e)}), 500


@example_entities_bp.route("/<entity_id>/transitions", methods=["GET"])
async def get_available_transitions(entity_id: str) -> ResponseReturnValue:
    """Get available transitions for ExampleEntity"""
    try:
        service = get_entity_service()

        transitions = await service.get_transitions(
            entity_id=entity_id, entity_class="ExampleEntity", entity_version="1"
        )

        return jsonify({"transitions": transitions, "entity_id": entity_id}), 200

    except Exception as e:
        logger.exception(
            "Error getting transitions for ExampleEntity %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500


# ---- Search Endpoints -----------------------------------------------------------


@example_entities_bp.route("/search", methods=["POST"])
async def search_entities() -> ResponseReturnValue:
    """Search ExampleEntities using Cyoda search format"""
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
            entity_class="ExampleEntity", condition=search_request, entity_version="1"
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
        logger.exception("Error searching ExampleEntities: %s", str(e))
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


@example_entities_bp.route("/find-all", methods=["GET"])
async def find_all_entities() -> ResponseReturnValue:
    """Find all ExampleEntities"""
    try:
        service = get_entity_service()

        results = await service.find_all(
            entity_class="ExampleEntity", entity_version="1"
        )

        return jsonify({"entities": results, "total": len(results)}), 200

    except Exception as e:
        logger.exception("Error finding all ExampleEntities: %s", str(e))
        return jsonify({"error": str(e)}), 500


@example_entities_bp.route("/<entity_id>/transitions", methods=["POST"])
@validate_request(TransitionRequest)
async def trigger_transition(
    entity_id: str, data: TransitionRequest
) -> ResponseReturnValue:
    """Trigger a specific workflow transition"""
    try:
        service = get_services()

        # Get current entity state
        current_entity = await service.get_by_id(
            entity_id=entity_id, entity_class="ExampleEntity", entity_version="1"
        )

        if not current_entity:
            return jsonify({"error": "ExampleEntity not found"}), 404

        previous_state = current_entity.metadata.state

        # Execute the transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition=data.transition_name,
            entity_class="ExampleEntity",
            entity_version="1",
        )

        logger.info(
            "Executed transition '%s' on ExampleEntity %s",
            data.transition_name,
            entity_id,
        )

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "message": "Transition executed successfully",
                    "previousState": previous_state,
                    "newState": response.metadata.state,
                }
            ),
            200,
        )

    except Exception as e:  # pragma: no cover
        logger.exception(
            "Error executing transition on ExampleEntity %s: %s", entity_id, str(e)
        )
        return jsonify({"error": str(e)}), 500
