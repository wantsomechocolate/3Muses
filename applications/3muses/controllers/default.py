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
import easypost
import stripe
#from gluon.contrib.stripe import Stripe

STRIPE_SESSION_RETIRE_HOURS=26 #(1/20.0)
SERVER_SESSION_RETIRE_HOURS=26 #(1/20.0)


## is it ok to have top level stuff here? It works so leave it until someone says its bad. 
if response.session_id_name in response.cookies:
    response.cookies[response.session_id_name]['expires']=int(3600*SERVER_SESSION_RETIRE_HOURS)

else:
    # cookie key doesn't get created until second time visiting a page for incognito chrome and probably
    # other private browsing modes. 
    pass


try:
    ## see if you can acces the heroku environment variables
    STRIPE_SECRET=os.environ['STRIPE_SECRET']
    STRIPE_PUBLISHABLE=os.environ['STRIPE_PUBLISHABLE']

## what exception exactly?
except KeyError:

    # you aren't running on heroku
    # this will fail if it can't find the local keys. GOOD.
    with open('/home/wantsomechocolate/Code/API Info/api_keys.txt','r') as fh:
        text=fh.read()
        api_keys = ast.literal_eval(text)
    
    STRIPE_SECRET=api_keys['stripe']['test']['STRIPE_SECRET']
    STRIPE_PUBLISHABLE=api_keys['stripe']['test']['STRIPE_PUBLISHABLE']

stripe.api_key = STRIPE_SECRET



try:
    ## see if you can acces the heroku environment variables
    EASYPOST_KEY=os.environ['EASYPOST_KEY']

## what exception exactly?
except KeyError:

    # you aren't running on heroku
    # this will fail if it can't find the local keys. GOOD.
    with open('/home/wantsomechocolate/Code/API Info/api_keys.txt','r') as fh:
        text=fh.read()
        api_keys = ast.literal_eval(text)
    
    EASYPOST_KEY=api_keys['easypost']['test']['EASYPOST_KEY']

easypost.api_key=EASYPOST_KEY

try:
    POSTMARK_API_KEY=os.environ['POSTMARK_API_KEY']
except KeyError:

    with open('/home/wantsomechocolate/Code/API Info/api_keys.txt','r') as fh:
        text=fh.read()
        api_keys=ast.literal_eval(text)

    POSTMARK_API_KEY=api_keys['postmark']['test']['POSTMARK_API_KEY']





if db._dbname=='sqlite':

    sqlite_tf=True

else:

    sqlite_tf=False



S3_BUCKET_PREFIX='https://s3.amazonaws.com/threemusesglass/site_images/'


## The static views (index, categories, display, product, meet the artist.)

def index():

    left_sidebar_enabled=True

    right_sidebar_enabled=True

    #return locals()

    return dict(
        left_sidebar_enabled=left_sidebar_enabled, 
        right_sidebar_enabled=right_sidebar_enabled,
        )



def categories():

    if request.args(0) is not None:
        redirect(URL('categories'))
    else:
        pass

    category_rows=db(db.categories.is_active==True).select(orderby=db.categories.display_order)

    left_sidebar_enabled=False

    right_sidebar_enabled=False

    #return locals()

    return dict(
        category_rows=category_rows,
        left_sidebar_enabled=left_sidebar_enabled, 
        right_sidebar_enabled=right_sidebar_enabled,
        )



def display():
    
    # if request.args(0) is None:
    #     redirect(URL('categories'))
    # else:
    #     pass

    category_name=request.args[0].replace("_"," ")


    category_id=int(db(db.categories.category_name==category_name).select().first()['id'])

    # category_id=request.args[0]
    product_rows=db((db.product.category_name==category_id)&(db.product.is_active==True)).select(orderby=db.product.display_order)
    

    # if len(product_rows) == 0:
    #     redirect(URL('dne.html', vars=dict(page='display')))
    # else:
    #     pass

    return dict(
        category_id=category_id,
        product_rows=product_rows,
        )



def product():

    product_id=request.args[0]

    product_row=db(db.product.id==product_id).select()

    cart_form=FORM(

        INPUT(_type="hidden",
            _name="qty",
            _value=1,
            #_placeholder="Enter Quantity",
            #requires=IS_INT_IN_RANGE(1,2),
        ),

        BR(),

        

        INPUT(_type='submit', _class="btn btn-default", _value="Add to Cart"),
    )

    if cart_form.accepts(request, session):

        if auth.is_logged_in():

            try:
                existing_cart_entry=db((db.muses_cart.product_id==product_id)&(db.muses_cart.user_id==auth.user_id)).select()[0]
                db.muses_cart[existing_cart_entry.id]=dict(product_qty=cart_form.vars.qty)

            except IndexError:

                db.muses_cart.insert(
                    user_id=auth.user_id,
                    product_id=product_id,
                    product_qty=cart_form.vars.qty,
                )

        else:

            if not session.cart:

                session.cart={}

            session.cart[product_id]=cart_form.vars.qty

    else:

        pass

    #return locals()

    return dict(
        product_id=product_id,
        product_row=product_row,
        cart_form=cart_form,
        )



## Meet the artist is under construction
def artist():
    return locals()



## Functions for adding things to session or db. 

