from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from urllib.parse import urlparse, parse_qs

import shopify
import os

API_KEY = os.environ.get('API_KEY')
API_SECRET = os.environ.get('API_SECRET')


def authenticate_app(request):
    """
    If the user goes to this view, it would redirect them to the shopify page to authenticate our app.
    :param request: HTTPRequest object
    :return:        Redirect to shopify page to authenticate our app
    """
    redirect_uri = 'http://protected-reef-37693.herokuapp.com/auth/callback'
    scope = ['write_products', 'read_products']

    shopify.Session.setup(api_key=API_KEY, secret=API_SECRET)

    shop = urlparse(request.build_absolute_uri())[1]

    # instantiate shop session
    session = shopify.Session(shop)

    permission_url = session.create_permission_url(scope=scope, redirect_uri=redirect_uri)

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

    # Return the user back to their shop
    return redirect(params['shop'])