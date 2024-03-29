# -*- coding: utf-8 -*-
import os,ast
#########################################################################
## This scaffolding model mak8es your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

from gluon.contrib.heroku import get_db

sqlite_tf=True


if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB


    ## If you are running remotely
    #if os.environ['ON_HEROKU']=='TRUE':
    if False:
        ## set sqlite_tf to false to avoid problems in other files
        sqlite_tf=False

        ## connect to db
        #db = DAL(os.environ['DATABASE_URL'], pool_size=10)
        #db = get_db(name=os.environ['DATABASE_URL'], pool_size=10)
        db = get_db(name='DATABASE_URL', pool_size=10, migrate=True, fake_migrate_all=True)


    ## You are running locally
    else:

        ## If you set sqlite_tf to true, than use it
        if sqlite_tf:
            db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])

        ## if not, connect to remote db
        else:
            #db = DAL(os.environ['DATABASE_URL'], pool_size=10)
            db = get_db(name='DATABASE_URL', pool_size=10)


        # ## a Key error means you are not running on heroku (hopefully), so try to get the db location locally
        # except (KeyError):

        #     if sqlite_tf==False:

        #         ## try to access the remote database locally AND connect to it
        #         try:
        #             with open('/home/wantsomechocolate/Code/API Info/database_urls.txt','r') as fh:
        #                 text=fh.read()
        #                 database_urls = ast.literal_eval(text)

        #             db = DAL(database_urls['heroku']['3muses']['DATABASE_URL'], pool_size=10)

        #         ## if you aren't running on heroku AND the database url was found locally but couldn't
        #         ## be connected to, connect using sqlite database. 
        #         except RuntimeError, IOError:
            
        #             db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])

        #     else:
        #         db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])

    #except:
     #   db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])

    #db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
    #db = DAL(os.environ['DATABASE_URL'], pool_size=10)
    session.connect(request, response, db, masterapp=None)


else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)


## configure email
mail = auth.settings.mailer
#mail.settings.server = 'smtp.postmarkapp.com:587'
# mail.settings.server = 'logging' or 'smtp.postmarkapp.com:587'
mail.settings.server = 'logging'
mail.settings.sender = 'admin@threemuses.glass'
# mail.settings.login = os.environ['POSTMARK_API_KEY']+':'+os.environ['POSTMARK_API_KEY']
mail.settings.login = 'username:password'

auth.messages.reset_password = 'Click on the link %s/%%(key)s to reset your password' % URL('reset_password', scheme=True)


## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## Other Auth Settings
auth.settings.login_url = URL('login')
auth.settings.logged_url = URL('profile')
auth.settings.remember_me_form = False
auth.settings.profile_onaccept = []
auth.settings.reset_password_onaccept = []
auth.messages.profile_updated = 'Profile updated'
auth.messages.invalid_reset_password = 'Invalid or expired link'

#auth.messages.reset_password_subject = 'Password reset'
#auth.settings.registration_requires_verification = True

auth.settings.profile_next = URL('profile')
auth.settings.register_next = URL('login')
auth.settings.request_reset_password_next = URL('login')
auth.settings.reset_password_next = URL('login')
auth.settings.verify_email_next = URL('login')

#auth.settings.login_next = URL('index')
#auth.settings.logout_next = URL('index')
#auth.settings.retrieve_username_next = URL('index')
#auth.settings.retrieve_password_next = URL('index')
#auth.settings.change_password_next = URL('index')



## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)


