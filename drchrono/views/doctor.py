import json

from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from social_django.models import UserSocialAuth

from drchrono.endpoints import DoctorEndpoint
from drchrono.services import ChronoOauth

from drchrono.models import Appointment

class DoctorWelcome(TemplateView):
    """
    The doctor can see what appointments they have today.
    """
    template_name = 'doctor_welcome.html'

    def make_api_request(self):
        """
        Use the token we have stored in the DB to make an API request and get doctor details. If this succeeds, we've
        proved that the OAuth setup is working
        """
        # We can create an instance of an endpoint resource class, and use it to fetch details
        access_token = ChronoOauth.get_token()
        api = DoctorEndpoint(access_token)
        # Grab the first doctor from the list; normally this would be the whole practice group, but your hackathon
        # account probably only has one doctor in it.
        return next(api.list())

    # Django 1.x TemplateView entry point
    def get_context_data(self, **kwargs):
        kwargs = super(DoctorWelcome, self).get_context_data(**kwargs)
        # Hit the API using one of the endpoints just to prove that we can
        # If this works, then your oAuth setup is working correctly.
        doctor_details = self.make_api_request()
        kwargs['doctor'] = doctor_details
        return kwargs

@csrf_exempt
def total_patient_wait_time(request):
    all_appointments = Appointment.objects.all()
    total_wait_time = 0

    for appt in all_appointments:
        total_wait_time += appt.time_spent_waiting

    return JsonResponse({
        'success' : True,
        'total_wait_time' : total_wait_time
    })