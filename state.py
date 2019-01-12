import datetime

from pony.orm import db_session

from models.base import db


class State(object):
    def __init__(self, config):
        self.config = config
        self.db = db
        self.db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
        self.db.generate_mapping(create_tables=True)

    @db_session
    def new_self_post(self, submission_id, wiki_name, revision_id, original_submission_id=None):
        self.db.SelfSubmission(submission_id=submission_id,
                               wiki_article_name=wiki_name,
                               revision_id=revision_id,
                               last_updated=datetime.datetime.now(),
                               status="posted",
                               original_submission_id=original_submission_id)

    @db_session
    def new_link_post(self, submission_id, url, original_submission_id=None):
        self.db.LinkSubmission(submission_id=submission_id,
                               url=url,
                               status="posted",
                               original_submission_id=original_submission_id)

    @db_session
    def update_revision(self, db_submission_id, revision_id):
        self.db.SelfSubmission[db_submission_id].revision_id = revision_id

    @db_session
    def submission_has_been_posted(self, submission_id):
        return self.db.Submission.exists(original_submission_id=submission_id, status="posted")

    @db_session
    def wiki_article_exists_in_db(self, name):
        return self.db.SelfSubmission.exists(wiki_article_name=name)

    @db_session
    def get_editable_submissions(self, include_archived=False):
        if include_archived:
            return self.db.SelfSubmission.select()[:]
        else:
            return self.db.SelfSubmission.select(
                lambda s: s.last_updated > datetime.datetime.now() - datetime.timedelta(days=180))[:]
