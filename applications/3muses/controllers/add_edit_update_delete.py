def cart():

#############################################################################################
###########----------------------------Cart Logic--------------------------------############
#############################################################################################

    cart_grid_header_list=["Cart","Item","Cost","Qty", "Delete"]

    cart_grid_table_row_LOL=[]

    if auth.is_logged_in():

        cart_db=db(db.muses_cart.user_id==auth.user_id).select()

        if not cart_db:

            cart_grid=DIV("You have not yet added anything to your cart")

        else:
        
            for row in cart_db:

                product=db(db.product.id==row.product_id).select().first()

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
                    row.product_qty, 
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
                    value, 
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

        shipping_grid_header_list=[':)', 'Carrier', 'Service', 'Cost']
        shipping_grid_table_row_LOL=[]

        # Build the shipping grid
        for i in range(len(shipment.rates)):

            radio_button=INPUT(_type='radio', _name='shipping', _value=shipment.rates[i].service)

            shipping_grid_table_row_list=[
                radio_button,
                shipment.rates[i].carrier,
                shipment.rates[i].service,
                shipment.rates[i].rate,
            ]

            shipping_grid_table_row_LOL.append(shipping_grid_table_row_list)
            
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
        'Card ID', 
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
                    stripe_cards['data'][i]['id'], 
                    delete_button
                ]


                card_grid_table_row_LOL.append(card_grid_table_row_list)

            card_grid=table_generation(card_grid_header_list, card_grid_table_row_LOL, 'address')

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
                session.card_info['card_id'],
                delete_button,
            ]

            card_grid_table_row_LOL.append(card_grid_table_row_list)

            card_grid=table_generation(card_grid_header_list, card_grid_table_row_LOL, 'address')

    return locals()








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