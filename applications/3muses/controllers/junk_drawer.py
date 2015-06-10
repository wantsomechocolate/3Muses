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















## Leftover from default.py
def checkout_1():


    from aux import retrieve_cart_contents


#############################################################################################
###########--------------------------Initial Logic-------------------------------############
#############################################################################################

    ## If someone tries to mess with the URL in the browser by going to 
    ## cart/arg, It will reload the page without the arg
    if request.args(0) is not None:
        redirect(URL('checkout'))
    else:
        pass

    ## If you try to visit this page while you are not logged in, you get logged in as a handicapped user. 
    ## but the nav options don't change. 
    if auth.is_logged_in():
        pass
    else:
        create_gimp_user()

# #############################################################################################
# ###########----------------------------Cart Logic--------------------------------############
# #############################################################################################

#     cart_information_LOD=[]
#     cart_information=dict(error=False,error_message=None,cart_information_LOD=cart_information_LOD)

#     ## Retrieve the current items from the users cart)
#     ## There is no check here to not include items that are sold out or no
#     ## longer active, That happens later.

#     #cart_db=db(db.muses_cart.user_id==auth.user_id).select()

#     cart_db=retrieve_cart_contents(auth,db)

#     ## If cart turns out to be empty, set cart_grid so the view can have
#     ## something to display. but now cart_grid_table_row_LOL will be empty,
#     ## which should disallow the user from pressing the checkout button. 
#     if not cart_db:

#         cart_information['error']=True
#         cart_information['error_message']="You have not yet added anything to your cart"
#         cart_is_empty=True

#     ## If the cart is not empty
#     else:
        
#         cart_is_empty=False
#         ## For each product in the cart
#         for row in cart_db:

#             ## Retreive product info from the db
#             product=db(db.product.id==row.product_id).select().first()

#             image=db(db.image.product_name==row.product_id).select().first()

#             if not image:
#                 srcattr=URL('static','img/no_images.png')
#             else:

#                 ## If using a local db get the product image locally
#                 if sqlite_tf:
#                     # # image=db(db.image.product_name==row.product_id).select().first()
#                     # if len(images)==0:
#                     #     srcattr=URL('static','img/no_images.png')
#                     # else:
#                     srcattr=URL('download', image.s3_url)
#                     # print ("sqlite")
                
#                 ## For the more common case, get the image from aws s3
#                 else:
#                     # srcattr=S3_BUCKET_PREFIX+str(db(db.image.product_name==row.product_id).select().first().s3_url)
#                     srcattr=S3_BUCKET_PREFIX+str(image.s3_url)

#             ## Create the product_image_url
#             product_image_url=A(IMG(_src=srcattr, _class='img-thumbnail cart-view-cart-tn'), _href=URL('default','product',args=[row.product_id]))

#             ## Create a delete button for the item
#             delete_button=A('X', _href=URL('delete_item_from_cart', vars=dict(pri_key=row.id,redirect_url=URL('cart'))), _class="btn btn-danger cart-view-cart-item-remove")

#             ## Populate a list with the current product info
#             cart_grid_table_row_list=[
#                 product_image_url, 
#                 product.product_name, 
#                 product.cost_USD, 
#                 #row.product_qty, This was used when qty could be over 1,
#                 delete_button
#             ]

#             cart_item_dict=dict(
#                 product_image_url=product_image_url,
#                 product_name=product.product_name,
#                 product_cost=product.cost_USD,
#                 product_delete_button=delete_button,
#                 product_active=product.is_active,
#                 )

#             cart_information_LOD.append(cart_item_dict)

#             ## If the item is no longer active, remove it from the cart.
#             if not product.is_active:
#                 db(db.muses_cart.product_id==product.id).delete()



# #############################################################################################
# ###########-----------------Address Logic (User and Non User)--------------------############
# #############################################################################################

#     address_information_LOD=[]
#     address_information=dict(error=False,error_message=None,address_information_LOD=address_information_LOD)

#     address_list=db(db.addresses.user_id==auth.user_id).select(orderby=db.addresses.street_address_line_1)

#     if not address_list:

#         address_list_is_empty=True
#         address_information['error']=True
#         address_information['error_message']="Please add an address to continue with your purchase"

#     else:

