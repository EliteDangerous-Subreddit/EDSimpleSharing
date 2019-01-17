# EDSimpleSharing
Utilizes a Reddit account for distributed editing of submissions through Reddit wiki articles.

In more english terms, it monitors wiki articles of a given subreddit and edits the corresponding submission. To post the submissions to begin with it listens to specific terms or wiki articles.

It's main purpose is to allow both moderators and approved wiki users to change specific submissions without shared Reddit account security concerns or disclosing moderator IP-addresses through Reddit logs, all while being able to see revision history of who changed what in the submissions.

For posting submissions it listens for new posts with a prefix taken from config that is allowed to create new submissions, which is moderators-only by default. It then creates a new submission on the specified subreddit and creates a new wiki page where one can edit from. After those two things have been created it may notify modmail if specified in config

## Installation

Requires Python 3.7 or higher. 

1. Copy `praw.ini.example` to `praw.ini` and configure as needed by setting up a [Reddit script app on the shared account](https://www.reddit.com/prefs/apps/)
1. Copy `config.yml.example` to `config.yml` and configure as needed
1. Setup a virtualenv if needed
1. Run `pip install -r requirements.txt`
1. Start the script by running `python main.py`