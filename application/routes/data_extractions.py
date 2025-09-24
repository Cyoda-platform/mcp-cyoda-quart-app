"""
DataExtraction Routes for Product Performance Analysis and Reporting System

Manages all DataExtraction-related API endpoints including CRUD operations
and workflow transitions for data extraction from Pet Store API.
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
    status: Optional[str] = Field(None, description="Filter by extraction status")
    extraction_type: Optional[str] = Field(
        None, description="Filter by extraction type"
    )
    state: Optional[str] = Field(None, description="Filter by workflow state")
    offset: int = Field(0, description="Pagination offset")
    limit: int = Field(50, description="Pagination limit")


class DataExtractionUpdateQueryParams(BaseModel):
    transition: Optional[str] = Field(
        None, description="Workflow transition to trigger"
    )


class DataExtractionResponse(BaseModel):
    success: bool = Field(True, description="Operation success status")
    data: Dict[str, Any] = Field(..., description="DataExtraction data")


class DataExtractionListResponse(BaseModel):
    extractions: list[Dict[str, Any]] = Field(
        ..., description="List of data extractions"
    )
    total: int = Field(..., description="Total number of data extractions")


class DeleteResponse(BaseModel):
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    entity_id: str = Field(..., description="Deleted entity ID")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class ValidationErrorResponse(BaseModel):
    error: str = Field(..., description="Validation error message")
    code: str = Field("VALIDATION_ERROR", description="Error code")


# Service proxy
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()


# Helper function
def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


# Blueprint
data_extractions_bp = Blueprint(
    "data_extractions", __name__, url_prefix="/api/data-extractions"
)


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
    """Create a new DataExtraction entity"""
    try:
        entity_data = data.model_dump(by_alias=True)

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
    """Get DataExtraction by ID"""
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
async def list_data_extractions(
    query_args: DataExtractionQueryParams,
) -> ResponseReturnValue:
    """List DataExtractions with optional filtering"""
    try:
        search_conditions: Dict[str, str] = {}

        if query_args.status:
            search_conditions["status"] = query_args.status
        if query_args.extraction_type:
            search_conditions["extractionType"] = query_args.extraction_type
        if query_args.state:
            search_conditions["state"] = query_args.state

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

        entity_list = [_to_entity_dict(r.data) for r in entities]

        # Apply pagination
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
    """Update DataExtraction and optionally trigger workflow transition"""
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


@data_extractions_bp.route("/count", methods=["GET"])
@tag(["data-extractions"])
@operation_id("count_data_extractions")
async def count_data_extractions() -> ResponseReturnValue:
    """Count total number of DataExtractions"""
    try:
        count = await service.count(
            entity_class=DataExtraction.ENTITY_NAME,
            entity_version=str(DataExtraction.ENTITY_VERSION),
        )
        return {"count": count}, 200
    except Exception as e:
        logger.exception("Error counting DataExtractions: %s", str(e))
        return {"error": str(e)}, 500
