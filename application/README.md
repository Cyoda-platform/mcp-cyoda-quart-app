# Application Directory

This directory is where users should add their custom Cyoda application code.

## Structure

Create your application modules following this structure:

```
application/
├── entity/
│   ├── __init__.py
│   ├── your_entity.py
│   └── another_entity.py
├── processor/
│   ├── __init__.py
│   └── your_processor.py
├── criterion/
│   ├── __init__.py
│   └── your_criterion.py
├── resources/
│   └── workflow/
│       └── yourentity/
│           └── version_1/
│               └── YourEntity.json
└── routes/
    ├── __init__.py
    └── your_routes.py
```

## Getting Started

1. **Copy example code**: Use the `example_application/` directory as a reference
2. **Update configuration**: Modify `services/config.py` to point to your modules:
   ```python
   "modules": [
       "application.processor",
       "application.criterion",
   ],
   ```
3. **Follow the testing guide**: See `CYODA_E2E_TESTING_GUIDE.md` for end-to-end testing

## Example Code

The `example_application/` directory contains working examples of:
- Entity models with proper ENTITY_NAME configuration
- Processors that create related entities
- Criteria for validation
- Workflow definitions
- Complete end-to-end functionality

Use these as templates for your own implementation.