def add_new_card():

    if auth.is_logged_in():

        stripe_form=FORM(
            DIV( 
                LABEL( 'Name on the Card',),
                
                DIV(
                    INPUT(
                        _type='text', 
                        _name='name', 
                        _class='form-control', 
                    ),
                ),
            ),

            DIV( 
                LABEL( 'Card Number',),
                
                DIV(
                    INPUT(
                        _type='integer', 
                        _name='number', 
                        _class='form-control', 
                    ),
                ),
            ),

            DIV(
                LABEL('Card CVC Number',),
                
                DIV(
                    INPUT(
                        _type='integer', 
                        _name='cvc', 
                        _class='form-control', 
                    ),
                ),
            ),

            DIV(
                LABEL('Expiration Month',),
                
                DIV(
                    INPUT(
                        _type='integer', 
                        _name='exp_month', 
                        _class='form-control', 
                    ),
                ),
            ),

            DIV(
                LABEL('Expiration Year (YYYY)',),
                
                DIV(
                    INPUT(
                        _type='integer', 
                        _name='exp_year', 
                        _class='form-control', 
                        requires=IS_INT_IN_RANGE(2014,3000),
                    ),
                ),
            ),
       
            INPUT(_type='submit', _class="btn btn-default"),
                
        _class='form-horizontal',
        _role='form').process()

    else:
        stripe_form=FORM(

            DIV( 
                LABEL( 'Email Address',),
                
                DIV(
                    INPUT(
                        _type='text', 
                        _name='email', 
                        _class='form-control', 
                    ),
                ),
            ),
            DIV( 
                LABEL( 'Name on the Card',),
                
                DIV(
                    INPUT(
                        _type='text', 
                        _name='name', 
                        _class='form-control', 
                    ),
                ),
            ),

            DIV( 
                LABEL( 'Card Number',),
                
                DIV(
                    INPUT(
                        _type='integer', 
                        _name='number', 
                        _class='form-control', 
                    ),
                ),
            ),

            DIV(
                LABEL('Card CVC Number',),
                
                DIV(
                    INPUT(
                        _type='integer', 
                        _name='cvc', 
                        _class='form-control', 
                    ),
                ),
            ),

            DIV(
                LABEL('Expiration Month',),
                
                DIV(
                    INPUT(
                        _type='integer', 
                        _name='exp_month', 
                        _class='form-control', 
                    ),
                ),
            ),

            DIV(
                LABEL('Expiration Year (YYYY)',),
                
                DIV(
                    INPUT(
                        _type='integer', 
                        _name='exp_year', 
                        _class='form-control', 
                        requires=IS_INT_IN_RANGE(2015,3000)
                    ),
                ),
            ),
       
            INPUT(_type='submit', _class="btn btn-default"),
                
        _class='form-horizontal',
        _role='form').process()



    if stripe_form.accepted:
        ## If there are no errors found in the form (which there shouldn't be because there are no
        ## requirements yet), try to retrieve the customer token from the database
        ## and create a new card. If the logged in user doesn't have a stripe customer token yet, 
        ## it will be unable to find one and raise an index error. 

        #from gluon.debug import dbg
        #dbg.set_trace()

        #existing_stripe_id=db(db.stripe_customers.user_id==auth.user_id).select()['stripeToken']
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
            if auth.is_logged_in():

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
                        stripeEmail=auth.user.email,
                    )

                ## if there was a problem connecting to the stripe api
                except stripe.error.APIConnectionError:
                    customer=None

            #If the user isn't logged in, add the info to session. 
            else:
                try:
                    customer = stripe.Customer.create(
                        email=stripe_form.vars.email,
                        card=dict(
                            name=stripe_form.vars.name,
                            number=stripe_form.vars.number,
                            cvc=stripe_form.vars.cvc,
                            exp_month=stripe_form.vars.exp_month,
                            exp_year=stripe_form.vars.exp_year,     
                        )
                    )

                    session_card=customer.cards.all()

                    #add the fact the current user has card info now to session
                    session.card_info=dict(
                        stripe_id=customer.id,
                        email=customer.email,
                        name=session_card['data'][0]['name'],
                        last4=session_card['data'][0]['last4'],
                        brand=session_card['data'][0]['brand'],
                        exp_month=session_card['data'][0]['exp_month'],
                        exp_year=session_card['data'][0]['exp_year'],
                        card_id=session_card['data'][0]['id'],
                        )
                except stripe.error.APIConnectionError:
                    customer=None

        redirect(URL('cart'))

    else:
        
        return dict(stripe_form=stripe_form)



def add_new_address():

    #http://codepen.io/Angelfire/pen/dJhyr

    add_address_form=FORM(
        DIV( 
            LABEL( 'Street Address/ PO Box/ Etc.',),
            
            DIV(
                INPUT(
                    _type='text', 
                    _name='street_address_line_1', 
                    _class='form-control', 
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
                ),
            ),
        ),
   
        INPUT(_type='submit', _class="btn btn-default"),
            
    _class='form-horizontal',
    _role='form').process()

    if add_address_form.accepted:

        if auth.is_logged_in():
            db.addresses.insert(
                user_id=auth.user_id,
                street_address_line_1=add_address_form.vars.street_address_line_1,
                street_address_line_2=add_address_form.vars.street_address_line_2,
                municipality=add_address_form.vars.municipality,
                administrative_area=add_address_form.vars.administrative_area,
                postal_code=add_address_form.vars.postal_code,
                country=add_address_form.vars.country,
            )

        else:
            session.address=dict(
                street_address_line_1=add_address_form.vars.street_address_line_1,
                street_address_line_2=add_address_form.vars.street_address_line_2,
                municipality=add_address_form.vars.municipality,
                administrative_area=add_address_form.vars.administrative_area,
                postal_code=add_address_form.vars.postal_code,
                country=add_address_form.vars.country,
            )

        redirect(URL('cart'))

    else:
        
        return dict(add_address_form=add_address_form)



