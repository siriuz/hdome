from pepsite.models import *
import time
from django.db.models import Q, F
from django.db.models import Count
from django.db.models import Max, Min
from django.db import connection

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

class PtmSearch( BaseSearch ):
    """


    """
    def get_experiments_basic( self, ptm_term ):
	expts = set( Experiment.objects.filter( ion__idestimate__ptms__description__iexact = ptm_term ) )
	if len( expts ):
	    return expts
        else:
	    return self.get_experiments_startswith( ptm_term )

    def get_experiments_startswith( self, ptm_term ):
	expts = set( Experiment.objects.filter( ion__idestimate__ptms__description__istartswith = ptm_term ) )
	if len( expts ):
	    return expts
        else:
	    return self.get_experiments_contains( ptm_term )

    def get_experiments_contains( self, ptm_term ):
	expts = set( Experiment.objects.filter( ion__idestimate__ptms__description__icontains = ptm_term ) )
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
    def get_peptide_array_from_protein_expt(self, proteins, expt, user, compare = False, compare_clean = False, comparators = None, cutoffs = False ):
        """docstring for get_peptide_array_from_proteins"""
        ides = IdEstimate.objects.filter( peptide__proteins__in = proteins, ion__experiment = expt ).order_by( 'peptide__sequence' )
        peptides = Peptide.objects.filter( idestimate__in = ides ).distinct()
        #return self.get_peptide_array_expt( ides, expt, user, cutoffs = cutoffs )
        return self.get_peptide_array_expt_restricted( ides, peptides, expt, user, compare = compare, compare_clean = compare_clean, comparators = comparators, cutoffs = cutoffs )

    def get_peptide_array_from_protein_expt_comparison(self, proteins, expt, exptz, user, cutoffs = False ):
        """docstring for get_peptide_array_from_proteins"""
        ides = IdEstimate.objects.filter( peptide__proteins__in = proteins, ion__experiment = expt ).order_by( 'peptide__sequence' )
        peptides = Peptide.objects.filter( idestimate__in = ides ).distinct()
        #return self.get_peptide_array_expt( ides, expt, user, cutoffs = cutoffs )
        return self.get_peptide_array_expt_restricted( ides, peptides, expt, exptz, user, cutoffs = cutoffs )

    def get_peptide_array_expt( self, ides, expt, user, cutoffs = False, cutoff_list = [0.05, 99.0], **kwargs ):
        """
        """
        ml = []
        for ide in ides.order_by('delta_mass'):
                    ptms = ide.ptms.all()
                    for ds in Dataset.objects.filter( ion__idestimate = ide, experiment = expt ).order_by( 'rank' ):
                        if user.has_perm( 'view_dataset', ds ):
                            for protein in Protein.objects.filter( peptoprot__peptide__idestimate = ide, peptoprot__peptide__idestimate__ion__dataset = ds ): 
                                p2p = PepToProt.objects.get( peptide = ide.peptide, protein = protein )
                                #if cutoffs and ds.dmass_cutoff > abs( ide.delta_mass ) and ds.confidence_cutoff < abs( ide.confidence ):
                                if cutoffs and ds.confidence_cutoff < abs( ide.confidence ):
                                    ml.append( { 'ide': ide, 'ptms' : ptms, 'expt' : expt, 'ds' : ds, 'protein' : protein, 'peptoprot' : p2p } )
                                elif not cutoffs:
                                    ml.append( { 'ide': ide, 'ptms' : ptms, 'expt' : expt, 'ds' : ds, 'protein' : protein, 'peptoprot' : p2p } )
                            break
	return ml

    def get_peptide_array_expt_restricted( self, ides, peptides, expt, user, cutoffs = False, compare = False, compare_clean = False, comparators = None, cutoff_list = [0.05, 99.0], **kwargs ):
            """
            """
            ml = []
            #ideset = IdEstimate.objects.filter( ion__experiment = expt, ion__dataset__confidence_cutoff__lte = F('confidence') ).distinct().annotate( count = Count('ptms'), best = IdEstimate.objects.all().aggregate( Min('delta_mass') )).filter( delta_mass = F('best') ).distinct()
            ideset = IdEstimate.objects.filter( ion__experiment = expt, ion__dataset__confidence_cutoff__lte = F('confidence'), id__in = ides ).distinct()
            print len( ideset )
            i = 0
            for ide in ideset:
              i += 1
              if i < 2001:
                if not (i % 1000):
                    print i

                ptms = ide.ptms.all()
                ds = ide.ion.dataset
                p2pz = PepToProt.objects.filter( peptide__idestimate = ide ).distinct()
                for p2p in p2pz:
                    protein = p2p.protein
                    ml.append(  { 'ide': ide, 'ptms' : ptms, 'expt' : expt, 'ds' : ds, 'protein' : protein, 'peptoprot' : p2p } )
            print 'ide processing done!'
            #for pep in peptides.order_by('sequence'):
            #print pep.sequence
            #ideset = IdEstimate.objects.filter( peptide = pep, id__in = ides, confidence__gte = ion__dataset__confidence_cutoff ).distinct().annotate( count = Count('ptms')).filter( 
            #ptmz = []
            #for ide in ideset:
            #    ptmcon = [ b.id for b in ide.ptms.all().order_by( 'id' ) ]
            #    if ptmcon not in ptmz:
            #        ptmz.append( ptmcon )
            #for ptmcon in ptmz:
            #    #print 'ptmcon', ptmcon
            #    #qlist = []
            #    td = []
            #    count = 0
            #    if not ptmcon:
            #        td = [ {'ptms__isnull' : True}, {'peptide' : pep }, {'ion__experiment' : expt } ]
            #    else:
            #        for ptm in ptmcon:
            #            td.append( { 'ptms__id' : ptm } )
            #        td += [ {'peptide' : pep }, {'ion__experiment' : expt } ]
            #    a = IdEstimate.objects.all().annotate( count = Count('ptms'))
            #    for dic in td:
            #        a = a.filter( **dic )
            #    a = a.filter( isRemoved = False )
            #    ideref = a.filter(count = len(ptmcon)).distinct()
            #    #print 'ideref', [b.id for b in ideref]
            #    entry = self.best_entries( ideref, ptmcon, expt, user, cutoffs = cutoffs ) 
            #    if compare:
            #        if entry is not None:
            #            checkers = self.check_datasets( comparators, pep, ptmcon, cutoffs = compare_clean )
            #            entry[ 'checkers' ] = checkers 
            #            ml.append( entry )
            #    else:
            #        if entry is not None:
            #            ml.append( entry )
            return ml

    def mkii_expt_query(self, exp_id, user_id, perm = False):
        """docstring for simple_expt_query"""
        expt = Experiment.objects.get( id = exp_id )
        print expt.title
        t0 = time.time()
        user = User.objects.get( id = user_id )
        dsets = Dataset.objects.filter( experiment__id = exp_id ).distinct()
        for ds in Experiment.objects.get( id = exp_id ).dataset_set.all():
            if not user.has_perm( 'view_dataset', ds ):
                dsets = dsets.exclude( ds )
        p1 = Peptide.objects.filter(idestimate__ion__experiment = exp_id, idestimate__ion__dataset__confidence_cutoff__lte = F('idestimate__confidence')).distinct()
        sql1 = "select ptmstr from pepsite_idestimate t3 left outer join (select t1.id, t1.confidence, \
                array_to_string(array_agg(t2.ptm_id order by t2.ptm_id),\'+\') as ptmstr from pepsite_idestimate t1 \
                left outer join pepsite_idestimate_ptms t2 on (t2.idestimate_id = t1.id) group by t1.id) as foo \
                on(foo.id = t3.id) where t3.id = pepsite_idestimate.id"
        v1 = IdEstimate.objects.extra( select = { 'ptmstr' :sql1, 'dm' : "abs(delta_mass)" } ).\
                filter( ion__experiment = exp_id, ion__dataset__confidence_cutoff__lte = F('confidence'), ion__dataset__in = dsets )\
                .order_by( 'dm' ).values( 'ptmstr', 'peptide', 'id' ).annotate( ptmc = Count('ptms') ).distinct().order_by('-ptmc')\
                
        j = v1.count()
        t1 = time.time()
        #return (v1, t1 - t0, j, exp_id, user_id, perm)
        return self.rapid_array( v1, exp_id ) 

    def mkiii_expt_query(self, exp_id, user_id, perm = False):
        """docstring for simple_expt_query"""
        t0 = time.time()
        cursor = connection.cursor()
        #cursor.execute( "DROP VIEW IF EXISTS \"allowedides\"" )
        #cursor.execute( "DROP VIEW IF EXISTS \"suppavail\"" )
        #cursor.execute( "DROP VIEW IF EXISTS \"suppcorrect\"" )
        expt = Experiment.objects.get( id = exp_id )
        print expt.title
        user = User.objects.get( id = user_id )
        dsets = Dataset.objects.filter( experiment__id = exp_id ).distinct()
        for ds in Experiment.objects.get( id = exp_id ).dataset_set.all():
            if not user.has_perm( 'view_dataset', ds ):
                dsets = dsets.exclude( ds )
        qq1 = IdEstimate.objects.filter( ion__dataset__in = dsets, ion__dataset__confidence_cutoff__lte = F('confidence') ).distinct().query
        cursor.execute( 'CREATE TEMP VIEW \"allowedides\" AS ' + str( qq1 ) )
        qq2 = "CREATE TEMP VIEW suppavail AS SELECT foo.id, foo.ptmstr,\
                min(abs(foo.delta_mass)) FROM (select t1.id, t1.confidence, t1.peptide_id, \
                t1.delta_mass, array_to_string(array_agg(t2.ptm_id order by t2.ptm_id),'+') AS ptmstr FROM \
                pepsite_idestimate t1 LEFT OUTER JOIN pepsite_idestimate_ptms t2 ON (t2.idestimate_id = t1.id) \
                \
                group by t1.id, t1.peptide_id) AS foo \
                GROUP BY foo.id, foo.ptmstr \
                "
        qq2a = "CREATE TEMP VIEW sv2 AS SELECT * FROM suppavail WHERE adm = min"
        qq3 = "CREATE TEMP VIEW suppcorrect AS SELECT DISTINCT foo.peptide_id, foo.ptmstr, min(abs(foo.delta_mass)) \
                FROM (select t1.id, t1.confidence, t1.peptide_id, t1.delta_mass, \
                array_to_string(array_agg(t2.ptm_id order by t2.ptm_id),'+') AS ptmstr FROM pepsite_idestimate \
                t1 LEFT OUTER JOIN pepsite_idestimate_ptms t2 ON (t2.idestimate_id = t1.id) \
                GROUP BY t1.id) AS \
                foo GROUP BY foo.peptide_id, foo.ptmstr"
        sql1 = "select ptmstr from pepsite_idestimate t3 left outer join (select t1.id, t1.confidence, \
                array_to_string(array_agg(t2.ptm_id order by t2.ptm_id),\'+\') as ptmstr from pepsite_idestimate t1 \
                left outer join pepsite_idestimate_ptms t2 on (t2.idestimate_id = t1.id) group by t1.id) as foo \
                on(foo.id = t3.id) where t3.id = pepsite_idestimate.id"
        qq4 = "SELECT DISTINCT allowedides.id FROM suppcorrect t1 \
                INNER JOIN suppavail t2 ON (t2.min = t1.min AND t2.ptmstr = t1.ptmstr) \
                INNER JOIN allowedides ON (t2.id = allowedides.id AND t1.min = abs(allowedides.delta_mass))"
        cursor.execute( qq2 )
        cursor.execute( qq3 )
        cursor.execute( qq4 )
        ides = cursor.fetchall()
        j = len(ides)
        cursor.execute( "DROP VIEW IF EXISTS \"allowedides\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"suppavail\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"suppcorrect\" CASCADE" )
        cursor.close()
        t1 = time.time()
        return self.rapid_array([b[0] for b in ides], exp_id)

    def mkiii_compare_query(self, prim_exp_id, other_exp_ids, user_id, primary_clean = True, perm = False):
        """docstring for simple_expt_query"""
        t0 = time.time()
        cursor = connection.cursor()
        #cursor.execute( "DROP VIEW IF EXISTS \"allowedides\" CASCADE" )
        #cursor.execute( "DROP VIEW IF EXISTS \"possibles\" CASCADE" )
        #cursor.execute( "DROP VIEW IF EXISTS \"ideproduct\" CASCADE" )
        #cursor.execute( "DROP VIEW IF EXISTS \"combinedideproduct\" CASCADE" )
        #cursor.execute( "DROP VIEW IF EXISTS \"ideproduct2\" CASCADE" )
        #cursor.execute( "DROP VIEW IF EXISTS \"ideproduct3\" CASCADE" )
        #cursor.execute( "DROP VIEW IF EXISTS \"allidescompare\" CASCADE" )
        #cursor.execute( "DROP VIEW IF EXISTS \"cleanidescompare\" CASCADE" )
        #cursor.execute( "DROP VIEW IF EXISTS \"suppavail\" CASCADE" )
        #cursor.execute( "DROP VIEW IF EXISTS \"suppcorrect\" CASCADE" )
        #cursor.execute( "DROP VIEW IF EXISTS \"sv2\" CASCADE" )
        expt = Experiment.objects.get( id = prim_exp_id )
        exptz = Experiment.objects.filter( id__in = other_exp_ids )
        print expt.title
        user = User.objects.get( id = user_id )
        dsets = Dataset.objects.filter( experiment__id = prim_exp_id ).distinct()
        for ds in Experiment.objects.get( id = prim_exp_id ).dataset_set.all():
            if not user.has_perm( 'view_dataset', ds ):
                dsets = dsets.exclude( ds )
        dsets_compare = Dataset.objects.filter( experiment__id__in = other_exp_ids ).distinct()
        for ds in dsets_compare:
            if not user.has_perm( 'view_dataset', ds ):
                dsets_compare = dsets_compare.exclude( ds )
        dsets_compare = dsets_compare.order_by( 'experiment', 'title' )
        self.compare_ds = dsets_compare # will be sent to template
        self.dsnos_ordered = [ b.id for b in dsets_compare ] # will be used to check presence of hit(s)
        qq1_dj = IdEstimate.objects.filter( ion__dataset__in = dsets ).distinct()
        if primary_clean:
            qq1_dj = qq1_dj.filter( ion__dataset__confidence_cutoff__lte = F('confidence') ).distinct()
        qq1_dj_compare = IdEstimate.objects.filter( ion__dataset__in = dsets_compare ).distinct()
        qq1_dj_compare_clean = qq1_dj_compare.filter( ion__dataset__confidence_cutoff__lte = F('confidence') ).distinct()
        qq1 = qq1_dj.query
        qq1_compare = qq1_dj_compare.query
        qq1_compare_clean = qq1_dj_compare_clean.query
        cursor.execute( 'CREATE TEMP VIEW \"allowedides\" AS ' + str( qq1 ) )
        cursor.execute( 'CREATE TEMP VIEW \"allidescompare\" AS ' + str( qq1_compare ) )
        cursor.execute( 'CREATE TEMP VIEW \"cleanidescompare\" AS ' + str( qq1_compare_clean ) )
        qq2 = "CREATE TEMP VIEW suppavail AS SELECT foo.id, foo.ptmstr,\
                min(abs(foo.delta_mass)) FROM (select t1.id, t1.confidence, t1.peptide_id, \
                t1.delta_mass, array_to_string(array_agg(t2.ptm_id order by t2.ptm_id),'+') AS ptmstr FROM \
                pepsite_idestimate t1 LEFT OUTER JOIN pepsite_idestimate_ptms t2 ON (t2.idestimate_id = t1.id) \
                \
                group by t1.id, t1.peptide_id) AS foo \
                GROUP BY foo.id, foo.ptmstr \
                "
        qq2a = "CREATE TEMP VIEW sv2 AS SELECT * FROM suppavail WHERE adm = min"
        qq3 = "CREATE TEMP VIEW suppcorrect AS SELECT DISTINCT foo.peptide_id, foo.ptmstr, min(abs(foo.delta_mass)) \
                FROM (select t1.id, t1.confidence, t1.peptide_id, t1.delta_mass, \
                array_to_string(array_agg(t2.ptm_id order by t2.ptm_id),'+') AS ptmstr FROM pepsite_idestimate \
                t1 LEFT OUTER JOIN pepsite_idestimate_ptms t2 ON (t2.idestimate_id = t1.id) \
                GROUP BY t1.id) AS \
                foo GROUP BY foo.peptide_id, foo.ptmstr"
        qq3a = "CREATE TEMP VIEW compcorrect AS SELECT DISTINCT foo.peptide_id, foo.ptmstr, min(abs(foo.delta_mass)) \
                FROM (select t1.id, t1.confidence, t1.peptide_id, t1.delta_mass, \
                array_to_string(array_agg(t2.ptm_id order by t2.ptm_id),'+') AS ptmstr FROM pepsite_idestimate \
                t1 LEFT OUTER JOIN pepsite_idestimate_ptms t2 ON (t2.idestimate_id = t1.id) \
                GROUP BY t1.id) AS \
                foo GROUP BY foo.peptide_id, foo.ptmstr \
                INNER JOIN pepsite_ion ON (pepsite_ion.id = allowedides.id) \
                "
        sql1 = "select ptmstr from pepsite_idestimate t3 left outer join (select t1.id, t1.confidence, \
                array_to_string(array_agg(t2.ptm_id order by t2.ptm_id),\'+\') as ptmstr from pepsite_idestimate t1 \
                left outer join pepsite_idestimate_ptms t2 on (t2.idestimate_id = t1.id) group by t1.id) as foo \
                on(foo.id = t3.id) where t3.id = pepsite_idestimate.id"
        qq4 = "CREATE TEMP VIEW possibles AS \
                SELECT DISTINCT allowedides.id as id, t2.ptmstr, t1.peptide_id FROM suppcorrect t1 \
                INNER JOIN suppavail t2 ON (t2.min = t1.min AND t2.ptmstr = t1.ptmstr) \
                INNER JOIN allowedides ON (t2.id = allowedides.id AND t1.min = abs(allowedides.delta_mass))"
        qq41 = "CREATE TEMP VIEW comparepossibles AS \
                SELECT DISTINCT allidescompare.id as id, t2.ptmstr, t1.peptide_id FROM suppcorrect t1 \
                INNER JOIN suppavail t2 ON (t2.min = t1.min AND t2.ptmstr = t1.ptmstr) \
                INNER JOIN allidescompare ON (t2.id = allidescompare.id)"
        qq42 = "CREATE TEMP VIEW cleancomparepossibles AS \
                SELECT DISTINCT cleanidescompare.id as id, t2.ptmstr, t1.peptide_id FROM suppcorrect t1 \
                INNER JOIN suppavail t2 ON (t2.min = t1.min AND t2.ptmstr = t1.ptmstr) \
                INNER JOIN cleanidescompare ON (t2.id = cleanidescompare.id)"
        qq4a = "CREATE TEMP VIEW ideproduct AS \
                SELECT DISTINCT id FROM \
                possibles"
        qq5 = "CREATE TEMP VIEW ideproduct2 AS \
                SELECT * FROM \
                (SELECT DISTINCT t1.peptide_id, t1.ptmstr, array_agg(t6.id) as dsid FROM suppcorrect t1 \
                INNER JOIN suppavail t2 ON (t2.min = t1.min AND t2.ptmstr = t1.ptmstr) \
                INNER JOIN allidescompare t4 ON (t2.id = t4.id) \
                INNER JOIN pepsite_idestimate t3 ON ( t4.id = t3.id ) \
                INNER JOIN pepsite_ion t5 ON ( t3.ion_id = t5.id ) \
                INNER JOIN pepsite_dataset t6 ON ( t5.dataset_id = t6.id )\
                GROUP BY t1.peptide_id, t1.ptmstr) AS foo"
        qq6 = "CREATE TEMP VIEW dsids AS \
                SELECT t1.id, t1.ptmstr, array_agg(t6.id) as dsid FROM suppcorrect t1 \
                INNER JOIN \
                "
        qq6 = "CREATE TEMP VIEW ideproduct2 AS \
                SELECT * FROM \
                (SELECT t1.id, t1.peptide_id, t1.ptmstr, array_agg(t6.id) as dsids  FROM \
                cleancomparepossibles t1 \
                INNER JOIN allidescompare t2 ON ( t1.id = t2.id ) \
                INNER JOIN pepsite_ion t5 ON ( t2.ion_id = t5.id ) \
                INNER JOIN pepsite_dataset t6 ON ( t5.dataset_id = t6.id )\
                GROUP BY t1.id, t1.peptide_id, t1.ptmstr \
                ) AS foo \
                "
        qq6a = "CREATE TEMP VIEW ideproduct3 AS \
                SELECT * FROM \
                (SELECT t1.id, t1.peptide_id, t1.ptmstr, array_agg(t6.id) as dsids  FROM \
                comparepossibles t1 \
                INNER JOIN cleanidescompare t2 ON ( t1.id = t2.id ) \
                INNER JOIN pepsite_ion t5 ON ( t2.ion_id = t5.id ) \
                INNER JOIN pepsite_dataset t6 ON ( t5.dataset_id = t6.id )\
                GROUP BY t1.id, t1.peptide_id, t1.ptmstr \
                ) AS foo \
                "
        qq7 = "CREATE TEMP VIEW combinedideproduct AS \
                SELECT * FROM \
                (SELECT DISTINCT t1.id, t2.dsids, t3.dsids as cleandsz  FROM \
                possibles t1 \
                INNER JOIN ideproduct2 t2 ON ( t1.peptide_id = t2.peptide_id AND t1.ptmstr = t2.ptmstr ) \
                INNER JOIN ideproduct3 t3 ON ( t1.peptide_id = t3.peptide_id AND t1.ptmstr = t3.ptmstr ) \
                ) AS foo \
                "
        qqresult = "SELECT * FROM combinedideproduct"
        cursor.execute( qq2 )
        cursor.execute( 'SELECT COUNT(*) FROM suppavail' )
        print cursor.fetchall(  )
        #cursor.execute( 'SELECT COUNT(foo.peptide_id) FROM (SELECT DISTINCT peptide_id, ptmstr FROM suppavail) as foo' )
        #print cursor.fetchall(  )
        #cursor.execute( qq2a )
        #cursor.execute( 'SELECT COUNT(*) FROM sv2' )
        #print cursor.fetchall(  )
        cursor.execute( qq3 )
        cursor.execute( 'SELECT COUNT(*) FROM suppcorrect' )
        print cursor.fetchall(  )
        cursor.execute( qq4 )
        cursor.execute( qq41 )
        cursor.execute( qq42 )
        cursor.execute( qq4a )
        cursor.execute( qq6 )
        cursor.execute( qq6a )
        cursor.execute( qq7 )
        cursor.execute( qqresult )
        ides = cursor.fetchall()
        j = len(ides)
        cursor.execute( "DROP VIEW IF EXISTS \"allowedides\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"possibles\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"comparepossibles\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"cleancomparepossibles\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"ideproduct\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"combinedideproduct\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"ideproduct2\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"ideproduct3\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"allidescompare\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"cleanidescompare\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"suppavail\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"suppcorrect\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"sv2\" CASCADE" )
        cursor.close()
        t1 = time.time()
        print 'finished processing with %d outputs' % ( len(ides) )
        return self.rapid_array_compare(ides, prim_exp_id)

    def rapid_array_compare(self, valuz, expt_id):
        """docstring for rapid_array"""
        t0 = time.time()
        print 'starting rapid_array_compare'
        hitlist = [False] * len( self.dsnos_ordered )
        expt = Experiment.objects.get( id = expt_id )
        rows = []
        ide_ids, ds_lists, ds_lists_clean =  [ b[0] for b in valuz ], [b[1] for b in valuz], [b[2] for b in valuz]
        ides = IdEstimate.objects.filter( id__in = ide_ids ).distinct()
        ch1 = {}
        for ide, dsnos, dsnos_clean in zip(ides, ds_lists, ds_lists_clean):
            repstr = '%s+%s' % ( ide.peptide.id, [ b.id for b in ide.ptms.all().order_by('id') ] )
            try:
                ch1[repstr]
                pass
            except:
                ch1[repstr] = True
                for prot in Protein.objects.filter( peptoprot__peptide__idestimate = ide ).distinct():
                    hitlist = [False] * len( self.dsnos_ordered )
                    p2p = PepToProt.objects.get( peptide = ide.peptide, protein = prot )
                    row = { 'ide': ide, 'ptms' : ide.ptms.all(), 'expt' : expt, 'ds' : ide.ion.dataset, 'protein' : prot, 'peptoprot' : p2p } 
                    for ds_no in dsnos:
                        hitlist[ self.dsnos_ordered.index( ds_no ) ] = 1
                    for ds_no in dsnos_clean:
                        hitlist[ self.dsnos_ordered.index( ds_no ) ] = 2
                    row['checkers'] = hitlist
                    rows.append(row)
        print 'finished rapid_array_compare with %d outputs' % ( len(rows) )
        t1 = time.time()
        return rows

    def rapid_array_crap(self, valuz, expt_id):
        """docstring for rapid_array"""
        t0 = time.time()
        expt = Experiment.objects.get( id = expt_id )
        rows = []
        #idlist =  [ b['id'] for b in valuz]
        ides = IdEstimate.objects.filter( id__in = valuz ).distinct()
        for ide in ides:
            for prot in Protein.objects.filter( peptoprot__peptide__idestimate = ide ).distinct():
                p2p = PepToProt.objects.get( peptide = ide.peptide, protein = prot )
                row = { 'ide': ide, 'ptms' : ide.ptms.all(), 'expt' : expt, 'ds' : ide.ion.dataset, 'protein' : prot, 'peptoprot' : p2p } 
                rows.append(row)
        t1 = time.time()
        return (t1 - t0, len(rows) )

    def rapid_array(self, valuz, expt_id):
        """docstring for rapid_array"""
        t0 = time.time()
        expt = Experiment.objects.get( id = expt_id )
        rows = []
        #idlist =  [ b['id'] for b in valuz]
        ides = IdEstimate.objects.filter( id__in = valuz ).distinct()
        ch1 = {}
        for ide in ides:
            repstr = '%s+%s' % ( ide.peptide.id, [ b.id for b in ide.ptms.all().order_by('id') ] )
            try:
                ch1[repstr]
                pass
            except:
                ch1[repstr] = True
                for prot in Protein.objects.filter( peptoprot__peptide__idestimate = ide ).distinct():
                    p2p = PepToProt.objects.get( peptide = ide.peptide, protein = prot )
                    row = { 'ide': ide, 'ptms' : ide.ptms.all(), 'expt' : expt, 'ds' : ide.ion.dataset, 'protein' : prot, 'peptoprot' : p2p } 
                    rows.append(row)
        t1 = time.time()
        return rows



    def nother_rapid_array(self, valuz, expt_id):
        """docstring for rapid_array"""
        t0 = time.time()
        expt = Experiment.objects.get( id = expt_id )
        rows = []
        #idlist =  [ b['id'] for b in valuz]
        ides = IdEstimate.objects.filter( id__in = valuz ).distinct()
        for ide in ides:
            for prot in Protein.objects.filter( peptoprot__peptide__idestimate = ide ).distinct():
                p2p = PepToProt.objects.get( peptide = ide.peptide, protein = prot )
                row = { 'ide': ide, 'ptms' : ide.ptms.all(), 'expt' : expt, 'ds' : ide.ion.dataset, 'protein' : prot, 'peptoprot' : p2p } 
                rows.append(row)
        t1 = time.time()
        return rows

    def check_datasets(self, datasets, peptide, ptmcon, cutoffs = False ):
        """docstring for e"""
        td = []
        hitdic = {}
        hitlist = [False] * len(datasets)
        for ds in datasets:
            hitdic[ds.experiment] = { ds : False }
        if not ptmcon:
            td = [ {'ptms__isnull' : True}, {'peptide' : peptide } ]
        else:
            for ptm in ptmcon:
                td.append( { 'ptms__id' : ptm } )
        td += [ {'peptide' : peptide } ]
        a = IdEstimate.objects.all().annotate( count = Count('ptms'))
        for dic in td:
            a = a.filter( **dic )
        ideref = a.filter(count = len(ptmcon)).distinct()
        for i in range( len(datasets)):
            if cutoffs:
                if IdEstimate.objects.filter( ion__dataset = datasets[i], id__in = ideref, confidence__gte = datasets[i].confidence_cutoff ):
                    hitlist[i] = 2
            else:
                if IdEstimate.objects.filter( ion__dataset = datasets[i], id__in = ideref, confidence__gte = datasets[i].confidence_cutoff ):
                    hitlist[i] = 2
                elif IdEstimate.objects.filter( ion__dataset = datasets[i], id__in = ideref ):
                    hitlist[i] = 1

        return hitlist

            

        

    def best_entries(self, ideref, ptmcon, expt, user, cutoffs = False):
        """docstring for best_entry"""
        locl = []
        ptms = Ptm.objects.filter( id__in = ptmcon )
        #print 'be_ptms', [ b.id for b in ptms ]
        for ide in ideref:
            #print 'individuals', ide.id, [ b.id for b in ptms ]
            for protein in Protein.objects.filter( peptoprot__peptide__idestimate = ide): # peptoprot__peptide__idestimate__ion__dataset = ds ): 
                for ds in Dataset.objects.filter( ion__idestimate = ide, experiment = expt ).order_by( 'rank' ):
                    if user.has_perm( 'view_dataset', ds ):
                        p2p = PepToProt.objects.get( peptide = ide.peptide, protein = protein )
                        #if cutoffs and ds.dmass_cutoff > abs( ide.delta_mass ) and ds.confidence_cutoff < abs( ide.confidence ):
                        if cutoffs and ds.confidence_cutoff < abs( ide.confidence ):
                            return( { 'ide': ide, 'ptms' : ptms, 'expt' : expt, 'ds' : ds, 'protein' : protein, 'peptoprot' : p2p } )
                        elif not cutoffs:
                            return( { 'ide': ide, 'ptms' : ptms, 'expt' : expt, 'ds' : ds, 'protein' : protein, 'peptoprot' : p2p } )
                        else:
                            #print 'missed out:', ide, ptms, ds, 'actual dmass =', ide.delta_mass, 'dmass_cutoff =', ds.dmass_cutoff, 'actual confidence =', ide.confidence, 'confidence cutoff =', ds.confidence_cutoff, 'cutoff status:', cutoffs
                            pass

    def best_entries_comparison(self, ideref, ptmcon, expt, exptz, user, cutoffs = False):
        """docstring for best_entry"""
        locl = []
        ptms = Ptm.objects.filter( id__in = ptmcon )
        #print 'be_ptms', [ b.id for b in ptms ]
        for ide in ideref:
            #print 'individuals', ide.id, [ b.id for b in ptms ]
            for protein in Protein.objects.filter( peptoprot__peptide__idestimate = ide): # peptoprot__peptide__idestimate__ion__dataset = ds ): 
                for ds in Dataset.objects.filter( ion__idestimate = ide, experiment = expt ).order_by( 'rank' ):
                    if user.has_perm( 'view_dataset', ds ):
                        p2p = PepToProt.objects.get( peptide = ide.peptide, protein = protein )
                        #if cutoffs and ds.dmass_cutoff > abs( ide.delta_mass ) and ds.confidence_cutoff < abs( ide.confidence ):
                        if cutoffs and ds.confidence_cutoff < abs( ide.confidence ):
                            d1 = { 'ide': ide, 'ptms' : ptms, 'expt' : expt, 'ds' : ds, 'protein' : protein, 'peptoprot' : p2p } 
                        elif not cutoffs:
                            d1 = { 'ide': ide, 'ptms' : ptms, 'expt' : expt, 'ds' : ds, 'protein' : protein, 'peptoprot' : p2p } 





