"""
Employee Routes for Cyoda Client Application

Manages all Employee-related API endpoints including CRUD operations
and workflow transitions as specified in functional requirements.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from quart import Blueprint, jsonify
from quart.typing import ResponseReturnValue
from quart_schema import (
    operation_id,
    tag,
    validate,
    validate_querystring,
)

# Import entity and models
from application.entity.employee.version_1.employee import Employee
from application.models.request_models import (
    EmployeeQueryParams,
    EmployeeUpdateQueryParams,
    SearchRequest,
)
from application.models.response_models import (
    CountResponse,
    DeleteResponse,
    EmployeeListResponse,
    EmployeeResponse,
    EmployeeSearchResponse,
    ErrorResponse,
    ValidationErrorResponse,
)
from common.service.entity_service import SearchConditionRequest
from services.services import get_entity_service


# Module-level service instance
class _ServiceProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_entity_service(), name)


service = _ServiceProxy()
logger = logging.getLogger(__name__)


def _to_entity_dict(data: Any) -> Dict[str, Any]:
    return data.model_dump(by_alias=True) if hasattr(data, "model_dump") else data


employees_bp = Blueprint("employees", __name__, url_prefix="/api/employees")


@employees_bp.route("", methods=["POST"])
@tag(["employees"])
@operation_id("create_employee")
@validate(
    request=Employee,
    responses={
        201: (EmployeeResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def create_employee(data: Employee) -> ResponseReturnValue:
    """Create a new Employee"""
    try:
        entity_data = data.model_dump(by_alias=True)
        response = await service.save(
            entity=entity_data,
            entity_class=Employee.ENTITY_NAME,
            entity_version=str(Employee.ENTITY_VERSION),
        )
        logger.info("Created Employee with ID: %s", response.metadata.id)
        return _to_entity_dict(response.data), 201
    except ValueError as e:
        logger.warning("Validation error creating Employee: %s", str(e))
        return {"error": str(e), "code": "VALIDATION_ERROR"}, 400
    except Exception as e:
        logger.exception("Error creating Employee: %s", str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@employees_bp.route("/<entity_id>", methods=["GET"])
@tag(["employees"])
@operation_id("get_employee")
@validate(
    responses={
        200: (EmployeeResponse, None),
        404: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def get_employee(entity_id: str) -> ResponseReturnValue:
    """Get Employee by ID"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        response = await service.get_by_id(
            entity_id=entity_id,
            entity_class=Employee.ENTITY_NAME,
            entity_version=str(Employee.ENTITY_VERSION),
        )

        if not response:
            return {"error": "Employee not found", "code": "NOT_FOUND"}, 404

        return _to_entity_dict(response.data), 200
    except Exception as e:
        logger.exception("Error getting Employee %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@employees_bp.route("", methods=["GET"])
@validate_querystring(EmployeeQueryParams)
@tag(["employees"])
@operation_id("list_employees")
@validate(
    responses={
        200: (EmployeeListResponse, None),
        500: (ErrorResponse, None),
    }
)
async def list_employees(query_args: EmployeeQueryParams) -> ResponseReturnValue:
    """List Employees with optional filtering"""
    try:
        search_conditions: Dict[str, str] = {}

        if query_args.employee_id:
            search_conditions["employee_id"] = query_args.employee_id
        if query_args.email:
            search_conditions["email"] = query_args.email
        if query_args.position_id:
            search_conditions["position_id"] = query_args.position_id
        if query_args.department:
            search_conditions["department"] = query_args.department
        if query_args.is_active is not None:
            search_conditions["is_active"] = str(query_args.is_active).lower()
        if query_args.state:
            search_conditions["state"] = query_args.state

        if search_conditions:
            builder = SearchConditionRequest.builder()
            for field, value in search_conditions.items():
                builder.equals(field, value)
            condition = builder.build()
            entities = await service.search(
                entity_class=Employee.ENTITY_NAME,
                condition=condition,
                entity_version=str(Employee.ENTITY_VERSION),
            )
        else:
            entities = await service.find_all(
                entity_class=Employee.ENTITY_NAME,
                entity_version=str(Employee.ENTITY_VERSION),
            )

        entity_list = [_to_entity_dict(r.data) for r in entities]
        start = query_args.offset
        end = start + query_args.limit
        paginated_entities = entity_list[start:end]

        return jsonify({"entities": paginated_entities, "total": len(entity_list)}), 200
    except Exception as e:
        logger.exception("Error listing Employees: %s", str(e))
        return jsonify({"error": str(e)}), 500


@employees_bp.route("/<entity_id>", methods=["PUT"])
@validate_querystring(EmployeeUpdateQueryParams)
@tag(["employees"])
@operation_id("update_employee")
@validate(
    request=Employee,
    responses={
        200: (EmployeeResponse, None),
        404: (ErrorResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def update_employee(
    entity_id: str, data: Employee, query_args: EmployeeUpdateQueryParams
) -> ResponseReturnValue:
    """Update Employee and optionally trigger workflow transition"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        transition: Optional[str] = query_args.transition
        entity_data: Dict[str, Any] = data.model_dump(by_alias=True)

        response = await service.update(
            entity_id=entity_id,
            entity=entity_data,
            entity_class=Employee.ENTITY_NAME,
            transition=transition,
            entity_version=str(Employee.ENTITY_VERSION),
        )

        logger.info("Updated Employee %s", entity_id)
        return jsonify(_to_entity_dict(response.data)), 200
    except ValueError as e:
        logger.warning("Validation error updating Employee %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "VALIDATION_ERROR"}), 400
    except Exception as e:
        logger.exception("Error updating Employee %s: %s", entity_id, str(e))
        return jsonify({"error": str(e), "code": "INTERNAL_ERROR"}), 500


@employees_bp.route("/<entity_id>", methods=["DELETE"])
@tag(["employees"])
@operation_id("delete_employee")
@validate(
    responses={
        200: (DeleteResponse, None),
        404: (ErrorResponse, None),
        400: (ErrorResponse, None),
        500: (ErrorResponse, None),
    }
)
async def delete_employee(entity_id: str) -> ResponseReturnValue:
    """Delete Employee"""
    try:
        if not entity_id or len(entity_id.strip()) == 0:
            return {"error": "Entity ID is required", "code": "INVALID_ID"}, 400

        await service.delete_by_id(
            entity_id=entity_id,
            entity_class=Employee.ENTITY_NAME,
            entity_version=str(Employee.ENTITY_VERSION),
        )

        logger.info("Deleted Employee %s", entity_id)
        response = DeleteResponse(
            success=True,
            message="Employee deleted successfully",
            entity_id=entity_id,
        )
        return response.model_dump(), 200
    except Exception as e:
        logger.exception("Error deleting Employee %s: %s", entity_id, str(e))
        return {"error": str(e), "code": "INTERNAL_ERROR"}, 500


@employees_bp.route("/count", methods=["GET"])
@tag(["employees"])
@operation_id("count_employees")
@validate(responses={200: (CountResponse, None), 500: (ErrorResponse, None)})
async def count_entities() -> ResponseReturnValue:
    """Count total number of Employees"""
    try:
        count = await service.count(
            entity_class=Employee.ENTITY_NAME,
            entity_version=str(Employee.ENTITY_VERSION),
        )
        response = CountResponse(count=count)
        return jsonify(response.model_dump()), 200
    except Exception as e:
        logger.exception("Error counting Employees: %s", str(e))
        return jsonify({"error": str(e)}), 500


@employees_bp.route("/search", methods=["POST"])
@tag(["employees"])
@operation_id("search_employees")
@validate(
    request=SearchRequest,
    responses={
        200: (EmployeeSearchResponse, None),
        400: (ValidationErrorResponse, None),
        500: (ErrorResponse, None),
    },
)
async def search_entities(data: SearchRequest) -> ResponseReturnValue:
    """Search Employees"""
    try:
        search_data = data.model_dump(by_alias=True, exclude_none=True)
        if not search_data:
            return {"error": "Search conditions required", "code": "EMPTY_SEARCH"}, 400

        builder = SearchConditionRequest.builder()
        for field, value in search_data.items():
            builder.equals(field, value)

        search_request = builder.build()
        results = await service.search(
            entity_class=Employee.ENTITY_NAME,
            condition=search_request,
            entity_version=str(Employee.ENTITY_VERSION),
        )

        entities = [_to_entity_dict(r.data) for r in results]
        return {"entities": entities, "total": len(entities)}, 200
    except Exception as e:
        logger.exception("Error searching Employees: %s", str(e))
        return {"error": str(e)}, 500
