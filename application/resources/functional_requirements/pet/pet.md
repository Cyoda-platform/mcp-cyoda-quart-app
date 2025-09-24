# Pet Entity Requirements

## Entity: Pet

**Purpose**: Represents pets available in the Purrfect Pets store.

## Attributes

- **name** (string, required): Pet's name (e.g., "Fluffy", "Buddy")
- **category** (object): Pet category with id and name (e.g., {"id": 1, "name": "Dogs"})
- **photoUrls** (array of strings, required): URLs to pet photos
- **tags** (array of objects): Tags for categorization with id and name
- **breed** (string): Pet breed information
- **age** (integer): Pet age in months
- **price** (number): Pet price in USD

## Relationships

- **Orders**: One pet can be referenced by multiple orders
- **Users**: Pets can be favorited by multiple users

## State Management

Pet availability status is managed through `entity.meta.state`:
- **available**: Pet is available for purchase
- **pending**: Pet is reserved/pending purchase
- **sold**: Pet has been sold

Note: The original Petstore API "status" field maps to `entity.meta.state` for workflow management.
