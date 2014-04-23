
import os
import sys

CURDIR = os.path.dirname( os.path.abspath( __file__ ) )
sys.path.append( CURDIR + '/../..' )

PROJ_NAME = 'hdome'

os.environ[ 'DJANGO_SETTINGS_MODULE' ] = '%s.settings' %( PROJ_NAME )

import django #required
django.setup() #required

from pepsite.queries_basic import QueryQuick


	
if __name__ == '__main__':
    qq1 = QueryQuick()
    qq1.add_q( ion__charge_state = 6 )
    qq1.add_q( ion__experiments__title = 'Trial Expt 9031 DP'  )
    a1 = qq1.quick_query_and_only() 
    print len(  a1 )
    print a1
    #print ( a1[0].proteins )
    print qq1.get_peptide_output( a1 )

