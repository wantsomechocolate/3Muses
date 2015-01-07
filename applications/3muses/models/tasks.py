# coding: utf8

def stripe_remove_session_users():
    
    ## imports
    import time
    import stripe

    ## Consts
    STRIPE_SESSION_RETIRE_HOURS=(1/10.0)

    ## API KEY
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


    ## set cursor_id to get through the while loop the first time
    cursor_id=""

    ## set has_more to True to enter the while loop initially
    has_more=True

    stripe_list_of_deleted_customers=[]
    stripe_list_of_deleted_customers.append("Test")

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
                    stripe_list_of_deleted_customers.append(stripe_customer)

                else:
                    pass
            else:
                pass


        ## This will be false if no more customers to retrieve. True if there are. 
        has_more=stripe_customer_list['has_more']

    return stripe_list_of_deleted_customers

from gluon.scheduler import Scheduler
Scheduler(db, dict(task1=stripe_remove_session_users))
