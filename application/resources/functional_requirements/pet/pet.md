# Pet Entity Requirements

## Entity: Pet

**Purpose**: Represents pets available in the Purrfect Pets store.

**Attributes**:
- `id`: Unique identifier (integer)
- `name`: Pet name (string, required)
- `category`: Pet category reference (Category entity)
- `photoUrls`: Array of photo URLs (string array, required)
- `tags`: Array of tags (Tag entity array)
- `status`: Pet availability status (enum: "available", "pending", "sold")

**Relationships**:
- Belongs to one Category
- Has many Tags
- Referenced by Orders

**Business Rules**:
- Name and photoUrls are mandatory
- Status determines availability for purchase
- Pet state transitions managed through workflow
