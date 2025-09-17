# DataSource Entity

## Description
Manages external data sources and handles downloading data from URLs.

## Attributes
- **url**: String - The URL to download data from
- **data_format**: String - Format of the data (csv, json, xml)
- **last_downloaded**: DateTime - Timestamp of last successful download
- **file_size**: Integer - Size of downloaded file in bytes
- **status**: String - Current status (pending, downloading, completed, failed)

## Relationships
- **Triggers**: DataAnalysis entity when download completes successfully
- **Referenced by**: Report entity for data source information

## Notes
Entity state is managed internally via `entity.meta.state` and should not appear in the entity schema.
