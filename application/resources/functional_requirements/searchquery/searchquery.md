# SearchQuery Entity Requirements

## Overview
The SearchQuery entity manages search operations for Hacker News items, including complex queries with parent hierarchy joins and filtering capabilities.

## Attributes
- **query_id**: Unique identifier for the search query
- **query_text**: Search terms and keywords
- **filters**: Search filters (type, author, date range, score)
- **include_children**: Boolean to include child comments in results
- **parent_hierarchy**: Boolean to traverse parent relationships
- **sort_by**: Sort criteria (score, time, relevance)
- **limit**: Maximum number of results
- **offset**: Pagination offset
- **executed_at**: Query execution timestamp
- **results_count**: Number of results returned
- **execution_time**: Query execution duration

## Relationships
- References HNItem entities in search results
- Links to search indices and cached results

## Search Capabilities
- Full-text search across titles, text content
- Filtering by item type, author, date ranges
- Parent-child hierarchy traversal for comments
- Relevance scoring and ranking
