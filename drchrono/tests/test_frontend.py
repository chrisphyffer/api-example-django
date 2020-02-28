from django.test import TestCase
from django.test import Client
from django.urls import reverse

class FrontendTests(TestCase):
    def test_frontend_settings(self):
        response = self.client.get(reverse('frontend_client_settings'))
        self.assertContains(response, 'success')