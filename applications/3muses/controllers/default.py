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

auth.settings.expiration = 999999999


## Functions that should be moved to their own module
from aux import get_env_var
from aux import splitSymbol
from aux import camelcaseToUnderscore


import stripe

stripe_keys = {
    'secret_key': os.environ['STRIPE_SECRET'],
    'publishable_key': os.environ['STRIPE_PUBLISHABLE']
}

stripe.api_key = stripe_keys['secret_key']


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


## Auth settings that need functions that are defined in this file
#auth.settings.reset_password_onaccept = [reset_password_callback]



## Maybe this info should go in a db table?
## The mapping for postal service types to business days required







## The postal service types to exclude in offerings. 

## exploring request
# for item in request:
#     print "----------------------------"
#     print item
#     print request[item]
#     print "----------------------------"

if request.env.http_host[:9]!='localhost':
    request.requires_https()



## The static views (index, categories, display, product, meet the artist.)

def index():

    category_rows=db(db.categories.is_active==True).select(orderby=db.categories.display_order)

    return dict(category_rows=category_rows)



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

    from aux import retrieve_cart_contents

    category_name=request.args[0].replace("_"," ")

    category_id=int(db(db.categories.category_name==category_name).select().first()['id'])

    product_rows=db((db.product.category_name==category_id)&(db.product.is_active==True)).select(orderby=db.product.display_order)

    category_rows=db(db.categories.is_active==True).select(orderby=db.categories.display_order)

    muses_cart=retrieve_cart_contents(auth,db)

    # print "muses_cart"
    # print muses_cart
    active_items=[]
    for row in muses_cart:
        active_items.append(row.product_id)

    # print "product_rows"
    # print product_rows

    return dict(
        category_id=category_id,
        product_rows=product_rows,
        category_rows=category_rows,
        active_items=active_items,
        )



def product():

    from datetime import datetime

    product_id=request.args[0]

    product_row=db(db.product.id==product_id).select()

    cart_row=db((db.muses_cart.product_id==product_id)&(db.muses_cart.user_id==auth.user_id)).select()


    cart_form=FORM(

        INPUT(
            _type="hidden",
            _name="qty",
            _value=1,
            #_placeholder="Enter Quantity",
            #requires=IS_INT_IN_RANGE(1,2),
        ),BR(),

        INPUT(_type='submit', _class="btn btn-info product-view-btn", _value="Add/Remove"),
    )


    if len(cart_row)==1 and cart_row[0].is_active==True:

        cart_form[2]['_value']="Remove from Cart"
        in_cart_ribbon=True

    else:

        cart_form[2]['_value']="Add to Cart"
        in_cart_ribbon=False


    if cart_form.accepts(request, session):

        ## If the cart was full when you pressed the button, remove the item
        if len(cart_row)==1 and cart_row[0].is_active==True:

            #cart_row=db((db.muses_cart.product_id==product_row[j].id)&(db.muses_cart.user_id==auth.user_id)).select()
            
            #existing_cart_entry_id=db((db.muses_cart.product_id==product_id)&(db.muses_cart.user_id==auth.user_id)).select()[0].id

            #del db.muses_cart[existing_cart_entry_id]

            existing_cart_entry=db((db.muses_cart.product_id==product_id)&(db.muses_cart.user_id==auth.user_id)).select()[0]

            db.muses_cart[existing_cart_entry.id]=dict(is_active=False,time_removed=datetime.now())

            # existing_cart_entry.update(is_active=False)
            # existing_cart_entry.update(time_removed=datetime.now())
            # existing_cart_entry.update_record()
            

            cart_form[2]['_value']="Add to Cart"
            in_cart_ribbon=False

        ## If the cart was empty when you pressed the button
        else:

            ## If the form is accepted, you must be logged in to add item to cart, so make sure
            if auth.is_logged_in():
                pass
            else:
                create_gimp_user()

            try:
                existing_cart_entry=db((db.muses_cart.product_id==product_id)&(db.muses_cart.user_id==auth.user_id)).select()[0]
                db.muses_cart[existing_cart_entry.id]=dict(product_qty=cart_form.vars.qty, time_added=datetime.now(), is_active=True)

            except IndexError:

                db.muses_cart.insert(
                    user_id=auth.user_id,
                    product_id=product_id,
                    product_qty=cart_form.vars.qty,
                    time_added=datetime.now(),
                    is_active=True,
                )

            cart_form[2]['_value']="Remove from Cart"
            in_cart_ribbon=True


    category_rows=db(db.categories.is_active==True).select(orderby=db.categories.display_order)



    return dict(
        product_id=product_id,
        product_row=product_row,
        cart_form=cart_form,
        category_rows=category_rows,
        in_cart_ribbon=in_cart_ribbon,
        )


# =A('X', _href=URL('delete_item_from_cart', vars=dict(pri_key=cart_row[0].id, redirect_url=URL('product',args=product_row[j].id))), _class="button")

    ## pri_key is the primary key referencing the muses_cart db table, which holds records for 
    ## every user and every item that user has in their cart. This function can only delete a single item at a time
    if auth.is_logged_in():
        del db.muses_cart[request.vars['pri_key']]
    else:
        dummy=session.cart.pop(request.vars['pri_key'])

    redirect(request.vars['redirect_url'])


## Meet the artist is under construction
# def artist():
#     return dict()



## Functions for adding things to session or db. 

## This needs to be shortened. Two long right now
## Consider bringing some of this crap to the view

# @auth.requires_login()
# def add_new_card():

#     stripe_form=FORM(

#         DIV( LABEL( 'Email Address',),DIV(INPUT(_type='text',_name='email', _class='form-control', ),),),

#         DIV( LABEL( 'Name on the Card',),DIV(INPUT(_type='text', _name='name', _class='form-control', ),),),

#         DIV( LABEL( 'Card Number',),DIV(INPUT(_type='integer', _name='number', _class='form-control', ),),),

#         DIV( LABEL('Card CVC Number',),DIV(INPUT(_type='integer', _name='cvc', _class='form-control', ),),),

#         DIV( LABEL('Expiration Month',),DIV(INPUT(_type='integer', _name='exp_month', _class='form-control', ),),),

#         DIV( LABEL('Expiration Year (YYYY)',),DIV(INPUT(_type='integer', _name='exp_year', _class='form-control', requires=IS_INT_IN_RANGE(2014,3000),),),),

#         INPUT(_type='submit', _class="btn btn-info add-new-card-view-btn"),

#         _class='form-horizontal',

#         _role='form').process()


#     if stripe_form.accepted:
#         ## If there are no errors found in the form (which there shouldn't be because there are no
#         ## requirements yet), try to retrieve the customer token from the database
#         ## and create a new card. If the logged in user doesn't have a stripe customer token yet, 
#         ## it will be unable to find one and raise an index error. 

#         try:
#             ## If the user has already gone through this process, they already have some email associated with their account, so I can just proceed for now. 
#             stripe_customer_token=db(db.stripe_customers.muses_id==auth.user_id).select()[0].stripe_id

#             customer=stripe.Customer.retrieve(stripe_customer_token)

#             if customer==None:
#                 pass
#             else:
#                 default_card=customer.cards.create(
#                     card=dict(
#                         name=stripe_form.vars.name,
#                         number=stripe_form.vars.number,
#                         cvc=stripe_form.vars.cvc,
#                         exp_month=stripe_form.vars.exp_month,
#                         exp_year=stripe_form.vars.exp_year,     
#                     )
#                 )

#             session.payment_method=default_card.id


#         # if there is no stripe customer token for the current user, the there will be an index error
#         # this means that the user doesn't have a token in the database
#         except IndexError:
#             # if user doesn't have stripe association yet when trying to create card
#             # create customer and first card at the same time.
#             #if auth.is_logged_in():

#             try:

#                 print ("Hello, we made it to the part where the user doesn't have any cards")
#                 ## And if they are gimp, also means they have no email correspondence yet. 



#                 if auth.has_membership('gimp'):




#                     email_from_user=stripe_form.vars.email

#                     existing_user=db(db.auth_user.email==email_from_user).select().first()

#                     if not existing_user:

#                         user_data.update(email=email_from_user)
#                         user_data.update_record()


#                         emails=db(db.email_correspondence.user_id==auth.user_id).select(db.email_correspondence.email)

#                         if email_from_user in emails:
#                             pass
#                         else:
#                             db.email_correspondence.insert(user_id=auth.user_id,email=email_from_user, is_active=True)

#                     else:

#                         emails=db(db.email_correspondence.user_id==auth.user_id).select(db.email_correspondence.email)

#                         if email_from_user in emails:
#                             pass
#                         else:
#                             db.email_correspondence.insert(user_id=auth.user_id,email=email_from_user, is_active=True)



#                     # muses_email=stripe_form.vars.email

#                     # product_record=db(db.auth_user.id==auth.user_id).select().first()

#                     # print (product_record)

#                     # product_record.update(email=muses_email)
#                     # product_record.update_record()


#                 customer = stripe.Customer.create(
#                     email=email_from_user,
#                     card=dict(
#                         name=stripe_form.vars.name,
#                         number=stripe_form.vars.number,
#                         cvc=stripe_form.vars.cvc,
#                         exp_month=stripe_form.vars.exp_month,
#                         exp_year=stripe_form.vars.exp_year,     
#                     )
#                 )

#                 # print customer

#                 session.payment_method=customer.default_source

#                 # add the fact the current customer is now a stripe customer to the db. 
#                 db.stripe_customers.insert(
#                     muses_id=auth.user_id,
#                     stripe_id=customer.id,
#                     ## might want to add some logic here to get a better email address when using a gimp user!
#                     stripeEmail=email_from_user,
#                     stripe_next_card_id=customer.default_source
#                 )

#             ## if there was a problem connecting to the stripe api
#             except stripe.error.APIConnectionError:
#                 customer=None

#         redirect(URL('checkout'))

#     else:
        
#         return dict(stripe_form=stripe_form)


@auth.requires_login()
def add_new_address_2(): #http://codepen.io/Angelfire/pen/dJhyr

    # db.addresses.country.requires = IS_IN_DB(db(db.country_codes.is_active==True), 'country_codes.country_name', '%(country_ISO_2)s')

    countries=db(db.country_codes.is_active==True).select()
    print countries

    from datetime import datetime

    add_address_form=FORM(

        DIV ( LABEL ( 'First Name', ) , DIV ( INPUT ( _type='text' , _name='first_name' , _class='form-control' , ) , ) , ) ,

        DIV ( LABEL ( 'Last Name', ), DIV ( INPUT ( _type='text', _name='last_name' , _class='form-control' , ) , ) , ),

        DIV ( LABEL( 'Street Address/ PO Box/ Etc.',),DIV(INPUT(_type='text', _name='street_address_line_1', _class='form-control', ),),),

        DIV ( LABEL ( 'Floor/ Suite/ Apt/ Etc.',),DIV(INPUT(_type='text', _name='street_address_line_2', _class='form-control', ),),),

        DIV ( LABEL ( 'Municipality',),DIV(INPUT(_type='text', _name='municipality', _class='form-control', ),),),

        DIV ( LABEL ( 'Administrative Area',),DIV(INPUT(_type='text', _name='administrative_area', _class='form-control', ),),),

        DIV ( LABEL ( 'Postal Code',),DIV(INPUT(_type='text', _name='postal_code', _class='form-control', ),),),

        DIV ( LABEL ( 'Country',),DIV(INPUT(_type='text', _name='country', _class='form-control', requires=IS_IN_DB(db(db.country_codes.is_active==True), 'country_codes.country_ISO_2', '%(country_name)s') ),),),

        INPUT(_type='submit', _class="btn btn-info form-submit-btn add-new-address-view-button"),
            
        _class='form-horizontal',

        _role='form')

    
    # add_address_form.element('input[name=Country]')['requires'] = IS_IN_DB(db(db.country_codes.is_active==True), 'country_codes.country_name', '%(country_ISO_2)s')

    if add_address_form.process().accepted:

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
            last_modified=datetime.now(),
        )

        redirect(URL('cart#address-information'))

    else:
        
        return dict(add_address_form=add_address_form)


@auth.requires_login()
def add_new_address():

    countries=db(db.country_codes.is_active==True).select()
    print countries

    from datetime import datetime

    add_address_form=SQLFORM(db.addresses)

    if add_address_form.process().accepted:

        redirect(URL('cart#address-information'))

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

    from aux import retrieve_cart_contents


#############################################################################################
###########--------------------------Initial Logic-------------------------------############
#############################################################################################

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
        # create_gimp_user()
        #response.flash=DIV("There are no items in your cart yet!",_class="flash_empty_cart")
        response.flash="There are no items in your cart yet!"
        session.flash=response.flash
        redirect(URL('categories'))





