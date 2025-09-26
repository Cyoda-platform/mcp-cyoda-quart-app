# Comment Entity

## Description
The Comment entity stores comment data ingested from external APIs for analysis and reporting.

## Attributes
- **id**: Unique identifier for the comment
- **source_api**: API source where the comment was retrieved from
- **external_id**: Original comment ID from the external API
- **content**: The actual comment text content
- **author**: Comment author information
- **timestamp**: When the comment was created
- **metadata**: Additional data from the API (likes, replies, etc.)
- **ingested_at**: When the comment was ingested into the system

## Relationships
- One Comment can have one Analysis (1:1)
- Multiple Comments can be included in one Report (N:1)
