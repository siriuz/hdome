from pepsite.models import *
from django.db.models import Q

class BaseSearch( object ):
    """



    """
    def get_model_object( self, obj_type, **conditions ):
	
	if not len( obj_type.objects.filter( **conditions ) ):
	    return obj_type( **conditions )
	    raise ClassNotFoundError( )
	elif len( obj_type.objects.filter( **conditions ) ) == 1:
	    return obj_type.objects.filter( **conditions )[0]
	else:
	    raise NonUniqueError(  )



class AlleleSearch( BaseSearch ):
    """


    """
    def get_experiments_basic( self, allele_code ):
	expts = Experiment.objects.filter( cell_line__alleles__code = allele_code, antibody__alleles__code = allele_code )
	return expts


class ExptAssemble( BaseSearch ):
    """


    """
    def get_peptide_info( self, expt_obj ):
        ids = IdEstimate.objects.filter( ion__experiments = expt_obj )
	#return ([['howdy', 'pardner'],])
	details = []
	for b in ids:
	    q1 = Q( peptide__ion__experiments = expt_obj )
	    q2 = Q( peptide__idestimate = b )
	    for prot in Protein.objects.filter( q1, q2  ):
   	        if b.ptm:
	            details.append([ self.extract_uniprot_id(prot.prot_id), b.peptide.id, b.peptide.sequence, b.ptm.description, b.delta_mass, b.ion.charge_state, b.ion.retention_time, b.ion.precursor_mass  ])
	        else:
	            details.append([ self.extract_uniprot_id(prot.prot_id), b.peptide.id, b.peptide.sequence, '', b.delta_mass, b.ion.charge_state, b.ion.retention_time, b.ion.precursor_mass  ])
        return details

    def extract_uniprot_id( self, crude_id ):
	return crude_id.split('|')[1]
