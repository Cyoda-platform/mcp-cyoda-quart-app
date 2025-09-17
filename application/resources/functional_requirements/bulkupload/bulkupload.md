# Bulk Upload Entity

## Overview
The Bulk Upload entity manages the process of uploading and processing multiple Hacker News items from JSON files. It handles validation, processing, and tracking of bulk import operations.

## Entity Name
- **Entity Name**: BulkUpload
- **Technical Name**: bulkupload

## Attributes

### Required Attributes
- **upload_id** (string): Unique identifier for the upload operation
- **filename** (string): Original filename of the uploaded JSON file
- **upload_type** (string): Type of upload ("json_file", "json_array", "csv_file")

### Optional Attributes
- **description** (string): Description of the upload operation
- **file_size** (integer): Size of the uploaded file in bytes
- **file_hash** (string): SHA-256 hash of the uploaded file for integrity
- **total_items** (integer): Total number of items in the upload
- **processed_items** (integer): Number of items successfully processed
- **failed_items** (integer): Number of items that failed processing
- **validation_errors** (array): List of validation errors encountered
- **processing_errors** (array): List of processing errors encountered
- **uploaded_by** (string): Username who initiated the upload
- **collection_id** (string): ID of the collection created from this upload

### System Attributes
- **uploaded_at** (integer): Unix timestamp when file was uploaded
- **started_at** (integer): Unix timestamp when processing started
- **completed_at** (integer): Unix timestamp when processing completed
- **processing_time** (integer): Total processing time in milliseconds
- **retry_count** (integer): Number of retry attempts for failed items

## Entity State Management
The entity state is managed internally via `entity.meta.state` and should NOT appear in the entity schema. The workflow manages the following states:
- **uploaded**: File has been uploaded but not processed
- **validating**: File content is being validated
- **validated**: File content has been validated successfully
- **processing**: Items are being processed and stored
- **completed**: All items have been processed successfully
- **partial_success**: Some items processed successfully, some failed
- **failed**: Upload processing failed completely

## Relationships

### File Relationships
- **Creates HN Items**: Bulk upload creates multiple HN Item entities
- **Creates Collection**: Bulk upload creates an HN Items Collection containing all processed items
- **References Upload Source**: Tracks the source file and metadata

### Processing Relationships
- **Error Tracking**: Links to specific validation and processing errors
- **Retry Management**: Tracks retry attempts for failed items

## Validation Rules
1. **Upload ID Uniqueness**: Each upload must have a unique `upload_id`
2. **File Format Validation**: File must be valid JSON format
3. **Content Structure Validation**: JSON must contain array of HN items or single item
4. **Item Schema Validation**: Each item must conform to HN Item schema
5. **File Size Limits**: File size must be within acceptable limits
6. **Duplicate Detection**: Check for duplicate items within upload and against existing items

## Business Rules
1. **Atomic Processing**: Either all items are processed or none (with rollback capability)
2. **Partial Success Handling**: Allow partial processing with detailed error reporting
3. **Duplicate Handling**: Skip duplicates or update existing items based on configuration
4. **Error Recovery**: Support retry mechanisms for transient failures
5. **Progress Tracking**: Provide real-time progress updates during processing
6. **Audit Trail**: Maintain complete audit trail of upload and processing activities
7. **Collection Creation**: Automatically create collection for successfully processed items
8. **Cleanup**: Remove temporary files and data after processing completion

## File Formats Supported
- **JSON Array**: Array of HN item objects
- **JSON Lines**: Newline-delimited JSON objects
- **Single JSON Object**: Single HN item object
- **CSV**: CSV format with predefined column mapping

## Processing Stages
1. **Upload**: File upload and initial validation
2. **Parse**: Parse file content and extract items
3. **Validate**: Validate each item against schema
4. **Process**: Create HN Item entities
5. **Collect**: Create collection with processed items
6. **Complete**: Finalize upload and cleanup

## Error Handling
- **Validation Errors**: Schema validation failures, missing required fields
- **Processing Errors**: Database errors, constraint violations
- **System Errors**: File system errors, memory issues
- **Business Logic Errors**: Duplicate handling, relationship validation
