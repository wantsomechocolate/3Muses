# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

import os, ast, time

STRIPE_SESSION_RETIRE_HOURS=26 #(1/20.0)
SERVER_SESSION_RETIRE_HOURS=26 #(1/20.0)
PRODUCTION_STATUS='test'
PAYPAL_MODE='sandbox' #sandbox or live
S3_BUCKET_PREFIX='https://s3.amazonaws.com/threemusesglass/site_images/'


## Functions that should be moved to their own module
from aux import get_env_var
from aux import splitSymbol
from aux import camelcaseToUnderscore


import stripe
STRIPE_SECRET=get_env_var('stripe', PRODUCTION_STATUS , 'STRIPE_SECRET')
STRIPE_PUBLISHABLE=get_env_var('stripe', PRODUCTION_STATUS , 'STRIPE_PUBLISHABLE')
stripe.api_key = STRIPE_SECRET


import easypost
EASYPOST_KEY=get_env_var('easypost',PRODUCTION_STATUS,'EASYPOST_KEY')
easypost.api_key=EASYPOST_KEY


POSTMARK_API_KEY=get_env_var('postmark',PRODUCTION_STATUS,'POSTMARK_API_KEY')


## Set Cookies to expire at time designated by Server Session Retire Hours 
if response.session_id_name in response.cookies:
    response.cookies[response.session_id_name]['expires']=int(3600*SERVER_SESSION_RETIRE_HOURS)
else:
    # cookie key doesn't get created until second time visiting a page for 
    # incognito chrome and probably other private browsing modes. 
    pass


## Tell the controller what db its using
if db._dbname=='sqlite':
    sqlite_tf=True
else:
    sqlite_tf=False


## The static views (index, categories, display, product, meet the artist.)

def index():

    return dict()



def categories():

    if request.args(0) is not None:

        redirect(URL('categories'))

    else:

        pass

    category_rows=db(db.categories.is_active==True).select(orderby=db.categories.display_order)

    return dict(
        category_rows=category_rows,
        )



def display():
    
    category_name=request.args[0].replace("_"," ")

    category_id=int(db(db.categories.category_name==category_name).select().first()['id'])

    product_rows=db((db.product.category_name==category_id)&(db.product.is_active==True)).select(orderby=db.product.display_order)

    return dict(
        category_id=category_id,
        product_rows=product_rows,
        )



def product():

    product_id=request.args[0]

    product_row=db(db.product.id==product_id).select()

    cart_form=FORM(

        INPUT(
            _type="hidden",
            _name="qty",
            _value=1,
            #_placeholder="Enter Quantity",
            #requires=IS_INT_IN_RANGE(1,2),
        ),BR(),

        INPUT(_type='submit', _class="btn", _value="Add to Cart"),
    )

    if cart_form.accepts(request, session):

        ## If the form is accepted, you must be logged in to add item to cart, so make sure
        if auth.is_logged_in():
            pass
        else:
            create_gimp_user()

        try:
            existing_cart_entry=db((db.muses_cart.product_id==product_id)&(db.muses_cart.user_id==auth.user_id)).select()[0]
            db.muses_cart[existing_cart_entry.id]=dict(product_qty=cart_form.vars.qty)

        except IndexError:

            db.muses_cart.insert(
                user_id=auth.user_id,
                product_id=product_id,
                product_qty=cart_form.vars.qty,
            )

    return dict(
        product_id=product_id,
        product_row=product_row,
        cart_form=cart_form,
        )



## Meet the artist is under construction
def artist():
    return dict()



## Functions for adding things to session or db. 

## This needs to be shortened. Two long right now
## Consider bringing some of this crap to the view

@auth.requires_login()
def add_new_card():

    stripe_form=FORM(

        DIV( LABEL( 'Name on the Card',),DIV(INPUT(_type='text', _name='name', _class='form-control', ),),),

        DIV( LABEL( 'Card Number',),DIV(INPUT(_type='integer', _name='number', _class='form-control', ),),),

        DIV( LABEL('Card CVC Number',),DIV(INPUT(_type='integer', _name='cvc', _class='form-control', ),),),

        DIV( LABEL('Expiration Month',),DIV(INPUT(_type='integer', _name='exp_month', _class='form-control', ),),),

        DIV( LABEL('Expiration Year (YYYY)',),DIV(INPUT(_type='integer', _name='exp_year', _class='form-control', requires=IS_INT_IN_RANGE(2014,3000),),),),

        INPUT(_type='submit', _class="btn btn-default"),

        _class='form-horizontal',

        _role='form').process()


    if stripe_form.accepted:
        ## If there are no errors found in the form (which there shouldn't be because there are no
        ## requirements yet), try to retrieve the customer token from the database
        ## and create a new card. If the logged in user doesn't have a stripe customer token yet, 
        ## it will be unable to find one and raise an index error. 

        try:
            stripe_customer_token=db(db.stripe_customers.muses_id==auth.user_id).select()[0].stripe_id
            customer=stripe.Customer.retrieve(stripe_customer_token)
            ## This is failing because customer is none I think?
            if customer==None:
                pass
            else:
                customer.cards.create(
                    card=dict(
                        name=stripe_form.vars.name,
                        number=stripe_form.vars.number,
                        cvc=stripe_form.vars.cvc,
                        exp_month=stripe_form.vars.exp_month,
                        exp_year=stripe_form.vars.exp_year,     
                    )
                )

        # if there is no stripe customer token for the current user, the there will be an index error
        # this means that the user doesn't have a token in the database
        except IndexError:
            # if user doesn't have stripe association yet when trying to create card
            # create customer and first card at the same time.
            #if auth.is_logged_in():

            try:
                customer = stripe.Customer.create(
                    email=auth.user.email,
                    card=dict(
                        name=stripe_form.vars.name,
                        number=stripe_form.vars.number,
                        cvc=stripe_form.vars.cvc,
                        exp_month=stripe_form.vars.exp_month,
                        exp_year=stripe_form.vars.exp_year,     
                    )
                )

                # add the fact the current customer is now a stripe customer to the db. 
                db.stripe_customers.insert(
                    muses_id=auth.user_id,
                    stripe_id=customer.id,
                    ## might want to add some logic here to get a better email address when using a gimp user!
                    stripeEmail=auth.user.email,
                )

            ## if there was a problem connecting to the stripe api
            except stripe.error.APIConnectionError:
                customer=None

        redirect(URL('cart'))

    else:
        
        return dict(stripe_form=stripe_form)


@auth.requires_login()
def add_new_address(): #http://codepen.io/Angelfire/pen/dJhyr

    add_address_form=FORM(

        DIV ( LABEL ( 'First Name', ) , DIV ( INPUT ( _type='text' , _name='first_name' , _class='form-control' , ) , ) , ) ,

        DIV ( LABEL ( 'Last Name', ), DIV ( INPUT ( _type='text', _name='last_name' , _class='form-control' , ) , ) , ),

        DIV ( LABEL( 'Street Address/ PO Box/ Etc.',),DIV(INPUT(_type='text', _name='street_address_line_1', _class='form-control', ),),),

        DIV ( LABEL ( 'Floor/ Suite/ Apt/ Etc.',),DIV(INPUT(_type='text', _name='street_address_line_2', _class='form-control', ),),),

        DIV ( LABEL ( 'Municipality',),DIV(INPUT(_type='text', _name='municipality', _class='form-control', ),),),

        DIV ( LABEL ( 'Administrative Area',),DIV(INPUT(_type='text', _name='administrative_area', _class='form-control', ),),),

        DIV ( LABEL ( 'Postal Code',),DIV(INPUT(_type='text', _name='postal_code', _class='form-control', ),),),

        DIV ( LABEL ( 'Country',),DIV(INPUT(_type='text', _name='country', _class='form-control', ),),),

        INPUT(_type='submit', _class="btn btn-default"),
            
        _class='form-horizontal',

        _role='form').process()

    if add_address_form.accepted:

        #if auth.is_logged_in():
        db.addresses.insert(
            user_id=auth.user_id,
            first_name=add_address_form.vars.first_name,
            last_name=add_address_form.vars.last_name,
            street_address_line_1=add_address_form.vars.street_address_line_1,
            street_address_line_2=add_address_form.vars.street_address_line_2,
            municipality=add_address_form.vars.municipality,
            administrative_area=add_address_form.vars.administrative_area,
            postal_code=add_address_form.vars.postal_code,
            country=add_address_form.vars.country,
            default_address=True,
        )

        redirect(URL('cart'))

    else:
        
        return dict(add_address_form=add_address_form)


## For a logged in user:
    ## Get cart information from the database
    ## Get address information from the data base
    ## Get shipping information from the address information
    ## Get purchase information from user selection
        ## If card, get details from the database and stripe
        ## if paypal, then no details to get really

## For a session user:
    ## Get cart information from the session
    ## Get address information from the session
    ## Get shipping info from the address info
    ## Get purchase selection from user
        ## If card, get from session and stripe
        ## if paypal, then no details to get really

def cart():

    ## If someone tries to mess with the URL in the browser by going to 
    ## cart/arg, It will reload the page without the arg
    if request.args(0) is not None:
        redirect(URL('cart'))
    else:
        pass

    ## If you try to visit this page while you are not logged in, you get logged in as a handicapped user. 
    ## but the nav option don't change. 
    if auth.is_logged_in():
        pass
    else:
        create_gimp_user()

#############################################################################################
###########-------------------Cart Logic---------------------############
#############################################################################################

    cart_information_LOD=[]
    cart_information=dict(error=False,error_message=None,cart_information_LOD=cart_information_LOD)

    ## Retrieve the current items from the users cart)
    ## There is no check here to not include items that are sold out or no
    ## longer active, That happens later.
    cart_db=db(db.muses_cart.user_id==auth.user_id).select()

    ## If cart turns out to be empty, set cart_grid so the view can have
    ## something to display. but now cart_grid_table_row_LOL will be empty,
    ## which should disallow the user from pressing the checkout button. 
    if not cart_db:

        cart_information['error']=True
        cart_information['error_message']="You have not yet added anything to your cart"
        cart_is_empty=True

    ## If the cart is not empty
    else:
        
        cart_is_empty=False
        ## For each product in the cart
        for row in cart_db:

            ## Retreive product info from the db
            product=db(db.product.id==row.product_id).select().first()

            ## If using a local db get the product image locally
            if sqlite_tf:
                srcattr=URL('download',db(db.image.product_name==row.product_id).select().first().s3_url)
            
            ## For the more common case, get the image from aws s3
            else:
                srcattr=S3_BUCKET_PREFIX+str(db(db.image.product_name==row.product_id).select().first().s3_url)

            ## Create the product_image_url
            product_image_url=A(IMG(_src=srcattr, _class='img-thumbnail'), _href=URL('default','product',args=[row.product_id]))

            ## Create a delete button for the item
            delete_button=A('X', _href=URL('delete_item_from_cart', vars=dict(pri_key=row.id,redirect_url=URL('cart'))), _class="btn")

            ## Populate a list with the current product info
            cart_grid_table_row_list=[
                product_image_url, 
                product.product_name, 
                product.cost_USD, 
                #row.product_qty, This was used when qty could be over 1,
                delete_button
            ]

            cart_item_dict=dict(
                product_image_url=product_image_url,
                product_name=product.product_name,
                product_cost=product.cost_USD,
                product_delete_button=delete_button,
                product_active=product.is_active,
                )

            cart_information_LOD.append(cart_item_dict)

            ## If the item is no longer active, remove it from the cart.
            if not product.is_active:
                db(db.muses_cart.product_id==product.id).delete()



#############################################################################################
###########-----------------Address Logic (User and Non User)--------------------############
#############################################################################################

    address_information_LOD=[]
    address_information=dict(error=False,error_message=None,address_information_LOD=address_information_LOD)

    address_list=db(db.addresses.user_id==auth.user_id).select(orderby=db.addresses.street_address_line_1)

    if not address_list:

        address_list_is_empty=True
        address_information['error']=True
        address_information['error_message']="Please add an address to continue with your purchase"

    else:

        address_list_is_empty=False

        for j in range(len(address_list)):

            # if address_list[j].default_address==True:
            #     radio_button=INPUT(_type='radio', _name='address', _value=address_list[j].id, _checked='checked')
            #     session.default_address_id=address_list[j].id
            # else:
            #     radio_button=INPUT(_type='radio', _name='address', _value=address_list[j].id)

            # edit_button=A('<-', _href=URL('edit_db_address', vars=dict(pri_key=address_list[j].id)), _class="btn")
            
            # delete_button=A('X', _href=URL('delete_address', vars=dict(pri_key=address_list[j].id, redirect_url=URL('cart'))), _class="btn")

            address_information_LOD.append(dict(
                first_name=address_list[j].first_name,
                last_name=address_list[j].last_name,
                street_address_line_1=address_list[j].street_address_line_1, 
                street_address_line_2=address_list[j].street_address_line_2, 
                municipality=address_list[j].municipality, 
                administrative_area=address_list[j].administrative_area, 
                postal_code=address_list[j].postal_code, 
                country=address_list[j].country,
                id=address_list[j].id,
                default_address=address_list[j].default_address,
            ))


