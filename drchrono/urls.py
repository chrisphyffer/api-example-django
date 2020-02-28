from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import admin
from drchrono.models import Appointment

from drchrono.views import appointment
from drchrono.views import patient
from drchrono.views import doctor
from drchrono.views import drchrono_setup
from drchrono.views import drchrono_callback
from drchrono.views import frontend

admin.autodiscover()
admin.site.register(Appointment)

urlpatterns = [ 

    # Have DR Chrono contact our endpoint.
    # url(r'^webhook-callback/', drchrono_callback.callback, name='webhook_callback'),

    # Have DR Chrono API Verify our webhook
    # url(r'^webhook-verify/', drchrono_callback.verify, name='webhook_verify'),



    # The frontend will get configuration settings from the server
    url(r'^frontend-client-settings/', frontend.frontend_client_settings, name='frontend_client_settings'),

    # Total Time of All Patients Doctor Has seen since the start of this system
    url(r'^total-patient-wait-time/', doctor.total_patient_wait_time, name='total_patient_wait_time'),

    # Verify the Patient has an existing appointment
    url(r'^verify-patient-has-appointment/', appointment.verify_patient_has_appointment_view, name='verify_patient_has_appointment'),

    # Check in the Patient
    url(r'^check-in-patient/', appointment.check_in_patient, name='check_in_patient'),

    # Look up Patient Information by ID
    url(r'^patient/(?P<patient_id>[0-9]+)/$', patient.fetch, name='fetch_patient'),

    # Cancel the appointment.
    url(r'^cancel-appointment/(?P<appointment_id>[\w\-]+)/$', appointment.cancel_appointment, name='cancel_appointment'),

    # Get the Appointment Status Only - For Refreshing the Frontend Appointments list.
    url(r'^appointments-status/$', appointment.list_today_status, name='appointment_list_status'),

    # Look up the Appointment by String ID (as specified in the Chrono API)
    url(r'^appointment/(?P<appointment_id>[\w\-]+)/$', appointment.fetch, name='fetch_appointment'),

    # Change the Status of the Appointment to 
    url(r'^begin-appointment/(?P<appointment_id>[\w\-]+)/$', appointment.begin_doctor_session, name='begin_appointment'),
    
    # Get the Appointment Listing
    url(r'^appointments/$', appointment.list_today, name='appointment_list'),

    url(r'^setup/$', drchrono_setup.SetupView.as_view(), name='setup'),
    url(r'^welcome/$', doctor.DoctorWelcome.as_view(), name='setup'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]