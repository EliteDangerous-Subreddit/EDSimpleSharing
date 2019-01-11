import re
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
        submissions = self.state.get_editable_submissions()
        for db_submission in submissions:
            wiki_subreddit = self.reddit.subreddit(self.state.config['wiki']['subreddit'])
            latest_revision = next(wiki_subreddit.wiki[db_submission.wiki_article_name].revisions())
            if latest_revision['id'] is not db_submission.revision_id:
                submission = self.reddit.submission(id=db_submission.submission_id)
                print("Updating " + submission.permalink)
                submission.edit(latest_revision['page'].content_md)
                self.state.update_revision(db_submission.id, latest_revision['id'])

    def add_new_scheduled_posts(self):
        # iterate through all wiki articles every 2 hours
        # check if any threads exist in category that is for the future
        # add to database table through State with wiki-title, time, and type
        # type is determined to be a link if wiki content only contains link, otherwise self
        print("checking wiki")
        wiki_subreddit = self.reddit.subreddit(self.state.config['wiki']['subreddit'])
        for wiki in wiki_subreddit.wiki:
            r = re.search(re.escape(self.state.config['wiki']['article_category']) + r"/(.+?)/(.+)", wiki.name)
            if r is not None:

                search_content = re.search(
                    r"^https?://(www\.)?[-a-zA-Z0-9@:%._+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_+.~#?&/=]*)$",
                    wiki.content_md)
                if search_content is not None:
                    submission_type = "link"
                else:
                    submission_type = "self"

                scheduled_time = datetime.strptime(r.group(1), "%Y-%m-%dT%H_%M_%S%")
                if scheduled_time > datetime.now() and not self.state.wiki_article_exists_in_db():
                    self.state.schedule_post(title=r.group(2),
                                             body=wiki.content_md,
                                             scheduled_time=scheduled_time,
                                             submission_type=submission_type)

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
        if self.state.submission_has_been_posted(submission.id):
            return

        post_to_subreddit = self.reddit.subreddit(self.state.config['submissions']['post_to_subreddit'])
        wiki_subreddit = self.reddit.subreddit(self.state.config['wiki']['subreddit'])
        post_title = submission.title[re.search(r'\[EDMods\]\s*', submission.title).span()[1]:]

        # Post needs to be a self post to save to wiki
        if submission.is_self:
            name = self.state.config['wiki']['article_category'] \
                   + "/" \
                   + datetime.utcfromtimestamp(submission.created_utc).isoformat().replace(":", "_") \
                   + "/" \
                   + post_title
            print(name)
            new_submission = post_to_subreddit.submit(title=post_title,
                                                      selftext=submission.selftext,
                                                      send_replies=False)
            new_submission.mod.distinguish()
            new_wiki_page = wiki_subreddit.wiki.create(name=name,
                                                       content=submission.selftext,
                                                       reason="New shared submission - "
                                                              + new_submission.shortlink)

            self.state.new_self_post(submission_id=new_submission.id,
                                     wiki_name=new_wiki_page.name,
                                     revision_id=next(new_wiki_page.revisions())['id'],
                                     original_submission_id=submission.id
                                     )
        else:
            new_submission = post_to_subreddit.submit(title=post_title,
                                                      url=submission.url,
                                                      send_replies=False)
            new_submission.mod.distinguish()
            self.state.new_link_post(submission_id=new_submission.id,
                                     url=submission.url,
                                     original_submission_id=submission.id)
