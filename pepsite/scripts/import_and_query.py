import os
import sys
import datetime
from django.utils.timezone import utc
from django.db.models import Q

PROJ_NAME = 'hdome'
APP_NAME = 'pepsite'

CURDIR = os.path.dirname( os.path.abspath( __file__ ) )

#print CURDIR

sys.path.append( CURDIR + '/../..' ) # gotta hit settings.py for site

SS = os.path.abspath( os.path.join( CURDIR, '../../background/eg_sheet_01.csv' ) )

#print SS

SF = ( 
			( ( 'HLA', 1 ), ( ( 'A*01:01:01:01', 'A1' ), ('B*08:01:01', 'B8'), ('C*08:01:01', 'Cw7'), ), 
			('pan', 'anti-HLA class-1 non-selective'), ("unknown SA male", 'caucasoid|male|consanguineous|homozygous', 'South Africa' ),
			(('human', 'homo sapiens', True),), ( '9022', 'adapted from human tissue', 'unknown' ) ),
	)


SELECTIVITIES = ( 
			( (( 'HLA', 1 ), ('HLA', 2),), ( ( 'A*01:01:01:01', False), ('A1', True ), ('B*08:01:01', False), ('B8', True), ('C*08:01:01', False), ('Cw7', True), ), 
			('pan', 'anti-HLA class-1 non-selective') ), 
			( ( 'HLA', 2 ), ( ( 'A*01:01:01:01', 'A1' ), ('B*08:01:01', 'B8'), ('C*08:01:01', 'Cw7'), ), 
			('pan', 'anti-HLA class-1 non-selective') ), 
	)

GENES =  (( 'HLA A', 1 ), ('HLA B', 1), ('HLA C', 1), ('HLA E', 1), ('HLA F', 1), ('HLA G', 1), ('HLA DR', 2), ('HLA DQ', 2), ('HLA DP', 2),)

#ALLS = ( ( 'A*01:01:01:01', False), ('A1', True ), ('B*08:01:01', False), ('B8', True), ('C*08:01:01', False), ('Cw7', True), )

ANBS= 	( ('pan', 'anti-HLA class-1 non-selective', ['HLA A', 'HLA B', 'HLA C'],), ('anti-DR', 'anti-HLA DR selective', ['HLA DR'],), ('anti-DQ', 'anti-HLA DQ selective', ['HLA DQ'],),  ('anti-DP', 'anti-HLA DP selective', ['HLA DP'],),  ) 

ENTITIES = ( ( 'human', 'homo sapiens', 'Unhairy ape', True), )

CELL_LINES = ( ( '9022', 'EBV transformed B lymphoblastoid cell line', '9022 anonymous donor', True), 
               ( '9013', 'EBV transformed B lymphoblastoid cell line', '9013 anonymous donor', True),
               ( '9031', 'EBV transformed B lymphoblastoid cell line', '9031 anonymous donor', True),
               ( '9087', 'EBV transformed B lymphoblastoid cell line', '9087 anonymous donor', True),

		)


INDIVIDUALS = (
		( '9022 anonymous donor', True, True, 'male|caucasoid|homozygous|consanguineous', 'South Africa', 'http://www.ebi.ac.uk/cgi-bin/ipd/imgt/hla/fetch_cell.cgi?10429', 'human' ),
		( '9013 anonymous donor', True, True, 'male|caucasoid|non-consanguinueous', 'France', 'http://www.ebi.ac.uk/cgi-bin/ipd/imgt/hla/fetch_cell.cgi?11647', 'human' ),
		( '9031 anonymous donor', True, True, 'male|caucasoid|consanguineous', 'Sweden', 'http://www.ebi.ac.uk/cgi-bin/ipd/imgt/hla/fetch_cell.cgi?10329', 'human' ),
		( '9087 anonymous donor', True, True, 'female|caucasoid|non-consanguineous', 'France', 'http://www.ebi.ac.uk/cgi-bin/ipd/imgt/hla/fetch_cell.cgi?11648', 'human' ),
		)

