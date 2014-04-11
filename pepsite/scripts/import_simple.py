import os
import sys
import datetime
import json


PROJ_NAME = 'hdome'
APP_NAME = 'pepsite'

CURDIR = os.path.dirname( os.path.abspath( __file__ ) )

print CURDIR

sys.path.append( CURDIR + '/../..' ) # gotta hit settings.py for site

os.environ[ 'DJANGO_SETTINGS_MODULE' ] = '%s.settings' %( PROJ_NAME )

import django #required
django.setup() #required

from django.contrib.auth.models import User
from pepsite.models import *

Allele.objects.all().delete()
Antibody.objects.all().delete()
Protein.objects.all().delete()
Peptide.objects.all().delete()
Ion.objects.all().delete()
Organism.objects.all().delete()
Individual.objects.all().delete()
CellLine.objects.all().delete()
IdEstimate.objects.all().delete()



#from pfm          import settings          #your project settings file
#from django.core.management  import setup_environ     #environment setup function

#setup_environ(settings)

print Allele.objects.all(), Antibody.objects.all()



ALLELES =     [ [ 'HLA Class-I', 'A*01:01:01:01', 'A1'],
		[ 'HLA Class-I', 'B*08:01:01', 'B8' ],
		[ 'HLA Class-I', 'C*08:01:01', 'Cw7' ],
		]

#u1 = User.objects.get( username = 'rimmer' )

class SfTools( object ):

  
    def setup(self):
	gene1 = Gene( name = 'HLA', gene_class = 1 )
	gene1.save()
	self.create_alleles( gene1, ALLELES )
	ab1 = Antibody( name = 'anti-HLA Class-I'	)
	ab1.save()
	for allele in Allele.objects.filter( gene = gene1 ):
	    ab1.alleles.add( allele )
	#print self.check_condition( Allele, ( dna_type = 'A*01:01:01:01' ) )
	#pep1.save()
	prot1 = Protein( prot_id = "sp|Q15120|PDK3_HUMAN", description = "[Pyruvate dehydrogenase [lipoamide]] kinase isozyme 3, mitochondrial " )
	prot1.save()
	pep1 = Peptide( sequence = 'VADVVKDAV', mass = 999.99, protein = prot1 )
        pep1.save()
	dt1 = datetime.datetime.now()
	exp1 = Experiment( title = 'First Experiment', date_time = dt1 )
	exp1.save()
	ion1 = Ion( charge_state = 2, precursor_mass = 978.5087, retention_time = 999.99, experiment = exp1 )
	ion1.save()
	host1 = Organism( common_name = 'human', sci_name = 'homo sapiens' )
	host1.save()
	ind1 = Individual( identifier = "unknown SA male", description = 'caucasoid|male|consanguineous|homozygous', nation_origin = 'South Africa' )
	ind1.save()
	ind1.organism = host1
	ind1.save()
	host1.save()
	cl1 = CellLine( name='9022', host = host1 )
	cl1.save()
	cl1.alleles.add( Allele.objects.filter(ser_type = 'A1')[0])
	host1.individuals = ind1
	host1.save()
	print ab1.alleles.all()
	print Individual.objects.all()
	ind2 = Individual.objects.get( identifier = "unknown SA male", description = 'caucasoid|male|consanguineous|homozygous', nation_origin = 'South Africa' )
	print host1.individuals
	host2 = Organism.objects.get( sci_name = 'homo sapiens' )
	print host2.individuals
	print ind2.organism_set.all()
	ion1.antibodies.add( ab1 )
	ion1.cell_lines.add( cl1 )
	id1 = IdEstimate( peptide = pep1, ion = ion1, experiment = exp1, delta_mass = 0.0064, confidence = 99 )
	id1.save()
	print ion1.antibodies.all()

    def create_alleles(self, gene_obj, allele_iterable ):
	for entry in allele_iterable:
	    if not len( Allele.objects.filter( gene = gene_obj, dna_type = entry[1] ) ): #integer 0 is falsy
	        al = Allele( gene = gene_obj, dna_type = entry[1], ser_type = entry[2] )
		al.save()

    def check_condition( self, obj_type, conditions ):
	if not len( obj_type.objects.filter( conditions ) ):
	    return obj_type( conditions )
	else:
	    return obj_type.objects.filter( conditions )[0]
	
    def auto_setup_row( self, row, delim = ',' ):
	row = row.strip().split( delim )
	

	

    def check_status(self):
	print 'Owner objects:'
	print Owner.objects.all()
	print 'Submission objects:'
	print Submission.objects.all()
	print 'Submissions\' projected release dates'
	for i in range(len( Submission.objects.all() )):
		print str(  Submission.objects.all()[i].proj_release)
	#print self.subobj.proj_release
	print 'PdbRef objects:'
	print PdbRef.objects.all()
	for p in PdbRef.objects.all():
	    print p.release_status
	print 'PubMedRef objects:'
	print PubMedRef.objects.all()
	print 'SubPdb relations'
	print SubPdb.objects.all()
	print 'SubPdb relations filtered'
	print SubPdb.objects.filter( release_override = True, pdbref__valid_entry = True )
	
    def test_pdb_obtain(self):
        pdblist = [ b.pdb_code.lower() for b in PdbRef.objects.all() ]
	p1 = PdbRef( pdb_code = '1fvk' )
	p2 = PdbRef( pdb_code = '3h93' )
	p1.get_descriptors()
	p1.get_release_status()
	p2.get_descriptors()	
	p2.get_release_status()
        pdblist = [ b.pdb_code.lower() for b in PdbRef.objects.all() ]
	#for p in ( p1, p2 ):
	#    if p not in self.subobj.pdbref_set.all():
	#	p.save()	
	#	sp = SubPdb.objects.create( submission = self.subobj, pdbref = p, trigger_release = True, release_override = True ) 
	#	#p.submission.add( self.subobj )
	#	#p.save()
	#	self.subobj.save()
	 

    def test_pubmed_obtain(self):
        pubmedlist = [ b.pubmed_code for b in PubMedRef.objects.all() ]
	for pdbent in self.subobj.pdbref_set.all():
	    if pdbent.pubmed_id != '':
	        p = PubMedRef( pubmed_code = pdbent.pubmed_id )
		p.get_descriptors()
	        if p not in self.subobj.pubmedref_set.all():
		    p.save()	
		    p.submission.add( self.subobj )
		    self.subobj.save() 
	    for k in ('authors', 'title', 'journal', 'volume', 'year' ):
		print p.pubmed_code, k, getattr( p, k )
	

	    

    def teardown(self):
	
	try:
	    u2 = User.objects.get( username = 'kfed' )
	    u2.delete()
	except:
	    pass
	try:
	    o2 = Owner.objects.get(pk=1)
	    o2.delete()
	except:
	    pass
	try:
	    Submission.objects.all().delete()
	except:
	    pass
	try:
	    PdbRef.objects.filter( pdb_code__in = ['1fvk', '3h93'] ).delete()
	except:
	    pass
        try:
	    PubMedRef.objects.filter( pubmed_code__in = ['9300489', '19788398']).delete()
	except:
	    pass

	#print Owner.objects.all()

if __name__ == "__main__":

    a1 = SfTools()
    #a1.teardown()
    a1.setup()
    #a1.check_status()
    #a1.test_pdb_obtain()
    #a1.check_status()
    #a1.test_pubmed_obtain()
    #a1.check_status()
    #a1.teardown()
    #a1.check_status()
