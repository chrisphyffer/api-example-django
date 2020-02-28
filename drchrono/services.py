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
        Find's a Patient By Name
        """
        params = {
            'first_name' : first_name,
            'last_name' : last_name
        }

        # Uppercase name, try different combinations of search.
        
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
        """

        current_date = datetime.now().strftime("%Y-%m-%d")

        # Check if the patient actually exists.
        patient_api = PatientEndpoint(ChronoOauth.get_token())
        if 'id' in params:
            patient = patient_api.fetch(id = params['id'])
        elif 'first_name' in params and 'last_name' in params:
            patient = PatientService.find_patient_by_name(params['first_name'], params['last_name'])

        if not patient:
            return {
                'error' : 'Patient not found in the Doctor\'s database.'
            }

        # Grab a list of our Current Appointments.
        api_appt = AppointmentEndpoint(ChronoOauth.get_token())
        current_appointments = api_appt.list(date=current_date)
        current_appointments_list = list(current_appointments)

        # Determine whether a patient can be seen by the doctor.
        #TODO: Do not yet factor Early Checkin or Late Arrivals. Just deal with a single status.
        target_appointment = None
        for appointment in current_appointments_list:
            if appointment['patient'] == patient['id'] and \
                appointment['status'] in settings.DRCHRONO_VALID_APPOINTMENTS:
                target_appointment = appointment
                break

            elif appointment['patient'] == patient['id']:
                pass

        if not target_appointment:
            return {
                'error' : 'Were sorry, it appears you have either: not confirmed an appointment with us today, '+\
                        'have already checked in, rescheduled, etc'
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
                local_appt_db = Appointment()
                local_appt_db.appt_id = appointments_list[i]['id']
                # Did not get a response from Chrono Team in regards to date handling, so doing it custom.
                local_appt_db.date_checked_in = timezone.now()
                local_appt_db.save()

                appointments_list[i]['date_checked_in'] = local_appt_db.date_checked_in