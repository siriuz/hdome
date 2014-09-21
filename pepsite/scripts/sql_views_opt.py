import os
import sys
import datetime
from django.utils.timezone import utc
from django.db.models import Q
from django.db.models import *
from django.db import IntegrityError, transaction

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


from django.db import connection
import time

def create_views_better():
    t0 = time.time()
    cursor = connection.cursor()
    sql1 = 'SELECT COUNT(*) FROM \
    pepsite_experiment t1 \
    INNER JOIN pepsite_experiment_proteins t2 \
    ON (t1.id = t2.experiment_id) \
    INNER JOIN pepsite_peptoprot t3 \
    ON (t3.protein_id = t2.protein_id) \
    '
    cursor.execute( sql1)
    print cursor.fetchall()
    t1 = time.time()
    tt = t1 -t0
    print 'time taken %f seconds' % tt


if __name__ == '__main__':
    create_views_better()

