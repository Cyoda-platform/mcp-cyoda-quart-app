# HNItem Entity

## Description
Represents a single Hacker News item in Firebase HN API JSON format. Supports all item types: stories, comments, jobs, Ask HNs, polls, and poll options.

## Attributes
- **id**: Unique integer identifier
- **type**: Item type ("job", "story", "comment", "poll", "pollopt")
- **by**: Username of author
- **time**: Creation date (Unix timestamp)
- **title**: Title for stories, polls, jobs (HTML)
- **text**: Comment/story/poll text (HTML)
- **url**: URL for stories
- **score**: Story score or poll option votes
- **parent**: Parent comment/story ID
- **kids**: Array of child comment IDs
- **descendants**: Total comment count
- **poll**: Associated poll ID for poll options
- **parts**: Related poll options for polls
- **deleted**: Boolean if item is deleted
- **dead**: Boolean if item is dead

## Relationships
- Self-referential parent-child hierarchy via parent/kids
- Poll-pollopt relationship via poll/parts
- User relationship via by field

## State Management
Entity state managed internally via `entity.meta.state` - not exposed in schema.
