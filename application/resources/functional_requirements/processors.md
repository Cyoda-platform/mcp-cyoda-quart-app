# Processors

## CommentAnalysisRequest Processors

### CommentAnalysisRequestInitProcessor

**Entity**: CommentAnalysisRequest
**Input Data**: CommentAnalysisRequest with postId and recipientEmail
**Description**: Initializes the comment analysis request and validates input data
**Output**: Updated CommentAnalysisRequest with requestedAt timestamp

**Pseudocode**:
```
process(commentAnalysisRequest):
    validate postId is positive integer
    validate recipientEmail is valid email format
    set requestedAt to current timestamp
    set completedAt to null
    set errorMessage to null
    return commentAnalysisRequest
```

### CommentAnalysisRequestFetchProcessor

**Entity**: CommentAnalysisRequest
**Input Data**: CommentAnalysisRequest in PENDING state
**Description**: Fetches comments from JSONPlaceholder API for the given postId
**Output**: CommentAnalysisRequest with associated Comment entities created

**Pseudocode**:
```
process(commentAnalysisRequest):
    apiUrl = "https://jsonplaceholder.typicode.com/comments?postId=" + commentAnalysisRequest.postId
    try:
        response = httpClient.get(apiUrl)
        if response.isSuccessful():
            commentsData = parseJson(response.body)
            for each commentData in commentsData:
                comment = new Comment()
                comment.id = commentData.id
                comment.postId = commentData.postId
                comment.name = commentData.name
                comment.email = commentData.email
                comment.body = commentData.body
                comment.analysisRequestId = commentAnalysisRequest.id
                comment.fetchedAt = current timestamp
                save comment
        else:
            throw ApiException("Failed to fetch comments: " + response.statusCode)
    catch Exception e:
        commentAnalysisRequest.errorMessage = e.message
        throw e
    return commentAnalysisRequest
```

### CommentAnalysisRequestAnalyzeProcessor

**Entity**: CommentAnalysisRequest
**Input Data**: CommentAnalysisRequest with associated Comment entities
**Description**: Analyzes the fetched comments and creates an AnalysisReport
**Output**: CommentAnalysisRequest with associated AnalysisReport created (AnalysisReport transitions to GENERATED)

**Pseudocode**:
```
process(commentAnalysisRequest):
    comments = findCommentsByAnalysisRequestId(commentAnalysisRequest.id)
    
    report = new AnalysisReport()
    report.analysisRequestId = commentAnalysisRequest.id
    report.totalComments = comments.size()
    
    totalLength = 0
    emailDomains = new Map()
    keywords = new Map()
    
    for each comment in comments:
        totalLength += comment.body.length()
        
        domain = extractDomainFromEmail(comment.email)
        emailDomains.increment(domain)
        
        words = extractKeywords(comment.body)
        for each word in words:
            keywords.increment(word)
    
    report.averageCommentLength = totalLength / comments.size()
    report.mostActiveEmailDomain = emailDomains.getMostFrequent()
    report.sentimentSummary = analyzeSentiment(comments)
    report.topKeywords = keywords.getTop10AsJson()
    report.generatedAt = current timestamp
    
    save report with transition to GENERATED state
    return commentAnalysisRequest
```

### CommentAnalysisRequestReportProcessor

**Entity**: CommentAnalysisRequest
**Input Data**: CommentAnalysisRequest with associated AnalysisReport
**Description**: Triggers the report sending process
**Output**: CommentAnalysisRequest (AnalysisReport transitions to SENDING)

**Pseudocode**:
```
process(commentAnalysisRequest):
    report = findAnalysisReportByRequestId(commentAnalysisRequest.id)
    update report with transition to SENDING state
    return commentAnalysisRequest
```

### CommentAnalysisRequestCompleteProcessor

**Entity**: CommentAnalysisRequest
**Input Data**: CommentAnalysisRequest with successfully sent report
**Description**: Marks the analysis request as completed
**Output**: Updated CommentAnalysisRequest with completedAt timestamp

**Pseudocode**:
```
process(commentAnalysisRequest):
    commentAnalysisRequest.completedAt = current timestamp
    return commentAnalysisRequest
```

### CommentAnalysisRequestFailProcessor

**Entity**: CommentAnalysisRequest
**Input Data**: CommentAnalysisRequest with error information
**Description**: Handles failure scenarios and sets error message
**Output**: Updated CommentAnalysisRequest with error details

**Pseudocode**:
```
process(commentAnalysisRequest):
    if commentAnalysisRequest.errorMessage is null:
        commentAnalysisRequest.errorMessage = "Unknown error occurred"
    log error details
    return commentAnalysisRequest
```

### CommentAnalysisRequestRetryProcessor

**Entity**: CommentAnalysisRequest
**Input Data**: CommentAnalysisRequest in FAILED state
**Description**: Resets the request for retry by clearing error state
**Output**: CommentAnalysisRequest ready for retry

**Pseudocode**:
```
process(commentAnalysisRequest):
    commentAnalysisRequest.errorMessage = null
    commentAnalysisRequest.completedAt = null
    return commentAnalysisRequest
```

## AnalysisReport Processors

### AnalysisReportGenerateProcessor

**Entity**: AnalysisReport
**Input Data**: AnalysisReport with analysis data
**Description**: Finalizes the report generation
**Output**: AnalysisReport ready for sending

**Pseudocode**:
```
process(analysisReport):
    validate all required fields are populated
    return analysisReport
```

### AnalysisReportSendProcessor

**Entity**: AnalysisReport
**Input Data**: AnalysisReport in GENERATED state
**Description**: Sends the analysis report via email
**Output**: AnalysisReport with email sending attempted

**Pseudocode**:
```
process(analysisReport):
    request = findCommentAnalysisRequestById(analysisReport.analysisRequestId)
    
    emailSubject = "Comment Analysis Report for Post " + request.postId
    emailBody = formatReportAsHtml(analysisReport)
    
    try:
        emailService.sendEmail(
            to: request.recipientEmail,
            subject: emailSubject,
            body: emailBody
        )
    catch Exception e:
        throw EmailException("Failed to send email: " + e.message)
    
    return analysisReport
```

### AnalysisReportSentProcessor

**Entity**: AnalysisReport
**Input Data**: AnalysisReport with successful email sending
**Description**: Marks the report as successfully sent
**Output**: Updated AnalysisReport with emailSentAt timestamp

**Pseudocode**:
```
process(analysisReport):
    analysisReport.emailSentAt = current timestamp
    return analysisReport
```

### AnalysisReportFailProcessor

**Entity**: AnalysisReport
**Input Data**: AnalysisReport with email sending failure
**Description**: Handles email sending failure
**Output**: AnalysisReport with failure logged

**Pseudocode**:
```
process(analysisReport):
    log email sending failure
    return analysisReport
```

### AnalysisReportRetryProcessor

**Entity**: AnalysisReport
**Input Data**: AnalysisReport in FAILED state
**Description**: Resets the report for retry email sending
**Output**: AnalysisReport ready for retry

**Pseudocode**:
```
process(analysisReport):
    analysisReport.emailSentAt = null
    return analysisReport
```
