"""
ExampleEntity Routes for Cyoda Client Application

Manages all ExampleEntity-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from quart import Blueprint, jsonify, request
from quart_schema import validate_querystring, validate_request

from entity.example_entity import ExampleEntity
from service.services import get_entity_service

logger = logging.getLogger(__name__)

example_entities_bp = Blueprint(
    "example_entities", __name__, url_prefix="/api/example-entities"
)

# Services will be accessed through the registry
entity_service = None


def get_services():
    """Get services from the registry lazily."""
    global entity_service
    if entity_service is None:
        entity_service = get_entity_service()
    return entity_service


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


@example_entities_bp.route("", methods=["POST"])
@validate_request(ExampleEntityCreateRequest)
async def create_example_entity(data: ExampleEntityCreateRequest):
    """Create a new ExampleEntity"""
    try:
        service = get_services()

        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data, entity_class="ExampleEntity", entity_version="1"
        )

        logger.info(f"Created ExampleEntity with ID: {response.metadata.id}")

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "message": "ExampleEntity created successfully",
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Error creating ExampleEntity: {str(e)}")
        return jsonify({"error": str(e)}), 500


@example_entities_bp.route("/<entity_id>", methods=["GET"])
async def get_example_entity(entity_id: str):
    """Get ExampleEntity by ID"""
    try:
        service = get_services()

        response = await service.get_by_id(
            entity_id=entity_id, entity_class="ExampleEntity", entity_version="1"
        )

        if not response:
            return jsonify({"error": "ExampleEntity not found"}), 404

        # Convert to API response format
        entity_data = response.data
        entity_data["id"] = response.metadata.id
        entity_data["state"] = response.metadata.state

        return jsonify(entity_data), 200

    except Exception as e:
        logger.error(f"Error getting ExampleEntity {entity_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500


@example_entities_bp.route("", methods=["GET"])
@validate_querystring(ExampleEntityQueryParams)
async def list_example_entities(query_args: ExampleEntityQueryParams):
    """List ExampleEntities with optional filtering"""
    try:
        service = get_services()

        # Build search conditions based on query parameters
        search_conditions = {}

        if query_args.category:
            search_conditions["category"] = query_args.category

        if query_args.is_active is not None:
            search_conditions["isActive"] = str(query_args.is_active).lower()

        if query_args.state:
            search_conditions["state"] = query_args.state

        # Get entities
        if search_conditions:
            entities = await service.search(
                entity_class="ExampleEntity",
                search_conditions=search_conditions,
                entity_version="1",
            )
        else:
            entities = await service.find_all(
                entity_class="ExampleEntity", entity_version="1"
            )

        # Convert to API response format
        entity_list = []
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

    except Exception as e:
        logger.error(f"Error listing ExampleEntities: {str(e)}")
        return jsonify({"error": str(e)}), 500


@example_entities_bp.route("/<entity_id>", methods=["PUT"])
@validate_request(ExampleEntityUpdateRequest)
async def update_example_entity(entity_id: str, data: ExampleEntityUpdateRequest):
    """Update ExampleEntity and optionally trigger workflow transition"""
    try:
        service = get_services()

        # Get transition from request body or query parameter
        transition = data.transition or request.args.get("transition")

        # Convert request to entity data (exclude None values)
        entity_data = {
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

        logger.info(f"Updated ExampleEntity {entity_id}")

        result = {
            "id": response.metadata.id,
            "message": "ExampleEntity updated successfully",
        }

        if transition:
            result["newState"] = response.metadata.state

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error updating ExampleEntity {entity_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500


@example_entities_bp.route("/<entity_id>", methods=["DELETE"])
async def delete_example_entity(entity_id: str):
    """Delete ExampleEntity"""
    try:
        service = get_services()

        await service.delete_by_id(
            entity_id=entity_id, entity_class="ExampleEntity", entity_version="1"
        )

        logger.info(f"Deleted ExampleEntity {entity_id}")

        return jsonify({"message": "ExampleEntity deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Error deleting ExampleEntity {entity_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500


@example_entities_bp.route("/<entity_id>/transitions", methods=["POST"])
@validate_request(TransitionRequest)
async def trigger_transition(entity_id: str, data: TransitionRequest):
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
            f"Executed transition '{json.transition_name}' on ExampleEntity {entity_id}"
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

    except Exception as e:
        logger.error(
            f"Error executing transition on ExampleEntity {entity_id}: {str(e)}"
        )
        return jsonify({"error": str(e)}), 500
