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

from django.db import connection


from django.contrib.auth.models import User
from pepsite.models import *
from pepsite import dbtools
import pepsite.uploaders
import time

def basic_insert( cursor, matchtuple ):
    sql1 = 'INSERT INTO pepsite_protein (description, name, prot_id)\
    SELECT i.field1 description, i.field1 \"name\", i.field2 prot_id \
    FROM (VALUES %s) AS i(field1, field2) \
    LEFT JOIN pepsite_protein as existing \
    ON (existing.description = i.field1 AND existing.prot_id = i.field2) \
    WHERE existing.id IS NULL \
    '
    cursor.execute( sql1 % ( matchtuple ) )
    #return cursor.fetchall()

def m2m_check( cursor, matchtuple ):
    pr = '(\'P01877\', \'Ig alpha-2 chain C region OS=Homo sapiens GN=IGHA2 PE=1 SV=3\')'
    pep = 1
    sql1 = 'WITH g(\"prot_id\", \"description\") AS\
            (SELECT * FROM (VALUES %s) AS foo) \
            INSERT INTO pepsite_peptoprot \
            SELECT \"protein_id\", \"peptide_id\" FROM \
            (SELECT t1.id as \"protein_id\", h.\"peptide_id\" \
            FROM g \
            LEFT JOIN pepsite_protein t1 \
            ON (t1.\"prot_id\" = g.\"prot_id\" AND\
            t1.\"description\" = g.\"description\" ) \
            , ( VALUES(%s) ) AS h(\"peptide_id\") \
            ) AS f2 \
            ' % ( pr, pep )
    cursor.execute( sql1 )
    return cursor.fetchall()

def multirapid( cursor, qstr ):

    sqlion = 'with f as \
            (select foo2.charge_state, foo2.precursor_mass:: double precision, foo2.retention_time::double precision, \
            foo2.mz:: double precision, foo2.spectrum, foo2.ds_title, foo2.expt_id, foo2.id, foo2.title \
            from( with g(charge_state, precursor_mass, retention_time, mz, spectrum, ds_title, expt_id) AS \
            (select * from (VALUES %s ) AS foo) \
            select * from  g INNER JOIN pepsite_dataset t1 ON \
            ( g.\"ds_title\" = t1.\"title\" AND g.\"expt_id\" = t1.\"experiment_id\" ) ) AS foo2) \
            SELECT * FROM \
            (select f.charge_state, f.precursor_mass, f.retention_time, f.mz, f.spectrum, f.expt_id as experiment_id, f.id as dataset_id \
            from f  \
            LEFT JOIN pepsite_ion AS existing \
            ON (f.id = existing.dataset_id AND f.charge_state = existing.charge_state AND f.retention_time = existing.retention_time \
            AND f.mz = existing.mz AND f.spectrum = existing.spectrum AND f.expt_id = existing.experiment_id) \
            where existing.id IS NOT NULL) AS foo4 \
            ' % ( qstr )
    cursor.execute( sqlion )
    return cursor.fetchall()

def get_ioninfo(cursor):
    """docstring for get_ioninfo"""
    ionsql = 'select t1.charge_state, t1.precursor_mass, CAST(t1.retention_time AS double precision), t1.mz, t1.spectrum, t2.id, t2.experiment_id from pepsite_ion t1 inner join pepsite_dataset t2 on (t2.id = t1.dataset_id) limit 200'
    cursor.execute( ionsql )
    ionstr = ''
    qf = cursor.fetchall()
    for line in qf:
        ionstr += '( %d, %f, %f, %f, \'%s\', %d, %d ), ' % ( line )
    return ionstr.strip(', ')

def readions(cursor):
    ions_to_create = [(3, 2192.08813476563, 45.0244, 731.7033, u'7.1.1.3747.4', 1, 22), (2, 1435.80944824219, 41.9072, 718.912, u'13.1.1.6524.16', 1, 5), (3, 1295.75793457031, 13.6884, 432.9266, u'18.1.1.2089.14', 1, 10), (2, 1158.69287109375, 23.1558, 580.3537, u'2.1.1.2770.31', 1, 12), (2, 1079.44030761719, 41.0175, 540.7274, u'21.1.1.10245.3', 1, 14)]
    ionstr = ''
    for line in ions_to_create:
        ionstr += '( %d, %f, %f, %f, \'%s\', %d, %d ), ' % ( line )
    return ionstr.strip(', ')

