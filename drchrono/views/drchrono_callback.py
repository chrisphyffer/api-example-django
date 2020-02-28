import hashlib
import hmac

from django.conf import settings
from django.http import JsonResponse

"""
Webhook would notify frontend via socket concerning
Patient updates or Appointment updates. No need for now
as we're not building a socket client<>server.
OR... we can retrieve all of our appointments to the Doctor's Local Server,
And have this webhook simply update our database, to forgo the need to constantly
Ping the Dr.Chrono API for a list of appointments. But I would have to install 
the localhost https on my machine for this hackathon and I'm not doing that. (yet)
"""

def verify(request):
    secret_token = hmac.new(settings.WEBHOOK_SECRET_TOKEN, request.GET['msg'], hashlib.sha256).hexdigest()
    return JsonResponse({
        'secret_token': secret_token
    })

def callback(request):
    return JsonResponse({
        'ok' : 'true'
    })