#############################################################################################
###########---------------Shipping Logic (User and Non User)---------------------############
#############################################################################################

    if cart_is_empty:
        shipping_information=dict(error=True, error_message="Please add something to your cart to continue", shipping_options_LOD=[])
    elif address_list_is_empty:
        shipping_information=dict(error=True, error_message="Please add an address to continue", shipping_options_LOD=[])
    else:
        shipping_information=dict(error=True, error_message="Generating shipping costs", shipping_options_LOD=[])

    # try:

    #     shipping_options_LOD=[]
    #     shipping_information=dict(error=False,error_message=None,shipping_options_LOD=shipping_options_LOD)


    #     #get default_address and make a dict out of it
    #     address=db((db.addresses.user_id==auth.user_id)&(db.addresses.default_address==True)).select().first()


    #     cart=db(db.muses_cart.user_id==auth.user_id).select()
    #     cart_for_shipping_calculations=[]
    #     cart_weight_oz=0
    #     cart_cost_USD=0

    #     for row in cart:

    #         product=db(db.product.id==row.product_id).select().first()
    #         cart_weight_oz+=float(product.weight_oz)*float(row.product_qty)
    #         cart_cost_USD+=float(product.cost_USD)*float(row.product_qty)

    #         cart_for_shipping_calculations.append(dict(
    #             product_name=product.product_name,
    #             product_cost=product.cost_USD,
    #             product_qty=row.product_qty,
    #             product_weight=product.weight_oz,
    #             product_shipping_desc=product.shipping_description,
    #         ))


    #     address_info=dict(
    #         street_address_line_1=address.street_address_line_1, 
    #         street_address_line_2=address.street_address_line_2, 
    #         municipality=address.municipality, 
    #         administrative_area=address.administrative_area, 
    #         postal_code=address.postal_code, 
    #         country=address.country,
    #     )


    #     # now logged in or not we have the address that was chosen, the address info for the address that was chosen
    #     # and the cart info, and the combined weight of our package. 

    #     shipment=create_shipment(address_info, cart_for_shipping_calculations)

    #     ## Put shipment info in the session to get it later!
    #     session.shipment_info_from_easypost=shipment

    #     # Generate list of sorted rates
    #     shipping_rates_for_sorting=[]
    #     for i in range(len(shipment.rates)):
    #         shipping_rates_for_sorting.append(float(shipment.rates[i].rate))
    #     shipping_rates_for_sorting.sort()


    #     shipping_grid_header_list=[':)', 'Carrier', 'Service', 'Cost']
    #     shipping_grid_table_row_LOL=[]
        

    #     # Build the shipping grid
    #     # I need to be able to sort the shipping rates based on the rate. 
    #     for j in range(len(shipping_rates_for_sorting)):

    #         for i in range(len(shipment.rates)):

    #             if shipping_rates_for_sorting[j]==float(shipment.rates[i].rate):

    #                 if shipment.rates[i].service==session.shipping_choice:

    #                 #radio_button=INPUT(_type='radio', _name='shipping', _value=shipment.rates[i].service)

    #                     radio_button=INPUT(_type='radio', _name='shipping', _checked='checked', _value=shipment.rates[i].service)

    #                 else:

    #                     radio_button=INPUT(_type='radio', _name='shipping', _value=shipment.rates[i].service)

    #                 shipping_grid_table_row_list=[
    #                     radio_button,
    #                     shipment.rates[i].carrier,
    #                     camelcaseToUnderscore(shipment.rates[i].service),
    #                     shipment.rates[i].rate,
    #                 ]

    #                 shipping_option_dict=dict(
    #                         carrier=shipment.rates[i].carrier,
    #                         service=camelcaseToUnderscore(shipment.rates[i].service),
    #                         rate=shipment.rates[i].rate,
    #                         rate_id=shipment.rates[i].id,
    #                         shipment_id=shipment.rates[i].shipment_id,
    #                         delivery_days=shipment.rates[i].delivery_days,
    #                     )

    #                 shipping_grid_table_row_LOL.append(shipping_grid_table_row_list)
    #                 shipping_options_LOD.append(shipping_option_dict)
    #             else:
    #                 pass

    #         shipping_grid=table_generation(shipping_grid_header_list, shipping_grid_table_row_LOL, 'shipping')

    # except easypost.Error:

    #     shipping_grid=DIV('There was a problem generating the shipping costs')
    #     shipping_information['error']=True,
    #     shipping_information['error_message']='There was a problem generating the shipping costs'
    #     #shipping_options_LOD.append(dict(error=error, error_message=error_message))

    # except AttributeError:

    #     shipping_grid=DIV('There is nothing in your cart to ship')

    #     shipping_information['error']=True,
    #     shipping_information['error_message']='There is nothing in your cart to ship'
    #     #shipping_options_LOD.append(dict(error=error, error_message=error_message))
        
    # except TypeError:

    #     shipping_grid=DIV('There is no address to ship to')

    #     shipping_information['error']=True,
    #     shipping_information['error_message']='There is no address to ship to'
    #     #shipping_options_LOD.append(dict(error=error, error_message=error_message))




#############################################################################################
###########-------------------Card Logic (User and Non User)---------------------############
#############################################################################################


    card_information_LOD=[]
    

    ## The headers for the table that I won't need for very much longer
    ## only applies to cards anyway. 
 

    ## a grid to fill up and give to table generater, but I might put more of the design in the view. 
    ## card_grid_table_row_LOL=[]

    ## If the user is logged in. 
    #if auth.is_logged_in():

    ## See if the user has any card information on stripe. 
    try:
        ## get stripe id from the db
        stripe_customer_token=db(db.stripe_customers.muses_id==auth.user_id).select()[0].stripe_id

        ## get stripe info using stripe api
        stripe_customer=stripe.Customer.retrieve(stripe_customer_token)

        ## put all stripe card info into a variable
        ## this will only hold the first 10 cards a person has. If they have more cards
        ## then they need help. 
        stripe_cards=stripe_customer.cards.all()

        for i in range(len(stripe_cards['data'])):

            if stripe_cards['data'][i]['id']==db(db.stripe_customers.muses_id==auth.user_id).select().first().stripe_next_card_id:
                radio_button=INPUT(_type='radio', _name='card', _value=stripe_cards['data'][i]['id'], _checked='checked')
            else:
                radio_button=INPUT(_type='radio', _name='card', _value=stripe_cards['data'][i]['id'])

            delete_button=A('X', _href=URL('delete_item_from_db_card', vars=dict(customer_id=stripe_customer_token, card_id=stripe_cards['data'][i]['id'])), _class="btn")

            card_information_LOD.append(dict(
                card_radio=radio_button, 
                card_name=stripe_cards['data'][i]['name'], 
                cart_last4=stripe_cards['data'][i]['last4'], 
                card_brand=stripe_cards['data'][i]['brand'], 
                card_exp_mo=stripe_cards['data'][i]['exp_month'], 
                card_exp_yr=stripe_cards['data'][i]['exp_year'], 
                #stripe_cards['data'][i]['id'], 
                card_delete=delete_button,
            ))

        card_information=dict(error=False, error_message=None, card_information_LOD=card_information_LOD)

            #card_grid_table_row_LOL.append(card_grid_table_row_list)

        #card_grid=table_generation(card_grid_header_list, card_grid_table_row_LOL, 'card')

        #card_grid.append(DIV(INPUT(_type='radio', _name='card', _value='paypal')))
        #card_grid.append(DIV("Pay with Paypal"))

        

    except IndexError:
        #the current user does not yet have a stripe customer token
        #stripe_customer_token=None
        #stripe_customer=None
        #stripe_cards=None

        #card_grid=DIV("You do not have any cards yet.")
        #card_grid.append(DIV(INPUT(_type='radio', _name='card', _value='paypal')))
        #card_grid.append(DIV("Pay with Paypal"))
        #card_grid=DIV("Pay with Paypal")

        card_information=dict(error=True, error_message="You do not have any cards", card_information_LOD=[])

    except AttributeError:
        #the current user does not yet have a stripe customer token
        # stripe_customer_token=None
        # stripe_customer=None
        # stripe_cards=None

        # card_grid=DIV("You do not have any cards yet, or there was a problem accessing your cards.")
        # card_grid.append(DIV(INPUT(_type='radio', _name='card', _value='paypal')))
        # card_grid.append(DIV("Pay with Paypal"))

        card_information=dict(error=True, error_message="You do not have any cards yet, or there was a problem accessing your cards.", card_information_LOD=[])

    except stripe.error.APIConnectionError, stripe.error.APIError:
        #No access to the internet, probably
        # stripe_customer_token=None
        # stripe_customer=None
        # stripe_cards=None

        # card_grid=DIV("There was a problem trying to access Stripe")
        # card_grid.append(DIV(INPUT(_type='radio', _name='card', _value='paypal')))
        # card_grid.append(DIV("Pay with Paypal"))

        card_information=dict(error=True, error_message="You do not have a good enough internet connection to access your cards", card_information_LOD=[])

    # ## If user is not logged in.
    # else:

    #     if not session.card_info:

    #         card_grid=DIV("You have not entered card information yet")
    #         card_grid.append(DIV(INPUT(_type='radio', _name='card', _value='paypal')))
    #         card_grid.append(DIV("Pay with Paypal"))

    #     else:

    #         #radio_button=FORM(INPUT(_type='radio', _name='card', _value=session.card_info['card_id'], _checked='checked'), _action="")

    #         radio_button=INPUT(_type='radio', _name='card', _value=session.card_info['card_id'], _checked='checked')

    #         delete_button=A('X', _href=URL('delete_item_from_session_card'), _class="btn btn-primary button")

    #         card_grid_table_row_list=[
    #             radio_button,
    #             session.card_info['name'],
    #             session.card_info['last4'],
    #             session.card_info['brand'],
    #             session.card_info['exp_month'],
    #             session.card_info['exp_year'],
    #             #session.card_info['card_id'],
    #             delete_button,
    #         ]

    #         card_grid_table_row_LOL.append(card_grid_table_row_list)

    #         card_grid=table_generation(card_grid_header_list, card_grid_table_row_LOL, 'address')

    #         card_grid.append(DIV(INPUT(_type='radio', _name='card', _value='paypal')))
    #         card_grid.append(DIV("Pay with Paypal"))

    return dict(

        cart_information=cart_information,

        #address_information_LOD=address_information_LOD,
        address_information=address_information,

        #address=address,
        #cart_for_shipping_calculations=cart_for_shipping_calculations,
        #cart=cart,


        #shipping_grid=shipping_grid,
        #shipping_options_LOD=shipping_options_LOD,
        shipping_information=shipping_information,

        card_information=card_information,
        )

    



## The view right before they click to get charged and stuff. 

## In checkout is where I'm going to do most of the preparation for the purchase history
## db entry. My plan is to make a giant dictionary with all of the stuff, then pass
## it as a var or arg to pay. then try to charge the card,
## if it works, I'll have all the info I need, if not I can decide what to do about it. 
def checkout():

## Currently checkout does, is logged in? then everything, then not logged in, and everything
## I figured out that I like the other method better. check for login on each thing you have to do.

#############################################################################################
###########-----------------------Cart Logic -----------------------############
#############################################################################################


    cart_for_shipping_calculations=[]
    cart_weight_oz=cart_cost_USD=0
    cart_grid_row_LOL=[]
    cart_grid_header_list=["TN",'Product Name', 'Cost']

    ## If the payment method is paypal, I need to create the payment link so that
    ## when the users presses pay they are sent to paypal. This is the beginning of that
    cart_for_paypal_LOD=[]

    ## If the user is logged in and ready to checkout
    if auth.is_logged_in():

        ## Retrieve cart based on user id
        ## I should probably be checking again to make sure that the products are still available. 
        ## maybe implement that timer crap. 
        cart=db(db.muses_cart.user_id==auth.user_id).select()
      
        ## for every item the user has in their cart
        ## logic placed at the cart level should ensure they have something in their cart,
        ## but you never now, I should have a backup plan here. 
        for row in cart:

            ## Retrieve the product info from the db
            product=db(db.product.id==row.product_id).select().first()

            ## Generate a dictionary for shipping information of the current product
            ## I believe this is only used for shipping internationally
            cart_for_shipping_dict=dict(
                product_name=product.product_name, 
                product_cost=product.cost_USD,
                product_qty=row.product_qty,
                product_weight=product.weight_oz,
                product_shipping_desc=product.shipping_description,
            )

            ## Append to list shipping info for all product in cart
            cart_for_shipping_calculations.append(cart_for_shipping_dict)

            ## Generate a dictionary for the paypal item. 
            cart_for_paypal_dict=dict(
                quantity=str(int(row.product_qty)),
                name=product.product_name,
                price='{:.2f}'.format(product.cost_USD),
                currency='USD',
                description=product.shipping_description,
                )

            ## Append the product dict to the list of dicts for paypal
            cart_for_paypal_LOD.append(cart_for_paypal_dict)


            ## Keeping track of cost and weight for presentation/display purposes.
            cart_weight_oz+=float(product.weight_oz)*float(row.product_qty)
            cart_cost_USD+=float(product.cost_USD)*float(row.product_qty)
            row_cost_USD=float(product.cost_USD)*float(row.product_qty)

            ## Get the thumbnail image for each product
            if sqlite_tf:
                srcattr=URL('download',db(db.image.product_name==row.product_id).select().first().s3_url)
            else:
                srcattr=S3_BUCKET_PREFIX+str(db(db.image.product_name==row.product_id).select().first().s3_url)
            product_image_url=A(IMG(_src=srcattr), _href=URL('default','product',args=[row.product_id]))

            ## Add product information to the row list and then add that to the list of lists(rows)
            cart_grid_table_row_list=[product_image_url, product.product_name, row_cost_USD]
            cart_grid_row_LOL.append(cart_grid_table_row_list)


    ## If the user is not logged in but ready to checkout. 
    else:

        for key, value in session.cart.iteritems():

            product=db(db.product.id==key).select().first()

            cart_for_shipping_dict=dict(
                product_name=product.product_name, 
                product_cost=product.cost_USD,
                product_qty=value,
                product_weight=product.weight_oz,
                product_shipping_desc=product.shipping_description,
            )

            cart_for_shipping_calculations.append(cart_for_shipping_dict)

            cart_for_paypal_dict=dict(
                quantity=str(int(value)),
                name=product.product_name,
                price='{:.2f}'.format(product.cost_USD),
                currency='USD',
                description=product.shipping_description,
                )

            ## Append the product dict to the list of dicts for paypal
            cart_for_paypal_LOD.append(cart_for_paypal_dict)

            # Value is from session 
            cart_weight_oz+=float(product.weight_oz)*float(value)
            cart_cost_USD+=float(product.cost_USD)*float(value)
            row_cost_USD=float(product.cost_USD)*float(value)

            if sqlite_tf:
                srcattr=URL('download',db(db.image.product_name==key).select().first().s3_url)
            else:
                srcattr=S3_BUCKET_PREFIX+str(db(db.image.product_name==key).select().first().s3_url)
            product_image_url=A(IMG(_src=srcattr), _href=URL('default','product',args=[key]))

            cart_grid_table_row_list=[product_image_url, product.product_name, row_cost_USD]
            cart_grid_row_LOL.append(cart_grid_table_row_list)


    ## Generate the table, takes header info, row info, and then css class prefix
    cart_grid=table_generation(cart_grid_header_list, cart_grid_row_LOL, 'checkout_cart')

    ## Add total cart cost to the session for receipt info testing
    session.cart_cost_USD=cart_cost_USD


