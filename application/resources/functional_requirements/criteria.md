# Criteria

## CommentAnalysisRequest Criteria

### 1. CommentAnalysisRequestHasCommentsCriterion

**Entity**: CommentAnalysisRequest
**Purpose**: Check if comments were successfully fetched from the API
**Condition**: At least one Comment entity exists for this analysis request

**Logic**:
```
evaluate(commentAnalysisRequest):
    comments = findCommentsByAnalysisRequestId(commentAnalysisRequest.id)
    return comments.size() > 0
```

**Usage**: Used in transition from FETCHING_COMMENTS to ANALYZING state

### 2. CommentAnalysisRequestAnalysisCompleteCriterion

**Entity**: CommentAnalysisRequest
**Purpose**: Check if all associated comments have been analyzed
**Condition**: All Comment entities for this request are in ANALYZED state

**Logic**:
```
evaluate(commentAnalysisRequest):
    comments = findCommentsByAnalysisRequestId(commentAnalysisRequest.id)
    
    if comments.size() == 0:
        return false
    
    for each comment in comments:
        if comment.meta.state != ANALYZED:
            return false
    
    return true
```

**Usage**: Used in transition from ANALYZING to SENDING_REPORT state

### 3. CommentAnalysisRequestFetchFailedCriterion

**Entity**: CommentAnalysisRequest
**Purpose**: Check if comment fetching failed
**Condition**: Error occurred during API call or no comments found when expected

**Logic**:
```
evaluate(commentAnalysisRequest):
    if commentAnalysisRequest.errorMessage != null:
        return true
    
    comments = findCommentsByAnalysisRequestId(commentAnalysisRequest.id)
    return comments.size() == 0
```

**Usage**: Used in transition from FETCHING_COMMENTS to FAILED state

### 4. CommentAnalysisRequestAnalysisFailedCriterion

**Entity**: CommentAnalysisRequest
**Purpose**: Check if comment analysis failed
**Condition**: Analysis process encountered errors or couldn't complete

**Logic**:
```
evaluate(commentAnalysisRequest):
    if commentAnalysisRequest.errorMessage != null:
        return true
    
    comments = findCommentsByAnalysisRequestId(commentAnalysisRequest.id)
    
    // Check if any comments failed to analyze after reasonable time
    for each comment in comments:
        if comment.meta.state == FETCHED and 
           (current time - comment.fetchedAt) > 5 minutes:
            return true
    
    return false
```

**Usage**: Used in transition from ANALYZING to FAILED state

### 5. CommentAnalysisRequestEmailFailedCriterion

**Entity**: CommentAnalysisRequest
**Purpose**: Check if email sending failed
**Condition**: Report exists but failed to send via email

**Logic**:
```
evaluate(commentAnalysisRequest):
    if commentAnalysisRequest.errorMessage != null:
        return true
    
    report = findReportByAnalysisRequestId(commentAnalysisRequest.id)
    
    if report == null:
        return true
    
    return report.meta.state == FAILED_TO_SEND
```

**Usage**: Used in transition from SENDING_REPORT to FAILED state

## CommentAnalysisReport Criteria

### 6. CommentAnalysisReportSendFailedCriterion

**Entity**: CommentAnalysisReport
**Purpose**: Check if email sending failed for the report
**Condition**: Email service returned failure or exception occurred

**Logic**:
```
evaluate(report):
    // Check if email sending was attempted but failed
    if report.sentAt == null and 
       (current time - report.generatedAt) > 2 minutes:
        return true
    
    return false
```

**Usage**: Used in transition from GENERATED to FAILED_TO_SEND state