## Functions that were used for testing purposes. 

def cookie_test():
    if not session.counter:
        session.counter=1
    else:
        session.counter+=1
    counter=session.counter
    message="Hello from MyApp"
    
    return locals()



@auth.requires_login()
def stripe_test():
    stripe.api_key = STRIPE_SECRET
    if request.env.request_method=='POST':
        token = request.vars['stripeToken']

        customer = stripe.Customer.create(card=token,description=request.vars['stripeEmail'])

        # stripe.Charge.create(
        #     amount=2000, # amount in cents, again
        #     currency="usd",
        #     customer=customer.id
        #     )

        db.stripe_customers.insert(
            muses_id=auth.user_id,
            stripe_id=customer.id,
            stripeEmail=request.vars['stripeEmail']
            )

        message="Card info saved on Stripe"
        return locals()

        #except stripe.CardError, e:
            # The card has been declined
            #return locals()

    else:
        message="Save a card"
        return locals()



def cart():

#############################################################################################
###########----------------------------Cart Logic--------------------------------############
#############################################################################################

    if request.args(0) is not None:
        redirect(URL('cart'))
    else:
        pass


    #cart_grid_header_list=["Cart","Item","Cost","Qty", "Delete"]
    cart_grid_header_list=["Cart","Item","Cost", "Delete"]

    cart_grid_table_row_LOL=[]

    if auth.is_logged_in():

        cart_db=db(db.muses_cart.user_id==auth.user_id).select()

        if not cart_db:

            cart_grid=DIV("You have not yet added anything to your cart")

        else:
        
            for row in cart_db:

                product=db(db.product.id==row.product_id).select().first()

                if product.is_active==False:

                    db(db.muses_cart.product_id==product.id).delete()

                else:

                    if sqlite_tf:
                        srcattr=URL('download',db(db.image.product_name==row.product_id).select().first().s3_url)
                    else:
                        srcattr=S3_BUCKET_PREFIX+str(db(db.image.product_name==row.product_id).select().first().s3_url)
                    product_image_url=A(IMG(_src=srcattr), _href=URL('default','product',args=[row.product_id]))

                    delete_button=A('X', _href=URL('delete_item_from_cart', vars=dict(pri_key=row.id,redirect_url=URL('cart'))), _class="btn btn-primary")

                    cart_grid_table_row_list=[
                        product_image_url, 
                        product.product_name, 
                        product.cost_USD, 
                        #row.product_qty, 
                        delete_button
                    ]

                    cart_grid_table_row_LOL.append(cart_grid_table_row_list)

            cart_grid=table_generation(cart_grid_header_list, cart_grid_table_row_LOL, 'cart')

    # if the user is not logged in, use session cookies instead to generate the cart
    else:

        if not session.cart:

            cart_grid=DIV("You have not yet added anything to your cart")

        else:

            for key, value in session.cart.iteritems():

                product=db(db.product.id==key).select()[0]

                if sqlite_tf:
                    srcattr=URL('download',db(db.image.product_name==key).select()[0].s3_url)
                else:
                    srcattr='https://s3.amazonaws.com/threemusesglass/site_images/'+str(db(db.image.product_name==key).select()[0].s3_url)
                product_image_url=A(IMG(_src=srcattr), _href=URL('default','product',args=[key]))

                delete_button=A('X', _href=URL('delete_item_from_cart', vars=dict(pri_key=key, redirect_url=URL('cart'))), _class="btn btn-primary")

                cart_grid_table_row_list=[
                    product_image_url, 
                    product.product_name, 
                    product.cost_USD, 
                    #value, 
                    delete_button
                ]

                cart_grid_table_row_LOL.append(cart_grid_table_row_list)

            cart_grid=table_generation(cart_grid_header_list, cart_grid_table_row_LOL, 'cart')


#############################################################################################
###########---------------------------Address Logic------------------------------############
#############################################################################################

    address_grid_header_list=[
        'Select One',
        'No. & Street/ P.O. Box/ etc.', 
        'Apt/ Suite/ Floor/ etc.', 
        'Town/ Section/ Municipality',
        'State/ Admin Area',
        'Postal Code',
        'Country', 
        'Edit', 
        'Delete'
    ]

    address_grid_table_row_LOL=[]

    if auth.is_logged_in():

        address_list=db(db.addresses.user_id==auth.user_id).select(orderby=db.addresses.street_address_line_1)

        if not address_list:

            address_grid=DIV("You have not added any addresses yet")

        else:

            for j in range(len(address_list)):

                if address_list[j].default_address==True:
                    radio_button=INPUT(_type='radio', _name='address', _value=address_list[j].id, _checked='checked')
                else:
                    radio_button=INPUT(_type='radio', _name='address', _value=address_list[j].id)

                edit_button=A('<-', _href=URL('edit_db_address', vars=dict(pri_key=address_list[j].id)), _class="btn btn-primary")
                
                delete_button=A('X', _href=URL('delete_address', vars=dict(pri_key=address_list[j].id, redirect_url=URL('cart'))), _class="btn btn-primary")

                address_grid_table_row_list=[
                    radio_button, 
                    address_list[j].street_address_line_1, 
                    address_list[j].street_address_line_2, 
                    address_list[j].municipality, 
                    address_list[j].administrative_area, 
                    address_list[j].postal_code, 
                    address_list[j].country, 
                    edit_button, 
                    delete_button
                ]

                address_grid_table_row_LOL.append(address_grid_table_row_list)

            address_grid=table_generation(address_grid_header_list, address_grid_table_row_LOL, 'address')

    else:

        if not session.address:

            address_grid=DIV("You have not added an address yet")

        else:

            radio_button=FORM(INPUT(_type='radio', _name='address', _value='address', _checked='checked'), _action="")
            edit_button=A('<-', _href=URL('edit_session_address'), _class="btn btn-primary")
            delete_button=A('X', _href=URL('delete_address', vars=dict(redirect_url=URL('cart'))), _class="btn btn-primary")

            address_grid_table_row_list=[
                radio_button, 
                session.address['street_address_line_1'], 
                session.address['street_address_line_2'], 
                session.address['municipality'], 
                session.address['administrative_area'], 
                session.address['postal_code'], 
                session.address['country'], 
                edit_button, 
                delete_button
            ]

            address_grid_table_row_LOL.append(address_grid_table_row_list)

            address_grid=table_generation(address_grid_header_list, address_grid_table_row_LOL, 'address')


