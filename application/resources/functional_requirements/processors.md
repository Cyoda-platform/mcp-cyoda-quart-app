# Processors

## CommentAnalysisRequest Processors

### 1. CommentAnalysisRequestInitProcessor

**Entity**: CommentAnalysisRequest
**Input**: CommentAnalysisRequest entity with postId and requestedBy
**Purpose**: Initialize the analysis request and validate input data
**Output**: Updated CommentAnalysisRequest with createdAt timestamp

**Pseudocode**:
```
process(commentAnalysisRequest):
    validate postId is positive integer
    validate requestedBy is valid email format
    set createdAt to current timestamp
    set completedAt to null
    set errorMessage to null
    save commentAnalysisRequest
    return commentAnalysisRequest
```

### 2. CommentAnalysisRequestFetchProcessor

**Entity**: CommentAnalysisRequest
**Input**: CommentAnalysisRequest in PENDING state
**Purpose**: Fetch comments from JSONPlaceholder API and create Comment entities
**Output**: CommentAnalysisRequest with associated Comment entities created

**Pseudocode**:
```
process(commentAnalysisRequest):
    try:
        apiUrl = "https://jsonplaceholder.typicode.com/comments?postId=" + commentAnalysisRequest.postId
        commentsData = httpClient.get(apiUrl)
        
        for each commentData in commentsData:
            comment = new Comment()
            comment.id = commentData.id
            comment.postId = commentData.postId
            comment.name = commentData.name
            comment.email = commentData.email
            comment.body = commentData.body
            comment.analysisRequestId = commentAnalysisRequest.id
            comment.wordCount = countWords(commentData.body)
            comment.fetchedAt = current timestamp
            save comment with transition to FETCHED state
        
        return commentAnalysisRequest
    catch Exception:
        set commentAnalysisRequest.errorMessage = exception message
        return commentAnalysisRequest
```

### 3. CommentAnalysisRequestAnalyzeProcessor

**Entity**: CommentAnalysisRequest
**Input**: CommentAnalysisRequest in FETCHING_COMMENTS state with associated comments
**Purpose**: Trigger analysis of all associated comments
**Output**: CommentAnalysisRequest with all comments analyzed

**Pseudocode**:
```
process(commentAnalysisRequest):
    comments = findCommentsByAnalysisRequestId(commentAnalysisRequest.id)
    
    for each comment in comments:
        if comment.meta.state == FETCHED:
            update comment with transition to ANALYZED state
    
    return commentAnalysisRequest
```

### 4. CommentAnalysisRequestReportProcessor

**Entity**: CommentAnalysisRequest
**Input**: CommentAnalysisRequest in ANALYZING state with all comments analyzed
**Purpose**: Create and generate analysis report
**Output**: CommentAnalysisRequest with associated CommentAnalysisReport created

**Pseudocode**:
```
process(commentAnalysisRequest):
    report = new CommentAnalysisReport()
    report.analysisRequestId = commentAnalysisRequest.id
    report.generatedAt = current timestamp
    save report with transition to GENERATED state
    
    return commentAnalysisRequest
```

### 5. CommentAnalysisRequestEmailProcessor

**Entity**: CommentAnalysisRequest
**Input**: CommentAnalysisRequest in SENDING_REPORT state
**Purpose**: Send the analysis report via email
**Output**: CommentAnalysisRequest with completedAt timestamp set

**Pseudocode**:
```
process(commentAnalysisRequest):
    report = findReportByAnalysisRequestId(commentAnalysisRequest.id)
    
    if report.meta.state == SENT:
        set commentAnalysisRequest.completedAt = current timestamp
        return commentAnalysisRequest
    else:
        set commentAnalysisRequest.errorMessage = "Failed to send email report"
        return commentAnalysisRequest
```

### 6. CommentAnalysisRequestFailProcessor

