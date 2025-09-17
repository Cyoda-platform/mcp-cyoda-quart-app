# HN Items Collection Entity

## Overview
The HN Items Collection entity represents a collection of multiple Hacker News items. This entity is used for managing arrays of HN items, batch operations, and collection-based queries.

## Entity Name
- **Entity Name**: HnItemsCollection
- **Technical Name**: hnitemscollection

## Attributes

### Required Attributes
- **collection_id** (string): Unique identifier for the collection
- **name** (string): Human-readable name for the collection
- **collection_type** (string): Type of collection ("manual", "firebase_fetch", "search_result", "bulk_import")

### Optional Attributes
- **description** (string): Description of the collection
- **item_ids** (array of integers): Array of HN Item IDs in this collection
- **total_items** (integer): Total number of items in the collection
- **created_by** (string): Username who created the collection
- **tags** (array of strings): Tags for categorizing collections
- **filters** (object): Filter criteria used to create the collection
- **sort_order** (string): Sort order for items ("score", "time", "id", "custom")

### System Attributes
- **created_at** (integer): Unix timestamp when collection was created
- **updated_at** (integer): Unix timestamp when collection was last updated
- **status** (string): Current status ("active", "archived", "processing")
- **item_count** (integer): Actual count of items (may differ from total_items during processing)

## Entity State Management
The entity state is managed internally via `entity.meta.state` and should NOT appear in the entity schema. The workflow manages the following states:
- **created**: Collection is created but empty
- **populating**: Collection is being populated with items
- **populated**: Collection has been populated with items
- **validated**: All items in collection have been validated
- **ready**: Collection is ready for use
- **archived**: Collection has been archived

## Relationships

### Item Relationships
- **Contains HN Items**: Collection references multiple HN Items via `item_ids`
- **Created from Bulk Upload**: Collections can be created from Bulk Upload processes
- **Generated from Search**: Collections can be results of Search Query operations

### Collection Hierarchies
- Collections can reference other collections for hierarchical organization
- Parent-child relationships between collections for nested structures

## Validation Rules
1. **Collection ID Uniqueness**: Each collection must have a unique `collection_id`
2. **Name Required**: Collection must have a non-empty name
3. **Type Validation**: `collection_type` must be one of the allowed values
4. **Item ID Validation**: All items in `item_ids` must reference existing HN Items
5. **Count Consistency**: `item_count` should match the length of `item_ids` array

## Business Rules
1. Collections can contain items of mixed types (stories, comments, jobs, etc.)
2. Items can belong to multiple collections
3. Collections created from Firebase fetch should preserve the original order
4. Manual collections allow custom ordering
5. Search result collections are read-only regarding item order
6. Bulk import collections track the import source
7. Collections can be filtered and sorted dynamically
8. Archived collections are read-only but preserved for historical reference

## Collection Types
- **manual**: User-created collections with custom item selection
- **firebase_fetch**: Collections created from Firebase HN API pulls
- **search_result**: Collections generated from search operations
- **bulk_import**: Collections created from bulk upload operations

## Operations
- Add/remove items from collection
- Merge collections
- Split collections
- Archive/restore collections
- Export collection metadata
- Generate collection statistics
