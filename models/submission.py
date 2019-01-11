from datetime import datetime

from .base import db

from pony.orm import *


class Submission(db.Entity):
    id = PrimaryKey(int, auto=True)
    submission_id = Required(str)
    created_at = Required(datetime, sql_default='CURRENT_TIMESTAMP')
    status = Required(str)
    original_submission_id = Optional(str)


class LinkSubmission(Submission):
    url = Required(str)


class SelfSubmission(Submission):
    wiki_article_name = Required(str)
    revision_id = Required(str)
    last_updated = Required(datetime)
