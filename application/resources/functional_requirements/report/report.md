# Report Entity

## Description
Generates and sends email reports to subscribers based on data analysis results.

## Attributes
- **analysis_id**: String - Reference to the DataAnalysis entity
- **subscribers**: Array - List of email addresses to send report to
- **report_content**: String - Generated report content
- **sent_at**: DateTime - When report was sent
- **delivery_status**: String - Email delivery status (pending, sent, failed)

## Relationships
- **Triggered by**: DataAnalysis entity when analysis completes
- **References**: DataSource and DataAnalysis entities for report content

## Notes
Entity state is managed internally via `entity.meta.state` and should not appear in the entity schema.
