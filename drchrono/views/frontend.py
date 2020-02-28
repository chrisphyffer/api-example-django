from django.conf import settings
from django.http import JsonResponse

def frontend_client_settings(request):
    return JsonResponse({
        'success' : True,
        'DRCHRONO_VALID_SEEABLE_PATIENTS' : settings.DRCHRONO_VALID_SEEABLE_PATIENTS,
        'DRCHRONO_CLOSED_APPOINTMENTS' : settings.DRCHRONO_CLOSED_APPOINTMENTS,
        'DRCHRONO_VALID_APPOINTMENTS' : settings.DRCHRONO_VALID_APPOINTMENTS,
        'PATIENT_LATE_CUTOFF_TIME' : settings.PATIENT_LATE_CUTOFF_TIME*60
    })