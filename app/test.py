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


class DevelopmentToProductionDeploymentTest(TestCase):
    """
    These tests ensure that the environment is correct when deploying to production.
    """

    def test_check_security_validation_is_on(self):
        # If environment variable is PRODUCTION, we should get bad response for bad requests
        if settings.DEVELOPMENT_MODE == 'PRODUCTION':
            response = self.client.get(reverse('index') + '?hmac=123&locale=123&protocol=123&shop=123&timestamp=123')
            self.assertEqual(response.status_code, 400)


class EntryPointTests(TestCase):
    """
    Tests app entry point redirects.
    """
    fixtures = ['entrypoint_fixture.json']

    def setUp(self):
        self.client = Client()

    def test_unregistered_store(self):
        # Store not registered app and not set up settings.
        shop = 'foobarbaz'
        response = self.client.get(
            reverse('index') + '?hmac=123&locale=123&protocol=123&shop={}&timestamp=123'.format(shop))
        self.assertRedirects(response, expected_url=reverse('install'), status_code=302, fetch_redirect_response=False)

    def test_registered_store_and_not_setup(self):
        # Store registered app but not set up settings.
        shop = 'not-setup-store.myshopify.com'
        response = self.client.get(
            reverse('index') + '?hmac=123&locale=123&protocol=123&shop={}&timestamp=123'.format(shop))
        self.assertRedirects(response, expected_url=reverse('wizard'), status_code=302, fetch_redirect_response=False)

    def test_registered_and_setup(self):
        # Store registered app but not set up settings.
        shop = 'setup-store.myshopify.com'
        response = self.client.get(
            reverse('index') + '?hmac=123&locale=123&protocol=123&shop={}&timestamp=123'.format(shop))
        self.assertRedirects(response, expected_url=reverse('dashboard'), status_code=302,
                             fetch_redirect_response=False)

    def test_check_security_validation_based_on_env(self):
        with self.settings(DEVELOPMENT_MODE='PRODUCTION'):
            response = self.client.get(reverse('index') + '?hmac=123&locale=123&protocol=123&shop=123&timestamp=123')
            self.assertEqual(response.status_code, 400)

        with self.settings(DEVELOPMENT_MODE='TEST'):
            response = self.client.get(reverse('index') + '?hmac=123&locale=123&protocol=123&shop=123&timestamp=123')
            self.assertIn(response.status_code, [200, 302])


class SessionTests(TestCase):
    """
    Test views security based on session.
    """

    def setUp(self):
        self.client = Client()

    def test_session_is_saved_based_on_env(self):
        with self.settings(DEVELOPMENT_MODE='TEST'):
            self.client.get(reverse('index') + '?hmac=123&locale=123&protocol=123&shop=123&timestamp=123')
            session = self.client.session
            self.assertEqual(session['shopify'], {'shop_url': '123'})

            # Reset self.client
            self.client = Client()

        with self.settings(DEVELOPMENT_MODE='PRODUCTION'):
            self.client.get(reverse('index') + '?hmac=123&locale=123&protocol=123&shop=123&timestamp=123')
            session = self.client.session
            self.assertEqual(session.get('shopify', None), None)

            # Reset self.client
            self.client = Client()

    def test_views_based_on_session(self):
        with self.settings(DEVELOPMENT_MODE='TEST'):
            self.client.get(reverse('index') + '?hmac=123&locale=123&protocol=123&shop=123&timestamp=123')
            session = self.client.session

            response = self.client.get(reverse('wizard'))
            self.assertEqual(response.status_code, 200)

            response = self.client.get(reverse('store_settings'))
            self.assertEqual(response.status_code, 200)

            response = self.client.get(reverse('dashboard'))
            self.assertEqual(response.status_code, 200)

            # Reset self.client
            self.client = Client()

        with self.settings(DEVELOPMENT_MODE='PRODUCTION'):
            self.client.get(reverse('index') + '?hmac=123&locale=123&protocol=123&shop=123&timestamp=123')
            session = self.client.session

            response = self.client.get(reverse('wizard'))
            self.assertRedirects(response, expected_url=reverse('install'), status_code=302,
                                 fetch_redirect_response=False)

            response = self.client.get(reverse('store_settings'))
            self.assertRedirects(response, expected_url=reverse('install'), status_code=302,
                                 fetch_redirect_response=False)

            response = self.client.get(reverse('dashboard'))
            self.assertRedirects(response, expected_url=reverse('install'), status_code=302,
                                 fetch_redirect_response=False)

            # Reset self.client
            self.client = Client()