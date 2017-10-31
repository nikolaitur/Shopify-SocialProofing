from django.test import TestCase, Client
from django.core.urlresolvers import reverse

import fnmatch


class AuthenticationTests(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.client = Client()

    def test_valid_shop_redirects(self):
        # Test that we return the correct redirect for a valid shop url
        response = self.client.get(reverse('authenticate_app'), SERVER_NAME='mystore.myshopify.com')

        # Valid url should redirect
        self.assertEqual(response.status_code, 302)

        # The permission url should match the following pattern
        self.assertTrue(fnmatch.fnmatch(response.url,
                                        'https://mystore.myshopify.com/admin/oauth/authorize'
                                        '?client_id=*&scope=*&redirect_uri=*'))


class DevelopmentToProductionDeploymentTest(TestCase):
    def test_development_settings_turned_off(self):
        pass
