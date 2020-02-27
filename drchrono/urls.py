from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import admin
admin.autodiscover()

from drchrono.models import Appointment
admin.site.register(Appointment)

import views

urlpatterns = [

    # Total Time of All Patients Doctor Has seen since the start of this system
    url(r'^total-wait-time-since-epoch/', views.total_wait_time_since_epoch, name='total_wait_time_since_epoch'),

    # Check in the Patient
    url(r'^check-in-patient/', views.check_in_patient, name='check_in_patient'),

    # Look up Patient Information by ID
    url(r'^patient/(?P<patient_id>[0-9]+)/$', views.fetch_patient, name='fetch_patient'),

    # Look up the Appointment by String ID (as specified in the Chrono API)
    url(r'^appointment/(?P<appointment_id>[\w\-]+)/$', views.fetch_appointment, name='fetch_appointment'),

    # Change the Status of the Appointment to 
    url(r'^begin-appointment/(?P<appointment_id>[\w\-]+)/$', views.begin_appointment, name='begin_appointment'),
    
    # Get the Appointment Listing
    url(r'^appointments/$', views.list_appointments, name='appointment_list'),

    url(r'^setup/$', views.SetupView.as_view(), name='setup'),
    url(r'^welcome/$', views.DoctorWelcome.as_view(), name='setup'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]