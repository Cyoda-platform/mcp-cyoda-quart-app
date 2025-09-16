"""
Application module for the cat fact subscription system.

This module provides the main application configuration and blueprint registration
for the cat fact subscription system.
"""
import logging

from quart import Quart
from quart_schema import QuartSchema

# Import application blueprints
from application.routes import (
    subscriber_bp,
    catfact_bp,
    emaildelivery_bp,
    weeklyschedule_bp,
    reporting_bp
)

logger = logging.getLogger(__name__)


def create_application_blueprints(app: Quart) -> None:
    """
    Register all application blueprints with the main Quart app.
    
    Args:
        app: The main Quart application instance
    """
    # Register subscriber routes
    app.register_blueprint(subscriber_bp)
    logger.info("Registered subscriber routes")
    
    # Register cat fact routes
    app.register_blueprint(catfact_bp)
    logger.info("Registered cat fact routes")
    
    # Register email delivery routes
    app.register_blueprint(emaildelivery_bp)
    logger.info("Registered email delivery routes")
    
    # Register weekly schedule routes
    app.register_blueprint(weeklyschedule_bp)
    logger.info("Registered weekly schedule routes")
    
    # Register reporting routes
    app.register_blueprint(reporting_bp)
    logger.info("Registered reporting routes")
    
    logger.info("All application blueprints registered successfully")


def configure_application_schema(app: Quart) -> None:
    """
    Configure OpenAPI schema for application routes.
    
    Args:
        app: The main Quart application instance
    """
    # Add application-specific tags to the schema
    if hasattr(app, 'quart_schema'):
        # Add tags for application endpoints
        app_tags = [
            {"name": "Subscribers", "description": "Subscriber management operations"},
            {"name": "Cat Facts", "description": "Cat fact retrieval and distribution operations"},
            {"name": "Email Deliveries", "description": "Email delivery tracking operations"},
            {"name": "Weekly Schedules", "description": "Weekly schedule management operations"},
            {"name": "Reports", "description": "Reporting and analytics operations"}
        ]
        
        # Extend existing tags
        if hasattr(app.quart_schema, 'tags'):
            app.quart_schema.tags.extend(app_tags)
        
        logger.info("Application schema configuration completed")


def initialize_application_components(app: Quart) -> None:
    """
    Initialize all application components.
    
    Args:
        app: The main Quart application instance
    """
    # Register blueprints
    create_application_blueprints(app)
    
    # Configure schema
    configure_application_schema(app)
    
    logger.info("Application components initialized successfully")
