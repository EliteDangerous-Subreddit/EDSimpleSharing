import re
from datetime import datetime
import praw
from state import State


class RedditMonitor(object):
    def __init__(self, state):
        """
        Initializes PRAW and sets state to the class.
        :param state: A State instance
        :type state: State
        """
        self.state = state
        self.reddit = praw.Reddit()

    def check_new_submissions(self):
        """
        Listens to new submissions from the ['submissions']['listen_from_subreddit'] config entry from config.yml.
        It should be possible to listen to multiple subreddits by using subreddits concatenated with plus,
        e.g. 'EliteDangerous+starcitizen'
        """
        print("checking submissions")
        subreddit = self.reddit.subreddit(self.state.config['submissions']['listen_from_subreddit'])
        p = re.compile(re.escape(self.state.config['submissions']['phrase']), re.IGNORECASE)
        for submission in subreddit.stream.submissions():
            if p.match(submission.title) \
                    and any(subreddit.moderator(redditor=submission.author)):
                self.create_new_post(submission)

    def check_wiki_updates(self):
        """
        Checks all the wiki articles and checks if the corresponding submission needs to be updated.
        If submission needs to be updated it replaces the submission content with the wiki content.
        """
        print("checking wiki")
        submissions = self.state.get_editable_submissions()
        for db_submission in submissions:
            wiki_subreddit = self.reddit.subreddit(self.state.config['wiki']['subreddit'])
            latest_revision = next(wiki_subreddit.wiki[db_submission.wiki_article_name].revisions())
            if latest_revision['id'] != db_submission.revision_id:
                submission = self.reddit.submission(id=db_submission.submission_id)
                print("Updating " + submission.permalink)
                submission.edit(latest_revision['page'].content_md)
                self.state.update_revision(db_submission.id, latest_revision['id'])

    def create_new_post(self, submission):
        """
        Creates a new wiki page and submission on u/EDMods based on submission
        :param submission: Submission from moderator that contains '[EDMods]'
        """
        if self.state.submission_has_been_posted(submission.id):
            return

        post_to_subreddit = self.reddit.subreddit(self.state.config['submissions']['post_to_subreddit'])
        wiki_subreddit = self.reddit.subreddit(self.state.config['wiki']['subreddit'])
        post_title = submission.title[re.search(re.escape(self.state.config['submissions']['phrase']) + r'\s*',
                                                submission.title,
                                                re.IGNORECASE
                                                ).span()[1]:]

        # Post needs to be a self post to save to wiki
        wiki_name = None
        if submission.is_self:
            new_submission, wiki_name = self.create_self_post(post_title, post_to_subreddit, submission, wiki_subreddit)
            wiki_name = f"/r/{self.state.config['wiki']['subreddit']}/wiki/{wiki_name}"
        else:
            new_submission = self.create_link_post(post_title, post_to_subreddit, submission)

        if self.state.config['notify_modmail']['activated']:
            self.notify_modmail(submission.author.name, new_submission, wiki_name)
        if self.state.config['submissions']['remove_original']:
            submission.mod.remove()

    def create_self_post(self, post_title, post_to_subreddit, submission, wiki_subreddit):
        name = self.state.config['wiki']['article_category'] \
               + "/" \
               + datetime.utcfromtimestamp(submission.created_utc).isoformat().replace(":", "-") \
               + "/" \
               + post_title
        print(name)
        new_submission = post_to_subreddit.submit(title=post_title,
                                                  selftext=submission.selftext,
                                                  send_replies=False)
        if self.state.config['submissions']['distinguish_post']:
            new_submission.mod.distinguish()
        new_wiki_page = wiki_subreddit.wiki.create(name=name,
                                                   content=submission.selftext,
                                                   reason=f"New shared submission - "
                                                   f"{new_submission.shortlink} by {submission.author.name}")
        if self.state.config['wiki']['mods_only']:
            new_wiki_page.mod.update(permlevel=2, listed=self.state.config['wiki']['list_in_wiki_list'])
        elif self.state.config['wiki']['list_in_wiki_list']:
            new_wiki_page.mod.update(listed=1)
        self.state.new_self_post(submission_id=new_submission.id,
                                 wiki_name=new_wiki_page.name,
                                 revision_id=next(new_wiki_page.revisions())['id'],
                                 original_submission_id=submission.id
                                 )
        return new_submission, name

    def create_link_post(self, post_title, post_to_subreddit, submission):
        new_submission = post_to_subreddit.submit(title=post_title,
                                                  url=submission.url,
                                                  send_replies=False)
        if self.state.config['submissions']['distinguish_post']:
            new_submission.mod.distinguish()
        self.state.new_link_post(submission_id=new_submission.id,
                                 url=submission.url,
                                 original_submission_id=submission.id)
        return new_submission

    def notify_modmail(self, created_by, submission, wiki_name):
        subreddit = self.reddit.subreddit(self.state.config['notify_modmail']['subreddit'])
        body = f"u/{created_by.name} created a new shared submission\n\n" + \
               f"[{submission.title}]({submission.permalink})"
        if wiki_name:
            body += f" ^([edit here]({wiki_name}))"
        subreddit.message("[Notification] New moderator shared post", body)
