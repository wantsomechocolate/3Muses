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