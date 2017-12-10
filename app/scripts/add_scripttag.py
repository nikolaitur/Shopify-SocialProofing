# Development test script to add script tag to store.
# More information here: https://help.shopify.com/api/reference

import shopify
import ssl

# Overrides the default function for context creation with the function to create an unverified context.
ssl._create_default_https_context = ssl._create_unverified_context

# Authentication
token = 'fb40ed51a032685beebb71c597502449'
session = shopify.Session("michael-john-devs.myshopify.com", token)
shopify.ShopifyResource.activate_session(session)

# Print how many script tags added already
print(shopify.ScriptTag().count())

# Loop through each script tag and print attributes of each
#for script_tag in shopify.ScriptTag().find():
#print(script_tag.attributes)

# Delete a script tag by id
#script_tag_id = '9512321055'
#script_tag_obj = (shopify.ScriptTag().find(script_tag_id))
  #shopify.ScriptTag.delete(script_tag_obj.id)

# Delete _ALL_ script tags
#[shopify.ScriptTag.delete(x.id) for x in shopify.ScriptTag.find()]

# Add script tag to the shop
shopify.ScriptTag(dict(display_scope='all', event='onload', src='https://protected-reef-37693.herokuapp.com/static/js/initializeModal.js')).save()
# shopify.ScriptTag(dict(display_scope='all', event='onload', src='https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js')).save()
# shopify.ScriptTag(dict(display_scope='all', event='onload', src='https://rawgit.com/notifyjs/notifyjs/master/dist/notify.js')).save()