#############################################################################################
###########----------------------------Cart Logic--------------------------------############
#############################################################################################

    cart_information_LOD=[]
    cart_cost_USD=0
    cart_information=dict(error=False,error_message=None,cart_information_LOD=cart_information_LOD,cart_cost_USD=cart_cost_USD)

    ## Retrieve the current items from the users cart)
    ## There is no check here to not include items that are sold out or no
    ## longer active, That happens later.

    #cart_db=db(db.muses_cart.user_id==auth.user_id).select()

    cart_db=retrieve_cart_contents(auth,db)

    if len(cart_db)==0:
        response.flash="There are no items in your cart yet!"
        session.flash=response.flash
        redirect(URL('categories'))
    else:
        pass

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

            image=db(db.image.product_name==row.product_id).select().first()

            if not image:
                srcattr=URL('static','img/no_images.png')
            else:

                ## If using a local db get the product image locally
                if sqlite_tf:
                    # # image=db(db.image.product_name==row.product_id).select().first()
                    # if len(images)==0:
                    #     srcattr=URL('static','img/no_images.png')
                    # else:
                    srcattr=URL('download', image.s3_url)
                    # print ("sqlite")
                
                ## For the more common case, get the image from aws s3
                else:
                    # srcattr=S3_BUCKET_PREFIX+str(db(db.image.product_name==row.product_id).select().first().s3_url)
                    srcattr=S3_BUCKET_PREFIX+str(image.s3_url)

            ## Create the product_image_url
            product_image_url=A(IMG(_src=srcattr, _class='img-thumbnail cart-view-cart-tn'), _href=URL('default','product',args=[row.product_id]))

            ## Create a delete button for the item
            delete_button=A('X', _href=URL('delete_item_from_cart', vars=dict(pri_key=row.id,redirect_url=URL('cart'))), _class="btn btn-danger cart-view-item-remove cart-view-cart-item-remove")

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
            ## Acutally, I want to just deactivate the item and keep it in the cart. Fool. 
            if not product.is_active:
                db(db.muses_cart.product_id==product.id).delete()
            else:
                cart_cost_USD+=product.cost_USD
                # print cart_cost_USD

        cart_information['cart_cost_USD']=cart_cost_USD

        session.cart_cost_USD=cart_cost_USD



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
        shipping_information=dict(error=True, error_message="Please select an address to continue", shipping_options_LOD=[])


#############################################################################################
###########-------------------Card Logic (User and Non User)---------------------############
#############################################################################################


    card_information_LOD=[]

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

            delete_button=A('X', _href=URL('delete_item_from_db_card', vars=dict(customer_id=stripe_customer_token, card_id=stripe_cards['data'][i]['id'])), _class="btn btn-danger cart-view-payment-card-deletebutton")

            card_information_LOD.append(dict(
                card_radio=radio_button, 
                card_name=stripe_cards['data'][i]['name'], 
                card_last4=stripe_cards['data'][i]['last4'], 
                card_brand=stripe_cards['data'][i]['brand'], 
                card_exp_mo=stripe_cards['data'][i]['exp_month'], 
                card_exp_yr=stripe_cards['data'][i]['exp_year'], 
                cart_id=stripe_cards['data'][i]['id'], 
                card_delete=delete_button,
            ))

        card_information=dict(error=False, error_message=None, card_information_LOD=card_information_LOD)


    except IndexError:

        #the current user does not yet have a stripe customer token
        card_information=dict(error=True, error_message="You do not have any cards", card_information_LOD=[])

    except AttributeError:

        #the current user does not yet have a stripe customer token
        card_information=dict(error=True, error_message="You do not have any cards yet, or there was a problem accessing your cards.", card_information_LOD=[])

    except stripe.error.APIConnectionError, stripe.error.APIError:

        #No access to the internet, probably
        card_information=dict(error=True, error_message="There was a problem connecting to stripe", card_information_LOD=[])


#############################################################################################
###########--------------------------------Final---------------------------------############
#############################################################################################

    return dict(

        cart_information=cart_information,

        address_information=address_information,

        shipping_information=shipping_information,

        card_information=card_information,

        )




## The view right before they click to get charged and stuff. 

## In checkout is where I'm going to do most of the preparation for the purchase history
## db entry. My plan is to make a giant dictionary with all of the stuff, then pass
## it as a var or arg to pay. then try to charge the card,
## if it works, I'll have all the info I need, if not I can decide what to do about it. 
def checkout():

    from datetime import datetime
    from datetime import timedelta
## Currently checkout does, is logged in? then everything, then not logged in, and everything
## I figured out that I like the other method better. check for login on each thing you have to do.

#############################################################################################
###########-----------------------Cart Logic -----------------------############
#############################################################################################



    if auth.is_logged_in():
        pass
    else:
        # create_gimp_user()
        response.flash="There are no items in your cart yet!"
        session.flash=response.flash
        redirect(URL('categories'))


    # session.summary_data={}

    import json

    from aux import retrieve_cart_contents
    #from aux import camelcaseToUnderscore

    cart_for_shipping_calculations=[]

    cart_weight_oz=cart_cost_USD=0

    ## If the payment method is paypal, I need to create the payment link so that
    ## when the users presses pay they are sent to paypal. This is the beginning of that
    cart_for_paypal_LOD=[]


    cart_information_LOD=[]
    cart_information=dict(error=False,error_message=None,information_LOD=cart_information_LOD)

    ## Retrieve the current items from the users cart)
    ## There is no check here to not include items that are sold out or no
    ## longer active, That happens later.
    #cart_db=db(db.muses_cart.user_id==auth.user_id).select()

    cart_db=retrieve_cart_contents(auth,db)

    if len(cart_db)==0:
        response.flash="There are no items in your cart yet!"
        session.flash=response.flash
        redirect(URL('categories'))
    else:
        pass

    ## If cart turns out to be empty, set cart_grid so the view can have
    ## something to display. but now cart_grid_table_row_LOL will be empty,
    ## which should disallow the user from pressing the checkout button. 
    if not cart_db:

        cart_information['error']=True
        cart_information['error_message']="Please go back and add something to your cart"
        cart_is_empty=True

    ## If the cart is not empty
    else:
        
        cart_is_empty=False
        ## For each product in the cart
        for row in cart_db:

            ## Retreive product info from the db
            product=db(db.product.id==row.product_id).select().first()

            # ## If using a local db get the product image locally
            # if sqlite_tf:
            #     srcattr=URL('download',db(db.image.product_name==row.product_id).select().first().s3_url)
            
            # ## For the more common case, get the image from aws s3
            # else:
            #     srcattr=S3_BUCKET_PREFIX+str(db(db.image.product_name==row.product_id).select().first().s3_url)

            ## Retreive product info from the db

            image=db(db.image.product_name==row.product_id).select().first()

            if not image:
                srcattr=URL('static','img/no_images.png')
            else:

                ## If using a local db get the product image locally
                if sqlite_tf:
                    # # image=db(db.image.product_name==row.product_id).select().first()
                    # if len(images)==0:
                    #     srcattr=URL('static','img/no_images.png')
                    # else:
                    srcattr=URL('download', image.s3_url)
                    # print ("sqlite")
                
                ## For the more common case, get the image from aws s3
                else:
                    # srcattr=S3_BUCKET_PREFIX+str(db(db.image.product_name==row.product_id).select().first().s3_url)
                    srcattr=S3_BUCKET_PREFIX+str(image.s3_url)




            ## Create the product_image_url
            product_image_url=A(IMG(_src=srcattr, _class='img-thumbnail cart-view-cart-tn'), _href=URL('default','product',args=[row.product_id]))


            cart_for_shipping_calculations.append(
                dict(
                    product_name=product.product_name, 
                    product_cost=product.cost_USD,
                    product_qty=row.product_qty,
                    product_weight=product.weight_oz,
                    product_shipping_desc=product.shipping_description,
                    )
                )

            cart_for_paypal_LOD.append(
                dict(   
                    quantity=str(int(row.product_qty)),
                    name=product.product_name,
                    price='{:.2f}'.format(product.cost_USD),
                    currency='USD',
                    description=product.shipping_description,
                    )
                )

            cart_information_LOD.append(
                dict(
                        product_image_url=product_image_url,
                        product_name=product.product_name,
                        product_cost=product.cost_USD,
                        #product_delete_button=delete_button,
                        product_active=product.is_active,
                    )
                )

            cart_weight_oz+=float(product.weight_oz)*float(row.product_qty)
            cart_cost_USD+=float(product.cost_USD)*float(row.product_qty)
            
            ## This was from a time when you could buy more than one of something. 
            # row_cost_USD=float(product.cost_USD)*float(row.product_qty)

            ## If the item is no longer active, remove it from the cart.
            if not product.is_active:
                db(db.muses_cart.product_id==product.id).delete()


    # session.cart_cost_USD=cart_cost_USD

    # session.summary_data['cart_cost_USD']=cart_cost_USD


#############################################################################################
###########--------------------------Address Logic ------------------------------############
#############################################################################################


    ## Get the address that they have as their default address
    error=False
    error_message=None
    address_information_LOD=[]

    address=db((db.addresses.user_id==auth.user_id)&(db.addresses.default_address==True)).select().first()

    address_information_LOD.append(dict(
        first_name=address.first_name,
        last_name=address.last_name,
        street_address_line_1=address.street_address_line_1, 
        street_address_line_2=address.street_address_line_2, 
        municipality=address.municipality, 
        administrative_area=address.administrative_area, 
        postal_code=address.postal_code, 
        country=address.country,
    ))

    ## This is how the cart logic works
    error=False
    error_message=None
    address_information=dict( error=error, error_message=error_message, information_LOD=address_information_LOD )



#############################################################################################
##########----------------------------Shipping Logic ----------------------------############
#############################################################################################


    ## This needs to be merged with the following try block. Its iterating one thing and then looking 
    ## into this for the same information but formatted differently. 

    shipping_rates_checkout=session.shipping_rates[address.id]

    for item in shipping_rates_checkout:
        if item['rate_id']==address.easypost_default_shipping_rate_id:
            shipping_info_checkout=item


    print "shipping info checkout"
    print shipping_info_checkout


    try:
        shipment=easypost.Shipment.retrieve(address.easypost_shipping_id)

        shipping_option_id=address.easypost_default_shipping_rate_id

        shipping_cost_USD=0

        error=False
        error_message=None
        shipping_information_LOD=[]

        for rate in shipment['rates']:
            if rate['id']==shipping_option_id:

                #carrier=camelcaseToUnderscore(rate['carrier'])
                # carrier=shipping_info_checkout['carrier']
                #delivery_days=shipping_info_checkout['delivery_days']
                #delivery_date=(datetime.today()+timedelta(days=delivery_days)).strftime("%a %b %d")
                # delivery_date=shipping_info_checkout['delivery_date_text']

                # camelcaseToUnderscore(shipment.rates[i].service)

                shipping_information_LOD.append(dict(
                    carrier=shipping_info_checkout['carrier'],
                    service=rate['service'],
                    service_display=camelcaseToUnderscore(rate['service']),
                    cost=rate['rate'],
                    delivery_date=shipping_info_checkout['delivery_date_text'],
                    ))
                shipping_cost_USD=float(rate['rate'])
            else:
                pass

        if len(shipping_information_LOD)==0:
            error=True
            error_message="Please go back to the cart and select an address"

        shipping_information=dict(error=error, error_message=error_message, information_LOD=shipping_information_LOD)

    ## Try to retreive from session instead?
    except easypost.Error:
        shipping_information=dict(error=True, error_message="Unexpected error communicating with EasyPost", information_LOD=None)

    ## I should put some logic here to pick the cheaper or more expensive rate if somehow there is an issue where a single rateid is used on multple option in the api resonse. 
    # elif len(shipping_information)>1:
    #     error=True
    #     error_message="The "
    #     shipping_information=[]

    # session.summary_data['shipping_cost_USD']=shipping_cost_USD

    total_cost_USD=cart_cost_USD+shipping_cost_USD
    session.total_cost_USD=total_cost_USD

    # session.summary_data['total_cost_USD']=total_cost_USD

    #shipping_grid=[shipment,shipping_option_id]



#############################################################################################
###########-----------------Summary Logic (User and Non User)--------------------############
#############################################################################################

    error=False
    error_message=None
    summary_information_LOD=[]

    summary_information_LOD.append(dict(
        cart_cost_USD=cart_cost_USD,
        shipping_cost_USD=shipping_cost_USD,
        total_cost_USD=cart_cost_USD+shipping_cost_USD,
    ))

    summary_information=dict(error=error, error_message=error_message, information_LOD=summary_information_LOD)


