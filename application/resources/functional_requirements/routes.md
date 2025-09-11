# Routes

## CommentAnalysisRequestRoutes

### 1. Create Comment Analysis Request

**Endpoint**: `POST /api/comment-analysis-requests`
**Purpose**: Create a new comment analysis request for a specific post ID
**Transition**: null (entity starts in INITIAL state automatically)

**Request Body**:
```json
{
    "postId": 1,
    "requestedBy": "user@example.com"
}
```

**Response Body**:
```json
{
    "id": 123,
    "postId": 1,
    "requestedBy": "user@example.com",
    "state": "PENDING",
    "createdAt": "2024-01-15T10:30:00Z",
    "completedAt": null,
    "errorMessage": null
}
```

### 2. Get Comment Analysis Request

**Endpoint**: `GET /api/comment-analysis-requests/{id}`
**Purpose**: Retrieve a specific comment analysis request by ID

**Response Body**:
```json
{
    "id": 123,
    "postId": 1,
    "requestedBy": "user@example.com",
    "state": "ANALYZING",
    "createdAt": "2024-01-15T10:30:00Z",
    "completedAt": null,
    "errorMessage": null
}
```

### 3. List Comment Analysis Requests

**Endpoint**: `GET /api/comment-analysis-requests`
**Purpose**: List all comment analysis requests with optional filtering
**Query Parameters**: 
- `requestedBy` (optional): Filter by email
- `state` (optional): Filter by state
- `page` (optional): Page number (default: 0)
- `size` (optional): Page size (default: 20)

**Response Body**:
```json
{
    "content": [
        {
            "id": 123,
            "postId": 1,
            "requestedBy": "user@example.com",
            "state": "COMPLETED",
            "createdAt": "2024-01-15T10:30:00Z",
            "completedAt": "2024-01-15T10:35:00Z",
            "errorMessage": null
        }
    ],
    "totalElements": 1,
    "totalPages": 1,
    "size": 20,
    "number": 0
}
```

### 4. Retry Failed Request

**Endpoint**: `PUT /api/comment-analysis-requests/{id}/retry`
**Purpose**: Retry a failed comment analysis request
**Transition**: "FAILED_TO_PENDING" (manual transition from FAILED to PENDING)

**Request Body**: (empty)

**Response Body**:
```json
{
    "id": 123,
    "postId": 1,
    "requestedBy": "user@example.com",
    "state": "PENDING",
    "createdAt": "2024-01-15T10:30:00Z",
    "completedAt": null,
    "errorMessage": null
}
```

### 5. Delete Comment Analysis Request

**Endpoint**: `DELETE /api/comment-analysis-requests/{id}`
**Purpose**: Delete a comment analysis request and all associated data

**Response**: `204 No Content`

## CommentRoutes

### 6. Get Comments by Analysis Request

**Endpoint**: `GET /api/comment-analysis-requests/{requestId}/comments`
**Purpose**: Retrieve all comments associated with a specific analysis request

**Response Body**:
```json
[
    {
        "id": 1,
        "postId": 1,
        "name": "id labore ex et quam laborum",
        "email": "Eliseo@gardner.biz",
        "body": "laudantium enim quasi est quidem magnam voluptate...",
        "analysisRequestId": 123,
        "sentiment": "POSITIVE",
        "wordCount": 25,
        "state": "ANALYZED",
        "fetchedAt": "2024-01-15T10:31:00Z"
    }
]
```

### 7. Get Single Comment

**Endpoint**: `GET /api/comments/{id}`
**Purpose**: Retrieve a specific comment by ID

**Response Body**:
```json
{
    "id": 1,
    "postId": 1,
    "name": "id labore ex et quam laborum",
    "email": "Eliseo@gardner.biz",
    "body": "laudantium enim quasi est quidem magnam voluptate ipsam eos\ntempora quo necessitatibus\ndolor quam autem quasi\nreiciendis et nam sapiente accusantium",
    "analysisRequestId": 123,
    "sentiment": "POSITIVE",
    "wordCount": 25,
    "state": "ANALYZED",
    "fetchedAt": "2024-01-15T10:31:00Z"
}
```

## CommentAnalysisReportRoutes

### 8. Get Analysis Report

**Endpoint**: `GET /api/comment-analysis-requests/{requestId}/report`
**Purpose**: Retrieve the analysis report for a specific request

**Response Body**:
```json
{
    "id": 456,
    "analysisRequestId": 123,
    "totalComments": 5,
    "positiveComments": 2,
    "negativeComments": 1,
    "neutralComments": 2,
    "averageWordCount": 23.4,
    "topCommenterEmail": "Eliseo@gardner.biz",
    "reportContent": "Comment Analysis Report\n\nPost ID: 1\nTotal Comments: 5\n...",
    "state": "SENT",
    "generatedAt": "2024-01-15T10:34:00Z",
    "sentAt": "2024-01-15T10:34:30Z"
}
```

### 9. Resend Report Email

**Endpoint**: `PUT /api/reports/{id}/resend`
**Purpose**: Resend a failed report via email
**Transition**: "FAILED_TO_SEND_TO_GENERATED" (manual transition from FAILED_TO_SEND to GENERATED)

**Request Body**: (empty)

**Response Body**:
```json
{
    "id": 456,
    "analysisRequestId": 123,
    "totalComments": 5,
    "positiveComments": 2,
    "negativeComments": 1,
    "neutralComments": 2,
    "averageWordCount": 23.4,
    "topCommenterEmail": "Eliseo@gardner.biz",
    "reportContent": "Comment Analysis Report\n\nPost ID: 1\nTotal Comments: 5\n...",
    "state": "GENERATED",
    "generatedAt": "2024-01-15T10:34:00Z",
    "sentAt": null
}
```

### 10. Download Report

**Endpoint**: `GET /api/reports/{id}/download`
**Purpose**: Download the report content as a text file

**Response**: Text file with Content-Type: text/plain and Content-Disposition: attachment

## Error Responses

All endpoints return appropriate HTTP status codes and error messages:

**400 Bad Request**:
```json
{
    "error": "Invalid request",
    "message": "Post ID must be a positive integer",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

**404 Not Found**:
```json
{
    "error": "Resource not found",
    "message": "Comment analysis request with ID 123 not found",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

**500 Internal Server Error**:
```json
{
    "error": "Internal server error",
    "message": "An unexpected error occurred",
    "timestamp": "2024-01-15T10:30:00Z"
}
```
