from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.conf import settings

import logging

logger = logging.getLogger(__name__)


def shop_login_required(func):
    def wrapper(request, *args, **kwargs):
        if settings.DEVELOPMENT_MODE == 'PRODUCTION':
            if not hasattr(request, 'session') or 'shopify' not in request.session:
                request.session['return_to'] = request.get_full_path()
                return redirect(reverse('install'))
        return func(request, *args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def api_authentication(func):
    # Session shop_url must match provided store_name in url

    def wrapper(request, store_name, *args, **kwargs):

        if settings.DEVELOPMENT_MODE == 'PRODUCTION':
            if store_name != request.session['shopify']['shop_url']:
                return HttpResponse(status=403)
        return func(request, store_name, *args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper
