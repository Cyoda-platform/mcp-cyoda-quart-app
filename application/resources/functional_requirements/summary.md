# Comment Analysis Application - Functional Requirements Summary

## Overview
This document summarizes the functional requirements for a comment analysis application that ingests comments from external APIs, analyzes them, and sends email reports.

## Entities Created

### 1. Comment Entity
- **Purpose**: Store comment data ingested from external APIs
- **Key Attributes**: source_api, external_id, content, author, timestamp, metadata, ingested_at
- **Relationships**: 1:1 with Analysis, N:1 with Report
- **File**: `application/resources/functional_requirements/comment/comment.md`

### 2. Analysis Entity  
- **Purpose**: Store comment analysis results including sentiment and toxicity
- **Key Attributes**: comment_id, sentiment_score, sentiment_label, keywords, language, toxicity_score, analyzed_at
- **Relationships**: 1:1 with Comment, N:1 with Report
- **File**: `application/resources/functional_requirements/analysis/analysis.md`

### 3. Report Entity
- **Purpose**: Manage email report generation and delivery
- **Key Attributes**: title, recipient_email, report_period_start, report_period_end, summary_data, generated_at, email_sent_at
- **Relationships**: 1:N with Comments and Analyses
- **File**: `application/resources/functional_requirements/report/report.md`

## Workflows Created

### 1. Comment Workflow
- **States**: initial_state → ingested → validated → analysis_triggered → completed
- **Processors**: IngestCommentProcessor, ValidateCommentProcessor, TriggerAnalysisProcessor
- **Key Features**: Automatic ingestion, manual validation, analysis triggering
- **Files**: 
  - `application/resources/functional_requirements/comment/comment_workflow.md`
  - `application/resources/workflow/comment/version_1/Comment.json`

### 2. Analysis Workflow
- **States**: initial_state → processing → completed/failed (with retry capability)
- **Processors**: StartAnalysisProcessor, CompleteAnalysisProcessor, RetryAnalysisProcessor
- **Criteria**: AnalysisSuccessfulCriterion, AnalysisFailedCriterion
- **Key Features**: Automatic analysis start, failure handling, retry mechanism
- **Files**:
  - `application/resources/functional_requirements/analysis/analysis_workflow.md`
  - `application/resources/workflow/analysis/version_1/Analysis.json`

### 3. Report Workflow
- **States**: initial_state → generating → ready → sent/failed
- **Processors**: StartReportGenerationProcessor, CompleteReportGenerationProcessor, SendEmailProcessor
- **Criteria**: ReportGenerationFailedCriterion, EmailSendingFailedCriterion
- **Key Features**: Automatic generation start, email delivery, failure handling
- **Files**:
  - `application/resources/functional_requirements/report/report_workflow.md`
  - `application/resources/workflow/report/version_1/Report.json`

## API Routes Created

### 1. Comment Routes (`/api/comments`)
- **POST /api/comments**: Create new comment for ingestion
- **GET /api/comments/{id}**: Retrieve specific comment
- **PUT /api/comments/{id}**: Update comment with optional workflow transition
- **GET /api/comments**: List comments with filtering
- **File**: `application/resources/functional_requirements/comment/comment_routes.md`

### 2. Analysis Routes (`/api/analyses`)
- **POST /api/analyses**: Create new analysis for a comment
- **GET /api/analyses/{id}**: Retrieve specific analysis
- **PUT /api/analyses/{id}**: Update analysis with optional workflow transition
- **GET /api/analyses**: List analyses with filtering
- **File**: `application/resources/functional_requirements/analysis/analysis_routes.md`

### 3. Report Routes (`/api/reports`)
- **POST /api/reports**: Create new report for specific period
- **GET /api/reports/{id}**: Retrieve specific report
- **PUT /api/reports/{id}**: Update report with optional workflow transition
- **GET /api/reports**: List reports with filtering
- **File**: `application/resources/functional_requirements/report/report_routes.md`

## Key Design Decisions

1. **Entity State Management**: All entity states are managed internally via `entity.meta.state` and not exposed in entity schemas
2. **Workflow Simplicity**: Kept workflows simple with minimal processors and criteria as per requirements
3. **Automatic Transitions**: Initial transitions are automatic, subsequent ones are manual for control
4. **Error Handling**: Included failure states and retry mechanisms where appropriate
5. **API Consistency**: All entities follow consistent REST API patterns with optional workflow transitions

## Implementation Notes

- All workflow JSON files are validated against the schema at `example_application/resources/workflow/workflow_schema.json`
- Processors include proper configuration for async execution and retry policies
- Routes support both entity operations and workflow state transitions
- Entity relationships support the complete comment analysis and reporting pipeline
