import os
import sys
import datetime
from django.utils.timezone import utc
from django.db.models import Q
from db_ops import dbtools

PROJ_NAME = 'hdome'
APP_NAME = 'pepsite'

CURDIR = os.path.dirname( os.path.abspath( __file__ ) )

#print CURDIR

sys.path.append( CURDIR + '/../..' ) # gotta hit settings.py for site


os.environ[ 'DJANGO_SETTINGS_MODULE' ] = '%s.settings' %( PROJ_NAME )

import django #required
django.setup() #required

from pepsite.models import *
from django.contrib.auth.models import User, Group, Permission
from guardian.shortcuts import assign_perm

       



        

            


if __name__ == '__main__':
    dbt = dbtools.DBTools()
    u3 = dbt.get_model_object( User, username = 'kfed' )
    u3.save()
    g1 = dbt.get_model_object( Group, name = 'Purcell Lab' )
    g1.save()
    g1.has_perm( 'pepsite.view_dataset' )
    ds1 = Dataset.objects.all()[0]
    print u3
    print u3.has_perm( 'pepsite.view_dataset', ds1)
    assign_perm('view_dataset', u3, ds1)
    print u3.has_perm( 'pepsite.view_dataset', ds1)
    u3 = dbt.get_model_object( User, username = 'kfed' )
    print u3.has_perm( 'pepsite.view_dataset', ds1)
    u4 = dbt.get_model_object( User, username = 'k' )





        
        

