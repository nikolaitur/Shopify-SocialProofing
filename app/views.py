import logging
from urllib.parse import urlparse

import shopify
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.template import loader
from django.views.decorators.clickjacking import xframe_options_exempt

from .utils import authenticate, parse_params, populate_default_settings
from .decorators import shop_login_required, api_authentication
from .models import Store, StoreSettings, Modal, ModalTextSettings
from django.core import serializers
from itertools import chain
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


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
        logger.info('Received permanent token: {} from {}'.format(token, params['shop']))

        request.session['shopify'] = {
            "shop_url": params['shop']
        }

        # Store permanent token or update if exists in db
        store, created = Store.objects.update_or_create(store_name=params['shop'], defaults={'permanent_token': token})

        # Return the user back to their shop
        return redirect('https://' + params['shop'])
    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest(e)


@xframe_options_exempt
def index(request):
    """
    This view is the entry point for our app in the store owner admin page.
    Redirects store owner to correct view based on account status.
    """

    try:
        session = authenticate(request)
        params = parse_params(request)

        request.session['shopify'] = {
            "shop_url": params['shop']
        }

        store_name = params['shop']

        exists_in_store_settings_table = StoreSettings.objects.filter(store__store_name=store_name).exists()
        exists_in_store_table = Store.objects.filter(store_name=store_name).exists()

        if not exists_in_store_table and not exists_in_store_settings_table:
            return HttpResponseRedirect(reverse('install'))

        if exists_in_store_table and not exists_in_store_settings_table:
            populate_default_settings(store_name)  # Populate store settings with defaults in db

        return HttpResponseRedirect(reverse('store_settings'))

    except Exception as e:
        logger.error(e)
        return HttpResponseBadRequest(e)


@xframe_options_exempt
@shop_login_required
def store_settings(request):
    """
    App settings.
    """
    params = parse_params(request)
    return HttpResponse('Settings page.')


@xframe_options_exempt
@shop_login_required
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


@xframe_options_exempt
@shop_login_required
@api_authentication
def store_settings_api(request, store_name):
    """
    Retrieve, update or delete store settings.
    """

    if request.method == 'GET':
        qs1 = Store.objects.filter(store_name=store_name)
        qs2 = StoreSettings.objects.filter(store__store_name=store_name)
        qs3 = Modal.objects.filter(store__store_name=store_name)

        merge = chain(qs1, qs2, qs3)

        qs_json = serializers.serialize('json', merge)
        return HttpResponse(qs_json, content_type='application/json')

    elif request.method == 'POST':
        params = {
            'look_back': request.POST.get('look_back', ''),
            'modal_text_settings': request.POST.get('modal_text_settings', ''),
            'location': request.POST.get('location', ''),
            'color': request.POST.get('color', ''),
            'duration': request.POST.get('duration', ''),
        }

        if any(y == '' for _, y in params.items()):  # All parameters must be provided
            logger.error('Bad request. Not all settings parameters provided.')
            return HttpResponseBadRequest('Bad request. Not all settings parameters provided.')

        # Update StoreSettings model
        obj = StoreSettings.objects.get(store__store_name=store_name)

        obj.look_back = params['look_back']
        obj.save()

        # Update Modal model
        obj = Modal.objects.get(store__store_name=store_name)
        modal_text_settings = ModalTextSettings.objects.get(modal_text_id=params['modal_text_settings'])

        obj.modal_text_settings = modal_text_settings  # Needs to be ModalTextSettings instance
        obj.location = params['location']
        obj.color = params['color']
        obj.duration = params['duration']
        obj.save()

        return HttpResponse('Success', status=200)

    return HttpResponseBadRequest(status=400)
