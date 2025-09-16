"""
Customer Routes for Purrfect Pets API

RESTful API endpoints for customer management operations.
Routes are thin proxies to EntityService with minimal business logic.
"""

import logging
from typing import Any, Dict, List, Optional

from quart import Blueprint, jsonify, request
from quart.typing import ResponseReturnValue

from application.entity.customer.version_1.customer import Customer
from services.services import get_entity_service

# Create blueprint for customer routes
customers_bp = Blueprint("customers", __name__, url_prefix="/api/customers")
logger = logging.getLogger(__name__)


@customers_bp.route("", methods=["GET"])
async def get_customers() -> ResponseReturnValue:
    """Get all customers with optional filtering."""
    try:
        entity_service = get_entity_service()
        
        # Get query parameters
        state = request.args.get("state")
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
        
        # Build filter criteria
        filters = {}
        if state:
            filters["state"] = state
        
        # Get customers from entity service
        response = await entity_service.get_all(
            entity_class=Customer.ENTITY_NAME,
            entity_version=str(Customer.ENTITY_VERSION),
            filters=filters,
            limit=limit,
            offset=offset,
        )
        
        # Convert to API response format
        customers = []
        for customer_data in response.data:
            customer = Customer(**customer_data)
            customers.append(customer.to_api_response())
        
        return jsonify({
            "customers": customers,
            "total": len(customers),
            "limit": limit,
            "offset": offset
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting customers: {str(e)}")
        return jsonify({"error": "Failed to retrieve customers"}), 500


@customers_bp.route("/<customer_id>", methods=["GET"])
async def get_customer(customer_id: str) -> ResponseReturnValue:
    """Get a specific customer by ID."""
    try:
        entity_service = get_entity_service()
        
        response = await entity_service.get_by_id(
            entity_id=customer_id,
            entity_class=Customer.ENTITY_NAME,
            entity_version=str(Customer.ENTITY_VERSION),
        )
        
        if not response:
            return jsonify({"error": "Customer not found"}), 404
        
        customer = Customer(**response.data)
        return jsonify(customer.to_api_response()), 200
        
    except Exception as e:
        logger.error(f"Error getting customer {customer_id}: {str(e)}")
        return jsonify({"error": "Failed to retrieve customer"}), 500


@customers_bp.route("", methods=["POST"])
async def create_customer() -> ResponseReturnValue:
    """Create a new customer."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Create customer entity
        customer = Customer(**data)
        
        # Save through entity service with registration transition
        response = await entity_service.save(
            entity=customer.model_dump(by_alias=True),
            entity_class=Customer.ENTITY_NAME,
            entity_version=str(Customer.ENTITY_VERSION),
            transition="transition_to_registered",
        )
        
        # Return created customer
        created_customer = Customer(**response.data)
        return jsonify(created_customer.to_api_response()), 201
        
    except ValueError as e:
        logger.warning(f"Validation error creating customer: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating customer: {str(e)}")
        return jsonify({"error": "Failed to create customer"}), 500


@customers_bp.route("/<customer_id>", methods=["PUT"])
async def update_customer(customer_id: str) -> ResponseReturnValue:
    """Update an existing customer."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Get transition if provided
        transition = data.pop("transition", None)
        
        # Update customer through entity service
        response = await entity_service.update(
            entity_id=customer_id,
            entity_data=data,
            entity_class=Customer.ENTITY_NAME,
            entity_version=str(Customer.ENTITY_VERSION),
            transition=transition,
        )
        
        if not response:
            return jsonify({"error": "Customer not found"}), 404
        
        # Return updated customer
        updated_customer = Customer(**response.data)
        return jsonify(updated_customer.to_api_response()), 200
        
    except ValueError as e:
        logger.warning(f"Validation error updating customer {customer_id}: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating customer {customer_id}: {str(e)}")
        return jsonify({"error": "Failed to update customer"}), 500


@customers_bp.route("/<customer_id>", methods=["DELETE"])
async def delete_customer(customer_id: str) -> ResponseReturnValue:
    """Delete a customer."""
    try:
        entity_service = get_entity_service()
        
        success = await entity_service.delete(
            entity_id=customer_id,
            entity_class=Customer.ENTITY_NAME,
            entity_version=str(Customer.ENTITY_VERSION),
        )
        
        if not success:
            return jsonify({"error": "Customer not found"}), 404
        
        return jsonify({"message": "Customer deleted successfully"}), 200
        
    except Exception as e:
        logger.error(f"Error deleting customer {customer_id}: {str(e)}")
        return jsonify({"error": "Failed to delete customer"}), 500


@customers_bp.route("/<customer_id>/verify", methods=["POST"])
async def verify_customer(customer_id: str) -> ResponseReturnValue:
    """Verify a customer."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()
        
        verification_documents = data.get("verification_documents", []) if data else []
        
        # Execute verification transition
        response = await entity_service.execute_transition(
            entity_id=customer_id,
            transition="transition_to_verified",
            entity_class=Customer.ENTITY_NAME,
            entity_version=str(Customer.ENTITY_VERSION),
            processor_kwargs={"verification_documents": verification_documents},
        )
        
        if not response:
            return jsonify({"error": "Customer not found or cannot be verified"}), 404
        
        # Return updated customer
        updated_customer = Customer(**response.data)
        return jsonify(updated_customer.to_api_response()), 200
        
    except Exception as e:
        logger.error(f"Error verifying customer {customer_id}: {str(e)}")
        return jsonify({"error": "Failed to verify customer"}), 500


@customers_bp.route("/<customer_id>/approve", methods=["POST"])
async def approve_customer(customer_id: str) -> ResponseReturnValue:
    """Approve a customer for adoptions."""
    try:
        entity_service = get_entity_service()
        
        # Execute approval transition
        response = await entity_service.execute_transition(
            entity_id=customer_id,
            transition="transition_to_approved",
            entity_class=Customer.ENTITY_NAME,
            entity_version=str(Customer.ENTITY_VERSION),
        )
        
        if not response:
            return jsonify({"error": "Customer not found or cannot be approved"}), 404
        
        # Return updated customer
        updated_customer = Customer(**response.data)
        return jsonify(updated_customer.to_api_response()), 200
        
    except Exception as e:
        logger.error(f"Error approving customer {customer_id}: {str(e)}")
        return jsonify({"error": "Failed to approve customer"}), 500


@customers_bp.route("/<customer_id>/suspend", methods=["POST"])
async def suspend_customer(customer_id: str) -> ResponseReturnValue:
    """Suspend a customer."""
    try:
        entity_service = get_entity_service()
        data = await request.get_json()
        
        suspension_reason = data.get("suspension_reason", "Policy violation") if data else "Policy violation"
        
        # Execute suspension transition
        response = await entity_service.execute_transition(
            entity_id=customer_id,
            transition="transition_to_suspended",
            entity_class=Customer.ENTITY_NAME,
            entity_version=str(Customer.ENTITY_VERSION),
            processor_kwargs={"suspension_reason": suspension_reason},
        )
        
        if not response:
            return jsonify({"error": "Customer not found or cannot be suspended"}), 404
        
        # Return updated customer
        updated_customer = Customer(**response.data)
        return jsonify(updated_customer.to_api_response()), 200
        
    except Exception as e:
        logger.error(f"Error suspending customer {customer_id}: {str(e)}")
        return jsonify({"error": "Failed to suspend customer"}), 500
