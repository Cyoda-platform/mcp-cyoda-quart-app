# MCP Search Tools

The MCP search module (`cyoda_mcp/tools/search.py`) contains exactly 2 tools that are fully compliant with Cyoda's native search format:

1. **`find_all`** - Find all entities of a specific type
2. **`search`** - Search entities with Cyoda-native search conditions

Both tools support full Cyoda compliance and use `entity_model` parameter naming.

## Simple Search (Backward Compatible)

For basic searches, you can use simple field-value pairs:

```json
{
  "entity_model": "laureate",
  "search_conditions": {
    "category": "Physics",
    "year": "2023"
  },
  "entity_version": "1"
}
```

## Complex Cyoda-style Search

For advanced searches, use the Cyoda search condition structure:

### Basic Structure

```json
{
  "entity_model": "laureate",
  "search_conditions": {
    "type": "group",
    "operator": "AND",
    "conditions": [
      // Individual conditions go here
    ]
  },
  "entity_version": "1"
}
```

### Lifecycle Conditions

Search by entity state or lifecycle status:

```json
{
  "type": "lifecycle",
  "field": "state",
  "operatorType": "EQUALS",
  "value": "VALIDATED"
}
```

### Simple JSON Path Conditions

Search by JSON path within entity data:

```json
{
  "type": "simple",
  "jsonPath": "$.category",
  "operatorType": "EQUALS",
  "value": "physics"
}
```

### Supported Operators

- `EQUALS` - Exact match
- `NOT_EQUALS` - Not equal to
- `CONTAINS` - Contains substring
- `GREATER_THAN` - Greater than (for numbers)
- `LESS_THAN` - Less than (for numbers)
- `GREATER_THAN_OR_EQUAL` - Greater than or equal
- `LESS_THAN_OR_EQUAL` - Less than or equal

### Complete Example

```json
{
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
  "entity_version": "1"
}
```

### OR Conditions

Use `"operator": "OR"` for OR logic:

```json
{
  "type": "group",
  "operator": "OR",
  "conditions": [
    {
      "type": "simple",
      "jsonPath": "$.category",
      "operatorType": "EQUALS",
      "value": "physics"
    },
    {
      "type": "simple",
      "jsonPath": "$.category",
      "operatorType": "EQUALS",
      "value": "chemistry"
    }
  ]
}
```

### Numeric Comparisons

```json
{
  "type": "simple",
  "jsonPath": "$.year",
  "operatorType": "GREATER_THAN",
  "value": 2020
}
```

### Array/Nested Path Searches

```json
{
  "type": "simple",
  "jsonPath": "$.laureates[*].firstname",
  "operatorType": "CONTAINS",
  "value": "Albert"
}
```

## Usage with MCP Tools

### Find All Entities

```bash
curl -X POST http://localhost:8000/mcp/tools/find_all \
  -H "Content-Type: application/json" \
  -d '{
    "entity_model": "laureate",
    "entity_version": "1"
  }'
```

### Search with Simple Conditions

```bash
curl -X POST http://localhost:8000/mcp/tools/search \
  -H "Content-Type: application/json" \
  -d '{
    "entity_model": "laureate",
    "search_conditions": {
      "category": "Physics",
      "year": "2023"
    },
    "entity_version": "1"
  }'
```

### Search with Cyoda-Native Conditions

```bash
curl -X POST http://localhost:8000/mcp/tools/search \
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
    },
    "entity_version": "1"
  }'
```

### Via MCP Client

The MCP client can now understand and use the complex search structure to formulate proper conditions for the Cyoda platform. The search tool is fully compliant with Cyoda's native search format.

## Migration from Old Format

**Old format (still supported):**
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

**New format (recommended):**
```json
{
  "type": "group",
  "operator": "AND",
  "conditions": [
    {
      "type": "simple",
      "jsonPath": "$.field1",
      "operatorType": "EQUALS",
      "value": "value1"
    },
    {
      "type": "simple",
      "jsonPath": "$.field2",
      "operatorType": "EQUALS",
      "value": "value2"
    }
  ]
}
```
