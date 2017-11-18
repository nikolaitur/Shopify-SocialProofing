import shopify
import logging

from django.conf import settings
from .models import StoreSettings, Store, Modal, ModalTextSettings

logger = logging.getLogger(__name__)


def authenticate(request):
    """
    Authenticates user requests to the app.

    :param request: Django Request Object
    :return:        Shopify session with shop name.
    """
    shopify.Session.setup(api_key=settings.API_KEY, secret=settings.API_SECRET)

    try:
        params = parse_params(request)
        session = shopify.Session(params['shop'])
        if settings.DEVELOPMENT_MODE == 'PRODUCTION':
            if not session.validate_params(params=params):
                raise Exception('Invalid HMAC: Possibly malicious login')

        return session
    except Exception as e:
        logger.error(e)
        raise Exception('Failed to authenticate request')


def parse_params(request):
    """
    Parse authentication GET parameters.
    """
    try:
        if request.method == 'GET':
            params = {}

            if 'code' in request.GET:
                params['code'] = request.GET['code']
            if 'hmac' in request.GET:
                params['hmac'] = request.GET['hmac']
            if 'locale' in request.GET:
                params['locale'] = request.GET['locale']
            if 'protocol' in request.GET:
                params['protocol'] = request.GET['protocol']
            if 'shop' in request.GET:
                params['shop'] = request.GET['shop']
            if 'timestamp' in request.GET:
                params['timestamp'] = request.GET['timestamp']

        # For development only. Set up a dummy shop parameter if it doesn't exist in URL
        if settings.DEVELOPMENT_MODE == 'TEST' and 'shop' not in request.GET:
            params['shop'] = 'michael-john-devs.myshopify.com'

        return params
    except Exception as e:
        logger.error(e)
        raise Exception('Failed to parse URI parameters')


def populate_default_settings(store_name):
    """
    Populate db with default settings
    """

    default_look_back = 1440        # Look back in seconds
    default_modal_text_id = 0       # Modal text id in database
    default_duration = 5            # Modal popup duration
    default_location = 'top-right'  # Default modal location
    default_color = '#4286f4'       # Default modal color

    default_modal_text_settings = ModalTextSettings.objects.get(modal_text_id=default_modal_text_id)

    try:
        store = Store.objects.get(store_name=store_name)
    except Store.DoesNotExists:
        store = store.objects.create(store_name=store_name)

    StoreSettings.objects.create(look_back=default_look_back, store=store)

    Modal.objects.create(store=store,
                         modal_text_settings=default_modal_text_settings,
                         location=default_location,
                         color=default_color,
                         duration=default_duration,
                         )
