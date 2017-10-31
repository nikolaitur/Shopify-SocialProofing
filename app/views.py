from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from urllib.parse import urlparse, parse_qs

import shopify
import os

API_KEY = os.environ.get('API_KEY')
API_SECRET = os.environ.get('API_SECRET')


def index(request):
    redirect_uri = 'http://protected-reef-37693.herokuapp.com/auth/callback'
    scope = ['write_products', 'read_products']

    shopify.Session.setup(api_key=API_KEY, secret=API_SECRET)

    shop = urlparse(request.build_absolute_uri())[1]
    shop = 'https://michael-john-devs.myshopify.com'  # For TEST. Turn off in production
    print('The parsed shop is {}'.format(shop))

    # instantiate shop session
    session = shopify.Session(shop)

    permission_url = session.create_permission_url(scope=scope, redirect_uri=redirect_uri)

    print('Permission url is {}'.format(permission_url))

    return redirect(permission_url)


def retrieve_token(request):
    # Parse callback url
    shopify.Session.setup(api_key=API_KEY, secret=API_SECRET)

    params = {
        'code': request.GET['code'],
        'timestamp': request.GET['timestamp'],
        'hmac': request.GET['hmac'],
        'shop': request.GET['shop']
    }

    print(params)

    # Fetch permanent token
    session = shopify.Session(params['shop'])
    token = session.request_token(params)

    print('Received permanent token: {}'.format(token))

    return redirect('http://google.com')
