# Criteria

## Subscriber Criteria

### SubscriberReactivationCriterion

**Entity:** Subscriber
**Description:** Checks if a bounced subscriber can be reactivated
**Input:** Subscriber entity in BOUNCED state
**Output:** Boolean indicating if reactivation is allowed

**Logic:**
- Check if subscriber has been bounced for more than 24 hours
- Check if bounce reason is not permanent (e.g., not "mailbox does not exist")
- Check if subscriber has not exceeded maximum reactivation attempts (e.g., 3 attempts)
- Return true if all conditions are met, false otherwise

## CatFact Criteria

### CatFactDistributionFailureCriterion

**Entity:** CatFact
**Description:** Determines if cat fact distribution has failed
**Input:** CatFact entity in SCHEDULED state with distribution attempt
**Output:** Boolean indicating if distribution failed

**Logic:**
- Check if actualSendDate is null after distribution attempt
- Check if more than 50% of email sends failed
- Check if critical system errors occurred during distribution
- Return true if any failure condition is met, false otherwise

### CatFactRetryCriterion

**Entity:** CatFact
**Description:** Checks if a failed cat fact distribution can be retried
**Input:** CatFact entity in FAILED state
**Output:** Boolean indicating if retry is allowed

**Logic:**
- Check if retry count is less than maximum allowed retries (e.g., 3)
- Check if failure reason is not permanent (e.g., not API unavailable)
- Check if enough time has passed since last failure (e.g., 1 hour)
- Return true if all conditions are met, false otherwise

## EmailCampaign Criteria

### EmailCampaignExecutionCriterion

**Entity:** EmailCampaign
**Description:** Checks if email campaign is ready for execution
**Input:** EmailCampaign entity in SCHEDULED state
**Output:** Boolean indicating if campaign can be executed

**Logic:**
- Check if current time is at or after scheduledDate
- Check if associated CatFact is in SCHEDULED state
- Check if there are active subscribers in the system
- Check if email service is available and operational
- Return true if all conditions are met, false otherwise

### EmailCampaignFailureCriterion

**Entity:** EmailCampaign
**Description:** Determines if email campaign execution has failed
**Input:** EmailCampaign entity in RUNNING state
**Output:** Boolean indicating if campaign failed

**Logic:**
- Check if more than 80% of email sends failed
- Check if critical system errors occurred during execution
- Check if campaign has been running for more than maximum allowed time (e.g., 2 hours)
- Check if email service became unavailable during execution
- Return true if any failure condition is met, false otherwise

### EmailCampaignRetryCriterion

**Entity:** EmailCampaign
**Description:** Checks if a failed email campaign can be retried
**Input:** EmailCampaign entity in FAILED state
**Output:** Boolean indicating if retry is allowed

**Logic:**
- Check if retry count is less than maximum allowed retries (e.g., 2)
- Check if failure reason is not permanent (e.g., not invalid campaign data)
- Check if enough time has passed since last failure (e.g., 30 minutes)
- Check if email service is now available and operational
- Return true if all conditions are met, false otherwise
