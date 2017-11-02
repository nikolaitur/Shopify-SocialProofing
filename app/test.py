from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.conf import settings

import fnmatch


class AuthenticationTests(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.client = Client()

    def test_valid_shop_redirects(self):
        # Test that we return the correct redirect for a valid shop url
        response = self.client.get(reverse('install'), SERVER_NAME='mystore.myshopify.com')

        # Valid url should redirect
        self.assertEqual(response.status_code, 302)

        # The permission url should match the following pattern
        self.assertTrue(fnmatch.fnmatch(response.url,
                                        'https://mystore.myshopify.com/admin/oauth/authorize'
                                        '?client_id=*&scope=*&redirect_uri=*'))

    def test_check_security_validation_based_on_env(self):
        with self.settings(DEVELOPMENT_MODE='PRODUCTION'):
            response = self.client.get(reverse('index') + '?hmac=123&locale=123&protocol=123&shop=123&timestamp=123')
            self.assertEqual(response.status_code, 400)

        with self.settings(DEVELOPMENT_MODE='TEST'):
            response = self.client.get(reverse('index') + '?hmac=123&locale=123&protocol=123&shop=123&timestamp=123')
            self.assertEqual(response.status_code, 200)


class DevelopmentToProductionDeploymentTest(TestCase):
    """
    These tests ensure that the environment is correct when deploying to production.
    """

    def test_check_security_validation_is_on(self):
        # If environment variable is PRODUCTION, we should get bad response for bad requests
        if settings.DEVELOPMENT_MODE == 'PRODUCTION':
            response = self.client.get(reverse('index') + '?hmac=123&locale=123&protocol=123&shop=123&timestamp=123')
            self.assertEqual(response.status_code, 400)
