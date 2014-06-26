import os
import sys

CURDIR = os.path.dirname( os.path.abspath( __file__ ) )
sys.path.append( CURDIR + '/../..' )

PROJ_NAME = 'hdome'

os.environ[ 'DJANGO_SETTINGS_MODULE' ] = '%s.settings' %( PROJ_NAME )

import django #required
django.setup() #required
from pepsite.make_searches import *
from django.db.models import Q
from pepsite.queries_basic import QueryQuick
import pickle
import pepsite.uploaders
from pepsite.models import *
import pprint

if __name__ == '__main__':
    user = User.objects.get( username = 'admin' )
    peptides = Peptide.objects.filter( sequence = 'TPLLMQALPMGALPQ' ) # this needs to be a queryset
    expt = Experiment.objects.get( title = 'ptm eg 03' )
    ides = IdEstimate.objects.filter( peptide = peptides[0], ion__experiments = expt )
    s1 = ExptArrayAssemble()
    pprint.pprint( s1.get_peptide_array_expt_restricted(  ides, peptides, expt, user) )
