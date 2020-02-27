from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from social_django.models import UserSocialAuth
from drchrono.endpoints import DoctorEndpoint
from drchrono.endpoints import AppointmentEndpoint
from drchrono.endpoints import PatientEndpoint
from drchrono.utils import chrono_oauth
from drchrono.utils.exceptions import NotFound
from drchrono.models import Appointment
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

"""
    check_in_patient()

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
@csrf_exempt
def check_in_patient(request):
    try:
        json_post = json.loads(request.body)

        if 'id' in json_post:
            params = {
                'id' : json_post['id']
            }
            print(params['id'])
        else:
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
        if params['id']:
            patient = api_patient.fetch(id=params['id'])
        else:
            patient = next(api_patient.list(params=params))
    except Exception, e:
        print(e)
        if params['id']:
            patient_name = '#{}'.format(params['id'])
        else:
            patient_name = '{} {}'.format(params['first_name'], params['last_name'])

        return JsonResponse({
            'error' : "NKMINAO2 Error retrieving Patient {} from the Dr. Chrono Database".\
                        format(patient_name)
        })

    print(patient)
    print('----------')
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

    appointment = Appointment.objects.filter(appt_id=target_appointment['id'])
    if appointment.count():
        appointment = appointment[0]
        appointment.appt_id = target_appointment['id']
        appointment.date_checked_in = timezone.now()
        appointment.save()
    else:
        appointment = Appointment()
        appointment.appt_id = target_appointment['id']
        appointment.date_checked_in = timezone.now()
        appointment.save()

    return JsonResponse({
                'success' : True    
            })

# List Today's Appointments
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

    # Grab Appointments that have not yet been set to 'In Session' / 'Completed' / Etc
    local_db_appointments = Appointment.objects.filter(time_spent_waiting = 0).all()
    for i in range(len(appointments_list)):
        for local_db_appointment in local_db_appointments:
            if local_db_appointment.appt_id == appointments_list[i]['id']:
                appointments_list[i]['date_checked_in'] = local_db_appointment.date_checked_in
                break


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

    appt_db = Appointment.objects.filter(appt_id=appointment_id).first()
    if appointment:
        appointment['date_checked_in'] = appt_db.date_checked_in

    return JsonResponse({
            'success' : True,
            'appointment' : appointment
        })

@csrf_exempt
def begin_appointment(request, appointment_id):
    api_appt = AppointmentEndpoint(chrono_oauth.get_token())
    api_appt.update(appointment_id, {'status' : 'In Session' })

    appointment = Appointment.objects.filter(appt_id=appointment_id)
    if appointment.count():
        appointment = appointment[0]
        appointment.set_time_spent_waiting()
        appointment.save()

    return JsonResponse({
            'success' : True
        }
    )

@csrf_exempt
def total_wait_time_since_epoch(request):
    all_appointments = Appointment.objects.all()
    total_wait_time = 0

    for appt in all_appointments:
        total_wait_time += appt.time_spent_waiting

    return JsonResponse({
        'success' : True,
        'total_wait_time' : total_wait_time
    })

# Webhook would notify frontend via socket concerning
# Patient updates or Appointment updates. No need for now
# as we're not building a socket client<>server.

# OR... we can retrieve all of our appointments to the Doctor's Local Server,
# And have this webhook simply update our database, to forgo the need to constantly
# Ping the Dr.Chrono API for a list of appointments. But I would have to install 
# the localhost https on my machine for this hackathon and I'm not doing that. (yet)
def webhook_callback(request):
    pass