class MassSearch( ExptArrayAssemble ):
    """


    """
    def get_ides_from_mass( self, mass, tolerance ):
        ides = IdEstimate.objects.filter( ion__precursor_mass__lte = mass + tolerance,  ion__precursor_mass__gte = mass - tolerance ).order_by( 'peptide__sequence' ) 
	return ides

    def get_unique_peptide_ides_from_mass( self, mass, tolerance, user ):
        ml = []
        ides = IdEstimate.objects.filter( ion__precursor_mass__lte = mass + tolerance,  ion__precursor_mass__gte = mass - tolerance ).distinct().order_by( 'peptide__sequence' ) 
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

    def get_unique_peptide_ides_from_mz( self, mass, tolerance, user ):
        ml = []
        ides = IdEstimate.objects.filter( ion__mz__lte = mass + tolerance,  ion__mz__gte = mass - tolerance ).distinct().order_by( 'peptide__sequence' ) 
        #peptides = set( [ b.peptide for b in ides ] )
        return self.get_peptide_array( ides, user, ion__mz__lte = mass + tolerance,  ion__mz__gte = mass - tolerance )

    def get_unique_peptide_ides_from_sequence( self, sequence, user ):
        ml = []
        ides = IdEstimate.objects.filter( peptide__sequence__icontains = sequence ).distinct().order_by( 'peptide__sequence' ) 
        #peptides = set( [ b.peptide for b in ides ] )
        return self.get_peptide_array( ides, user, ion__idestimate__peptide__sequence__icontains = sequence )

    def get_peptide_array_from_ptm( self, ptm_obj, user ):
        ml = []
        ides = IdEstimate.objects.filter( ptms = ptm_obj ).order_by( 'peptide__sequence' ) 
        peptides = set( [ b.peptide for b in ides ] )
        return self.get_peptide_array( ides, user, ion__idestimate__ptms = ptm_obj )

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
        #for ide in ides:
        for expt in Experiment.objects.filter( ion__idestimate__in = ides, **kwargs ).distinct():# ion__precursor_mass__lte = mass + tolerance,  ion__precursor_mass__gte = mass - tolerance ):
            peptides = Peptide.objects.filter( idestimate__in = ides, idestimate__ion__experiment = expt ).distinct()
            ml += self.get_peptide_array_expt_restricted( ides, peptides, expt, user, cutoffs = True )
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
        ids = IdEstimate.objects.filter( ion__experiment = expt_obj )
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
	    peplist = p.peptide_set.filter( proteins = p, ion__experiment = expt_obj )
   	    for pep in peplist:
                idlist = pep.idestimate_set.filter( peptide__proteins = p, ion__experiment = expt_obj )
                for ide in idlist:
		    flist.append( [ p, pep, ide ] )
	return flist

    def extract_uniprot_id( self, crude_id ):
	return crude_id.split('|')[1]

    def get_common_alleles( self, expt_obj ):
	return Allele.objects.filter( cellline__experiment = expt_obj, antibody__experiment = expt_obj )

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
            elif dic[k]['qtype'] == 'ptm':
                al = PtmSearch()
                expts.append( set( al.get_experiments_basic( dic[k]['qstring'] ) ) )
        return list( set.intersection( *expts ) )


