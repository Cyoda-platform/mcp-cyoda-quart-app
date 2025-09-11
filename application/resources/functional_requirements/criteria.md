# Criteria

## MailIsHappyCriterion

### Entity
Mail

### Description
Determines if a mail entity contains happy/positive content by analyzing the email subject and body text for positive sentiment indicators.

### Input
- Mail entity in PENDING_ANALYSIS state
- Required fields: content, subject

### Logic
Evaluates the mail content for positive sentiment by checking for:
- Positive keywords (happy, joy, celebration, success, congratulations, etc.)
- Positive emoticons/emojis
- Exclamation marks indicating excitement
- Overall positive tone in the text

### Evaluation Criteria
Returns `true` if:
- Content contains positive keywords above a threshold
- Subject line indicates positive sentiment
- Overall sentiment analysis score is positive
- No negative sentiment indicators override the positive ones

Returns `false` otherwise

### Implementation Notes
- Uses natural language processing for sentiment analysis
- Maintains a dictionary of positive keywords and phrases
- Considers context to avoid false positives

---

## MailIsGloomyCriterion

### Entity
Mail

### Description
Determines if a mail entity contains gloomy/negative content by analyzing the email subject and body text for negative sentiment indicators.

### Input
- Mail entity in PENDING_ANALYSIS state
- Required fields: content, subject

### Logic
Evaluates the mail content for negative sentiment by checking for:
- Negative keywords (sad, depressed, failure, loss, grief, etc.)
- Negative emoticons/emojis
- Words indicating distress or unhappiness
- Overall negative tone in the text

### Evaluation Criteria
Returns `true` if:
- Content contains negative keywords above a threshold
- Subject line indicates negative sentiment
- Overall sentiment analysis score is negative
- Negative sentiment indicators are predominant

Returns `false` otherwise

### Implementation Notes
- Uses natural language processing for sentiment analysis
- Maintains a dictionary of negative keywords and phrases
- Considers context to avoid false negatives
- Should be mutually exclusive with MailIsHappyCriterion (if one returns true, the other should return false)

### Fallback Behavior
If neither criterion returns true (neutral content), the system should default to treating the mail as gloomy to ensure it receives appropriate handling.
