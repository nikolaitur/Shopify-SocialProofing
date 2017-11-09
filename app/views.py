from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from urllib.parse import urlparse, parse_qs
from django.template import loader
from django.views.decorators.clickjacking import xframe_options_exempt
from django.conf import settings
from django.contrib.staticfiles.templatetags import staticfiles

from .models import Stores

import shopify
import logging

logger = logging.getLogger(__name__)

@xframe_options_exempt
def index(request):
    """
    This view is the embedded app shown in their store.
    """
    shopify.Session.setup(api_key=settings.API_KEY, secret=settings.API_SECRET)
    template = loader.get_template('app/index.html')
    try:
        params = {
            'hmac': request.GET['hmac'],
            'locale': request.GET['locale'],
            'protocol': request.GET['protocol'],
            'shop': request.GET['shop'],
            'timestamp': request.GET['timestamp'],
        }

        session = shopify.Session(params['shop'])
        if settings.DEVELOPMENT_MODE == 'PRODUCTION':
            if not session.validate_params(params=params):
                raise Exception('Invalid HMAC: Possibly malicious login')

        context = {
            'api_key': settings.API_KEY,
            'shop': params['shop'],
        }

        return HttpResponse(template.render(context, request))
    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest('<h1>Something bad happened.</h1>')
    
def install(request):
    """
    Redirect user to the shopify page to authenticate our app.
    Example request from: https://mystore.myshopify.com
    """
    try:
        shopify.Session.setup(api_key=settings.API_KEY, secret=settings.API_SECRET)
        shop = urlparse(request.build_absolute_uri())[1]
        session = shopify.Session(shop)
        permission_url = session.create_permission_url(scope=settings.SHOPIFY_API_SCOPE,
                                                       redirect_uri=settings.SHOPIFY_AUTH_CALLBACK_URL)
        return redirect(permission_url)

    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest('<h1>Something bad happened.</h1>')


def auth_callback(request):
    """
    After the user has approved our app, they are redirected from Shopify to us with a temporary code.
    We use this temporary code in exchange for a permanent one with offline access and store it in our db.
    """
    shopify.Session.setup(api_key=settings.API_KEY, secret=settings.API_SECRET)

    try:
        params = {
            'code': request.GET['code'],
            'timestamp': request.GET['timestamp'],
            'hmac': request.GET['hmac'],
            'shop': request.GET['shop']
        }

        session = shopify.Session(params['shop'])
        token = session.request_token(params)
        print('Received permanent token: {}'.format(token))

        # Store permanent token or update if exists in db
        store, created = Stores.objects.update_or_create(store_name=params['shop'], defaults={'permanent_token': token})

        # Return the user back to their shop
        return redirect('https://' + params['shop'])
    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest('<h1>Something bad happened.</h1>')
