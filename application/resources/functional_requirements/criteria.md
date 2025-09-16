# Criteria

## CommentAnalysisRequest Criteria

### CommentAnalysisRequestFetchSuccessCriterion

**Entity**: CommentAnalysisRequest
**Description**: Checks if comments were successfully fetched from the API
**Condition**: Comments exist for the analysis request and no error message is set

**Logic**:
```
evaluate(commentAnalysisRequest):
    comments = findCommentsByAnalysisRequestId(commentAnalysisRequest.id)
    return comments.size() > 0 AND commentAnalysisRequest.errorMessage is null
```

### CommentAnalysisRequestFetchFailureCriterion

**Entity**: CommentAnalysisRequest
**Description**: Checks if comment fetching failed
**Condition**: Error message is set or no comments were fetched

**Logic**:
```
evaluate(commentAnalysisRequest):
    comments = findCommentsByAnalysisRequestId(commentAnalysisRequest.id)
    return commentAnalysisRequest.errorMessage is not null OR comments.size() == 0
```

### CommentAnalysisRequestAnalysisSuccessCriterion

**Entity**: CommentAnalysisRequest
**Description**: Checks if comment analysis was completed successfully
**Condition**: Analysis report exists and is properly generated

**Logic**:
```
evaluate(commentAnalysisRequest):
    report = findAnalysisReportByRequestId(commentAnalysisRequest.id)
    return report is not null AND 
           report.totalComments > 0 AND
           report.generatedAt is not null AND
           commentAnalysisRequest.errorMessage is null
```

### CommentAnalysisRequestAnalysisFailureCriterion

**Entity**: CommentAnalysisRequest
**Description**: Checks if comment analysis failed
**Condition**: Analysis report is missing or incomplete, or error message is set

**Logic**:
```
evaluate(commentAnalysisRequest):
    report = findAnalysisReportByRequestId(commentAnalysisRequest.id)
    return report is null OR 
           report.generatedAt is null OR
           commentAnalysisRequest.errorMessage is not null
```

### CommentAnalysisRequestEmailSuccessCriterion

**Entity**: CommentAnalysisRequest
**Description**: Checks if the email report was sent successfully
**Condition**: Associated analysis report has emailSentAt timestamp set

**Logic**:
```
evaluate(commentAnalysisRequest):
    report = findAnalysisReportByRequestId(commentAnalysisRequest.id)
    return report is not null AND 
           report.emailSentAt is not null AND
           commentAnalysisRequest.errorMessage is null
```

### CommentAnalysisRequestEmailFailureCriterion

**Entity**: CommentAnalysisRequest
**Description**: Checks if email sending failed
**Condition**: Email was not sent or error message is set

**Logic**:
```
evaluate(commentAnalysisRequest):
    report = findAnalysisReportByRequestId(commentAnalysisRequest.id)
    return report is null OR 
           report.emailSentAt is null OR
           commentAnalysisRequest.errorMessage is not null
```

## AnalysisReport Criteria

### AnalysisReportEmailSuccessCriterion

**Entity**: AnalysisReport
**Description**: Checks if the email was sent successfully
**Condition**: Email service completed successfully without exceptions

**Logic**:
```
evaluate(analysisReport):
    return no exceptions occurred during email sending AND
           email service returned success status
```

### AnalysisReportEmailFailureCriterion

**Entity**: AnalysisReport
**Description**: Checks if email sending failed
**Condition**: Email service threw an exception or returned failure status

**Logic**:
```
evaluate(analysisReport):
    return exception occurred during email sending OR
           email service returned failure status
```
