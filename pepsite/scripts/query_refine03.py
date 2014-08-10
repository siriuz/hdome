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

    def mkiv_create_views(self, exp_id, user_id, perm = False):
        """docstring for simple_expt_query"""
        t0 = time.time()
        cursor = connection.cursor()
        cursor.execute( "DROP VIEW IF EXISTS \"allowedides\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"suppavail\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"prot_expt\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"semi_master\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"grand_master\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"master_allowed\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"master_disallowed\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"allowed_comparisons\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"disallowed_comparisons\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"all_compares\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"suppcorrect\"" )
        cursor.execute( "DROP VIEW IF EXISTS \"sv2\"" )
        expt = Experiment.objects.get( id = exp_id )
        print expt.title
        user = User.objects.get( id = user_id )
        # Generate SQL for finding permitted IdEstimates
        qq1 = IdEstimate.objects.filter( ion__experiment = expt, ion__dataset__confidence_cutoff__lt = F('confidence') ).distinct().query
        cursor.execute( 'CREATE VIEW \"allowedides\" AS ' + str( qq1 ) )
        # Generate SQL for finding idestimate-ptms combo with lowest possible abs(delta_mass) [per experiment] 
        # NOTE: This contins one row per IdEstimate - it can be a starting point for a 'master' view
        qq2 = "CREATE VIEW suppavail AS SELECT foo.id, foo.ptmstr, foo.experiment_id, \
                min(abs(foo.delta_mass)) minadm, foo.ptmarray, foo.ptmdescarray FROM \
                ( select t1.id, t1.peptide_id, t3.experiment_id, \
                t1.delta_mass, array_to_string(array_agg(t2.ptm_id order by t2.ptm_id),'+') AS ptmstr, \
                array_agg((t2.ptm_id, t4.description)::text order by t2.ptm_id) AS ptmarray, \
                array_agg(t4.description order by t2.ptm_id) AS ptmdescarray \
                FROM pepsite_idestimate t1 \
                LEFT OUTER JOIN pepsite_idestimate_ptms t2 \
                ON (t2.idestimate_id = t1.id) \
                LEFT OUTER JOIN pepsite_ptm t4 \
                ON ( t2.ptm_id = t4.id ) \
                INNER JOIN pepsite_ion t3 \
                ON ( t1.ion_id = t3.id ) \
                GROUP BY t1.id, t1.peptide_id, t3.experiment_id \
                ) AS foo \
                GROUP BY foo.id, foo.ptmstr, foo.ptmarray, foo.ptmdescarray, foo.experiment_id \
                "
        # Find peptide-ptms combo with lowest possible abs(delta_mass) [per experiment]
        qq3 = "CREATE VIEW suppcorrect AS SELECT DISTINCT \
                foo.peptide_id, foo.ptmstr, foo.experiment_id, min(abs(foo.delta_mass)) as minadm \
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
                INNER JOIN suppavail t2 ON (t2.minadm = t1.minadm AND t2.ptmstr = t1.ptmstr) \
                INNER JOIN allowedides t3 ON (t2.id = t3.id AND t1.minadm = abs(t3.delta_mass))"
        # Assign correct protein identifications and peptide positionings on a per experiment basis
        qqprot = "CREATE VIEW prot_expt AS SELECT DISTINCT \
                t1.id as p2p_id, t1.peptide_id, t1.protein_id, array_agg(t2.position_id ORDER BY t2.position_id) as posnarray, \
                array_to_string( array_agg( CAST(t3.initial_res AS text) || '-' || CAST(t3.final_res AS text) ORDER BY t3.initial_res ), ' ') as posnstr, \
                t4.description AS protein_description, t4.prot_id as protein_uniprot_code \
                FROM pepsite_peptoprot t1 \
                LEFT OUTER JOIN pepsite_peptoprot_positions t2 \
                ON ( t1.id = t2.peptoprot_id  ) \
                LEFT OUTER JOIN pepsite_position t3 \
                ON ( t2.position_id = t3.id ) \
                LEFT OUTER JOIN pepsite_protein t4 \
                ON ( t1.protein_id = t4.id ) \
                GROUP BY t1.id, t1.peptide_id, t1.protein_id, t4.description, t4.prot_id \
                "
        # now let us create a master view which contains prepackaged peptide data for display
        qqsemimaster = "CREATE VIEW semi_master AS \
                SELECT t1.*, t2.peptide_id, t2.delta_mass, abs( t2.delta_mass ) as abdm, \
                t2.confidence, t2.\"isRemoved\",  t2.ion_id, \
                t3.title as experiment_title, t4.sequence as peptide_sequence, \
                char_length( t4.sequence ) as peptide_length, \
                t5.charge_state, t5.retention_time, t5.dataset_id, \
                t6.confidence_cutoff \
                FROM \
                suppavail t1 \
                INNER JOIN pepsite_idestimate t2 \
                ON ( t1.id = t2.id ) \
                INNER JOIN pepsite_experiment t3 \
                ON ( t1.experiment_id = t3.id ) \
                INNER JOIN pepsite_peptide t4 \
                ON ( t2.peptide_id = t4.id ) \
                INNER JOIN pepsite_ion t5 \
                ON ( t5.id = t2.ion_id ) \
                INNER JOIN pepsite_dataset t6 \
                ON ( t6.id = t5.dataset_id ) \
                "
        qqmaster = "CREATE MATERIALIZED VIEW grand_master AS \
                SELECT t1.*, \
                t3.protein_id, t3.posnarray, t3.posnstr, \
                t3.protein_description, t3.protein_uniprot_code \
                FROM semi_master t1\
                INNER JOIN pepsite_experiment_proteins t2 \
                ON ( t1.experiment_id = t2.experiment_id ) \
                INNER JOIN prot_expt t3 \
                ON ( t3.protein_id = t2.protein_id AND t3.peptide_id = t1.peptide_id ) \
                "
        qqallowed = "CREATE MATERIALIZED VIEW master_allowed AS \
                SELECT DISTINCT ON (t1.peptide_id, t1.ptmstr, t1.experiment_id, t1.protein_id) t1.* \
                FROM grand_master t1 \
                INNER JOIN suppcorrect t2 \
                ON (t1.peptide_id = t2.peptide_id AND t1.ptmstr = t2.ptmstr \
                AND t1.abdm = t2.minadm ) \
                WHERE t1.confidence > t1.confidence_cutoff and t1.\"isRemoved\" = false \
                ORDER BY t1.peptide_id, t1.ptmstr, t1.experiment_id, t1.protein_id, t1.ion_id \
                "
        qqdisallowed = "CREATE MATERIALIZED VIEW master_disallowed AS \
                SELECT * FROM grand_master \
                EXCEPT \
                SELECT * FROM master_allowed \
                "
        qqallowcompare = "CREATE VIEW allowed_comparisons AS \
                SELECT t1.peptide_id, t1.ptmstr, array_agg( DISTINCT t1.experiment_id ORDER BY t1.experiment_id ) AS allowed_array  \
                FROM master_allowed t1 \
                GROUP BY t1.peptide_id, t1.ptmstr \
                "
        qqdisallowcompare = "CREATE VIEW disallowed_comparisons AS \
                SELECT t1.peptide_id, t1.ptmstr, array_agg( DISTINCT t1.experiment_id ORDER BY t1.experiment_id ) AS disallowed_array \
                FROM master_disallowed t1 \
                GROUP BY t1.peptide_id, t1.ptmstr \
                "
        qqallcompares = "CREATE MATERIALIZED VIEW allcompares AS \
                SELECT t1.*, t2.allowed_array, t3.disallowed_array \
                FROM grand_master t1 \
                LEFT OUTER JOIN allowed_comparisons t2 \
                ON ( t1.peptide_id = t2.peptide_id AND t1.ptmstr = t2.ptmstr ) \
                LEFT OUTER JOIN disallowed_comparisons t3 \
                ON ( t1.peptide_id = t3.peptide_id AND t1.ptmstr = t3.ptmstr ) \
                "
        cursor.execute( qq2 )
        cursor.execute( 'SELECT COUNT(*) FROM suppavail' )
        print 'suppavail', cursor.fetchall(  )
        cursor.execute( qq3 )
        cursor.execute( 'SELECT COUNT(*) FROM suppcorrect' )
        print 'suppcorrect', cursor.fetchall(  )
        cursor.execute( qqprot )
        cursor.execute( 'SELECT COUNT(*) FROM prot_expt' )
        print 'prot_expt', cursor.fetchall(  )
        cursor.execute( qqsemimaster )
        cursor.execute( 'SELECT COUNT(*) FROM semi_master' )
        print 'semi_master', cursor.fetchall(  )
        cursor.execute( qqmaster )
        cursor.execute( 'SELECT COUNT(*) FROM grand_master' )
        print 'grand_master', cursor.fetchall(  )
        cursor.execute( qqallowed )
        cursor.execute( 'SELECT COUNT(*) FROM master_allowed' )
        print 'master_allowed', cursor.fetchall(  )
        cursor.execute( qqdisallowed )
        cursor.execute( 'SELECT COUNT(*) FROM master_disallowed' )
        print 'master_disallowed', cursor.fetchall(  )
        cursor.execute( qqallowcompare )
        cursor.execute( 'SELECT COUNT(*) FROM allowed_comparisons' )
        print 'allowed_comparisons', cursor.fetchall(  )
        cursor.execute( qqdisallowcompare )
        cursor.execute( 'SELECT COUNT(*) FROM disallowed_comparisons' )
        print 'disallowed_comparisons', cursor.fetchall(  )
        cursor.execute( qqallcompares )
        cursor.execute( 'SELECT COUNT(*) FROM allcompares' )
        print 'allcompares', cursor.fetchall(  )
        cursor.execute( qq4 )
        ides = self.dictfetchall( cursor )
        j = len(ides)
        cursor.close()
        t1 = time.time()
        return (ides, t1 - t0, j, exp_id, user_id, perm)

    def dictfetchall(self, cursor):
        "Returns all rows from a cursor as a dict"
        t0 = time.time()
        desc = cursor.description
        returndic = [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]
        t1 = time.time()
        tt = t1 - t0
        print 'dict assembly time taken = %f' % tt 
        return returndic
        
    
    def dictfetchall_augmented(self, cursor):
        "Returns all rows from a cursor as a dict"
        t0 = time.time()
        desc = cursor.description
        returnlist = []
        for row in cursor.fetchall():
            local = {}
            for key, val in zip( [col[0] for col in desc], row ):
                if key == 'ptmarray':
                    local[ key ] = [ b.strip('(').strip(')').split(',') for b in val ]
                else:
                    local[ key ] = val
            returnlist.append( local )
        t1 = time.time()
        tt = t1 - t0
        print 'dict assembly augmented time taken = %f' % tt 
        return returnlist


    def basic_expt_query( self, expt_id ):
        """
        """
        cursor = connection.cursor()
        sql_expt = "SELECT * \
                FROM master_allowed \
                WHERE experiment_id = %s\
                "
        cursor.execute( sql_expt, [ expt_id ] )
        return self.dictfetchall_augmented( cursor )


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
    print '\n\nmkii_expt_query ran in %f seconds with %d outputs for expt_id = %d, user_id = %d, permission checking = %r\n\n' %  q2r[1:] 
    expt_1_rows = qo.basic_expt_query( 1 )
    print '\n\n', expt_1_rows[:22], '\n\n'
    print 'expt 1 rows returned = %d' % len( expt_1_rows )

