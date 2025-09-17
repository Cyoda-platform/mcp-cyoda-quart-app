# HN Item Entity Requirements

## Entity Name
HnItem

## Description
Represents a Hacker News item in the JSON format of the Firebase HN API. Items can be stories, comments, jobs, Ask HNs, polls, or poll options.

## Attributes

### Required Attributes
- **id** (integer): The item's unique identifier from Hacker News
- **type** (string): The type of item - one of "job", "story", "comment", "poll", or "pollopt"

### Optional Attributes
- **by** (string): The username of the item's author
- **time** (integer): Creation date of the item, in Unix Time
- **title** (string): The title of the story, poll or job (HTML)
- **text** (string): The comment, story or poll text (HTML)
- **url** (string): The URL of the story
- **score** (integer): The story's score, or the votes for a pollopt
- **parent** (integer): The comment's parent: either another comment or the relevant story
- **kids** (array of integers): The ids of the item's comments, in ranked display order
- **descendants** (integer): In the case of stories or polls, the total comment count
- **dead** (boolean): true if the item is dead
- **deleted** (boolean): true if the item is deleted
- **poll** (integer): The pollopt's associated poll
- **parts** (array of integers): A list of related pollopts, in display order

## Relationships
- **Parent-Child**: Comments have parent items (stories or other comments) via the `parent` field
- **Hierarchical**: Items can have child comments via the `kids` field
- **Poll-PollOpt**: Poll options are linked to polls via the `poll` field, polls have options via `parts` field

## Business Rules
- The `id` must be unique across all HN items
- Items with type "comment" should have a `parent` field
- Items with type "story", "poll", or "job" may have `kids` (comments)
- Items with type "pollopt" should have a `poll` field
- Items with type "poll" should have a `parts` field with poll options
- The `descendants` field represents the total count of all nested comments
