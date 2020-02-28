import json
from datetime import datetime

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings

from drchrono.models import Appointment
from drchrono.endpoints import PatientEndpoint
from drchrono.endpoints import AppointmentEndpoint
from drchrono.services import ChronoOauth
from drchrono.services import PatientService
from drchrono.services import AppointmentService


@csrf_exempt
def cancel_appointment(request, appointment_id):
    """
    Cancel the Doctor / Patient Appointment.
    """
    api_appt = AppointmentEndpoint(ChronoOauth.get_token())
    api_appt.update(appointment_id, {'status' : 'Cancelled' })

    return JsonResponse({
            'success' : True
        })

@csrf_exempt
def begin_doctor_session(request, appointment_id):
    """
    Begin the Patient's appointment with the doctor.
    """
    api_appt = AppointmentEndpoint(ChronoOauth.get_token())
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
def verify_patient_has_appointment_view(request):
    """
    A view wrapper for AppointmentService.verify_patient_has_appointment(request)
    """
    json_post = json.loads(request.body)
    target_appointment = AppointmentService.verify_patient_has_appointment(params=json_post)
    if 'error' in target_appointment:
        return JsonResponse({
            'error' : target_appointment['error']
        })
    return JsonResponse({
        'success' : True,
        'appointment' : target_appointment
    })

@csrf_exempt
def check_in_patient(request):
    """
    If our Patient has a scheduled appointment, we will look up this patient
    from our list of appointments and change their status to `Checked In`

    Feature: 
    The Appointment that is closest to the actual time will be chosen.

    If patient is not new...then the system will reject since the patient does not have
    an appointment. 
    """

    # We must verify the patient's name and demographics.
    json_post = json.loads(request.body)

    # Verify if the patient has an appointment today.
    # This will return an appointment object and we can work off that.
    target_appointment = AppointmentService.verify_patient_has_appointment(params=json_post)
    if 'error' in target_appointment:
        return JsonResponse({
            'error' : target_appointment['error']
        })
        
    # Update our patient's demographic information
    demographic_fields = ['gender', 'preferred_language']
    patient_params = {}
    for demographic_field in demographic_fields:
        if demographic_field in json_post:
            patient_params[demographic_field] = json_post[demographic_field]

    api_patient = PatientEndpoint(ChronoOauth.get_token())
    api_patient.update(id=target_appointment['patient'], params=patient_params)

    # Update our Appointment Status.
    try:
        api_appt = AppointmentEndpoint(ChronoOauth.get_token())
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

@csrf_exempt
def list_today(request):
    """
    List Today's Appointments
    """
    api_appt = AppointmentEndpoint(ChronoOauth.get_token())
    current_date = datetime.now().strftime("%Y-%m-%d")
    try:
        appointments_data = api_appt.list(date=current_date)
        appointments_list = list(appointments_data)
    except Exception, e:
        print(e)
        return JsonResponse({
                'error' : 'D))0000MNN Could not fetch Appointments List.'
            })

    AppointmentService.synchronize_appointments_db(appointments_list)

    return JsonResponse({
            'success' : True, 
            'appointments' : list(appointments_list)
        })

@csrf_exempt
def list_today_status(request):
    """
    List Today's Appointment Statuses only.
    Even though the API gets the entire Appointment Data,
    Down the road, there will be an opportunity to get partial data.
    """
    api_appt = AppointmentEndpoint(ChronoOauth.get_token())
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

    AppointmentService.synchronize_appointments_db(appointments_list)

    # We just need the status from the appointments list.
    appointment_list_status = {}
    checked_in_list = {}
    for appointment in appointments_list:
        appointment_list_status[appointment['id']] = appointment['status']
        if appointment['status'] in settings.DRCHRONO_VALID_SEEABLE_PATIENTS:
            appointment_checkin = Appointment.objects.filter(appt_id=appointment['id']).first()
            if not appointment_checkin:
                appointment_checkin = Appointment()
                appointment_checkin.appt_id = appointment['id']
                appointment_checkin.date_checked_in = timezone.now()
                appointment_checkin.save()
            
            checked_in_list[appointment['id']] = appointment_checkin.date_checked_in

    return JsonResponse(
        {
            'success' : True, 
            'status' : appointment_list_status,
            'date_checked_in' : checked_in_list
        })

@csrf_exempt
def fetch(request, appointment_id):
    """
    Fetch an Appointment by `id`
    """
    api = AppointmentEndpoint(ChronoOauth.get_token())
    try:
        appointment = api.fetch(id = appointment_id)
    except NotFound:
        return JsonResponse(
            {
                'error' : "00101012992 Appointment #{} was not found in the Dr. Chrono Database".format(appointment_id)
            })

    appt_db = Appointment.objects.filter(appt_id=appointment_id).first()
    if appointment and appt_db:
        appointment['date_checked_in'] = appt_db.date_checked_in

    return JsonResponse({
            'success' : True,
            'appointment' : appointment
        })
