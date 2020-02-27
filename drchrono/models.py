from django.utils import timezone
from django.db import models

import time
import datetime
import pytz

class Appointment(models.Model):
    appt_id = models.CharField(max_length=120)
    date_checked_in = models.DateTimeField('Date Updated To Arrived or Checked In')
    time_spent_waiting = models.IntegerField(default=0)

    # DO NOT USE INIT FOR DJANGO MODELS...
    # https://stackoverflow.com/questions/5290001/object-has-no-attribute-state
    # def __init__(self, appt_id):

    def set_time_spent_waiting(self):
        # get date in UTC epoch seconds, 
        # subtracted by current date in UTC epoch seconds
        checked_in_epoch = (self.date_checked_in - datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()
        self.time_spent_waiting = time.time() - checked_in_epoch
        self.date_session_started = timezone.now()
        pass

    def __str__(self):
        return 'Appointment #{} Checked in: {}'.format(self.appt_id, self.date_checked_in)
    def __repr__(self):
        return {
            'appt_id' : self.appt_id,
            'date_checked_in' : self.date_checked_in,
            'time_spent_waiting' : self.time_spent_waiting
        }