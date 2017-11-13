import logging
from urllib.parse import urlparse

import shopify
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import loader
from django.views.decorators.clickjacking import xframe_options_exempt

from app.utils import authenticate, parse_params
from .models import Store, StoreSettings

logger = logging.getLogger(__name__)


@xframe_options_exempt
def index(request):
    """
    This view is the entry point for our app in the store owner admin page.
    Redirects store owner to correct view based on account status.
    """

    try:
        session = authenticate(request)
        params = parse_params(request)
        store_name = params['shop']

        exists_in_store_settings_table = StoreSettings.objects.filter(store__store_name=store_name).exists()
        exists_in_store_table = Store.objects.filter(store_name=store_name).exists()

        if exists_in_store_table and not exists_in_store_settings_table:
            # Registered app but did not setup store settings yet
            return HttpResponseRedirect(reverse('wizard'))
        elif exists_in_store_table and exists_in_store_settings_table:
            # Registered app and set up store
            return HttpResponseRedirect(reverse('dashboard'))
        else:
            # Redirect to install page
            return HttpResponseRedirect(reverse('install'))

    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest(e)


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
        return HttpResponseBadRequest(e)


def auth_callback(request):
    """
    After the user has approved our app, they are redirected from Shopify to us with a temporary code.
    We use this temporary code in exchange for a permanent one with offline access and store it in our db.
    """
    try:

        session = authenticate(request)
        params = parse_params(request)
        token = session.request_token(params)
        print('Received permanent token: {}'.format(token))

        # Store permanent token or update if exists in db
        store, created = Store.objects.update_or_create(store_name=params['shop'], defaults={'permanent_token': token})

        # Return the user back to their shop
        return redirect('https://' + params['shop'])
    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest(e)


@xframe_options_exempt
def wizard(request):
    """
    Setup wizard.
    """
    params = parse_params(request)
    return HttpResponse('setup wizard.')


@xframe_options_exempt
def store_settings(request):
    """
    App settings.
    """
    params = parse_params(request)
    return HttpResponse('Settings page.')


@xframe_options_exempt
def dashboard(request):
    """
    Analytics dashboard.
    """
    params = parse_params(request)
    template = loader.get_template('app/index.html')
    try:
        shop = params['shop']

        context = {
            'api_key': settings.API_KEY,
            'shop': shop,
        }

        return HttpResponse(template.render(context, request))
    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest(e)
