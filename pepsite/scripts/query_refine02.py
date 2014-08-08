import os
import sys
import datetime
from django.utils.timezone import utc
from django.db.models import *
import time
from django.db import connection

PROJ_NAME = 'hdome'
APP_NAME = 'pepsite'

CURDIR = os.path.dirname( os.path.abspath( __file__ ) )

#print CURDIR

sys.path.append( CURDIR + '/../..' ) # gotta hit settings.py for site

os.environ[ 'DJANGO_SETTINGS_MODULE' ] = '%s.settings' %( PROJ_NAME )

import django #required
django.setup() #required

from django.contrib.auth.models import User
from pepsite.models import *
from pepsite import dbtools
import pepsite.uploaders

class QueryOpt( object ):

    def simple_expt_query(self, exp_id, user_id, perm = False):
        """docstring for simple_expt_query"""
        t0 = time.time()
        user = User.objects.get( id = user_id )
        p1 = Peptide.objects.filter(idestimate__ion__experiment = exp_id, idestimate__ion__dataset__confidence_cutoff__lte = F('idestimate__confidence')).distinct()
        v1 = IdEstimate.objects.filter(ion__experiment = exp_id, ion__dataset__confidence_cutoff__lte = F('confidence')).extra( select = {'dm' : "abs(delta_mass)"}).annotate( ptmc = Count('ptms__id') ).distinct()
        if perm:
            dsets = Dataset.objects.filter( experiment__id = exp_id ).distinct()
            for ds in Experiment.objects.get( id = exp_id ).dataset_set.all():
                if not user.has_perm( 'view_dataset', ds ):
                    dsets = dsets.exclude( ds )
            p1 = p1.filter( idestimate__ion__dataset__in = dsets ).distinct()
            v1 = v1.filter( ion__dataset__in = dsets ).distinct()

        #lv1 = len(v1)
        #lp1 = len(p1)
        #print lv1, lp1
        i = 0
        j = 0
        for pep in p1:
            i += 1
            #print 'peptide %d of %d:' % ( i, lp1 )
            v2 = IdEstimate.objects.filter(ion__experiment = exp_id, peptide = pep, ion__dataset__confidence_cutoff__lte = F('confidence')).extra( select = {'dm' : "abs(delta_mass)"}).annotate( ptmc = Count('ptms__id') ).distinct()
            ptmz = []
            for ide in v2:
                ptmcon = [ b.id for b in ide.ptms.all().order_by( 'id' ) ]
                if ptmcon not in ptmz:
                    ptmz.append( ptmcon )
            #ptms = Ptm.objects.filter(idestimate__peptide = pep, idestimate__ion__experiment = expno, idestimate__ion__dataset__confidence_cutoff__lte = F('idestimate__confidence') ).distinct()
            #thruz = IdEstimate.ptms.through.objects.filter( idestimate__ion__experiment = expno, idestimate__in = v2 ).distinct()
            k = 0
            for ptmcon in ptmz:
                a = v2
                if not ptmcon:
                    a = a.filter( ptms__isnull = True, ptmc = 0 ).distinct().order_by( 'dm' )[0]
                    k += 1
                else:
                    a = a.filter( ptmc = len(ptmcon) ).distinct()
                    for ptm in ptmcon:
                       a = v2.filter( ptms = ptm )
                    a = a.distinct().order_by( 'dm' )[0]
                    k += 1
                j += k
                #v2 = v2.filter( ptms = ptm )
            v2 = v2.distinct().annotate( best_dm = Min( 'delta_mass' ) ).filter( best_dm = F('delta_mass') ).distinct()
            #print '%d outputs' % k
        t1 = time.time()
        return (t1 - t0, j, exp_id, user_id, perm)
        print 'f timing:', t1-t0,  ', outputs:', j

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
        return (v1, t1 - t0, j, exp_id, user_id, perm)

    def mkiv_expt_query(self, exp_id, user_id, perm = False):
        """docstring for simple_expt_query"""
        t0 = time.time()
        cursor = connection.cursor()
        cursor.execute( "DROP VIEW IF EXISTS \"allowedides\"" )
        cursor.execute( "DROP VIEW IF EXISTS \"disallowedides\"" )
        expt = Experiment.objects.get( id = exp_id )
        print expt.title
        user = User.objects.get( id = user_id )
        qq1a = IdEstimate.objects.filter( ion__dataset__in = dsets, ion__dataset__confidence_cutoff__lt = F('confidence') ).distinct().query
        cursor.execute( 'CREATE TEMP VIEW \"allowedides\" AS ' + str( qq1 ) )
        qq1b = IdEstimate.objects.filter( ion__dataset__in = dsets, ion__dataset__confidence_cutoff__gte = F('confidence') ).distinct().query
        cursor.execute( 'CREATE TEMP VIEW \"disallowedides\" AS ' + str( qq2 ) )
        qq4 = "SELECT DISTINCT allowedides.id FROM suppcorrect t1 \
                INNER JOIN suppavail t2 ON (t2.min = t1.min AND t2.ptmstr = t1.ptmstr) \
                INNER JOIN allowedides ON (t2.id = allowedides.id AND t1.min = abs(allowedides.delta_mass))"
        cursor.execute( qq4 )
        ides = cursor.fetchall()
        j = len(ides)
        cursor.execute( "DROP VIEW IF EXISTS \"allowedides\"" )
        cursor.execute( "DROP VIEW IF EXISTS \"suppavail\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"suppcorrect\"" )
        cursor.close()
        #ideobjs = IdEstimate.objects.filter( id__in = [b[0] for b in ides] ).distinct()
        #ideobjs = ideobjs.filter( 
        t1 = time.time()
        return (ides, t1 - t0, j, exp_id, user_id, perm)

    def mkiv_create_views(self, exp_id, user_id, perm = False):
        """docstring for simple_expt_query"""
        t0 = time.time()
        cursor = connection.cursor()
        cursor.execute( "DROP VIEW IF EXISTS \"allowedides\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"suppavail\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"shizzle\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"suppcorrect\"" )
        cursor.execute( "DROP VIEW IF EXISTS \"sv2\"" )
        expt = Experiment.objects.get( id = exp_id )
        print expt.title
        user = User.objects.get( id = user_id )
        # Generate SQL for finding permitted IdEstimates
        qq1 = IdEstimate.objects.filter( ion__experiment = expt, ion__dataset__confidence_cutoff__lt = F('confidence') ).distinct().query
        cursor.execute( 'CREATE VIEW \"allowedides\" AS ' + str( qq1 ) )
        # Generate SQL for finding idestimate-ptms combo with lowest possible abs(delta_mass) [per experiment] 
        qq2 = "CREATE VIEW suppavail AS SELECT foo.id, foo.ptmstr, foo.experiment_id, \
                min(abs(foo.delta_mass)) FROM \
                ( select t1.id, t1.peptide_id, t3.experiment_id, \
                t1.delta_mass, array_to_string(array_agg(t2.ptm_id order by t2.ptm_id),'+') AS ptmstr \
                FROM pepsite_idestimate t1 \
                LEFT OUTER JOIN pepsite_idestimate_ptms t2 \
                ON (t2.idestimate_id = t1.id) \
                INNER JOIN pepsite_ion t3 \
                ON ( t1.ion_id = t3.id ) \
                GROUP BY t1.id, t1.peptide_id, t3.experiment_id \
                ) AS foo \
                GROUP BY foo.id, foo.ptmstr, foo.experiment_id \
                "
        # Find peptide-ptms combo with lowest possible abs(delta_mass) [per experiment]
        qq3 = "CREATE VIEW suppcorrect AS SELECT DISTINCT \
                foo.peptide_id, foo.ptmstr, foo.experiment_id, min(abs(foo.delta_mass)) \
                FROM (select t1.id, t1.confidence, t1.peptide_id, t1.delta_mass, \
                t3.experiment_id, \
                array_to_string(array_agg(t2.ptm_id order by t2.ptm_id),'+') AS ptmstr \
                FROM pepsite_idestimate t1 \
                LEFT OUTER JOIN pepsite_idestimate_ptms t2 \
                ON (t2.idestimate_id = t1.id) \
                INNER JOIN pepsite_ion t3 \
                ON (t1.ion_id = t3.id ) \
                GROUP BY t1.id, t3.experiment_id \
                ) AS foo \
                GROUP BY foo.peptide_id, foo.ptmstr, foo.experiment_id"
        # Locate those idestimates whch represent best value for both peptide-ptms and idestimate-ptms
        qq4 = "SELECT DISTINCT t3.id FROM \
                suppcorrect t1 \
                INNER JOIN suppavail t2 ON (t2.min = t1.min AND t2.ptmstr = t1.ptmstr) \
                INNER JOIN allowedides t3 ON (t2.id = t3.id AND t1.min = abs(t3.delta_mass))"
        # now let us create a master view which contains prepackaged peptide data for display
        qqmaster = " \
                "
        cursor.execute( qq2 )
        cursor.execute( 'SELECT COUNT(*) FROM suppavail' )
        print 'suppavail', cursor.fetchall(  )
        cursor.execute( qq3 )
        cursor.execute( 'SELECT COUNT(*) FROM suppcorrect' )
        print 'suppcorrect', cursor.fetchall(  )
        cursor.execute( qq4 )
        ides = cursor.fetchall()
        j = len(ides)
        cursor.close()
        #ideobjs = IdEstimate.objects.filter( id__in = [b[0] for b in ides] ).distinct()
        #ideobjs = ideobjs.filter( 
        t1 = time.time()
        #print 'time taken = %f' % t1-t0
        return (ides, t1 - t0, j, exp_id, user_id, perm)

    def mkiii_compare_query(self, prim_exp_id, other_exp_ids, user_id, primary_clean = True, others_clean = False, perm = False):
        """docstring for simple_expt_query"""
        t0 = time.time()
        cursor = connection.cursor()
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
        cursor.execute( "DROP VIEW IF EXISTS \"compcorrect\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"sv2\" CASCADE" )
        expt = Experiment.objects.get( id = prim_exp_id )
        exptz = Experiment.objects.filter( id__in = other_exp_ids )
        print expt.title
        user = User.objects.get( id = user_id )
        dsets = Dataset.objects.filter( experiment__id = exp_id ).distinct()
        for ds in Experiment.objects.get( id = exp_id ).dataset_set.all():
            if not user.has_perm( 'view_dataset', ds ):
                dsets = dsets.exclude( ds )
        dsets_compare = Dataset.objects.filter( experiment__id__in = other_exp_ids ).distinct()
        for ds in dsets_compare:
            if not user.has_perm( 'view_dataset', ds ):
                dsets_compare = dsets_compare.exclude( ds )
        dsets_compare.order_by ( 'experiment', 'title' )
        self.dsnos_ordered = [ b.id for b in dsets_compare ]
        qq1_dj = IdEstimate.objects.filter( ion__dataset__in = dsets ).distinct()
        if primary_clean:
            qq1_dj = qq1_dj.filter( ion__dataset__confidence_cutoff__lte = F('confidence') ).distinct()
        qq1_dj_compare = IdEstimate.objects.filter( ion__dataset__in = dsets_compare ).distinct()
        qq1_dj_compare_clean = qq1_dj_compare.filter( ion__dataset__confidence_cutoff__lte = F('confidence') ).distinct()
        qq1 = qq1_dj.query
        qq1_compare = qq1_dj_compare.query
        qq1_compare_clean = qq1_dj_compare_clean.query
        cursor.execute( 'CREATE VIEW \"allowedides\" AS ' + str( qq1 ) )
        cursor.execute( 'CREATE VIEW \"allidescompare\" AS ' + str( qq1_compare ) )
        cursor.execute( 'CREATE VIEW \"cleanidescompare\" AS ' + str( qq1_compare_clean ) )
        qq2 = "CREATE VIEW suppavail AS SELECT foo.id, foo.ptmstr,\
                min(abs(foo.delta_mass)) FROM (select t1.id, t1.confidence, t1.peptide_id, \
                t1.delta_mass, array_to_string(array_agg(t2.ptm_id order by t2.ptm_id),'+') AS ptmstr FROM \
                pepsite_idestimate t1 LEFT OUTER JOIN pepsite_idestimate_ptms t2 ON (t2.idestimate_id = t1.id) \
                \
                group by t1.id, t1.peptide_id) AS foo \
                GROUP BY foo.id, foo.ptmstr \
                "
        qq2a = "CREATE VIEW sv2 AS SELECT * FROM suppavail WHERE adm = min"
        qq3 = "CREATE VIEW suppcorrect AS SELECT DISTINCT foo.peptide_id, foo.ptmstr, min(abs(foo.delta_mass)) \
                FROM (select t1.id, t1.confidence, t1.peptide_id, t1.delta_mass, \
                array_to_string(array_agg(t2.ptm_id order by t2.ptm_id),'+') AS ptmstr FROM pepsite_idestimate \
                t1 LEFT OUTER JOIN pepsite_idestimate_ptms t2 ON (t2.idestimate_id = t1.id) \
                GROUP BY t1.id) AS \
                foo GROUP BY foo.peptide_id, foo.ptmstr"
        qq3a = "CREATE VIEW compcorrect AS SELECT DISTINCT foo.peptide_id, foo.ptmstr, min(abs(foo.delta_mass)) \
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
        qq4 = "CREATE VIEW possibles AS \
                SELECT DISTINCT allowedides.id as id, t2.ptmstr, t1.peptide_id FROM suppcorrect t1 \
                INNER JOIN suppavail t2 ON (t2.min = t1.min AND t2.ptmstr = t1.ptmstr) \
                INNER JOIN allowedides ON (t2.id = allowedides.id AND t1.min = abs(allowedides.delta_mass))"
        qq41 = "CREATE VIEW comparepossibles AS \
                SELECT DISTINCT allidescompare.id as id, t2.ptmstr, t1.peptide_id FROM suppcorrect t1 \
                INNER JOIN suppavail t2 ON (t2.min = t1.min AND t2.ptmstr = t1.ptmstr) \
                INNER JOIN allidescompare ON (t2.id = allidescompare.id)"
        qq42 = "CREATE VIEW cleancomparepossibles AS \
                SELECT DISTINCT cleanidescompare.id as id, t2.ptmstr, t1.peptide_id FROM suppcorrect t1 \
                INNER JOIN suppavail t2 ON (t2.min = t1.min AND t2.ptmstr = t1.ptmstr) \
                INNER JOIN cleanidescompare ON (t2.id = cleanidescompare.id)"
        qq4a = "CREATE VIEW ideproduct AS \
                SELECT DISTINCT id FROM \
                possibles"
        qq5 = "CREATE VIEW ideproduct2 AS \
                SELECT * FROM \
                (SELECT DISTINCT t1.peptide_id, t1.ptmstr, array_agg(t6.id) as dsid FROM suppcorrect t1 \
                INNER JOIN suppavail t2 ON (t2.min = t1.min AND t2.ptmstr = t1.ptmstr) \
                INNER JOIN allidescompare t4 ON (t2.id = t4.id) \
                INNER JOIN pepsite_idestimate t3 ON ( t4.id = t3.id ) \
                INNER JOIN pepsite_ion t5 ON ( t3.ion_id = t5.id ) \
                INNER JOIN pepsite_dataset t6 ON ( t5.dataset_id = t6.id )\
                GROUP BY t1.peptide_id, t1.ptmstr) AS foo"
        qq6 = "CREATE VIEW dsids AS \
                SELECT t1.id, t1.ptmstr, array_agg(t6.id) as dsid FROM suppcorrect t1 \
                INNER JOIN \
                "
        qq6 = "CREATE VIEW ideproduct2 AS \
                SELECT * FROM \
                (SELECT t1.id, t1.peptide_id, t1.ptmstr, array_agg(t6.id) as dsids  FROM \
                comparepossibles t1 \
                INNER JOIN allidescompare t2 ON ( t1.id = t2.id ) \
                INNER JOIN pepsite_ion t5 ON ( t2.ion_id = t5.id ) \
                INNER JOIN pepsite_dataset t6 ON ( t5.dataset_id = t6.id )\
                GROUP BY t1.id, t1.peptide_id, t1.ptmstr \
                ) AS foo \
                "
        qq6a = "CREATE VIEW ideproduct3 AS \
                SELECT * FROM \
                (SELECT t1.id, t1.peptide_id, t1.ptmstr, array_agg(t6.id) as dsids  FROM \
                cleancomparepossibles t1 \
                INNER JOIN cleanidescompare t2 ON ( t1.id = t2.id ) \
                INNER JOIN pepsite_ion t5 ON ( t2.ion_id = t5.id ) \
                INNER JOIN pepsite_dataset t6 ON ( t5.dataset_id = t6.id )\
                GROUP BY t1.id, t1.peptide_id, t1.ptmstr \
                ) AS foo \
                "
        qq7 = "CREATE VIEW combinedideproduct AS \
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
        #cursor.execute( qq3a )
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
        cursor.execute( "DROP VIEW IF EXISTS \"compcorrect\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"sv2\" CASCADE" )
        cursor.close()
        t1 = time.time()
        return (ides, t1 - t0, j, exp_id, user_id, perm)

    def master_views_query(self, primary_clean = True, others_clean = False, perm = False):
        """docstring for simple_expt_query"""
        t0 = time.time()
        cursor = connection.cursor()
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
        cursor.execute( "DROP VIEW IF EXISTS \"suppavail_all\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"augmented_ides\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"suppcorrect\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"compcorrect\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"sv2\" CASCADE" )
        #expt = Experiment.objects.get( id = prim_exp_id )
        #exptz = Experiment.objects.filter( id__in = other_exp_ids )
        #print expt.title
        #user = User.objects.get( id = user_id )
        #dsets = Dataset.objects.filter( experiment__id = exp_id ).distinct()
        #for ds in Experiment.objects.get( id = exp_id ).dataset_set.all():
        #    if not user.has_perm( 'view_dataset', ds ):
        #        dsets = dsets.exclude( ds )
        #dsets_compare = Dataset.objects.filter( experiment__id__in = other_exp_ids ).distinct()
        #for ds in dsets_compare:
        #    if not user.has_perm( 'view_dataset', ds ):
        #        dsets_compare = dsets_compare.exclude( ds )
        #dsets_compare.order_by ( 'experiment', 'title' )
        #self.dsnos_ordered = [ b.id for b in dsets_compare ]
        #qq1_dj = IdEstimate.objects.filter( ion__dataset__in = dsets ).distinct()
        #if primary_clean:
        #    qq1_dj = qq1_dj.filter( ion__dataset__confidence_cutoff__lte = F('confidence') ).distinct()
        #qq1_dj_compare = IdEstimate.objects.filter( ion__dataset__in = dsets_compare ).distinct()
        #qq1_dj_compare_clean = qq1_dj_compare.filter( ion__dataset__confidence_cutoff__lte = F('confidence') ).distinct()
        #qq1 = qq1_dj.query
        #qq1_compare = qq1_dj_compare.query
        #qq1_compare_clean = qq1_dj_compare_clean.query
        #cursor.execute( 'CREATE TEMP VIEW \"allowedides\" AS ' + str( qq1 ) )
        #cursor.execute( 'CREATE TEMP VIEW \"allidescompare\" AS ' + str( qq1_compare ) )
        #cursor.execute( 'CREATE TEMP VIEW \"cleanidescompare\" AS ' + str( qq1_compare_clean ) )
        qq2 = "CREATE TEMP VIEW suppavail_all AS SELECT foo.id, foo.ptmarray, foo.ptmstr, foo.peptide_id \
                FROM (select t1.id, t1.confidence, t1.peptide_id, \
                t1.delta_mass, array_agg(t2.ptm_id order by t2.ptm_id) AS ptmarray, array_to_string(array_agg(t2.ptm_id order by t2.ptm_id),'+') AS ptmstr FROM \
                pepsite_idestimate t1 LEFT OUTER JOIN pepsite_idestimate_ptms t2 ON (t2.idestimate_id = t1.id) \
                group by t1.id, t1.peptide_id, t1.peptide_id) AS foo \
                "
        qq2 = "CREATE VIEW suppavail_all AS SELECT foo.id, foo.ptmarray, foo.ptmstr, foo.peptide_id, foo.ptmz \
                FROM (select t1.id, t1.confidence, t1.peptide_id, \
                t1.delta_mass, array_agg(t2.ptm_id ORDER BY t2.ptm_id) AS ptmarray, array_to_string(array_agg(t2.ptm_id order by t2.ptm_id),'+') AS ptmstr, \
                array_agg(t3.description order by t3.id) AS ptmz FROM \
                pepsite_idestimate t1 LEFT OUTER JOIN pepsite_idestimate_ptms t2 ON (t2.idestimate_id = t1.id) \
                INNER JOIN pepsite_ptm t3 ON ( t3.id = t2.ptm_id ) \
                GROUP BY t1.id, t1.peptide_id, t1.peptide_id) AS foo \
                "
        qq2a = "CREATE TEMP VIEW augmented_ides AS \
                SELECT t1.id, t1.peptide_id, t1.ptmarray, t1.ptmstr, t2.confidence, t2.delta_mass, \
                t2.\"isRemoved\", t3.mz, t3.precursor_mass, t3.retention_time, \
                t4.confidence_cutoff, t4.id as dataset_id, t5.id as experiment_id, \
                t6.id as cell_line_id \
                FROM \
                suppavail_all t1 INNER JOIN pepsite_idestimate t2 ON (t1.id = t2.id) \
                INNER JOIN pepsite_ion t3 ON (t2.ion_id = t3.id) \
                INNER JOIN pepsite_dataset t4 on (t3.dataset_id = t4.id) \
                INNER JOIN pepsite_experiment t5 on (t3.experiment_id = t5.id) \
                INNER JOIN pepsite_cellline t6 on (t5.cell_line_id = t6.id) \
                INNER JOIN pepsite_peptide t7 on (t2.peptide_id = t7.id) \
                "
        qq3 = "CREATE TEMP VIEW prot_ides AS \
                SELECT t1.id as p2p_id, t1.protein_id, t2.* FROM pepsite_peptoprot t1 \
                INNER JOIN augmented_ides t2 ON \
                ( t2.peptide_id = t1.peptide_id ) \
                "
        qqresult = "SELECT * FROM augmented_ides"
        cursor.execute( qq2 )
        cursor.execute( qq2a )
        cursor.execute( qq3 )
        cursor.execute( 'SELECT COUNT (*) FROM pepsite_idestimate' )
        print 'idestimate table length =', cursor.fetchall(  )
        cursor.execute( 'SELECT COUNT (*) FROM augmented_ides' )
        print 'augmented ide view length =', cursor.fetchall(  )
        cursor.execute( 'SELECT COUNT (*) FROM prot_ides' )
        print 'prot ide view length =', cursor.fetchall(  )
        cursor.execute( qqresult )
        ides_aug = cursor.fetchall(  )
        print ides_aug[:4]
        cursor.execute( "DROP VIEW IF EXISTS \"allowedides\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"suppavail_all\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"augmented_ides\" CASCADE" )
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
        cursor.execute( "DROP VIEW IF EXISTS \"compcorrect\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"sv2\" CASCADE" )
        cursor.close()
        t1 = time.time()
        print 'time taken =', t1-t0
        return None
        return (ides, t1 - t0, j, exp_id, user_id, perm)


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
        return (t1 - t0, len(rows) )

    def rapid_array_compare(self, valuz, expt_id):
        """docstring for rapid_array"""
        t0 = time.time()
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
        t1 = time.time()
        return (t1 - t0, len(rows) )

    def make_array_from_ide_vals(self, valuz, expt_id):
        """docstring for make_array_from_ides"""
        t0 = time.time()
        rows = []
        expt = Experiment.objects.get( id = expt_id )
        i = 0
        for local in valuz:
            i += 1
            #print i,
            ide = IdEstimate.objects.get( id = local )
            #pep = ide.peptide
            ptms = ide.ptms.all()
            ds = ide.ion.dataset
            proteins = Protein.objects.filter( peptoprot__peptide__idestimate = ide ).distinct()
            #print proteins.count(),
            for prot in proteins:
                p2p = PepToProt.objects.get( peptide = ide.peptide, protein = prot )
                row = { 'ide': ide, 'ptms' : ptms, 'expt' : expt, 'ds' : ds, 'protein' : prot, 'peptoprot' : p2p } 
                rows.append(row)
        t1 = time.time()
        return ( t1 - t0, rows )


