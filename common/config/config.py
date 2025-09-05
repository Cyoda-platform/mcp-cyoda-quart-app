"""
Enhanced configuration module with backward compatibility.

This module provides backward compatibility with the old configuration system
while using the new configuration manager under the hood.
"""

import os
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import new configuration system
try:
    from .manager import get_config_manager, get_config
    _use_new_config = True
    _config_manager = get_config_manager()
except ImportError:
    _use_new_config = False

# Legacy lambda for backward compatibility
get_env = lambda key: os.getenv(key) or (_ for _ in ()).throw(Exception(f"{key} not found"))

CYODA_HOST = get_env("CYODA_HOST")
CYODA_CLIENT_ID = get_env("CYODA_CLIENT_ID")
CYODA_CLIENT_SECRET = get_env("CYODA_CLIENT_SECRET")
CYODA_TOKEN_URL = f"https://{CYODA_HOST}/api/oauth/token"
CHAT_ID = os.getenv("CHAT_ID", "cyoda-client")
ENTITY_VERSION = os.getenv("ENTITY_VERSION", "1")
GRPC_PROCESSOR_TAG = os.getenv("GRPC_PROCESSOR_TAG", "cloud_manager_app")
CYODA_AI_URL = os.getenv("CYODA_AI_URL", f"https://{CYODA_HOST}/ai")
CYODA_API_URL = os.getenv("CYODA_API_URL", f"https://{CYODA_HOST}/api")
GRPC_ADDRESS = os.getenv("GRPC_ADDRESS", f"grpc-{CYODA_HOST}")
PROJECT_DIR = os.getenv("PROJECT_DIR", "/tmp")
CHAT_REPOSITORY = os.getenv("CHAT_REPOSITORY", "cyoda")
IMPORT_WORKFLOWS = bool(os.getenv("IMPORT_WORKFLOWS", "true"))

# Constants
CYODA_ENTITY_TYPE_EDGE_MESSAGE = "EDGE_MESSAGE"