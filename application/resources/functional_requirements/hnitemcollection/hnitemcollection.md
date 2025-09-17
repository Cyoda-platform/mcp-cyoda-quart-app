# HNItemCollection Entity

## Description
Manages bulk operations for HN items including array uploads, file uploads, and batch processing from Firebase HN API.

## Attributes
- **collection_id**: Unique identifier for the collection
- **collection_type**: Type ("array", "file_upload", "firebase_pull")
- **source**: Source description (filename, API endpoint, etc.)
- **total_items**: Total number of items in collection
- **processed_items**: Number of successfully processed items
- **failed_items**: Number of failed items
- **created_at**: Collection creation timestamp
- **completed_at**: Collection completion timestamp
- **items**: Array of HNItem references or data
- **processing_errors**: Array of error details

## Relationships
- Contains multiple HNItem entities
- References individual HNItem processing results

## State Management
Entity state managed internally via `entity.meta.state` - not exposed in schema.
