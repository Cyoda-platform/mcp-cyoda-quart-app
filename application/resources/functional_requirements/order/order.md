# Order Entity Requirements

## Entity: Order

**Purpose**: Represents purchase orders for pets in the Purrfect Pets store.

## Attributes

- **petId** (string, required): Reference to the pet being ordered
- **userId** (string, required): Reference to the user placing the order
- **quantity** (integer): Number of pets ordered (default: 1)
- **shipDate** (string, date-time): Expected shipping date
- **complete** (boolean): Whether the order is complete
- **totalAmount** (number): Total order amount in USD
- **shippingAddress** (object): Delivery address details

## Relationships

- **Pet**: Each order references one pet
- **User**: Each order belongs to one user

## State Management

Order processing status is managed through `entity.meta.state`:
- **placed**: Order has been placed
- **approved**: Order has been approved for processing
- **delivered**: Order has been delivered

Note: The original Petstore API "status" field maps to `entity.meta.state` for workflow management.
