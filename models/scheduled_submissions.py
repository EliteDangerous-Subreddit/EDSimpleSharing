import datetime

from models.base import db
from pony.orm import *


class ScheduledSubmission(db.Entity):
    id = PrimaryKey(int, auto=True)
    submission = Required("Submission")
    scheduled_time = Required(datetime)
