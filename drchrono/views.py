from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from social_django.models import UserSocialAuth
from drchrono.endpoints import DoctorEndpoint
from drchrono.endpoints import AppointmentEndpoint
from drchrono.endpoints import PatientEndpoint
from drchrono.utils import chrono_oauth
from drchrono.utils.exceptions import NotFound
from datetime import datetime
import json

class SetupView(TemplateView):
    """
    The beginning of the OAuth sign-in flow. Logs a user into the kiosk, and saves the token.
    """
    template_name = 'kiosk_setup.html'


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
        access_token = chrono_oauth.get_token()
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



#TODO: It appears that the Dr.Chrono patient_list endpoint 
# does not have a query for matching patients with scheduled day.
@csrf_exempt
def fetch_patient(request, patient_id):
    api = PatientEndpoint(chrono_oauth.get_token())
    try:
        patient = api.fetch(id = patient_id)
    except NotFound:
        return JsonResponse({
                'error' : "ONFLNEM1 Patient #{} was not found in the Dr. Chrono Database".format(patient_id)
            })
    except Exception, e:
        print(e)
        return JsonResponse({
                'error' : "ONFLNEM1 Issue fetching Patient #{} from the Dr. Chrono Database".format(patient_id)
            })

    return JsonResponse({
            'success' : True,
            'patient' : patient
        })

@csrf_exempt
def check_in_patient(request):
    # Post Request to check in the patient.
    """
        If our Patient has a scheduled appointment, we will look up this patient
        from our list of appointments and change their status to 'Arrived'.

        If patient is not new...then do nothing, that will be an extra feature...


        This patient could have multiple times scheduled throuhgout the same day.
        A Patient Could Arrive Late. 
            > An appointment may automatically be cancelled if the patient is more than X minutes late.
            > If the patient has multiple meetings, and misses the first meeting (due to > x minutes), 
                that first meeting is cancelled, and they must wait for their next meeting.
            > If the patient is EARLY to their scheduled meeting, the wait time will not start until
                the patient's Scheduled time.
    """

    try:
        json_post = json.loads(request.body)

        params = {
                    'first_name' : json_post['first_name'], 
                    'last_name' : json_post['last_name']
                }
    except Exception, e:
        print(e)
        return JsonResponse({
            'error': '0949nONE There is an Error with the Request Data.'
        })

    api_appt = AppointmentEndpoint(chrono_oauth.get_token())
    api_patient = PatientEndpoint(chrono_oauth.get_token())
    current_date = datetime.now().strftime("%Y-%m-%d")

    try: 
        current_appointments = api_appt.list(date=current_date)
        current_appointments_list = list(current_appointments)
    except Exception, e:
        print(e)
        return JsonResponse({
            'error': 'DLNEO!02 There was an error retrieving the current appointments list.'
        })

    try:
        patient = next(api_patient.list(params=params))
    except Exception, e:
        print(e)
        return JsonResponse({
            'error' : "NKMINAO2 Error retrieving Patient {} {} from the Dr. Chrono Database".format(\
                                params['first_name'], params['last_name'])
        })

    #TODO: Do not yet factor Early Checkin or Late Arrivals. Just deal with a single status.
    target_appointment = None
    for appointment in current_appointments_list:
        print(appointment)
        if appointment['patient'] == patient['id'] and \
            (appointment['status'] == 'Confirmed' or appointment['status'] == 'Arrived' ):
            target_appointment = appointment
            break

        elif appointment['patient'] == patient['id']:
            pass

    if not target_appointment:
        return JsonResponse({
            'error' : 'Were sorry, it appears you haven\'t confirmed an appointment with us today, '+\
                      'you have already checked in, rescheduled, etc'
        })

    try:
        api_appt.update(target_appointment['id'], {'status':'Checked In'})
    except Exception, e:
        print(e)
        return JsonResponse({
            'error' : 'DOEEN21)1 There was an error updating your schedule, please check with our Staff.'
        })

    return JsonResponse({
                'success' : True    
            })

@csrf_exempt
def list_appointments(request):

    api_appt = AppointmentEndpoint(chrono_oauth.get_token())
    current_date = datetime.now().strftime("%Y-%m-%d")
    try:
        
        appointments_data = api_appt.list(date=current_date)
        appointments_list = list(appointments_data)
    except Exception, e:
        print(e)
        return JsonResponse(
            {
                'error' : 'D))0000MNN Could not fetch Appointments List.'
            })

    return JsonResponse(
        {
            'success' : True, 
            'appointments' : list(appointments_list)
        })

@csrf_exempt
def fetch_appointment(request, appointment_id):
    api = AppointmentEndpoint(chrono_oauth.get_token())
    try:
        appointment = api.fetch(id = appointment_id)
    except NotFound:
        return JsonResponse(
            {
                'error' : "00101012992 Appointment #{} was not found in the Dr. Chrono Database".format(appointment_id)
            })

    return JsonResponse(
        {
            'success' : True,
            'appointment' : appointment
        })

@csrf_exempt
def begin_appointment(request, appointment_id):
    api_appt = AppointmentEndpoint(chrono_oauth.get_token())
    api_appt.update(appointment_id, {'status' : 'In Session' })
    return JsonResponse(
        {
            'success' : True
        }
    )

# Webhook would notify frontend via socket concerning
# Patient updates or Appointment updates. No need for now
# as we're not building a socket client<>server.

# OR... we can retrieve all of our appointments to the Doctor's Local Server,
# And have this webhook simply update our database, to forgo the need to constantly
# Ping the Dr.Chrono API for a list of appointments. But I would have to install 
# the localhost https on my machine for this hackathon and I'm not doing that. (yet)
def webhook_callback(request):
    pass