import os
import sys
import datetime
from django.utils.timezone import utc
from django.db.models import Q
from django.db.models import *
from django.db import IntegrityError, transaction

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
import pepsite.uploaders as ul


from django.db import connection
import time

def create_views_better():
    t0 = time.time()
    cursor = connection.cursor()
    cursor.execute('DROP MATERIALIZED VIEW IF EXISTS mega_unagg CASCADE')
    cursor.execute('DROP MATERIALIZED VIEW IF EXISTS mega_posns CASCADE')
    cursor.execute('DROP MATERIALIZED VIEW IF EXISTS mega_comparisons CASCADE')
    cursor.execute('DROP MATERIALIZED VIEW IF EXISTS clean_comparisons CASCADE')
    cursor.execute('DROP MATERIALIZED VIEW IF EXISTS notclean_comparisons CASCADE')
    sqlcreate1 = 'CREATE MATERIALIZED VIEW mega_unagg AS \
                SELECT t1.id as idestimate_id, t1.\"isRemoved\", t1.\"isValid\", t1.reason, t1.confidence, t1.delta_mass, ABS(t1.delta_mass) AS absdm, \
                t2.id as ion_id, t2.charge_state, t2.mz, t2.precursor_mass, t2.retention_time, t2.spectrum, \
                t3.id as dataset_id, t3.title as dataset_title, t3.confidence_cutoff, \
                t3a.id as lodgement_id, t3a.title as lodgement_title, t3a.datafilename, t3a.\"isFree", \
                t4.id AS experiment_id, t4.title AS experiment_title, \
                t5.id as peptide_id, t5.sequence AS peptide_sequence, \
                t7.id AS ptm_id, t7.description as ptm_description, t7.\"name\" as \"ptm_name\", \
                t10.id as protein_id, t10.description AS protein_description, t10.prot_id AS uniprot_code \
                FROM \
                pepsite_idestimate t1 \
                INNER JOIN pepsite_ion t2 \
                ON (t1.ion_id = t2.id) \
                INNER JOIN pepsite_dataset t3 \
                ON (t2.dataset_id = t3.id) \
                INNER JOIN pepsite_lodgement t3a \
                ON (t3.lodgement_id = t3a.id ) \
                INNER JOIN pepsite_experiment t4 \
                ON (t4.id = t3.experiment_id) \
                INNER JOIN pepsite_peptide t5 \
                ON (t5.id = t1.peptide_id ) \
                INNER JOIN pepsite_idestimate_proteins t9 \
                ON (t9.idestimate_id = t1.id ) \
                INNER JOIN pepsite_protein t10 \
                ON (t10.id = t9.protein_id AND t10.id = t9.protein_id ) \
                LEFT JOIN pepsite_idestimate_ptms t6 \
                ON (t1.id = t6.idestimate_id ) \
                LEFT JOIN pepsite_ptm t7 \
                ON (t7.id = t6.ptm_id ) \
                '
    sqlq2 = 'SELECT COUNT(*) \
                FROM \
                pepsite_idestimate t1 \
                INNER JOIN pepsite_ion t2 \
                ON (t1.ion_id = t2.id) \
                INNER JOIN pepsite_dataset t3 \
                ON (t2.dataset_id = t3.id) \
                INNER JOIN pepsite_lodgement t3a \
                ON (t3.lodgement_id = t3a.id ) \
                INNER JOIN pepsite_experiment t4 \
                ON (t4.id = t3.experiment_id) \
                INNER JOIN pepsite_peptide t5 \
                ON (t5.id = t1.peptide_id ) \
                INNER JOIN pepsite_idestimate_proteins t9 \
                ON (t9.idestimate_id = t1.id ) \
                INNER JOIN pepsite_protein t10 \
                ON (t10.id = t9.protein_id AND t10.id = t9.protein_id ) \
                LEFT JOIN pepsite_idestimate_ptms t6 \
                ON (t1.id = t6.idestimate_id ) \
                LEFT JOIN pepsite_ptm t7 \
                ON (t7.id = t6.ptm_id ) \
                '
    morestuff = ' \
                LEFT JOIN pepsite_peptoprot_positions t11 \
                ON (t11.peptoprot_id = t9.id) \
                LEFT JOIN pepsite_position t12 \
                ON (t12.id = t11.position_id ) \
                '
    sqlmega_agg2 = 'CREATE MATERIALIZED VIEW mega_posns AS \
                SELECT foo1.idestimate_id, foo1.\"isRemoved\", foo1.\"isValid\", foo1.reason, foo1.confidence, foo1.delta_mass, ABS(foo1.delta_mass) AS absdm, \
                foo1.ion_id, foo1.charge_state, foo1.mz, foo1.precursor_mass, foo1.retention_time, foo1.spectrum, \
                foo1.dataset_id, foo1.dataset_title, foo1.confidence_cutoff, \
                foo1.lodgement_id, foo1.lodgement_title, foo1.datafilename, foo1.\"isFree", \
                foo1.experiment_id, foo1.experiment_title, \
                foo1.peptide_id, foo1.peptide_sequence, \
                foo1.proteinarray, foo1.ptmarray, foo1.ptmstr, foo1.proteinstr, foo1.uniprotstr , \
                foo1.ptmidarray, foo1.proteinidarray FROM \
                ( SELECT t1.idestimate_id, t1.\"isRemoved\", t1.\"isValid\", t1.reason, t1.confidence, t1.delta_mass, \
                t1.ion_id, t1.charge_state, t1.mz, t1.precursor_mass, t1.retention_time, t1.spectrum, \
                t1.dataset_id, t1.dataset_title, t1.confidence_cutoff, \
                t1.lodgement_id, t1.lodgement_title, t1.datafilename, t1.\"isFree", \
                t1.experiment_id, t1.experiment_title, \
                t1.peptide_id, t1.peptide_sequence, \
                array_agg( DISTINCT (t1.protein_id, \'|||\' || t1.protein_description || \'|||\', t1.uniprot_code)::text ORDER BY  (t1.protein_id, \'|||\' || t1.protein_description || \'|||\', t1.uniprot_code)::text  ) AS proteinarray, \
                array_to_string(array_agg( DISTINCT t1.protein_description order by t1.protein_description),\'; \') AS proteinstr, \
                array_to_string(array_agg( DISTINCT t1.uniprot_code order by t1.uniprot_code),\'; \') AS uniprotstr, \
                array_agg( DISTINCT (t1.ptm_id, t1.ptm_description)::text order by (t1.ptm_id, t1.ptm_description)::text ) AS ptmarray, \
                array_to_string(array_agg( DISTINCT t1.ptm_description order by t1.ptm_description),\'; \') AS ptmstr, \
                array_agg( DISTINCT t1.ptm_id order by t1.ptm_id) AS ptmidarray, \
                array_agg( DISTINCT t1.protein_id order by t1.protein_id) AS proteinidarray \
                FROM mega_unagg t1 \
                GROUP BY t1.idestimate_id, t1.\"isRemoved\", t1.\"isValid\", t1.reason, t1.confidence, t1.delta_mass, \
                t1.ion_id, t1.charge_state, t1.mz, t1.precursor_mass, t1.retention_time, t1.spectrum, \
                t1.dataset_id, t1.dataset_title, t1.confidence_cutoff, \
                t1.lodgement_id, t1.lodgement_title, t1.datafilename, t1.\"isFree", \
                t1.experiment_id, t1.experiment_title, \
                t1.peptide_id, t1.peptide_sequence \
                ) as foo1 \
                \
                '
    sqlcompare = 'CREATE MATERIALIZED VIEW mega_comparisons AS \
                SELECT t1.*, foo1.allowed_array, foo2.disallowed_array \
                FROM mega_posns t1 \
                LEFT JOIN \
                ( SELECT \
                t2.peptide_id, \
                t2.ptmarray, \
                array_agg( DISTINCT t2.experiment_id ORDER BY t2.experiment_id ) AS allowed_array \
                FROM \
                ( select * FROM mega_posns mp WHERE mp.\"isRemoved\" = false AND mp.confidence > mp.confidence_cutoff ) AS t2 \
                GROUP BY \
                t2.peptide_id, \
                t2.ptmarray \
                ) \
                AS foo1 \
                ON ( t1.peptide_id = foo1.peptide_id AND t1.ptmarray = foo1.ptmarray ) \
                LEFT JOIN \
                ( SELECT \
                t3.peptide_id, \
                t3.ptmarray, \
                array_agg( DISTINCT t3.experiment_id ORDER BY t3.experiment_id ) AS disallowed_array \
                FROM \
                ( select * FROM mega_posns mp2 WHERE mp2.\"isRemoved\" = true OR mp2.confidence <= mp2.confidence_cutoff ) AS t3 \
                GROUP BY \
                t3.peptide_id, \
                t3.ptmarray \
                ) \
                AS foo2 \
                ON ( t1.peptide_id = foo2.peptide_id AND t1.ptmarray = foo2.ptmarray ) \
                '
    sqlcleancompare = 'CREATE MATERIALIZED VIEW clean_comparisons AS \
                SELECT DISTINCT ON (peptide_id, ptmarray, experiment_id ) t2.* \
                FROM \
                (SELECT t1.peptide_id, t1.ptmarray, \
                MIN( t1.absdm ) AS minabsdm \
                FROM mega_comparisons t1 \
                GROUP BY t1.peptide_id, t1.ptmarray, experiment_id ) as foo1 \
                LEFT JOIN \
                mega_comparisons t2 \
                ON (foo1.peptide_id = t2.peptide_id AND foo1.ptmarray = t2.ptmarray AND foo1.minabsdm = t2.absdm ) \
                '
    sqlnotcleancompare = 'CREATE MATERIALIZED VIEW notclean_comparisons AS \
                SELECT * FROM mega_comparisons \
                EXCEPT SELECT * FROM clean_comparisons \
                '
    cursor.execute( sqlcreate1 )
    cursor.execute('SELECT COUNT(*) FROM mega_unagg')
    print 'mega_unagg count:', cursor.fetchall()
    cursor.execute( sqlmega_agg2 )
    cursor.execute('SELECT COUNT(*) FROM mega_posns')
    print 'mega_posns count:', cursor.fetchall()
    cursor.execute( sqlcompare )
    cursor.execute('SELECT COUNT(*) FROM mega_comparisons')
    print 'mega_comparisons count:', cursor.fetchall()
    cursor.execute( sqlcleancompare )
    cursor.execute( 'SELECT COUNT(*) FROM clean_comparisons' )
    print 'clean_comparisons', cursor.fetchall(  )
    cursor.execute( sqlnotcleancompare )
    cursor.execute( 'SELECT COUNT(*) FROM notclean_comparisons' )
    print 'notclean_comparisons', cursor.fetchall(  )

    t1 = time.time()
    tt = t1 -t0
    print 'time taken %f seconds' % tt


if __name__ == '__main__':
    create_views_better()
    #ulinst = ul.Uploads()
    # ulinst.create_views_rapid()

