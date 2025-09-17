# HNItemCollection Entity Requirements

## Overview
The HNItemCollection entity manages bulk operations for Hacker News items, including batch uploads, Firebase API pulls, and collection management.

## Attributes
- **collection_id**: Unique identifier for the collection
- **name**: Descriptive name for the collection
- **source**: Source of items ("firebase_api", "bulk_upload", "manual")
- **total_items**: Total number of items in collection
- **processed_items**: Number of successfully processed items
- **failed_items**: Number of failed items
- **items**: Array of HNItem references or data
- **created_at**: Collection creation timestamp
- **updated_at**: Last update timestamp
- **metadata**: Additional collection metadata

## Relationships
- Contains multiple HNItem entities
- Links to processing results and error logs

## Use Cases
- Bulk upload of HN items from JSON files
- Triggered pulls from Firebase HN API
- Batch processing and validation of multiple items
