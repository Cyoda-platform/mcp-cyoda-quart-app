# Order Entity

## Description
Represents orders placed by users for pet adoption or purchase.

## Attributes
- **userId**: Reference to User entity (string)
- **petId**: Reference to Pet entity (string)
- **orderDate**: Date order was placed (string)
- **totalAmount**: Total order amount (number)
- **paymentMethod**: Payment method used (string) - credit_card, cash, check
- **deliveryAddress**: Delivery address (string)
- **specialInstructions**: Additional notes (string)
- **estimatedDeliveryDate**: Expected delivery date (string)

## Relationships
- **User**: Many-to-one relationship with User entity
- **Pet**: Many-to-one relationship with Pet entity

## Business Rules
- Order state managed through entity.meta.state (not in schema)
- Orders require payment processing
- Completed orders mark pets as unavailable
- Orders can be cancelled before processing
