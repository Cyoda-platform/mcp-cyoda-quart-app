# HNItem Entity Requirements

## Overview
The HNItem entity represents individual Hacker News items from the Firebase HN API, including stories, comments, jobs, Ask HNs, and polls.

## Attributes
- **id**: Unique integer identifier from HN API
- **type**: Item type ("story", "comment", "job", "poll", "pollopt")
- **by**: Username of the item's author
- **time**: Creation date in Unix timestamp
- **title**: Title of the story, poll or job (HTML)
- **text**: Comment, story or poll text (HTML)
- **url**: URL of the story
- **score**: Story's score or votes for pollopt
- **parent**: Parent item ID for comments
- **kids**: Array of child comment IDs
- **descendants**: Total comment count for stories/polls
- **poll**: Associated poll ID for pollopts
- **parts**: Related pollopt IDs for polls
- **deleted**: Boolean indicating if item is deleted
- **dead**: Boolean indicating if item is dead

## Relationships
- Parent-child relationships through `parent` and `kids` fields
- Poll-pollopt relationships through `poll` and `parts` fields
- Hierarchical comment threading support

## Data Source
Items are sourced from Firebase HN API endpoints and user submissions.
