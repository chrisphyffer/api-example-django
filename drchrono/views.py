from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings

from social_django.models import UserSocialAuth

from drchrono.endpoints import DoctorEndpoint


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

    def get_token(self):
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']
        return access_token

    def make_api_request(self):
        """
        Use the token we have stored in the DB to make an API request and get doctor details. If this succeeds, we've
        proved that the OAuth setup is working
        """
        # We can create an instance of an endpoint resource class, and use it to fetch details
        access_token = self.get_token()
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

# Our webhook will call back this url and give data.
# OAuth Procedure - Auth server verifies authenticity of app using a `SECRET KEY`
# Belonging to you, like a user salt.
import hashlib, hmac


def chrono_api_callback(request):

    # TODO: Error catch invalid request parameters and log them.
    try:
        callback_message = bytearray(request.GET['msg'], 'utf-8')
    except:
        return JsonResponse({})

    secret_token = hmac.new(settings.WEBHOOK_SECRET_TOKEN, callback_message, hashlib.sha256).hexdigest()

    return JsonResponse(
        {
            'secret_token': str(secret_token)
        }
    )

@csrf_exempt
def frontend_api_call(request):
    return JsonResponse(
        {
            'success' : True
        }
    )