SHEET_LIST = ( 
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9022_class1.csv' ) ), ['pan'], '9022', 'Trial Expt 9022 pan', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9022_DP.csv' ) ), ['anti-DP'], '9022', 'Trial Expt 9022 DP', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9022_DQ.csv' ) ), ['anti-DQ'], '9022', 'Trial Expt 9022 DQ', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9022_DR.csv' ) ), ['anti-DR'], '9022', 'Trial Expt 9022 DR', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9013_class1.csv' ) ), ['pan'], '9013', 'Trial Expt 9013 pan', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9013_DP.csv' ) ), ['anti-DP'], '9013', 'Trial Expt 9013 DP', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9013_DQ.csv' ) ), ['anti-DQ'], '9013', 'Trial Expt 9013 DQ', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9013_DR.csv' ) ), ['anti-DR'], '9013', 'Trial Expt 9013 DR', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9031_class1.csv' ) ), ['pan'], '9031', 'Trial Expt 9031 pan', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9031_DP.csv' ) ), ['anti-DP'], '9031', 'Trial Expt 9031 DP', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9031_DQ.csv' ) ), ['anti-DQ'], '9031', 'Trial Expt 9031 DQ', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9031_DR.csv' ) ), ['anti-DR'], '9031', 'Trial Expt 9031 DR', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9087_class1.csv' ) ), ['pan'], '9087', 'Trial Expt 9087 pan', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9087_DP.csv' ) ), ['anti-DP'], '9087', 'Trial Expt 9087 DP', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9087_DQ.csv' ) ), ['anti-DQ'], '9087', 'Trial Expt 9087 DQ', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9087_DR.csv' ) ), ['anti-DR'], '9087', 'Trial Expt 9087 DR', ),
		 )
#print SF[0][:]

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

#print Allele.objects.all(), Antibody.objects.all()


ROW = 'VADVVKDAY,,sp|Q15120|PDK3_HUMAN,[Pyruvate dehydrogenase [lipoamide]] kinase isozyme 3; mitochondrial ,99,0.0064,2,978.5087'


with open( os.path.join( CURDIR, '../../background/compact_alleles.csv' ), 'r' ) as f:
    ALLELES = [ b.strip().split(',') for b in f ] 
