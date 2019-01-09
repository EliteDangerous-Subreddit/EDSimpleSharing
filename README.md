# EDSimpleSharing
Utilizes a Reddit account for distributed editing of submissions through Reddit wiki articles.

In more english terms, it monitors wiki articles of a given subreddit and edits the corresponding submission. To post the submissions to begin with it listens to specific terms or wiki articles.

It's main purpose is to allow both moderators and approved submitters to change specific submissions without shared Reddit account security concerns, disclosing moderator IP-addresses through Reddit logs, and be able to see revision history of who changed what in the submissions.


For posting submissions it listens

1. New wiki pages that have timestamp in the future, and
1. New posts by moderators or approved users with config-specific prefix entry. 

## Requirements

Python 3.7+