def createions(cursor, ionstr):
        sqlionins = 'INSERT INTO pepsite_ion(charge_state, precursor_mass, retention_time, mz, spectrum, dataset_id, experiment_id ) \
                SELECT g.charge_state, g.precursor_mass, CAST(g.retention_time AS double precision), g.mz, g.spectrum, g.dataset_id, g.experiment_id\
                from (VALUES %s ) \
                AS g(charge_state, precursor_mass, retention_time, mz, spectrum, dataset_id, experiment_id) \
                ' % ( ionstr )
        sqlion = ' \
                SELECT g.retention_time \
                from (VALUES ( %d, %f, %f, %f, \'%s\', %d, %d ) ) \
                AS g(charge_state, precursor_mass, retention_time, mz, spectrum, experiment_id, dataset_id) \
                ' % ( 3, 2192.08813476563, 45.0244, 731.7033, u'7.1.1.3747.4', 1, 22) 
        sqlion = ' \
                SELECT g.retention_time \
                from (VALUES %s ) \
                AS g(charge_state, precursor_mass, retention_time, mz, spectrum, dataset_id, experiment_id) \
                ' % ( ionstr ) 
        cursor.execute( sqlionins )
        #print 'retentiontime', cursor.fetchall()

def raw_create_ions(cursor):
    ionslist = [(2, 928.509888, 32.8253, 465.2622, u'1.1.1.3257.6', u'Dataset #1 from Auto Lodgement for 9013 Class I at datetime = 2014-08-01 02:21:11.676168+00:00', 1), (2, 985.524292, 21.2241, 493.7694, u'1.1.1.3123.8', u'Dataset #1 from Auto Lodgement for 9013 Class I at datetime = 2014-08-01 02:21:11.676168+00:00', 1), (2, 1197.692505, 32.2745, 599.8535, u'1.1.1.3250.29', u'Dataset #1 from Auto Lodgement for 9013 Class I at datetime = 2014-08-01 02:21:11.676168+00:00', 1)]
    ionstr = ''
    for line in ionslist:
        ionstr += '( %d, %f, %f, %f, \'%s\', \'%s\', %d ), ' % ( line )
    ionstr = ionstr.strip(', ')
    sqlion_old = 'with f(charge_state, precursor_mass, retention_time, mz, spectrum, dataset_id, experiment_id) as \
            (select foo2.charge_state::integer, foo2.precursor_mass::double precision, foo2.retention_time::double precision, \
            foo2.mz:: double precision, foo2.spectrum, foo2.id, foo2.expt_id \
            from ( with g(charge_state, precursor_mass, retention_time, mz, spectrum, ds_title, expt_id) AS \
            (select foo.charge_state, foo.precursor_mass, foo.retention_time, foo.mz, foo.spectrum, foo.ds_title, foo.expt_id from (VALUES %s ) \
            AS foo(charge_state, precursor_mass, retention_time, mz, spectrum, ds_title, expt_id) ) \
            select * from  g INNER JOIN pepsite_dataset t1 ON \
            ( g.\"ds_title\" = t1.\"title\" AND g.\"expt_id\" = t1.\"experiment_id\" ) ) AS foo2 \
            ) \
            INSERT INTO pepsite_ion (charge_state, precursor_mass, retention_time, mz, spectrum, dataset_id, experiment_id) \
            select f.charge_state::integer, f.precursor_mass, f.retention_time::double precision, f.mz, f.spectrum, f.experiment_id, f.dataset_id \
            from f  \
            LEFT JOIN pepsite_ion AS existing \
            ON (f.dataset_id = existing.dataset_id AND f.charge_state = existing.charge_state AND f.retention_time = existing.retention_time \
            AND f.mz = existing.mz AND f.spectrum = existing.spectrum AND f.experiment_id = existing.experiment_id) \
            where existing.id IS NULL\
            ' % ( ionstr )
    cursor.execute(sqlion_old)