#         address_list_is_empty=False

#         for j in range(len(address_list)):

#             address_information_LOD.append(dict(
#                 first_name=address_list[j].first_name,
#                 last_name=address_list[j].last_name,
#                 street_address_line_1=address_list[j].street_address_line_1, 
#                 street_address_line_2=address_list[j].street_address_line_2, 
#                 municipality=address_list[j].municipality, 
#                 administrative_area=address_list[j].administrative_area, 
#                 postal_code=address_list[j].postal_code, 
#                 country=address_list[j].country,
#                 id=address_list[j].id,
#                 default_address=address_list[j].default_address,
#             ))


# #############################################################################################
# ###########---------------Shipping Logic (User and Non User)---------------------############
# #############################################################################################

#     if cart_is_empty:
#         shipping_information=dict(error=True, error_message="Please add something to your cart to continue", shipping_options_LOD=[])
#     elif address_list_is_empty:
#         shipping_information=dict(error=True, error_message="Please add an address to continue", shipping_options_LOD=[])
#     else:
#         shipping_information=dict(error=True, error_message="Generating shipping costs", shipping_options_LOD=[])


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
                card_id=stripe_cards['data'][i]['id'], 
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

        # cart_information=cart_information,

        # address_information=address_information,

        # shipping_information=shipping_information,

        card_information=card_information,

        )














def cart_backup():


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
        create_gimp_user()

#############################################################################################
###########----------------------------Cart Logic--------------------------------############
#############################################################################################

    cart_information_LOD=[]
    cart_information=dict(error=False,error_message=None,cart_information_LOD=cart_information_LOD)

    ## Retrieve the current items from the users cart)
    ## There is no check here to not include items that are sold out or no
    ## longer active, That happens later.

    #cart_db=db(db.muses_cart.user_id==auth.user_id).select()

    cart_db=retrieve_cart_contents(auth,db)

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
            delete_button=A('X', _href=URL('delete_item_from_cart', vars=dict(pri_key=row.id,redirect_url=URL('cart'))), _class="btn btn-danger cart-view-cart-item-remove")

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


















    
def cart_only():

#############################################################################################
###########--------------------------Initial Logic-------------------------------############
#############################################################################################

    ## If someone tries to mess with the URL in the browser by going to 
    ## cart/arg, It will reload the page without the arg
    if request.args(0) is not None:
        redirect(URL('cart_only'))
    else:
        pass

    ## If you try to visit this page while you are not logged in, you get logged in as a handicapped user. 
    ## but the nav option don't change. 
    if auth.is_logged_in():
        pass
    else:
        create_gimp_user()


    # print (request.env.web2py_original_uri)

#############################################################################################
###########----------------------------Cart Logic--------------------------------############
#############################################################################################

    current_cart_cost=0

    cart_information_LOD=[]
    cart_information=dict(error=False,error_message=None,cart_information_LOD=cart_information_LOD)

    ## Retrieve the current items from the users cart)
    ## There is no check here to not include items that are sold out or no
    ## longer active, That happens later.
    #cart_db=db(db.muses_cart.user_id==auth.user_id).select()

    cart_db=retrieve_cart_contents(auth,db)

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
            delete_button=A('X', _href=URL('delete_item_from_cart', vars=dict(pri_key=row.id,redirect_url=URL('cart'))), _class="btn btn-danger cart-view-cart-item-remove")

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
            else:
                current_cart_cost+=product.cost_USD

        session.current_cart_cost=current_cart_cost
#############################################################################################
###########--------------------------------Final---------------------------------############
#############################################################################################

    return dict(

        cart_information=cart_information,

        )















def cart_sample():

    from aux import retrieve_cart_contents

#############################################################################################
###########--------------------------Initial Logic-------------------------------############
#############################################################################################

    ## If someone tries to mess with the URL in the browser by going to 
    ## cart/arg, It will reload the page without the arg
    if request.args(0) is not None:
        redirect(URL('cart_only'))
    else:
        pass

    ## If you try to visit this page while you are not logged in, you get logged in as a handicapped user. 
    ## but the nav option don't change. 
    if auth.is_logged_in():
        pass
    else:
        create_gimp_user()


    # print (request.env.web2py_original_uri)

