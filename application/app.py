"""
Purrfect Pets API Application.

Main application file that registers all blueprints and configures the Quart app.
"""

import logging
import os

from quart import Quart, jsonify

from application.routes.appointment_routes import appointment_bp
from application.routes.medical_record_routes import medical_record_bp
from application.routes.owner_routes import owner_bp
# Import all blueprints
from application.routes.pet_routes import pet_bp
from application.routes.veterinarian_routes import veterinarian_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def create_app():
    """Create and configure the Quart application."""
    app = Quart(__name__)

    # Configure app
    app.config["DEBUG"] = os.getenv("DEBUG", "false").lower() == "true"
    app.config["TESTING"] = os.getenv("TESTING", "false").lower() == "true"

    # Register blueprints
    app.register_blueprint(pet_bp)
    app.register_blueprint(owner_bp)
    app.register_blueprint(veterinarian_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(medical_record_bp)

    # Health check endpoint
    @app.route("/health", methods=["GET"])
    async def health_check():
        """Health check endpoint."""
        return jsonify(
            {"status": "healthy", "service": "Purrfect Pets API", "version": "1.0.0"}
        )

    # Root endpoint
    @app.route("/", methods=["GET"])
    async def root():
        """Root endpoint with API information."""
        return jsonify(
            {
                "message": "Welcome to Purrfect Pets API",
                "version": "1.0.0",
                "endpoints": {
                    "pets": "/pets",
                    "owners": "/owners",
                    "veterinarians": "/veterinarians",
                    "appointments": "/appointments",
                    "medical_records": "/medical-records",
                    "health": "/health",
                },
            }
        )

    # Error handlers
    @app.errorhandler(404)
    async def not_found(error):
        """Handle 404 errors."""
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    async def internal_error(error):
        """Handle 500 errors."""
        logger.exception("Internal server error")
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(400)
    async def bad_request(error):
        """Handle 400 errors."""
        return jsonify({"error": "Bad request"}), 400

    logger.info("Purrfect Pets API application created successfully")

    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    """Run the application."""
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "false").lower() == "true"

    logger.info(f"Starting Purrfect Pets API on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
