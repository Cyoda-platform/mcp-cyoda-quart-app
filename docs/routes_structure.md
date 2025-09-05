# Routes Structure Documentation

This document describes the organized route structure for the Quart client application. The routes have been separated into logical modules for better maintainability and organization.

## Overview

The application routes are now organized into separate modules based on functionality:

- **Jobs** (`routes/jobs.py`) - Job scheduling and management
- **Laureates** (`routes/laureates.py`) - Nobel laureate operations
- **Subscribers** (`routes/subscribers.py`) - Subscriber management
- **Health** (`routes/health.py`) - Health checks and monitoring
- **MCP** (`routes/mcp.py`) - FastMCP integration
- **System** (`routes/system.py`) - System information and metrics

## Route Modules

### 1. Jobs Routes (`/jobs`)

**Blueprint**: `jobs_bp`  
**Prefix**: `/jobs`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/jobs/schedule` | Schedule a new job |
| GET | `/jobs/{job_id}` | Get job status by ID |
| GET | `/jobs` | List all jobs |
| PUT | `/jobs/{job_id}` | Update job status |
| DELETE | `/jobs/{job_id}` | Delete a job |

**Example Usage**:
```bash
# Schedule a job
curl -X POST http://localhost:8000/jobs/schedule

# Get job status
curl -X GET http://localhost:8000/jobs/{job_id}

# List all jobs
curl -X GET http://localhost:8000/jobs
```

### 2. Laureates Routes (`/laureates`)

**Blueprint**: `laureates_bp`  
**Prefix**: `/laureates`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/laureates` | Get laureates with optional filtering |
| GET | `/laureates/{technical_id}` | Get specific laureate |
| POST | `/laureates` | Create new laureate |
| PUT | `/laureates/{technical_id}` | Update laureate |
| DELETE | `/laureates/{technical_id}` | Delete laureate |
| POST | `/laureates/sync` | Sync laureates from Nobel API |

**Query Parameters** (for GET `/laureates`):
- `year`: Filter by year
- `category`: Filter by category

**Example Usage**:
```bash
# Get all laureates
curl -X GET http://localhost:8000/laureates

# Filter by year and category
curl -X GET "http://localhost:8000/laureates?year=2023&category=Physics"

# Sync from Nobel API
curl -X POST http://localhost:8000/laureates/sync
```

### 3. Subscribers Routes (`/subscribers`)

**Blueprint**: `subscribers_bp`  
**Prefix**: `/subscribers`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/subscribers` | List all subscribers |
| POST | `/subscribers` | Add new subscriber |
| GET | `/subscribers/{subscriber_id}` | Get specific subscriber |
| PUT | `/subscribers/{subscriber_id}` | Update subscriber |
| DELETE | `/subscribers/{subscriber_id}` | Delete subscriber |
| PUT | `/subscribers/{subscriber_id}/status` | Update subscriber status |
| POST | `/subscribers/notify` | Send notifications to subscribers |
| GET | `/subscribers/stats` | Get subscriber statistics |

**Example Usage**:
```bash
# Add subscriber
curl -X POST http://localhost:8000/subscribers \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# Get subscriber stats
curl -X GET http://localhost:8000/subscribers/stats
```

### 4. Health Routes (`/health`)

**Blueprint**: `health_bp`  
**Prefix**: `/health`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Main health check |
| GET | `/health/live` | Kubernetes liveness probe |
| GET | `/health/ready` | Kubernetes readiness probe |
| GET | `/health/detailed` | Detailed health check with system info |
| GET | `/health/startup` | Startup probe |

**Example Usage**:
```bash
# Basic health check
curl -X GET http://localhost:8000/health

# Detailed health check
curl -X GET http://localhost:8000/health/detailed
```

### 5. MCP Routes (`/mcp`)

**Blueprint**: `mcp_bp`  
**Prefix**: `/mcp`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/mcp/tools` | List available MCP tools |
| GET | `/mcp/catalog` | Get Cyoda tools catalog |
| POST | `/mcp/tools/{tool_name}` | Call specific MCP tool |
| GET | `/mcp/status` | Get MCP server status |
| GET | `/mcp/tools/{tool_name}/info` | Get tool information |
| GET | `/mcp/health` | MCP server health check |

