#!/usr/bin/env python3
"""
Application launcher script.

This script launches the Cyoda client application from the root directory
to ensure proper module resolution.
"""

import os
import sys

if __name__ == "__main__":
    # Add the current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    # Import and run the application
    from application.app import app

    host = os.getenv("APP_HOST", "127.0.0.1")  # Default to localhost for security
    port = int(os.getenv("APP_PORT", "8000"))
    debug = os.getenv("APP_DEBUG", "false").lower() == "true"

    app.run(use_reloader=False, debug=debug, host=host, port=port)
