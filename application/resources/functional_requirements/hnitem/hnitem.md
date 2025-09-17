# HN Item Entity

## Overview
The HN Item entity represents individual Hacker News items following the Firebase HN API JSON format. This entity supports stories, comments, jobs, Ask HNs, polls, and poll options.

## Entity Name
- **Entity Name**: HnItem
- **Technical Name**: hnitem

## Attributes

### Required Attributes
- **id** (integer): The item's unique id
- **type** (string): The type of item. One of "job", "story", "comment", "poll", or "pollopt"

### Optional Attributes
- **deleted** (boolean): true if the item is deleted
- **by** (string): The username of the item's author
- **time** (integer): Creation date of the item, in Unix Time
- **text** (string): The comment, story or poll text. HTML
- **dead** (boolean): true if the item is dead
- **parent** (integer): The comment's parent: either another comment or the relevant story
- **poll** (integer): The pollopt's associated poll
- **kids** (array of integers): The ids of the item's comments, in ranked display order
- **url** (string): The URL of the story
- **score** (integer): The story's score, or the votes for a pollopt
- **title** (string): The title of the story, poll or job. HTML
- **parts** (array of integers): A list of related pollopts, in display order
- **descendants** (integer): In the case of stories or polls, the total comment count

### System Attributes
- **source** (string): Source of the item ("firebase_api", "manual_post", "bulk_upload")
- **imported_at** (integer): Unix timestamp when item was imported
- **last_updated** (integer): Unix timestamp when item was last updated

## Entity State Management
The entity state is managed internally via `entity.meta.state` and should NOT appear in the entity schema. The workflow manages the following states:
- **pending**: Item is pending validation
- **validated**: Item has been validated
- **stored**: Item is successfully stored
- **failed**: Item processing failed

## Relationships

### Parent-Child Relationships
- **Parent Items**: Comments reference their parent story or comment via the `parent` field
- **Child Items**: Stories and comments can have child comments via the `kids` array
- **Poll Relationships**: Poll options reference their poll via the `poll` field, polls reference their options via the `parts` array

### Collection Relationships
- HN Items can be part of HN Items Collections
- HN Items can be created through Bulk Upload processes

## Validation Rules
1. **ID Uniqueness**: Each HN Item must have a unique `id`
2. **Type Validation**: `type` must be one of the allowed values
3. **Parent Validation**: If `parent` is specified, the parent item must exist
4. **Kids Validation**: All items in `kids` array must be valid item IDs
5. **Poll Validation**: If `poll` is specified, the poll item must exist and be of type "poll"
6. **Parts Validation**: If `parts` is specified, all items must be of type "pollopt"

## Business Rules
1. Only stories, polls, and jobs can have a `score`
2. Only comments can have a `parent`
3. Only poll options can have a `poll` reference
4. Only polls can have `parts`
5. `descendants` is calculated automatically for stories and polls
6. Items from Firebase API should preserve original structure
7. Manual posts must include required fields
8. Bulk uploads must validate all items before processing
