from pony.orm import *


class State(object):
    def __init__(self, config):
        self.config = config
        self.db = Database()
        self.db.bind(provider='sqlite', filename='database.sqlite', create_db=True)

    def new_post(self, submission, wiki):
        # save submission and wiki info to database
        # wiki info should save revision datetime or revision number
        # submission info should include date of creation to be able to retrieve posts younger than 6 months
        pass
