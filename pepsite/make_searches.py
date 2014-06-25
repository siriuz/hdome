from pepsite.models import *
from django.db.models import Q

def rek(lok):
    a = abs( lok)
    for x in j:
        pass



class BaseSearch( object ):
    """This is a space-saving docstring



    """
    def fname(self):
        """docstring for fname"""
        pass
    def get_model_object( self, obj_type, **conditions ):

	if not len( obj_type.objects.filter( **conditions ) ):
	    return obj_type( **conditions )
	    raise ClassNotFoundError( )
	elif len( obj_type.objects.filter( **conditions ) ) == 1:
	    return obj_type.objects.filter( **conditions )[0]
	else:
	    raise NonUniqueError(  )



class ProteinsSearch( BaseSearch ):
    """


    """
    def get_experiments_basic( self, pr_term ):
	expts = set( Experiment.objects.filter( ion__peptides__proteins__description__iexact = pr_term ) )
	proteins = set( Protein.objects.filter( description__iexact = pr_term ) )
	if len( expts ):
	    return ( expts, proteins )
        else:
	    return self.get_experiments_startswith( pr_term )

    def get_experiments_startswith( self, pr_term ):
	expts = set( Experiment.objects.filter( ion__peptides__proteins__description__istartswith = pr_term ) )
	proteins = set( Protein.objects.filter( description__istartswith = pr_term ) )
	if len( expts ):
	    return ( expts, proteins )
        else:
	    return self.get_experiments_contains( pr_term )

    def get_experiments_contains( self, pr_term ):
	expts = set( Experiment.objects.filter( ion__peptides__proteins__description__icontains = pr_term ) )
	proteins = set( Protein.objects.filter( description__icontains = pr_term ) )
	return ( expts, proteins )

class CellLineSearch( BaseSearch ):
    """


    """
    def get_experiments_basic( self, cl_term ):
	expts = set( Experiment.objects.filter( cell_line__name__iexact = cl_term ) )
	if len( expts ):
	    return expts
        else:
	    return self.get_experiments_startswith( cl_term )

    def get_experiments_startswith( self, cl_term ):
	expts = set( Experiment.objects.filter( cell_line__name__istartswith = cl_term ) )
	if len( expts ):
	    return expts
        else:
	    return self.get_experiments_contains( cl_term )

    def get_experiments_contains( self, cl_term ):
	expts = set( Experiment.objects.filter( cell_line__name__icontains = cl_term ) )
	return expts


class ExperimentTitleSearch( BaseSearch ):
    """


    """
    def get_experiments_basic( self, cl_term ):
	expts = set( Experiment.objects.filter( title__iexact = cl_term ) )
	if len( expts ):
	    return expts
        else:
	    return self.get_experiments_startswith( cl_term )

    def get_experiments_startswith( self, cl_term ):
	expts = set( Experiment.objects.filter( title__istartswith = cl_term ) )
	if len( expts ):
	    return expts
        else:
	    return self.get_experiments_contains( cl_term )

    def get_experiments_contains( self, cl_term ):
	expts = set( Experiment.objects.filter( title__icontains = cl_term ) )
	return expts

class CellLineTissueSearch( BaseSearch ):
    """


    """
    def get_experiments_basic( self, cl_term ):
	expts = set( Experiment.objects.filter( cell_line__tissue_type__iexact = cl_term ) )
	if len( expts ):
	    return expts
        else:
	    return self.get_experiments_startswith( cl_term )

    def get_experiments_startswith( self, cl_term ):
	expts = set( Experiment.objects.filter( cell_line__tissue_type__istartswith = cl_term ) )
	if len( expts ):
	    return expts
        else:
	    return self.get_experiments_contains( cl_term )

    def get_experiments_contains( self, cl_term ):
	expts = set( Experiment.objects.filter( cell_line__name__icontains = cl_term ) )
	return expts

class AlleleSearch( BaseSearch ):
    """


    """
    def get_experiments_basic( self, allele_code ):
	expts = set( Experiment.objects.filter( cell_line__alleles__code__iexact = allele_code, antibody__alleles__code__iexact = allele_code ) )
	if len( expts ):
	    return expts
        else:
	    return self.get_experiments_startswith( allele_code )

    def get_experiments_startswith( self, allele_code ):
	expts = set( Experiment.objects.filter( cell_line__alleles__code__istartswith = allele_code, antibody__alleles__code__istartswith = allele_code ) )
	if len( expts ):
	    return expts
        else:
	    return self.get_experiments_contains( allele_code )

    def get_experiments_contains( self, allele_code ):
	expts = set( Experiment.objects.filter( cell_line__alleles__code__icontains = allele_code, antibody__alleles__code__icontains = allele_code ) )
	return expts