if __name__=='__main__':
    exp_id = 1
    other_exp_ids = [1,2]
    user_id = 1
    print 'here we go... expecting 1578 returns...\n'
    qo = QueryOpt()
    q2r = qo.mkiv_create_views( 1, 1 )
    ar1 = q2r[0]
    #print ar1
    #print ar1.count()
    #print dir(q1r[0])
    print '\n\nmkii_expt_query ran in %f seconds with %d outputs for expt_id = %d, user_id = %d, permission checking = %r\n\n' %  q2r[1:]   #print 'simple_expt_query ran in %f seconds with %d outputs for expt_id = %d, user_id = %d, permission checking = %r' % qo.simple_expt_query( exp_id, user_id, perm = False)
    #q3r = qo.mkiii_compare_query( exp_id, other_exp_ids, user_id, perm = False)
    #print '\n\nmkiii_expt_query ran in %f seconds with %d outputs for expt_id = %d, user_id = %d, permission checking = %r\n\n' %  q3r[1:]   #print 'simple_expt_query ran in %f seconds with %d outputs for expt_id = %d, user_id = %d, permission checking = %r' % qo.simple_expt_query( exp_id, user_id, perm = False)
    #print q3r[0][:4]
    #ar1 = q3r[0][:]
    #print '\n\nrapid_array_compare ran for %f seconds and returned %d results\n\n' % ( qo.rapid_array_compare(ar1, exp_id)  )
    #q2r = qo.make_array_from_ide_vals( ar1, exp_id )
    #print '\n\nassembled array of size %d in %f seconds\n\n' % ( q2r[1].count(), q2r[0] )
    #print q2r[1][:3]
    #print 'simple_expt_query ran in %f seconds with %d outputs for expt_id = %d, user_id = %d, permission checking = %r' % qo.simple_expt_query( exp_id, user_id, perm = True)

    #i = 0
    #for ide in v1:
    #    i += 1
    #    print '%d of %d:' % ( i, lv1 )
    #    v2 = IdEstimate.objects.filter(ion__experiment = 2, peptide = ide.peptide, ion__dataset__confidence_cutoff__lte = F('confidence')).annotate( ptmc = Count('ptms__id') ).filter( ptmc = len( ide.ptms.all() )).distinct()
    #    ptms = ide.ptms.all()
    #    for ptm in ptms:
    #        v2 = v2.filter( ptms = ptm )
    #    v2 = v2.distinct().annotate( best_dm = Min( 'delta_mass' ) ).filter( best_dm = F('delta_mass') ).distinct()
    #    print '%d outputs' % len(v2)