#############################################################################################
###########--------------------------Address Logic ------------------------------############
#############################################################################################

    address_grid_header_list=[
        'Street Line 1', 
        'Street Line 2', 
        'Municipality',
        'State or Equivilent',
        'Postal Code',
        'Country',
    ]

    ## If the user is logged in and ready to checkout
    if auth.is_logged_in():

        ## Get the address that they have as their default address
        address=db((db.addresses.user_id==auth.user_id)&(db.addresses.default_address==True)).select().first()

        address_dict=dict(
            street_address_line_1=address.street_address_line_1, 
            street_address_line_2=address.street_address_line_2, 
            municipality=address.municipality, 
            administrative_area=address.administrative_area, 
            postal_code=address.postal_code, 
            country=address.country,
        )

        address_grid_row_list=[
            address.street_address_line_1, 
            address.street_address_line_2, 
            address.municipality, 
            address.administrative_area, 
            address.postal_code, 
            address.country,
        ]
      
    ## If the user is not logged in but ready to checkout out
    else:

        ## You can get everything you need from the session. 
        address_dict=dict(
            street_address_line_1=session.address['street_address_line_1'],
            street_address_line_2=session.address['street_address_line_2'],
            municipality=session.address['municipality'],
            administrative_area=session.address['administrative_area'],
            postal_code=session.address['postal_code'],
            country=session.address['country'],
        )
       
        address_grid_row_list=[
            session.address['street_address_line_1'], 
            session.address['street_address_line_2'], 
            session.address['municipality'], 
            session.address['administrative_area'], 
            session.address['postal_code'], 
            session.address['country'],
        ]


    address_grid=table_generation(address_grid_header_list, [address_grid_row_list], 'checkout_address')




#############################################################################################
##########----------------------------Shipping Logic ----------------------------############
#############################################################################################

    ## Instead of using the shipping cost from the selected radio button,
    ## This is actually making another api call to easypost. That's super dumb.
    ## I have to change that right now. 
    # shipment=create_shipment(address_dict, cart_for_shipping_calculations)

    shipment=session.shipment_info_from_easypost

    shipping_grid_header_list=['Carrier', 'Service', 'Cost']

    shipping_grid_row_list=[]
    shipping_dict={}

    match_found=False
    shipping_cost_USD=0
    for rate in shipment.rates:
        if rate.service==session.shipping_choice:
            #create grid

            shipping_grid_row_list=[rate.carrier, rate.service, rate.rate, ]
            shipping_dict=dict(
                carrier=rate.carrier,
                service=rate.service,
                rate=rate.rate,
            )

            shipping_cost_USD=float(rate.rate)

            shipping_grid=table_generation(shipping_grid_header_list, [shipping_grid_row_list], 'checkout_shipping')

            match_found=True
        else:
            pass

    if match_found==False:
        shipping_grid=DIV("Go back to cart and select a shipping service")
    else:
        pass

    total_cost_USD=cart_cost_USD+shipping_cost_USD

    session.total_cost_USD=total_cost_USD



#############################################################################################
###########------------------------------Card Logic -----------------------------############
#############################################################################################

    card_grid_header_list=[
        'Name', 
        'Last 4', 
        'Card Type',
        'Expiration Month',
        'Expiration Year', 
    ]


    if auth.is_logged_in():

        ## If for some reason the payment method wasn't set, set an assumption?
        #if not session.payment_method:
        #    session.payment_method='stripe'

        if session.payment_method=='stripe':

            ## This is the url attached tothe pay button
            ## for paypal it will be more complicated. 
            approval_url=URL('pay')

            ## Retrieve the default card for the current customer by:
            ## Getting the stripe customer info from db with user_id
            stripe_customer_row=db(db.stripe_customers.muses_id==auth.user_id).select().first()

            ## From that get the customer id and default card id
            stripe_customer_token=stripe_customer_row.stripe_id
            stripe_customer_card=stripe_customer_row.stripe_next_card_id

            ## Use stripe API to retrieve customer and then to retrieve card from customer
            stripe_customer=stripe.Customer.retrieve(stripe_customer_token)
            stripe_card=stripe_customer.cards.retrieve(stripe_customer_card)

            ## Generate table information
            card_grid_row_list=[
                stripe_card['name'],
                stripe_card['last4'], 
                stripe_card['brand'], 
                stripe_card['exp_month'], 
                stripe_card['exp_year'],
            ]


        ## If not paying with stripe, then assume they are paying with Paypal
        ## For a logged in user and a non logged in user, the functionality
        ## right now is identical
        else:

            ## import all the helper stuff
            import paypalrestsdk
            from aux import get_env_var
            from aux import id_generator
            from aux import paypal_create_payment_dict

            ## Get the paypal keys
            PAYPAL_CLIENT_ID=get_env_var('paypal',PRODUCTION_STATUS,'PAYPAL_CLIENT_ID')
            PAYPAL_CLIENT_SECRET=get_env_var('paypal',PRODUCTION_STATUS,'PAYPAL_CLIENT_SECRET')

            ## configure paypal api with keys
            paypalrestsdk.configure({
                "mode": PAYPAL_MODE, # sandbox or live
                "client_id": PAYPAL_CLIENT_ID,
                "client_secret": PAYPAL_CLIENT_SECRET })


            invoice_number=id_generator()


            ## cart_for_paypal_LOD is from the cart logic section
            payment_dict=paypal_create_payment_dict(
                intent='sale',
                payment_method='paypal', 
                redirect_urls=dict(
                    return_url="https://threemusesglass.herokuapp.com/paypal_confirmation",
                    cancel_url="https://threemusesglass.herokuapp.com"),
                cost_dict=dict(
                    shipping_cost_USD=shipping_cost_USD, 
                    cart_cost_USD=cart_cost_USD, 
                    total_cost_USD=total_cost_USD),
                transaction_description='Purchase from ThreeMusesGlass',
                invoice_number=invoice_number,
                items_paypal_list_of_dicts=cart_for_paypal_LOD,)


            payment=paypalrestsdk.Payment(payment_dict)

            if payment.create():
                status="Created successfully"
                approval_url=payment['links'][1]['href']
                session.expect_paypal_webhook=True
                #session.payment_id=payment
            else:
                status=payment.error
                approval_url=status


            card_grid=DIV('You are using Paypal for this purchase')

            card_grid_header_list=[
                'Name', 
                'Email', 
                'Payment Type',
            ]

            card_grid_row_list=[
                'Name',
                'Email',
                'Paypal',
            ]

            #card_grid=table_generation(card_grid_header_list, [card_grid_row_list], 'checkout_card')


    ## Card logic for non logged in user. 
    else:

        ## The default choice thing?
        # if not session.payment_method:
        #    session.payment_method='stripe'

        if session.payment_method=='stripe':

            approval_url=URL('pay')

            card_grid_row_list=[
                session.card_info['name'],
                session.card_info['last4'],
                session.card_info['brand'],
                session.card_info['exp_month'],
                session.card_info['exp_year'],
                #session.card_info['card_id'],
            ]

            card_grid=table_generation(card_grid_header_list, [card_grid_row_list], 'checkout_card')


        else:

            import paypalrestsdk
            from aux import get_env_var
            from aux import id_generator
            from aux import paypal_create_payment_dict

            PAYPAL_CLIENT_ID=get_env_var('paypal', PRODUCTION_STATUS, 'PAYPAL_CLIENT_ID')
            PAYPAL_CLIENT_SECRET=get_env_var('paypal', PRODUCTION_STATUS, 'PAYPAL_CLIENT_SECRET')

            paypalrestsdk.configure({
                "mode": PAYPAL_MODE, # sandbox or live
                "client_id": PAYPAL_CLIENT_ID,
                "client_secret": PAYPAL_CLIENT_SECRET })

            invoice_number=id_generator()

            payment_dict=paypal_create_payment_dict(
                intent='sale',
                payment_method='paypal', 
                redirect_urls=dict(
                    return_url="https://threemusesglass.herokuapp.com/paypal_confirmation",
                    cancel_url="https://threemusesglass.herokuapp.com"),
                cost_dict=dict(
                    shipping_cost_USD=shipping_cost_USD, 
                    cart_cost_USD=cart_cost_USD, 
                    total_cost_USD=total_cost_USD),
                transaction_description='Purchase from ThreeMusesGlass',
                invoice_number=invoice_number,
                items_paypal_list_of_dicts=cart_for_paypal_LOD,)


            payment=paypalrestsdk.Payment(payment_dict)

            if payment.create():
                status="Created successfully"
                approval_url=payment['links'][1]['href']
                session.expect_paypal_webhook=True
                #session.payment_id=payment
            else:
                status=payment.error
                approval_url=status

            #return dict(status=status, approval_url=approval_url)

            card_grid=DIV('You are using Paypal for this purchase')

            card_grid_header_list=[
                'Name', 
                'Email', 
                'Payment Type',
            ]

            card_grid_row_list=[
                'Name',
                'Email',
                'Paypal',
            ]

            #card_grid=table_generation(card_grid_header_list, [card_grid_row_list], 'checkout_card')

    card_grid=table_generation(card_grid_header_list, [card_grid_row_list], 'checkout_card')




#############################################################################################
###########-----------------Summary Logic (User and Non User)--------------------############
#############################################################################################

    summary_grid_header_list=['Cart Cost','Shipping Cost', 'Total']
    summary_grid_row_lists=[cart_cost_USD,shipping_cost_USD,cart_cost_USD+shipping_cost_USD]

    summary_dict=dict(
        cart_cost_USD=cart_cost_USD,
        shipping_cost_USD=shipping_cost_USD,
        total_cost_USD=cart_cost_USD+shipping_cost_USD,
    )

    summary_grid=table_generation(summary_grid_header_list, [summary_grid_row_lists], "summary")

#############################################################################################
###########---------------------Put Everything in Session------------------------############
#############################################################################################


    ## Adding all the info to the session for use in databasing purchase history inforation
    ## list of dicts
    session.purchase_history_cart_info=cart_for_shipping_calculations

    ## dictionary of address info
    session.purchase_history_address_info=address_dict

    ## dictionary of shipping_info
    session.purchase_history_shipping_info=shipping_dict

    ## Card info is transferred via the stripe interface right now. 
    #session.purchase_history_card_info=card_grid_row_list

    ## dictionary of summary info
    session.purchase_history_summary_info=summary_dict

    return dict(
        cart_grid=cart_grid,
        address_grid=address_grid,
        shipping_grid=shipping_grid,
        card_grid=card_grid,
        summary_grid=summary_grid,
        approval_url=approval_url,
        )





