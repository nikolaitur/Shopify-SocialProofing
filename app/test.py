from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.conf import settings
from .models import StoreSettings

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

    def test_debug_is_off(self):
        if settings.DEVELOPMENT_MODE == 'PRODUCTION':
            self.assertTrue(settings.DEBUG, False)

    def test_app_url_is_not_localhost_nor_test_site(self):
        if settings.DEVELOPMENT_MODE == 'PRODUCTION':
            self.assertTrue('127.0.0.1' not in settings.APP_URL, 'App URL should not be pointed to localhost.')
            self.assertTrue('protected-reef-37693' not in settings.APP_URL,
                            'App URL should not be pointed to test site.')


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

        with self.settings(DEVELOPMENT_MODE='TEST'):
            response = self.client.get(
                reverse('index') + '?hmac=123&locale=123&protocol=123&shop={}&timestamp=123'.format(shop))
        self.assertRedirects(response, expected_url=reverse('install'), status_code=302, fetch_redirect_response=False)

    def test_registered_store_and_not_setup(self):
        # Store registered app but not set up settings.
        shop = 'not-setup-store.myshopify.com'

        with self.settings(DEVELOPMENT_MODE='TEST'):
            response = self.client.get(
                reverse('index') + '?hmac=123&locale=123&protocol=123&shop={}&timestamp=123'.format(shop))

        self.assertRedirects(response, expected_url=reverse('store_settings'), status_code=302,
                             fetch_redirect_response=False)

        # Default settings should be populated in STORE_SETTINGS table
        self.assertTrue(StoreSettings.objects.filter(store__store_name=shop).exists())

    def test_registered_and_setup(self):
        # Store registered app but not set up settings.
        shop = 'setup-store.myshopify.com'
        response = self.client.get(
            reverse('index') + '?hmac=123&locale=123&protocol=123&shop={}&timestamp=123'.format(shop))
        self.assertRedirects(response, expected_url=reverse('store_settings'), status_code=302,
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

            response = self.client.get(reverse('store_settings'))
            self.assertEqual(response.status_code, 200)

            # Reset self.client
            self.client = Client()

        with self.settings(DEVELOPMENT_MODE='PRODUCTION'):
            self.client.get(reverse('index') + '?hmac=123&locale=123&protocol=123&shop=123&timestamp=123')
            session = self.client.session

            response = self.client.get(reverse('store_settings'))
            self.assertRedirects(response, expected_url=reverse('install'), status_code=302,
                                 fetch_redirect_response=False)

            # Reset self.client
            self.client = Client()


class TestStoreSettingsAPI(TestCase):
    """
    Test Store Settings API View.
    """

    fixtures = ['entrypoint_fixture.json']

    def setUp(self):
        self.client = Client()

    def test_get_valid_request(self):
        with self.settings(DEVELOPMENT_MODE='TEST'):
            response = self.client.get(
                reverse('store_settings_api', kwargs={'store_name': 'not-setup-store.myshopify.com'}))
            self.assertEqual(response.status_code, 200)

        with self.settings(DEVELOPMENT_MODE='PRODUCTION'):
            # No cookies
            response = self.client.get(
                reverse('store_settings_api', kwargs={'store_name': 'not-setup-store.myshopify.com'}))
            self.assertEqual(response.status_code, 302)

            # TODO: Add unit test with cookies

    def test_post_valid_request(self):
        with self.settings(DEVELOPMENT_MODE='TEST'):
            for social_scope in settings.SOCIAL_SCOPES:
                response = self.client.post(
                    reverse('store_settings_api', kwargs={'store_name': 'setup-store.myshopify.com'}),
                    {'look_back': '24',
                     'location': 'top-left',
                     'color': '#FFFFF',
                     'duration': '5',
                     'social_scope': social_scope}
                )
                self.assertEqual(response.status_code, 200)

    def test_post_invalid_request_bad_social_scope(self):
        with self.settings(DEVELOPMENT_MODE='TEST'):
            response = self.client.post(
                reverse('store_settings_api', kwargs={'store_name': 'setup-store.myshopify.com'}),
                {'look_back': '24',
                 'location': 'top-left',
                 'color': '#FFFFF',
                 'duration': '5',
                 'social_scope': 'FOO'},
            )
            self.assertEqual(response.status_code, 400)


class TestRelatedProductsAPI(TestCase):
    """
    Test Related Products API
    """
    fixtures = ['entrypoint_fixture.json']

    def setUp(self):
        self.client = Client()

    def test_get_valid_request(self):
        with self.settings(DEVELOPMENT_MODE='PRODUCTION'):
            response = self.client.get(
                reverse('related_products_api', kwargs={'store_name': 'michael-john-devs.myshopify.com',
                                                        'product_id': '293835145247'}))
            self.assertEqual(response.status_code, 200)

    def test_get_invalid_request(self):
        response = self.client.get(
            reverse('related_products_api', kwargs={'store_name': 'michael-john-devs.myshopify.com',
                                                    'product_id': '11111'}))
        self.assertEqual(response.status_code, 200)


class TestModalAPI(TestCase):
    """
    Test Modal API
    """
    fixtures = ['entrypoint_fixture.json']

    def setUp(self):
        self.client = Client()

    def test_get_valid_request(self):
        response = self.client.get(
            reverse('modal_api', kwargs={'store_name': 'michael-john-devs.myshopify.com',
                                         'product_id': '293835145247', }))
        self.assertEqual(response.status_code, 200)

    def test_get_invalid_request(self):
        # Invalid product id
        response = self.client.get(
            reverse('modal_api', kwargs={'store_name': 'michael-john-devs.myshopify.com',
                                         'product_id': '11111111111', }))
        self.assertEqual(response.status_code, 200)

        # Store does not exist
        response = self.client.get(
            reverse('modal_api', kwargs={'store_name': 'this-store-does-not-exist.com',
                                         'product_id': '293835145247', }))
        self.assertEqual(response.status_code, 400)


class TestModalMetricsAPI(TestCase):
    """
    Test Modal Metrics API
    """
    fixtures = ['entrypoint_fixture.json']

    def setUp(self):
        self.client = Client()

    def test_get_valid_post_request(self):
        response = self.client.post(reverse('modal_metrics_api'),
                                    {'store_name': 'michael-john-devs.myshopify.com',
                                     'product_id_from': '293835145247',
                                     'product_id_to': '297692921887'})
        self.assertEqual(response.status_code, 200)

    def test_get_invalid_post_request(self):
        # Valid store, product that doesn't exist
        response = self.client.post(reverse('modal_metrics_api'),
                                    {'store_name': 'michael-john-devs.myshopify.com',
                                     'product_id_from': '22222222',
                                     'product_id_to': '111111111111'})
        self.assertEqual(response.status_code, 400)

        # Store that doesn't exist, valid products
        response = self.client.post(reverse('modal_metrics_api'),
                                    {'store_name': 'this-store-does-not-exist.com',
                                     'product_id_from': '293835145247',
                                     'product_id_to': '297692921887'})
        self.assertEqual(response.status_code, 400)

        # Valid store, valid product from but product to is a different store
        response = self.client.post(reverse('modal_metrics_api'),
                                    {'store_name': 'michael-john-devs.myshopify.com',
                                     'product_id_from': '293835145247',
                                     'product_id_to': '487347945514'})
        self.assertEqual(response.status_code, 400)

        # Not all parameters provided
        response = self.client.post(reverse('modal_metrics_api'),
                                    {'store_name': 'michael-john-devs.myshopify.com',
                                     'product_id_to': '487347945514'})
        self.assertEqual(response.status_code, 400)
