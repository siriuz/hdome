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




if __name__ == '__main__':
    cursor = connection.cursor()
    print basic_insert( cursor, ('(\'insulin\', \'A0305\'), (\'insulin2\', \'A03052\')') )
    print m2m_check( cursor, ('(\'insulin\', \'A0305\'), (\'insulin2\', \'A03052\')') )
