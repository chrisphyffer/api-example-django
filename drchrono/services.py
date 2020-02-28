import time
import pytz
from datetime import datetime

from django.conf import settings
from django.utils import timezone
from social_django.models import UserSocialAuth
from drchrono.endpoints import PatientEndpoint
from drchrono.endpoints import AppointmentEndpoint
from drchrono.models import Appointment

class ChronoOauth:
    @staticmethod
    def get_token():
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']
        return access_token

class PatientService:
    @staticmethod
    def find_patient_by_name(first_name, last_name):
        """
        Find's a Patient By Name.
        Assuming Dr. Chrono's Patient Record Name entries are capitalized.
        """
        params = {
            'first_name' : first_name.lower().capitalize(),
            'last_name' : last_name.lower().capitalize()
        }
        
        try: 
            api_patient = PatientEndpoint(ChronoOauth.get_token())
            patient = next(api_patient.list(params=params))
        except StopIteration:
            return None

        return patient

class AppointmentService:
    @staticmethod
    def verify_patient_has_appointment(params):
        """
        Verify that a patient has a confirmed appointment with the doctor before
        asking for their Demographics information.
        
        parameters = {
            'patient_id',
            'first_name',
            'last_name',
            'appointment_id',
            'override_late'  # Will not exclude this appointment from 
            }
        """

        current_date = datetime.now().strftime("%Y-%m-%d")

        # Check if the patient actually exists.
        patient_api = PatientEndpoint(ChronoOauth.get_token())
        patient = None
        if 'patient_id' in params:
            patient = patient_api.fetch(id = params['patient_id'])
        elif 'first_name' in params and 'last_name' in params:
            patient = PatientService.find_patient_by_name(params['first_name'], params['last_name'])

        if not patient:
            return {
                'error' : 'Patient not found in the Doctor\'s database.'
            }

        
        api_appt = AppointmentEndpoint(ChronoOauth.get_token())
        if 'appointment_id' in params and params['appointment_id']:
            """
            Check a patient into a specific appointment.
            """
            target_appointment = api_appt.fetch(id=params['appointment_id'])
            
        else:
            """
            Grab a list of the nearest available Appointment.
            """

            current_appointments = api_appt.list(date=current_date)
            current_appointments_list = list(current_appointments)

            # Determine whether a patient can be seen by the doctor.
            # The api automatically sorts the schedules by the time.
            #TODO: Do not yet factor Early Checkin or Late Arrivals. Just deal with a single status.
            target_appointment = None
            for appointment in current_appointments_list:

                # If a patient has multiple schedules throughout the day,
                # that patient cannot be 'checked_in' twice.
                if appointment['patient'] == patient['id'] and \
                    appointment['status'] in settings.DRCHRONO_VALID_SEEABLE_PATIENTS:
                    break

                if appointment['patient'] == patient['id'] and \
                    appointment['status'] in settings.DRCHRONO_VALID_APPOINTMENTS:

                    # No time to debug this extra functionality...
                    #if 'override_late' not in params or not params['override_late']:
                    #    # If this appointment time is later than the Doctors Practice's
                    #    # Late limit, then skip this appointment.
                    #    scheduled_time = datetime.strptime (appointment['scheduled_time'], "%Y-%m-%dT%H:%M:%S")
                    #    schedule_epoch = (scheduled_time - datetime(1970, 1, 1)).total_seconds()
                    #
                    #    late_time = time.time() - schedule_epoch
                    #    if late_time > settings.PATIENT_LATE_CUTOFF_TIME*60:
                    #        print('wut? {} {}'.format(late_time, settings.PATIENT_LATE_CUTOFF_TIME))
                    #        continue
                    
                    target_appointment = appointment
                    break

                elif appointment['patient'] == patient['id']:
                    pass

        if not target_appointment:
            return {
                'error' : 'Were sorry, it appears you have either: not confirmed an appointment, '+\
                        'have already checked in, are Late (over {} Minutes), rescheduled, etc'.\
                            format(settings.PATIENT_LATE_CUTOFF_TIME)
            }

        return target_appointment

    @staticmethod
    def synchronize_appointments_db(appointments_list):
        """
        Grab Appointments that have not yet been set to 'In Session' / 'Completed' / Etc
        """
        local_db_appointments = Appointment.objects.filter(time_spent_waiting = 0).all()
        for i in range(len(appointments_list)):
            found_local_db_appt = False
            for local_db_appointment in local_db_appointments:
                if local_db_appointment.appt_id == appointments_list[i]['id']:
                    appointments_list[i]['date_checked_in'] = local_db_appointment.date_checked_in
                    found_local_db_appt = True
                    break
            
            if not found_local_db_appt and appointments_list[i]['status'] in settings.DRCHRONO_VALID_SEEABLE_PATIENTS:
                appointment_checkin = Appointment()
                appointment_checkin.appt_id = appointments_list[i]['id']
                # Did not get a response from Chrono Team in regards to date handling, so doing it custom.
                appointment_checkin.date_checked_in = timezone.now()
                appointment_checkin.save()

                appointments_list[i]['date_checked_in'] = appointment_checkin.date_checked_in