def pay():

    import json

    #The purpose of this function is to populate the database table purchase history with all 
    # of the info about the purchase and ultimately generate a receipt looking thing. 
    # also send an email using postmark. 

    ## Try to put payment through. 
    if auth.is_logged_in():
        ## Get customer_id from stripe data in db
        customer_id=db(db.stripe_customers.muses_id==auth.user_id).select().first().stripe_id


        user_data=db(db.auth_user.id==auth.user_id).select().first()

        muses_id=user_data.id
        muses_email_address=user_data.email
        muses_name=user_data.first_name
        
    else:
        ## If anonymous user, get customer stripe id from session
        customer_id=session.card_info['stripe_id']
        muses_id=None
        muses_name=None

        

    ## Get total cost from session (Need to get a lot more than this I think)
    total_cost_USD=session.total_cost_USD


    ## To try and charge the card with the stripe id (defualt card should already be set within stripe)
    charge=stripe.Charge.create(
        amount=int(float(total_cost_USD)*100),
        currency='usd',
        customer=customer_id,
        #description='test purchase',
    )

    ## Set email address (if not logged in use stripe email)
    if auth.is_logged_in():
        pass
    else:
        ## change to the email from charge
        muses_email_address=session.card_info['email']


    ## Populating the purchase history dict
    ## This is used in the next view to show the user the purchase details. 
    purchase_history_dict=dict(

        muses_id=muses_id,
        muses_email_address=muses_email_address,
        muses_name=muses_name,

        ## Session Fields (These actually come from response not session)
        session_id_3muses=response.session_id_3muses,
        session_db_table=response.session_db_table,
        session_db_record_id=response.session_db_record_id,

        ## Shipping Fields
        shipping_street_address_line_1=session.purchase_history_address_info['street_address_line_1'],
        shipping_street_address_line_2=session.purchase_history_address_info['street_address_line_2'],
        shipping_municipality=session.purchase_history_address_info['municipality'],
        shipping_administrative_area=session.purchase_history_address_info['administrative_area'],
        shipping_postal_code=session.purchase_history_address_info['postal_code'],
        shipping_country=session.purchase_history_address_info['country'],

        ## Easypost Fields?
        easypost_shipping_service=session.purchase_history_shipping_info['service'],
        easypost_shipping_carrier=session.purchase_history_shipping_info['carrier'],
        easypost_shipment_id=None,#session.purchase_history_shipping_info['id'],
        easypost_rate_id=None,#session.purchase_history_shipping_info['shipment_id'],
        easypost_rate=session.purchase_history_shipping_info['rate'],
        easypost_api_response=session.shipping_json,


        ## Payment Fields
        payment_service='stripe',
        payment_confirmation_dictionary=json.dumps(charge, default=lambda x: None),


        ## Legacy Fields
        payment_method='stripe',
        payment_stripe_name=charge['card']['name'],
        payment_stripe_user_id=charge['customer'],
        payment_stripe_last_4=charge['card']['last4'],
        payment_stripe_brand=charge['card']['brand'],
        payment_stripe_exp_month=charge['card']['exp_month'],
        payment_stripe_exp_year=charge['card']['exp_year'],
        payment_stripe_card_id=charge['card']['id'],
        payment_stripe_transaction_id=charge['id'],

        ## Cart Details
        cart_base_cost=session.purchase_history_summary_info['cart_cost_USD'],
        cart_shipping_cost=session.purchase_history_summary_info['shipping_cost_USD'],
        cart_total_cost=session.purchase_history_summary_info['total_cost_USD'],

    )

    ## place data in the database. 
    purchase_history_data_id=db.purchase_history_data.bulk_insert([purchase_history_dict])[0]

    ## Add id of most recent purchase to the session for viewing purposes.
    session.session_purchase_history_data_id=purchase_history_data_id


    ## For every item in the cart, insert a record with the id of the purchase history, the product id and the qty.
    purchase_history_products_LOD=[]

    ## If logged in, get the cart information from the database
    if auth.is_logged_in():

        cart=db(db.muses_cart.user_id==auth.user_id).select()

        
        ## For item in cart, add id from record above with product and qty and all info about the product,
        ## then deal with inventory by removing the item from the cart.
        for row in cart:
            product_record=db(db.product.id==row.product_id).select().first()
            current_qty=int(product_record.qty_in_stock)
            qty_purchased=int(row.product_qty)
            new_qty=current_qty-qty_purchased

            ## Remove item from the cart
            db(db.muses_cart.product_id==product_record.id).delete()


            purchase_history_product_dict=dict(

                purchase_history_data_id=purchase_history_data_id,
                product_id=product_record.id,
                product_qty=int(row.product_qty),

                category_name=product_record.category_name,
                product_name=product_record.product_name,
                description=product_record.description,
                cost_USD=product_record.cost_USD,
                qty_in_stock=new_qty,
                is_active=product_record.is_active,
                display_order=product_record.display_order,
                shipping_description=product_record.shipping_description,
                weight_oz=product_record.weight_oz,

            )

            ## Generate a list of dicts to use bulk insert
            purchase_history_products_LOD.append(purchase_history_product_dict)


            ## If you lowered the qty to 0 or less, make qty 0 and deactivate item
            if new_qty<=0:

                product_record.update(qty_in_stock=0)
                product_record.update_record()
                product_record.update(is_active=False)
                product_record.update_record()

            ## If not, just lower the qty
            else:
                product_record.update(qty_in_stock=new_qty)
                product_record.update_record()

    ## If the user is not logged in, get the cart information from session. 
    else:


        for product_id, qty in session.cart.iteritems():
            product_record=db(db.product.id==product_id).select().first()
            current_qty=int(product_record.qty_in_stock)
            qty_purchased=int(qty)
            new_qty=current_qty-qty_purchased


            purchase_history_product_dict=dict(

                purchase_history_data_id=purchase_history_data_id,
                product_id=product_record.id,
                product_qty=qty_purchased,

                category_name=product_record.category_name,
                product_name=product_record.product_name,
                description=product_record.description,
                cost_USD=product_record.cost_USD,
                qty_in_stock=new_qty,
                is_active=product_record.is_active,
                display_order=product_record.display_order,
                shipping_description=product_record.shipping_description,
                weight_oz=product_record.weight_oz,

            )

            ## Generate a list of dicts to use bulk insert
            purchase_history_products_LOD.append(purchase_history_product_dict)


            if new_qty<=0:
                product_record.update(qty_in_stock=0)
                product_record.update_record()
                product_record.update(is_active=False)
                product_record.update_record()
            else:
                product_record.update(qty_in_stock=new_qty)
                product_record.update_record()

        session.cart=None



    purchase_history_products_ids=db.purchase_history_products.bulk_insert(purchase_history_products_LOD)




####### This is where I need to make the reciept! DO IT!




## This is a scary place in the code 
## if True, lol









#What confirmation thing are you trying to view?
    #purchase_history_data_id=38#request.args[0]

##   try:
    #Try to convert and compare the url arg with the session arg that the user is allowed to view. 
    if True: #int(purchase_history_data_id)==int(session.session_purchase_history_data_id):

        ## if success, then get the corresponding db info
        purchase_history_data_row=db(db.purchase_history_data.id==purchase_history_data_id).select().first()

        purchase_history_products_rows=db(db.purchase_history_products.purchase_history_data_id==purchase_history_data_id).select()

        ## product table
        product_header_row=['Product','Total Weight (oz)','Total Cost($)']
        product_table_row_LOL=[]
        product_total_weight=0
        product_total_cost=0

        ## change this so that you don't have to go into the product database to get this data
        ## It should all be available in the other purchase history tables. 
        ## I'm doing this because the product table has all editable stuff
        ## And I want a more permanent record of the transaction. 
        for row in purchase_history_products_rows:
            #product_data=db(db.product.id==row.product_id).select().first()

            line_item_weight_oz=int(row.product_qty)*int(row.weight_oz)
            line_item_cost_usd=int(row.product_qty)*int(row.cost_USD)

            product_table_row=[
                row.product_name,
                line_item_weight_oz,
                line_item_cost_usd,
            ]

            product_total_weight+=line_item_weight_oz
            product_total_cost+=line_item_cost_usd

            product_table_row_LOL.append(product_table_row)

        product_totals_row=['Total',product_total_weight,product_total_cost,]

        product_table_row_LOL.append(product_totals_row)

        confirmation_product_grid=table_generation(product_header_row,product_table_row_LOL,'confirmation_product')


        ##Shipping Address Table
        address_header_row=['Street Address Info', 'Local Address Info', 'Country']
        address_table_row_LOL=[[
            purchase_history_data_row.shipping_street_address_line_1+" "+purchase_history_data_row.shipping_street_address_line_2,
            purchase_history_data_row.shipping_municipality+", "+purchase_history_data_row.shipping_administrative_area+" "+purchase_history_data_row.shipping_postal_code,
            purchase_history_data_row.shipping_country,
        ]]

        confirmation_address_grid=table_generation(address_header_row,address_table_row_LOL,"confirmation_address")


        ##Shipping Info Table
        shipping_header_row=['Carrier-Rate', 'Shipping Weight (Oz)', 'Estimated Shipping Cost ($)']
        shipping_table_row_LOL=[[
            purchase_history_data_row.easypost_shipping_carrier + " - " + purchase_history_data_row.easypost_shipping_service,
            product_total_weight,
            purchase_history_data_row.easypost_rate,
        ]]

        confirmation_shipping_grid=table_generation(shipping_header_row,shipping_table_row_LOL,"confirmation_shipping")


        ##Card Table
        card_header_row=['Name', 'Brand-Last4', 'Expiration(mm/yyyy)']
        card_table_row_LOL=[[
            purchase_history_data_row.payment_stripe_name,
            purchase_history_data_row.payment_stripe_brand + " - " + purchase_history_data_row.payment_stripe_last_4,
            purchase_history_data_row.payment_stripe_exp_month + " / " + purchase_history_data_row.payment_stripe_exp_year,
        ]]

        confirmation_card_grid=table_generation(card_header_row,card_table_row_LOL,"confirmation_card")


        ##Summary Table

        summary_header_row=['Shipping Cost ($)', 'Product Cost ($)', 'Total Cost ($)']
        summary_table_row_LOL=[[
            purchase_history_data_row.easypost_rate,
            product_total_cost,
            float(purchase_history_data_row.easypost_rate)+product_total_cost,
        ]]

        confirmation_summary_grid=table_generation(summary_header_row,summary_table_row_LOL,"confirmation_summary")

        final_div=DIV(_class="muses_pay")
        final_div.append(DIV("Product Details",_class="confirmation_heading"))
        final_div.append(confirmation_product_grid)
        final_div.append(DIV("Address Details",_class="confirmation_heading"))
        final_div.append(confirmation_address_grid)
        final_div.append(DIV("Shipping Details",_class="confirmation_heading"))
        final_div.append(confirmation_shipping_grid)
        final_div.append(DIV("Payment Details",_class="confirmation_heading"))
        final_div.append(confirmation_card_grid)
        final_div.append(DIV("Summary",_class="confirmation_heading"))
        final_div.append(confirmation_summary_grid)
        

    #     return dict(
    #         final_div=final_div,
    #         purchase_history_data_row = purchase_history_data_row,
    #         purchase_history_products_rows = purchase_history_products_rows,
    #         #confirmation_product_grid = confirmation_product_grid,
    #     )

    # ## if not, they are trying to view something they don't have access to.
    # else:
    #     ## This is not the place for a user to be looking around past purchases. If it's not in session
    #     ## They can't see it here. 
    #     return dict(
    #         purchase_history_data_row = "SessionError",
    #         purchase_history_products_rows = None,
    #     )

    # ## If the url arg is not convertible to an integer, than you get this error.
    # ## just return same stuff. 
    # except ValueError:
    #         return dict(
    #             purchase_history_data_row = "ValueError",
    #             purchase_history_products_rows = None,
    #         )

    # except TypeError:
    #         return dict(
    #             purchase_history_data_row = "TypeError",
    #             purchase_history_products_rows = None,
    #         )

    #final_div['styles']
    final_div_html=final_div.xml()


    email_icons=dict(
        products_icon_url="https://s3.amazonaws.com/threemusesglass/icons/ProductIcon.png",
        address_icon_url="https://s3.amazonaws.com/threemusesglass/icons/AddressIcon.png",
        shipping_icon_url="https://s3.amazonaws.com/threemusesglass/icons/ShippingIcon.png",
        payment_icon_url="https://s3.amazonaws.com/threemusesglass/icons/PaymentIcon.png",
        summary_icon_url="https://s3.amazonaws.com/threemusesglass/icons/SummaryIcon.png",
        )

    #purchase_history_dict
    #purchase_history_products_LOD

    ## Try to overwrite the date with a string and convert back later using dateutil if necessary

    receipt_context=dict(
        email_icons=email_icons,
        #purchase_details=purchase_history_dict,
        #product_details=purchase_history_products_LOD,
        product_info=product_table_row_LOL,
        address_info=address_table_row_LOL,
        shipping_info=shipping_table_row_LOL,
        card_info=card_table_row_LOL,
        summary_info=summary_table_row_LOL,
        )

    #receipt_message_html = response.render('receipt.html', receipt_context)
    receipt_message_html = response.render('default/receipt.html', receipt_context)


    from postmark import PMMail
    message = PMMail(api_key=POSTMARK_API_KEY,
        subject="Order Confirmation",
        sender="confirmation@threemuses.glass",
        to=muses_email_address,
        #html_body=final_div_html,
        html_body=receipt_message_html,
        tag="confirmation")
    message.send()


    ## This has to be last, duh.
    redirect(URL('confirmation', args=(purchase_history_data_id)))


def confirmation():

    ## This function has a problem with deleting a user
    ## And then someone reusing the same email when they sign up
    ## FIX IT. 

    #What confirmation thing are you trying to view?
    

    # try:
    #     active_purchase_history_data_id=int(session.session_purchase_history_data_id)
    # except TypeError:
    #     active_purchase_history_data_id=-10


    try:
        purchase_history_data_id=request.args[0]
    #Try to convert and compare the url arg with the session arg that the user is allowed to view. 
        if int(purchase_history_data_id)==int(session.session_purchase_history_data_id):

            ## if success, then get the corresponding db info
            purchase_history_data_row=db(db.purchase_history_data.id==purchase_history_data_id).select().first()

            purchase_history_products_rows=db(db.purchase_history_products.purchase_history_data_id==purchase_history_data_id).select()

            ## product table
            product_header_row=['Product','Total Weight (oz)','Total Cost($)']
            product_table_row_LOL=[]
            product_total_weight=0
            product_total_cost=0

            ## change this so that you don't have to go into the product database to get this data
            ## It should all be available in the other purchase history tables. 
            ## I'm doing this because the product table has all editable stuff
            ## And I want a more permanent record of the transaction. 
            for row in purchase_history_products_rows:
                #product_data=db(db.product.id==row.product_id).select().first()

                line_item_weight_oz=int(row.product_qty)*int(row.weight_oz)
                line_item_cost_usd=int(row.product_qty)*int(row.cost_USD)

                product_table_row=[
                    row.product_name,
                    line_item_weight_oz,
                    line_item_cost_usd,
                ]

                product_total_weight+=line_item_weight_oz
                product_total_cost+=line_item_cost_usd

                product_table_row_LOL.append(product_table_row)

            product_totals_row=['Total',product_total_weight,product_total_cost,]

            product_table_row_LOL.append(product_totals_row)

            confirmation_product_grid=table_generation(product_header_row,product_table_row_LOL,'confirmation_product')


            ##Shipping Address Table
            address_header_row=['Street Address Info', 'Local Address Info', 'Country']
            address_table_row_LOL=[[
                purchase_history_data_row.shipping_street_address_line_1+" "+purchase_history_data_row.shipping_street_address_line_2,
                purchase_history_data_row.shipping_municipality+", "+purchase_history_data_row.shipping_administrative_area+" "+purchase_history_data_row.shipping_postal_code,
                purchase_history_data_row.shipping_country,
            ]]

            confirmation_address_grid=table_generation(address_header_row,address_table_row_LOL,"confirmation_address")


            ##Shipping Info Table
            shipping_header_row=['Carrier-Rate', 'Shipping Weight (Oz)', 'Estimated Shipping Cost ($)']
            shipping_table_row_LOL=[[
                purchase_history_data_row.easypost_shipping_carrier + " - " + purchase_history_data_row.easypost_shipping_service,
                product_total_weight,
                purchase_history_data_row.easypost_rate,
            ]]

            confirmation_shipping_grid=table_generation(shipping_header_row,shipping_table_row_LOL,"confirmation_shipping")


            ##Card Table
            if purchase_history_data_row.payment_method=='stripe':
                card_header_row=['Name', 'Brand-Last4', 'Expiration(mm/yyyy)']
                card_table_row_LOL=[[
                    purchase_history_data_row.payment_stripe_name,
                    purchase_history_data_row.payment_stripe_brand + " - " + purchase_history_data_row.payment_stripe_last_4,
                    purchase_history_data_row.payment_stripe_exp_month + " / " + purchase_history_data_row.payment_stripe_exp_year,
                ]]

            elif purchase_history_data_row.payment_method=='paypal':
                card_header_row=['Name', 'Paypal Email', 'Something Else']
                card_table_row_LOL=[[
                    'Name', 'Email', 'Else'
                ]]

            confirmation_card_grid=table_generation(card_header_row,card_table_row_LOL,"confirmation_card")


            ##Summary Table

            summary_header_row=['Shipping Cost ($)', 'Product Cost ($)', 'Total Cost ($)']
            summary_table_row_LOL=[[
                purchase_history_data_row.easypost_rate,
                product_total_cost,
                float(purchase_history_data_row.easypost_rate)+product_total_cost,
            ]]

            confirmation_summary_grid=table_generation(summary_header_row,summary_table_row_LOL,"confirmation_summary")

            final_div=DIV()
            final_div.append(DIV("Product Details",_class="confirmation_heading"))
            final_div.append(confirmation_product_grid)
            final_div.append(DIV("Address Details",_class="confirmation_heading"))
            final_div.append(confirmation_address_grid)
            final_div.append(DIV("Shipping Details",_class="confirmation_heading"))
            final_div.append(confirmation_shipping_grid)
            final_div.append(DIV("Payment Details",_class="confirmation_heading"))
            final_div.append(confirmation_card_grid)
            final_div.append(DIV("Summary",_class="confirmation_heading"))
            final_div.append(confirmation_summary_grid)
            

            return dict(
                final_div=final_div,
                purchase_history_data_row = purchase_history_data_row,
                purchase_history_products_rows = purchase_history_products_rows,
                #confirmation_product_grid = confirmation_product_grid,
            )

        ## if not, they are trying to view something they don't have access to.
        else:
            ## This is not the place for a user to be looking around past purchases. If it's not in session
            ## They can't see it here. 
            return dict(
                purchase_history_data_row = "SessionError",
                purchase_history_products_rows = None,
            )

    ## If the url arg is not convertible to an integer, than you get this error.
    ## just return same stuff. 
    except ValueError:
            return dict(
                purchase_history_data_row = "ValueError",
                purchase_history_products_rows = None,
            )

    except TypeError:
            return dict(
                purchase_history_data_row = "TypeError",
                purchase_history_products_rows = None,
            )

    except IndexError:
        return dict(
                purchase_history_data_row = "IndexError",
                purchase_history_products_rows = None,
            )



