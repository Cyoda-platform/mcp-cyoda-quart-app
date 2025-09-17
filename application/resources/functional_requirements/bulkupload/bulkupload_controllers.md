# Bulk Upload Controllers

## Overview
The Bulk Upload controller provides REST API endpoints for managing bulk upload operations of Hacker News items from JSON files. It supports file upload, validation, processing, and monitoring.

## Controller Name
**BulkUploadController**

## Base URL
`/api/v1/bulkupload`

## Endpoints

### 1. Create Bulk Upload
**POST** `/api/v1/bulkupload`

Initiates a new bulk upload operation with file upload.

#### Request (Multipart Form Data)
```
Content-Type: multipart/form-data

Fields:
- file: JSON file containing HN items
- description: Optional description of the upload
- upload_type: Type of upload (json_file, json_array, csv_file)
```

#### Response (201 Created)
```json
{
  "success": true,
  "data": {
    "technical_id": "upload_123456",
    "upload_id": "bulk_upload_20231201_001",
    "filename": "hn_items_december.json",
    "upload_type": "json_file",
    "description": "December 2023 HN items bulk import",
    "file_size": 2048576,
    "file_hash": "sha256:abc123def456...",
    "uploaded_at": 1640995200,
    "meta": {
      "state": "uploaded",
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2023-12-01T10:00:00Z"
    }
  },
  "message": "Bulk upload initiated successfully"
}
```

### 2. Get Upload by ID
**GET** `/api/v1/bulkupload/{technical_id}`

Retrieves a specific bulk upload by its technical ID.

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "technical_id": "upload_123456",
    "upload_id": "bulk_upload_20231201_001",
    "filename": "hn_items_december.json",
    "upload_type": "json_file",
    "description": "December 2023 HN items bulk import",
    "file_size": 2048576,
    "file_hash": "sha256:abc123def456...",
    "total_items": 150,
    "processed_items": 145,
    "failed_items": 5,
    "collection_id": "bulk_import_collection_001",
    "uploaded_at": 1640995200,
    "started_at": 1640995250,
    "completed_at": 1640995400,
    "processing_time": 150000,
    "validation_status": "passed",
    "uploaded_by": "user123",
    "meta": {
      "state": "partial_success",
      "created_at": "2023-12-01T10:00:00Z",
      "updated_at": "2023-12-01T10:05:00Z"
    }
  }
}
```

### 3. List Bulk Uploads
**GET** `/api/v1/bulkupload`

Retrieves a list of bulk uploads with optional filtering and pagination.

#### Query Parameters
- `upload_type` (optional): Filter by upload type
- `state` (optional): Filter by workflow state
- `uploaded_by` (optional): Filter by uploader
- `status` (optional): Filter by processing status
- `limit` (optional): Number of uploads to return (default: 50, max: 200)
- `offset` (optional): Number of uploads to skip (default: 0)
- `sort` (optional): Sort field (uploaded_at, completed_at, file_size) (default: uploaded_at)
- `order` (optional): Sort order (asc, desc) (default: desc)

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "uploads": [
      {
        "technical_id": "upload_123456",
        "upload_id": "bulk_upload_20231201_001",
        "filename": "hn_items_december.json",
        "upload_type": "json_file",
        "total_items": 150,
        "processed_items": 145,
        "failed_items": 5,
        "uploaded_at": 1640995200,
        "meta": {
          "state": "partial_success"
        }
      }
    ],
    "pagination": {
      "total": 12,
      "limit": 50,
      "offset": 0,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

### 4. Trigger Workflow Transition
**POST** `/api/v1/bulkupload/{technical_id}/transition`

Triggers a specific workflow transition for a bulk upload.

#### Request Body
```json
{
  "transition": "validate_upload",
  "parameters": {
    "force_validation": true
  }
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "technical_id": "upload_123456",
    "previous_state": "uploaded",
    "current_state": "validating",
    "transition": "validate_upload",
    "triggered_at": "2023-12-01T10:15:00Z"
  },
  "message": "Transition 'validate_upload' triggered successfully"
}
```

### 5. Get Upload Progress
**GET** `/api/v1/bulkupload/{technical_id}/progress`

Retrieves real-time progress information for a bulk upload.

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "upload_id": "bulk_upload_20231201_001",
    "current_state": "processing",
    "progress": {
      "total_items": 150,
      "processed_items": 75,
      "failed_items": 2,
      "current_item": 77,
      "percentage_complete": 50.0,
      "estimated_time_remaining": 120000,
      "processing_rate": 0.5
    },
    "status": {
      "validation_status": "passed",
      "processing_status": "in_progress",
      "last_updated": "2023-12-01T10:12:30Z"
    }
  }
}
```

