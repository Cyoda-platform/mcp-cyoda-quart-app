import asyncio
import logging

from quart import Quart
from quart_schema import QuartSchema, ResponseSchemaValidationError, hide

from service.services import initialize_services, get_grpc_client
from common.exception.exception_handler import register_error_handlers
# Import blueprints for different route groups
from routes import jobs_bp, laureates_bp, subscribers_bp, health_bp, system_bp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Quart(__name__)

QuartSchema(app,
            info={"title": "Cyoda Client API", "version": "0.1.0"},
            tags=[{"name": "Cyoda Client", "description": "Cloud Client API: prototype"}],
            security=[{"bearerAuth": []}],
            security_schemes={
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                }
            })

# Register blueprints
app.register_blueprint(jobs_bp)
app.register_blueprint(laureates_bp)
app.register_blueprint(subscribers_bp)
app.register_blueprint(health_bp)
app.register_blueprint(system_bp)



# Register error handlers for custom and generic exceptions
@app.errorhandler(ResponseSchemaValidationError)
async def handle_response_validation_error():
    return {"error": "VALIDATION"}, 500

register_error_handlers(app)

@app.route("/favicon.ico")
@hide
def favicon():
    return "", 200
# Startup tasks: initialize services and start the GRPC stream in the background
@app.before_serving
async def startup():
    # Initialize services with centralized configuration
    import asyncio
    from service.config import get_service_config, validate_configuration

    # Validate configuration and log any issues
    validation = validate_configuration()
    if not validation['valid']:
        logger.error("Service configuration validation failed!")
        raise RuntimeError("Invalid service configuration")

    # Initialize services with validated configuration
    config = get_service_config()
    logger.info("Initializing services at application startup...")
    initialize_services(config)
    logger.info("All services initialized successfully at startup")

    # Get the gRPC client and start the stream
    grpc_client = get_grpc_client()
    app.background_task = asyncio.create_task(grpc_client.grpc_stream())

# Shutdown tasks: cancel the background tasks when shutting down
@app.after_serving
async def shutdown():
    """Cleanup tasks on shutdown."""
    logger.info("Shutting down application...")

    # Cancel the background gRPC stream task
    if hasattr(app, 'background_task'):
        app.background_task.cancel()
        try:
            await app.background_task
        except asyncio.CancelledError:
            pass

    logger.info("Application shutdown complete")


# Middleware to add CORS headers to every response
@app.before_serving
async def add_cors_headers():
    @app.after_request
    async def apply_cors(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response


if __name__ == "__main__":
    app.run(use_reloader=False, debug=True, host="0.0.0.0", port=8000)