#############################################################################################
###########---------------------------Shipping Logic-----------------------------############
#############################################################################################

    try:

        if auth.is_logged_in():

            #get default_address and make a dict out of it
            address=db((db.addresses.user_id==auth.user_id)&(db.addresses.default_address==True)).select().first()

            cart=db(db.muses_cart.user_id==auth.user_id).select()
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
                

            ## address logic
            #address=db((db.addresses.user_id==auth.user_id)&(db.addresses.default_address==True)).select().first()

            address_info=dict(
                street_address_line_1=address.street_address_line_1, 
                street_address_line_2=address.street_address_line_2, 
                municipality=address.municipality, 
                administrative_area=address.administrative_area, 
                postal_code=address.postal_code, 
                country=address.country,
            )

        else:

            cart_for_shipping_calculations=[]
            cart_weight_oz=0
            cart_cost_USD=0

            for key, value in session.cart.iteritems():

                product=db(db.product.id==key).select().first()
                product_name=product.product_name
                product_cost=product.cost_USD
                product_qty=value

                total_cost=float(product_cost)*float(product_qty)

                product_weight=product.weight_oz
                product_shipping_desc=product.shipping_description

                cart_weight_oz+=float(product.weight_oz)

                cart_for_shipping_dict=dict(
                    product_name=product_name, 
                    product_cost=product_cost,
                    product_qty=product_qty,
                    product_weight=product.weight_oz,
                    product_shipping_desc=product_shipping_desc,
                )

                cart_for_shipping_calculations.append(cart_for_shipping_dict)


            ## Address logic    
            address_info=dict(
            street_address_line_1=session.address['street_address_line_1'],
            street_address_line_2=session.address['street_address_line_2'],
            municipality=session.address['municipality'],
            administrative_area=session.address['administrative_area'],
            postal_code=session.address['postal_code'],
            country=session.address['country'],
            )

        # now logged in or not we have the address that was chosen, the address info for the address that was chosen
        # and the cart info, and the combined weight of our package. 

        shipment=create_shipment(address_info, cart_for_shipping_calculations)

        # Generate list of sorted rates
        shipping_rates_for_sorting=[]
        for i in range(len(shipment.rates)):
            shipping_rates_for_sorting.append(float(shipment.rates[i].rate))
        shipping_rates_for_sorting.sort()


        shipping_grid_header_list=[':)', 'Carrier', 'Service', 'Cost']
        shipping_grid_table_row_LOL=[]

        # Build the shipping grid
        # I need to be able to sort the shipping rates based on the rate. 
        for j in range(len(shipping_rates_for_sorting)):


            for i in range(len(shipment.rates)):

                if shipping_rates_for_sorting[j]==float(shipment.rates[i].rate):

                    if shipment.rates[i].service==session.shipping_choice:

                    #radio_button=INPUT(_type='radio', _name='shipping', _value=shipment.rates[i].service)

                        radio_button=INPUT(_type='radio', _name='shipping', _checked='checked', _value=shipment.rates[i].service)

                    else:

                        radio_button=INPUT(_type='radio', _name='shipping', _value=shipment.rates[i].service)

                    shipping_grid_table_row_list=[
                        radio_button,
                        shipment.rates[i].carrier,
                        shipment.rates[i].service,
                        shipment.rates[i].rate,
                    ]

                    shipping_grid_table_row_LOL.append(shipping_grid_table_row_list)
                else:
                    pass

            
            
            shipping_grid=table_generation(shipping_grid_header_list, shipping_grid_table_row_LOL, 'shipping')

    except easypost.Error:

        shipping_grid=DIV('There was a problem generating the shipping costs.')

    except AttributeError:

        shipping_grid=DIV('There is nothing in your cart to ship')

    except TypeError:

        shipping_grid=DIV('There is no address to ship to')


