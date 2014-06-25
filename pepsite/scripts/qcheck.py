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
import pickle
import pepsite.uploaders
from pepsite.models import *

if __name__ == '__main__':
    if sys.argv[1] == 'upload':
        with open( '/home/rimmer/praccie/hdome/background/trial_ul_01.pickle', 'rb') as f:
            ul = pickle.load( f )
        ul.get_protein_metadata(  )
        try:
            a1 = Lodgement.objects.get( title = ul.lodgement_title )
            a1.delete()
        except:
            pass
        print '\n\nuniprot updates fetched'
        ul.prepare_upload_simple( )
        print '\n\nboilerplate saved'
        ul.upload_simple()
        print '\n\ndata saved'
    elif sys.argv[1] == 'check':
        print 'ok'
