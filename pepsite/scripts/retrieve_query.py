import os
import sys
import datetime
from django.utils.timezone import utc
from django.db.models import Q
from django.db.models import *
from django.db import IntegrityError, transaction
from django.db import connection

PROJ_NAME = 'hdome'
APP_NAME = 'pepsite'

CURDIR = os.path.dirname( os.path.abspath( __file__ ) )

#print CURDIR

sys.path.append( CURDIR + '/../..' ) # gotta hit settings.py for site

os.environ[ 'DJANGO_SETTINGS_MODULE' ] = '%s.settings' %( PROJ_NAME )

import django #required
django.setup() #required

from django.contrib.auth.models import User
from pepsite.models import *
from pepsite import dbtools
import pepsite.uploaders
import time


BGFILE = os.path.join( CURDIR, '../../background/newdata_with_files_correct.csv' )


def dq(cursor):
    ds = 'SELECT * FROM pepsite_idestimate t1 \
        LEFT JOIN pepsite_ion t2 ON \
        (t1.ion_id = t2.id) \
        LIMIT 6'
    cursor.execute(ds)
    return cursor.fetchall()

if __name__=='__main__':
    cursor = connection.cursor()
    a = dq(cursor)
    print a[:3]
