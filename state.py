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
    def new_self_post(self, submission_id, wiki_name, revision_id):
        self.db.SelfSubmission(submission_id=submission_id,
                               wiki_article_name=wiki_name,
                               revision_id=revision_id,
                               last_updated=datetime.datetime.now(),
                               status="posted")
        # save submission and wiki info to database
        # wiki info should save revision datetime or revision number
        # submission info should include date of creation to be able to retrieve posts younger than 6 months
        pass

    @db_session
    def new_link_post(self, submission_id):
        pass

    @db_session
    def submission_has_been_posted(self, submission_id):
        return self.db.Submission.exists(submission_id=submission_id, status="posted")

    @db_session
    def wiki_article_exists_in_db(self, name):
        return self.db.SelfSubmission.exists(wiki_article_name=name)

    @db_session
    def get_editable_submissions(self, include_archived=False):
        if include_archived:
            return self.db.SelfSubmission.select()[:]
        else:
            return self.db.SelfSubmission.select(
                lambda s: s.last_updated < datetime.datetime.now() - datetime.timedelta(days=180))[:]
