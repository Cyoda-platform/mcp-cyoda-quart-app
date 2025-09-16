# Routes

## CommentAnalysisRequestRoutes

### POST /api/comment-analysis-requests

**Description**: Create a new comment analysis request
**Transition**: null (entity starts in INITIAL state automatically)

**Request Body**:
```json
{
    "postId": 1,
    "recipientEmail": "user@example.com"
}
```

**Response Body**:
```json
{
    "id": 123,
    "postId": 1,
    "recipientEmail": "user@example.com",
    "requestedAt": "2024-01-15T10:30:00Z",
    "completedAt": null,
    "errorMessage": null,
    "state": "PENDING"
}
```

### GET /api/comment-analysis-requests/{id}

**Description**: Get a specific comment analysis request by ID

**Path Parameters**:
- `id` (Long): The ID of the comment analysis request

**Response Body**:
```json
{
    "id": 123,
    "postId": 1,
    "recipientEmail": "user@example.com",
    "requestedAt": "2024-01-15T10:30:00Z",
    "completedAt": "2024-01-15T10:35:00Z",
    "errorMessage": null,
    "state": "COMPLETED"
}
```

### GET /api/comment-analysis-requests

**Description**: Get all comment analysis requests with optional filtering

**Query Parameters**:
- `state` (String, optional): Filter by state (PENDING, FETCHING_COMMENTS, ANALYZING, SENDING_REPORT, COMPLETED, FAILED)
- `postId` (Integer, optional): Filter by post ID
- `page` (Integer, optional, default=0): Page number for pagination
- `size` (Integer, optional, default=20): Page size for pagination

**Response Body**:
```json
{
    "content": [
        {
            "id": 123,
            "postId": 1,
            "recipientEmail": "user@example.com",
            "requestedAt": "2024-01-15T10:30:00Z",
            "completedAt": "2024-01-15T10:35:00Z",
            "errorMessage": null,
            "state": "COMPLETED"
        }
    ],
    "totalElements": 1,
    "totalPages": 1,
    "size": 20,
    "number": 0
}
```

### PUT /api/comment-analysis-requests/{id}

**Description**: Update a comment analysis request (mainly for retry functionality)
**Transition**: "FAILED_TO_PENDING" (when retrying a failed request)

**Path Parameters**:
- `id` (Long): The ID of the comment analysis request

**Request Body**:
```json
{
    "transitionName": "FAILED_TO_PENDING",
    "recipientEmail": "newemail@example.com"
}
```

**Response Body**:
```json
{
    "id": 123,
    "postId": 1,
    "recipientEmail": "newemail@example.com",
    "requestedAt": "2024-01-15T10:30:00Z",
    "completedAt": null,
    "errorMessage": null,
    "state": "PENDING"
}
```

### DELETE /api/comment-analysis-requests/{id}

**Description**: Delete a comment analysis request (only allowed for FAILED or COMPLETED requests)

**Path Parameters**:
- `id` (Long): The ID of the comment analysis request

**Response**: 204 No Content

## CommentRoutes

### GET /api/comments

**Description**: Get comments associated with analysis requests

**Query Parameters**:
- `analysisRequestId` (Long, optional): Filter by analysis request ID
- `postId` (Integer, optional): Filter by post ID
- `page` (Integer, optional, default=0): Page number for pagination
- `size` (Integer, optional, default=50): Page size for pagination

**Response Body**:
```json
{
    "content": [
        {
            "id": 1,
            "postId": 1,
            "name": "id labore ex et quam laborum",
            "email": "Eliseo@gardner.biz",
            "body": "laudantium enim quasi est quidem magnam voluptate ipsam eos...",
            "analysisRequestId": 123,
            "fetchedAt": "2024-01-15T10:31:00Z"
        }
    ],
    "totalElements": 5,
    "totalPages": 1,
    "size": 50,
    "number": 0
}
```

### GET /api/comments/{id}

**Description**: Get a specific comment by ID

**Path Parameters**:
- `id` (Long): The ID of the comment

**Response Body**:
```json
{
    "id": 1,
    "postId": 1,
    "name": "id labore ex et quam laborum",
    "email": "Eliseo@gardner.biz",
    "body": "laudantium enim quasi est quidem magnam voluptate ipsam eos\ntempora quo necessitatibus\ndolor quam autem quasi\nreiciendis et nam sapiente accusantium",
    "analysisRequestId": 123,
    "fetchedAt": "2024-01-15T10:31:00Z"
}
```

## AnalysisReportRoutes

### GET /api/analysis-reports/{id}

**Description**: Get a specific analysis report by ID

**Path Parameters**:
- `id` (Long): The ID of the analysis report

**Response Body**:
```json
{
    "id": 456,
    "analysisRequestId": 123,
    "totalComments": 5,
    "averageCommentLength": 156.4,
    "mostActiveEmailDomain": "gardner.biz",
    "sentimentSummary": "Mixed sentiment with mostly neutral tone",
    "topKeywords": "[\"labore\", \"voluptate\", \"quasi\", \"dolor\", \"enim\"]",
    "generatedAt": "2024-01-15T10:33:00Z",
    "emailSentAt": "2024-01-15T10:34:00Z",
    "state": "SENT"
}
```

### GET /api/analysis-reports

**Description**: Get analysis reports with optional filtering

**Query Parameters**:
- `analysisRequestId` (Long, optional): Filter by analysis request ID
- `state` (String, optional): Filter by state (GENERATED, SENDING, SENT, FAILED)
- `page` (Integer, optional, default=0): Page number for pagination
- `size` (Integer, optional, default=20): Page size for pagination

**Response Body**:
```json
{
    "content": [
        {
            "id": 456,
            "analysisRequestId": 123,
            "totalComments": 5,
            "averageCommentLength": 156.4,
            "mostActiveEmailDomain": "gardner.biz",
            "sentimentSummary": "Mixed sentiment with mostly neutral tone",
            "topKeywords": "[\"labore\", \"voluptate\", \"quasi\", \"dolor\", \"enim\"]",
            "generatedAt": "2024-01-15T10:33:00Z",
            "emailSentAt": "2024-01-15T10:34:00Z",
            "state": "SENT"
        }
    ],
    "totalElements": 1,
    "totalPages": 1,
    "size": 20,
    "number": 0
}
```

### PUT /api/analysis-reports/{id}

**Description**: Update an analysis report (mainly for retry email functionality)
**Transition**: "FAILED_TO_SENDING" (when retrying email sending)

**Path Parameters**:
- `id` (Long): The ID of the analysis report

**Request Body**:
```json
{
    "transitionName": "FAILED_TO_SENDING"
}
```

**Response Body**:
```json
{
    "id": 456,
    "analysisRequestId": 123,
    "totalComments": 5,
    "averageCommentLength": 156.4,
    "mostActiveEmailDomain": "gardner.biz",
    "sentimentSummary": "Mixed sentiment with mostly neutral tone",
    "topKeywords": "[\"labore\", \"voluptate\", \"quasi\", \"dolor\", \"enim\"]",
    "generatedAt": "2024-01-15T10:33:00Z",
    "emailSentAt": null,
    "state": "SENDING"
}
```
