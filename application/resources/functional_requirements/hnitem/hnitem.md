# HNItem Entity Requirements

## Entity Name
HNItem

## Description
Represents a Hacker News item in the Firebase HN API JSON format. Supports stories, comments, jobs, Ask HNs, and polls.

## Attributes

### Core Attributes
- **id**: Unique integer identifier for the item
- **type**: Item type ("story", "comment", "job", "poll", "pollopt")
- **by**: Username of the item's author
- **time**: Creation date in Unix timestamp
- **deleted**: Boolean indicating if item is deleted
- **dead**: Boolean indicating if item is dead

### Content Attributes  
- **title**: Title of story, poll, or job (HTML)
- **text**: Comment, story, or poll text (HTML)
- **url**: URL of the story
- **score**: Story score or pollopt votes
- **descendants**: Total comment count for stories/polls

### Relationship Attributes
- **parent**: Parent item ID for comments
- **kids**: Array of child comment IDs
- **poll**: Associated poll ID for pollopts
- **parts**: Array of related pollopt IDs for polls

## Relationships
- **Parent-Child**: Comments reference parent items via `parent` field
- **Poll-Options**: Polls contain `parts` array of pollopt IDs
- **Hierarchical**: Items form tree structures via `kids` arrays

## Business Rules
- All items must have unique `id` values
- `type` field determines which other fields are relevant
- Comments must have valid `parent` reference
- Polls must have associated `parts` array
