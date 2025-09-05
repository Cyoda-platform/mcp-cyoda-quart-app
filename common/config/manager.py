"""
Configuration Management System.

This module provides a comprehensive configuration management system with
validation, environment-specific settings, and type safety.
"""

import os
import json
import logging
from typing import Any, Dict, Optional, Union, Type, TypeVar, List
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import yaml

from common.config.config import CYODA_TOKEN_URL, GRPC_ADDRESS
from common.interfaces.services import IConfigurationProvider

logger = logging.getLogger(__name__)

T = TypeVar('T')


class Environment(Enum):
    """Application environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class ConfigValue:
    """Configuration value with metadata."""
    key: str
    value: Any = None
    default: Any = None
    required: bool = False
    description: str = ""
    env_var: Optional[str] = None
    value_type: Type = str
    validator: Optional[callable] = None


@dataclass
class ConfigSection:
    """Configuration section containing related values."""
    name: str
    description: str = ""
    values: Dict[str, ConfigValue] = field(default_factory=dict)
    
    def add_value(self, config_value: ConfigValue) -> 'ConfigSection':
        """Add a configuration value to this section."""
        self.values[config_value.key] = config_value
        return self
    
    def get_value(self, key: str) -> Optional[ConfigValue]:
        """Get a configuration value by key."""
        return self.values.get(key)


class ConfigurationError(Exception):
    """Configuration related errors."""
    pass


class ConfigurationValidator:
    """Validates configuration values."""
    
    @staticmethod
    def validate_url(value: str) -> bool:
        """Validate URL format."""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(value) is not None
    
    @staticmethod
    def validate_port(value: Union[str, int]) -> bool:
        """Validate port number."""
        try:
            port = int(value)
            return 1 <= port <= 65535
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_email(value: str) -> bool:
        """Validate email format."""
        import re
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return email_pattern.match(value) is not None
    
    @staticmethod
    def validate_non_empty(value: str) -> bool:
        """Validate non-empty string."""
        return isinstance(value, str) and len(value.strip()) > 0


class ConfigurationManager(IConfigurationProvider):
    """Comprehensive configuration manager with validation and environment support."""
    
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        self.environment = environment
        self._sections: Dict[str, ConfigSection] = {}
        self._loaded_files: List[str] = []
        self._env_prefix = "CYODA_"
        self._initialized = False
    
    def initialize(self, config_files: Optional[List[str]] = None) -> 'ConfigurationManager':
        """
        Initialize the configuration manager.
        
        Args:
            config_files: Optional list of configuration files to load
            
        Returns:
            Self for method chaining
        """
        if self._initialized:
            logger.warning("Configuration manager already initialized")
            return self
        
        logger.info(f"Initializing configuration manager for environment: {self.environment.value}")
        
        # Define default configuration
        self._define_default_configuration()
        
        # Load configuration files if provided
        if config_files:
            for config_file in config_files:
                self.load_from_file(config_file)
        
        # Load from environment variables
        self._load_from_environment()
        
        # Validate configuration
        self._validate_configuration()
        
        self._initialized = True
        logger.info("Configuration manager initialized successfully")
        return self
    
    def _define_default_configuration(self):
        """Define default configuration structure."""
        
        # Authentication section
        auth_section = ConfigSection(
            name="authentication",
            description="Authentication and authorization settings"
        )
        
        auth_section.add_value(ConfigValue(
            key="client_id",
            default="default_client",
            required=False,
            description="OAuth client ID",
            env_var="CYODA_CLIENT_ID"
        ))
        
        auth_section.add_value(ConfigValue(
            key="client_secret",
            default="default_secret",
            required=False,
            description="OAuth client secret",
            env_var="CYODA_CLIENT_SECRET"
        ))
        
        auth_section.add_value(ConfigValue(
            key="token_url",
            default=CYODA_TOKEN_URL,
            required=False,
            description="OAuth token endpoint URL",
            env_var=CYODA_TOKEN_URL,
            validator=ConfigurationValidator.validate_url
        ))
        
        self._sections["authentication"] = auth_section
        
        # gRPC section
        grpc_section = ConfigSection(
            name="grpc",
            description="gRPC client settings"
        )
        
        grpc_section.add_value(ConfigValue(
            key="address",
            default="grpc.cyoda.com:443",
            required=False,
            description="gRPC server address",
            env_var=GRPC_ADDRESS
        ))
        
        grpc_section.add_value(ConfigValue(
            key="timeout",
            default=30,
            description="gRPC request timeout in seconds",
            env_var="GRPC_TIMEOUT",
            value_type=int
        ))
        
        self._sections["grpc"] = grpc_section
        
        # Repository section
        repo_section = ConfigSection(
            name="repository",
            description="Data repository settings"
        )
        
        repo_section.add_value(ConfigValue(
            key="type",
            default="cyoda",
            description="Repository type (cyoda, memory)",
            env_var="CHAT_REPOSITORY"
        ))
        
        self._sections["repository"] = repo_section
        
        # Logging section
        logging_section = ConfigSection(
            name="logging",
            description="Logging configuration"
        )
        
        logging_section.add_value(ConfigValue(
            key="level",
            default="INFO",
            description="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
            env_var="LOG_LEVEL"
        ))
        
        logging_section.add_value(ConfigValue(
            key="format",
            default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            description="Log format string",
            env_var="LOG_FORMAT"
        ))
        
        self._sections["logging"] = logging_section
        
        # Application section
        app_section = ConfigSection(
            name="application",
            description="Application-specific settings"
        )
        
        app_section.add_value(ConfigValue(
            key="name",
            default="Cyoda Client",
            description="Application name",
            env_var="APP_NAME"
        ))
        
        app_section.add_value(ConfigValue(
            key="version",
            default="1.0.0",
            description="Application version",
            env_var="ENTITY_VERSION"
        ))
        
        app_section.add_value(ConfigValue(
            key="debug",
            default=self.environment == Environment.DEVELOPMENT,
            description="Enable debug mode",
            env_var="DEBUG",
            value_type=bool
        ))
        
        self._sections["application"] = app_section
    
    def load_from_file(self, file_path: str) -> 'ConfigurationManager':
        """Load configuration from a file."""
        path = Path(file_path)
        
        if not path.exists():
            logger.warning(f"Configuration file not found: {file_path}")
            return self
        
        try:
            with open(path, 'r') as f:
                if path.suffix.lower() in ['.yml', '.yaml']:
                    data = yaml.safe_load(f)
                elif path.suffix.lower() == '.json':
                    data = json.load(f)
                else:
                    logger.error(f"Unsupported configuration file format: {path.suffix}")
                    return self
            
            self._merge_configuration(data)
            self._loaded_files.append(file_path)
            logger.info(f"Loaded configuration from: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {file_path}: {e}")
        
        return self
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        for section in self._sections.values():
            for config_value in section.values.values():
                if config_value.env_var:
                    env_value = os.getenv(config_value.env_var)
                    if env_value is not None:
                        # Convert to appropriate type
                        try:
                            if config_value.value_type == bool:
                                config_value.value = env_value.lower() in ('true', '1', 'yes', 'on')
                            elif config_value.value_type == int:
                                config_value.value = int(env_value)
                            elif config_value.value_type == float:
                                config_value.value = float(env_value)
                            else:
                                config_value.value = env_value
                        except (ValueError, TypeError) as e:
                            logger.error(f"Invalid value for {config_value.env_var}: {env_value} ({e})")
    
    def _merge_configuration(self, data: Dict[str, Any]):
        """Merge configuration data into existing structure."""
        for section_name, section_data in data.items():
            if section_name in self._sections:
                section = self._sections[section_name]
                for key, value in section_data.items():
                    if key in section.values:
                        section.values[key].value = value
    
    def _validate_configuration(self):
        """Validate all configuration values."""
        errors = []

        for section in self._sections.values():
            for config_value in section.values.values():
                # Check required values - but only warn, don't fail
                if config_value.required and (config_value.value is None or config_value.value == ""):
                    logger.warning(f"Required configuration value missing: {section.name}.{config_value.key}")
                    # Set a default value if possible
                    if config_value.default is not None:
                        config_value.value = config_value.default

                # Run custom validators
                if config_value.validator and config_value.value is not None:
                    try:
                        if not config_value.validator(config_value.value):
                            logger.warning(f"Invalid value for {section.name}.{config_value.key}: {config_value.value}")
                    except Exception as e:
                        logger.warning(f"Validation error for {section.name}.{config_value.key}: {e}")

        # Don't raise errors, just log warnings to allow app to start
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key (section.key format)."""
        if '.' not in key:
            raise ValueError("Configuration key must be in 'section.key' format")
        
        section_name, value_key = key.split('.', 1)
        
        if section_name not in self._sections:
            return default
        
        section = self._sections[section_name]
        config_value = section.get_value(value_key)
        
        if config_value is None:
            return default
        
        return config_value.value if config_value.value is not None else config_value.default
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get all values from a configuration section."""
        if section not in self._sections:
            return {}
        
        section_obj = self._sections[section]
        result = {}
        
        for key, config_value in section_obj.values.items():
            result[key] = config_value.value if config_value.value is not None else config_value.default
        
        return result
    
    def has(self, key: str) -> bool:
        """Check if a configuration key exists."""
        if '.' not in key:
            return False
        
        section_name, value_key = key.split('.', 1)
        
        if section_name not in self._sections:
            return False
        
        return value_key in self._sections[section_name].values
    
    def get_configuration_info(self) -> Dict[str, Any]:
        """Get information about the current configuration."""
        return {
            "environment": self.environment.value,
            "loaded_files": self._loaded_files,
            "sections": {
                name: {
                    "description": section.description,
                    "values": {
                        key: {
                            "description": config_value.description,
                            "required": config_value.required,
                            "has_value": config_value.value is not None,
                            "env_var": config_value.env_var
                        }
                        for key, config_value in section.values.items()
                    }
                }
                for name, section in self._sections.items()
            }
        }


# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None


def get_config_manager() -> ConfigurationManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        env = Environment(os.getenv('ENVIRONMENT', 'development'))
        _config_manager = ConfigurationManager(env)
        _config_manager.initialize()
    return _config_manager


def reset_config_manager() -> None:
    """Reset the global configuration manager instance (for testing/reloading)."""
    global _config_manager
    _config_manager = None


def get_config(key: str, default: Any = None) -> Any:
    """Get a configuration value using the global manager."""
    return get_config_manager().get(key, default)


def get_config_section(section: str) -> Dict[str, Any]:
    """Get a configuration section using the global manager."""
    return get_config_manager().get_section(section)
