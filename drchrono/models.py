import time
import datetime
import pytz

from django.utils import timezone
from django.db import models

class Appointment(models.Model):
    appt_id = models.CharField(max_length=120)
    date_checked_in = models.DateTimeField('Date Updated To Arrived or Checked In')
    time_spent_waiting = models.IntegerField(default=0)

    def set_time_spent_waiting(self):
        # Called when our the doctor is seeing our patient. 
        # This function stops the patient waiting timer.
        checked_in_epoch = (self.date_checked_in - datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()
        self.time_spent_waiting = time.time() - checked_in_epoch
        self.date_session_started = timezone.now()

    def __str__(self):
        return 'Appointment #{} Checked in: {}'.format(self.appt_id, self.date_checked_in)

    def __repr__(self):
        return {
            'appt_id' : self.appt_id,
            'date_checked_in' : self.date_checked_in,
            'time_spent_waiting' : self.time_spent_waiting
        }

#class ChronoUpdates(models.Model):
#    pass