#############################################################################################
###########----------------------------Card Logic--------------------------------############
#############################################################################################

    card_grid_header_list=[
        'Select One', 
        'Name', 
        'Last 4', 
        'Card Type',
        'Expiration Month',
        'Expiration Year', 
        #'Card ID', 
        'Delete'
    ]

    card_grid_table_row_LOL=[]

    if auth.is_logged_in():

        try:
            stripe_customer_token=db(db.stripe_customers.muses_id==auth.user_id).select()[0].stripe_id
            stripe_customer=stripe.Customer.retrieve(stripe_customer_token)
            stripe_cards=stripe_customer.cards.all()

            for i in range(len(stripe_cards['data'])):

                if stripe_cards['data'][i]['id']==db(db.stripe_customers.muses_id==auth.user_id).select().first().stripe_next_card_id:
                    radio_button=INPUT(_type='radio', _name='card', _value=stripe_cards['data'][i]['id'], _checked='checked')
                else:
                    radio_button=INPUT(_type='radio', _name='card', _value=stripe_cards['data'][i]['id'])

                delete_button=A('X', _href=URL('delete_item_from_db_card', vars=dict(customer_id=stripe_customer_token, card_id=stripe_cards['data'][i]['id'])), _class="btn btn-primary")

                card_grid_table_row_list=[
                    radio_button, 
                    stripe_cards['data'][i]['name'], 
                    stripe_cards['data'][i]['last4'], 
                    stripe_cards['data'][i]['brand'], 
                    stripe_cards['data'][i]['exp_month'], 
                    stripe_cards['data'][i]['exp_year'], 
                    #stripe_cards['data'][i]['id'], 
                    delete_button
                ]

                card_grid_table_row_LOL.append(card_grid_table_row_list)

            card_grid=table_generation(card_grid_header_list, card_grid_table_row_LOL, 'card')

        except IndexError:
            #the current user does not yet have a stripe customer token
            stripe_customer_token=None
            stripe_customer=None
            stripe_cards=None

            card_grid=DIV("You do not have any cards yet.")

        except AttributeError:
            #the current user does not yet have a stripe customer token
            stripe_customer_token=None
            stripe_customer=None
            stripe_cards=None

            card_grid=DIV("You do not have any cards yet, or there was a problem accessing your cards.")

        except stripe.error.APIConnectionError, stripe.error.APIError:
            #No access to the internet, probably
            stripe_customer_token=None
            stripe_customer=None
            stripe_cards=None

            card_grid=DIV("There was a problem trying to access Stripe")

    else:

        if not session.card_info:

            card_grid=DIV("You have not entered card information yet")

        else:

            radio_button=FORM(INPUT(_type='radio', _name='card', _value=session.card_info['card_id'], _checked='checked'), _action="")

            delete_button=A('X', _href=URL('delete_item_from_session_card'), _class="btn btn-primary")

            card_grid_table_row_list=[
                radio_button,
                session.card_info['name'],
                session.card_info['last4'],
                session.card_info['brand'],
                session.card_info['exp_month'],
                session.card_info['exp_year'],
                #session.card_info['card_id'],
                delete_button,
            ]

            card_grid_table_row_LOL.append(card_grid_table_row_list)

            card_grid=table_generation(card_grid_header_list, card_grid_table_row_LOL, 'address')

    return locals()



## The view right before they click to get charged and stuff. 

## In checkout is where I'm going to do most of the preparation for the purchase history
## db entry. My plan is to make a giant dictionary with all of the stuff, then pass
## it as a var or arg to pay. then try to charge the card,
## if it works, I'll have all the info I need, if not I can decide what to do about it. 
def checkout():

    if auth.is_logged_in():

#############################################################################################
###########----------------------------Cart Logic--------------------------------############
#############################################################################################

        ## Retrieve cart based on user id
        cart=db(db.muses_cart.user_id==auth.user_id).select()

        ## Initialize some vars
        cart_for_shipping_calculations=[]
        cart_weight_oz=cart_cost_USD=0
        cart_grid_row_LOL=[]
        cart_grid_header_list=["TN",'Product Name', 'Cost']

        ## for every item the user has in their cart
        for row in cart:

            ## Retrieve the product from the db
            product=db(db.product.id==row.product_id).select().first()

            ## Generate a dictionary for shipping information of the current product
            cart_for_shipping_dict=dict(
                product_name=product.product_name, 
                product_cost=product.cost_USD,
                product_qty=row.product_qty,
                product_weight=product.weight_oz,
                product_shipping_desc=product.shipping_description,
            )

            ## Append to list shipping info for all product in cart
            cart_for_shipping_calculations.append(cart_for_shipping_dict)

            ## Keeping track of cost and weight
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

        ## Generate the table, takes header info, row info, and then css class prefix
        cart_grid=table_generation(cart_grid_header_list, cart_grid_row_LOL, 'checkout_cart')

        ## Add total cart cost to the session for receipt info testing
        session.cart_cost_USD=cart_cost_USD


#############################################################################################
###########--------------------------Address Logic-------------------------------############
#############################################################################################

        address=db((db.addresses.user_id==auth.user_id)&(db.addresses.default_address==True)).select().first()

        address_grid_header_list=[
            'Street Line 1', 
            'Street Line 2', 
            'Municipality',
            'Administrative Area',
            'Postal Code',
            'Country',
        ]

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

        address_grid=table_generation(address_grid_header_list, [address_grid_row_list], 'checkout_address')
      


#############################################################################################
###########----------------------------Card Logic--------------------------------############
#############################################################################################

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
        card_grid_header_list=[
            'Name', 
            'Last 4', 
            'Card Type',
            'Expiration Month',
            'Expiration Year', 
        ]

        card_grid_row_list=[
            stripe_card['name'],
            stripe_card['last4'], 
            stripe_card['brand'], 
            stripe_card['exp_month'], 
            stripe_card['exp_year'],
        ]

        card_grid=table_generation(card_grid_header_list, [card_grid_row_list], 'checkout_card')

        # card_grid_table_row=DIV(_class='checkout_card_grid_table_row')
        # for i in range(len(card_grid_table_row_list)):
        #     card_grid_table_row.append(DIV(card_grid_table_row_list[i],_class="checkout_card_grid_table_cell checkout_card_grid_col checkout_card_grid_col_"+str(i+1)))
        # card_grid.append(card_grid_table_row)


    else:

#############################################################################################
###########----------------------------Cart Logic--------------------------------############
#############################################################################################

        cart_for_shipping_calculations=[]

        cart_grid_row_LOL=[]

        cart_weight_oz=cart_cost_USD=0

        cart_grid_header_list=["TN",'Product Name', 'Cost']

        for key, value in session.cart.iteritems():

            product=db(db.product.id==key).select().first()

            #product_name=product.product_name
            #product_cost=product.cost_USD
            #product_qty=value

            total_cost=float(product.cost_USD)*float(value)

            #product_weight=product.weight_oz
            #product_shipping_desc=product.shipping_description

            cart_for_shipping_dict=dict(
                product_name=product.product_name, 
                product_cost=product.cost_USD,
                product_qty=value,
                product_weight=product.weight_oz,
                product_shipping_desc=product.shipping_description,
            )

            cart_for_shipping_calculations.append(cart_for_shipping_dict)

            # Value is from session 
            cart_weight_oz+=float(product.weight_oz)*float(value)

            cart_cost_USD+=float(product.cost_USD)*float(value)


            if sqlite_tf:
                srcattr=URL('download',db(db.image.product_name==key).select().first().s3_url)
            else:
                srcattr=S3_BUCKET_PREFIX+str(db(db.image.product_name==key).select().first().s3_url)
            product_image_url=A(IMG(_src=srcattr), _href=URL('default','product',args=[key]))


            cart_grid_table_row_list=[product_image_url, product.product_name, total_cost]

            cart_grid_row_LOL.append(cart_grid_table_row_list)

            #cart_grid_table_row=DIV(_class="checkout_cart_grid_table_row")

            #for i in range(len(cart_grid_table_row_list)):

                #cart_grid_table_row.append(DIV(cart_grid_table_row_list[i],_class="checkout_cart_grid_table_cell checkout_cart_grid_col checkout_cart_grid_col_"+str(i+1)))

            #cart_grid.append(cart_grid_table_row)


        cart_grid=table_generation(cart_grid_header_list, cart_grid_row_LOL, 'checkout_cart')




#############################################################################################
###########--------------------------Address Logic-------------------------------############
#############################################################################################

        address_grid_header_list=[
            'Street Line 1', 
            'Street Line 2', 
            'Municipality',
            'Administrative Area',
            'Postal Code',
            'Country',
        ]

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
###########----------------------------Card Logic--------------------------------############
#############################################################################################

        card_grid_header_list=[
            'Name', 
            'Last 4', 
            'Card Type',
            'Expiration Month',
            'Expiration Year', 
        ]

        card_grid_row_list=[
            session.card_info['name'],
            session.card_info['last4'],
            session.card_info['brand'],
            session.card_info['exp_month'],
            session.card_info['exp_year'],
            #session.card_info['card_id'],
        ]


        card_grid=table_generation(card_grid_header_list, [card_grid_row_list], 'checkout_card')


#############################################################################################
###########--------------------------Shipping Logic------------------------------############
#############################################################################################

    shipment=create_shipment(address_dict, cart_for_shipping_calculations)

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
###########--------------------------Summary Logic-------------------------------############
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

    return locals()


def pay():

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


        ## Payment Fields
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

    #return locals()


def confirmation():

    ## This function has a problem with deleting a user
    ## And then someone reusing the same email when they sign up
    ## FIX IT. 

    #What confirmation thing are you trying to view?
    purchase_history_data_id=request.args[0]

##   try:
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



def sessions():
    session_db=db(db.web2py_session_3muses).select()[0].session_data
    return locals()



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

    left_sidebar_enabled=True
    right_sidebar_enabled=False

    return locals()



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
    return locals()



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
    return locals()

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

@auth.requires_membership('admin')
def set_order_number():

    session.session_purchase_history_data_id=request.args[0]

    return dict(message="Done!")



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
            message="Other error",
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


def default_address_2():
    session.test_var=request.vars.default_address_id
    if auth.is_logged_in():
        rows=db((db.addresses.user_id==auth.user_id)&(db.addresses.default_address==True)).select()
        for row in rows:
            row.default_choice=False
        db(db.addresses.id==request.vars.default_address_id).select()[0].default_address=True

    

    return locals()

