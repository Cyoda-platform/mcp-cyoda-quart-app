# HN Item Entity

## Overview
Represents a Hacker News item from the Firebase HN API, supporting all item types: stories, comments, jobs, polls, and poll options.

## Attributes
- **id**: Unique integer identifier (required)
- **type**: Item type - "story", "comment", "job", "poll", or "pollopt" (required)
- **by**: Username of the author
- **time**: Creation timestamp (Unix time)
- **text**: Content text (HTML format)
- **url**: Story URL
- **score**: Story score or poll option votes
- **title**: Story, poll, or job title (HTML)
- **kids**: Array of child comment IDs
- **parent**: Parent comment or story ID
- **poll**: Associated poll ID (for poll options)
- **parts**: Related poll option IDs (for polls)
- **descendants**: Total comment count
- **deleted**: Boolean indicating if item is deleted
- **dead**: Boolean indicating if item is dead

## Relationships
- **Parent-Child**: Comments reference parent items via `parent` field
- **Poll-Options**: Polls reference options via `parts`, options reference poll via `poll`
- **Hierarchical**: Items form tree structures through `kids` and `parent` relationships

## Notes
Entity state is managed internally via `entity.meta.state` and not exposed in the schema.
