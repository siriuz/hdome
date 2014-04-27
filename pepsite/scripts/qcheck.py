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
    q3 = Q( proteins = pr1 )
    peps1 = Peptide.objects.filter( q0, q1, q2, q3 )
    
    q10 = Q( peptide__ion__experiments = exp1 )
    q11 = Q( peptide__ion__experiments__cell_line = cl1 )
    q12 = Q( peptide__ion__experiments__antibody = ab1 )
    q13 = Q( peptide__proteins = pr1 )
    ptms1 = Ptm.objects.filter( q10, q12, q12, q13 )
    print len(peps1), len(ptms1)
    retrieved = []
    for ptm in set(ptms1):
	for pep in set(peps1):
	    q21 = Q( ptms = ptm )
	    q22 = Q( id = pep.id )
	    rez = Peptide.objects.filter( q21, q22, q0, q1, q2, q3 )
	    if len(rez) == 1:
		print pep.sequence, ptm.description
		retrieved.append( [ pep.sequence, ptm.description, pr1.prot_id ] )
	    elif len(rez) > 1:
		print pep.sequence, 'multplicity of', len(rez), ptm.description
		retrieved.append( [ pep.sequence, ptm.description, pr1.prot_id ] )
	   
    retrieved = sorted( retrieved, key = lambda x: x[0] ) 
    expected = sorted( DB_PEPTIDES, key = lambda x: x[0] ) 
    print len(retrieved), len(expected)
    for ent in retrieved:
	if ent not in expected:
		print ent 

    retrieved2 = []
    for pep in set(peps1):
	for ptm in set(ptms1):
	    q31 = Q( id = ptm.id )
	    q32 = Q( peptide = pep )
	    rez = Ptm.objects.filter( q31, q32, q10, q11, q12, q13 )
	    if len(rez) == 1:
		print pep.id, pep.sequence, ptm.description
		retrieved2.append( [ pep.sequence, ptm.description, pr1.prot_id ] )
	    elif len(rez) > 1:
		print pep.id, pep.sequence, 'multplicity of', len(rez), ptm.description
		retrieved2.append( [ pep.sequence, ptm.description, pr1.prot_id ] )
    retrieved2 = sorted( retrieved2, key = lambda x: x[0] ) 
    expected = sorted( DB_PEPTIDES, key = lambda x: x[0] ) 
    print len(retrieved2), len(expected)
    for ent in retrieved2:
	if ent not in expected:
		print ent 

    print len(set(peps1)), len(set([ b.id for b in peps1] )) 
    print set([ b.id for b in peps1] )
    
    for pep in set(peps1):
	#print pep.id,
	q32 = Q( peptide = pep )
	rez = set(Ptm.objects.filter( q32, q10, q11, q12, q13 ))
	#print len(rez)
	
	for ion in Ion.objects.filter( experiments = exp1, peptides = pep ):
	    id1 = IdEstimate.objects.get( peptide = pep, ion = ion )
	    print 'new', pep.sequence, pr1.prot_id, pr1.description, id1.delta_mass, id1.confidence, ion.charge_state, ion.precursor_mass, ion.retention_time, [ b.description for b in rez ]


    for ent in retrieved2:
        if ent not in expected:
	    pep2 = Peptide.objects.get( sequence = ent[0] )
	    ptm2 = Ptm.objects.get( description = ent[1] )
	    qe1 = Q( ion__peptides = pep2 )
	    qe2 = Q( ion__peptides__ptms = ptm2 )
	    qe3 = Q( ion__peptides__proteins = pr1 )
	    print ent, Experiment.objects.filter( qe1, qe2, qe3 )
	    for expt in Experiment.objects.filter( qe1, qe2, qe3 ):
	        for ion in Ion.objects.filter( experiments = expt, peptides = pep2 ):
		   qptm1 = Q( peptide = pep2 )
		   qptm2 = Q( peptide__proteins = pr1 )
		   qptm3 = Q( peptide__ion__experiments = expt )
		   qptm4 = Q( peptide__ion = ion )
		   print ion, pep2.sequence, expt, Ptm.objects.filter( qptm1, qptm2, qptm3, qptm4)#, qptm4 )
		   #print Ptm.objects.filter( qptm1, qptm2, qptm3 ).query