# def sessions():
#     session_db=db(db.web2py_session_3muses).select()[0].session_data
#     return dict(session_db=session_db)



## Functions that require admin priveledges. These are so my mom can update products and stuff
## without bothering me. 

# @auth.requires_membership('admin')
# def manage():

#     if not request.args:

#         title="Manage Page"
#         grid="List items for manage pages"

#     elif request.args[0]=='products':

#         grid=SQLFORM.grid(
#             db.product, 
#             maxtextlength=100,
#             )
#         grid.element('.web2py_counter', replace=None)

#         title="Product Grid"

#     elif request.args[0]=='product_images':

#         grid=SQLFORM.grid(db.image,maxtextlength=100)
#         return redirect(URL('cart'))

#         grid.element('.web2py_counter', replace=None)

#         title="Product Images Grid"


#     elif request.args[0]=='test':
#         title='test'
#         grid='test'

#     elif request.args[0]=='categories':

#         grid=SQLFORM.grid(db.categories,
#             maxtextlength=100,)
#         grid.element('.web2py_counter', replace=None)

#         title='categories'

#     else:
#         return redirect(URL('manage'))

#     return dict(title=title, grid=grid)



@auth.requires_membership('admin')
def manage_products():
    product_grid=SQLFORM.grid(db.product, 
        # fields=[
        #     db.product.product_name, 
        #     db.product.description, 
        #     db.product.cost_USD,
        #     db.product.is_active,
        # ], 
        maxtextlength=100,
        )

    product_grid.element('.web2py_counter', replace=None)

    return dict(product_grid=product_grid)



@auth.requires_membership('admin')
def manage_product_images():
    image_grid=SQLFORM.grid(db.image, 
        # fields=[
        #     db.image.category_name, 
        #     db.image.product_name, 
        #     db.image.title,
        #     db.image.s3_url
        # ],
        maxtextlength=100)

    image_grid.element('.web2py_counter', replace=None)
    return dict(grid=image_grid)



@auth.requires_membership('admin')
def manage_categories():
    category_grid=SQLFORM.grid(db.categories, 
        # fields=[
        #     db.categories.category_name,
        #     db.categories.category_description,
        #     db.categories.s3_url,
        # ],
        maxtextlength=100,
        )

    category_grid.element('.web2py_counter', replace=None)
    return dict(grid=category_grid)

@auth.requires_membership('admin')
def manage_purchase_history_data():
    purchase_history_data_grid=SQLFORM.grid(db.purchase_history_data, 
        # fields=[
        #     db.categories.category_name,
        #     db.categories.category_description,
        #     db.categories.s3_url,
        # ],
        maxtextlength=100,
        )

    purchase_history_data_grid.element('.web2py_counter', replace=None)
    return dict(purchase_history_data_grid=purchase_history_data_grid)

@auth.requires_membership('admin')
def manage_purchase_history_products():
    
    purchase_history_products_grid=SQLFORM.grid(db.purchase_history_products, 
        # fields=[
        #     db.categories.category_name,
        #     db.categories.category_description,
        #     db.categories.s3_url,
        # ],
        maxtextlength=100,
        )

    purchase_history_products_grid.element('.web2py_counter', replace=None)

    return dict(purchase_history_products_grid=purchase_history_products_grid)



@auth.requires_membership('admin')
def manage_landing_page_images():
    landing_page_image_grid=SQLFORM.grid(db.landing_page_images,
        maxtextlength=100,
        )

    landing_page_image_grid.element('.web2py_counter', replace=None)
    return locals()

@auth.requires_membership('admin')
def reset_inventory():

    products=db(db.product.display_order<500).select()

    for product_record in products:

        product_record.update(qty_in_stock=1)
        product_record.update_record()
        product_record.update(is_active=True)
        product_record.update_record()

    #return dict(message="Done!")
    redirect(URL('categories'))

# @auth.requires_membership('admin')
# def set_order_number():

#     session.session_purchase_history_data_id=request.args[0]

#     return dict(message="Done!")



## pulled from a random place on the internet, currently is not being used. 
def handle_error():
    """ Custom error handler that returns correct status codes."""
    
    code = request.vars.code
    request_url = request.vars.request_url
    ticket = request.vars.ticket

    debug=False

    if request.env.http_host[:9]=='localhost':
        debug=True


 
    if code is not None and request_url != request.url: # Make sure error url is not current url to avoid infinite loop.
        response.status = int(code) # Assign the error status code to the current response. (Must be integer to work.)
 
    if code == '403':

        error_page=DIV(_class='error_page_container')

        error_page.append(DIV("You are not authoized to view this page, apparently."))
        error_page.append(DIV("That's not a challenge, though. I know you could if you really wanted to."))

    elif code == '404':

        error_page=DIV(_class='error_page_container')

        error_url=request.env.http_host+request_url

        error_page.append(DIV("On second thought, let's not go to " + 
            error_url + ". 'Tis a silly place."))

        error_page.append(DIV("This URL is currently not mapped to anything. Sorry!"))
        #error_page.append(DIV(request.env.http_host+request_url))


        return dict(error_page=error_page)


    elif code == '500':
        
        # Get ticket URL:
        #ticket_url = "<a href='%(scheme)s://%(host)s/admin/default/ticket/%(ticket)s' target='_blank'>%(ticket)s</a>" % {'scheme':'https','host':request.env.http_host,'ticket':ticket}

        if debug==True:
            ticket_url = A(_href='/admin/default/ticket/%(ticket)s' % {'ticket':ticket}, _target='_blank'
            )

        else:
            ticket_url = A(_href='%(scheme)s://%(host)s/admin/default/ticket/%(ticket)s' % {'scheme':'https','host':request.env.http_host, 'ticket':ticket}, _target='_blank'
            )

        error_page=DIV(_class='error_page_container')
        if auth.has_membership('admin'):
            error_page.append(DIV('A server error has occured, because you are an admin\
                you can see the following link to the ticket that was raised:'))
            error_page.append(ticket_url)

        elif debug==True:
            error_page.append(DIV('A server error has occured, because you are running on local host\
                you can see the following link to the ticket that was raised:'))
            error_page.append(ticket_url)

        else:
            error_page.append(DIV("Oh no! What did you do! Just kidding, this error is on us!\
                a ticket is being mailed to an admin and we'll get right on this issue."))
            error_page.append(DIV(ticket_url))

            from postmark import PMMail
            message = PMMail(api_key=POSTMARK_API_KEY,
                subject="A ticket was raised",
                sender="confirmation@threemuses.glass",
                to="wantsomechocolate@gmail.com",
                #html_body=final_div_html,
                html_body=error_page.xml(),
                tag="web2py_ticket")
            message.send()




        # Email a notice, etc:
       # mail.send(to=['admins@myapp.com '],
       #             subject="New Error",
       #             message="Error Ticket:  %s" % ticket_url)
        
        return dict(error_page=error_page)
    
    else:
        return dict(
            error_page="Congratulaions, you've passed all the errors handling and went straight to this catch-all error page.",
            )