ALLELES = [ [b[0], b[1], bool(int(b[2])), int(b[3]), b[4] ] for b in ALLELES ]



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


    def clear_all( self ):
	Allele.objects.all().delete()
	Gene.objects.all().delete()
	Antibody.objects.all().delete()
	Protein.objects.all().delete()
	Peptide.objects.all().delete()
	Ion.objects.all().delete()
	Entity.objects.all().delete()
	Individual.objects.all().delete()
	CellLine.objects.all().delete()
	IdEstimate.objects.all().delete()


    def create_gene_allele_antibody( self, genes_fields, cell_lines_fields, entities_fields, individuals_fields, alleles_fields, antibodies_fields  ):
	"""


	>>>create_sheet_structures( ( 'HLA', 1 ), ( ( 'A*01:01:01:01', 'A1' ), ('B*08:01:01', 'B8'), ('C*08:01:01', 'Cw7'), ), 
		('pan', 'anti-HLA class-1 non-selective'), ("unknown SA male", 'caucasoid|male|consanguineous|homozygous', 'South Africa' ),
		(('human', 'homo sapiens', 1),), ( '9022', 'adapted from human tissue', 'unknown' ) )

	"""
	for gene_z in genes_fields: 
	    gene1 = self.get_model_object( Gene, name = gene_z[0], gene_class = gene_z[1] )
	    gene1.save()
	for ent in entities_fields:
	    ent_x = self.get_model_object( Entity, common_name = ent[0], sci_name = ent[1], description = ent[2], isOrganism = ent[3] )
	    ent_x.save()
	for ind in individuals_fields:
	    ent_z = self.get_model_object( Entity, common_name = ind[6] )
	    ent_z.save()
            ind_x = self.get_model_object( Individual, identifier = ind[0], isHost = ind[1], 
			isAnonymous = ind[2], description = ind[3], nation_origin = ind[4], web_ref = ind[5],  entity = ent_z )
	    ind_x.save()
	for cl in cell_lines_fields:
	    ind_z = self.get_model_object( Individual, identifier = cl[2], isHost = cl[3] )
	    ind_z.save()
	    cl_x = self.get_model_object( CellLine, name = cl[0], description = cl[1] )
	    cl_x.save()
	    self.add_if_not_already( ind_z, cl_x, cl_x.individuals )
	    cl_x.save()
	for entry in alleles_fields:
	    gene_z = self.get_model_object( Gene, name = entry[4], gene_class = int(entry[3]) )
	    gene_z.save()
	    cl_z = self.get_model_object( CellLine, name = entry[0] )
	    al1 = self.get_model_object( Allele, gene = gene_z, code = entry[1], isSer = bool(int(entry[2])) )
	    al1.save()
	    #al1.cellline_set.add( cl_z )
	    self.add_if_not_already( cl_z, al1, al1.cellline_set )
	    al1.save()
	for ab in antibodies_fields:
	    anb_x = self.get_model_object( Antibody, name = ab[0], description = ab[1] )
	    anb_x.save()
	    for al_z in ab[2]:
		alleles_z = Allele.objects.filter( gene__name = al_z )
		for allele in alleles_z:
		    #anb_x.alleles.add( allele )  
	    	    self.add_if_not_already( allele, anb_x, anb_x.alleles )
	    #print anb_x, [ [ b, b.isSer ] for b in anb_x.alleles.all() ]

    def add_if_not_already( self, obj1, obj2, obj2_lookup ):
	if obj1 not in obj2_lookup.all():
	     obj2_lookup.add( obj1 )


    def process_ss_list( self, ss_list ):
	for ss in ss_list:
	    self.create_all_entries( ss )
 
    def create_all_entries(self, full_options ):
	    dt1 = datetime.datetime.utcnow().replace(tzinfo=utc)
	    csv_ss = full_options[0]
	    with open( csv_ss, 'r' ) as f:
	        spreadsheet = [b.strip() for b in f ][1:]
	    #print 'spreadsheet %s has %d rows' %( csv_ss, len(spreadsheet) )
	    ab_list, cl_name = full_options[1], full_options[2]
	    cl1 = self.get_model_object( CellLine, name = cl_name) #, date_time = dt1, cell_line = cl1 )
	    cl1.save()
	    expt_new = self.get_model_object( Experiment, title = full_options[3], date_time = dt1, cell_line = cl1 )
	    expt_new.save()
	    for ab in ab_list:
		ab_obj = self.get_model_object( Antibody, name = ab )
		ab_obj.save()
	    	self.add_if_not_already( ab_obj, expt_new, expt_new.antibody_set )
	        #expt_new.antibody_set.add( ab_obj ) 
	    for i in range(len(spreadsheet)):
	        print csv_ss + ',' + str(expt_new) + ',' + str( i ) +',',
	        self.process_row( spreadsheet[i], expt_new )
	

    def process_row(self, rowstring, expt_obj, delim = ',' ):
	row = rowstring.strip().split( delim )
	prot1 = self.get_model_object( Protein, prot_id = row[2])#, description = row[3] )
	prot1.description = row[3]
	prot1.save()
	pep1 = self.get_model_object( Peptide, sequence = row[0], mass = 999.99 ) #, protein = prot1 )
        pep1.save()
	#pep1.proteins.add( prot1 )
	self.add_if_not_already( prot1, pep1, pep1.proteins )
	#self.add_if_not_already( ptm, pep1, pep1.ptms )
	ion1 = self.get_model_object(Ion, charge_state = int(row[6]), precursor_mass = row[7], retention_time = 999.99 )
	ion1.save()
	#ion1.experiments.add( expt_obj )
	if row[1]:
	    ptm = self.get_model_object( Ptm, description = row[1], mass_change = -22.2 )
	    ptm.save()
	    id1 = self.get_model_object(IdEstimate, peptide = pep1, ptm = ptm, ion = ion1, delta_mass = float(row[5]), confidence = row[4] )
	    id1.save()
	    print ',' + ptm.description + ',',
	else:
	    id1 = self.get_model_object(IdEstimate, peptide = pep1, ion = ion1, delta_mass = float(row[5]), confidence = row[4] )
	    id1.save()
	    print ',BLANK,',
	self.add_if_not_already( expt_obj, ion1, ion1.experiments )
	#id1 = self.get_model_object(IdEstimate, peptide = pep1, ion = ion1, delta_mass = float(row[5]), confidence = row[4] )
	#id1.save()
	print ',' + prot1.prot_id + ',' + pep1.sequence + ',' + str( ion1.charge_state ) + ','


    def get_model_object( self, obj_type, **conditions ):
	
	if not len( obj_type.objects.filter( **conditions ) ):
	    return obj_type( **conditions )
	    raise ClassNotFoundError( )
	elif len( obj_type.objects.filter( **conditions ) ) == 1:
	    return obj_type.objects.filter( **conditions )[0]
	else:
	    raise NonUniqueError(  )

    def trial_queries( self ):
	q1 = Q( ion__experiments__title = 'Trial Expt 9031 DP' )	
	q2 = Q( ion__charge_state = 6 )
	q3 = Q( idestimate__confidence__gte = 99 )
	print len( Peptide.objects.filter( q1 & q2 & q3 ) )


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


if __name__ == "__main__":

    a1 = SfTools()
    a1.clear_all()
    a1.create_gene_allele_antibody( GENES, CELL_LINES, ENTITIES, INDIVIDUALS, ALLELES, ANBS )
    a1.process_ss_list( SHEET_LIST )
    #a1.trial_queries()

