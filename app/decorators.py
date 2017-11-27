from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.conf import settings
from django.db.models import F
from .models import APIMetrics
from datetime import date
from django.core.urlresolvers import resolve
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


def track_statistics(func):
    # Session shop_url must match provided store_name in url

    def wrapper(request, *args, **kwargs):
        view = resolve(request.path_info).url_name
        snapshot_date = date.today()

        if request.method == 'GET':
            try:
                api_metrics_obj = APIMetrics.objects.get(snapshot_date=snapshot_date, view=view, method='GET')
                api_metrics_obj.view_count += 1
                api_metrics_obj.save()
            except Exception as e:
                APIMetrics.objects.create(snapshot_date=snapshot_date, view=view, method='GET', view_count=1)

        if request.method == 'POST':
            try:
                api_metrics_obj = APIMetrics.objects.get(snapshot_date=snapshot_date, view=view, method='POST')
                api_metrics_obj.view_count += 1
                api_metrics_obj.save()
            except Exception as e:
                APIMetrics.objects.create(snapshot_date=snapshot_date, view=view, method='POST', view_count=1)

        return func(request, *args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper
