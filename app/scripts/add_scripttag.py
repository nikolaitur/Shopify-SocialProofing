# Development test script to add script tag to store. Run using Pyton 2.7.x.
# More information here: https://help.shopify.com/api/reference

import shopify

token = 'e8c49b1c40bde5e8bf956703f5f62797'
session = shopify.Session("michael-john-devs.myshopify.com", token)
shopify.ShopifyResource.activate_session(session)

# Print how many script tags added already
print shopify.ScriptTag().count()

# Add script tag to the shop
shopify.ScriptTag(dict(display_scope='all', event='onload', src='https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js')).save()
shopify.ScriptTag(dict(display_scope='all', event='onload', src='https://rawgit.com/notifyjs/notifyjs/master/dist/notify.js')).save()
shopify.ScriptTag(dict(display_scope='all', event='onload', src='https://protected-reef-37693.herokuapp.com/modal')).save()