## functions that come with the welcome app ##
def user():
    
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """

    ## This is what I had in the user.html doc to do the purchase history
    # <h2>Purchase History</h2>
    # {{purchase_history=db(db.purchase_history_data.muses_id==auth.user_id).select()}}
    # {{for purchase in purchase_history:}}
    #     <h3>Purchase Details</h3>
    #     {{=purchase}}
    #     <h3>Purchase Products</h3>
    #     {{purchase_history_products=db(db.purchase_history_products.purchase_history_data_id==purchase.id).select()}}
    #     {{=purchase_history_products}}

    # {{pass}}


    #purchase_history=db(db.purchase_history_data.muses_id==auth.user_id).select()
    #for purchase in purchase_history:
        #purchase_history_products=db(db.purchase_history_products.purchase_history_data_id==purchase.id).select()

    ## create a table with a row for each purchase and a link to each purchases' corresponding products.
    ## Have the ability to be able to look at all products. 

    ## Use custom tables or web2py tables for this? With web2py tables user can export
    ## filter, sort. I'm going to try using web2py tables first. 

    #grid=SQLFORM.smartgrid(db.purchase_history_data, linked_tables=['purchase_history_products'])

    return dict(form=auth())



@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)



def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()



@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())





## Random CRUD operations
def delete_item_from_cart():

    ## pri_key is the primary key referencing the muses_cart db table, which holds records for 
    ## every user and every item that user has in their cart. This function can only delete a single item at a time
    if auth.is_logged_in():
        del db.muses_cart[request.vars['pri_key']]
    else:
        dummy=session.cart.pop(request.vars['pri_key'])

    redirect(request.vars['redirect_url'])


def delete_address():
    if auth.is_logged_in():
        del db.addresses[request.vars['pri_key']]
    else:
        dummy=session.pop('address')
    redirect(request.vars['redirect_url'])


def delete_card():
    if auth.is_logged_in():
        ## This actually isn't deleting anything from the database. 
        ## It collects the customer and card id passed to the function via request
        ## and tells stripe to delete the card from the user.
        customer = stripe.Customer.retrieve(request.vars['customer_id'])
        customer.cards.retrieve(request.vars['card_id']).delete()

        redirect(request.vars['redirect_url'])

    else:
        ## The add_new_card function adds the 'stripe_id' to the session.
        ## Retrieve it here 
        stripe_id=session.card_info['stripe_id']

        ## To then retrieve that customer using stripe API and delete it
        ## Need to add some code in here to handle when communication with Stripe is unavailable.
        customer=stripe.Customer.retrieve(stripe_id)
        customer.delete()

    redirect(request.vars['redirect_url'])


def delete_item_from_db_card():

    ## This actually isn't deleting anything from the database. 
    ## It collects the customer and card id passed to the function via request
    ## and tells stripe to delete the card from the user.
    customer = stripe.Customer.retrieve(request.vars['customer_id'])
    customer.cards.retrieve(request.vars['card_id']).delete()

    redirect(URL('cart'))

## removes customer from stripe and current session
def delete_item_from_session_card():

    ## The add_new_card function adds the 'stripe_id' to the session.
    ## Retrieve it here 
    stripe_id=session.card_info['stripe_id']

    ## To then retrieve that customer using stripe API and delete it
    ## Need to add some code in here to handle when communication with Stripe is unavailable.
    customer=stripe.Customer.retrieve(stripe_id)
    customer.delete()

    ## After deleting the customer from the stripe db remove the card info from the session.
    dummy=session.pop('card_info')

    redirect(URL('cart'))





## Functions to edit items in session

def edit_session_address():

    edit_address_form=FORM(

        DIV( 
            LABEL( 'First Name',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='first_name', 
                    _class='form-control',
                    _value=session.address['first_name'],
                ),
            ),
        ),

        DIV( 
            LABEL( 'Last Name',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='last_name', 
                    _class='form-control',
                    _value=session.address['last_name'],
                ),
            ),
        ),

        DIV( 
            LABEL( 'Street Address/ PO Box/ Etc.',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='street_address_line_1', 
                    _class='form-control',
                    _value=session.address['street_address_line_1'],
                ),
            ),
        ),

        DIV( 
            LABEL( 'Floor/ Suite/ Apt/ Etc.',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='street_address_line_2', 
                    _class='form-control', 
                    _value=session.address['street_address_line_2'],
                ),
            ),
        ),

        DIV(
            LABEL('Municipality',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='municipality', 
                    _class='form-control', 
                    _value=session.address['municipality'],
                ),
            ),
        ),

        DIV(
            LABEL('Administrative Area',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='administrative_area', 
                    _class='form-control', 
                    _value=session.address['administrative_area'],
                ),
            ),
        ),

        DIV(
            LABEL('Postal Code',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='postal_code', 
                    _class='form-control', 
                    _value=session.address['postal_code'],
                ),
            ),
        ),

        DIV(
            LABEL('Country',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='country', 
                    _class='form-control', 
                    _value=session.address['country'],
                ),
            ),
        ),
   
        INPUT(_type='submit', _class="btn btn-default"),
            
    _class='form-horizontal',
    _role='form').process()

    if edit_address_form.accepted:

        if auth.is_logged_in():
            pass
            # db.addresses.insert(
            #     user_id=auth.user_id,
            #     street_address_line_1=add_address_form.vars.street_address_line_1,
            #     street_address_line_2=add_address_form.vars.street_address_line_2,
            #     municipality=add_address_form.vars.municipality,
            #     administrative_area=add_address_form.vars.administrative_area,
            #     postal_code=add_address_form.vars.postal_code,
            #     country=add_address_form.vars.country,
            # )

        else:
            session.address=dict(
                first_name=edit_address_form.vars.first_name,
                last_name=edit_address_form.vars.last_name,
                street_address_line_1=edit_address_form.vars.street_address_line_1,
                street_address_line_2=edit_address_form.vars.street_address_line_2,
                municipality=edit_address_form.vars.municipality,
                administrative_area=edit_address_form.vars.administrative_area,
                postal_code=edit_address_form.vars.postal_code,
                country=edit_address_form.vars.country,
            )

        redirect(URL('cart'))

    else:
        
        return dict(edit_address_form=edit_address_form)


#functions to edit things in db

def edit_db_address():

    #if auth.is_logged_in:

    address_row=db(db.addresses.id==request.vars['pri_key']).select()[0]

    edit_address_form=FORM(
        DIV( 
            LABEL( 'Street Address/ PO Box/ Etc.',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='street_address_line_1', 
                    _class='form-control',
                    _value=address_row['street_address_line_1'],
                ),
            ),
        ),

        DIV( 
            LABEL( 'Floor/ Suite/ Apt/ Etc.',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='street_address_line_2', 
                    _class='form-control', 
                    _value=address_row['street_address_line_2'],
                ),
            ),
        ),

        DIV(
            LABEL('Municipality',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='municipality', 
                    _class='form-control', 
                    _value=address_row['municipality'],
                ),
            ),
        ),

        DIV(
            LABEL('Administrative Area',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='administrative_area', 
                    _class='form-control', 
                    _value=address_row['administrative_area'],
                ),
            ),
        ),

        DIV(
            LABEL('Postal Code',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='postal_code', 
                    _class='form-control', 
                    _value=address_row['postal_code'],
                ),
            ),
        ),

        DIV(
            LABEL('Country',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='country', 
                    _class='form-control', 
                    _value=address_row['country'],
                ),
            ),
        ),
   
        INPUT(_type='submit', _class="btn btn-default"),
            
    _class='form-horizontal',
    _role='form').process()

    if edit_address_form.accepted:

        if auth.is_logged_in():
            db.addresses[request.vars['pri_key']]=dict(
                street_address_line_1=edit_address_form.vars.street_address_line_1,
                street_address_line_2=edit_address_form.vars.street_address_line_2,
                municipality=edit_address_form.vars.municipality,
                administrative_area=edit_address_form.vars.administrative_area,
                postal_code=edit_address_form.vars.postal_code,
                country=edit_address_form.vars.country,
                )
            # db.addresses.insert(
            #     user_id=auth.user_id,
            #     street_address_line_1=add_address_form.vars.street_address_line_1,
            #     street_address_line_2=add_address_form.vars.street_address_line_2,
            #     municipality=add_address_form.vars.municipality,
            #     administrative_area=add_address_form.vars.administrative_area,
            #     postal_code=add_address_form.vars.postal_code,
            #     country=add_address_form.vars.country,
            # )

        else:
            pass

        redirect(URL('cart'))

    else:
        
        return dict(edit_address_form=edit_address_form)




def edit_address():


    if auth.is_logged_in():
        address_pre_changes_dict=db(db.addresses.id==request.vars['pri_key']).select()[0]
        #address_row['street_address_line_1'],

    else:
        address_pre_changes_dict=session.address
        #session.address['first_name']

    edit_address_form=FORM(

        DIV( 
            LABEL( 'First Name',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='first_name', 
                    _class='form-control',
                    _value=address_pre_changes_dict['first_name'],
                ),
            ),
        ),

        DIV( 
            LABEL( 'Last Name',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='last_name', 
                    _class='form-control',
                    _value=address_pre_changes_dict['last_name'],
                ),
            ),
        ),

        DIV( 
            LABEL( 'Street Address/ PO Box/ Etc.',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='street_address_line_1', 
                    _class='form-control',
                    _value=address_pre_changes_dict['street_address_line_1'],
                ),
            ),
        ),

        DIV( 
            LABEL( 'Floor/ Suite/ Apt/ Etc.',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='street_address_line_2', 
                    _class='form-control', 
                    _value=address_pre_changes_dict['street_address_line_2'],
                ),
            ),
        ),

        DIV(
            LABEL('Municipality',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='municipality', 
                    _class='form-control', 
                    _value=address_pre_changes_dict['municipality'],
                ),
            ),
        ),

        DIV(
            LABEL('Administrative Area',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='administrative_area', 
                    _class='form-control', 
                    _value=address_pre_changes_dict['administrative_area'],
                ),
            ),
        ),

        DIV(
            LABEL('Postal Code',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='postal_code', 
                    _class='form-control', 
                    _value=address_pre_changes_dict['postal_code'],
                ),
            ),
        ),

        DIV(
            LABEL('Country',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='country', 
                    _class='form-control', 
                    _value=address_pre_changes_dict['country'],
                ),
            ),
        ),
   
        INPUT(_type='submit', _class="btn btn-default"),
            
    _class='form-horizontal',
    _role='form').process()

    if edit_address_form.accepted:

        address_post_changes_dict=dict(
                first_name=edit_address_form.vars.first_name,
                last_name=edit_address_form.vars.last_name,
                street_address_line_1=edit_address_form.vars.street_address_line_1,
                street_address_line_2=edit_address_form.vars.street_address_line_2,
                municipality=edit_address_form.vars.municipality,
                administrative_area=edit_address_form.vars.administrative_area,
                postal_code=edit_address_form.vars.postal_code,
                country=edit_address_form.vars.country,
                default_address=True,
                )

        if auth.is_logged_in():
            db.addresses[request.vars['pri_key']]=address_post_changes_dict

        else:
            session.address=address_post_changes_dict

        redirect(URL('cart'))

    else:
        
        return dict(edit_address_form=edit_address_form)







def default_address_2():
    session.test_var=request.vars.default_address_id
    if auth.is_logged_in():
        rows=db((db.addresses.user_id==auth.user_id)&(db.addresses.default_address==True)).select()
        for row in rows:
            row.default_choice=False
        db(db.addresses.id==request.vars.default_address_id).select()[0].default_address=True

    

    return locals()

def ajax_shipping_information():

    #try:
    import easypost
    import json
    from aux import create_shipment

    default_address_id=int(request.vars.new_choice)
    #default_address_id=10
    session.default_address_id=default_address_id
    

    ## Get all the addresses associated with the current user that are set 
    ## to be the default (should only be one, but who knows)
    addresses=db((db.addresses.user_id==auth.user_id)&(db.addresses.default_address==True)).select()

    ## Set the default address flag of every address to False
    for address_row in addresses:
        address_row.update(default_address=False)
        address_row.update_record()

    ## Make a brand new request to the db? but this time only select the 
    ## address targeted to be the default.
    address = db(db.addresses.id==default_address_id).select().first()
    ## address=db((db.addresses.user_id==auth.user_id)&(db.addresses.default_address==True)).select().first()
    address.update(default_address=True)
    address.update_record()


    ## Prepare an address dict
    address_info=dict(
        street_address_line_1=address.street_address_line_1, 
        street_address_line_2=address.street_address_line_2, 
        municipality=address.municipality, 
        administrative_area=address.administrative_area, 
        postal_code=address.postal_code, 
        country=address.country,
    )

    ## Now get all the items in the current user's cart.
    cart=db(db.muses_cart.user_id==auth.user_id).select()

    if not cart:
        error_status=True
        error_message='There is nothing in your cart to ship'
        return json.dumps(dict(error_status=error_status, error_message=error_message, shipping_options_LOD=[]))

    cart_for_shipping_calculations=[]
    cart_weight_oz=0
    cart_cost_USD=0

    for row in cart:
        product=db(db.product.id==row.product_id).select().first()
        cart_weight_oz+=float(product.weight_oz)*float(row.product_qty)
        cart_cost_USD+=float(product.cost_USD)*float(row.product_qty)

        cart_for_shipping_calculations.append(dict(
            product_name=product.product_name,
            product_cost=product.cost_USD,
            product_qty=row.product_qty,
            product_weight=product.weight_oz,
            product_shipping_desc=product.shipping_description,
            ))

    shipping_options_LOD=[]
    error_status=False
    error_message=None
    shipping_information=dict(
        shipping_options_LOD=shipping_options_LOD,
        error_status=error_status,
        error_message=error_message,
        )

    try:
        # now logged in or not we have the address that was chosen, the address info for the address that was chosen
        # and the cart info, and the combined weight of our package.
        shipment=create_shipment(address_info, cart_for_shipping_calculations)


        ## Put shipment info in the session to get it later!
        session.shipment_info_from_easypost=shipment

        # Generate list of sorted rates
        shipping_rates_for_sorting=[]
        for i in range(len(shipment.rates)):
            shipping_rates_for_sorting.append(float(shipment.rates[i].rate))
        shipping_rates_for_sorting.sort()

        
        # Build the shipping grid
        # I need to be able to sort the shipping rates based on the rate. 
        for j in range(len(shipping_rates_for_sorting)):

            for i in range(len(shipment.rates)):

                if shipping_rates_for_sorting[j]==float(shipment.rates[i].rate):

                    if shipment.rates[i].service==session.shipping_choice:

                        radio_button=INPUT(_type='radio', _name='shipping', _checked='checked', _value=shipment.rates[i].service)

                    else:

                        radio_button=INPUT(_type='radio', _name='shipping', _value=shipment.rates[i].service)

                    shipping_option_dict=dict(
                            carrier=shipment.rates[i].carrier,
                            service=camelcaseToUnderscore(shipment.rates[i].service),
                            rate=shipment.rates[i].rate,
                            rate_id=shipment.rates[i].id,
                            shipment_id=shipment.rates[i].shipment_id,
                            delivery_days=shipment.rates[i].delivery_days,
                        )

                    shipping_options_LOD.append(shipping_option_dict)

        error_status=False
        error_message=None
        return json.dumps(dict(error_status=error_status, error_message=error_message, shipping_options_LOD=shipping_options_LOD))

    except easypost.Error:
        error_status=True
        error_message='There was a problem generating the shipping costs for '+str(default_address_id)
        return json.dumps(dict(error_status=error_status, error_message=error_message, shipping_options_LOD=[]))

    except AttributeError:
        error_status=True
        error_message='There is nothing in your cart to ship'
        return json.dumps(dict(error_status=error_status, error_message=error_message, shipping_options_LOD=[]))

    except TypeError:
        error_status=True
        error_message='There is no address to ship to'
        return json.dumps(dict(error_status=error_status, error_message=error_message, shipping_options_LOD=[]))




def default_card():
    if auth.is_logged_in():
        row=db(db.stripe_customers.muses_id==auth.user_id).select().first()
        row.update(stripe_next_card_id=request.vars.stripe_next_card_id)
        row.update_record()

    if request.vars.stripe_next_card_id=='paypal':
        session.payment_method='paypal'
    else:
        session.payment_method='stripe'

def one():
    ajax_test=FORM(INPUT(_name='nametest', _onkeyup="ajax('echo', ['nametest'], ':eval')"))
    return locals()

def echo():
    #return "jQuery(alert('msg')"
    return "jQuery('#target').html(%s);" % repr(request.vars.nametest)
    #return request.vars.name

def two():
    row = db(db.addresses==2)
    #row.update(default_address=True)
    #row.update_record()
    return locals()
            

def easypost_test():
    import easypost

    from_address=easypost.Address.create(
        company='threemusesglass',
        street1='308 Clearcreek Rd',
        city='Myrtle Beach',
        state='SC',
        zip='29572',
    )

    to_address_domestic=easypost.Address.create(
        name='James McGlynn',
        street1='363 Cranbury Rd',
        street2='Apt D09',
        city='East Brunswick',
        state='NJ',
        zip='08816',
    )

    to_address_international=easypost.Address.create(
        name='James McGlynn',
        street1='200 Broadway Av',
        city='West Beach',
        state='SA',
        zipcode='5024',
        country='AUSTRALIA'
    )

    parcel=easypost.Parcel.create(
        length=4,
        width=4,
        height=2,
        weight=4,
    )

    shipment_domestic=easypost.Shipment.create(
        to_address = to_address_domestic,
        from_address = from_address,
        parcel=parcel,
    )

    customs_item1=easypost.CustomsItem.create(
        description='eCig drip tip',
        quantity=1,
        value=40,
        weight=6,
        hs_tariff_number=700100,
        origin_country='US',
    )

    customs_info=easypost.CustomsInfo.create(

        customs_items=[customs_item1],
        contents_type='merchandise',
        #contents_explanation=None,
        restriction_type='none',
        #restriction_comments=None,
        customs_certify=True,
        customs_signer='James McGlynn',
        non_delivery_option='return',
        eel_pfc='NOEEI 30.37(a).',
    )

    shipment_international=easypost.Shipment.create(

        to_address=to_address_international,
        from_address=from_address,
        parcel=parcel,
        customs_info=customs_info,

    )


    return locals()


def loading_data():
    if request.vars.waiting_for=='easypost':
        return "Generating shipping costs, please wait!"

    elif request.vars.waiting_for=='stripe':
        return "Retrieving card info!"

    else:
        return "I'm doing something right now, hold on!"






def table_generation(grid_header_list, grid_row_lists, basename):
    
    grid=DIV()

    grid['_class']=str(basename)+'_grid_container'

    if grid_header_list!=None:

        grid_header_row=DIV()

        grid_header_row['_class']=str(basename)+'_grid_header_row grid_header_row'

        for i in range(len(grid_header_list)):

            grid_header_row.append(DIV(DIV(grid_header_list[i]), _class=str(basename)+"_grid_header_cell grid_header_cell "+str(basename)+"_grid_col grid_col "+str(basename)+"_grid_col_"+str(i+1)))
        
        grid.append(grid_header_row)

    else:

        pass

    for grid_row_list in grid_row_lists:

        grid_table_row=DIV(_class=str(basename)+"_grid_table_row grid_table_row")

        for i in range(len(grid_row_list)):

            grid_table_row.append(DIV(grid_row_list[i],_class=str(basename)+"_grid_table_cell grid_table_cell "+str(basename)+"_grid_col grid_col "+str(basename)+"_grid_col_"+str(i+1)))

        grid.append(grid_table_row)

    return grid


def add_shipping_choice_to_session():
    import json

    session.shipping_choice=request.vars.shipping_choice

    shipping_dict=dict(
        shipping_choice=session.shipping_choice, 
    )
    
    shipping_json=json.dumps(shipping_dict, default=lambda x: None)

    return shipping_json


def stripe_remove_session_users():
    
    ## set cursor_id to get through the while loop the first time
    cursor_id=""

    ## set has_more to True to enter the while loop initially
    has_more=True

    ## While there are no more pages of users to go through
    while has_more==True:

        ## If this is the first time calling for customers...
        if cursor_id=="":
            ## Get the first 10 stripe customers (make the call with no args)
            stripe_customer_list=stripe.Customer.all()
        ## If this is not the first time
        else:
            ## make the call by setting starting_after to the id of the customer ending the previous call.
            stripe_customer_list=stripe.Customer.all(starting_after=cursor_id)

        ## Get the data portion of the dictionary returned.
        stripe_customer_list_data=stripe_customer_list['data']

        ## Get the id of the final customer in the list for next iteration.
        cursor_id=stripe_customer_list_data[-1]['id']

        ## Check to see if the email of the customer is in the threemuses user list. 
        ## (I should be using stripe id not email for this)
        for stripe_customer in stripe_customer_list_data:
            three_muses_user=db(db.stripe_customers.stripe_id==stripe_customer['id']).select().first()
            if not three_muses_user:

                hours_since_creation=(time.time()-stripe_customer['created'])/3600

                if hours_since_creation>=STRIPE_SESSION_RETIRE_HOURS:

                    scu=stripe.Customer.retrieve(stripe_customer['id'])
                    dummy=scu.delete()

                else:
                    pass
            else:
                pass


        ## This will be false if no more customers to retrieve. True if there are. 
        has_more=stripe_customer_list['has_more']

    return dict(message="Done!")

@auth.requires_login()
def view_purchase_history():
    query=(db.purchase_history_data.muses_id==auth.user_id)

    db.purchase_history_data.id.readable=db.purchase_history_data.id.writable=False
    db.purchase_history_data.muses_name.readable=db.purchase_history_data.muses_name.writable=False
    db.purchase_history_data.muses_id.readable=db.purchase_history_data.muses_id.writable=False
    db.purchase_history_data.muses_email_address.readable=db.purchase_history_data.muses_email_address.writable=False
    db.purchase_history_data.session_id_3muses.readable=db.purchase_history_data.session_id_3muses.writable=False
    db.purchase_history_data.session_db_table.readable=db.purchase_history_data.session_db_table.writable=False
    db.purchase_history_data.session_db_record_id.readable=db.purchase_history_data.session_db_record_id.writable=False
    db.purchase_history_data.easypost_rate_id.readable=db.purchase_history_data.easypost_rate_id.writable=False
    db.purchase_history_data.easypost_shipment_id.readable=db.purchase_history_data.easypost_shipment_id.writable=False
    db.purchase_history_data.payment_method.readable=db.purchase_history_data.payment_method.writable=False
    db.purchase_history_data.payment_stripe_user_id.readable=db.purchase_history_data.payment_stripe_user_id.writable=False
    db.purchase_history_data.payment_stripe_card_id.readable=db.purchase_history_data.payment_stripe_card_id.writable=False
    db.purchase_history_data.payment_stripe_transaction_id.readable=db.purchase_history_data.payment_stripe_transaction_id.writable=False

    db.purchase_history_data.writable=False


    db.purchase_history_products.id.readable=db.purchase_history_products.id.writable=False
    db.purchase_history_products.purchase_history_data_id.readable=db.purchase_history_products.purchase_history_data_id.writable=False
    db.purchase_history_products.product_id.readable=db.purchase_history_products.product_id.writable=False
    db.purchase_history_products.category_name.readable=db.purchase_history_products.category_name.writable=False
    db.purchase_history_products.qty_in_stock.readable=db.purchase_history_products.qty_in_stock.writable=False
    db.purchase_history_products.is_active.readable=db.purchase_history_products.is_active.writable=False
    db.purchase_history_products.display_order.readable=db.purchase_history_products.display_order.writable=False
    db.purchase_history_products.shipping_description.readable=db.purchase_history_products.shipping_description.writable=False


    grid=SQLFORM.smartgrid(db.purchase_history_data, 
        constraints=dict(purchase_history_data=query),
        linked_tables=['purchase_history_products'],
        searchable=False,
        deletable=False,
        create=False,
        editable=False,
        exportclasses=dict(csv_with_hidden_cols=False,
                            tsv_with_hidden_cols=False,
                            html=False,
                            json=False,
                            tsv=False,
                            xml=False,
                            ),
        )



    return dict(grid=grid)


def receipt_test():

    email_icons=dict(
        products_icon_url="https://s3.amazonaws.com/threemusesglass/icons/ProductIcon.png",
        address_icon_url="https://s3.amazonaws.com/threemusesglass/icons/AddressIcon.png",
        shipping_icon_url="https://s3.amazonaws.com/threemusesglass/icons/ShippingIcon.png",
        payment_icon_url="https://s3.amazonaws.com/threemusesglass/icons/PaymentIcon.png",
        summary_icon_url="https://s3.amazonaws.com/threemusesglass/icons/SummaryIcon.png",
        )



    receipt_context=dict(
        email_icons=email_icons,
        )

    receipt_message_html = response.render('default/receipt.html', receipt_context)

    return receipt_message_html

    # purchase_history_dict=dict(

    #     muses_id="muses_id",
    #     muses_email_address="muses_email_address",
    #     muses_name="muses_name",

    #     ## Session Fields (These actually come from response not session)
    #     session_id_3muses="response.session_id_3muses",
    #     session_db_table="response.session_db_table",
    #     session_db_record_id="response.session_db_record_id",

    #     ## Shipping Fields
    #     shipping_street_address_line_1="session.purchase_history_address_info['street_address_line_1']",
    #     shipping_street_address_line_2="session.purchase_history_address_info['street_address_line_2']",
    #     shipping_municipality="session.purchase_history_address_info['municipality']",
    #     shipping_administrative_area=session.purchase_history_address_info['administrative_area'],
    #     shipping_postal_code=session.purchase_history_address_info['postal_code'],
    #     shipping_country=session.purchase_history_address_info['country'],

    #     ## Easypost Fields?
    #     easypost_shipping_service=session.purchase_history_shipping_info['service'],
    #     easypost_shipping_carrier=session.purchase_history_shipping_info['carrier'],
    #     easypost_shipment_id=None,#session.purchase_history_shipping_info['id'],
    #     easypost_rate_id=None,#session.purchase_history_shipping_info['shipment_id'],
    #     easypost_rate=session.purchase_history_shipping_info['rate'],


    #     ## Payment Fields
    #     payment_method='stripe',
    #     payment_stripe_name=None,#charge['name'],
    #     payment_stripe_user_id=charge['customer'],
    #     payment_stripe_last_4=charge['card']['last4'],
    #     payment_stripe_brand=charge['card']['brand'],
    #     payment_stripe_exp_month=charge['card']['exp_month'],
    #     payment_stripe_exp_year=charge['card']['exp_year'],
    #     payment_stripe_card_id=charge['card']['id'],
    #     payment_stripe_transaction_id=charge['id'],

    #     ## Cart Details
    #     cart_base_cost=session.purchase_history_summary_info['cart_cost_USD'],
    #     cart_shipping_cost=session.purchase_history_summary_info['shipping_cost_USD'],
    #     cart_total_cost=session.purchase_history_summary_info['total_cost_USD'],

    # )

    # context=dict(
    #     products_icon_url="https://s3.amazonaws.com/threemusesglass/icons/ProductIcon.png",
    #     address_icon_url="https://s3.amazonaws.com/threemusesglass/icons/AddressIcon.png",
    #     shipping_icon_url="https://s3.amazonaws.com/threemusesglass/icons/ShippingIcon.png",
    #     payment_icon_url="https://s3.amazonaws.com/threemusesglass/icons/PaymentIcon.png",
    #     summary_icon_url="https://s3.amazonaws.com/threemusesglass/icons/SummaryIcon.png",
    #     )

    # return context



# def dne():

#     if request.vars is None:
#         redirect(URL('index'))
#     else:
#         if request.vars['page'] == 'display':
#             error_message="This line of products doesn't exist, so I don't think I would link you here"
#         else:
#             error_message="There was an error in the URL, hopefully is doesn't happen again!"



#     return dict(error_message=error_message, error_url=request.vars['request_url'])



import string
import random
def id_generator(size=16, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))




def paypal_test_checkout():
    import paypalrestsdk
    from aux import get_env_var
    from aux import id_generator
    from aux import paypal_create_payment_dict


    PAYPAL_CLIENT_ID=get_env_var('paypal',PRODUCTION_STATUS,'PAYPAL_CLIENT_ID')
    PAYPAL_CLIENT_SECRET=get_env_var('paypal',PRODUCTION_STATUS,'PAYPAL_CLIENT_SECRET')


    paypalrestsdk.configure({
        "mode": PAYPAL_MODE, # sandbox or live
        "client_id": PAYPAL_CLIENT_ID,
        "client_secret": PAYPAL_CLIENT_SECRET })


    invoice_number=id_generator()

    items_LOD=[

    dict(
        quantity="1",
        name="eCig Drip Tip",
        price="20.00",
        currency="USD",
        description="Description of item",
        ),

    dict(
        quantity="1",
        name="eCig Drip Tip Black",
        price="20.00",
        currency="USD",
        description="Black eCig Drip Tip",
        ),

    ]

    payment_dict=paypal_create_payment_dict(
        intent='sale',
        payment_method='paypal', 
        redirect_urls=dict(
            return_url="https://threemusesglass.herokuapp.com/paypal_webhooks",
            cancel_url="https://threemusesglass.herokuapp.com"),
        cost_dict=dict(
            shipping_cost_USD=2.00, 
            cart_cost_USD=40, 
            total_cost_USD=42),
        transaction_description='Purchase from ThreeMusesGlass',
        invoice_number=invoice_number,
        items_paypal_list_of_dicts=items_LOD,)


    payment=paypalrestsdk.Payment(payment_dict)


    if payment.create():
        status="Created successfully"
        approval_url=payment['links'][1]['href']
        session.expect_paypal_webhook=True
        #session.payment_id=payment
    else:
        status=payment.error
        approval_url="payment not created, no url for you"

    return dict(status=status, approval_url=approval_url)



def paypal_webhooks():

    ## Get the keys! and configure to send stuff
    import paypalrestsdk
       
    PAYPAL_CLIENT_ID=get_env_var('paypal', PRODUCTION_STATUS,'PAYPAL_CLIENT_ID')
    PAYPAL_CLIENT_SECRET=get_env_var('paypal', PRODUCTION_STATUS,'PAYPAL_CLIENT_SECRET')

    paypalrestsdk.configure({
        "mode": PAYPAL_MODE, # sandbox or live
        "client_id": PAYPAL_CLIENT_ID,
        "client_secret": PAYPAL_CLIENT_SECRET })


    ## Make sure this person recently started the purchase process
    if session.expect_paypal_webhook:

    # session.paypal_vars=request.vars

        payer_id=request.vars['PayerID']
        payment_id=request.vars['paymentId']
        
        ## Use the paymentId (with a capital I :/) to retrieve payment object
        payment=paypalrestsdk.Payment.find(payment_id)

        ## Try to execute the payment with the payer_id
        if payment.execute({"payer_id":payer_id}):

            status="success"
            session.expect_paypal_webhook=False

        else:

            status=payment.error
            session.expect_paypal_webhook=False

        return dict(status=status,payer_id=payer_id,payment_id=payment_id, payment=payment)

    else:

        return dict(
            status="n/a",
            payer_id=None, 
            payment_id=None,
            payment=None,)


def paypal_confirmation():

    ## Get the keys! and set configuration
    import paypalrestsdk
    import json
       
    PAYPAL_CLIENT_ID=get_env_var('paypal', PRODUCTION_STATUS,'PAYPAL_CLIENT_ID')
    PAYPAL_CLIENT_SECRET=get_env_var('paypal', PRODUCTION_STATUS,'PAYPAL_CLIENT_SECRET')

    paypalrestsdk.configure({
        "mode": PAYPAL_MODE, # sandbox or live
        "client_id": PAYPAL_CLIENT_ID,
        "client_secret": PAYPAL_CLIENT_SECRET })


    skip=False
    ## Make sure this person recently started the purchase process
    if session.expect_paypal_webhook or skip:
    #if True:
    # session.paypal_vars=request.vars

        payer_id=request.vars['PayerID']
        payment_id=request.vars['paymentId']
        
        ## Use the paymentId to retrieve payment object
        payment=paypalrestsdk.Payment.find(payment_id)
        

        ## Try to execute the payment with the payer_id
        if payment.execute({"payer_id":payer_id}) or skip:
        #if True:
            status="success"
            session.expect_paypal_webhook=False


            ## Get user information
            if auth.is_logged_in():

                user_data=db(db.auth_user.id==auth.user_id).select().first()

                muses_id=user_data.id
                muses_email_address=user_data.email
                muses_name=user_data.first_name
                
            else:
                ## If anonymous user,
                muses_id=None
                muses_name=None
                muses_email_address=payment['payer']['payer_info']['email']



            ## Populating the purchase history dict
            ## This is used in the next view to show the user the purchase details. 
            purchase_history_dict=dict(

                muses_id=muses_id,
                muses_email_address=muses_email_address,
                muses_name=muses_name,

                ## Session Fields (These actually come from response not session)
                session_id_3muses=response.session_id_3muses,
                session_db_table=response.session_db_table,
                session_db_record_id=response.session_db_record_id,

                ## Shipping Fields
                shipping_street_address_line_1=session.purchase_history_address_info['street_address_line_1'],
                shipping_street_address_line_2=session.purchase_history_address_info['street_address_line_2'],
                shipping_municipality=session.purchase_history_address_info['municipality'],
                shipping_administrative_area=session.purchase_history_address_info['administrative_area'],
                shipping_postal_code=session.purchase_history_address_info['postal_code'],
                shipping_country=session.purchase_history_address_info['country'],

                ## Easypost Fields?
                easypost_shipping_service=session.purchase_history_shipping_info['service'],
                easypost_shipping_carrier=session.purchase_history_shipping_info['carrier'],
                easypost_shipment_id=None,#session.purchase_history_shipping_info['id'],
                easypost_rate_id=None,#session.purchase_history_shipping_info['shipment_id'],
                easypost_rate=session.purchase_history_shipping_info['rate'],
                easypost_api_response=session.shipping_json,


                payment_service='paypal',
                payment_confirmation_dictionary=json.dumps(payment.to_dict(), default=lambda x: None),

                ## Legacy Fields
                payment_method='paypal',
                payment_stripe_name=None,
                payment_stripe_user_id=None,
                payment_stripe_last_4=None,
                payment_stripe_brand=None,
                payment_stripe_exp_month=None,
                payment_stripe_exp_year=None,
                payment_stripe_card_id=None,
                payment_stripe_transaction_id=None,

                #payment_paypal_name=,
                #payment_paypal_id=,
                #payment_paypal_etc=,

                # payment_paypal_intent=payment['intent'],



                # payment_paypal_transaction_id=payment['id'],
                # payment_paypal_create_time=payment['create_time'],
                # payment_paypal_state=payment['state'],


                ## Cart Details
                cart_base_cost=session.purchase_history_summary_info['cart_cost_USD'],
                cart_shipping_cost=session.purchase_history_summary_info['shipping_cost_USD'],
                cart_total_cost=session.purchase_history_summary_info['total_cost_USD'],

            )

            ## place data in the database. 
            purchase_history_data_id=db.purchase_history_data.bulk_insert([purchase_history_dict])[0]

            ## Add id of most recent purchase to the session for viewing purposes.
            session.session_purchase_history_data_id=purchase_history_data_id


            ## For every item in the cart, insert a record with the id of the purchase history, the product id and the qty.
            purchase_history_products_LOD=[]

            ## If logged in, get the cart information from the database
            if auth.is_logged_in():

                cart=db(db.muses_cart.user_id==auth.user_id).select()

                
                ## For item in cart, add id from record above with product and qty and all info about the product,
                ## then deal with inventory by removing the item from the cart.
                for row in cart:
                    product_record=db(db.product.id==row.product_id).select().first()
                    current_qty=int(product_record.qty_in_stock)
                    qty_purchased=int(row.product_qty)
                    new_qty=current_qty-qty_purchased

                    ## Remove item from the cart
                    db(db.muses_cart.product_id==product_record.id).delete()


                    purchase_history_product_dict=dict(

                        purchase_history_data_id=purchase_history_data_id,
                        product_id=product_record.id,
                        product_qty=int(row.product_qty),

                        category_name=product_record.category_name,
                        product_name=product_record.product_name,
                        description=product_record.description,
                        cost_USD=product_record.cost_USD,
                        qty_in_stock=new_qty,
                        is_active=product_record.is_active,
                        display_order=product_record.display_order,
                        shipping_description=product_record.shipping_description,
                        weight_oz=product_record.weight_oz,

                    )

                    ## Generate a list of dicts to use bulk insert
                    purchase_history_products_LOD.append(purchase_history_product_dict)


                    ## If you lowered the qty to 0 or less, make qty 0 and deactivate item
                    if new_qty<=0:

                        product_record.update(qty_in_stock=0)
                        product_record.update_record()
                        product_record.update(is_active=False)
                        product_record.update_record()

                    ## If not, just lower the qty
                    else:
                        product_record.update(qty_in_stock=new_qty)
                        product_record.update_record()

            ## If the user is not logged in, get the cart information from session. 
            else:


                for product_id, qty in session.cart.iteritems():
                    product_record=db(db.product.id==product_id).select().first()
                    current_qty=int(product_record.qty_in_stock)
                    qty_purchased=int(qty)
                    new_qty=current_qty-qty_purchased


                    purchase_history_product_dict=dict(

                        purchase_history_data_id=purchase_history_data_id,
                        product_id=product_record.id,
                        product_qty=qty_purchased,

                        category_name=product_record.category_name,
                        product_name=product_record.product_name,
                        description=product_record.description,
                        cost_USD=product_record.cost_USD,
                        qty_in_stock=new_qty,
                        is_active=product_record.is_active,
                        display_order=product_record.display_order,
                        shipping_description=product_record.shipping_description,
                        weight_oz=product_record.weight_oz,

                    )

                    ## Generate a list of dicts to use bulk insert
                    purchase_history_products_LOD.append(purchase_history_product_dict)


                    if new_qty<=0:
                        product_record.update(qty_in_stock=0)
                        product_record.update_record()
                        product_record.update(is_active=False)
                        product_record.update_record()
                    else:
                        product_record.update(qty_in_stock=new_qty)
                        product_record.update_record()

                session.cart=None



            purchase_history_products_ids=db.purchase_history_products.bulk_insert(purchase_history_products_LOD)


        ##   try:
            #Try to convert and compare the url arg with the session arg that the user is allowed to view. 
            if True: #int(purchase_history_data_id)==int(session.session_purchase_history_data_id):

                ## if success, then get the corresponding db info
                purchase_history_data_row=db(db.purchase_history_data.id==purchase_history_data_id).select().first()

                purchase_history_products_rows=db(db.purchase_history_products.purchase_history_data_id==purchase_history_data_id).select()

                ## product table
                product_header_row=['Product','Total Weight (oz)','Total Cost($)']
                product_table_row_LOL=[]
                product_total_weight=0
                product_total_cost=0

                ## change this so that you don't have to go into the product database to get this data
                ## It should all be available in the other purchase history tables. 
                ## I'm doing this because the product table has all editable stuff
                ## And I want a more permanent record of the transaction. 
                for row in purchase_history_products_rows:
                    #product_data=db(db.product.id==row.product_id).select().first()

                    line_item_weight_oz=int(row.product_qty)*int(row.weight_oz)
                    line_item_cost_usd=int(row.product_qty)*int(row.cost_USD)

                    product_table_row=[
                        row.product_name,
                        line_item_weight_oz,
                        line_item_cost_usd,
                    ]

                    product_total_weight+=line_item_weight_oz
                    product_total_cost+=line_item_cost_usd

                    product_table_row_LOL.append(product_table_row)

                product_totals_row=['Total',product_total_weight,product_total_cost,]

                product_table_row_LOL.append(product_totals_row)

                confirmation_product_grid=table_generation(product_header_row,product_table_row_LOL,'confirmation_product')


                ##Shipping Address Table
                address_header_row=['Street Address Info', 'Local Address Info', 'Country']
                address_table_row_LOL=[[
                    purchase_history_data_row.shipping_street_address_line_1+" "+purchase_history_data_row.shipping_street_address_line_2,
                    purchase_history_data_row.shipping_municipality+", "+purchase_history_data_row.shipping_administrative_area+" "+purchase_history_data_row.shipping_postal_code,
                    purchase_history_data_row.shipping_country,
                ]]

                confirmation_address_grid=table_generation(address_header_row,address_table_row_LOL,"confirmation_address")


                ##Shipping Info Table
                shipping_header_row=['Carrier-Rate', 'Shipping Weight (Oz)', 'Estimated Shipping Cost ($)']
                shipping_table_row_LOL=[[
                    purchase_history_data_row.easypost_shipping_carrier + " - " + purchase_history_data_row.easypost_shipping_service,
                    product_total_weight,
                    purchase_history_data_row.easypost_rate,
                ]]

                confirmation_shipping_grid=table_generation(shipping_header_row,shipping_table_row_LOL,"confirmation_shipping")


                ##Card Table
                card_header_row=['Paypal Name', 'Paypal Email', 'Paypal Invoice Number']
                card_table_row_LOL=[[
                    payment['payer']['payer_info']['first_name']+payment['payer']['payer_info']['last_name'],
                    payment['payer']['payer_info']['email'],
                    'invoice_number',
                ]]

                confirmation_card_grid=table_generation(card_header_row,card_table_row_LOL,"confirmation_card")


                ##Summary Table

                summary_header_row=['Shipping Cost ($)', 'Product Cost ($)', 'Total Cost ($)']
                summary_table_row_LOL=[[
                    purchase_history_data_row.easypost_rate,
                    product_total_cost,
                    float(purchase_history_data_row.easypost_rate)+product_total_cost,
                ]]

                confirmation_summary_grid=table_generation(summary_header_row,summary_table_row_LOL,"confirmation_summary")

                final_div=DIV(_class="muses_pay")
                final_div.append(DIV("Product Details",_class="confirmation_heading"))
                final_div.append(confirmation_product_grid)
                final_div.append(DIV("Address Details",_class="confirmation_heading"))
                final_div.append(confirmation_address_grid)
                final_div.append(DIV("Shipping Details",_class="confirmation_heading"))
                final_div.append(confirmation_shipping_grid)
                final_div.append(DIV("Payment Details",_class="confirmation_heading"))
                final_div.append(confirmation_card_grid)
                final_div.append(DIV("Summary",_class="confirmation_heading"))
                final_div.append(confirmation_summary_grid)
                

            final_div_html=final_div.xml()


            email_icons=dict(
                products_icon_url="https://s3.amazonaws.com/threemusesglass/icons/ProductIcon.png",
                address_icon_url="https://s3.amazonaws.com/threemusesglass/icons/AddressIcon.png",
                shipping_icon_url="https://s3.amazonaws.com/threemusesglass/icons/ShippingIcon.png",
                payment_icon_url="https://s3.amazonaws.com/threemusesglass/icons/PaymentIcon.png",
                summary_icon_url="https://s3.amazonaws.com/threemusesglass/icons/SummaryIcon.png",
                )

            #purchase_history_dict
            #purchase_history_products_LOD

            ## Try to overwrite the date with a string and convert back later using dateutil if necessary

            receipt_context=dict(
                email_icons=email_icons,
                #purchase_details=purchase_history_dict,
                #product_details=purchase_history_products_LOD,
                product_info=product_table_row_LOL,
                address_info=address_table_row_LOL,
                shipping_info=shipping_table_row_LOL,
                card_info=card_table_row_LOL,
                summary_info=summary_table_row_LOL,
                )

            #receipt_message_html = response.render('receipt.html', receipt_context)
            receipt_message_html = response.render('default/receipt.html', receipt_context)


            from postmark import PMMail
            message = PMMail(api_key=POSTMARK_API_KEY,
                subject="Order Confirmation",
                sender="confirmation@threemuses.glass",
                to=muses_email_address,
                #html_body=final_div_html,
                html_body=receipt_message_html,
                tag="confirmation")

            ## try:
            message.send()

            ## except postmark.core.PMMailUnprocessableEntityException:
            ## tell the user that the email I tried to send the receipt to failed
            ## and that they need to choose a different one if they want a reciept!


            ## This has to be last, duh.
            redirect(URL('confirmation', args=(purchase_history_data_id)))



        ## If the payment failed
        else:

            status=payment.error
            session.expect_paypal_webhook=False

        return dict(status=status,payer_id=payer_id,payment_id=payment_id, payment=payment)

    else:

        return dict(
            status="n/a",
            payer_id=None, 
            payment_id=None,
            payment=None,)


def get_current_default_address_id():
    if not session.default_address_id:
        session.default_address_id=10
    else:
        return session.default_address_id


## A Change


def update_default_address():

    session.default_address_id=request.vars['default_address_id']

    if auth.is_logged_in:

        address_row=db(db.addresses.id==request.vars['default_address_id']).select()[0]
        address_row.update(default_address=True)

    else:
        pass

    return "dummy"


def add_to_cart():
    return "dummy"

def scratch():
    
    return dict()

def scratch_ajax():

    import json
    new_choice=request.vars['new_choice']
    if session.current_choice:

        ## If the new choice is the same as the current choice, mark down that there was no change
        if session.current_choice==request.vars['new_choice']:
            return json.dumps(dict(current_choice=session.current_choice,previous_choice=session.previous_choice,change=False))
        
        ## Otherwise, set old choice to current choice and current choice to new choice. 
        else:
            session.previous_choice=session.current_choice
            session.current_choice=request.vars['new_choice']
            return json.dumps(dict(current_choice=session.current_choice,previous_choice=session.previous_choice,change=True))

    ## If there was no current choice, then just make current choice new choice and previous choice None
    else:
        session.current_choice=request.vars['new_choice']
        session.previous_choice=None
        return json.dumps(dict(current_choice=session.current_choice,previous_choice=session.previous_choice,change=True))



def get_session_var():
    key=request.vars['session_var']
    return session[key]


def create_gimp_user():
    from aux import id_generator
    from time import time
    if auth.is_logged_in():
        return dict()
    else:
        temp_password=str(id_generator())+str(time())

        temp_email=str(time())+'@'+str(id_generator())+'.com'

        user_id=db.auth_user.insert(first_name="Session", last_name="User", email=temp_email, password=db.auth_user.password.requires[0](temp_password)[0])
        
        auth.add_membership('gimp',db.auth_user(user_id))

        auth.login_bare(temp_email,temp_password)
        
        return dict()


def bootstrap_nav():
    return dict()