class PeptideSearch( BaseSearch ):
    """


    """
    def get_experiments_from_peptide( self, peptide_obj ):
	expts = set(Experiment.objects.filter( ion__peptides = peptide_obj ))
	return expts


class ExptArrayAssemble( BaseSearch ):
    """
    """
    def get_peptide_array_from_protein_expt(self, proteins, expt, user, cutoffs = False ):
        """docstring for get_peptide_array_from_proteins"""
        ides = IdEstimate.objects.filter( peptide__proteins__in = proteins, ion__experiments = expt ).order_by( 'peptide__sequence' )
        return self.get_peptide_array_expt( ides, expt, user, cutoffs = cutoffs )

    def get_peptide_array_expt( self, ides, expt, user, cutoffs = False, cutoff_list = [0.05, 99.0], **kwargs ):
        """
        """
        ml = []
        for ide in ides.order_by('delta_mass'):
                    ptms = ide.ptms.all()
                    for ds in Dataset.objects.filter( ions__idestimate = ide, experiment = expt ).order_by( 'rank' ):
                        if user.has_perm( 'view_dataset', ds ):
                            for protein in Protein.objects.filter( peptoprot__peptide__idestimate = ide, peptoprot__peptide__idestimate__ion__dataset = ds ): 
                                p2p = PepToProt.objects.get( peptide = ide.peptide, protein = protein )
                                #if cutoffs and ds.dmass_cutoff > abs( ide.delta_mass ) and ds.confidence_cutoff < abs( ide.confidence ):
                                if cutoffs and ds.dmass_cutoff > abs( ide.delta_mass ) and ds.confidence_cutoff < abs( ide.confidence ):
                                    ml.append( { 'ide': ide, 'ptms' : ptms, 'expt' : expt, 'ds' : ds, 'protein' : protein, 'peptoprot' : p2p } )
                                elif not cutoffs:
                                    ml.append( { 'ide': ide, 'ptms' : ptms, 'expt' : expt, 'ds' : ds, 'protein' : protein, 'peptoprot' : p2p } )
                            break
	return ml




class MassSearch( BaseSearch ):
    """


    """
    def get_ides_from_mass( self, mass, tolerance ):
        ides = IdEstimate.objects.filter( ion__precursor_mass__lte = mass + tolerance,  ion__precursor_mass__gte = mass - tolerance ).order_by( 'peptide__sequence' ) 
	return ides

    def get_unique_peptide_ides_from_mass( self, mass, tolerance, user ):
        ml = []
        ides = IdEstimate.objects.filter( ion__precursor_mass__lte = mass + tolerance,  ion__precursor_mass__gte = mass - tolerance ).order_by( 'peptide__sequence' ) 
        peptides = set( [ b.peptide for b in ides ] )
        return self.get_peptide_array( ides, user, ion__precursor_mass__lte = mass + tolerance,  ion__precursor_mass__gte = mass - tolerance )
        for ide in ides:
                for expt in Experiment.objects.filter( ion__idestimate = ide, ion__precursor_mass__lte = mass + tolerance,  ion__precursor_mass__gte = mass - tolerance ):
                    for ds in Dataset.objects.filter( ions__idestimate = ide, experiment = expt ).order_by( 'rank' ):
                        if user.has_perm( 'view_dataset', ds ):
                            for protein in Protein.objects.filter( peptoprot__peptide__idestimate = ide, peptoprot__peptide__idestimate__ion__dataset = ds ): 
                                p2p = PepToProt.objects.get( peptide = ide.peptide, protein = protein )
                                ml.append( { 'ide': ide, 'expt' : expt, 'ds' : ds, 'protein' : protein, 'peptoprot' : p2p } )
                            break
	return ml

    def get_peptide_array_from_ptm( self, ptm_obj, user ):
        ml = []
        ides = IdEstimate.objects.filter( ptm = ptm_obj ).order_by( 'peptide__sequence' ) 
        peptides = set( [ b.peptide for b in ides ] )
        return self.get_peptide_array( ides, user, ion__idestimate__ptm = ptm_obj )

    def get_peptide_array_from_protein( self, protein_obj, user ):
        ml = []
        ides = IdEstimate.objects.filter( peptide__proteins = protein_obj ).order_by( 'peptide__sequence' ) 
        peptides = set( [ b.peptide for b in ides ] )
        return self.get_peptide_array( ides, user, ion__idestimate__peptide__proteins = protein_obj )

    def get_peptide_array_from_peptide( self, peptide_obj, user ):
        ml = []
        ides = IdEstimate.objects.filter( peptide = peptide_obj ) 
        peptides = set( [ b.peptide for b in ides ] )
        return self.get_peptide_array( ides, user, ion__idestimate__peptide = peptide_obj )

    def get_peptide_array( self, ides, user, **kwargs ):
        """
        """
        ml = []
        for ide in ides:
            for expt in Experiment.objects.filter( ion__idestimate = ide, **kwargs ):# ion__precursor_mass__lte = mass + tolerance,  ion__precursor_mass__gte = mass - tolerance ):
                    for ds in Dataset.objects.filter( ions__idestimate = ide, experiment = expt ).order_by( 'rank' ):
                        if user.has_perm( 'view_dataset', ds ):
                            for protein in Protein.objects.filter( peptoprot__peptide__idestimate = ide, peptoprot__peptide__idestimate__ion__dataset = ds ): 
                                p2p = PepToProt.objects.get( peptide = ide.peptide, protein = protein )
                                ml.append( { 'ide': ide, 'expt' : expt, 'ds' : ds, 'protein' : protein, 'peptoprot' : p2p } )
                            break
	return ml

    def find_hirank_peptide(self, peptide, ):
        """docstring for find_hirank_peptide"""
        pass




