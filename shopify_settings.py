import os

if os.environ.get('API_KEY') and os.environ.get('API_SECRET'):
    API_KEY = os.environ.get('API_KEY')
    API_SECRET = os.environ.get('API_SECRET')
else:
    raise EnvironmentError('API_KEY or API_SECRET environment variables not set.')

if os.environ.get('DEVELOPMENT_MODE'):
    DEVELOPMENT_MODE = os.environ.get('DEVELOPMENT_MODE')
    if DEVELOPMENT_MODE not in ['TEST', 'PRODUCTION']:
        raise EnvironmentError('DEVELOPMENT_MODE {} is not valid.'.format(DEVELOPMENT_MODE))
else:
    raise EnvironmentError('DEVELOPMENT_MODE environment variable not set.')
SOCIAL_SCOPES = ['product', 'vendor', 'collections', 'tags', 'product_type', 'any']
SHOPIFY_API_SCOPE = ['write_products', 'read_products', 'read_script_tags', 'write_script_tags',
                     'read_product_listings', 'read_orders', 'read_fulfillments', 'read_analytics']

if DEVELOPMENT_MODE == 'TEST':
    APP_URL = 'https://protected-reef-37693.herokuapp.com'
else:
    APP_URL = '<TO-BE-DECIDED>'

SHOPIFY_AUTH_CALLBACK_URL = APP_URL + '/auth/callback'
