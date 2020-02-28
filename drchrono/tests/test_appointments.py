import json
from django.http import HttpResponse
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from drchrono.models import Appointment

class AppointmentTests(TestCase):
    def test_appointment_wait_time_total(self):
        pass