# Entities

## Subscriber Entity

**Name:** Subscriber

**Description:** Represents a user who has subscribed to receive weekly cat facts via email.

**Attributes:**
- `id` (Long): Unique identifier for the subscriber
- `email` (String): Email address of the subscriber (unique, required)
- `firstName` (String): First name of the subscriber (optional)
- `lastName` (String): Last name of the subscriber (optional)
- `subscriptionDate` (LocalDateTime): Date and time when the user subscribed
- `isActive` (Boolean): Whether the subscription is currently active
- `unsubscribeToken` (String): Unique token for unsubscribing (UUID)

**Relationships:**
- One-to-many with EmailDelivery entity (one subscriber can have multiple email deliveries)

**Notes:**
- Entity state will be managed by the system workflow (not included in schema)
- The state represents the subscription lifecycle (e.g., pending, active, unsubscribed)

---

## CatFact Entity

**Name:** CatFact

**Description:** Represents a cat fact retrieved from the external API and stored for weekly distribution.

**Attributes:**
- `id` (Long): Unique identifier for the cat fact
- `fact` (String): The actual cat fact text (required)
- `length` (Integer): Length of the fact text
- `retrievedDate` (LocalDateTime): Date and time when the fact was retrieved from API
- `scheduledSendDate` (LocalDateTime): Date and time when this fact is scheduled to be sent
- `apiFactId` (String): Original ID from the Cat Fact API (if available)

**Relationships:**
- One-to-many with EmailDelivery entity (one cat fact can be sent to multiple subscribers)

**Notes:**
- Entity state will be managed by the system workflow (not included in schema)
- The state represents the fact lifecycle (e.g., retrieved, scheduled, sent)

---

## EmailDelivery Entity

**Name:** EmailDelivery

**Description:** Represents the delivery of a cat fact email to a specific subscriber.

**Attributes:**
- `id` (Long): Unique identifier for the email delivery
- `subscriberId` (Long): Foreign key to Subscriber entity
- `catFactId` (Long): Foreign key to CatFact entity
- `sentDate` (LocalDateTime): Date and time when the email was sent
- `deliveryAttempts` (Integer): Number of delivery attempts made
- `lastAttemptDate` (LocalDateTime): Date and time of the last delivery attempt
- `errorMessage` (String): Error message if delivery failed (optional)
- `opened` (Boolean): Whether the email was opened by the recipient
- `openedDate` (LocalDateTime): Date and time when the email was opened (optional)

**Relationships:**
- Many-to-one with Subscriber entity
- Many-to-one with CatFact entity

**Notes:**
- Entity state will be managed by the system workflow (not included in schema)
- The state represents the delivery lifecycle (e.g., pending, sent, delivered, failed, opened)

---

## WeeklySchedule Entity

**Name:** WeeklySchedule

**Description:** Represents the weekly schedule for cat fact distribution.

**Attributes:**
- `id` (Long): Unique identifier for the schedule
- `weekStartDate` (LocalDate): Start date of the week
- `weekEndDate` (LocalDate): End date of the week
- `catFactId` (Long): Foreign key to the CatFact for this week (optional)
- `scheduledDate` (LocalDateTime): When the cat fact retrieval and sending is scheduled
- `executedDate` (LocalDateTime): When the schedule was actually executed (optional)
- `subscriberCount` (Integer): Number of active subscribers at the time of execution

**Relationships:**
- Many-to-one with CatFact entity (optional, set when fact is retrieved)

**Notes:**
- Entity state will be managed by the system workflow (not included in schema)
- The state represents the schedule lifecycle (e.g., created, fact_retrieved, emails_sent, completed)
