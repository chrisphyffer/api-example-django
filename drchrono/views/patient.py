import json

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from drchrono.models import Appointment
from drchrono.endpoints import PatientEndpoint
from drchrono.services import ChronoOauth
from drchrono.utils.exceptions import NotFound
from drchrono.services import PatientService

@csrf_exempt
def fetch(request, patient_id):
    """
    Fetch a patient by ID
    """
    api = PatientEndpoint(ChronoOauth.get_token())
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
def find_patient_by_name_view(request):
    """
    View Wrapper for patient.find_patient_by_name()
    """
    # Verify our Request Object has all the paremeters required.
    try:
        json_post = json.loads(request.body)
        first_name = json_post['first_name'],
        last_name = json_post['last_name']
    except Exception, e:
        print(e)
        return JsonResponse({
            'error': '0949nONE There is an Error with the Request Data.'
        })

    try:
        patient = PatientService.find_patient_by_name(first_name, last_name)
    except Exception, e:
        print(e)
        return JsonResponse({
            'error' : '094NDASI1! There was an issue finding the patient by name.'
        })

    return JsonResponse({
        'Success' : True,
        'patient' : patient
    })
    