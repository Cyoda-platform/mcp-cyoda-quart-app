# Entities

## 1. Subscriber Entity

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
- `confirmationToken` (String): Token for email confirmation (UUID, nullable after confirmation)
- `confirmedAt` (LocalDateTime): Date and time when email was confirmed (nullable)

**Entity State:** 
- The entity state represents the subscription lifecycle (PENDING_CONFIRMATION, ACTIVE, UNSUBSCRIBED)
- Access via `entity.meta.state` in processor code
- Cannot be modified directly - managed by workflow transitions

**Relationships:**
- One-to-Many with SubscriberInteraction (one subscriber can have multiple interactions)

---

## 2. CatFact Entity

**Name:** CatFact

**Description:** Represents a cat fact retrieved from the external API and stored for weekly distribution.

**Attributes:**
- `id` (Long): Unique identifier for the cat fact
- `factText` (String): The actual cat fact content (required)
- `externalId` (String): ID from the external Cat Fact API (if available)
- `retrievedAt` (LocalDateTime): Date and time when the fact was retrieved
- `scheduledSendDate` (LocalDate): Date when this fact is scheduled to be sent
- `sentAt` (LocalDateTime): Date and time when the fact was actually sent (nullable)
- `source` (String): Source of the cat fact (default: "catfact.ninja")

**Entity State:**
- The entity state represents the cat fact lifecycle (RETRIEVED, SCHEDULED, SENT, FAILED)
- Access via `entity.meta.state` in processor code
- Cannot be modified directly - managed by workflow transitions

**Relationships:**
- One-to-Many with SubscriberInteraction (one cat fact can have multiple interactions from different subscribers)

---

## 3. SubscriberInteraction Entity

**Name:** SubscriberInteraction

**Description:** Tracks interactions between subscribers and cat facts for reporting purposes.

**Attributes:**
- `id` (Long): Unique identifier for the interaction
- `subscriberId` (Long): Foreign key to Subscriber entity
- `catFactId` (Long): Foreign key to CatFact entity
- `interactionType` (String): Type of interaction (EMAIL_SENT, EMAIL_OPENED, EMAIL_CLICKED, UNSUBSCRIBED)
- `interactionDate` (LocalDateTime): Date and time of the interaction
- `emailDeliveryStatus` (String): Status of email delivery (SENT, DELIVERED, BOUNCED, FAILED)
- `userAgent` (String): User agent string for web-based interactions (optional)
- `ipAddress` (String): IP address of the user for web-based interactions (optional)

**Entity State:**
- The entity state represents the interaction lifecycle (RECORDED, PROCESSED)
- Access via `entity.meta.state` in processor code
- Cannot be modified directly - managed by workflow transitions

**Relationships:**
- Many-to-One with Subscriber (many interactions belong to one subscriber)
- Many-to-One with CatFact (many interactions can be related to one cat fact)

---

## 4. EmailCampaign Entity

**Name:** EmailCampaign

**Description:** Represents a weekly email campaign that sends cat facts to all active subscribers.

**Attributes:**
- `id` (Long): Unique identifier for the email campaign
- `catFactId` (Long): Foreign key to the CatFact being sent
- `campaignDate` (LocalDate): Date of the campaign
- `scheduledAt` (LocalDateTime): When the campaign was scheduled
- `startedAt` (LocalDateTime): When the campaign execution started (nullable)
- `completedAt` (LocalDateTime): When the campaign execution completed (nullable)
- `totalSubscribers` (Integer): Total number of active subscribers at campaign time
- `emailsSent` (Integer): Number of emails successfully sent
- `emailsFailed` (Integer): Number of emails that failed to send
- `subject` (String): Email subject line
- `templateVersion` (String): Version of the email template used

**Entity State:**
- The entity state represents the campaign lifecycle (SCHEDULED, IN_PROGRESS, COMPLETED, FAILED)
- Access via `entity.meta.state` in processor code
- Cannot be modified directly - managed by workflow transitions

**Relationships:**
- Many-to-One with CatFact (many campaigns can use the same cat fact, but each campaign uses one cat fact)
