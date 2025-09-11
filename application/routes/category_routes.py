"""
Category Routes for Purrfect Pets API

Manages all Category-related API endpoints as specified in functional requirements.
"""

import logging
from typing import Any, Dict, List, Optional, Protocol, cast

from pydantic import BaseModel, Field
from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import validate_request

from services.services import get_entity_service

logger = logging.getLogger(__name__)

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")


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


entity_service: Optional[EntityServiceProtocol] = None


def get_services() -> EntityServiceProtocol:
    global entity_service
    if entity_service is None:
        entity_service = cast(EntityServiceProtocol, get_entity_service())
    return entity_service


class CategoryCreateRequest(BaseModel):
    name: str = Field(..., description="Name of the category")
    description: Optional[str] = Field(
        default=None, description="Description of the category"
    )


class CategoryUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, description="Name of the category")
    description: Optional[str] = Field(
        default=None, description="Description of the category"
    )


@categories_bp.route("", methods=["GET"])
async def get_categories() -> ResponseReturnValue:
    """Get all categories"""
    try:
        service = get_services()
        entities = await service.find_all(entity_class="Category", entity_version="1")

        categories = []
        for entity in entities:
            category_data = {
                "id": entity.get_id(),
                "name": entity.data.get("name"),
                "description": entity.data.get("description"),
                "status": _map_state_to_status(entity.get_state()),
            }
            categories.append(category_data)

        return jsonify(categories), 200

    except Exception as e:
        logger.exception("Error getting categories: %s", str(e))
        return jsonify({"error": str(e)}), 500


@categories_bp.route("/<category_id>", methods=["GET"])
async def get_category(category_id: str) -> ResponseReturnValue:
    """Get category by ID"""
    try:
        service = get_services()
        response = await service.get_by_id(
            entity_id=category_id, entity_class="Category", entity_version="1"
        )

        if not response:
            return jsonify({"error": "Category not found"}), 404

        category_data = {
            "id": response.metadata.id,
            "name": response.data.get("name"),
            "description": response.data.get("description"),
            "status": _map_state_to_status(response.metadata.state),
        }

        return jsonify(category_data), 200

    except Exception as e:
        logger.exception("Error getting category %s: %s", category_id, str(e))
        return jsonify({"error": str(e)}), 500


@categories_bp.route("", methods=["POST"])
@validate_request(CategoryCreateRequest)
async def create_category(data: CategoryCreateRequest) -> ResponseReturnValue:
    """Create a new category"""
    try:
        service = get_services()
        entity_data: Dict[str, Any] = data.model_dump()

        response = await service.save(
            entity=entity_data, entity_class="Category", entity_version="1"
        )

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "name": entity_data.get("name"),
                    "status": _map_state_to_status(response.metadata.state),
                    "message": "Category created successfully",
                }
            ),
            201,
        )

    except Exception as e:
        logger.exception("Error creating category: %s", str(e))
        return jsonify({"error": str(e)}), 500


@categories_bp.route("/<category_id>", methods=["PUT"])
@validate_request(CategoryUpdateRequest)
async def update_category(
    category_id: str, data: CategoryUpdateRequest
) -> ResponseReturnValue:
    """Update a category"""
    try:
        service = get_services()
        transition: Optional[str] = request.args.get("transitionName")

        entity_data: Dict[str, Any] = {
            k: v for k, v in data.model_dump(exclude_none=True).items()
        }

        response = await service.update(
            entity_id=category_id,
            entity=entity_data,
            entity_class="Category",
            transition=transition,
            entity_version="1",
        )

        return (
            jsonify(
                {
                    "id": response.metadata.id,
                    "name": entity_data.get("name", ""),
                    "status": _map_state_to_status(response.metadata.state),
                    "message": "Category updated successfully",
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Error updating category %s: %s", category_id, str(e))
        return jsonify({"error": str(e)}), 500


def _map_state_to_status(state: str) -> str:
    """Map entity state to API status"""
    state_mapping = {"active": "ACTIVE", "inactive": "INACTIVE"}
    return state_mapping.get(state, "UNKNOWN")