#############################################################################################
###########---------------------------Payment Logic -----------------------------############
#############################################################################################

    import paypalrestsdk
    from aux import get_env_var
    from aux import id_generator
    from aux import paypal_create_payment_dict

    error=False
    error_message=None
    payment_information_LOD=[]


    invoice_number=id_generator()


    ## Should the invoice ID be generated here and put in session?
    ## I only have one right now for paypal because they require one. 


    # if session.payment_method[:4]=='card':

    #     ## This is the url attached to the pay button
    #     ## for paypal it will be more complicated. 
    #     approval_url=URL('pay')

    #     ## Retrieve the default card for the current customer by:
    #     ## Getting the stripe customer info from db with user_id
    #     stripe_customer_row=db(db.stripe_customers.muses_id==auth.user_id).select().first()

    #     # print stripe_customer_row

    #     ## From that get the customer id and default card id
    #     stripe_customer_token=stripe_customer_row.stripe_id
    #     stripe_customer_card=stripe_customer_row.stripe_next_card_id

    #     ## Use stripe API to retrieve customer and then to retrieve card from customer
    #     stripe_customer=stripe.Customer.retrieve(stripe_customer_token)
        
    #     stripe_card=stripe_customer.cards.retrieve(stripe_customer_card)


    #     payment_information_LOD.append(dict(
    #         payment_method='stripe',
    #         card_name=stripe_card['name'],
    #         card_last4=stripe_card['last4'], 
    #         card_brand=stripe_card['brand'], 
    #         card_exp_mo=stripe_card['exp_month'], 
    #         card_exp_year=stripe_card['exp_year'],
    #         approval_url=approval_url,
    #         ))

    #     payment_information=dict(error=error, error_message=error_message, information_LOD=payment_information_LOD)


    # ## If not paying with stripe, then assume they are paying with Paypal
    # ## For a logged in user and a non logged in user, the functionality
    # ## right now is identical
    # elif session.payment_method=='paypal':

    ## STRIPE INFO
    stripe_approval_url=URL('pay_stripe')


    ## PAYPAL INFO

    ## import all the helper stuff


    ## Get the paypal keys
    PAYPAL_CLIENT_ID=get_env_var('paypal',PRODUCTION_STATUS,'PAYPAL_CLIENT_ID')
    PAYPAL_CLIENT_SECRET=get_env_var('paypal',PRODUCTION_STATUS,'PAYPAL_CLIENT_SECRET')

    ## configure paypal api with keys
    paypalrestsdk.configure({
        "mode": PAYPAL_MODE, # sandbox or live
        "client_id": PAYPAL_CLIENT_ID,
        "client_secret": PAYPAL_CLIENT_SECRET })



    ## This will usually fail because of a namespace conflict
    ## I"m just keeping it here so I can tweak the web experience 
    ## everytime until I like it, then I will gray it out. 
    web_profile = paypalrestsdk.WebProfile({
        ## This has to be a unique name
        "name": "ThreeMusesGlass06",
        "presentation": {
            "brand_name": "ThreeMusesGlass",
            #Reactivae when you have an image to use. 
            # "logo_image": "http://s3-ec.buzzfed.com/static/2014-07/18/8/enhanced/webdr02/anigif_enhanced-buzz-21087-1405685585-12.gif",
            "locale_code": "US"
        },
        "input_fields": {
            "allow_note": True,
            "no_shipping": 1,
            "address_override": 1
        },
        "flow_config": {
            "landing_page_type": "Login",
        }
    })

    if web_profile.create():
        experience_profile_id=web_profile.id
        print "Profile was created" 
        print web_profile.id
    else:
        # experience_profile_id='XP-SLXS-5VPC-DL2F-VE9X'
        experience_profile_id='XP-2GPD-TN78-784C-A28C'

        print "There was an error creating the profile - see below."
        print web_profile.error


    ## cart_for_paypal_LOD is from the cart logic section
    payment_dict=paypal_create_payment_dict(
        intent='sale',
        payment_method='paypal', 
        experience_profile_id=experience_profile_id,
        redirect_urls=dict(
            return_url="https://threemusesglass.herokuapp.com/paypal_confirmation",
            cancel_url="https://threemusesglass.herokuapp.com/cart"),
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
        paypal_approval_url=payment['links'][1]['href']
        session.expect_paypal_webhook=True
        #session.payment_id=payment
    else:
        status=payment.error
        approval_url=status
        # print status


    payment_information_LOD.append(dict(

        stripe_approval_url=stripe_approval_url,
        paypal_approval_url=paypal_approval_url,
        invoice_number=invoice_number,

        ))

    payment_information=dict(error=error, error_message=error_message, information_LOD=payment_information_LOD)

       
    # ## If trying to use an unsupported payment method. 
    # else:

    #     error=True
    #     error_message="Go back and select a valid payment method"

    #     payment_information=dict(error=error, error_message=error_message, information_LOD=[dict(payment_method=None)])





#############################################################################################
###########---------------------Put Everything in Session------------------------############
#############################################################################################


    ## Adding all the info to the session for use in databasing purchase history inforation
    ## list of dicts
    # session.purchase_history_cart_info=cart_for_shipping_calculations

    session.cart_information=cart_information

    ## dictionary of address info
    #session.purchase_history_address_info=address_dict

    session.address_information=address_information

    ## dictionary of shipping_info
    #session.purchase_history_shipping_info=shipping_dict

    session.shipping_information=shipping_information

    ## Card info is transferred via the stripe interface right now. 
    #session.purchase_history_card_info=card_grid_row_list

    session.payment_information=payment_information

    ## dictionary of summary info
    session.summary_information=summary_information

    # print "cart_information"
    # print cart_information

    # print "address_information"
    # print address_information

    return dict(
        cart_information=cart_information,
        address_information=address_information,
        shipping_information=shipping_information,
        payment_information=payment_information,
        summary_information=summary_information,
        )



def stripe_custom():



    
    return dict()


def pay_stripe():

    ## This is used as the action to an html form. If it it does not either redirect or return a well formatted http response
    ## the user just sees "server error"

    ## So I'm wrapping the whole thing in a try block
    # try:
    if True:

        # /pay_stripe?stripeToken=tok_16GUlyBJewwJxtz76FQUa91R&stripeEmail=wantsomechocolate@gmail.com

        ### This function is for paying with stripe only

        ## The purpose of this function is to populate the database table purchase history with all 
        ## of the info about the purchase and send an email using postmark. 
        ## Presenting the confirmation screen is done later using the database
        import json
        from aux import create_purchase_history_dict
        from aux import generate_confirmation_email_receipt_context
        from aux import retrieve_cart_contents

        import stripe

        stripe_keys = {
            'secret_key': os.environ['STRIPE_SECRET'],
            'publishable_key': os.environ['STRIPE_PUBLISHABLE']
        }

        stripe.api_key = stripe_keys['secret_key']



        # try:

        ## Get customer_id from stripe data in db. They should have one, if they don't at this point
        ## something went wrong.

        ## Not True anymore
        # customer_id=db(db.stripe_customers.muses_id==auth.user_id).select().first().stripe_id

        ## From Session ##
        total_cost_USD=session.summary_information['information_LOD'][0]['total_cost_USD']


        ## To try and charge the card with the stripe id (defualt card should already be set within stripe)
        ## Otherwise something else went wrong
        ## TODO: Add description back in?
        ## TODO: What if the charge fails or the user cancels?

        # charge=stripe.Charge.create(
        #     amount=int(float(total_cost_USD)*100),
        #     currency='usd',
        #     customer=customer_id,
        #     #description='test purchase',
        # )

        # Get the credit card details submitted by the form


        # Create the charge on Stripe's servers - this will charge the user's card
        try:

            token = request.vars['stripeToken']

            print 'Token'
            print token

            stripe_email=request.vars['stripeEmail']

            print "Email:"
            print stripe_email

            
            print "BC - Before charge"

            ## Usual process
            # charge = stripe.Charge.create(
            #     amount=int(float(total_cost_USD)*100), # amount in cents, again
            #     currency="usd",
            #     source=token,
            #     description="Purchase from ThreeMusesGlass",
            #     )

            ## For debugging
            charge = stripe.Charge.retrieve('ch_16JNSKBJewwJxtz72EQeStZU')
            stripe_email='wantsomechocolate@gmail.com'

            # charge=json.loads("""{
            #       "amount": 4204, 
            #       "amount_refunded": 0, 
            #       "application_fee": null, 
            #       "balance_transaction": "txn_16GUrGBJewwJxtz7afwqINqy", 
            #       "captured": true, 
            #       "created": 1434979266, 
            #       "currency": "usd", 
            #       "customer": null, 
            #       "description": "Purchase from ThreeMusesGlass", 
            #       "destination": null, 
            #       "dispute": null, 
            #       "failure_code": null, 
            #       "failure_message": null, 
            #       "fraud_details": {}, 
            #       "id": "ch_16GUrGBJewwJxtz76RdXJp6b", 
            #       "invoice": null, 
            #       "livemode": false, 
            #       "metadata": {}, 
            #       "object": "charge", 
            #       "paid": true, 
            #       "receipt_email": null, 
            #       "receipt_number": null, 
            #       "refunded": false, 
            #       "refunds": {
            #         "data": [], 
            #         "has_more": false, 
            #         "object": "list", 
            #         "total_count": 0, 
            #         "url": "/v1/charges/ch_16GUrGBJewwJxtz76RdXJp6b/refunds"
            #       }, 
            #       "shipping": null, 
            #       "source": {
            #         "address_city": null, 
            #         "address_country": null, 
            #         "address_line1": null, 
            #         "address_line1_check": null, 
            #         "address_line2": null, 
            #         "address_state": null, 
            #         "address_zip": "10018", 
            #         "address_zip_check": "pass", 
            #         "brand": "Visa", 
            #         "country": "US", 
            #         "customer": null, 
            #         "cvc_check": null, 
            #         "dynamic_last4": null, 
            #         "exp_month": 12, 
            #         "exp_year": 2020, 
            #         "fingerprint": "kCCBgxubKDsM9l5g", 
            #         "funding": "credit", 
            #         "id": "card_16GUlyBJewwJxtz74A4RJ1yF", 
            #         "last4": "4242", 
            #         "metadata": {}, 
            #         "name": "wantsomechocolate@gmail.com", 
            #         "object": "card"
            #       }, 
            #       "statement_descriptor": null, 
            #       "status": "succeeded"
            #     }""")

    
            print 'charge'
            print charge
            print 'charge'
            print charge['id']


            ##################################################
            ################------USER INFO-------############
            ##################################################

            ## Get the information from the db about the user
            user_data=db(db.auth_user.id==auth.user_id).select().first()


        
            ##################################################
            ################-----ADDRESS AND------############
            ################----SHIPPING INFO-----############
            ##################################################
            default_address=db((db.addresses.user_id==auth.user_id)&(db.addresses.default_address==True)).select().first()



            shipping_rate_info=session.shipping_rates[default_address.id]
            for item in shipping_rate_info:
                if item['rate_id']==default_address.easypost_default_shipping_rate_id:
                    shipping_info=item


            # payment_data_uniform=dict(
            #     payment_email=stripe_email,

            #     )


            print "Creating the purchase history dict"

            purchase_history_dict=create_purchase_history_dict(
                ## This is probably really dangerous
                session_data=response,
                user_data=user_data,
                address_data=default_address,
                shipping_data=shipping_info,
                payment_service='stripe',
                payment_data=charge,
                payment_email=stripe_email,
                payment_invoice_number=session.payment_information['information_LOD'][0]['invoice_number'],
                payment_id=charge['id'],
                summary_data=session.summary_information,
                )


            print "Putting purchase history info in the db"

            #################################################
            ########----PUT PURCHASE INFO IN THE DB------####
            #################################################

            ## place data in the database. 
            purchase_history_data_id=db.purchase_history_data.bulk_insert([purchase_history_dict])[0]

            ## Add id of most recent purchase to the session for viewing purposes.
            session.session_purchase_history_data_id=purchase_history_data_id


            print "Preparing purchase history product info"

            #################################################
            ########----PUT PRODUCT INFO IN THE DB-------####
            #################################################

            ## For every item in the cart, insert a record with the id of the purchase history, the product id and the qty.
            purchase_history_products_LOD=[]

            cart=retrieve_cart_contents(auth,db)
            
            ## For item in cart, add id from record above with product and qty and all info about the product,
            ## then deal with inventory by removing the item from the cart.
            for row in cart:
                product_record=db(db.product.id==row.product_id).select().first()
                current_qty=int(product_record.qty_in_stock)
                qty_purchased=int(row.product_qty)
                new_qty=current_qty-qty_purchased

                ## Remove item from the cart
                db(db.muses_cart.product_id==product_record.id).delete()

                ## Prepare dict for bulk insert
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


            print "Putting purchase product info in the DB"
            ## Actually put everything in the db
            purchase_history_products_ids=db.purchase_history_products.bulk_insert(purchase_history_products_LOD)


            print "Generating receipt context"

            #################################################
            ########----SENDING THE CONFIRMATION EMAIL---####
            #################################################

            # receipt_context=generate_confirmation_email_receipt_context(
            #     muses_email_address=stripe_email, 
            #     purchase_history_data_row=db(db.purchase_history_data.id==purchase_history_data_id).select().first(),
            #     purchase_history_products_rows=db(db.purchase_history_products.purchase_history_data_id==purchase_history_data_id).select(),
            # )

            receipt_context=dict(
                purchase_history_data_row=db(db.purchase_history_data.id==purchase_history_data_id).select().first(),
                purchase_history_products_rows=db(db.purchase_history_products.purchase_history_data_id==purchase_history_data_id).select(),
                )

            receipt_message_html = response.render('default/receipt.html', receipt_context)



            # email_address_query=db(db.email_correspondence.user_id==auth.user_id).select(db.email_correspondence.email).first()
            # email_address=list(email_address_query.as_dict().values())[0]

            print "Sending the purchase email"

            print 'stripe email'
            print stripe_email

            from postmark import PMMail
            message = PMMail(api_key=POSTMARK_API_KEY,
                subject="Order Confirmation",
                sender="confirmation@threemuses.glass",
                # to=user_data.email,
                # to=email_address,
                to=stripe_email,
                #html_body=final_div_html,
                html_body=receipt_message_html,
                tag="confirmation")
            message.send()


            #################################################
            ########----SEND TO CONFIMATION SCREEN-------####
            #################################################
            redirect(URL('confirmation', args=(purchase_history_data_id)))



            ## Add catchers for these errors:

            ## KeyError

        except stripe.error.CardError, e:
            # The card has been declined
            ## redirect to checkout, eventually add in the fact that card was declined. 
          
            #ToDo: Add flash message to redirect
            redirect(URL('checkout'))

    # except Exception, error:
    #     print "An exception was thrown"
    #     print  str(error)
    #     #ToDo: Add flash message to redirect

    #     response.flash="Something Went Wrong - Contact Us"
    #     session.flash=response.flash

    #     redirect(URL('default','index'))

    # else:
    #     print "Everything looks great!"

    # finally:
    #     redirect(URL('confirmation', args=(purchase_history_data_id)))




def create_user_after_purchase_callback(form):
    ## This guys is the man
    ## https://groups.google.com/forum/#!topic/web2py/gka0Mg05I44

    from time import time
    from utils import web2py_uuid
    # print "We got called back!"

    print "create user callback called"

    user = db.auth_user(auth.user_id)  

    max_time=time()+3600

    reset_password_key = str(int(max_time)) + '-' + web2py_uuid()

    user.update_record(reset_password_key=reset_password_key)

    link = URL(reset_password,
                args=(reset_password_key),
                scheme=True)

    auth.messages.profile_updated = 'Please check your email to activate your account!'
    #auth.messages.reset_password_subject = 'Welcome!'

    print link
    print user.email

    mail.send(to=user.email,subject='Thanks for signing up!',
             message='Click this link to complete the signup process %s'%link)


def test_callback_no_args():
    from time import time
    from utils import web2py_uuid
    print "We got called back!"

    user = db.auth_user(auth.user_id)  

    max_time=time()+3600

    reset_password_key = str(int(max_time)) + '-' + web2py_uuid()

    user.update_record(reset_password_key=reset_password_key)

    link = URL(reset_password,
                args=(reset_password_key),
                scheme=True)

    print link

    mail.send(to='wantsomechocolate@gmail.com',subject='Thanks for signing up!',
             message='Click this link to complete the signup process %s'%link)  

    return dict()




def reset_password_callback(form):
    print "reset_password_got a callback!"

    if auth.has_membership(11,auth.user_id):
        auth.del_membership(11,auth.user_id)
        new_group_id=auth.add_group('user_%s'%str(auth.user_id), 'Group uniquely assigned to user %s'%str(auth.user_id))
        auth.add_membership(new_group_id,auth.user_id)

    else:
        print "this was a just a regular ol' user resetting their password"

    # auth.del_membership(group_id, user_id)
    # auth.add_membership(group_id, user_id)
    # auth.add_group('role', 'description')

def reset_password_callback_no_arg():
    print "reset_password got a callback!"

    if auth.has_membership(11,auth.user_id):
        auth.del_membership(11,auth.user_id)
        new_group_id=auth.add_group('user_%s'%str(auth.user_id), 'Group uniquely assigned to user %s'%str(auth.user_id))
        auth.add_membership(new_group_id,auth.user_id)

    else:
        print "this was a just a regular ol' user resetting their password"

    return dict()



def confirmation():

    import json
    import paypalrestsdk
    import stripe

    

    ## This function has a problem with deleting a user
    ## And then someone reusing the same email when they sign up
    ## FIX IT. 


    #What confirmation thing are you trying to view?


    # try:
    #     active_purchase_history_data_id=int(session.session_purchase_history_data_id)
    # except TypeError:
    #     active_purchase_history_data_id=-10

    #########################
    # try:
    ######################### 


    # print auth.user_id

    # user_id=auth.user_id

    # user=db(db.auth_user.id==auth.user_id).select().first()

    # print user.reset_password_key

    # print (db(db.auth_user.id==auth.user_id).select().first()).reset_password_key

    # reset_password_key=


    purchase_history_data_id=request.args[0]
    #Try to convert and compare the url arg with the session arg that the user is allowed to view. 
    if int(purchase_history_data_id)==int(session.session_purchase_history_data_id if session.session_purchase_history_data_id is not None else 0):

        ## if success, then get the corresponding db info
        purchase_history_data_row=db(db.purchase_history_data.id==purchase_history_data_id).select().first()

        # payment_information=json.loads(purchase_history_data_row.payment_confirmation_dictionary)

        if purchase_history_data_row['payment_service']=='stripe':

            payment_information_api=stripe.Charge.retrieve(purchase_history_data_row['payment_confirmation_id'])

        elif purchase_history_data_row['payment_service']=='paypal':

            payment_information_api=paypalrestsdk.Payment.find(purchase_history_data_row['payment_confirmation_id'])

        else:

            payment_information=api

        print payment_information_api

        purchase_history_products_rows=db(db.purchase_history_products.purchase_history_data_id==purchase_history_data_id).select()

        ## product table
        # product_header_row=['Product','Total Weight (oz)','Total Cost($)']
        # product_table_row_LOL=[]

        product_total_weight=0
        product_total_cost=0

        cart_information_LOD=[]
        cart_information=dict(error=False,error_message=None,information_LOD=cart_information_LOD)

        ## change this so that you don't have to go into the product database to get this data
        ## It should all be available in the other purchase history tables. 
        ## I'm doing this because the product table has all editable stuff
        ## And I want a more permanent record of the transaction. 
        for row in purchase_history_products_rows:
            #product_data=db(db.product.id==row.product_id).select().first()

            line_item_weight_oz=int(row.product_qty)*int(row.weight_oz)
            line_item_cost_usd=int(row.product_qty)*int(row.cost_USD)

            cart_information_LOD.append(
                dict(
                        # product_image_url=product_image_url,
                        product_name=row.product_name,
                        product_cost=row.cost_USD,
                        #product_delete_button=delete_button,
                        product_active=row.is_active,
                    ))

            # product_table_row=[
            #     row.product_name,
            #     line_item_weight_oz,
            #     line_item_cost_usd,
            # ]

            product_total_weight+=line_item_weight_oz
            product_total_cost+=line_item_cost_usd

            # product_table_row_LOL.append(product_table_row)

        # product_totals_row=['Total',product_total_weight,product_total_cost,]

        # product_table_row_LOL.append(product_totals_row)

        # confirmation_product_grid=table_generation(product_header_row,product_table_row_LOL,'confirmation_product')



        ##Shipping Address Table

#############################################################################################
###########-----------------------------Address Logic----------------------------############
#############################################################################################

        # error=False
        # error_message=None
        address_information_LOD=[]

        # address_header_row=['Street Address Info', 'Local Address Info', 'Country']

        address_information_LOD.append(dict(
            first_name=purchase_history_data_row.shipping_name_first,
            last_name=purchase_history_data_row.shipping_name_last,
            street_address_line_1=purchase_history_data_row.shipping_street_address_line_1, 
            street_address_line_2=purchase_history_data_row.shipping_street_address_line_2, 
            municipality=purchase_history_data_row.shipping_municipality, 
            administrative_area=purchase_history_data_row.shipping_administrative_area, 
            postal_code=purchase_history_data_row.shipping_postal_code, 
            country=purchase_history_data_row.shipping_country,
        ))

        address_information=dict( error=False, error_message=None, information_LOD=address_information_LOD )



        # address_table_row_LOL=[[
        #     purchase_history_data_row.shipping_street_address_line_1+" "+purchase_history_data_row.shipping_street_address_line_2,
        #     purchase_history_data_row.shipping_municipality+", "+purchase_history_data_row.shipping_administrative_area+" "+purchase_history_data_row.shipping_postal_code,
        #     purchase_history_data_row.shipping_country,
        # ]]

        # confirmation_address_grid=table_generation(address_header_row,address_table_row_LOL,"confirmation_address")



        ##Shipping Info Table

#############################################################################################
###########-----------------------------Shipping Logic---------------------------############
#############################################################################################

        shipping_information_LOD=[]

        # shipping_rates_confirmation=session.shipping_rates[address.id]

        # for item in shipping_rates_confirmation:
        #     if item['rate_id']==address.easypost_default_shipping_rate_id:
        #         shipping_info_confirmation=item



        shipping_information_LOD.append(dict(
            carrier=purchase_history_data_row.easypost_shipping_carrier,
            service=purchase_history_data_row.easypost_shipping_service,
            cost=purchase_history_data_row.easypost_rate,
            #IF you want this you have to add it :/
            delivery_date=purchase_history_data_row.easypost_delivery_date_text, #shipping_info_confirmation['delivery_date_text'],
        ))

        shipping_information=dict( error=False, error_message=None, information_LOD=shipping_information_LOD )


        # shipping_header_row=['Carrier-Rate', 'Shipping Weight (Oz)', 'Estimated Shipping Cost ($)']
        # shipping_table_row_LOL=[[
        #     purchase_history_data_row.easypost_shipping_carrier + " - " + purchase_history_data_row.easypost_shipping_service,
        #     product_total_weight,
        #     purchase_history_data_row.easypost_rate,
        # ]]

        # confirmation_shipping_grid=table_generation(shipping_header_row,shipping_table_row_LOL,"confirmation_shipping")



#############################################################################################
###########-----------------Summary Logic (User and Non User)--------------------############
#############################################################################################

        error=False
        error_message=None
        summary_information_LOD=[]

        summary_information_LOD.append(dict(
            cart_cost_USD=purchase_history_data_row.cart_base_cost,
            shipping_cost_USD=purchase_history_data_row.cart_shipping_cost,
            total_cost_USD=purchase_history_data_row.cart_total_cost,
        ))

        summary_information=dict(error=error, error_message=error_message, information_LOD=summary_information_LOD)


        # summary_header_row=['Shipping Cost ($)', 'Product Cost ($)', 'Total Cost ($)']
        # summary_table_row_LOL=[[
        #     purchase_history_data_row.easypost_rate,
        #     product_total_cost,
        #     float(purchase_history_data_row.easypost_rate)+product_total_cost,
        # ]]

        # confirmation_summary_grid=table_generation(summary_header_row,summary_table_row_LOL,"confirmation_summary")


#############################################################################################
###########---------------------------Payment Information====--------------------############
#############################################################################################

        error=False
        error_message=None
        payment_information_LOD=[]

        ##Card Table
        if purchase_history_data_row.payment_service=='stripe':

            if payment_information_api['source']['object']=='card':

                payment_information_LOD.append(
                    dict(
                        payment_service='stripe',
                        payment_object='card',
                        card_brand=payment_information_api['source']['brand'],
                        card_last4=payment_information_api['source']['last4'],
                        email=payment_information_api['source']['name'],
                        ))

                # payment_information=dict(error=False, error_message=None, information_LOD=payment_information_LOD)
            elif payment_information_api['source']['object']=='bitcoin_receiver':

                payment_information_LOD.append(
                    dict(
                        payment_service='stripe',
                        email=payment_information_api['source']['email'],
                        payment_object='Bitcoin',
                        ))

            else:
                payment_information_LOD.append(
                    dict(
                        payment_service='stripe',
                        email=payment_information_api['source']['email'],
                        payment_object='other',
                        ))




        elif purchase_history_data_row.payment_service=='paypal':

            payment_information_LOD.append(
                dict(
                    payment_service='paypal',
                    email=payment_information_api['payer']['payer_info']['email']
                    ))



        payment_information=dict(error=error, error_message=error_message, information_LOD=payment_information_LOD)


        # final_div=DIV()
        # final_div.append(DIV("Product Details",_class="confirmation_heading"))
        # final_div.append(confirmation_product_grid)
        # final_div.append(DIV("Address Details",_class="confirmation_heading"))
        # final_div.append(confirmation_address_grid)
        # final_div.append(DIV("Shipping Details",_class="confirmation_heading"))
        # final_div.append(confirmation_shipping_grid)
        # final_div.append(DIV("Payment Details",_class="confirmation_heading"))
        # final_div.append(confirmation_card_grid)
        # final_div.append(DIV("Summary",_class="confirmation_heading"))
        # final_div.append(confirmation_summary_grid)
        

        # email_address_query=db(db.email_correspondence.user_id==auth.user_id).select(db.email_correspondence.email).first()
        # email_address=list(email_address_query.as_dict().values())[0]


#############################################################################################
###########---------------------------Confirmation Information====--------------------############
#############################################################################################

        confirmation_information_LOD=[]

        if auth.has_membership('gimp'):
            email_address=payment_information['information_LOD'][0]['email']
        else:
            # email_address=auth_user.email

            email_address = (db.auth_user(auth.user_id)).email

        confirmation_information_LOD.append(dict(
            email_address=email_address,
            invoice_number=purchase_history_data_row.payment_invoice_number,
            ))

        confirmation_information=dict(error=False, error_message=None, information_LOD=confirmation_information_LOD)



        ##Create Account after purchase
        auth.settings.profile_onaccept = [create_user_after_purchase_callback]
        auth.messages.profile_updated = 'Check your email!'
        form_profile=auth.profile(next=URL('confirmation',args=(request.args[0])))
        form_profile.elements('input[type=submit]')[0]['_value']="Sign Up"
        

        return dict(
            confirmation_information=confirmation_information,

            cart_information=cart_information,
            address_information=address_information,
            shipping_information=shipping_information,
            payment_information=payment_information,
            summary_information=summary_information,

            form_profile=form_profile,
            # reset_password_key=reset_password_key,
        )

    ## if not, they are trying to view something they don't have access to.
    #redirect them!
    else:
        ## This is not the place for a user to be looking around past purchases. If it's not in session
        ## They can't see it here. 
        response.flash="You aren't allowed to view the confirmation with that ID"
        session.flash=response.flash
        redirect(URL('categories'))


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

    # except IndexError:
    #     return dict(
    #             purchase_history_data_row = "IndexError",
    #             purchase_history_products_rows = None,
    #         )







## Functions that require admin priveledges. These are so my mom can update products and stuff
## without bothering me. 

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
    return dict(grid=purchase_history_data_grid)

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

    return dict(grid=purchase_history_products_grid)



@auth.requires_membership('admin')
def manage_landing_page_images():
    landing_page_image_grid=SQLFORM.grid(db.landing_page_images,
        maxtextlength=100,
        )

    landing_page_image_grid.element('.web2py_counter', replace=None)
    return dict(grid=landing_page_image_grid)

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






@auth.requires_membership('admin')
def manage_products_new():
    ## Get all the products in a category
    
    # try:
    #     category_name=request.args[0]

    #     category_name=category_name.replace('_', ' ')

    #     category_id = db(db.categories.category_name==category_name).select().first().id

    #     products = db(db.product.category_name==category_id).select()

    # except IndexError:

    #     products = db(db.product.id>0).select()




    # product_images_LOD=[]

    # product_LOD=[]

    # for product in products:
    #     images = db(db.image.product_name==product.id).select()
    #     images_dict={
    #         product.product_name:images,
    #     }
    #     product_images_LOD.append(images_dict)

    #     product_dict=product.as_dict()

    #     img_urls=[]

    #     for image in images:
    #         img_urls.append(image.as_dict())

    #     product_dict['images']=img_urls

    #     product_LOD.append(product_dict)

    # return dict(product_LOD = product_LOD)

    return dict()


def ajax_manage_products_new():

    import json

    ## Get all the products in a category
    
    try:
        category_name=request.args[0]

        category_name=category_name.replace('_', ' ')

        category_id = db(db.categories.category_name==category_name).select().first().id

        products = db(db.product.category_name==category_id).select()

    except IndexError:

        products = db(db.product.id>0).select()

    except AttributeError:

        products = db(db.product.id>0).select()

        response.flash="There are no products associated with that category. Showing all products"
        # session.flash=response.flash


    product_images_LOD=[]

    product_LOD=[]

    for product in products:
        images = db(db.image.product_name==product.id).select()
        images_dict={
            product.product_name:images,
        }
        product_images_LOD.append(images_dict)

        product_dict=product.as_dict()

        category_id=product_dict['category_name']

        category_name=db(db.categories.id==category_id).select().first().category_name

        print category_name

        product_dict['category_name']=category_name

        image_data=[]

        for image in images:
            image_dict=image.as_dict()
            s3_url_info=image_dict['s3_url']


            if sqlite_tf:
                full_url=URL('download', s3_url_info)
            else:
                full_url='https://s3.amazonaws.com/threemusesglass/site_images/'+s3_url_info

            image_dict['s3_url']=full_url

            # image_delete_url=A('X',_href=URL('delete_product_image', args=[image_dict['id']])).xml()
            # image_dict['image_delete_url']=image_delete_url

            image_data.append(image_dict)

        #print image_data

        product_dict['images']=image_data

        product_LOD.append(product_dict)


    core_columns=db((db.core_columns.table_name=='manage_products_new')&(db.core_columns.core==True)).select(orderby=db.core_columns.column_order).as_list()


    for item in core_columns:
        item['data']=item['data_ref']


    collapse_expand=dict(
        className='details-control',
        orderable=False,
        data=None,
        defaultContent='',
        # width='50px',
        )


    columns_LOD=core_columns

    columns_LOD.insert(0,collapse_expand)

    print core_columns



    # core_columns=[

    #     dict(
    #         className='details-control',
    #         orderable=False,
    #         data=None,
    #         defaultContent='',
    #         width='50px',
    #         ),
        
    #     dict(
    #         table_name='Bracelets',
    #         core=True,

    #         data='product_name',
    #         defaultContent='',
    #         title='Product Name',

    #         width='200px',
    #         ),

    #     dict(
    #         table_name='Bracelets',
    #         core=True,

    #         data='description',
    #         defaultContent='',
    #         title='Description',
    #         width='400px',
    #         ),

    #     dict(
    #         table_name='Bracelets',
    #         core=True,

    #         data='cost_USD',
    #         defaultContent='',
    #         title='Cost ($)',
    #         ),

    #     dict(
    #         table_name='Bracelets',
    #         core=True,

    #         data='weight_oz',
    #         defaultContent='',
    #         title='Weight (oz)',
    #         ),

    #     dict(
    #         table_name='Bracelets',
    #         core=True,

    #         data='is_active',
    #         defaultContent='',
    #         title='Is Active',
    #         ),

    #     dict(
    #         table_name='Bracelets',
    #         core=True,

    #         data='shipping_description',
    #         defaultContent='',
    #         title='Shipping Description',
    #         ),

    #     dict(
    #         table_name='Bracelets',
    #         core=True,

    #         data='qty_in_stock',
    #         defaultContent='',
    #         title='Quantity in Stock',
    #         ),

    #     dict(
    #         table_name='Bracelets',
    #         core=True,

    #         data='id',
    #         defaultContent='',
    #         title='DB ID',
    #         ),

    #     dict(
    #         table_name='Bracelets',
    #         core=True,

    #         data='category_name',
    #         defaultContent='',
    #         title='Category Name',
    #         ),

    #     dict(
    #         table_name='Bracelets',
    #         core=True,

    #         data='display_order',
    #         defaultContent='',
    #         title='Display Order',
    #         ),

    #     ]


    json_data={
        'data':product_LOD,
        'columns':core_columns,
        }






    return json.dumps(json_data)








@auth.requires_membership('admin')
def remove_image_association_from_product():
    return dict()

@auth.requires_membership('admin')
def add_image_to_product():
    return dict()

@auth.requires_membership('admin')
def remove_image_association_from_product():
    return dict()

@auth.requires_membership('admin')
def remove_image_association_from_product():
    return dict()


















## pulled from a random place on the internet
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

    from datetime import datetime

    ## pri_key is the primary key referencing the muses_cart db table, which holds records for 
    ## every user and every item that user has in their cart. This function can only delete a single item at a time
    # if auth.is_logged_in():
    #     del db.muses_cart[request.vars['pri_key']]
    # else:
    #     dummy=session.cart.pop(request.vars['pri_key'])


    cart_row=db(db.muses_cart.id==request.vars['pri_key']).select()[0]
    # print cart_row

    cart_row.update(is_active=False,time_removed=datetime.now())
    cart_row.update_record()


    redirect(request.vars['redirect_url'])


def delete_address():
    if auth.is_logged_in():
        del db.addresses[request.vars['pri_key']]
    else:
        dummy=session.pop('address')
    redirect(request.vars['redirect_url'])



def delete_product_image():

    # try:
    image_id = request.args[0]

    db(db.image.id == image_id).delete()

    response.flash="Sucessfully Deleted"
    session.flash=response.flash
    redirect(URL('manage_products_new'))

        # return True

    # except:

        # response.flash="There was a problem"
        # session.flash=response.flash
        # redirect(URL('manage_products_new'))
        # return False


#def add_product_image():



def dropzone_sample():
    return dict()





def dropzone_upload():
    #print request.vars
    import io

    field_storage_object=request.vars['file']

    # print field_storage_object.name

    # print dir(field_storage_object)

    filename = field_storage_object.filename
    # filesize = field_storage_object.length


    # file_handle=gzip.GzipFile(fileobj=io.BytesIO(field_storage_object.value), mode='r')
    # file_handle=io.BytesIO(field_storage_object.value)

    # filesize = len(io.BytesIO(field_storage_object.value))


    # fh = field_storage_object.file

    filesize = request.vars['filesize']

    print filesize
    #category_id=1
    product_id=request.args[0]

    category_id = db(db.product.id == product_id ).select().first().category_name

    db_id=db.image.insert(
        category_name = category_id,
        product_name = product_id,
        title = filename,
        s3_url = field_storage_object,
        filesize = filesize,
        )

    return db_id


def dropzone_delete():
    db_id=request.vars.id
    db(db.image.id==str(db_id)).delete()
    print "haldskjf"
    return "SUCCESS"


def prepopulate_dropzone():
    import json

    product_id=request.args[0]

    product_images = db(db.image.product_name==product_id).select()

    #product_images_dict = product_images.as_dict()


    image_data=[]

    for image in product_images:
        image_dict=image.as_dict()
        s3_url_info=image_dict['s3_url']


        if sqlite_tf:
            full_url=URL('download', s3_url_info)
        else:
            full_url='https://s3.amazonaws.com/threemusesglass/site_images/'+str(s3_url_info)

        print full_url

        image_dict['s3_url']=full_url






        image_data.append(image_dict)



    return json.dumps(image_data)





# def delete_card():
#     if auth.is_logged_in():
#         ## This actually isn't deleting anything from the database. 
#         ## It collects the customer and card id passed to the function via request
#         ## and tells stripe to delete the card from the user.
#         customer = stripe.Customer.retrieve(request.vars['customer_id'])
#         customer.cards.retrieve(request.vars['card_id']).delete()

#         redirect(request.vars['redirect_url'])

#     else:
#         ## The add_new_card function adds the 'stripe_id' to the session.
#         ## Retrieve it here 
#         stripe_id=session.card_info['stripe_id']

#         ## To then retrieve that customer using stripe API and delete it
#         ## Need to add some code in here to handle when communication with Stripe is unavailable.
#         customer=stripe.Customer.retrieve(stripe_id)
#         customer.delete()

#     redirect(request.vars['redirect_url'])


# def delete_item_from_db_card():

#     ## This actually isn't deleting anything from the database. 
#     ## It collects the customer and card id passed to the function via request
#     ## and tells stripe to delete the card from the user.
#     customer = stripe.Customer.retrieve(request.vars['customer_id'])
#     customer.cards.retrieve(request.vars['card_id']).delete()

#     redirect(URL('checkout'))


# ## removes customer from stripe and current session
# def delete_item_from_session_card():

#     ## The add_new_card function adds the 'stripe_id' to the session.
#     ## Retrieve it here 
#     stripe_id=session.card_info['stripe_id']

#     ## To then retrieve that customer using stripe API and delete it
#     ## Need to add some code in here to handle when communication with Stripe is unavailable.
#     customer=stripe.Customer.retrieve(stripe_id)
#     customer.delete()

#     ## After deleting the customer from the stripe db remove the card info from the session.
#     dummy=session.pop('card_info')

#     redirect(URL('cart'))




## Functions to edit items in session

# def edit_session_address():

#     edit_address_form=FORM(

#         DIV( 
#             LABEL( 'First Name',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='first_name', 
#                     _class='form-control',
#                     _value=session.address['first_name'],
#                 ),
#             ),
#         ),

#         DIV( 
#             LABEL( 'Last Name',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='last_name', 
#                     _class='form-control',
#                     _value=session.address['last_name'],
#                 ),
#             ),
#         ),

#         DIV( 
#             LABEL( 'Street Address/ PO Box/ Etc.',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='street_address_line_1', 
#                     _class='form-control',
#                     _value=session.address['street_address_line_1'],
#                 ),
#             ),
#         ),

#         DIV( 
#             LABEL( 'Floor/ Suite/ Apt/ Etc.',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='street_address_line_2', 
#                     _class='form-control', 
#                     _value=session.address['street_address_line_2'],
#                 ),
#             ),
#         ),

#         DIV(
#             LABEL('Municipality',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='municipality', 
#                     _class='form-control', 
#                     _value=session.address['municipality'],
#                 ),
#             ),
#         ),

#         DIV(
#             LABEL('Administrative Area',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='administrative_area', 
#                     _class='form-control', 
#                     _value=session.address['administrative_area'],
#                 ),
#             ),
#         ),

#         DIV(
#             LABEL('Postal Code',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='postal_code', 
#                     _class='form-control', 
#                     _value=session.address['postal_code'],
#                 ),
#             ),
#         ),

#         DIV(
#             LABEL('Country',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='country', 
#                     _class='form-control', 
#                     _value=session.address['country'],
#                 ),
#             ),
#         ),
   
#         INPUT(_type='submit', _class="btn btn-default form-submit-btn"),
            
#     _class='form-horizontal',
#     _role='form').process()

#     if edit_address_form.accepted:

#         if auth.is_logged_in():
#             pass
#             # db.addresses.insert(
#             #     user_id=auth.user_id,
#             #     street_address_line_1=add_address_form.vars.street_address_line_1,
#             #     street_address_line_2=add_address_form.vars.street_address_line_2,
#             #     municipality=add_address_form.vars.municipality,
#             #     administrative_area=add_address_form.vars.administrative_area,
#             #     postal_code=add_address_form.vars.postal_code,
#             #     country=add_address_form.vars.country,
#             # )

#         else:
#             session.address=dict(
#                 first_name=edit_address_form.vars.first_name,
#                 last_name=edit_address_form.vars.last_name,
#                 street_address_line_1=edit_address_form.vars.street_address_line_1,
#                 street_address_line_2=edit_address_form.vars.street_address_line_2,
#                 municipality=edit_address_form.vars.municipality,
#                 administrative_area=edit_address_form.vars.administrative_area,
#                 postal_code=edit_address_form.vars.postal_code,
#                 country=edit_address_form.vars.country,
#             )

#         redirect(URL('cart'))

#     else:
        
#         return dict(edit_address_form=edit_address_form)


# #functions to edit things in db

# def edit_db_address():

#     #if auth.is_logged_in:

#     address_row=db(db.addresses.id==request.vars['pri_key']).select()[0]

#     edit_address_form=FORM(
#         DIV( 
#             LABEL( 'Street Address/ PO Box/ Etc.',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='street_address_line_1', 
#                     _class='form-control',
#                     _value=address_row['street_address_line_1'],
#                 ),
#             ),
#         ),

#         DIV( 
#             LABEL( 'Floor/ Suite/ Apt/ Etc.',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='street_address_line_2', 
#                     _class='form-control', 
#                     _value=address_row['street_address_line_2'],
#                 ),
#             ),
#         ),

#         DIV(
#             LABEL('Municipality',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='municipality', 
#                     _class='form-control', 
#                     _value=address_row['municipality'],
#                 ),
#             ),
#         ),

#         DIV(
#             LABEL('Administrative Area',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='administrative_area', 
#                     _class='form-control', 
#                     _value=address_row['administrative_area'],
#                 ),
#             ),
#         ),

#         DIV(
#             LABEL('Postal Code',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='postal_code', 
#                     _class='form-control', 
#                     _value=address_row['postal_code'],
#                 ),
#             ),
#         ),

#         DIV(
#             LABEL('Country',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='country', 
#                     _class='form-control', 
#                     _value=address_row['country'],
#                 ),
#             ),
#         ),
   
#         INPUT(_type='submit', _class="btn btn-default"),
            
#     _class='form-horizontal',
#     _role='form').process()

#     if edit_address_form.accepted:

#         if auth.is_logged_in():
#             db.addresses[request.vars['pri_key']]=dict(
#                 street_address_line_1=edit_address_form.vars.street_address_line_1,
#                 street_address_line_2=edit_address_form.vars.street_address_line_2,
#                 municipality=edit_address_form.vars.municipality,
#                 administrative_area=edit_address_form.vars.administrative_area,
#                 postal_code=edit_address_form.vars.postal_code,
#                 country=edit_address_form.vars.country,
#                 )
#             # db.addresses.insert(
#             #     user_id=auth.user_id,
#             #     street_address_line_1=add_address_form.vars.street_address_line_1,
#             #     street_address_line_2=add_address_form.vars.street_address_line_2,
#             #     municipality=add_address_form.vars.municipality,
#             #     administrative_area=add_address_form.vars.administrative_area,
#             #     postal_code=add_address_form.vars.postal_code,
#             #     country=add_address_form.vars.country,
#             # )

#         else:
#             pass

#         redirect(URL('cart'))

#     else:
        
#         return dict(edit_address_form=edit_address_form)



# @auth.requires_login()
# def edit_address_2():

#     from datetime import datetime

#     # if auth.is_logged_in():

#     allowable_address_ids=[]
#     allowable_addresses=db(db.addresses.user_id==auth.user_id).select(db.addresses.id)
#     for address_row in allowable_addresses:
#         allowable_address_ids.append(str(address_row.id))

#     # print allowable_address_ids

#     if request.vars['pri_key'] not in allowable_address_ids:

#         response.flash="You aren't allowed to edit the address with that id"
#         session.flash=response.flash
#         redirect(URL('cart'))


#     address_pre_changes_dict=db(db.addresses.id==request.vars['pri_key']).select()[0]
#     #address_row['street_address_line_1'],

#     # else:
#     #     address_pre_changes_dict=session.address
#         #session.address['first_name']

#     edit_address_form=FORM(

#         DIV( 
#             LABEL( 'First Name',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='first_name', 
#                     _class='form-control',
#                     _value=address_pre_changes_dict['first_name'],
#                 ),
#             ),
#         ),

#         DIV( 
#             LABEL( 'Last Name',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='last_name', 
#                     _class='form-control',
#                     _value=address_pre_changes_dict['last_name'],
#                 ),
#             ),
#         ),

#         DIV( 
#             LABEL( 'Street Address/ PO Box/ Etc.',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='street_address_line_1', 
#                     _class='form-control',
#                     _value=address_pre_changes_dict['street_address_line_1'],
#                 ),
#             ),
#         ),

#         DIV( 
#             LABEL( 'Floor/ Suite/ Apt/ Etc.',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='street_address_line_2', 
#                     _class='form-control', 
#                     _value=address_pre_changes_dict['street_address_line_2'],
#                 ),
#             ),
#         ),

#         DIV(
#             LABEL('Municipality',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='municipality', 
#                     _class='form-control', 
#                     _value=address_pre_changes_dict['municipality'],
#                 ),
#             ),
#         ),

#         DIV(
#             LABEL('Administrative Area',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='administrative_area', 
#                     _class='form-control', 
#                     _value=address_pre_changes_dict['administrative_area'],
#                 ),
#             ),
#         ),

#         DIV(
#             LABEL('Postal Code',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='postal_code', 
#                     _class='form-control', 
#                     _value=address_pre_changes_dict['postal_code'],
#                 ),
#             ),
#         ),

#         DIV(
#             LABEL('Country',),
            
#             DIV(
#                 INPUT(
#                     _type='text', 
#                     _name='country', 
#                     _class='form-control', 
#                     _value=address_pre_changes_dict['country'],
#                 ),
#             ),
#         ),
   
#         INPUT(_type='submit', _class="btn btn-info form-submit-btn"),
            
#     _class='form-horizontal',
#     _role='form').process()

#     if edit_address_form.accepted:

#         address_post_changes_dict=dict(
#                 first_name=edit_address_form.vars.first_name,
#                 last_name=edit_address_form.vars.last_name,
#                 street_address_line_1=edit_address_form.vars.street_address_line_1,
#                 street_address_line_2=edit_address_form.vars.street_address_line_2,
#                 municipality=edit_address_form.vars.municipality,
#                 administrative_area=edit_address_form.vars.administrative_area,
#                 postal_code=edit_address_form.vars.postal_code,
#                 country=edit_address_form.vars.country,
#                 default_address=True,
#                 last_modified=datetime.now()
#                 )

#         if auth.is_logged_in():
#             db.addresses[request.vars['pri_key']]=address_post_changes_dict

#         else:
#             session.address=address_post_changes_dict

#         redirect(URL('cart#address-information'))

#     else:
        
#         return dict(edit_address_form=edit_address_form)










# @auth.requires_login()
# def edit_address():

#     from datetime import datetime

#     allowable_address_ids=[]
#     allowable_addresses=db(db.addresses.user_id==auth.user_id).select(db.addresses.id)
#     for address_row in allowable_addresses:
#         allowable_address_ids.append(str(address_row.id))

#     if request.vars['pri_key'] not in allowable_address_ids:

#         response.flash="You aren't allowed to edit the address with that id"
#         session.flash=response.flash
#         redirect(URL('cart'))

#     address_pre_changes_dict=db(db.addresses.id==request.vars['pri_key']).select()[0]

#     edit_address_form=SQLFORM(db.addresses,record=request.vars['pri_key'], buttons=[TAG.button('Submit',_type="submit"), A("Cancel",_class='btn',_href=URL("cart"))])

#     if edit_address_form.process().accepted:

#         redirect(URL('cart#address-information'))

#     else:
        
#         return dict(edit_address_form=edit_address_form)










@auth.requires_login()
def address():

    from datetime import datetime

    db.addresses.default_address.value=True

    if not request.vars['pri_key']:
        address_id=None
    else:


        address_id=request.vars['pri_key']
        allowable_address_ids=[]
        allowable_addresses=db(db.addresses.user_id==auth.user_id).select(db.addresses.id)
        for address_row in allowable_addresses:
            allowable_address_ids.append(str(address_row.id))

        if address_id not in allowable_address_ids:

            response.flash="You aren't allowed to edit the address with that id"
            session.flash=response.flash
            redirect(URL('cart'))


    address_form=SQLFORM(
        db.addresses,
        record=address_id, 
        buttons=[
        A("Cancel",_class='btn btn-danger',_href=URL("cart#address-information")),
        TAG.button('Submit',_type="submit", _class="btn btn-info")
        ],
        fields=['first_name','last_name','street_address_line_1','street_address_line_2','municipality','administrative_area','postal_code','country'],
        labels={'first_name':'First Name',
                'last_name':'Last Name',
                'street_address_line_1':'Street Address Line 1',
                'street_address_line_2':'Street Address Line 2',
                'municipality': 'City/Town/Municipality',
                'administrative_area':'State/Administrative Area',
                'postal_code':'Zipcode/Postal Code',
                'country':'Country',
                },
    )

    address_form.vars.default_address=True

    # address_form.custom.widget.field_name['_class'] = 'bla bla'

    for input_field in address_form.elements('input', _class='string'):
        input_field['_class'] = 'form-control'

    for input_field in address_form.elements('select',_class='generic-widget'):
        input_field['_class'] = 'generic-widget address-view-combo-box'


    if address_form.process().accepted:

        redirect(URL('cart#address-information'))

    else:
        
        return dict(address_form=address_form)


# @auth.requires_login()
# def add_new_address():

#     countries=db(db.country_codes.is_active==True).select()
#     print countries

#     from datetime import datetime

#     add_address_form=SQLFORM(db.addresses)

#     if add_address_form.process().accepted:

#         redirect(URL('cart#address-information'))

#     else:
        
#         return dict(add_address_form=add_address_form)















# def default_address_2():
#     session.test_var=request.vars.default_address_id
#     if auth.is_logged_in():
#         rows=db((db.addresses.user_id==auth.user_id)&(db.addresses.default_address==True)).select()
#         for row in rows:
#             row.default_choice=False
#         db(db.addresses.id==request.vars.default_address_id).select()[0].default_address=True
#     return locals()



def ajax_shipping_information():


    ## Imports
    import easypost
    import json
    from aux import create_shipment
    from aux import retrieve_cart_contents
    from aux import bdays_to_days
    from aux import ordinal_indicator
    from datetime import datetime
    from datetime import timedelta


    ## Don't know where I should put this, probably not here though. 
    shipping_rates_ignore=dict(
        USPS=dict(
            US=[
                'ParcelSelect',
                ],
            
            INT=[
                'FirstClassMailInternational',
                'GlobalExpressGuaranteed'
                ],

            ),
        )


    ## This is the address_id in the DB of the clicked address
    default_address_id=int(request.vars.new_choice)

    print "default_address_id"
    print default_address_id

    ## Add to session for easy retrieval? - I don't think this is necessary anymore as I'm storing in db
    # session.default_address_id=default_address_id
    
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
    address.update(default_address=True)
    address.update_record()

    ## We have the address from the DB so now we have to prep it for inclusion in a call to easypost
    address_info=dict(
        first_name=address.first_name,
        last_name=address.last_name,
        street_address_line_1=address.street_address_line_1, 
        street_address_line_2=address.street_address_line_2, 
        municipality=address.municipality, 
        administrative_area=address.administrative_area, 
        postal_code=address.postal_code, 
        country=address.country,
    )


    ## I need the default shipping rate id
    easypost_default_shipping_rate_id=address.easypost_default_shipping_rate_id


    ## As part of the request to easypost we need to know the cart contents - get from the DB
    cart=retrieve_cart_contents(auth,db, is_active=True)

    ## If the cart is empty!
    if not cart:
        error_status=True
        error_message='There is nothing in your cart to ship'
        return json.dumps(dict(error_status=error_status, error_message=error_message, shipping_options_LOD=[]))

    ## Don't really need an else because of the return, but if there is stuff in the cart
    cart_for_shipping_calculations=[]
    cart_weight_oz=0
    cart_cost_USD=0

    ## For item in the cart
    for row in cart:
        product=db(db.product.id==row.product_id).select().first()
        cart_weight_oz+=float(product.weight_oz)*float(row.product_qty)
        cart_cost_USD+=float(product.cost_USD)*float(row.product_qty)

        # cart_last_modified_list.append(row.time_added)
        # if row.time_removed is not None:
        #     cart_last_modified_list.append(row.time_removed)
        # print cart_last_modified_list

        cart_for_shipping_calculations.append(dict(
            product_name=product.product_name,
            product_cost=product.cost_USD,
            product_qty=row.product_qty,
            product_weight=product.weight_oz,
            product_shipping_desc=product.shipping_description,
            ))


    ## Get a whole new cart to do the last modified time!?!?!??
    cart_last_modified_list=[]
    cart_for_last_modified_time=retrieve_cart_contents(auth,db,is_active=False)

    for row in cart_for_last_modified_time:

        cart_last_modified_list.append(row.time_added)

        if row.time_removed is not None:
            cart_last_modified_list.append(row.time_removed)

        # print cart_last_modified_list


    ## Not sure why this is in this particular place yet
    shipping_options_LOD=[]
    error_status=False
    error_message=None

    shipping_information=dict(
        shipping_options_LOD=shipping_options_LOD,
        error_status=error_status,
        error_message=error_message,
        )


    ## The following tries to decide whether or not to make another call to easypost. 
    ## Get the time of when shit happened 
    easypost_last_retrieved_time=address.easypost_api_datetime

    address_last_modified_time=address.last_modified
    cart_last_modified_time=max(cart_last_modified_list)
    threshold_time=datetime.now()-timedelta(hours=24)

    ## Put all the times in a list (except the api time)
    ## and remove any possible nones so that the max function works ok!
    time_list=[address_last_modified_time,cart_last_modified_time,threshold_time]
    time_list_no_none=[x for x in time_list if x is not None]

    if len(time_list_no_none)==0:
        time_list_no_none=[datetime.now()]

    master_last_modified_time=max(time_list_no_none)

    # print "api time"
    # print easypost_last_retrieved_time
    # print "last modified time"
    # print master_last_modified_time

    ## After getting the address from the db, check to see if the address id is 
    ## already associated with a session variable for shipping rates
    # print session.shipping_rates

    ## Does session.shipping_rates exist?
    if session.shipping_rates:
        ## Is there a listing for the selected address?
        if default_address_id in session.shipping_rates.keys():
            ## Is the time that the shipping info was retrieved current enough?
            if easypost_last_retrieved_time>master_last_modified_time:
                ## If all that passes, just get the shipping_rates from session. 
                shipping_rates=session.shipping_rates

                ## For every rate in shipping_rates
                for key,value in shipping_rates.iteritems():

                    ## Set them all to false one by one, and then the default set to true
                    for rate in shipping_rates[key]:
                        rate['selected_shipping_option']=False
                        if rate['rate_id']==easypost_default_shipping_rate_id:
                            rate['selected_shipping_option']=True

                ## Then reset session.shipping_rates to the new shipping_rates that you just made. 
                session.shipping_rates=shipping_rates

                ## Return that shit. This function is used for ajax
                return json.dumps(dict(error_status=False, error_message=None, shipping_options_LOD=session.shipping_rates[default_address_id]))



    ## If session.shipping_rates doesn't exist, 
    ## the default_address_id is not one of the addresses that has shipping info
    ## the shipping_info is not current enough,
    ## Then we have to make a call to easypost to get new shit. 

    ## Now we have the address that was chosen, the address info for the address that was chosen
    ## the cart info, and the combined weight of our package. Let's make a call
    try:

        print "Creating a new shipment"

        ## This function call takes these params and makes a call to easypost
        ## and returns exactly what it gets back. 
        shipment=create_shipment(address_info, cart_for_shipping_calculations)
        print shipment

        ## Put shipment info in the session to get it later!
        ## PUT THIS IN THE DB INSTEAD? NO! Just put the ID
        ## This is different than the session.shipping_rates
        session.shipment_info_from_easypost=shipment

        ## At this point I've already put the clicked address info in the db
        ## so now I'm just getting it back out!
        clicked_address = db(db.addresses.id==default_address_id).select().first()
        
        clicked_address.update(easypost_shipping_id=shipment.id)
        clicked_address.update(easypost_api_datetime=datetime.now())

        clicked_address.update_record()

        ## If no rates were returned by the call
        if len(shipment.rates)==0:
            error_status=True
            error_message='No rates are being returned for the selected address'
            return json.dumps(dict(error_status=error_status, error_message=error_message, shipping_options_LOD=[]))

        ## If there appear to be some rates that came back. 
        else:
            # Generate list of sorted rates
            shipping_rates_for_sorting=[]
            for i in range(len(shipment.rates)):
                shipping_rates_for_sorting.append(float(shipment.rates[i].rate))

            #shipping_rates_for_sorting.sort()
            shipping_rates_for_sorting=sorted(shipping_rates_for_sorting)

            
            # Build the shipping grid
            # I need to be able to sort the shipping rates based on the rate. 
            for j in range(len(shipping_rates_for_sorting)):

                for i in range(len(shipment.rates)):

                    if shipping_rates_for_sorting[j]==float(shipment.rates[i].rate):


                        ## This is to lazily exclude shipping options if they are in the exclude shipping options list
                        include_option=True
                        try:

                            ## Convert Country Code to either US or INT
                            country_io=shipment['to_address']['country']
                            if country_io=='US':
                                pass
                            else:
                                country_io='INT'

                            ## If the shipping rate name is in the list, exclude it. 
                            # print shipment.rates[i].service
                            # print shipping_rates_ignore[shipment.rates[i].carrier][country_io]
                            if shipment.rates[i].service in shipping_rates_ignore[shipment.rates[i].carrier][country_io]:
                                include_option=False
                            else:
                                pass

                        ## If you run into a key_error, don't exclude anything. 
                        except:
                            pass


                        ## If the option makes into consideration
                        if include_option:

                            ## I don't think I need this anymore

                            # if shipment.rates[i].service==session.shipping_choice:
                            #     radio_button=INPUT(_type='radio', _name='shipping', _checked='checked', _value=shipment.rates[i].service)
                            # else:
                            #     radio_button=INPUT(_type='radio', _name='shipping', _value=shipment.rates[i].service)

                            # print "shipment rate"
                            # print shipment.rates[i].id
                            # print "address db shipping rate id"
                            # print address.easypost_default_shipping_rate_id

                            ## If the brand new shipment that just came back has the same id as the default
                            ## rate id somehow, then make that the selected shipping option? 
                            if shipment.rates[i].id==address.easypost_default_shipping_rate_id:
                                selected_shipping_option=True
                                print "Does this ever turn out to be true?"
                            else:
                                selected_shipping_option=False

                            ## BUSINESS DAYS ARE CALCULATED HERE!
                            # print "# Days"
                            # print shipment.rates[i].delivery_days
                            # print "Country"
                            # print shipment['to_address']['country']
                            # print "Carrier"
                            # print shipment.rates[i].carrier
                            # print "Service"
                            # print shipment.rates[i].service

                            delivery_days=bdays_to_days(shipment.rates[i].delivery_days, country=shipment['to_address']['country'], carrier=shipment.rates[i].carrier, rate_name=shipment.rates[i].service)

                            print delivery_days

                            delivery_date=(datetime.today()+timedelta(days=delivery_days))

                            print delivery_date

                            delivery_date_text=delivery_date.strftime("%a %b %d")+ordinal_indicator(int(delivery_date.strftime("%d")))

                            print delivery_date_text

                            shipping_option_dict=dict(
                                carrier=shipment.rates[i].carrier,
                                service=camelcaseToUnderscore(shipment.rates[i].service),
                                service_original=shipment.rates[i].service,
                                rate=shipment.rates[i].rate,
                                rate_id=shipment.rates[i].id,
                                shipment_id=shipment.rates[i].shipment_id,
                                delivery_days=delivery_days,
                                delivery_date=delivery_date.isoformat(),
                                delivery_date_text=delivery_date_text,
                                selected_shipping_option=selected_shipping_option,
                                )

                            print "here"
                            shipping_options_LOD.append(shipping_option_dict)

                            print "here 2"

                        else:
                            pass

            error_status=False
            error_message=None

            if not session.shipping_rates:
                session.shipping_rates={}

            session.shipping_rates[address.id]=shipping_options_LOD

            return json.dumps(dict(error_status=error_status, error_message=error_message, shipping_options_LOD=shipping_options_LOD))


    except easypost.Error:
        error_status=True
        #error_message='There was a problem generating the shipping costs for '+str(default_address_id)
        error_message='There was a problem fetching the shipping information'
        return json.dumps(dict(error_status=error_status, error_message=error_message, shipping_options_LOD=[]))

    except AttributeError:
        error_status=True
        error_message='There is nothing in your cart to ship'
        return json.dumps(dict(error_status=error_status, error_message=error_message, shipping_options_LOD=[]))

    except TypeError:
        error_status=True
        error_message='There is no address to ship to'
        return json.dumps(dict(error_status=error_status, error_message=error_message, shipping_options_LOD=[]))


## Old shipping code
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




def ajax_choose_shipping_option():

    import json

    easypost_default_shipping_rate_id=request.vars.shipping_choice_rate_id

    default_address=db((db.addresses.user_id==auth.user_id)&(db.addresses.default_address==True)).select().first()

    default_address.update(easypost_default_shipping_rate_id=easypost_default_shipping_rate_id)

    default_address.update_record()

    ## Also update the session variable so that the client side can more easily know what the default shipping choice is




    #I need to know the address id, and then I can retrieve the appropriate rates dict, then I need to know the rate id so I can edit the appropriate rate.

    #print (session.shipping_rates[default_address.id])

    for rate_index in range(len(session.shipping_rates[default_address.id])):

        # print ("hello?")
        # print session.shipping_rates[default_address.id][rate_index]['rate_id']
        # print default_address.easypost_default_shipping_rate_id

        if session.shipping_rates[default_address.id][rate_index]['rate_id']==default_address.easypost_default_shipping_rate_id:

            # print ("setting the default shipping option in the session")
            shipping_cost_USD=session.shipping_rates[default_address.id][rate_index]['rate']
            # print (shipping_cost_USD)
            session.shipping_rates[default_address.id][rate_index]['selected_shipping_option']=True


    # print session.cart_cost_USD

    # print session.shipping_rates

    try:

        total_cost_USD=float(shipping_cost_USD)+float(session.cart_cost_USD)
        total_cost_USD="{0:.2f}".format(total_cost_USD)

        session.total_cost_USC=int(float(total_cost_USD)*100)

    except:

        total_cost_USD="There was a problem"


    return json.dumps(dict(
        shipping_cost_USD=shipping_cost_USD,
        total_cost_USD=total_cost_USD,#total_cost_USD,
        ))

def ajax_choose_payment_option():

    session.payment_method=request.vars.payment_method





def default_card():
    if auth.is_logged_in():
        row=db(db.stripe_customers.muses_id==auth.user_id).select().first()
        row.update(stripe_next_card_id=request.vars.stripe_next_card_id)
        row.update_record()

    if request.vars.stripe_next_card_id=='paypal':
        session.payment_method='paypal'
    else:
        session.payment_method='stripe'


# def one():
#     ajax_test=FORM(INPUT(_name='nametest', _onkeyup="ajax('echo', ['nametest'], ':eval')"))
#     return locals()

# def echo():
#     #return "jQuery(alert('msg')"
#     return "jQuery('#target').html(%s);" % repr(request.vars.nametest)
#     #return request.vars.name

# def two():
#     row = db(db.addresses==2)
#     #row.update(default_address=True)
#     #row.update_record()
#     return locals()
            




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



# def stripe_remove_session_users():
    
#     ## set cursor_id to get through the while loop the first time
#     cursor_id=""

#     ## set has_more to True to enter the while loop initially
#     has_more=True

#     ## While there are no more pages of users to go through
#     while has_more==True:

#         ## If this is the first time calling for customers...
#         if cursor_id=="":
#             ## Get the first 10 stripe customers (make the call with no args)
#             stripe_customer_list=stripe.Customer.all()
#         ## If this is not the first time
#         else:
#             ## make the call by setting starting_after to the id of the customer ending the previous call.
#             stripe_customer_list=stripe.Customer.all(starting_after=cursor_id)

#         ## Get the data portion of the dictionary returned.
#         stripe_customer_list_data=stripe_customer_list['data']

#         ## Get the id of the final customer in the list for next iteration.
#         cursor_id=stripe_customer_list_data[-1]['id']

#         ## Check to see if the email of the customer is in the threemuses user list. 
#         ## (I should be using stripe id not email for this)
#         for stripe_customer in stripe_customer_list_data:
#             three_muses_user=db(db.stripe_customers.stripe_id==stripe_customer['id']).select().first()
#             if not three_muses_user:

#                 hours_since_creation=(time.time()-stripe_customer['created'])/3600

#                 if hours_since_creation>=STRIPE_SESSION_RETIRE_HOURS:

#                     scu=stripe.Customer.retrieve(stripe_customer['id'])
#                     dummy=scu.delete()

#                 else:
#                     pass
#             else:
#                 pass


#         ## This will be false if no more customers to retrieve. True if there are. 
#         has_more=stripe_customer_list['has_more']

#     return dict(message="Done!")


@auth.requires_login()
def view_purchase_history():
    query=(db.purchase_history_data.muses_id==auth.user_id)

    db.purchase_history_data.id.readable=db.purchase_history_data.id.writable=False
    # db.purchase_history_data.muses_name.readable=db.purchase_history_data.muses_name.writable=False
    db.purchase_history_data.muses_id.readable=db.purchase_history_data.muses_id.writable=False
    db.purchase_history_data.muses_email_address.readable=db.purchase_history_data.muses_email_address.writable=False
    # db.purchase_history_data.session_id_3muses.readable=db.purchase_history_data.session_id_3muses.writable=False
    # db.purchase_history_data.session_db_table.readable=db.purchase_history_data.session_db_table.writable=False
    db.purchase_history_data.session_db_record_id.readable=db.purchase_history_data.session_db_record_id.writable=False
    db.purchase_history_data.easypost_rate_id.readable=db.purchase_history_data.easypost_rate_id.writable=False
    db.purchase_history_data.easypost_shipment_id.readable=db.purchase_history_data.easypost_shipment_id.writable=False
    # db.purchase_history_data.payment_service.readable=db.purchase_history_data.payment_service.writable=False
    db.purchase_history_data.payment_confirmation_id.readable=db.purchase_history_data.payment_service.writable=False
    # db.purchase_history_data.payment_stripe_user_id.readable=db.purchase_history_data.payment_stripe_user_id.writable=False
    # db.purchase_history_data.payment_stripe_card_id.readable=db.purchase_history_data.payment_stripe_card_id.writable=False
    # db.purchase_history_data.payment_stripe_transaction_id.readable=db.purchase_history_data.payment_stripe_transaction_id.writable=False

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
        fields=[
            db.purchase_history_data.muses_transaction_datetime,
            db.purchase_history_data.payment_invoice_number,
            db.purchase_history_data.payment_service,
            db.purchase_history_data.cart_base_cost,
            db.purchase_history_data.cart_shipping_cost,
            db.purchase_history_data.cart_total_cost,
            db.purchase_history_data.shipping_name_first,
            db.purchase_history_data.shipping_name_last,
            db.purchase_history_data.shipping_street_address_line_1,
            db.purchase_history_data.shipping_street_address_line_2,
            db.purchase_history_data.shipping_municipality,
            db.purchase_history_data.shipping_administrative_area,
            db.purchase_history_data.shipping_postal_code,
            db.purchase_history_data.shipping_country,
            db.purchase_history_data.easypost_shipping_carrier,
            db.purchase_history_data.easypost_shipping_service,
            db.purchase_history_data.easypost_delivery_date,
            ],

        headers={
            'purchase_history_data.muses_transaction_datetime':'Purchase Date',
            'purchase_history_data.payment_invoice_number':'Confirmation #',
            'purchase_history_data.payment_service':'Payment Method',
            'purchase_history_data.cart_base_cost':'Subtotal',
            'purchase_history_data.cart_shipping_cost':'Shipping Cost',
            'purchase_history_data.cart_total_cost':'Total Cost',
            'purchase_history_data.shipping_name_first':'First Name',
            'purchase_history_data.shipping_name_last':'Last Name',
            'purchase_history_data.shipping_street_address_line_1':'Address L1',
            'purchase_history_data.shipping_street_address_line_2':'Address L2',
            'purchase_history_data.shipping_municipality':'City/ Town',
            'purchase_history_data.shipping_administrative_area':'State/ Admin Area',
            'purchase_history_data.shipping_postal_code':'Postal Code',
            'purchase_history_data.shipping_country':'Country',
            'purchase_history_data.easypost_shipping_carrier':'Carrier',
            'purchase_history_data.easypost_shipping_service':'Service',
            'purchase_history_data.easypost_delivery_date':'Estimated Delivery Date',
            },
        )

    return dict(grid=grid)