class ProteinSearch( BaseSearch ):
    """


    """
    def get_experiments_from_protein( self, protein_obj ):
	expts = set(Experiment.objects.filter( ion__peptides__proteins = protein_obj ))
	return expts

class ExptAssemble( BaseSearch ):
    """


    """
    def get_peptide_info( self, expt_obj ):
        ids = IdEstimate.objects.filter( ion__experiments = expt_obj )
	#return ([['howdy', 'pardner'],])
	details = []
	for b in ids:

	    q2 = Q( peptide__idestimate = b )
	    for prot in Protein.objects.filter( q1, q2  ):
   	        if b.ptm:
	            details.append([ prot.prot_id, prot.id, b.peptide.id, b.peptide.sequence, b.ptm.description, b.delta_mass, b.ion.charge_state, b.ion.retention_time, b.ion.precursor_mass  ])
	        else:
	            details.append([ prot.prot_id, prot.id, b.peptide.id, b.peptide.sequence, '', b.delta_mass, b.ion.charge_state, b.ion.retention_time, b.ion.precursor_mass  ])
        return sorted( details, key = lambda a: a[0] )

    def get_ancillaries( self, protein_list, expt_obj ):
	flist = []
	for p in protein_list:
	    peplist = p.peptide_set.filter( proteins = p, ion__experiments = expt_obj )
   	    for pep in peplist:
                idlist = pep.idestimate_set.filter( peptide__proteins = p, ion__experiments = expt_obj )
                for ide in idlist:
		    flist.append( [ p, pep, ide ] )
	return flist

    def extract_uniprot_id( self, crude_id ):
	return crude_id.split('|')[1]

    def get_common_alleles( self, expt_obj ):
	return Allele.objects.filter( cellline__experiment = expt_obj, antibody__experiments = expt_obj )

class CompositeSearch( BaseSearch ):
    """


    """
    def make_qseries(self, dic, keys):
        """docstring for make_qseries"""
        expts = []
        for k in keys:
            if dic[k]['qtype'] == 'pr_name':
                ps = ProteinsSearch()
                expts.append( set( ps.get_experiments_basic( dic[k]['qstring'] )[0] ) )
            elif dic[k]['qtype'] == 'tissue':
                ct = CellLineTissueSearch()
                expts.append( set( ct.get_experiments_basic( dic[k]['qstring'] ) ) )
            elif dic[k]['qtype'] == 'cell_line':
                cl = CellLineSearch()
                expts.append( set( cl.get_experiments_basic( dic[k]['qstring'] ) ) )
            elif dic[k]['qtype'] == 'ex_title':
                ex = ExperimentTitleSearch()
                expts.append( set( ex.get_experiments_basic( dic[k]['qstring'] ) ) )
            elif dic[k]['qtype'] == 'allele':
                al = AlleleSearch()
                expts.append( set( al.get_experiments_basic( dic[k]['qstring'] ) ) )
        return list( set.intersection( *expts ) )


