# Entities

## CommentAnalysisRequest

**Description**: Represents a request to analyze comments for a specific post ID.

**Attributes**:
- `id` (Long): Unique identifier for the analysis request
- `postId` (Integer): The post ID to fetch comments for from JSONPlaceholder API
- `recipientEmail` (String): Email address to send the analysis report to
- `requestedAt` (LocalDateTime): Timestamp when the request was created
- `completedAt` (LocalDateTime): Timestamp when the analysis was completed (nullable)
- `errorMessage` (String): Error message if the analysis failed (nullable)

**Relationships**:
- One-to-Many with `Comment` (a request can have multiple comments)
- One-to-One with `AnalysisReport` (a request generates one report)

**Notes**:
- The entity state represents the workflow state (PENDING, FETCHING_COMMENTS, ANALYZING, SENDING_REPORT, COMPLETED, FAILED)
- State is managed automatically by the workflow system via entity.meta.state

## Comment

**Description**: Represents a comment fetched from the JSONPlaceholder API.

**Attributes**:
- `id` (Long): Unique identifier for the comment (from API)
- `postId` (Integer): The post ID this comment belongs to
- `name` (String): Name/title of the comment
- `email` (String): Email address of the comment author
- `body` (String): Content/body of the comment
- `analysisRequestId` (Long): Foreign key to the CommentAnalysisRequest
- `fetchedAt` (LocalDateTime): Timestamp when the comment was fetched

**Relationships**:
- Many-to-One with `CommentAnalysisRequest` (multiple comments belong to one request)

**Notes**:
- Comments are fetched from external API and stored for analysis
- No workflow state needed as comments are static data

## AnalysisReport

**Description**: Represents the analysis report generated from comments.

**Attributes**:
- `id` (Long): Unique identifier for the report
- `analysisRequestId` (Long): Foreign key to the CommentAnalysisRequest
- `totalComments` (Integer): Total number of comments analyzed
- `averageCommentLength` (Double): Average length of comments in characters
- `mostActiveEmailDomain` (String): Email domain that appears most frequently
- `sentimentSummary` (String): Summary of sentiment analysis (e.g., "Mostly positive")
- `topKeywords` (String): JSON array of most frequent keywords
- `generatedAt` (LocalDateTime): Timestamp when the report was generated
- `emailSentAt` (LocalDateTime): Timestamp when the report was sent via email (nullable)

**Relationships**:
- One-to-One with `CommentAnalysisRequest` (one report per request)

**Notes**:
- The entity state represents the workflow state (GENERATED, SENDING, SENT, FAILED)
- State is managed automatically by the workflow system via entity.meta.state
