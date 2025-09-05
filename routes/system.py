"""
System information and metrics routes.

This module contains routes for system information, metrics, and configuration.
"""

import logging
import os
from datetime import datetime, timezone

from quart import Blueprint, jsonify

from common.config.config import CYODA_TOKEN_URL

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

system_bp = Blueprint('system', __name__)


@system_bp.route('/metrics', methods=['GET'])
async def metrics():
    """
    Metrics endpoint in Prometheus format.
    
    Returns application metrics in Prometheus exposition format.
    """
    try:
        # Placeholder for metrics collection
        # In a real implementation, you would use a metrics library like prometheus_client
        
        metrics_data = """
# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",status="200"} 100
http_requests_total{method="POST",status="200"} 50
http_requests_total{method="GET",status="404"} 5

# HELP http_request_duration_seconds HTTP request duration in seconds
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 80
http_request_duration_seconds_bucket{le="0.5"} 140
http_request_duration_seconds_bucket{le="1.0"} 150
http_request_duration_seconds_bucket{le="+Inf"} 155
http_request_duration_seconds_sum 45.2
http_request_duration_seconds_count 155

# HELP cyoda_entities_total Total number of entities by type
# TYPE cyoda_entities_total gauge
cyoda_entities_total{type="laureate"} 50
cyoda_entities_total{type="subscriber"} 25
cyoda_entities_total{type="job"} 10
"""
        
        return metrics_data, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        
    except Exception as e:
        logger.exception("Metrics export failed")
        return jsonify({
            "error": f"Metrics export failed: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500


@system_bp.route('/metrics/summary', methods=['GET'])
async def metrics_summary():
    """
    Metrics summary endpoint in JSON format.
    
    Returns a summary of application metrics in JSON format.
    """
    try:
        # Placeholder metrics summary
        # In a real implementation, this would collect actual metrics
        
        summary = {
            "http_requests": {
                "total": 155,
                "success_rate": 0.97,
                "average_duration_ms": 291.6
            },
            "entities": {
                "laureates": 50,
                "subscribers": 25,
                "jobs": 10,
                "total": 85
            },
            "system": {
                "uptime_seconds": 3600,
                "memory_usage_mb": 256,
                "cpu_usage_percent": 15.5
            },
            "mcp": {
                "tools_available": 10,
                "tools_called": 25,
                "success_rate": 0.96
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return jsonify(summary), 200
        
    except Exception as e:
        logger.exception("Metrics summary failed")
        return jsonify({
            "error": f"Metrics summary failed: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500


@system_bp.route('/info', methods=['GET'])
async def system_info():
    """
    System information endpoint.
    
    Returns comprehensive system and application information.
    """
    try:
        import os
        import sys
        import platform
        
        # Basic system information
        system_info = {
            "application": {
                "name": "Cyoda Client Template",
                "version": "1.0.0",
                "environment": os.getenv("ENVIRONMENT", "development"),
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": platform.platform()
            },
            "configuration": {
                "entity_version": os.getenv("ENTITY_VERSION", "1.0"),
                "chat_repository": os.getenv("CHAT_REPOSITORY", "cyoda"),
                "cyoda_client_configured": bool(os.getenv("CYODA_CLIENT_ID")),
                "debug_mode": os.getenv("DEBUG", "false").lower() == "true"
            },
            "runtime": {
                "process_id": os.getpid(),
                "working_directory": os.getcwd(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        
        # Add optional system metrics if psutil is available
        try:
            import psutil
            process = psutil.Process()
            
            system_info["system_metrics"] = {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": psutil.disk_usage('/').percent,
                "process_memory_mb": process.memory_info().rss / 1024 / 1024,
                "process_cpu_percent": process.cpu_percent(),
                "process_create_time": process.create_time(),
                "open_files": len(process.open_files()),
                "num_threads": process.num_threads()
            }
        except ImportError:
            logger.info("psutil not available, skipping system metrics")
        
        return jsonify(system_info), 200
        
    except Exception as e:
        logger.exception("System info failed")
        return jsonify({
            "error": f"System info failed: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500


@system_bp.route('/config', methods=['GET'])
async def get_configuration():
    """
    Get application configuration (non-sensitive values only).
    
    Returns current application configuration excluding sensitive information.
    """
    try:
        import os
        
        # Safe configuration values (no secrets)
        config = {
            "application": {
                "name": "Cyoda Client Template",
                "version": "1.0.0",
                "environment": os.getenv("ENVIRONMENT", "development")
            },
            "cyoda": {
                "entity_version": os.getenv("ENTITY_VERSION", "1.0"),
                "chat_repository": os.getenv("CHAT_REPOSITORY", "cyoda"),
                "client_id_configured": bool(os.getenv("CYODA_CLIENT_ID")),
                "client_secret_configured": bool(os.getenv("CYODA_CLIENT_SECRET")),
                "token_url": CYODA_TOKEN_URL
            },
            "features": {
                "mcp_enabled": True,
                "health_checks_enabled": True,
                "metrics_enabled": True
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return jsonify(config), 200
        
    except Exception as e:
        logger.exception("Configuration retrieval failed")
        return jsonify({
            "error": f"Configuration retrieval failed: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500


@system_bp.route('/version', methods=['GET'])
async def get_version():
    """
    Get application version information.
    
    Returns version and build information.
    """
    try:
        import sys
        import platform
        
        version_info = {
            "application": {
                "name": "Cyoda Client Template",
                "version": "1.0.0",
                "build_date": "2025-09-03",
                "git_commit": os.getenv("GIT_COMMIT", "unknown")
            },
            "runtime": {
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "python_implementation": platform.python_implementation(),
                "platform": platform.platform(),
                "architecture": platform.architecture()[0]
            },
            "dependencies": {
                "quart": "latest",
                "fastmcp": "2.12.0",
                "httpx": "latest"
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return jsonify(version_info), 200
        
    except Exception as e:
        logger.exception("Version info failed")
        return jsonify({
            "error": f"Version info failed: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500


@system_bp.route('/status', methods=['GET'])
async def system_status():
    """
    Overall system status endpoint.
    
    Returns a comprehensive status of all system components.
    """
    try:
        from service.services import get_entity_service, get_auth_service
        from cyoda_mcp.server import get_mcp_server
        
        # Check service availability
        entity_service = get_entity_service()
        auth_service = get_auth_service()
        mcp_server = get_mcp_server()
        
        status = {
            "overall_status": "healthy",
            "components": {
                "entity_service": {
                    "status": "healthy" if entity_service else "unhealthy",
                    "available": bool(entity_service)
                },
                "auth_service": {
                    "status": "healthy" if auth_service else "unhealthy",
                    "available": bool(auth_service)
                },
                "mcp_server": {
                    "status": "healthy" if mcp_server else "unhealthy",
                    "available": bool(mcp_server),
                    "name": mcp_server.name if mcp_server else None
                }
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Determine overall status
        unhealthy_components = [
            name for name, component in status["components"].items()
            if component["status"] != "healthy"
        ]
        
        if unhealthy_components:
            status["overall_status"] = "degraded" if len(unhealthy_components) < len(status["components"]) else "unhealthy"
            status["unhealthy_components"] = unhealthy_components
        
        status_code = 200 if status["overall_status"] == "healthy" else 503
        return jsonify(status), status_code
        
    except Exception as e:
        logger.exception("System status check failed")
        return jsonify({
            "overall_status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 503
