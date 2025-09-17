# DataAnalysis Entity

## Description
Handles analysis of downloaded data using pandas and generates insights.

## Attributes
- **data_source_id**: String - Reference to the DataSource entity
- **analysis_type**: String - Type of analysis (summary, statistical, trend)
- **results**: Object - Analysis results and insights
- **metrics**: Object - Calculated metrics (mean, median, counts, etc.)
- **created_at**: DateTime - When analysis was performed

## Relationships
- **Triggered by**: DataSource entity when data download completes
- **Triggers**: Report entity when analysis is complete

## Notes
Entity state is managed internally via `entity.meta.state` and should not appear in the entity schema.
