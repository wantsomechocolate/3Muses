# coding: utf8
    
## imports
import time
import os
from gluon import DAL




## Get db
cwd=os.getcwd()
tables_folder="applications/3muses/databases"
tables_folder_path=os.path.join(cwd,tables_folder)
db = DAL(os.environ['HEROKU_POSTGRESQL_SILVER_URL'], pool_size=10, folder=tables_folder, auto_import=True)

## Consts
SERVER_SESSION_RETIRE_HOURS=os.environ['SESSION_EXPIRY_HOURS']



## Get the current time and the cutoff_time
utc_seconds=time.time()+time.timezone
#cutoff_seconds=utc_seconds+SERVER_SESSION_RETIRE_HOURS*3600



server_session_rows=db(db.web2py_session_3muses.id>0).select()

for row in server_session_rows:
	session_time=row.modified_datetime
	session_seconds=time.mktime(session_time.timetuple())

	delta_seconds = utc_seconds - session_seconds
	delta_hours=delta_seconds

	if delta_hours>=24:
		db(db.web2py_session_3muses.id==row.id).delete()

print "Done!"


# >>> cwd=os.getcwd()

# Traceback (most recent call last):
#   File "<pyshell#0>", line 1, in <module>
#     cwd=os.getcwd()
# NameError: name 'os' is not defined
# >>> import time
# >>> import os
# >>> from gluon import DAL
# >>> cwd=os.getcwd()
# >>> tables_folder="applications/3muses/databases"
# >>> tables_folder_path=os.path.join(cwd,tables_folder)
# >>> db = DAL(os.environ['HEROKU_POSTGRESQL_SILVER_URL'], pool_size=10, folder=tables_folder, auto_import=True)

# Traceback (most recent call last):
#   File "<pyshell#7>", line 1, in <module>
#     db = DAL(os.environ['HEROKU_POSTGRESQL_SILVER_URL'], pool_size=10, folder=tables_folder, auto_import=True)
#   File "/home/wantsomechocolate/Code/3Muses/env/lib/python2.7/UserDict.py", line 23, in __getitem__
#     raise KeyError(key)
# KeyError: 'HEROKU_POSTGRESQL_SILVER_URL'
# >>> db = DAL('postgres://indwamrcfiuuyc:eAekhfWAE7JWK0VRtIjXf2RKUq@ec2-54-204-40-96.compute-1.amazonaws.com:5432/dcfrb6vgot8bp', pool_size=10, folder=tables_folder, auto_import=True)
# >>> SERVER_SESSION_RETIRE_HOURS=24
# >>> utc_seconds=time.time()+time.timezone
# >>> utc_seconds
# 1421099500.278764
# >>> time.ctime(utc_seconds)
# 'Mon Jan 12 16:51:40 2015'
# >>> cutoff_seconds=utc_time+SERVER_SESSION_RETIRE_HOURS*3600

# Traceback (most recent call last):
#   File "<pyshell#13>", line 1, in <module>
#     cutoff_seconds=utc_time+SERVER_SESSION_RETIRE_HOURS*3600
# NameError: name 'utc_time' is not defined
# >>> cutoff_seconds=utc_seconds+SERVER_SESSION_RETIRE_HOURS*3600
# >>> time.ctime(cutoff_seconds)
# 'Tue Jan 13 16:51:40 2015'
# >>> server_session_rows=db(db.web2py_session_3muses.id>0).select()
# >>> row=server_session_rows[0]
# >>> session_time=row.modified_datetime
# >>> session_time
# datetime.datetime(2015, 1, 12, 1, 57, 27)
# >>> session_seconds=time.mktime(session_time.timetuple())
# >>> session_seconds
# 1421045847.0
# >>> time.ctime(session_seconds)
# 'Mon Jan 12 01:57:27 2015'
# >>> delta_seconds = cutoff_seconds - session_seconds
# >>> delta_seconds/3600
# 38.90368854555819
# >>> delta_seconds = utc_seconds - session_seconds
# >>> delta_seconds/3600
14.903688545558188