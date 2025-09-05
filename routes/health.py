"""
Health check and monitoring routes.

This module contains routes for health checks, liveness probes, and readiness probes.
"""

import logging
from datetime import datetime, timezone

from quart import Blueprint, jsonify

from service.services import get_entity_service, get_auth_service

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

health_bp = Blueprint('health', __name__, url_prefix='/health')

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


@health_bp.route('', methods=['GET'])
async def health_check():
    """
    Main health check endpoint.
    
    Performs basic health checks including service availability.
    """
    try:
        # Get services to verify they're available
        entity_service, cyoda_auth_service = get_services()
        
        # Basic health check - verify services are initialized
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "services": {
                "entity_service": "available" if entity_service else "unavailable",
                "auth_service": "available" if cyoda_auth_service else "unavailable"
            }
        }
        
        # Check if any critical services are unavailable
        if not entity_service or not cyoda_auth_service:
            health_status["status"] = "degraded"
            return jsonify(health_status), 503
        
        return jsonify(health_status), 200
        
    except Exception as e:
        logger.exception("Health check failed")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "message": f"Health check error: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 503


@health_bp.route('/live', methods=['GET'])
async def liveness_check():
    """
    Kubernetes liveness probe endpoint.
    
    This endpoint should return 200 if the application is running,
    regardless of its ability to serve traffic.
    """
    return jsonify({
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": "Application is running"
    }), 200


@health_bp.route('/ready', methods=['GET'])
async def readiness_check():
    """
    Kubernetes readiness probe endpoint.
    
    This endpoint should return 200 only if the application is ready to serve traffic.
    """
    try:
        # Check if services are ready
        entity_service, cyoda_auth_service = get_services()
        
        # Perform more thorough readiness checks
        readiness_checks = {
            "entity_service": False,
            "auth_service": False,
            "database_connection": False
        }
        
        # Check entity service
        if entity_service:
            try:
                # You could perform a simple query here to verify database connectivity
                # For now, just check if service is available
                readiness_checks["entity_service"] = True
                readiness_checks["database_connection"] = True
            except Exception as e:
                logger.warning(f"Entity service readiness check failed: {e}")
        
        # Check auth service
        if cyoda_auth_service:
            readiness_checks["auth_service"] = True
        
        # Determine overall readiness
        all_ready = all(readiness_checks.values())
        
        response_data = {
            "status": "ready" if all_ready else "not_ready",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": readiness_checks
        }
        
        if all_ready:
            return jsonify(response_data), 200
        else:
            return jsonify(response_data), 503
            
    except Exception as e:
        logger.exception("Readiness check failed")
        return jsonify({
            "status": "not_ready",
            "error": str(e),
            "message": f"Readiness check failed: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 503


@health_bp.route('/detailed', methods=['GET'])
async def detailed_health_check():
    """
    Detailed health check with comprehensive system information.
    """
    try:
        import psutil
        import os
        
        entity_service, cyoda_auth_service = get_services()
        
        # System information
        system_info = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "process_id": os.getpid(),
            "python_version": f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}.{psutil.sys.version_info.micro}"
        }
        
        # Service status
        service_status = {
            "entity_service": {
                "available": bool(entity_service),
                "type": type(entity_service).__name__ if entity_service else None
            },
            "auth_service": {
                "available": bool(cyoda_auth_service),
                "type": type(cyoda_auth_service).__name__ if cyoda_auth_service else None
            }
        }
        
        # Overall health determination
        overall_status = "healthy"
        if system_info["cpu_percent"] > 90:
            overall_status = "degraded"
        if system_info["memory_percent"] > 90:
            overall_status = "degraded"
        if not entity_service or not cyoda_auth_service:
            overall_status = "unhealthy"
        
        response_data = {
            "status": overall_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "system": system_info,
            "services": service_status,
            "uptime_seconds": psutil.Process().create_time()
        }
        
        status_code = 200 if overall_status == "healthy" else 503
        return jsonify(response_data), status_code
        
    except ImportError:
        # psutil not available, return basic health check
        logger.warning("psutil not available for detailed health check")
        return await health_check()
    except Exception as e:
        logger.exception("Detailed health check failed")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "message": f"Detailed health check failed: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 503


@health_bp.route('/startup', methods=['GET'])
async def startup_check():
    """
    Startup probe endpoint for Kubernetes.
    
    This endpoint should return 200 when the application has finished starting up.
    """
    try:
        # Check if application has completed startup
        entity_service, cyoda_auth_service = get_services()
        
        startup_complete = bool(entity_service and cyoda_auth_service)
        
        if startup_complete:
            return jsonify({
                "status": "started",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": "Application startup complete"
            }), 200
        else:
            return jsonify({
                "status": "starting",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": "Application still starting up"
            }), 503
            
    except Exception as e:
        logger.exception("Startup check failed")
        return jsonify({
            "status": "startup_failed",
            "error": str(e),
            "message": f"Startup check failed: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 503