def default_address():

    try:
        import easypost

        from_address=easypost.Address.create(
            company='threemusesglass',
            street1='308 Clearcreek Rd',
            city='Myrtle Beach',
            state='SC',
            zip='29572',
        )


        if auth.is_logged_in():
            addresses=db((db.addresses.user_id==auth.user_id)&(db.addresses.default_address==True)).select()
            for address_row in addresses:
                address_row.update(default_address=False)
                address_row.update_record()

            address = db(db.addresses.id==request.vars.default_address_id).select().first()
            #address = db(db.addresses.id==8).select().first()
            address.update(default_address=True)
            address.update_record()
        

            cart=db(db.muses_cart.user_id==auth.user_id).select()
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
                

            ## address logic
            #address=db((db.addresses.user_id==auth.user_id)&(db.addresses.default_address==True)).select().first()

            address_info=dict(
                street_address_line_1=address.street_address_line_1, 
                street_address_line_2=address.street_address_line_2, 
                municipality=address.municipality, 
                administrative_area=address.administrative_area, 
                postal_code=address.postal_code, 
                country=address.country,
            )

        else:
            ## Cart logic

            cart_for_shipping_calculations=[]
            cart_weight_lbs=0

            for key, value in session.cart.iteritems():
                product=db(db.product.id==key).select().first()
                product_name=product.product_name
                product_cost=product.cost_USD
                product_qty=value
                total_cost=float(product_cost)*float(product_qty)

                product_weight=product.weight_oz
                product_shipping_desc=product.shipping_description

                cart_weight_lbs+=product_weight

                cart_for_shipping_dict=dict(
                    product_name=product_name, 
                    product_cost=product_cost,
                    product_qty=product_qty,
                    product_weight=product_weight,
                    product_shipping_desc=product_shipping_desc,
                )

                cart_for_shipping_calculations.append(cart_for_shipping_dict)


            ## Address logic    
            address_info=dict(
            street_address_line_1=session.address['street_address_line_1'],
            street_address_line_2=session.address['street_address_line_2'],
            municipality=session.address['municipality'],
            administrative_area=session.address['administrative_area'],
            postal_code=session.address['postal_code'],
            country=session.address['country'],
            )

        # now logged in or not we have the address that was chosen, the address info for the address that was chosen
        # and the cart info, and the combined weight of our package. 


        parcel=easypost.Parcel.create(
            length=8,
            width=8,
            height=4,
            weight=cart_weight_oz,
        )

        if address_info['country']=='United States':

            to_address=easypost.Address.create(
                #name=address_info['card_name'],
                street1=address_info['street_address_line_1'],
                street2=address_info['street_address_line_2'],
                city=address_info['municipality'],
                state=address_info['administrative_area'],
                zip=address_info['postal_code'],
            )

            shipment=easypost.Shipment.create(
                to_address = to_address,
                from_address = from_address,
                parcel=parcel,
            )

        else:

            to_address=easypost.Address.create(
                #name=address_info['card_name'],
                street1=address_info['street_address_line_1'],
                street2=address_info['street_address_line_2'],
                city=address_info['municipality'],
                state=address_info['administrative_area'],
                zip=address_info['postal_code'],
                country=address_info['country'],
            )

            customs_items=[]
            for item in cart_for_shipping_calculations:
                customs_item=easypost.CustomsItem.create(
                    description=item['product_shipping_desc'],
                    quantity=item['product_qty'],
                    value=item['product_cost'],
                    #weight in oz converted to pounds
                    weight=(float(item['product_weight'])/16),
                    hs_tariff_number=700100,
                    origin_country='US',
                )
                customs_items.append(customs_item)

            if address_info['country']=='Canada':

                customs_info=easypost.CustomsInfo.create(
                    customs_items=customs_items,
                    contents_type='merchandise',
                    #contents_explanation=None,
                    restriction_type='none',
                    #restriction_comments=None,
                    customs_certify=True,
                    customs_signer='James McGlynn',
                    non_delivery_option='return',
                    eel_pfc='NOEEI 30.36',
                )

            else:

                customs_info=easypost.CustomsInfo.create(
                    customs_items=customs_items,
                    contents_type='merchandise',
                    #contents_explanation=None,
                    restriction_type='none',
                    #restriction_comments=None,
                    customs_certify=True,
                    customs_signer='James McGlynn',
                    non_delivery_option='return',
                    eel_pfc='NOEEI 30.37(a).',
                )

            shipment=easypost.Shipment.create(
                to_address=to_address,
                from_address=from_address,
                parcel=parcel,
                customs_info=customs_info,
            )

            #session.shipping_rates=shipment.rates
            shipping_rates_for_session={}
            for rate in shipment.rates:
                shipping_rates_for_session[rate.id]="test"
            session.shipping_rates=shipping_rates_for_session

        

        ## Hey this is new!
        ## Trying to get sorting to work for the ajax call
        shipping_rates_for_sorting=[]
        for i in range(len(shipment.rates)):
            shipping_rates_for_sorting.append(float(shipment.rates[i].rate))
        shipping_rates_for_sorting.sort()



        shipping_grid_container=DIV(_class='shipping_grid_container')
        shipping_grid_header_row=DIV(_class='shipping_grid_header_row')

        shipping_grid_header_list=['Radio', 'Carrier', 'Service', 'Cost']

        for i in range(len(shipping_grid_header_list)):
            shipping_grid_header_row.append(DIV(shipping_grid_header_list[i],_class="shipping_grid_header_cell shipping_grid_table_col_"+str(i+1)))
        shipping_grid_container.append(shipping_grid_header_row)


        #for j in range(len(shipping_rates_for_sorting)):

        for i in range(len(shipment.rates)):

            #if shipping_rates_for_sorting[j]==float(shipment.rates[i].rate):

            shipping_grid_table_row=DIV(_class='shipping_grid_table_row')

            shipping_grid_table_row.append(DIV(INPUT(_type='radio', _name='shipping', _value=shipment.rates[i].service),_class="shipping_grid_table_cell shipping_grid_table_col_1"))
            shipping_grid_table_row.append(DIV(shipment.rates[i].carrier,_class="shipping_grid_table_cell shipping_grid_table_col_2"))
            shipping_grid_table_row.append(DIV(shipment.rates[i].service,_class="shipping_grid_table_cell shipping_grid_table_col_3"))
            shipping_grid_table_row.append(DIV(shipment.rates[i].rate,_class="shipping_grid_table_cell shipping_grid_table_col_4"))
            

            shipping_grid_container.append(shipping_grid_table_row)

            #else:
                #pass

        return shipping_grid_container
        #return "test"
        #return dict(rate_list=rate_list)
        #return dict(rate_list=rate_list)

    except easypost.Error:
        shipping_grid_container=DIV('There was a problem generating the shipping costs')
        return shipping_grid_container

    except AttributeError:
        shipping_grid_container=DIV('There is nothing in your cart to ship')
        return shipping_grid_container

    except TypeError:
        shipping_grid_container=DIV('There is no address to ship to')
        return shipping_grid_container



