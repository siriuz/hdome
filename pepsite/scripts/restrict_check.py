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
from django.db.models import Count

if __name__ == '__main__':
    user = User.objects.get( username = 'admin' )
    peptides = Peptide.objects.filter( sequence = 'TPLLMQALPMGALPQ' ) # this needs to be a queryset
    expt = Experiment.objects.get( title = 'doctored 01' )
    ides = IdEstimate.objects.filter( peptide = peptides[0], ion__experiment = expt )
    for ide in ides:
        print ide, ide.id, [ b.id for b in ide.ptms.all()]
    s1 = ExptArrayAssemble()
    newlist =  s1.get_peptide_array_expt_restricted(  ides, peptides, expt, user) 
    for x in newlist:
        print x['ide'], x['ide'].id, [ b.id for b in x['ptms'] ]
    print IdEstimate.objects.get( id = 400 ).ptms.all()
    qlist = [ Q( ptms__id = 5 ), Q( ptms__id = 12 ), Q( peptide = peptides[0]), Q(ion__experiment = expt ) ]
    print IdEstimate.objects.filter( *qlist ).distinct()
    print IdEstimate.objects.filter( ptms__id = 5 ).filter( ptms__id = 12 ).filter( peptide = peptides[0]).filter( ion__experiment = expt ).distinct()
    print IdEstimate.objects.annotate(count=Count('ptms')).filter( ptms__id = 5 ).filter( ptms__id = 12 ).filter(count=2).filter( peptide = peptides[0]).filter( ion__experiment = expt ).distinct()
    print IdEstimate.objects.filter( *qlist[:2] ).filter( peptide = peptides[0]).filter( ion__experiment = expt ).distinct()