#############################################################################################
###########----------------------------Cart Logic--------------------------------############
#############################################################################################

    cart_information_LOD=[]
    cart_information=dict(error=False,error_message=None,cart_information_LOD=cart_information_LOD)

    ## Retrieve the current items from the users cart)
    ## There is no check here to not include items that are sold out or no
    ## longer active, That happens later.
    #cart_db=db(db.muses_cart.user_id==auth.user_id).select()

    cart_db=retrieve_cart_contents(auth,db)

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
            delete_button=A('X', _href=URL('delete_item_from_cart', vars=dict(pri_key=row.id,redirect_url=URL('cart'))), _class="btn btn-danger cart-view-cart-item-remove")

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
###########--------------------------------Final---------------------------------############
#############################################################################################

    return dict(

        cart_information=cart_information,

        )





def pay():
    ### This function is for paying with stripe only

    ## The purpose of this function is to populate the database table purchase history with all 
    ## of the info about the purchase and send an email using postmark. 
    ## Presenting the confirmation screen is done later using the database
    import json
    from aux import create_purchase_history_dict
    from aux import generate_confirmation_email_receipt_context
    from aux import retrieve_cart_contents

    ## Get customer_id from stripe data in db. They should have one, if they don't at this point
    ## something went wrong.
    customer_id=db(db.stripe_customers.muses_id==auth.user_id).select().first().stripe_id

    ## From Session ##
    total_cost_USD=session.summary_information['information_LOD'][0]['total_cost_USD']

    ## To try and charge the card with the stripe id (defualt card should already be set within stripe)
    ## Otherwise something else went wrong
    ## TODO: Add description back in?
    ## TODO: What if the charge fails or the user cancels?
    charge=stripe.Charge.create(
        amount=int(float(total_cost_USD)*100),
        currency='usd',
        customer=customer_id,
        #description='test purchase',
    )


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


    purchase_history_dict=create_purchase_history_dict(

        ## This is probably really dangerous
        session_data=response,

        user_data=user_data,

        address_data=default_address,

        ## Consider putting shipping response in session and passing them here?
        # shipping_data=rates,
        
        payment_service='stripe',

        payment_data=charge,

        summary_data=session.summary_information,

        )



    #################################################
    ########----PUT PURCHASE INFO IN THE DB------####
    #################################################

    ## place data in the database. 
    purchase_history_data_id=db.purchase_history_data.bulk_insert([purchase_history_dict])[0]

    ## Add id of most recent purchase to the session for viewing purposes.
    session.session_purchase_history_data_id=purchase_history_data_id


    #################################################
    ########----PUT PRODUCT INFO IN THE DB-------####
    #################################################

    ## For every item in the cart, insert a record with the id of the purchase history, the product id and the qty.
    purchase_history_products_LOD=[]

    #cart=db(db.muses_cart.user_id==auth.user_id).select()

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

    ## Actually put everything in the db
    purchase_history_products_ids=db.purchase_history_products.bulk_insert(purchase_history_products_LOD)


    #################################################
    ########----SENDING THE CONFIRMATION EMAIL---####
    #################################################

    receipt_context=generate_confirmation_email_receipt_context(
        muses_email_address=user_data.email, 
        purchase_history_data_row=db(db.purchase_history_data.id==purchase_history_data_id).select().first(),
        purchase_history_products_rows=db(db.purchase_history_products.purchase_history_data_id==purchase_history_data_id).select(),
    )

    receipt_message_html = response.render('default/receipt.html', receipt_context)



    email_address_query=db(db.email_correspondence.user_id==auth.user_id).select(db.email_correspondence.email).first()
    email_address=list(email_address_query.as_dict().values())[0]

    from postmark import PMMail
    message = PMMail(api_key=POSTMARK_API_KEY,
        subject="Order Confirmation",
        sender="confirmation@threemuses.glass",
        # to=user_data.email,
        to=email_address,
        #html_body=final_div_html,
        html_body=receipt_message_html,
        tag="confirmation")
    message.send()


    #################################################
    ########----SEND TO CONFIMATION SCREEN-------####
    #################################################
    redirect(URL('confirmation', args=(purchase_history_data_id)))




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






## functions that come with the welcome app ##
# def user():
    
