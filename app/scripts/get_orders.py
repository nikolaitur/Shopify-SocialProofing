# Development test script to get all orders for a store. Run using Pyton 2.7.x.
# More information here: https://help.shopify.com/api/reference

import shopify

# Authentication
token = 'e8c49b1c40bde5e8bf956703f5f62797'
session = shopify.Session("michael-john-devs.myshopify.com.myshopify.com", token)
shopify.ShopifyResource.activate_session(session)

# Get orders as a list
orders = shopify.Order.find()
print orders  # Order list, for example [order(168793374751)]

# Loop through each order and print out attributes of each order
for order in orders:
    print order.__dict__    # Print all attributes of an order

# Sample output of a single order
'''
{'_initialized': True, 'attributes': {u'subtotal_price': u'55.00', u'buyer_accepts_marketing': False,
u'reference': None, u'shipping_lines': [], u'cart_token': None, u'updated_at': u'2017-11-02T22:43:05-04:00', 
u'taxes_included': False, u'currency': u'USD', u'discount_codes': [], u'financial_status': u'paid', 
u'source_name': u'shopify_draft_order', u'closed_at': None, u'processed_at': u'2017-11-02T22:43:05-04:00', 
u'payment_gateway_names': [u'manual'], u'location_id': 3035987999, u'gateway': u'manual', u'confirmed': True, 
u'user_id': 3462463519, u'fulfillments': [], u'landing_site_ref': None, u'customer_locale': None, u'source_identifier': None, 
u'id': 168793374751, u'note': u'yytrf', u'landing_site': None, u'browser_ip': None, u'total_line_items_price': u'55.00', 
u'cancelled_at': None, u'test': False, u'email': u'', u'total_tax': u'0.00', u'cancel_reason': None, u'tax_lines': [], u'tags': u'', 
u'app_id': 1354745, u'phone': None, u'total_discounts': u'0.00', u'number': 1, u'checkout_id': None, u'processing_method': u'manual', 
u'device_id': None, u'referring_site': None, u'line_items': [line_item(385168801823)], u'total_price': u'55.00', u'name': u'#1001', 
u'refunds': [], u'checkout_token': None, u'created_at': u'2017-11-02T22:43:05-04:00', u'note_attributes': [], 
u'fulfillment_status': None, u'total_price_usd': u'55.00', u'source_url': None, u'contact_email': None, 
u'order_status_url': u'https://checkout.shopify.com/24950576/orders/6005115e7515587016d1007bcfeabe23/authenticate?key=5f43fd61e2fff7b7ae45f5ca8e601e02', 
u'order_number': 1001, u'token': u'6005115e7515587016d1007bcfeabe23', u'total_weight': 0}, 
'errors': <pyactiveresource.activeresource.Errors object at 0x10d1aa4d0>, '_prefix_options': {}, 
'klass': <class 'shopify.resources.order.Order'>}
'''