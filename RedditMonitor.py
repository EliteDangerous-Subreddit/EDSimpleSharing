from datetime import datetime

import praw


class RedditMonitor(object):
    def __init__(self, state):
        self.state = state
        self.reddit = praw.Reddit()

    def check_new_submissions(self):
        """
        Listens to new submissions from the ['submissions']['listen_from_subreddit'] config entry from config.yml.
        It should be possible to listen to multiple subreddits by using subreddits concatenated with plus,
        e.g. 'EliteDangerous+starcitizen'
        :return:
        """
        subreddit = self.reddit.subreddit(self.state.config['submissions']['listen_from_subreddit'])
        print("checking submissions")
        for submission in subreddit.stream.submissions():
            if submission.title.startswith('[EDMods]') and any(subreddit.moderator(redditor=submission.author)):
                self.create_new_post(submission)

    def check_wiki_updates(self):
        """
        Checks all the wiki articles and checks if the corresponding submission needs to be updated.
        If submission needs to be updated it replaces the submission content with the wiki content.
        """
        # retrieve all relevant wiki page name from database
        # iterate through all wiki pages' revisions to see if they correspond with database entry
        # if not, there is a change and original post should be updated
        print("checking wiki")
        pass

    def add_new_scheduled_posts(self):
        # iterate through all wiki articles every 2 hours
        # check if any threads exist in category that is for the future
        # add to database table through State with wiki-title, time, and type
        # type is determined to be a link if wiki content only contains link, otherwise self
        pass

    def check_scheduled_posts(self):
        # iterate through database every minute to see if post datetime is in the future or past
        # if it is in the past, post it through self.create_new_post if it has not been more than a day
        # add to database that the post has been posted
        pass

    def create_new_post(self, submission):
        """
        Creates a new wiki page and submission on u/EDMods based on submission
        :param submission: Submission from moderator that contains '[EDMods]'
        """
        wiki_subreddit = self.reddit.subreddit(self.state.config['wiki']['subreddit'])
        # Post needs to be a self post to save to wiki
        if submission.is_self:
            name = self.state.config['wiki']['article_category'] \
                   + "/" \
                   + datetime.utcfromtimestamp(submission.created_utc).isoformat().replace(":", "_") \
                   + "/" \
                   + submission.title[len('[EDMods]'):]
            print(name)
            new_wiki_page = wiki_subreddit.wiki.create(name, submission.selftext, "Creating new u/EDMods submission")
            # TODO below
            # post_to_subreddit = self.reddit.subreddit(self.state.config['submissions']['post_to_subreddit'])
            # new_submission = post_to_subreddit.submit(title=submission.title[len('[EDMods]'):],
            #                                           selftext=submission.selftext,
            #                                           send_replies=False)
            # self.state.new_post(new_submission, new_wiki_page)
        else:
            # Post new submission with link
            pass
        pass