#     """
#     exposes:
#     http://..../[app]/default/user/login
#     http://..../[app]/default/user/logout
#     http://..../[app]/default/user/register
#     http://..../[app]/default/user/profile
#     http://..../[app]/default/user/retrieve_password
#     http://..../[app]/default/user/change_password
#     http://..../[app]/default/user/manage_users (requires membership in
#     use @auth.requires_login()
#         @auth.requires_membership('group name')
#         @auth.requires_permission('read','table name',record_id)
#     to decorate functions that need access control
#     """

#     ## This is what I had in the user.html doc to do the purchase history
#     # <h2>Purchase History</h2>
#     # {{purchase_history=db(db.purchase_history_data.muses_id==auth.user_id).select()}}
#     # {{for purchase in purchase_history:}}
#     #     <h3>Purchase Details</h3>
#     #     {{=purchase}}
#     #     <h3>Purchase Products</h3>
#     #     {{purchase_history_products=db(db.purchase_history_products.purchase_history_data_id==purchase.id).select()}}
#     #     {{=purchase_history_products}}

#     # {{pass}}


#     #purchase_history=db(db.purchase_history_data.muses_id==auth.user_id).select()
#     #for purchase in purchase_history:
#         #purchase_history_products=db(db.purchase_history_products.purchase_history_data_id==purchase.id).select()

#     ## create a table with a row for each purchase and a link to each purchases' corresponding products.
#     ## Have the ability to be able to look at all products. 

#     ## Use custom tables or web2py tables for this? With web2py tables user can export
#     ## filter, sort. I'm going to try using web2py tables first. 

#     #grid=SQLFORM.smartgrid(db.purchase_history_data, linked_tables=['purchase_history_products'])

#     #print "anything"

#     # user_page=request.args[0]
#     #2if 
                                                                                                                                                                                                    

#     return dict(form=auth())


# def mylogin(): 
#     return dict(form=auth.login())


# def myregister(): return dict(form=auth.register())
# def myprofile(): return dict(form=auth.profile())


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


# def bootstrap_nav():
#     return dict()

# def shopping_cart():
#     return dict()



# def new_hotness():

#     if request.args(0) is not None:

#         redirect(URL('categories'))

#     else:

#         pass

#     category_rows=db(db.categories.is_active==True).select(orderby=db.categories.display_order)

#     return dict(
#         category_rows=category_rows,
#         )



# def drop_muses_cart_table():

#     db.muses_cart.drop()

#     return dict("The cart table is has been did dropped. ")


# def stripe():
#     return dict()

# def stripe_index():

#     return dict(key=stripe_keys['publishable_key'])

# def stripe_charge():

#     amount = 500

#     customer = stripe.Customer.create(
#         email='wantsomechocolate@gmail.com',
#         card=request.form['stripeToken']
#     )

#     charge = stripe.Charge.create(
#         customer=customer.id,
#         amount=amount,
#         currency='usd',
#         description='Flask Charge'
#     )

#     return dict(amount=amount)


# def web_stripe():
#     from gluon.contrib.stripe import StripeForm

#     form = StripeForm(
#         pk=stripe_keys['publishable_key'],
#         sk=stripe_keys['secret_key'],
#         amount=150, # $1.5 (amount is in cents)
#         description="Nothing").process()
#     if form.accepted:
#         payment_id = form.response['id']
#         redirect(URL('thank_you'))
#     elif form.errors:
#         redirect(URL('pay_error'))
#     return dict(form=form)


# def checkout_stripe():
#     return dict(pk=stripe_keys['publishable_key'])

# def checkout_stripe_2():

#     # Set your secret key: remember to change this to your live secret key in production
#     # See your keys here https://dashboard.stripe.com/account/apikeys
#     import stripe
#     import os
#     stripe.api_key = stripe_keys['secret_key']

#     # Get the credit card details submitted by the form
#     token = request.vars['stripeToken']

#     # Create the charge on Stripe's servers - this will charge the user's card
#     try:
#       charge = stripe.Charge.create(
#           amount=1000, # amount in cents, again
#           currency="usd",
#           source=token,
#           description="Example charge"
#       )

#       redirect(URL('stripe_test','default','success'))

#     except stripe.error.CardError, e:
#       # The card has been declined
#       redirect(URL('stripe_test','default','fail'))