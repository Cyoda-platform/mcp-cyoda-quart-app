"""
DataExtraction Routes for Pet Store Performance Analysis System

Manages all DataExtraction-related API endpoints including CRUD operations
and workflow transitions for scheduled data extraction from Pet Store API.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from quart import Blueprint
from quart.typing import ResponseReturnValue
from quart_schema import operation_id, tag, validate, validate_querystring

from application.entity.data_extraction.version_1.data_extraction import DataExtraction
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service

logger = logging.getLogger(__name__)


# Request/Response models
class DataExtractionQueryParams(BaseModel):
    schedule_type: Optional[str] = Field(
        None, alias="scheduleType", description="Filter by schedule type"
    )
    execution_status: Optional[str] = Field(
        None, alias="executionStatus", description="Filter by execution status"
    )
    state: Optional[str] = Field(None, description="Filter by workflow state")
    limit: int = Field(50, description="Maximum number of results", ge=1, le=1000)
    offset: int = Field(0, description="Number of results to skip", ge=0)


class DataExtractionUpdateQueryParams(BaseModel):
    transition: Optional[str] = Field(
        None, description="Workflow transition to execute"
    )


class SearchRequest(BaseModel):
    job_name: Optional[str] = Field(None, alias="jobName")
    schedule_type: Optional[str] = Field(None, alias="scheduleType")
    execution_status: Optional[str] = Field(None, alias="executionStatus")


class ErrorResponse(BaseModel):
    error: str
    code: Optional[str] = None


class DeleteResponse(BaseModel):
    success: bool
    message: str
    entity_id: str


# Helper to normalize entity data
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


# Create blueprint
data_extractions_bp = Blueprint(
    "data_extractions", __name__, url_prefix="/api/data-extractions"
)


@data_extractions_bp.route("", methods=["POST"])
@tag(["data-extractions"])
@operation_id("create_data_extraction")
@validate(
    request=DataExtraction,
    responses={
        201: (Dict[str, Any], None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_data_extraction(data: DataExtraction) -> ResponseReturnValue:
    """Create a new DataExtraction entity"""
    try:
        entity_data = data.model_dump(by_alias=True)

        entity_service = get_entity_service()
        response = await entity_service.save(
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
        200: (Dict[str, Any], None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_data_extraction(entity_id: str) -> ResponseReturnValue:
    """Get DataExtraction by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        entity_service = get_entity_service()
        response = await entity_service.get_by_id(
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
        200: (Dict[str, Any], None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_data_extractions(
    query_args: DataExtractionQueryParams,
) -> ResponseReturnValue:
    """List DataExtractions with optional filtering"""
    try:
        entity_service = get_entity_service()
        search_conditions: Dict[str, str] = {}

        if query_args.schedule_type:
            search_conditions["scheduleType"] = query_args.schedule_type
        if query_args.execution_status:
            search_conditions["executionStatus"] = query_args.execution_status
        if query_args.state:
            search_conditions["state"] = query_args.state

        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()

            entities = await entity_service.search(
                entity_class=DataExtraction.ENTITY_NAME,
                condition=condition,
                entity_version=str(DataExtraction.ENTITY_VERSION),
            )
        else:
            entities = await entity_service.find_all(
                entity_class=DataExtraction.ENTITY_NAME,
                entity_version=str(DataExtraction.ENTITY_VERSION),
            )

        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return {"entities": paginated_entities, "total": len(entity_list)}, 200

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
        200: (Dict[str, Any], None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_data_extraction(
    entity_id: str, data: DataExtraction, query_args: DataExtractionUpdateQueryParams
) -> ResponseReturnValue:
    """Update DataExtraction and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        entity_service = get_entity_service()
        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await entity_service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=DataExtraction.ENTITY_NAME,
            transition=transition,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        logger.info("Updated DataExtraction %s", entity_id)
        return _to_entity_dict(response.data), 200

    except ValueError as e:
        logger.warning(
            "Validation error updating DataExtraction %s: %s", entity_id, str(e)
        )
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
    """Delete DataExtraction"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        entity_service = get_entity_service()
        await entity_service.delete_by_id(
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
        200: (Dict[str, Any], None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_data_extractions(data: SearchRequest) -> ResponseReturnValue:
    """Search DataExtractions using field-value search"""
    try:
        search_data = data.model_dump(by_alias=True, exclude_none=True)

        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        entity_service = get_entity_service()
        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await entity_service.search(
            entity_class=DataExtraction.ENTITY_NAME,
            condition=search_request,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"entities": entities, "total": len(entities)}, 200

    except Exception as e:
        logger.exception("Error searching DataExtractions: %s", str(e))
        return {"error": str(e)}, 500


@data_extractions_bp.route("/<entity_id>/trigger", methods=["POST"])
@tag(["data-extractions"])
@operation_id("trigger_data_extraction")
@validate(
    responses={
        200: (Dict[str, Any], None),
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

        entity_service = get_entity_service()

        # Execute the validate transition to start the extraction process
        response = await entity_service.execute_transition(
            entity_id=entity_id,
            transition="validate",
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )

        logger.info("Triggered data extraction for %s", entity_id)

        return {
            "success": True,
            "message": "Data extraction triggered successfully",
            "entity_id": entity_id,
            "new_state": response.metadata.state,
        }, 200

    except ValueError as e:
        logger.warning("Invalid entity ID %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INVALID_ID"}, 400
    except Exception as e:
        logger.exception("Error triggering data extraction %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500