def receipt_test():

    # email_icons=dict(
    #     products_icon_url="https://s3.amazonaws.com/threemusesglass/icons/ProductIcon.png",
    #     address_icon_url="https://s3.amazonaws.com/threemusesglass/icons/AddressIcon.png",
    #     shipping_icon_url="https://s3.amazonaws.com/threemusesglass/icons/ShippingIcon.png",
    #     payment_icon_url="https://s3.amazonaws.com/threemusesglass/icons/PaymentIcon.png",
    #     summary_icon_url="https://s3.amazonaws.com/threemusesglass/icons/SummaryIcon.png",
    #     )

    receipt_context=dict(
        purchase_history_data_row=db(db.purchase_history_data.id==200).select().first(),
        purchase_history_products_rows=db(db.purchase_history_products.purchase_history_data_id==200).select(),
        )

    # receipt_context=dict(
    #     email_icons=email_icons,
    #     )

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


def receipt():
    return dict()


import string
import random
def id_generator(size=16, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))




def paypal_confirmation():

    ## Get the keys! and set configuration
    import paypalrestsdk
    import json
    from aux import create_purchase_history_dict
    from aux import generate_confirmation_email_receipt_context
    from aux import retrieve_cart_contents
       
    PAYPAL_CLIENT_ID=get_env_var('paypal', PRODUCTION_STATUS,'PAYPAL_CLIENT_ID')
    PAYPAL_CLIENT_SECRET=get_env_var('paypal', PRODUCTION_STATUS,'PAYPAL_CLIENT_SECRET')

    paypalrestsdk.configure({
        "mode": PAYPAL_MODE, # sandbox or live
        "client_id": PAYPAL_CLIENT_ID,
        "client_secret": PAYPAL_CLIENT_SECRET })


    skip=True
    ## Make sure this person recently started the purchase process
    if session.expect_paypal_webhook or skip:
    #if True:
    # session.paypal_vars=request.vars

        payer_id=request.vars['PayerID']
        payment_id=request.vars['paymentId']
        
        ## Use the paymentId to retrieve payment object
        payment=paypalrestsdk.Payment.find(payment_id)

        email_address=payment['payer']['payer_info']['email']


        ## Try to execute the payment with the payer_id
        if payment.execute({"payer_id":payer_id}) or skip:
        #if True:
            # print payment
            status="success"
            session.expect_paypal_webhook=False

            ## Get user information
            # if auth.is_logged_in():

            user_data=db(db.auth_user.id==auth.user_id).select().first()


            ## Decided against this for now:

            # ## If you get from paypal and the user isn't full flegged
            # ## you have to add their email to the list of correspondence
            # if auth.has_membership('gimp'):

            #     #muses_email_address=payment['payer']['payer_info']['email']
            #     # user_record=db(db.auth_user.id==auth.user_id).select().first()
            #     # print (user_record)

            #     ## Even though they are gimp user, check to see if the email they used for paypal exists in the db
            #     existing_user=db(db.auth_user.email==payment['payer']['payer_info']['email']).select().first()

            #     ## If the email does not exixt it means you can change the user's email to the one the used in paypal
            #     if not existing_user:

            #         user_data.update(email=payment['payer']['payer_info']['email'])
            #         user_data.update_record()

            #         ## This tries to get a list of emails from the db but I'm pretty sure it is failing and that is 
            #         ## it still adds the email to the correspondence even though the logic is here to prevent that. 
            #         emails=db(db.email_correspondence.user_id==auth.user_id).select(db.email_correspondence.email)

            #         if payment['payer']['payer_info']['email'] in emails:
            #             pass
            #         else:
            #             db.email_correspondence.insert(user_id=auth.user_id,email=payment['payer']['payer_info']['email'], is_active=True)

            #     else:

            #         emails=db(db.email_correspondence.user_id==auth.user_id).select(db.email_correspondence.email)

            #         ## Same here as above comment. 
            #         if payment['payer']['payer_info']['email'] in emails:
            #             pass
            #         else:
            #             db.email_correspondence.insert(user_id=auth.user_id,email=payment['payer']['payer_info']['email'], is_active=True)



            address_data=db((db.addresses.user_id==auth.user_id)&(db.addresses.default_address==True)).select().first()


            shipping_rate_info=session.shipping_rates[address_data.id]
            for item in shipping_rate_info:
                if item['rate_id']==address_data.easypost_default_shipping_rate_id:
                    shipping_info=item


            purchase_history_dict=create_purchase_history_dict(
                ## This is probably really dangerous
                session_data=response,
                user_data=user_data,
                address_data=address_data,
                shipping_data=shipping_info,
                payment_service='paypal',
                payment_data=payment,
                payment_email=email_address,
                payment_invoice_number=session.payment_information['information_LOD'][0]['invoice_number'],
                payment_id=payment_id,
                summary_data=session.summary_information,
                )

            ## place data in the database. 
            purchase_history_data_id=db.purchase_history_data.bulk_insert([purchase_history_dict])[0]

            ## Add id of most recent purchase to the session for viewing purposes.
            session.session_purchase_history_data_id=purchase_history_data_id


            ## For every item in the cart, insert a record with the id of the purchase history, the product id and the qty.
            purchase_history_products_LOD=[]

            cart=retrieve_cart_contents(auth,db)

            
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


            purchase_history_products_ids=db.purchase_history_products.bulk_insert(purchase_history_products_LOD)


            receipt_context=generate_confirmation_email_receipt_context(
                muses_email_address=email_address, 
                purchase_history_data_row=db(db.purchase_history_data.id==purchase_history_data_id).select().first(),
                purchase_history_products_rows=db(db.purchase_history_products.purchase_history_data_id==purchase_history_data_id).select(),
            )


            #receipt_message_html = response.render('receipt.html', receipt_context)
            receipt_message_html = response.render('default/receipt.html', receipt_context)

            # email_address_query=db(db.email_correspondence.user_id==auth.user_id).select(db.email_correspondence.email).first()
            # email_address=list(email_address_query.as_dict().values())[0]
            #print email_address
            
            from postmark import PMMail
            message = PMMail(api_key=POSTMARK_API_KEY,
                subject="Order Confirmation",
                sender="confirmation@threemuses.glass",
                #to=user_data.email,
                to=email_address,
                #html_body=final_div_html,
                html_body=receipt_message_html,
                tag="confirmation")

            ## try:

            ## Set this up so that it emails rebecca if anything bad happens with the info she
            ## needs to send out the product. 
            message.send()

            ## except postmark.core.PMMailUnprocessableEntityException:
            ## tell the user that the email I tried to send the receipt to failed
            ## and that they need to choose a different one if they want a reciept!


            ## This has to be last, duh.
            redirect(URL('confirmation', args=(purchase_history_data_id)))



        ## If the payment failed this should go still redirect to confirmation just with an error instead of confirmation?
        ## OF should it go to a completely different page?
        else:

            status=payment.error
            session.expect_paypal_webhook=False

        return dict(status=status,payer_id=payer_id,payment_id=payment_id, payment=payment)

    ## What is this about?
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

