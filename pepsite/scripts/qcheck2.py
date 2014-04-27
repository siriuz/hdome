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

DB_PEPTIDES = [
['DHNFVKAINAIQKSW','[Undefined] ','sp|P53634|CATC_HUMAN'],
['DHNFVKAINAIQKSWT','[Undefined] ','sp|P53634|CATC_HUMAN'],
['DPFNPFELTNHAVLLVGYGTD','[Amidated@C-term] ','sp|P53634|CATC_HUMAN'],
['EKKVVVYLQKLDTAYDD','[Undefined] ','sp|P53634|CATC_HUMAN'],
['GMDYWIVKNSWGTG','[Undefined] ','sp|P53634|CATC_HUMAN'],
['GPQEKKVVVYLQKLDTAYD','[Deamidated(Q)@12] ','sp|P53634|CATC_HUMAN'],
['GPQEKKVVVYLQKLDTAYD','[Undefined] ','sp|P53634|CATC_HUMAN'],
['GPQEKKVVVYLQKLDTAYDD','[Undefined] ','sp|P53634|CATC_HUMAN'],
['GPQEKKVVVYLQKLDTAYDDL','[Undefined] ','sp|P53634|CATC_HUMAN'],
['GPQEKKVVVYLQKLDTAYDDLG','[Undefined] ','sp|P53634|CATC_HUMAN'],
['GPQEKKVVVYLQKLDTAYDDLGNSGHF','[Undefined] ','sp|P53634|CATC_HUMAN'],
['GPQEKKVVVYLQKLDTAYDDLGNSGHFT','[Undefined] ','sp|P53634|CATC_HUMAN'],
['HGPMAVAFEVYDDFLHYKKGIYHHTG','[Undefined] ','sp|P53634|CATC_HUMAN'],
['KKVVVYLQKLDT','[Dehydrated(D)@11] ','sp|P53634|CATC_HUMAN'],
['KKVVVYLQKLDTAY','[Dehydrated(Y)@14] ','sp|P53634|CATC_HUMAN'],
['KKVVVYLQKLDTAYDDL','[Undefined] ','sp|P53634|CATC_HUMAN'],
['KKVVVYLQKLDTAYDDLG','[Undefined] ','sp|P53634|CATC_HUMAN'],
['KKVVVYLQKLDTAYDDLGNSGHFT','[Undefined] ','sp|P53634|CATC_HUMAN'],
['KVVVYLQKLDT','[Dehydrated(D)@10] ','sp|P53634|CATC_HUMAN'],
['KVVVYLQKLDTA','[Dehydrated(T)@11] ','sp|P53634|CATC_HUMAN'],
['KVVVYLQKLDTAY','[Dehydrated(T)@11] ','sp|P53634|CATC_HUMAN'],
['KVVVYLQKLDTAY','[Dehydrated(Y)@13] ','sp|P53634|CATC_HUMAN'],
['KYDHNFVKAINAIQKS','[Undefined] ','sp|P53634|CATC_HUMAN'],
['KYDHNFVKAINAIQKSWT','[Undefined] ','sp|P53634|CATC_HUMAN'],
['SGMDYWIVKNSWGTG','[Undefined] ','sp|P53634|CATC_HUMAN'],
['SGMDYWIVKNSWGTGWG','[Undefined] ','sp|P53634|CATC_HUMAN'],
['VVVYLQKLDTAYD','[Undefined] ','sp|P53634|CATC_HUMAN'],
['VVVYLQKLDTAYDDL','[Undefined] ','sp|P53634|CATC_HUMAN'],
['VVVYLQKLDTAYDDLG','[Undefined] ','sp|P53634|CATC_HUMAN'],
['WIVKNSWGTGWG','[Undefined] ','sp|P53634|CATC_HUMAN'],
['YDHNFVKAINAIQ','[Undefined] ','sp|P53634|CATC_HUMAN'],
['YWIVKNSWGTGWG','[Undefined] ','sp|P53634|CATC_HUMAN'],
]

if __name__ == '__main__':
    cl1 = CellLine.objects.get( name = '9031')
    ab1 = Antibody.objects.get( name = 'anti-DR' )
    exp1 = Experiment.objects.get( cell_line = cl1, antibody = ab1 )
    pr1 = Protein.objects.get( prot_id = 'sp|P53634|CATC_HUMAN', description = 'Dipeptidyl peptidase 1 OS=Homo sapiens GN=CTSC PE=1 SV=2' )
    q0 = Q( ion__experiments = exp1 )
    q1 = Q( ion__experiments__cell_line = cl1 )
    q2 = Q( ion__experiments__antibody = ab1 )
    q3 = Q( peptide__proteins = pr1 )
    ids = IdEstimate.objects.filter( q0, q1, q2, q3 )
    
    retrieved = []
    print len( set(ids ))
    for ide in set(ids):
	    print ide, ide.peptide.sequence, ide.ptm.description, pr1.prot_id, pr1.description 
	    retrieved.append( [ ide.peptide.sequence, ide.ptm.description, pr1.prot_id ] )
	   
    retrieved = sorted( retrieved, key = lambda x: x[0] ) 
    expected = sorted( DB_PEPTIDES, key = lambda x: x[0] )
    print retrieved == expected 
