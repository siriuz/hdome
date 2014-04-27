
import sys
from django.db.models import Q
from pepsite.models import *

class QueryQuick( object ):
    """



    """
    def __init__(self, module = 'pepsite.models', rootobj = 'Peptide' ):
	self.qlist = []
	self.module = module
	self.rootobj = rootobj

    def retrieve_model_obj_from_str( self, obj ):
	return 

    def create_q( self, **query ):
	return( Q( **query ) )

    def add_q( self, **query ):
	self.qlist.append( self.create_q( **query ) )

    def run_q_all_and(self, module, obj, qlist ):
	model = getattr(sys.modules[ module ], obj  )
	#query = self.qlist2query( qlist )
	return model.objects.filter( *qlist )

    def quick_query_and_only( self ):
	return self.run_q_all_and( self.module, self.rootobj, self.qlist )

    def qlist2query( self, qlist ):
	pass

    def reconstitute_peptide_info( self, pepObj, exptId ):
	q1 = Q( peptide__ion__experiments__title = exptId )
	q2 = Q( peptide = pepObj )
	q3 = Q( peptide__ion__experiments__title = exptId )
	q4 = Q( peptide = pepObj )
	
	return (pepObj, Protein.objects.filter( q1, q2 ), Ptm.objects.filter( q3, q4 ) ) 
	prot_name = pepObj.proteins.all()[0].name 
	return ( [ [b.name, b.prot_id ] for b in pepObj.proteins.all() ] )
	#return ( prot_name, uniprot_code )	

    def reconstitute_ion_info( self, ionObj, exptId ):
	pass
	q1 = Q( )

    def get_peptide_output( self, plist, exptId ):
	return ( [ self.reconstitute_peptide_info( b, exptId ) for b in plist ] )

    def retrieve_from_cell_line( self, cell_line_name, ab_name ):
	cl1 = CellLine.objects.get( name = cell_line_name, experiment__antibody__name = ab_name )
	allz = Allele.objects.filter( cellline = cl1 )
	exptz = Experiment.objects.filter( cell_line = cl1 )
	pepz = Peptide.objects.filter( ion__experiments__cell_line = cl1, ion__experiments__antibody__name = ab_name )
	idez = IdEstimate.objects.filter( ion__experiments__cell_line = cl1, ion__experiments__antibody__name = ab_name )
	ptm1 = Ptm.objects.filter( peptide__idestimate__ion__experiments__cell_line = cl1, peptide__idestimate__ion__experiments__antibody__name = ab_name )[0]
	protz = Protein.objects.filter( peptide__idestimate__ion__experiments__cell_line = cl1, peptide__idestimate__ion__experiments__antibody__name = ab_name, peptide__ptms = ptm1 )
	return ( cl1, allz, exptz, pepz, idez, protz )
	

    def report_from_cell_line( self, cell_line_name, ab_name ):
	cl1 = CellLine.objects.get( name = cell_line_name, experiment__antibody__name = ab_name )
	ab1 = Antibody.objects.get( name = ab_name )
	#allz = Allele.objects.filter( cellline = cl1 )
	#exptz = Experiment.objects.filter( cell_line = cl1 )
	#pepz = Peptide.objects.filter( ion__experiments__cell_line = cl1, ion__experiments__antibody__name = ab_name )
	#idez = IdEstimate.objects.filter( ion__experiments__cell_line = cl1, ion__experiments__antibody__name = ab_name )
	ptmz = Ptm.objects.filter( peptide__idestimate__ion__experiments__cell_line = cl1, peptide__idestimate__ion__experiments__antibody__name = ab_name )
	protz_all = Protein.objects.filter( peptide__idestimate__ion__experiments__cell_line = cl1, peptide__idestimate__ion__experiments__antibody__name = ab_name )
	print len(protz_all)
	print len( ptmz )
	i = 0
	for prot in protz_all:
	    ptmz = set( Ptm.objects.filter( peptide__idestimate__ion__experiments__cell_line = cl1, peptide__idestimate__ion__experiments__antibody = ab1, peptide__proteins = prot ) )
	    i += len(ptmz)
	    print prot, prot.id, len(ptmz)
	print i
	#    for ptm in ptmz:
	#        print prot.name, prot.description, prot.prot_id, ptm.description, ptm.mass_change  
	    
	
	
if __name__ == '__main__':
    qq1 = QueryQuick()
    qq1.add_q( ion__charge_state = 6 )
    qq1.add_q( ion__experiments__title = 'Trial Expt 9031 DP'  )
    print len(  qq1.quick_qery_and_only() )

