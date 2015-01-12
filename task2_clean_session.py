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
SERVER_SESSION_RETIRE_HOURS=24



## Get the current time and the cutoff_time
utc_seconds=time.time()+time.timezone
cutoff_seconds=utc_time+SERVER_SESSION_RETIRE_HOURS*3600



server_session_rows=db(db.web2py_session_3muses.id>0).select()

for row in server_session_rows:
	session_time=row.modified_datetime
	session_seconds=time.mktime(session_time.timetuple())

	delta_seconds = cutoff_seconds - session_seconds

	if delta_seconds<=0:
		db(db.web2py_session_3muses.id==row.id).delete()

print "Done!"