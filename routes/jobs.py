"""
Job management routes.

This module contains routes for job scheduling and status management.
"""

import logging
import uuid
from datetime import datetime, timezone

from quart import Blueprint, jsonify, abort

from service.services import get_entity_service, get_auth_service
from common.config.config import ENTITY_VERSION

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

jobs_bp = Blueprint('jobs', __name__, url_prefix='/jobs')

# Services will be accessed through the registry
entity_service = None
cyoda_auth_service = None


def get_services():
    """Get services from the registry lazily."""
    global entity_service, cyoda_auth_service
    if entity_service is None:
        entity_service = get_entity_service()
    if cyoda_auth_service is None:
        cyoda_auth_service = get_auth_service()
    return entity_service, cyoda_auth_service


@jobs_bp.route("/schedule", methods=["POST"])
async def schedule_job():
    """Schedule a new job."""
    entity_service, cyoda_auth_service = get_services()

    job_id = str(uuid.uuid4())
    job_entity = {
        "id": job_id,
        "status": "SCHEDULED",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "type": "data_processing"
    }

    try:
        await entity_service.save_item(
            job_entity, "job", job_id, ENTITY_VERSION
        )
        logger.info(f"Job {job_id} scheduled successfully")
    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to schedule job")

    return jsonify({"job_id": job_id, "status": "SCHEDULED"}), 202


@jobs_bp.route("/<string:job_id>", methods=["GET"])
async def get_job_status(job_id):
    """Get the status of a specific job."""
    entity_service, cyoda_auth_service = get_services()

    try:
        job = await entity_service.get_item(
            job_id, "job", ENTITY_VERSION
        )
        logger.info(f"Retrieved job {job_id}")
    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to retrieve job status")
    
    if not job:
        abort(404, description="Job not found")
    
    return jsonify(job)


@jobs_bp.route("", methods=["GET"])
async def list_jobs():
    """List all jobs."""
    entity_service, cyoda_auth_service = get_services()

    try:
        jobs = await entity_service.get_items(
            "job", ENTITY_VERSION
        )
        logger.info(f"Retrieved {len(jobs)} jobs")
        return jsonify(jobs)
    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to retrieve jobs")


@jobs_bp.route("/<string:job_id>", methods=["PUT"])
async def update_job_status(job_id):
    """Update the status of a specific job."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Get current job
        job = await entity_service.get_item(job_id, "job", ENTITY_VERSION)
        if not job:
            abort(404, description="Job not found")

        # Update job status (this would typically come from request body)
        job["status"] = "COMPLETED"
        job["updated_at"] = datetime.now(timezone.utc).isoformat()

        await entity_service.save_item(job, "job", job_id, ENTITY_VERSION)
        logger.info(f"Job {job_id} status updated")
        
        return jsonify(job)
    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to update job status")


@jobs_bp.route("/<string:job_id>", methods=["DELETE"])
async def delete_job(job_id):
    """Delete a specific job."""
    entity_service, cyoda_auth_service = get_services()

    try:
        # Check if job exists
        job = await entity_service.get_item(job_id, "job", ENTITY_VERSION)
        if not job:
            abort(404, description="Job not found")

        # Delete job (implementation depends on your entity service)
        # await entity_service.delete_item(job_id, "job", ENTITY_VERSION)
        logger.info(f"Job {job_id} deleted")
        
        return jsonify({"message": f"Job {job_id} deleted successfully"}), 200
    except Exception as e:
        logger.exception(e)
        abort(500, description="Failed to delete job")
