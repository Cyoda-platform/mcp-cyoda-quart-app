# Entities

## 1. CommentAnalysisRequest

**Description**: Represents a request to analyze comments for a specific post ID.

**Attributes**:
- `id` (Long): Unique identifier for the analysis request
- `postId` (Integer): The post ID to fetch comments for from JSONPlaceholder API
- `requestedBy` (String): Email address of the user who requested the analysis
- `createdAt` (LocalDateTime): Timestamp when the request was created
- `completedAt` (LocalDateTime): Timestamp when the analysis was completed (nullable)
- `errorMessage` (String): Error message if the analysis failed (nullable)

**Relationships**:
- One-to-Many with Comment (one request can have multiple comments)
- One-to-One with CommentAnalysisReport (one request generates one report)

**Notes**: 
- Entity state represents the workflow state (PENDING, FETCHING_COMMENTS, ANALYZING, SENDING_REPORT, COMPLETED, FAILED)
- No status/state field in schema as it's managed by entity.meta.state

## 2. Comment

**Description**: Represents a comment fetched from the JSONPlaceholder API.

**Attributes**:
- `id` (Long): Unique identifier (from API)
- `postId` (Integer): The post ID this comment belongs to
- `name` (String): Comment title/name
- `email` (String): Email of the comment author
- `body` (String): Comment content/body
- `analysisRequestId` (Long): Foreign key to CommentAnalysisRequest
- `sentiment` (String): Analyzed sentiment (POSITIVE, NEGATIVE, NEUTRAL) - set during analysis
- `wordCount` (Integer): Number of words in the comment body
- `fetchedAt` (LocalDateTime): Timestamp when the comment was fetched

**Relationships**:
- Many-to-One with CommentAnalysisRequest (many comments belong to one request)

**Notes**:
- Entity state represents processing state (FETCHED, ANALYZED)
- Comments are created when fetched from API and updated during analysis

## 3. CommentAnalysisReport

**Description**: Represents the analysis report generated from comments.

**Attributes**:
- `id` (Long): Unique identifier for the report
- `analysisRequestId` (Long): Foreign key to CommentAnalysisRequest
- `totalComments` (Integer): Total number of comments analyzed
- `positiveComments` (Integer): Number of positive sentiment comments
- `negativeComments` (Integer): Number of negative sentiment comments
- `neutralComments` (Integer): Number of neutral sentiment comments
- `averageWordCount` (Double): Average word count across all comments
- `topCommenterEmail` (String): Email of the most active commenter
- `reportContent` (String): Full text report content
- `generatedAt` (LocalDateTime): Timestamp when the report was generated
- `sentAt` (LocalDateTime): Timestamp when the report was sent via email (nullable)

**Relationships**:
- One-to-One with CommentAnalysisRequest (one report per request)

**Notes**:
- Entity state represents report state (GENERATED, SENT, FAILED_TO_SEND)
- Report is generated after all comments are analyzed and then sent via email
