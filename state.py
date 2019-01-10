from models.base import db


class State(object):
    def __init__(self, config):
        self.config = config
        self.db = db
        self.db.bind(provider='sqlite', filename='database.sqlite', create_db=True)

    def new_self_post(self, submission, wiki):
        # save submission and wiki info to database
        # wiki info should save revision datetime or revision number
        # submission info should include date of creation to be able to retrieve posts younger than 6 months
        pass

    def new_link_post(self, submission):
        pass

    def submission_has_been_posted(self, submission):
        pass

    def wiki_article_exists_in_db(self, name):
        pass

    def get_editable_submissions(self, include_archived=False):
        pass