**Example Usage**:
```bash
# Get tools catalog
curl -X GET http://localhost:8000/mcp/catalog

# Call a tool (get entity)
curl -X POST http://localhost:8000/mcp/tools/get_entity \
  -H "Content-Type: application/json" \
  -d '{"entity_model": "laureate", "entity_id": "123"}'

# Call search tool with simple conditions
curl -X POST http://localhost:8000/mcp/tools/search_entities \
  -H "Content-Type: application/json" \
  -d '{"entity_model": "laureate", "search_conditions": {"category": "Physics"}}'

# Call search tool with complex Cyoda-style conditions
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
        }
      ]
    }
  }'
```

### 6. System Routes (Root Level)

**Blueprint**: `system_bp`  
**No prefix** (root level routes)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/metrics` | Prometheus metrics |
| GET | `/metrics/summary` | JSON metrics summary |
| GET | `/info` | System information |
| GET | `/config` | Application configuration |
| GET | `/version` | Version information |
| GET | `/status` | Overall system status |

**Example Usage**:
```bash
# Get system info
curl -X GET http://localhost:8000/info

# Get metrics summary
curl -X GET http://localhost:8000/metrics/summary
```

## Benefits of Separated Routes

### 1. **Better Organization**
- Each module focuses on a specific domain
- Easier to locate and modify specific functionality
- Clear separation of concerns

### 2. **Improved Maintainability**
- Smaller, focused files are easier to understand
- Changes to one area don't affect others
- Easier to add new functionality

### 3. **Team Collaboration**
- Different team members can work on different modules
- Reduced merge conflicts
- Clear ownership boundaries

### 4. **Testing**
- Each module can be tested independently
- More focused unit tests
- Easier to mock dependencies

### 5. **Scalability**
- Easy to add new route modules
- Can be split into microservices later
- Better performance through focused imports

## Migration from Old Structure

The old monolithic `routes/routes.py` file has been:

1. **Backed up** as `routes/routes_backup.py`
2. **Split** into the 6 separate modules
3. **Removed** from the active codebase
4. **Replaced** with organized imports in `app.py`

### Changes in `app.py`

**Before**:
```python
from routes.routes import routes_bp
app.register_blueprint(routes_bp)
```

**After**:
```python
from routes import jobs_bp, laureates_bp, subscribers_bp, health_bp, mcp_bp, system_bp

app.register_blueprint(jobs_bp)
app.register_blueprint(laureates_bp)
app.register_blueprint(subscribers_bp)
app.register_blueprint(health_bp)
app.register_blueprint(mcp_bp)
app.register_blueprint(system_bp)
```

## Adding New Routes

To add a new route module:

1. **Create** a new file in `routes/` directory
2. **Define** a Blueprint with appropriate prefix
3. **Add** route handlers
4. **Import** the blueprint in `routes/__init__.py`
5. **Register** the blueprint in `app.py`

**Example**:
```python
# routes/new_module.py
from quart import Blueprint, jsonify

new_bp = Blueprint('new_module', __name__, url_prefix='/new')

@new_bp.route('/endpoint', methods=['GET'])
async def new_endpoint():
    return jsonify({"message": "New endpoint"})
```

## Best Practices

1. **Use descriptive blueprint names** that match the module purpose
2. **Apply consistent URL prefixes** for logical grouping
3. **Include comprehensive error handling** in each route
4. **Add logging** for debugging and monitoring
5. **Document** all endpoints with docstrings
6. **Validate** input data using Quart-Schema where appropriate
7. **Follow RESTful conventions** for HTTP methods and status codes

## Testing

Each route module should have corresponding tests:

```
tests/
├── test_jobs_routes.py
├── test_laureates_routes.py
├── test_subscribers_routes.py
├── test_health_routes.py
├── test_mcp_routes.py
└── test_system_routes.py
```

This organized structure makes the application more maintainable, scalable, and easier to understand for both current and future developers.
