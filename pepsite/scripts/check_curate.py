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
import pepsite
from pepsite import dbtools
import pepsite.uploaders as ul


from django.db import connection
import time

def trunc(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    slen = len('%.*f' % (n, f))
    return str(f)[:slen]

def import_minimal( fileobj, user ):
    t0 = time.time()
    ldg_obj = Lodgement.objects.get( id = ldg_id )
    ul = pepsite.uploaders.Uploads( user = user )
    ul.preprocess_ss_simple( fileobj )
    for k in ul.uldict.keys():


def curate_better(ldg_id, fileobj, user):
    t0 = time.time()
    ldg_obj = Lodgement.objects.get( id = ldg_id )
    ul = pepsite.uploaders.Uploads( user = user )
    ul.preprocess_ss_simple( fileobj )
    for k in ul.uldict.keys():
        local = ul.uldict[k]
        print local
        if True:
            pep = Peptide.objects.get( sequence = local['peptide_sequence'] )
            print pep.id, pep.sequence
            proteins = []
            ptms = []
            for ptm_desc in local['ptms']:
                ptm, _ = Ptm.objects.get_or_create( description = ptm_desc, name = ptm_desc )
                ptm.save()
                ptms.append( ptm )
            dsno = local['dataset']
            dstitle = ul.entitle_ds(dsno, ldg_obj.datafilename)
            #print 'dstitle: %s' % dstitle
            dataset = Dataset.objects.get(lodgement__id = ldg_id, title = dstitle)
            try:
                #print 'Ion.objects.get( charge_state = %s, precursor_mass = %s, retention_time = %s, mz = %s, dataset__id = %s)' % (local['charge'], local['precursor_mass'],
                #    local['retention_time'], local['mz'], dataset.id)
                ion = Ion.objects.get( charge_state = local['charge'], precursor_mass = round(float(local['precursor_mass']), 6),
                                       retention_time = float(local['retention_time']), mz = float(local['mz']), dataset__id = dataset.id )
                #print 'Ion retrieval succeded'
            except:
                ion = Ion.objects.get( charge_state = local['charge'], precursor_mass = trunc(float(local['precursor_mass']), 6),
                                       retention_time = float(local['retention_time']), mz = float(local['mz']), dataset__id = dataset.id )
            print ion
            if not ptms:
                td = [ {'ptms__isnull' : True}, {'peptide__id' : pep.id }, {'ion__id' : ion.id } ]
            else:
                #print ptms
                for ptm in ptms:
                    td.append( { 'ptms__id' : ptm.id } )
                td += [ {'peptide__id' : pep.id }, {'ion__id' : ion.id } ]
            a = IdEstimate.objects.all().annotate( count = Count('ptms'))
            for dic in td:
                a = a.filter( **dic )

            print a.distinct()
            print td
            print local
            ide = a.filter(count = len(ptms))[0]
            print 'a hit, %s' % td
            break
            #print 'Dataset retrieval: %s, %d' % ( dataset.title, dataset.id )
        # except:
        #     #print 'setup failed'
        #     pass
        # #except:
        # #    print 'Dataset retrieval failed for lodgement__id = %d and title = \"%s\" vs ' % (ldg_obj.id, dstitle)
        # #finally:
        # #    print 'print Ion find failed: Ion.objects.get( charge_state = %s, precursor_mass = %s, retention_time = %s, mz = %s, dataset__id = %s)' % (local['charge'], local['precursor_mass'],
        # #                local['retention_time'], local['mz'], dataset.id)
        #
        #
        # # except:
        # #     print 'Ion retrieval failed'
        #     #ion.save()
        # if True:
        #     td = []
        #     print ptms
            # ide.isRemoved = True
                # ide.save()
            # except:
            #     print 'a miss, %s' % td
            #     pass
        # except:
        #     pass

    t1 = time.time()
    tt = t1 -t0
    print 'time taken %f seconds' % tt


if __name__ == '__main__':
    user = User.objects.get(username = 'admin')
    with open( os.path.join(CURDIR, 'Time_Trial_Import4_PeptideSummary.trial4'), 'rb' )  as f:
        curate_better(187, f, user)
    #ulinst = ul.Uploads()
    # ulinst.create_views_rapid()

