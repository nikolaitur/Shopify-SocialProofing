import logging
from urllib.parse import urlparse

import shopify
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.template import loader
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db.models import Sum

from .utils import authenticate, parse_params, populate_default_settings
from .decorators import shop_login_required, api_authentication
from .models import Store, StoreSettings, Modal, Orders, Product
from django.core import serializers
from itertools import chain
from django.utils import timezone
from datetime import timedelta
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
        store, created = Store.objects.update_or_create(store_name=params['shop'],
                                                        defaults={'permanent_token': token, 'active': True})

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
    template = loader.get_template('app/index.html')
    params = parse_params(request)
    return HttpResponse(template.render())


@xframe_options_exempt
@shop_login_required
@api_authentication
def store_settings_api(request, store_name):
    """
    Retrieve, update or delete store settings.
    """

    if request.method == 'GET':
        try:
            modal_obj = Modal.objects.filter(store__store_name=store_name).first()
            store_obj = Store.objects.filter(store_name=store_name).first()
            store_settings_obj = StoreSettings.objects.filter(store__store_name=store_name).first()

            response_dict = dict()
            response_dict['store_name'] = store_name
            response_dict['look_back'] = store_settings_obj.look_back

            response_dict['active'] = store_obj.active

            response_dict['social_setting'] = modal_obj.social_setting
            response_dict['color_brightness'] = modal_obj.color_brightness
            response_dict['color_hue'] = modal_obj.color_hue
            response_dict['color_saturation'] = modal_obj.color_saturation
            response_dict['size'] = modal_obj.size
            response_dict['location'] = modal_obj.location

            return JsonResponse(response_dict, safe=False)

        except Exception as e:
            logger.error(e)
            return HttpResponseBadRequest(e)

    elif request.method == 'POST':
        post_params = dict(request.POST.lists())

        try:
            store_settings_obj = StoreSettings.objects.get(store__store_name=store_name)
            modal_obj = Modal.objects.get(store__store_name=store_name)
        except Exception:
            return HttpResponseBadRequest('{} does not exist'.format(store_name), status=400)

        for key, value in post_params.items():
            if hasattr(store_settings_obj, key):
                setattr(store_settings_obj, key, value[0])
                store_settings_obj.save()
            if hasattr(modal_obj, key):
                setattr(modal_obj, key, value[0])
                modal_obj.save()

        return HttpResponse('Success', status=200)

    return HttpResponseBadRequest(status=400)


@xframe_options_exempt
@shop_login_required
@api_authentication
def orders_api(request, store_name):
    """
    Return all orders for a given store name, e.g. mystore.myshopify.com.
    """
    if request.method == 'GET':
        qs1 = Orders.objects.filter(store__store_name=store_name)
        qs_json = serializers.serialize('json', qs1)
        return HttpResponse(qs_json, content_type='application/json')

    return HttpResponseBadRequest('Invalid request')


@xframe_options_exempt
@shop_login_required
@api_authentication
def products_api(request, store_name):
    """
    Return all orders for a given store name, e.g. mystore.myshopify.com.
    """
    if request.method == 'GET':
        qs1 = Product.objects.filter(store__store_name=store_name)
        qs_json = serializers.serialize('json', qs1)
        return HttpResponse(qs_json, content_type='application/json')

    return HttpResponseBadRequest('Invalid request')


def modal_api(request, store_name, product_id):
    """
    Public modal api. Returns a json string with relevant modal information.
    """
    if request.method == 'GET':
        try:
            # Returned products should be within store's look_back parameter
            look_back = StoreSettings.objects.filter(store__store_name=store_name).values('look_back')[0]['look_back']
            time_threshold = timezone.now() - timedelta(seconds=look_back * 60 * 60)

            order_obj = Orders.objects \
                .filter(store__store_name=store_name) \
                .filter(product__product_id=product_id) \
                .filter(processed_at__range=[time_threshold, timezone.now()])
            order_obj_first = order_obj.first()
            modal_obj = Modal.objects.filter(store__store_name=store_name).first()

            response_dict = dict()
            response_dict['store_name'] = store_name
            response_dict['product_id'] = product_id

            response_dict['social_setting'] = modal_obj.social_setting
            response_dict['color_brightness'] = modal_obj.color_brightness
            response_dict['color_hue'] = modal_obj.color_hue
            response_dict['color_saturation'] = modal_obj.color_saturation
            response_dict['size'] = modal_obj.size
            response_dict['location'] = modal_obj.location

            response_dict['first_name'] = order_obj_first.first_name if hasattr(order_obj_first, 'first_name') else None
            response_dict['last_name'] = order_obj_first.last_name if hasattr(order_obj_first, 'last_name') else None
            response_dict['province_code'] = order_obj_first.province_code if hasattr(order_obj_first,
                                                                                      'province_code') else None
            response_dict['country_code'] = order_obj_first.country_code if hasattr(order_obj_first,
                                                                                    'country_code') else None
            response_dict['last_order_qty'] = order_obj_first.qty if hasattr(order_obj_first, 'qty') else None
            response_dict['processed_at'] = order_obj_first.processed_at if hasattr(order_obj_first,
                                                                                    'processed_at') else None
            response_dict['qty_from_look_back'] = order_obj.aggregate(Sum('qty'))['qty__sum']

            return JsonResponse(response_dict, safe=False)
        except Exception as e:
            logger.error(e)
            return HttpResponseBadRequest('Something went wrong.')

    return HttpResponseBadRequest('Invalid request')
