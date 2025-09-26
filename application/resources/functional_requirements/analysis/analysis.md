# Analysis Entity

## Description
The Analysis entity stores the results of comment analysis including sentiment, keywords, and metrics.

## Attributes
- **id**: Unique identifier for the analysis
- **comment_id**: Reference to the analyzed comment
- **sentiment_score**: Numerical sentiment analysis result (-1 to 1)
- **sentiment_label**: Text label (positive, negative, neutral)
- **keywords**: Extracted keywords from the comment
- **language**: Detected language of the comment
- **toxicity_score**: Content toxicity assessment (0 to 1)
- **analyzed_at**: When the analysis was performed

## Relationships
- One Analysis belongs to one Comment (1:1)
- Multiple Analyses can be included in one Report (N:1)
