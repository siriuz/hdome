import os
import sys
import datetime
from django.utils.timezone import utc


PROJ_NAME = 'hdome'
APP_NAME = 'pepsite'

CURDIR = os.path.dirname( os.path.abspath( __file__ ) )

print CURDIR

sys.path.append( CURDIR + '/../..' ) # gotta hit settings.py for site

SS = os.path.abspath( os.path.join( CURDIR, '../../background/eg_sheet_01.csv' ) )

print SS

os.environ[ 'DJANGO_SETTINGS_MODULE' ] = '%s.settings' %( PROJ_NAME )

import django #required
django.setup() #required

from django.contrib.auth.models import User
from pepsite.models import *


#Allele.objects.all().delete()
#Gene.objects.all().delete()
#Antibody.objects.all().delete()
#Protein.objects.all().delete()
#Peptide.objects.all().delete()
#Ion.objects.all().delete()
#Organism.objects.all().delete()
#Individual.objects.all().delete()
#CellLine.objects.all().delete()
#IdEstimate.objects.all().delete()



#from pfm          import settings          #your project settings file
#from django.core.management  import setup_environ     #environment setup function

#setup_environ(settings)

print Allele.objects.all(), Antibody.objects.all()


ROW = 'VADVVKDAY,,sp|Q15120|PDK3_HUMAN,[Pyruvate dehydrogenase [lipoamide]] kinase isozyme 3; mitochondrial ,99,0.0064,2,978.5087'

ALLELES =     [ [ 'HLA Class-I', 'A*01:01:01:01', 'A1'],
		[ 'HLA Class-I', 'B*08:01:01', 'B8' ],
		[ 'HLA Class-I', 'C*08:01:01', 'Cw7' ],
		]

#u1 = User.objects.get( username = 'rimmer' )


class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class NonUniqueError(Error):
    def __init__(self, msg = 'Query yielded more than one class instance' ):
        self.msg = msg

    def __str__(self):
	return repr( self.msg )

class ClassNotFoundError(Error):
    def __init__(self, msg = 'Query yielded zero class instances' ):
        self.msg = msg

    def __str__(self):
	return repr( self.msg )

class SfTools( object ):

 
    def create_sheet_structures( self ):
	gene1 = self.get_model_object( Gene, name = 'HLA', gene_class = 1 )
	gene1.save()
	for entry in ALLELES:
	    al1 = self.get_model_object( Allele, gene = gene1, dna_type = entry[1], ser_type = entry[2] )
	    al1.save()
	ab1 = self.get_model_object( Antibody, name = 'anti-HLA Class-I'	)
	ab1.save()
	for allele in Allele.objects.filter( gene = gene1 ):
	    ab1.alleles.add( allele )
	ind1 = self.get_model_object( Individual, identifier = "unknown SA male", description = 'caucasoid|male|consanguineous|homozygous', nation_origin = 'South Africa' )
	ind1.save()
	host1 = self.get_model_object(Organism, common_name = 'human', sci_name = 'homo sapiens', isHost = True )
	host1.save()
	ind1.organism = host1 
	ind1.save()
	host1.save()
	cl1 = CellLine( name='9022' )
	cl1.save()
	#cl1.alleles.add( Allele.objects.filter(ser_type = 'A1')[0])
	cl1.organisms.add( host1 )
	#host1.individuals = ind1
	#host1.save()
	return (gene1, ab1, ind1, host1, cl1)
	
 
    def setup(self, csv_ss ):
	with open( csv_ss, 'r' ) as f:
	    spreadsheet = [b.strip() for b in f ][1:]
	print 'spreadsheet has %d rows' %( len(spreadsheet) )
	gene1, ab1, ind1, host1, cl1 = self.create_sheet_structures()
	for i in range(len(spreadsheet)):
	    print i,
	    self.process_row( spreadsheet[i], gene1, ab1, ind1, host1, cl1 )
	

    def process_row(self, rowstring, gene_obj, ab_obj, ind_obj, host_obj, cl_obj, delim = ',' ):
	row = rowstring.strip().split( delim )
	gene1, ab1, ind1, host1, cl1 = gene_obj, ab_obj, ind_obj, host_obj, cl_obj
	prot1 = self.get_model_object( Protein, prot_id = row[2], description = row[3] )
	prot1.save()
	pep1 = self.get_model_object( Peptide, sequence = row[0], mass = 999.99 ) #, protein = prot1 )
        pep1.save()
	pep1.proteins.add( prot1 )

	dt1 = datetime.datetime.utcnow().replace(tzinfo=utc)

	exp1 = self.get_model_object( Experiment, title = 'First Experiment', date_time = dt1, cell_line = cl1 )
	exp1.save()
	ion1 = self.get_model_object(Ion, charge_state = int(row[6]), precursor_mass = row[7], retention_time = 999.99 )
	ion1.save()
	ion1.experiments.add( exp1 )
	
	#ion1.antibodies.add( ab1 )
	#ion1.cell_lines.add( cl1 )
	id1 = self.get_model_object(IdEstimate, peptide = pep1, ion = ion1, delta_mass = float(row[5]), confidence = row[4] )
	id1.save()


    def get_model_object( self, obj_type, **conditions ):
	
	if not len( obj_type.objects.filter( **conditions ) ):
	    return obj_type( **conditions )
	    raise ClassNotFoundError( )
	elif len( obj_type.objects.filter( **conditions ) ) == 1:
	    return obj_type.objects.filter( **conditions )[0]
	else:
	    raise NonUniqueError(  )
	
    def create_alleles(self, gene_obj, allele_iterable ):
	for entry in allele_iterable:
	    if not len( Allele.objects.filter( gene = gene_obj, dna_type = entry[1] ) ): #integer 0 is falsy
	        al = Allele( gene = gene_obj, dna_type = entry[1], ser_type = entry[2] )
		al.save()

	
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
	

    def trial_queries( self ):
	elist = IdEstimate.objects.filter( confidence__lte = 98.0 )
	for a in elist:
	    print a, a.peptide, a.ion, a.peptide.proteins.all(), a.peptide.ptms.all(), a.ion.experiments.all() # a.experiment, a.peptide.protein, a.peptide.ptms.all(), a.ion.cell_lines.all(), a.ion.antibodies.all(), [ b.alleles.all() for b in a.ion.cell_lines.all() ], [ b.infecteds.all() for b in a.ion.cell_lines.all() ], [ a.gene for ent in [ b.alleles.all() for b in a.ion.cell_lines.all() ] for a.gene in ent ]
	

	
	    # organism, gene,

	pepseq = Peptide.objects.get( sequence = 'EENVPSSVTDVALPA' )
	protz = Protein.objects.filter( peptide__sequence = 'EENVPSSVTDVALPA' )
	print protz
	protz = Protein.objects.filter( peptide__idestimate__confidence__gte = 99.0 )
	print protz
	protz = Protein.objects.filter( peptide__idestimate__ion__experiments__cell_line__organisms__individual__description = '' )
	print protz
	
	

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
    #a1.setup( SS )
    a1.trial_queries()

    #a1.check_status()
    #a1.test_pdb_obtain()
    #a1.check_status()
    #a1.test_pubmed_obtain()
    #a1.check_status()
    #a1.teardown()
    #a1.check_status()