def default_card():
    if auth.is_logged_in():
        row=db(db.stripe_customers.muses_id==auth.user_id).select().first()
        row.update(stripe_next_card_id=request.vars.stripe_next_card_id)
        row.update_record()

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

            grid_header_row.append(DIV(grid_header_list[i], _class=str(basename)+"_grid_header_cell grid_header_cell "+str(basename)+"_grid_col grid_col "+str(basename)+"_grid_col_"+str(i+1)))
        
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
    
    shipping_json=json.dumps(shipping_dict)

    return shipping_json




def create_shipment(to_address_dict, shipping_cart_LOD):
    import easypost

    package_weight_oz=0
    for item in shipping_cart_LOD:
        package_weight_oz+=float(item['product_weight'])*float(item['product_qty'])

    from_address=easypost.Address.create(
        company='threemusesglass',
        street1='308 Clearcreek Rd',
        city='Myrtle Beach',
        state='SC',
        zip='29572',
    )

    parcel=easypost.Parcel.create(
        #price really depends on weight so the dimensions are hard coded in here for now
        length=8,
        width=8,
        height=4,
        weight=package_weight_oz,
    )

    # If the package is shipping domestic
    if to_address_dict['country']=='United States':

        to_address=easypost.Address.create(
            #name = to_address_dict['name'],
            street1=to_address_dict['street_address_line_1'], 
            street2=to_address_dict['street_address_line_2'],
            city = to_address_dict['municipality'],
            state = to_address_dict['administrative_area'],
            zip = to_address_dict['postal_code'],
        )

        shipment=easypost.Shipment.create(
            to_address = to_address,
            from_address = from_address,
            parcel=parcel,
        )

    else:

        to_address=easypost.Address.create(
            #name = to_address_dict['name'],
            street1=to_address_dict['street_address_line_1'], 
            street2=to_address_dict['street_address_line_2'],
            city = to_address_dict['municipality'],
            state = to_address_dict['administrative_area'],
            zip = to_address_dict['postal_code'],
            country=to_address_dict['country'],
        )

        customs_items=[]
        for item in shipping_cart_LOD:
            customs_item=easypost.CustomsItem.create(
                description=item['product_shipping_desc'],
                quantity=item['product_qty'],
                value=item['product_cost'],
                weight=float(item['product_weight']),
                ## This is most generic tariff number for glass
                hs_tariff_number=700100,
                origin_country='US',
            )
            customs_items.append(customs_item)

        if to_address_dict['country']=='Canada':

            customs_info=easypost.CustomsInfo.create(
                customs_items=customs_items,
                contents_type='merchandise',
                #contents_explanation=None,
                restriction_type='none',
                #restriction_comments=None,
                customs_certify=True,
                customs_signer='James McGlynn',
                non_delivery_option='return',
                eel_pfc='NOEEI 30.36',
            )

        else:

            customs_info=easypost.CustomsInfo.create(
                customs_items=customs_items,
                contents_type='merchandise',
                #contents_explanation=None,
                restriction_type='none',
                #restriction_comments=None,
                customs_certify=True,
                customs_signer='James McGlynn',
                non_delivery_option='return',
                eel_pfc='NOEEI 30.37(a).',
            )

        shipment=easypost.Shipment.create(
            to_address=to_address,
            from_address=from_address,
            parcel=parcel,
            customs_info=customs_info,
        )

    return shipment


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


def paypal_test_checkout():
    import paypalrestsdk


    try:
        ## see if you can acces the heroku environment variables
        PAYPAL_CLIENT_ID=os.environ['PAYPAL_CLIENT_ID']
        PAYPAL_CLIENT_SECRET=os.environ['PAYPAL_CLIENT_SECRET']

    ## what exception exactly?
    except KeyError:

        # you aren't running on heroku
        # this will fail if it can't find the local keys. GOOD.
        with open('/home/wantsomechocolate/Code/API Info/api_keys.txt','r') as fh:
            text=fh.read()
            api_keys = ast.literal_eval(text)
        
        PAYPAL_CLIENT_ID=api_keys['paypal']['test']['PAYPAL_CLIENT_ID']
        PAYPAL_CLIENT_SECRET=api_keys['paypal']['test']['PAYPAL_CLIENT_SECRET']


    paypalrestsdk.configure({
        "mode": "sandbox", # sandbox or live
        "client_id": PAYPAL_CLIENT_ID,
        "client_secret": PAYPAL_CLIENT_SECRET })

    payment=paypalrestsdk.Payment({

        "intent": "sale",

        "payer": {
            "payment_method": "paypal",
            #"payer_info":{} Prefilled when payment method is paypal
            },

        "transactions": [

                {
                    "amount":{
                        "currency":"USD",
                        "total":"100.25",
                    },

                    "description":"Test transaction description",

                    "invoice_number":"A3H2JK89SZ",

                },

            ],
        })

    status=""
    if payment.create():
        status="Created successfully"
        session.paypal_response=payment
    else:
        status=payment.error



def paypal_webhooks():

    session.paypal_webhooks=True
    session.paypal_vars=request.vars
    session.paypal_args=request.args

    return dict()
