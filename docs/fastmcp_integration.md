# FastMCP Integration with Cyoda Client

This document describes the FastMCP (Model Context Protocol) integration that provides tools for working with Cyoda services.

## Overview

The FastMCP integration adds a comprehensive toolkit for interacting with Cyoda services through MCP tools. It includes:

- **Cyoda Tools Catalog**: A single tool that provides access to all available Cyoda operations
- **Entity Operations**: CRUD operations for Cyoda entities
- **Environment Management**: Tools for managing Cyoda environment settings

## Architecture

### Components

1. **FastMCP Server** (`cyoda_mcp/server.py`): Main MCP server with all tools
2. **HTTP Routes** (`routes/routes.py`): HTTP endpoints for accessing MCP tools
3. **Tests** (`tests/test_mcp_integration.py`): Comprehensive test suite

### Tools Available

#### 1. Cyoda Tools Catalog
- **Tool Name**: `cyoda_tools_catalog`
- **Description**: Returns a comprehensive catalog of all available Cyoda tools
- **Parameters**: None
- **Returns**: Structured catalog with tool descriptions and usage examples

#### 2. Entity Operations
- **get_entity**: Retrieve a single entity by ID
- **list_entities**: List all entities of a specific type
- **search_entities**: Search entities with conditions
- **create_entity**: Create a new entity
- **update_entity**: Update an existing entity
- **delete_entity**: Delete an entity by ID

#### 3. Environment Management
- **get_env_settings**: Get current Cyoda environment settings
- **set_env_setting**: Set an environment variable (current session only)
- **list_env_vars**: List all Cyoda-related environment variables

## Usage

### HTTP Endpoints

The FastMCP tools are accessible via HTTP endpoints:

#### Get Tools Catalog
```bash
GET /mcp/catalog
```

Returns the complete Cyoda tools catalog with descriptions and usage examples.

#### List Available Tools
```bash
GET /mcp/tools
```

Returns a list of all available MCP tools.

#### Call a Specific Tool
```bash
POST /mcp/tools/{tool_name}
Content-Type: application/json

{
  "param1": "value1",
  "param2": "value2"
}
```

#### Get MCP Server Status
```bash
GET /mcp/status
```

Returns the current status of the MCP server.

### Examples

#### 1. Get the Tools Catalog
```bash
curl -X GET http://localhost:8000/mcp/catalog
```

#### 2. Retrieve an Entity
```bash
curl -X POST http://localhost:8000/mcp/tools/get_entity \
  -H "Content-Type: application/json" \
  -d '{
    "entity_model": "laureate",
    "entity_id": "123e4567-e89b-12d3-a456-426614174000",
    "entity_version": "1.0"
  }'
```

#### 3. List All Entities of a Type
```bash
curl -X POST http://localhost:8000/mcp/tools/list_entities \
  -H "Content-Type: application/json" \
  -d '{
    "entity_model": "subscriber",
    "entity_version": "1.0"
  }'
```

#### 4. Create a New Entity
```bash
curl -X POST http://localhost:8000/mcp/tools/create_entity \
  -H "Content-Type: application/json" \
  -d '{
    "entity_model": "subscriber",
    "entity_data": {
      "email": "user@example.com",
      "name": "John Doe"
    },
    "entity_version": "1.0"
  }'
```

#### 5. Search Entities

**Simple Search (field-value pairs):**
```bash
curl -X POST http://localhost:8000/mcp/tools/search_entities \
  -H "Content-Type: application/json" \
  -d '{
    "entity_model": "laureate",
    "search_conditions": {
      "category": "Physics",
      "year": "2023"
    },
    "entity_version": "1.0"
  }'
```

**Advanced Cyoda-style Search:**
```bash
curl -X POST http://localhost:8000/mcp/tools/search_entities \
  -H "Content-Type: application/json" \
  -d '{
    "entity_model": "laureate",
    "search_conditions": {
      "type": "group",
      "operator": "AND",
      "conditions": [
        {
          "type": "lifecycle",
          "field": "state",
          "operatorType": "EQUALS",
          "value": "VALIDATED"
        },
        {
          "type": "simple",
          "jsonPath": "$.category",
          "operatorType": "EQUALS",
          "value": "physics"
        },
        {
          "type": "simple",
          "jsonPath": "$.laureates[*].motivation",
          "operatorType": "CONTAINS",
          "value": "neural networks"
        }
      ]
    },
    "entity_version": "1.0"
  }'
```

#### 6. Get Environment Settings
```bash
curl -X POST http://localhost:8000/mcp/tools/get_env_settings
```

#### 7. Set Environment Variable
```bash
curl -X POST http://localhost:8000/mcp/tools/set_env_setting \
  -H "Content-Type: application/json" \
  -d '{
    "key": "CYODA_CLIENT_ID",
    "value": "your_client_id"
  }'
```

## Configuration

### Environment Variables

The following environment variables are used by the MCP tools:

- `CYODA_CLIENT_ID`: OAuth client ID for Cyoda authentication
- `CYODA_CLIENT_SECRET`: OAuth client secret (hidden in responses)
- `CYODA_TOKEN_URL`: OAuth token endpoint URL
- `CHAT_REPOSITORY`: Repository type (`cyoda` or `in_memory`)
- `ENTITY_VERSION`: Default entity model version

### Security

- Only Cyoda-related environment variables can be set through the MCP tools
- Client secrets are hidden in all responses for security
- All operations respect the existing authentication and authorization mechanisms

## Testing

Run the comprehensive test suite:

```bash
python -m pytest tests/test_mcp_integration.py -v
```

The tests cover:
- MCP server initialization
- Tools catalog functionality
- Entity CRUD operations
- Environment management
- Error handling

## Integration with Existing Application

The FastMCP server is automatically initialized when the Quart application starts. The integration:

1. Initializes the FastMCP server during app startup
2. Registers all tools automatically
3. Provides HTTP endpoints for tool access
4. Maintains compatibility with existing Cyoda services

## Error Handling

All MCP tools return structured responses with success/error indicators:

```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2025-09-03T18:35:56Z"
}
```

Or for errors:

```json
{
  "success": false,
  "error": "Error description",
  "timestamp": "2025-09-03T18:35:56Z"
}
```

## Future Enhancements

Potential future improvements:
- WebSocket support for real-time MCP communication
- Additional entity operations (bulk operations, transactions)
- Enhanced search capabilities with complex queries
- Integration with Cyoda's streaming capabilities
- Authentication and authorization for MCP endpoints
