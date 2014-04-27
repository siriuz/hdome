import os
import sys

CURDIR = os.path.dirname( os.path.abspath( __file__ ) )
sys.path.append( CURDIR + '/../..' )

PROJ_NAME = 'hdome'

os.environ[ 'DJANGO_SETTINGS_MODULE' ] = '%s.settings' %( PROJ_NAME )

import django #required
django.setup() #required

from django.db.models import Q
from pepsite.queries_basic import QueryQuick

from pepsite.models import *
from pepsite.make_searches import *

if __name__ == '__main__':
    s1 = AlleleSearch()
    print s1.get_experiments_basic( 'DQ6' )
