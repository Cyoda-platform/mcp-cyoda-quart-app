# Order Entity Requirements

## Entity: Order

**Purpose**: Represents purchase orders for pets in the store.

**Attributes**:
- `id`: Unique identifier (integer)
- `petId`: Reference to purchased pet (integer)
- `quantity`: Number of pets ordered (integer)
- `shipDate`: Shipping date (datetime)
- `status`: Order status (enum: "placed", "approved", "delivered")
- `complete`: Order completion flag (boolean)

**Relationships**:
- References one Pet
- May be associated with a User (implied)

**Business Rules**:
- Orders must reference valid pets
- Status progression: placed → approved → delivered
- Complete flag indicates final order state
