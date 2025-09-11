# Entities

## 1. Subscriber Entity

**Name**: Subscriber

**Description**: Represents a user who has subscribed to receive weekly cat facts via email.

**Attributes**:
- `id` (Long): Unique identifier for the subscriber
- `email` (String): Email address of the subscriber (unique, required)
- `firstName` (String): First name of the subscriber (optional)
- `lastName` (String): Last name of the subscriber (optional)
- `subscriptionDate` (LocalDateTime): Date and time when the user subscribed
- `isActive` (Boolean): Whether the subscription is currently active
- `unsubscribeToken` (String): Unique token for unsubscribing (UUID)

**Relationships**:
- One-to-many with EmailDelivery entity (a subscriber can receive multiple email deliveries)
- One-to-many with Interaction entity (a subscriber can have multiple interactions)

**Entity State**: The system will manage the subscriber state through workflow transitions. States include: PENDING, ACTIVE, UNSUBSCRIBED.

---

## 2. CatFact Entity

**Name**: CatFact

**Description**: Represents a cat fact retrieved from the external API and stored for weekly distribution.

**Attributes**:
- `id` (Long): Unique identifier for the cat fact
- `factText` (String): The actual cat fact content (required)
- `factLength` (Integer): Length of the fact text
- `retrievedDate` (LocalDateTime): Date and time when the fact was retrieved from API
- `scheduledSendDate` (LocalDate): Date when this fact is scheduled to be sent
- `externalFactId` (String): Original ID from the Cat Fact API (if available)

**Relationships**:
- One-to-many with EmailDelivery entity (a cat fact can be sent to multiple subscribers)

**Entity State**: The system will manage the cat fact state through workflow transitions. States include: RETRIEVED, SCHEDULED, SENT, ARCHIVED.

---

## 3. EmailDelivery Entity

**Name**: EmailDelivery

**Description**: Represents the delivery of a specific cat fact to a specific subscriber.

**Attributes**:
- `id` (Long): Unique identifier for the email delivery
- `subscriberId` (Long): Foreign key to Subscriber entity
- `catFactId` (Long): Foreign key to CatFact entity
- `sentDate` (LocalDateTime): Date and time when the email was sent
- `deliveryAttempts` (Integer): Number of delivery attempts made
- `lastAttemptDate` (LocalDateTime): Date and time of the last delivery attempt
- `errorMessage` (String): Error message if delivery failed (optional)

**Relationships**:
- Many-to-one with Subscriber entity
- Many-to-one with CatFact entity
- One-to-many with Interaction entity (an email delivery can have multiple interactions)

**Entity State**: The system will manage the email delivery state through workflow transitions. States include: PENDING, SENT, FAILED, DELIVERED.

---

## 4. Interaction Entity

**Name**: Interaction

**Description**: Represents user interactions with cat facts (opens, clicks, unsubscribes, etc.).

**Attributes**:
- `id` (Long): Unique identifier for the interaction
- `subscriberId` (Long): Foreign key to Subscriber entity
- `emailDeliveryId` (Long): Foreign key to EmailDelivery entity (optional)
- `interactionType` (String): Type of interaction (EMAIL_OPEN, LINK_CLICK, UNSUBSCRIBE, etc.)
- `interactionDate` (LocalDateTime): Date and time when the interaction occurred
- `ipAddress` (String): IP address of the user (optional, for analytics)
- `userAgent` (String): User agent string (optional, for analytics)
- `additionalData` (String): Additional interaction data in JSON format (optional)

**Relationships**:
- Many-to-one with Subscriber entity
- Many-to-one with EmailDelivery entity (optional)

**Entity State**: The system will manage the interaction state through workflow transitions. States include: RECORDED, PROCESSED.

---

## 5. WeeklySchedule Entity

**Name**: WeeklySchedule

**Description**: Represents the weekly schedule for cat fact distribution and manages the weekly cycle.

**Attributes**:
- `id` (Long): Unique identifier for the weekly schedule
- `weekStartDate` (LocalDate): Start date of the week (Monday)
- `weekEndDate` (LocalDate): End date of the week (Sunday)
- `scheduledSendDate` (LocalDate): Planned date for sending cat facts this week
- `catFactId` (Long): Foreign key to the CatFact selected for this week (optional)
- `totalSubscribers` (Integer): Number of active subscribers for this week
- `emailsSent` (Integer): Number of emails successfully sent
- `emailsFailed` (Integer): Number of emails that failed to send

**Relationships**:
- Many-to-one with CatFact entity (optional, until a fact is assigned)

**Entity State**: The system will manage the weekly schedule state through workflow transitions. States include: CREATED, FACT_ASSIGNED, EMAILS_SENT, COMPLETED.
