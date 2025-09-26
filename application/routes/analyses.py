"""
Analysis Routes for Cyoda Client Application

Manages all Analysis-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import (
    operation_id,
    tag,
    validate,
    validate_querystring,
)

from application.entity.analysis.version_1.analysis import Analysis
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service


# Request/Response Models
class AnalysisQueryParams(BaseModel):
    """Query parameters for Analysis endpoints."""

    comment_id: Optional[str] = Field(default=None, description="Filter by comment ID")
    state: Optional[str] = Field(default=None, description="Filter by workflow state")
    sentiment_label: Optional[str] = Field(
        default=None, description="Filter by sentiment label"
    )
    limit: int = Field(default=50, description="Number of results", ge=1, le=1000)
    offset: int = Field(default=0, description="Pagination offset", ge=0)


class AnalysisUpdateQueryParams(BaseModel):
    """Query parameters for Analysis update operations."""

    transition: Optional[str] = Field(
        default=None, description="Workflow transition to trigger"
    )


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(default=None, description="Error code")


class AnalysisResponse(BaseModel):
    """Response model for single analysis operations."""

    id: str = Field(..., description="Analysis ID")
    status: str = Field(..., description="Operation status")


class AnalysisListResponse(BaseModel):
    """Response model for analysis list operations."""

    analyses: List[Dict[str, Any]] = Field(..., description="List of analyses")
    total: int = Field(..., description="Total number of analyses")
    limit: int = Field(..., description="Applied limit")
    offset: int = Field(..., description="Applied offset")


# Module-level service instance
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()
logger = logging.getLogger(__name__)


# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


analyses_bp = Blueprint("analyses", __name__, url_prefix="/api/analyses")


@analyses_bp.route("", methods=["POST"])
@tag(["analyses"])
@operation_id("create_analysis")
@validate(
    request=Analysis,
    responses={
        201: (AnalysisResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_analysis(data: Analysis) -> ResponseReturnValue:
    """Create a new analysis for a comment"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=Analysis.ENTITY_NAME,
            entity_version=str(Analysis.ENTITY_VERSION),
        )

        logger.info("Created Analysis with ID: %s", response.metadata.id)

        # Return created entity ID and status
        return {"id": response.metadata.id, "status": "created"}, 201

    except ValueError as e:
        logger.warning("Validation error creating Analysis: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Analysis: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@analyses_bp.route("/<entity_id>", methods=["GET"])
@tag(["analyses"])
@operation_id("get_analysis")
@validate(
    responses={
        200: (dict, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_analysis(entity_id: str) -> ResponseReturnValue:
    """Retrieve a specific analysis by ID"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Analysis.ENTITY_NAME,
            entity_version=str(Analysis.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Analysis not found", "code": "NOT_FOUND"}, 404

        # Return the entity with state information
        entity_data = _to_entity_dict(response.data)
        entity_data["meta"] = {"state": response.metadata.state}

        return entity_data, 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting Analysis %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@analyses_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(AnalysisUpdateQueryParams)
@tag(["analyses"])
@operation_id("update_analysis")
@validate(
    request=Analysis,
    responses={
        200: (dict, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_analysis(
    entity_id: str, data: Analysis, query_args: AnalysisUpdateQueryParams
) -> ResponseReturnValue:
    """Update analysis and optionally trigger workflow transition"""
    try:
        # Validate entity ID format
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        # Get transition from query parameters
        transition: Optional[str] = query_args.transition

        # Convert request to entity data
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        # Update the entity
        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Analysis.ENTITY_NAME,
            transition=transition,
            entity_version=str(Analysis.ENTITY_VERSION),
        )

        logger.info("Updated Analysis %s", entity_id)

        # Return response with new state if transition was applied
        result = {"id": response.metadata.id, "status": "updated"}

        if transition:
            result["new_state"] = response.metadata.state

        return result, 200

    except ValueError as e:
        logger.warning("Validation error updating Analysis %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating Analysis %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@analyses_bp.route("", methods=["GET"])
@validate_querystring(AnalysisQueryParams)
@tag(["analyses"])
@operation_id("list_analyses")
@validate(
    responses={
        200: (AnalysisListResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_analyses(query_args: AnalysisQueryParams) -> ResponseReturnValue:
    """List all analyses with optional filtering"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.comment_id:
            search_conditions["comment_id"] = query_args.comment_id

        if query_args.state:
            search_conditions["state"] = query_args.state

        if query_args.sentiment_label:
            search_conditions["sentiment_label"] = query_args.sentiment_label

        # Get entities
        if search_conditions:
            # Build search condition request
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=Analysis.ENTITY_NAME,
                condition=condition,
                entity_version=str(Analysis.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=Analysis.ENTITY_NAME,
                entity_version=str(Analysis.ENTITY_VERSION),
            )

        # Convert entities and add state information
        entity_list = []
        for r in entities:
            entity_data = _to_entity_dict(r.data)
            entity_data["meta"] = {"state": r.metadata.state}
            entity_list.append(entity_data)

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return {
            "analyses": paginated_entities,
            "total": len(entity_list),
            "limit": query_args.limit,
            "offset": query_args.offset,
        }, 200

    except Exception as e:
        logger.exception("Error listing Analyses: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
