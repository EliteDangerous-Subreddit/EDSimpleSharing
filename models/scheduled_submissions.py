import datetime

from models.base import db
from pony.orm import *


class ScheduledSubmission(db.Entity):
    id = PrimaryKey(int, auto=True)
    title = Required(str)
    body = Required(LongStr)
    submission_type = Required(str)
    scheduled_time = Required(datetime)
