# Report Entity

## Description
The Report entity manages the generation and delivery of email reports containing comment analysis summaries.

## Attributes
- **id**: Unique identifier for the report
- **title**: Report title/subject
- **recipient_email**: Email address to send the report to
- **report_period_start**: Start date for the reporting period
- **report_period_end**: End date for the reporting period
- **summary_data**: Aggregated analysis results and metrics
- **generated_at**: When the report was generated
- **email_sent_at**: When the email was successfully sent

## Relationships
- One Report can include multiple Comments (1:N)
- One Report can include multiple Analyses (1:N)
