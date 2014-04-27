
import os
import sys

CURDIR = os.path.dirname( os.path.abspath( __file__ ) )
sys.path.append( CURDIR + '/../..' )

PROJ_NAME = 'hdome'

os.environ[ 'DJANGO_SETTINGS_MODULE' ] = '%s.settings' %( PROJ_NAME )

import django #required
django.setup() #required

from pepsite.queries_basic import QueryQuick

from pepsite.models import *

	
if __name__ == '__main__':
    qq1 = QueryQuick()
    qq1.add_q( ion__charge_state = 6 )
    qq1.add_q( ion__experiments__title = 'Trial Expt 9031 DP'  )
    a1 = qq1.quick_query_and_only() 
    #print len(  a1 )
    #print a1
    #print ( a1[0].proteins )
    #print qq1.get_peptide_output( a1, 'Trial Expt 9031 DP' )
    #print Ptm.objects.all()
    clret = qq1.retrieve_from_cell_line( '9031', 'anti-DR' )
    #print clret[0], len(clret[1]), len(clret[2]), len(clret[3] ), len( clret[4]), len(clret[5])
    qq1.report_from_cell_line( '9031', 'anti-DR' )