def reformat_to_str( iterable ):
    retstr = '('
    for elem in iterable:
        if not elem:
            retstr += 'NULL, '

        elif type( elem ) in ( list, tuple ):
            retstr += reformat_to_str(elem)
        elif type( elem ) == int:
            retstr += '%s, ' % elem
        elif elem.isdigit():
            retstr += '%s, ' % elem
        else:
            try:
                retstr += '%f, ' % float(elem)
            except ValueError:
                retstr += '\'%s\', ' % elem
    retstr = retstr.strip(', ') + ' ), '
    return retstr

def reformat_lazy( iterable ):
    retstr = '('
    for elem in iterable:
        if not elem:
            retstr += 'NULL, '

        elif type( elem ) in ( list, tuple ):
            retstr += reformat_to_str(elem)
        elif type( elem ) == int:
            retstr += '%s, ' % elem
        elif elem.isdigit():
            retstr += '%s, ' % elem
        else:
            try:
                retstr += '%f, ' % float(elem)
            except ValueError:
                retstr += '\'%s\', ' % elem
    retstr = retstr.strip(', ') + ' ), '
    return retstr
                


def createides(cursor):
    combinedml = [('EPSQGTTTFAVTSILRVAAED', [['P01877', 'Ig alpha-2 chain C region OS=Homo sapiens GN=IGHA2 PE=1 SV=3']], '7', ('3', '2192.08813476563', '45.0244', '731.7033', '7.1.1.3747.4'), ('99.0000009536743', '-0.00799696985632181'), [], 1), ('GTTTFAVTSILRVA', [['P01877', 'Ig alpha-2 chain C region OS=Homo sapiens GN=IGHA2 PE=1 SV=3']], '13', ('2', '1435.80944824219', '41.9072', '718.912', '13.1.1.6524.16'), ('99.0000009536743', '0.00594259006902575'), [], 1), ('HPRLSLHRPAL', [['P01877', 'Ig alpha-2 chain C region OS=Homo sapiens GN=IGHA2 PE=1 SV=3']], '18', ('3', '1295.75793457031', '13.6884', '432.9266', '18.1.1.2089.14'), ('99.0000009536743', '0.000513856008183211'), [], 1), ('PRLSLHRPAL', [['P01877', 'Ig alpha-2 chain C region OS=Homo sapiens GN=IGHA2 PE=1 SV=3']], '2', ('2', '1158.69287109375', '23.1558', '580.3537', '2.1.1.2770.31'), ('99.0000009536743', '-0.00571600021794438'), [], 1), ('QPWNHGETF', [['P01877', 'Ig alpha-2 chain C region OS=Homo sapiens GN=IGHA2 PE=1 SV=3']], '21', ('2', '1079.44030761719', '41.0175', '540.7274', '21.1.1.10245.3'), ('99.0000009536743', '-0.0058127399533987'), ['Gln->pyro-Glu@N-term', 'Dehydrated(T)@8'], 1)]
    combinedml = [('EPSQGTTTFAVTSILRVAAED', [['P01877', 'Ig alpha-2 chain C region OS=Homo sapiens GN=IGHA2 PE=1 SV=3']], '7', ('3', '2192.08813476563', '45.0244', '731.7033', '7.1.1.3747.4'), ('99.0000009536743', '-0.00799696985632181'), [], 1), ('GTTTFAVTSILRVA', [['P01877', 'Ig alpha-2 chain C region OS=Homo sapiens GN=IGHA2 PE=1 SV=3']], '13', ('2', '1435.80944824219', '41.9072', '718.912', '13.1.1.6524.16'), ('99.0000009536743', '0.00594259006902575'), [], 1), ('HPRLSLHRPAL', [['P01877', 'Ig alpha-2 chain C region OS=Homo sapiens GN=IGHA2 PE=1 SV=3']], '18', ('3', '1295.75793457031', '13.6884', '432.9266', '18.1.1.2089.14'), ('99.0000009536743', '0.000513856008183211'), [], 1), ('PRLSLHRPAL', [['P01877', 'Ig alpha-2 chain C region OS=Homo sapiens GN=IGHA2 PE=1 SV=3']], '2', ('2', '1158.69287109375', '23.1558', '580.3537', '2.1.1.2770.31'), ('99.0000009536743', '-0.00571600021794438'), [], 1), ('QPWNHGETF', [['P01877', 'Ig alpha-2 chain C region OS=Homo sapiens GN=IGHA2 PE=1 SV=3']], '21', ('2', '1079.44030761719', '41.0175', '540.7274', '21.1.1.10245.3'), ('99.0000009536743', '-0.0058127399533987'), [['Gln->pyro-Glu@N-term'], ['Dehydrated(T)@8']], 1)] 
    combinedml = [['EPSQGTTTFAVTSILRVAAED', '3', '2192.08813476563', '45.0244', '731.7033', '7.1.1.3747.4', '7', 1], ['GTTTFAVTSILRVA', '2', '1435.80944824219', '41.9072', '718.912', '13.1.1.6524.16', '13', 1], ['HPRLSLHRPAL', '3', '1295.75793457031', '13.6884', '432.9266', '18.1.1.2089.14', '18', 1], ['PRLSLHRPAL', '2', '1158.69287109375', '23.1558', '580.3537', '2.1.1.2770.31', '2', 1], ['QPWNHGETF', '2', '1079.44030761719', '41.0175', '540.7274', '21.1.1.10245.3', '21', 1]]
    combinedml = [['EPSQGTTTFAVTSILRVAAED', '3', '2192.08813476563', '45.0244', '731.7033', '7.1.1.3747.4', '7', 1, 22, 32], ['GTTTFAVTSILRVA', '2', '1435.80944824219', '41.9072', '718.912', '13.1.1.6524.16', '13', 1, 5, 78], ['HPRLSLHRPAL', '3', '1295.75793457031', '13.6884', '432.9266', '18.1.1.2089.14', '18', 1, 10, 25], ['PRLSLHRPAL', '2', '1158.69287109375', '23.1558', '580.3537', '2.1.1.2770.31', '2', 1, 12, 27], ['QPWNHGETF', '2', '1079.44030761719', '41.0175', '540.7274', '21.1.1.10245.3', '21', 1, 14, 54]]
    mstr = reformat_to_str( combinedml ).strip(', ')[1:-1]
    print mstr
    msql = 'WITH f AS \
            (SELECT foo.* FROM  (VALUES %s ) AS foo(peptide_sequence, charge_state, precursor_mass, \
            retention_time, mz, spectrum, dataset_title, experiment_id ) \
            INNER JOIN pepsite_peptide t2 ON (foo.peptide_sequence = t2.sequence) ) \
            SELECT peptide_sequence FROM f\
            ' % mstr
    cursor.execute( msql )
    a1 = cursor.fetchall()
    msql2 = 'WITH f AS \
            (SELECT foo.* FROM pepsite_idestimate t2 \
            INNER JOIN \
            (VALUES %s ) AS foo(peptide_sequence, charge_state, precursor_mass, \
            retention_time, mz, spectrum, dataset_title, experiment_id, dataset_id, peptide_id ) \
            ON (foo.peptide_sequence = t2.sequence) ) \
            SELECT peptide_sequence FROM f \
            ' % mstr
    cursor.execute( msql2 )
    a2 = cursor.fetchall()
    return a2








if __name__ == '__main__':
    cursor = connection.cursor()
    print basic_insert( cursor, ('(\'insulin\', \'A0305\'), (\'insulin2\', \'A03052\')') )
    #print m2m_check( cursor, ('(\'insulin\', \'A0305\'), (\'insulin2\', \'A03052\')') )
    #print multirapid( cursor, get_ioninfo(cursor) )
    #print createions( cursor, get_ioninfo(cursor) )
    #print raw_create_ions( cursor )
    print createides( cursor )