**Entity**: CommentAnalysisRequest
**Input**: CommentAnalysisRequest in any state that failed
**Purpose**: Handle failure scenarios and set error message
**Output**: CommentAnalysisRequest with error details

**Pseudocode**:
```
process(commentAnalysisRequest):
    if errorMessage is null or empty:
        set errorMessage = "Process failed at " + current state
    
    return commentAnalysisRequest
```

### 7. CommentAnalysisRequestRetryProcessor

**Entity**: CommentAnalysisRequest
**Input**: CommentAnalysisRequest in FAILED state
**Purpose**: Reset request for retry by clearing error state
**Output**: CommentAnalysisRequest ready for retry

**Pseudocode**:
```
process(commentAnalysisRequest):
    set errorMessage = null
    set completedAt = null
    return commentAnalysisRequest
```

## Comment Processors

### 8. CommentFetchProcessor

**Entity**: Comment
**Input**: Comment entity with basic data from API
**Purpose**: Process and validate fetched comment data
**Output**: Comment entity ready for analysis

**Pseudocode**:
```
process(comment):
    validate comment.email is valid email format
    validate comment.body is not null or empty
    if comment.wordCount is null:
        comment.wordCount = countWords(comment.body)
    
    return comment
```

### 9. CommentAnalyzeProcessor

**Entity**: Comment
**Input**: Comment in FETCHED state
**Purpose**: Analyze comment sentiment and extract metrics
**Output**: Comment with sentiment analysis completed

**Pseudocode**:
```
process(comment):
    sentiment = analyzeSentiment(comment.body)
    comment.sentiment = sentiment // POSITIVE, NEGATIVE, or NEUTRAL
    
    return comment
```

## CommentAnalysisReport Processors

### 10. CommentAnalysisReportGenerateProcessor

**Entity**: CommentAnalysisReport
**Input**: CommentAnalysisReport with analysisRequestId
**Purpose**: Generate comprehensive analysis report from analyzed comments
**Output**: CommentAnalysisReport with complete report content

**Pseudocode**:
```
process(report):
    comments = findCommentsByAnalysisRequestId(report.analysisRequestId)
    
    report.totalComments = comments.size()
    report.positiveComments = count comments where sentiment == POSITIVE
    report.negativeComments = count comments where sentiment == NEGATIVE
    report.neutralComments = count comments where sentiment == NEUTRAL
    report.averageWordCount = average of all comment.wordCount
    
    emailCounts = count comments grouped by email
    report.topCommenterEmail = email with highest comment count
    
    report.reportContent = generateReportText(report)
    
    return report
```

### 11. CommentAnalysisReportSendProcessor

**Entity**: CommentAnalysisReport
**Input**: CommentAnalysisReport in GENERATED state
**Purpose**: Send report via email to the requester
**Output**: CommentAnalysisReport with email sent

**Pseudocode**:
```
process(report):
    request = findCommentAnalysisRequestById(report.analysisRequestId)
    
    emailSubject = "Comment Analysis Report for Post " + request.postId
    emailBody = report.reportContent
    recipientEmail = request.requestedBy
    
    success = emailService.sendEmail(recipientEmail, emailSubject, emailBody)
    
    if success:
        report.sentAt = current timestamp
    
    return report
```

### 12. CommentAnalysisReportFailProcessor

**Entity**: CommentAnalysisReport
**Input**: CommentAnalysisReport that failed to send
**Purpose**: Handle email sending failures
**Output**: CommentAnalysisReport with failure handled

**Pseudocode**:
```
process(report):
    // Log the failure for monitoring
    log.error("Failed to send report " + report.id)
    return report
```

### 13. CommentAnalysisReportRetryProcessor

**Entity**: CommentAnalysisReport
**Input**: CommentAnalysisReport in FAILED_TO_SEND state
**Purpose**: Reset report for retry sending
**Output**: CommentAnalysisReport ready for retry

**Pseudocode**:
```
process(report):
    set sentAt = null
    return report
```