# def scratch():
#     return dict()

# def scratch_ajax():

#     import json
#     new_choice=request.vars['new_choice']
#     if session.current_choice:

#         ## If the new choice is the same as the current choice, mark down that there was no change
#         if session.current_choice==request.vars['new_choice']:
#             return json.dumps(dict(current_choice=session.current_choice,previous_choice=session.previous_choice,change=False))
        
#         ## Otherwise, set old choice to current choice and current choice to new choice. 
#         else:
#             session.previous_choice=session.current_choice
#             session.current_choice=request.vars['new_choice']
#             return json.dumps(dict(current_choice=session.current_choice,previous_choice=session.previous_choice,change=True))

#     ## If there was no current choice, then just make current choice new choice and previous choice None
#     else:
#         session.current_choice=request.vars['new_choice']
#         session.previous_choice=None
#         return json.dumps(dict(current_choice=session.current_choice,previous_choice=session.previous_choice,change=True))



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
        # temp_password='guestuser'

        # temp_email=str(time())+'@'+str(id_generator())+'.com'
        temp_email="GUEST_USER"+'@'+str(int(time()*100))+'.'+str(id_generator())

        user_id=db.auth_user.insert(first_name="Guest", last_name="User", email=temp_email, password=db.auth_user.password.requires[0](temp_password)[0])
        
        auth.add_membership('gimp',db.auth_user(user_id))

        auth.login_bare(temp_email,temp_password)
        
        return dict()