### 6. Get Upload Errors
**GET** `/api/v1/bulkupload/{technical_id}/errors`

Retrieves validation and processing errors for a bulk upload.

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "upload_id": "bulk_upload_20231201_001",
    "error_summary": {
      "validation_errors": 2,
      "processing_errors": 3,
      "total_errors": 5
    },
    "validation_errors": [
      {
        "item_index": 45,
        "error": "Missing required field 'type'",
        "item_data": {"id": 12345, "title": "Test"}
      }
    ],
    "processing_errors": [
      {
        "item_index": 67,
        "item_id": 23456,
        "error": "Duplicate item ID",
        "details": "Item with ID 23456 already exists"
      }
    ]
  }
}
```

### 7. Retry Failed Items
**POST** `/api/v1/bulkupload/{technical_id}/retry`

Retries processing of failed items in a bulk upload.

#### Request Body
```json
{
  "retry_all": true,
  "specific_items": []
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "upload_id": "bulk_upload_20231201_001",
    "retry_initiated": true,
    "items_to_retry": 5,
    "retry_count": 2,
    "estimated_completion": "2023-12-01T10:25:00Z"
  },
  "message": "Retry process initiated for failed items"
}
```

### 8. Get Upload Report
**GET** `/api/v1/bulkupload/{technical_id}/report`

Generates a detailed report for a completed bulk upload.

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "upload_id": "bulk_upload_20231201_001",
    "report": {
      "summary": {
        "total_items": 150,
        "successfully_processed": 145,
        "failed_items": 5,
        "success_rate": 96.67,
        "processing_time_ms": 150000
      },
      "file_info": {
        "filename": "hn_items_december.json",
        "file_size_bytes": 2048576,
        "upload_type": "json_file"
      },
      "processing_stats": {
        "validation_time_ms": 5000,
        "processing_time_ms": 145000,
        "average_item_processing_time_ms": 1000
      },
      "collection_info": {
        "collection_id": "bulk_import_collection_001",
        "items_added": 145
      },
      "error_breakdown": {
        "validation_errors": 2,
        "processing_errors": 3,
        "duplicate_items": 1,
        "invalid_format": 1,
        "missing_fields": 3
      }
    },
    "generated_at": "2023-12-01T10:30:00Z"
  }
}
```

### 9. Download Upload File
**GET** `/api/v1/bulkupload/{technical_id}/download`

Downloads the original uploaded file.

#### Response (200 OK)
```
Content-Type: application/json
Content-Disposition: attachment; filename="hn_items_december.json"

[Original file content]
```

### 10. Cancel Upload
**POST** `/api/v1/bulkupload/{technical_id}/cancel`

Cancels an ongoing bulk upload operation.

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "upload_id": "bulk_upload_20231201_001",
    "cancelled_at": "2023-12-01T10:20:00Z",
    "items_processed_before_cancel": 75,
    "cleanup_status": "in_progress"
  },
  "message": "Bulk upload cancelled successfully"
}
```

### 11. Delete Upload
**DELETE** `/api/v1/bulkupload/{technical_id}`

Deletes a bulk upload record and associated files.

#### Response (200 OK)
```json
{
  "success": true,
  "message": "Bulk upload deleted successfully"
}
```

### 12. Validate Upload File
**POST** `/api/v1/bulkupload/validate`

Validates an upload file without creating a bulk upload record.

#### Request (Multipart Form Data)
```
Content-Type: multipart/form-data

Fields:
- file: JSON file to validate
```

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "validation_result": {
      "is_valid": true,
      "total_items": 150,
      "validation_errors": [],
      "warnings": [
        "Item at index 45 has no score field"
      ],
      "file_info": {
        "size_bytes": 2048576,
        "format": "json",
        "structure": "array"
      }
    }
  },
  "message": "File validation completed"
}
```

## Workflow Transitions

The following transitions are available for bulk uploads:

1. **validate_upload**: Validates the uploaded file and content
2. **start_processing**: Starts processing validated items
3. **retry_failed_items**: Retries processing of failed items
4. **retry_upload**: Retries the entire upload process

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": {
    "code": "INVALID_FILE",
    "message": "Invalid file format",
    "details": "File must be a valid JSON file"
  }
}
```

### 413 Payload Too Large
```json
{
  "success": false,
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "File size exceeds maximum limit",
    "details": "Maximum file size is 50MB"
  }
}
```

### 422 Unprocessable Entity
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "File validation failed",
    "details": [
      "Item at index 5: Missing required field 'type'",
      "Item at index 12: Invalid item type 'invalid_type'"
    ]
  }
}
```
