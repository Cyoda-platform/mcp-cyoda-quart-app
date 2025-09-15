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
- `isActive` (Boolean): Whether the subscription is active (default: true)
- `unsubscribeToken` (String): Unique token for unsubscribing (generated automatically)

**Relationships:**
- One-to-many with SubscriberInteraction entity

**Notes:**
- The entity state will be managed automatically by the workflow system
- State represents the subscription lifecycle (e.g., pending, active, unsubscribed)

## CatFact Entity

**Name:** CatFact

**Description:** Represents a cat fact retrieved from the external API and stored for weekly distribution.

**Attributes:**
- `id` (Long): Unique identifier for the cat fact
- `fact` (String): The actual cat fact text (required)
- `length` (Integer): Length of the fact text
- `retrievedDate` (LocalDateTime): Date and time when the fact was retrieved from API
- `scheduledSendDate` (LocalDateTime): Date and time when this fact is scheduled to be sent
- `actualSendDate` (LocalDateTime): Date and time when this fact was actually sent (nullable)
- `externalApiId` (String): ID from the external Cat Fact API (if available)

**Relationships:**
- One-to-many with SubscriberInteraction entity

**Notes:**
- The entity state will be managed automatically by the workflow system
- State represents the fact lifecycle (e.g., retrieved, scheduled, sent, failed)

## SubscriberInteraction Entity

**Name:** SubscriberInteraction

**Description:** Tracks interactions between subscribers and cat facts for reporting purposes.

**Attributes:**
- `id` (Long): Unique identifier for the interaction
- `subscriberId` (Long): Foreign key to Subscriber entity
- `catFactId` (Long): Foreign key to CatFact entity
- `interactionType` (String): Type of interaction (EMAIL_SENT, EMAIL_OPENED, EMAIL_CLICKED, UNSUBSCRIBED)
- `interactionDate` (LocalDateTime): Date and time of the interaction
- `metadata` (String): Additional metadata about the interaction (JSON format, optional)

**Relationships:**
- Many-to-one with Subscriber entity
- Many-to-one with CatFact entity

**Notes:**
- The entity state will be managed automatically by the workflow system
- State represents the interaction lifecycle (e.g., recorded, processed)

## EmailCampaign Entity

**Name:** EmailCampaign

**Description:** Represents a weekly email campaign that sends cat facts to all active subscribers.

**Attributes:**
- `id` (Long): Unique identifier for the email campaign
- `catFactId` (Long): Foreign key to CatFact entity
- `campaignName` (String): Name of the campaign (e.g., "Weekly Cat Facts - Week 1")
- `scheduledDate` (LocalDateTime): Date and time when the campaign is scheduled to run
- `startedDate` (LocalDateTime): Date and time when the campaign started (nullable)
- `completedDate` (LocalDateTime): Date and time when the campaign completed (nullable)
- `totalSubscribers` (Integer): Total number of active subscribers at campaign time
- `emailsSent` (Integer): Number of emails successfully sent
- `emailsFailed` (Integer): Number of emails that failed to send
- `errorMessage` (String): Error message if campaign failed (nullable)

**Relationships:**
- Many-to-one with CatFact entity

**Notes:**
- The entity state will be managed automatically by the workflow system
- State represents the campaign lifecycle (e.g., scheduled, running, completed, failed)
