
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

    def reconstitute_peptide_info( self, pepObj):
	prot_name = pepObj.proteins.all()[0].name 
	uniprot_code = 	pepObj.proteins.all()[0].prot_id
	return ( prot_name, uniprot_code )	

    def get_peptide_output( self, plist ):
	return ( [ self.reconstitute_peptide_info( b ) for b in plist ] )

	
	
if __name__ == '__main__':
    qq1 = QueryQuick()
    qq1.add_q( ion__charge_state = 6 )
    qq1.add_q( ion__experiments__title = 'Trial Expt 9031 DP'  )
    print len(  qq1.quick_qery_and_only() )

