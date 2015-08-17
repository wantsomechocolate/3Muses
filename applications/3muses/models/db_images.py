import fs.s3fs
import os, ast


if db._dbname=='sqlite':
	sqlite_tf=True
else:
	sqlite_tf=False

# try:

## see if you can acces the heroku environment variables
myfs = fs.s3fs.S3FS('threemusesglass','site_images',os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY'])

# ## what exception exactly?
# except KeyError:

# 	# you aren't running on heroku
# 	# this will fail if it can't find the local keys. GOOD.
# 	# with open('/home/wantsomechocolate/Code/API Info/api_keys.txt','r') as fh:
# 	# 	text=fh.read()
# 	# 	api_keys = ast.literal_eval(text)
	
# 	# AWS_ACCESS_KEY_ID=api_keys['aws']['wantsomechocolate']['AWS_ACCESS_KEY_ID']
# 	# AWS_SECRET_ACCESS_KEY=api_keys['aws']['wantsomechocolate']['AWS_SECRET_ACCESS_KEY']

# 	AWS_ACCESS_KEY_ID=os.environ['AWS_ACCESS_KEY_ID']
# 	AWS_SECRET_ACCESS_KEY=os.environ['AWS_SECRET_ACCESS_KEY']

# 	myfs = fs.s3fs.S3FS('threemusesglass','site_images',AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)



db.define_table('categories',
	Field('category_name'),
	Field('category_description','text'),
	Field('is_active','boolean'),
	Field('s3_url', 'upload'),
	Field('display_order','integer'),
	format='%(category_name)s'
	)
db.categories.is_active.default=True

if sqlite_tf:
	pass
else:
	db.categories.s3_url.uploadfs=myfs

db.define_table('product',
	Field('category_name', 'reference categories'),
	Field('product_name', writable=True),
	Field('description','text', writable=True),
	Field('cost_USD','float'),
	Field('qty_in_stock','integer'),
	Field('is_active','boolean'),
	Field('display_order','integer'),
	Field('shipping_description'),
	Field('weight_oz'),
	## if purchased by is an email, non-users could potentially do bad things. 
	#Field('purchased_by'),
	# having a field here for purchased by doesn't work in the case of multiple inventory!
	format='%(product_name)s'
	)
db.product.is_active.default=True
#db.product.purchased_by.default=None


## The table that will hold all the purchase records
## except for quantity
db.define_table('purchase_history_data',

	## Muses Fields
	Field('muses_id'),
	Field('muses_email_address'),
	Field('muses_transaction_datetime','datetime'),

	Field('session_db_record_id'),

	
	## Shipping Address Fields
	Field('shipping_name_first'), ## Added new ## Probably don't need this field
	Field('shipping_name_last'), ## Added new ## Probably don't need this field
	Field('shipping_street_address_line_1'),
	Field('shipping_street_address_line_2'),
	Field('shipping_municipality'),
	Field('shipping_administrative_area'),
	Field('shipping_postal_code'),
	Field('shipping_country'),

	## Shipping Fields
	Field('easypost_shipping_service'), ## Probably don't need this field
	Field('easypost_shipping_service_raw'), ## Added new
	Field('easypost_shipping_carrier'), ## Probably don't need this field
	Field('easypost_rate_id'),
	Field('easypost_shipment_id'),
	Field('easypost_rate'), ## Probably don't need this field

	Field('easypost_delivery_days','integer'),
	Field('easypost_delivery_date_text'),
	Field('easypost_delivery_date','datetime'),
	
	## Payment Fields
	Field('payment_service'),
	Field('payment_confirmation_id'),
	Field('payment_invoice_number'),
	Field('payment_email_address'),
	Field('payment_minimal_confirmation_info'),

	## Cart Summary Details
	Field('cart_base_cost'), ## Probably don't need this field
	Field('cart_shipping_cost'), ## Probably don't need this field
	Field('cart_total_cost'), ## Probably don't need this field

	singular=T("Purchase History Data"),
	plural=T("Purchase History Data"),
)


## Vestigial Fields
	## User Fields
	## These will be None for non users
	# Field('muses_name'),

	## Session Fields (These actually come from response not session)
	## These will be available for all users
	# Field('session_id_3muses'),
	# Field('session_db_table'), ## Probably don't need this field


	## Shipping Fields
	## Name is seperated because shipping and billing 
	## Addresses are going to be used interchangeably 
	## like on every other site.
	## Although a billing address isn't necessary for paypal


	## Easypost Fields?
	## I might want to add a field here that stores
	## serialized json of the entire api response used for 
	## shipping rates. 
	# Field('easypost_api_response', 'text'), ## Probably don't need this field

	## Payment Fields are going to be vastly different
	## I'm keeping all the old fields for now, 
	## but the new idea is to store the payment confirmation response in the db
	## as serialized json. and just keep the payment service top level. 

	# ## Payment Fields
	# Field('payment_confirmation_dictionary', 'text'), ## Probably don't need this field

	# ## Legacy Fields - Might keep some high level stuff 
	# ## just to make browsing the data easier. 
	# Field('payment_method'),
	# Field('payment_stripe_name'),
	# Field('payment_stripe_user_id'),
	# Field('payment_stripe_last_4'),
	# Field('payment_stripe_brand'),
	# Field('payment_stripe_exp_month'),
	# Field('payment_stripe_exp_year'),
	# Field('payment_stripe_card_id'),
	# Field('payment_stripe_transaction_id'),


	# ## Billing address information
	# Field('billing_first_name'),
	# Field('billing_last_name'),
	# Field('billing_street_line_1'),
	# Field('billing_street_line_2'),
	# Field('billing_municipality'),
	# Field('billing_administrative_area'),
	# Field('billing_postal_code'),
	# Field('billing_country_code'),




## Failed Experiment
# db.define_table('purchase_history_data2',

# 	## 3Muses User Fields
# 	Field('user_data', 'text'),

# 	## Session Fields (These actually come from response not session)
# 	Field('response_data', 'text'),

# 	## Shipping/Address Fields
# 	Field('address_data', 'text'),

# 	## Payment Fields
# 	Field('payment_data', 'text'),

# 	## Summary Fields
# 	Field('summary_data', 'text'),

# 	singular=T("Purchase History Data"),
# 	plural=T("Purchase History Data"),
# )




## This purchase history product table
## is going to save everything about a product
## this is becaus I want the site master to be able to reuse products
## without having to copy a product or anything. 
## Just upload new pictures and keep the desc, weight, etc. 
db.define_table('purchase_history_products',

	Field('purchase_history_data_id','reference purchase_history_data'),

	## Cart info
	Field('product_id'),
	Field('product_qty'),

	## Product Info
	Field('category_name'),
	Field('product_name'),
	Field('description','text'),
	Field('cost_USD','float'),
	Field('qty_in_stock','integer'),
	Field('is_active','boolean'),
	Field('display_order','integer'),
	Field('shipping_description'),
	Field('weight_oz'),
	singular=T("Purchase History Product"),
	plural=T("Purchase History Products"),
	)


db.define_table('image',
	Field('category_name', 'reference categories'),
	Field('product_name', 'reference product'),
	Field('title'),
	Field('s3_url', 'upload'),
	)

db.image.title.requires=IS_NOT_IN_DB(db,db.image.title)
if sqlite_tf:
	pass
else:
	db.image.s3_url.uploadfs=myfs


db.define_table('landing_page_images',
	Field('image_purpose'),
	Field('s3_url', 'upload'),
	)
if sqlite_tf:
	pass
else:
	db.landing_page_images.s3_url.uploadfs=myfs

# this table can have multiple stripe tokens per user
# when a returning user is buying something, ask the user which card they want to use
# by showing them the last four digits of the card. 

db.define_table('stripe_customers',
	Field('muses_id', 'reference auth_user'),
	Field('stripe_id'),
	Field('stripeEmail'),
	Field('stripe_next_card_id'),
	)
db.stripe_customers.id.readable=False

db.define_table('muses_cart',
	Field('user_id', 'reference auth_user'),
	Field('product_id', 'reference product'),
	Field('product_qty', requires=IS_INT_IN_RANGE(0,10)),
	Field('time_added', 'datetime'),
	Field('is_active','boolean'),
	Field('time_removed', 'datetime'),
	)

db.muses_cart.is_active.default==True
db.muses_cart.id.writable=db.muses_cart.id.readable=False
db.muses_cart.user_id.writable=db.muses_cart.user_id.readable=False
# the line below was for when I had the row name as a link instead of just having a seperate link
# it needed to be called in using the fields arg or else it wasn't available
# for the lambda function, so I had to make it hidden here. 
#db.muses_cart.product_id.writable=db.muses_cart.product_id.readable=False
db.muses_cart.product_id.writable=False








## A Country codes table
db.define_table('country_codes',
	Field('country_name'),
	Field('country_ISO_2'),
	Field('country_ISO_3'),
	Field('country_ISO_numeric'),
	Field('is_active','boolean')
	)

db.country_codes.country_ISO_2.requires=IS_LENGTH(minsize=2, maxsize=2, error_message='Must be 2 characters')
db.country_codes.country_ISO_3.requires=IS_LENGTH(minsize=3, maxsize=3, error_message='Must be 3 characters')




# a cart will hold the amount of money to charge and the concatonated description of everything purchased?, nah, I need a plugin for this. 
#db.define_table('cart')
#create a view for this so that mom can add and remove images 

db.define_table('addresses',
	Field('user_id', 'reference auth_user'),
	# Field('first_name'),
	# Field('last_name'),

	## Address Fields
	# Field('name'),
	Field('first_name'),
	Field('last_name'),
	Field('street_address_line_1'),
	Field('street_address_line_2'),
	Field('municipality'),
	Field('administrative_area'),
	Field('postal_code'),
	Field('country'),

	## Default Fields
	Field('default_address', 'boolean'),
	Field('last_modified', 'datetime'),
	# Field('easypost_api_response', 'text'),

	## Shipping Fields
	Field('easypost_shipping_id'),
	Field('easypost_api_datetime', 'datetime'),
	Field('easypost_default_shipping_rate_id'),
	)

db.addresses.id.readable=False
db.addresses.user_id.readable=False
db.addresses.user_id.writable=False

db.addresses.user_id.default=auth.user_id

db.addresses.default_address.readable=db.addresses.default_address.writable=False
db.addresses.last_modified.readable=db.addresses.last_modified.writable=False
db.addresses.easypost_shipping_id.readable=db.addresses.easypost_shipping_id.writable=False
db.addresses.easypost_api_datetime.readable=db.addresses.easypost_api_datetime.writable=False
db.addresses.easypost_default_shipping_rate_id.readable=db.addresses.easypost_default_shipping_rate_id.writable=False

db.addresses.country.requires = IS_IN_DB(db(db.country_codes.is_active==True), 'country_codes.country_ISO_2', '%(country_name)s')





db.define_table('email_correspondence',
	Field('user_id', 'reference auth_user'),
	Field('email'),
	Field('is_active', 'boolean'),
	)

db.email_correspondence.email.requires = IS_EMAIL(error_message='invalid email!')
db.email_correspondence.is_active.default=True












## Keeping track of purchases:
## Purchase table
## Store everything about the purchase except product and qty
## Then link the everything about the purchase table (I like this because it keeps a record
## of what you entered at the time (in case you change data))
## purchase info id product qty
## Then to retreieve the information, use email address to get the id of any purchases
## Then go to the other table and get product information about that purchase. 
## for sessions, if they just made a purchase you can get the information,
## but if not say that you will email them a copy of them purchase history
## for users, you can just show them the purchase history.


## I need a way to either copy products so my mom can resuse stuff. Or I need to include
## product information in the history, not just qty, but also, which images, descriptions etc 
## were used. I think I'll go the route of more purchase history information
## I also want to try to store things as dictionaries, so the tables don't have to have
## 1000 columns. It also helps with having seperate columns for different source of similar info. 
## like stripe vs paypal. 