@auth.requires_login()
def profile():

    if auth.has_membership('gimp'):

        response.flash="Log in to access your profile"
        session.flash=response.flash
        redirect(URL('login', vars=dict(_next='profile')))

    else:
        pass

    return dict(form=auth.profile())



def login():
    return dict(form=auth.login())

def request_reset_password():
    return dict(form=auth.request_reset_password(next=URL('default','index')))

# def set_reset_message(form):
#     user = db.auth_user(email=form.vars.email)
#     username = user.username if user else ''
#     auth.messages.reset_password = 'Hey %s, click on the link %%(link)s to reset your password' % username
# auth.settings.reset_password_onvalidation = set_reset_message


def reset_password():
    #auth.settings.reset_password_onvalidation = [reset_password_callback]
    auth.settings.reset_password_onaccept = [reset_password_callback]

    # reset_password_callback('arg')

    form=auth.reset_password()

    # if form.accepted:
    #     print "WTF"
    #     reset_password_callback(form)
    # else:
    #     print "not accepted, betch"
    #     pass

    return dict(form=form)

def logout():
    return dict(form=auth.logout(next=URL('categories')))

def register():
    return dict(form=auth.register())

# def custom_auth_form():
#     return dict(form=auth())


def change_password():

    if auth.has_membership('gimp'):
        response.flash="You don't have a password to change!"
        session.flash=response.flash
        redirect(URL('categories'))

    return dict(form=auth.change_password(next=URL('profile')))




# def bdays_to_days():
#     from pandas.tseries.offsets import CustomBusinessDay
#     from pandas.tseries.holiday import USFederalHolidayCalendar
#     from datetime import datetime

#     bday_us = CustomBusinessDay(calendar=USFederalHolidayCalendar())
#     start_date=datetime.today()
#     end_date=start_date+bday_us*3

#     elapsed_days=(end_date-start_date).days


#     return dict(days=elapsed_days)


def session_look():
    return dict(session_vars=session)