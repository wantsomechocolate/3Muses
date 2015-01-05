## Readme

    ThreeMuses is project to create a website that will serve as an online showcase, store, sales tracker, etc, etc. 
    I would say just use etsy but there is a specific reason why that is not being done. 

## 3rd Party

3rd Party Services in use so far:

    Web2py      |   Web framework
    Heroku      |   Web hosting
    PostMark    |   Send transactional emails
    Stripe      |   Handle credit card information
    Postgresql  |   Database
    AWS(S3)     |   Image storage

3rd Party services yet to be integrated:

    Paypal      |   Because paypal


Notes:

    Procfile text that might schedule session cleanup

    web: python web2py.py -a 'admin' -i 0.0.0.0 -p $PORT
    web: nohup python web2py.py -a 'admin' -i 0.0.0.0 -p $PORT -S app -M -R scripts/sessions2trash.py &

    This worked locally to get the session cleaner to work
    I didn't have to include the app name, probably because it is the default/main app

    nohup python web2py.py -a asdfasdf -M -R scripts/sessions2trash.py &

    But I still have no idea how to deploy this (will have to change the Procfile to something that works)
    and now I have no clue how to get this working with other scheduled tasks. 
