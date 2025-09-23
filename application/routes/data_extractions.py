"""
DataExtraction Routes for Pet Store Performance Analysis System

Manages all DataExtraction-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue
from quart_schema import (
    operation_id,
    tag,
    validate,
    validate_querystring,
)

from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

# Import entity and models
from ..entity.data_extraction.version_1.data_extraction import DataExtraction
from ..models import (
    CountResponse,
    DeleteResponse,
    ErrorResponse,
    DataExtractionListResponse,
    DataExtractionResponse,
    DataExtractionSearchResponse,
    DataExtractionQueryParams,
    DataExtractionUpdateQueryParams,
    ExistsResponse,
    SearchRequest,
    TransitionRequest,
    TransitionResponse,
    TransitionsResponse,
    ValidationErrorResponse,
)

# Module-level service proxy
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)

service = _ServiceProxy()
logger = logging.getLogger(__name__)

# Helper to normalize entity data from service
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data

data_extractions_bp = Blueprint("data_extractions", __name__, url_prefix="/api/data-extractions")


@data_extractions_bp.route("", methods=["POST"])
@tag(["data-extractions"])
@operation_id("create_data_extraction")
@validate(
    request=DataExtraction,
    responses={
        201: (DataExtractionResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_data_extraction(data: DataExtraction) -> ResponseReturnValue:
    """Create a new DataExtraction with comprehensive validation"""
    try:
        # Convert request to entity data
        entity_data = data.model_dump(by_alias=True)

        # Save the entity
        response = await service.save(
            entity=entity_data,
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        logger.info("Created DataExtraction with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201

    except ValueError as e:
        logger.warning("Validation error creating DataExtraction: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating DataExtraction: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@data_extractions_bp.route("/<entity_id>", methods=["GET"])
@tag(["data-extractions"])
@operation_id("get_data_extraction")
@validate(
    responses={
        200: (DataExtractionResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_data_extraction(entity_id: str) -> ResponseReturnValue:
    """Get DataExtraction by ID with validation"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        if not response:
            return {"error": "DataExtraction not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error getting DataExtraction %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@data_extractions_bp.route("", methods=["GET"])
@validate_querystring(DataExtractionQueryParams)
@tag(["data-extractions"])
@operation_id("list_data_extractions")
@validate(
    responses={
        200: (DataExtractionListResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_data_extractions(query_args: DataExtractionQueryParams) -> ResponseReturnValue:
    """List DataExtractions with optional filtering and validation"""
    try:
        # Build search conditions based on query parameters
        search_conditions: Dict[str, str] = {}

        if query_args.job_type:
            search_conditions["jobType"] = query_args.job_type
        if query_args.execution_status:
            search_conditions["executionStatus"] = query_args.execution_status
        if query_args.state:
            search_conditions["state"] = query_args.state

        # Get entities
        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await service.search(
                entity_class=DataExtraction.ENTITY_NAME,
                condition=condition,
                entity_version=str(DataExtraction.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=DataExtraction.ENTITY_NAME,
                entity_version=str(DataExtraction.ENTITY_VERSION),
            )

        # Convert to list and apply pagination
        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply date filtering if specified
        if query_args.scheduled_after or query_args.scheduled_before:
            filtered_list = []
            for entity in entity_list:
                scheduled_time = entity.get("scheduledTime")
                
                if query_args.scheduled_after and scheduled_time and scheduled_time < query_args.scheduled_after:
                    continue
                if query_args.scheduled_before and scheduled_time and scheduled_time > query_args.scheduled_before:
                    continue
                    
                filtered_list.append(entity)
            entity_list = filtered_list

        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return {"extractions": paginated_entities, "total": len(entity_list)}, 200

    except Exception as e:
        logger.exception("Error listing DataExtractions: %s", str(e))
        return {"error": str(e)}, 500


@data_extractions_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(DataExtractionUpdateQueryParams)
@tag(["data-extractions"])
@operation_id("update_data_extraction")
@validate(
    request=DataExtraction,
    responses={
        200: (DataExtractionResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_data_extraction(
    entity_id: str, data: DataExtraction, query_args: DataExtractionUpdateQueryParams
) -> ResponseReturnValue:
    """Update DataExtraction and optionally trigger workflow transition with validation"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=DataExtraction.ENTITY_NAME,
            transition=transition,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        logger.info("Updated DataExtraction %s", entity_id)
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning("Validation error updating DataExtraction %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error updating DataExtraction %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@data_extractions_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["data-extractions"])
@operation_id("delete_data_extraction")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_data_extraction(entity_id: str) -> ResponseReturnValue:
    """Delete DataExtraction with validation"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        logger.info("Deleted DataExtraction %s", entity_id)
        response = DeleteResponse(
            success=True,
            message="DataExtraction deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error deleting DataExtraction %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@data_extractions_bp.route("/search", methods=["POST"])
@tag(["data-extractions"])
@operation_id("search_data_extractions")
@validate(
    request=SearchRequest,
    responses={
        200: (DataExtractionSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_data_extractions(data: SearchRequest) -> ResponseReturnValue:
    """Search DataExtractions using field-value search with validation"""
    try:
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=DataExtraction.ENTITY_NAME,
            condition=search_request,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"extractions": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching DataExtractions: %s", str(e))
        return {"error": str(e)}, 500


@data_extractions_bp.route("/count", methods=["GET"])
@tag(["data-extractions"])
@operation_id("count_data_extractions")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_data_extractions() -> ResponseReturnValue:
    """Count total number of DataExtractions"""
    try:
        count = await service.count(
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        response = CountResponse(count=count)
        return response.model_dump(), 200

    except Exception as e:
        logger.exception("Error counting DataExtractions: %s", str(e))
        return {"error": str(e)}, 500


@data_extractions_bp.route("/<entity_id>/trigger", methods=["POST"])
@tag(["data-extractions"])
@operation_id("trigger_data_extraction")
@validate(
    responses={
        200: (DataExtractionResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def trigger_data_extraction(entity_id: str) -> ResponseReturnValue:
    """Manually trigger a data extraction job"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        # Get current entity
        current_entity = await service.get_by_id(
            entity_id=entity_id,
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        if not current_entity:
            return {"error": "DataExtraction not found", "code": "NOT_FOUND"}, 404

        # Trigger the execute transition
        response = await service.execute_transition(
            entity_id=entity_id,
            transition="execute",
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        logger.info("Triggered DataExtraction %s", entity_id)
        return _to_entity_dict(response.data), 200

    except Exception as e:
        logger.exception("Error triggering DataExtraction %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
