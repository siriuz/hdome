import os
import sys
import datetime
from django.utils.timezone import utc
from django.db.models import *
import time

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

    def rapid_array(self, valuz):
        """docstring for rapid_array"""
        t0 = time.time()
        idlist =  [ b['id'] for b in valuz]
        ides = IdEstimate.objects.filter( id__in = idlist ).distinct()
        t1 = time.time()
        return (t1 - t0, ides.count() )

    def make_array_from_ide_vals(self, valuz, expt_id):
        """docstring for make_array_from_ides"""
        t0 = time.time()
        rows = []
        expt = Experiment.objects.get( id = expt_id )
        i = 0
        for local in valuz:
            i += 1
            #print i,
            ide = IdEstimate.objects.get( id = local['id'] )
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
    user_id = 1
    print 'here we go... expecting 1578 returns...\n'
    qo = QueryOpt()
    q1r = qo.mkii_expt_query( exp_id, user_id, perm = False)
    ar1 = q1r[0]
    print ar1
    print ar1.count()
    #print dir(q1r[0])
    print '\n\nmkii_expt_query ran in %f seconds with %d outputs for expt_id = %d, user_id = %d, permission checking = %r\n\n' %  q1r[1:]   #print 'simple_expt_query ran in %f seconds with %d outputs for expt_id = %d, user_id = %d, permission checking = %r' % qo.simple_expt_query( exp_id, user_id, perm = False)
    print '\n\nrapid_array ran for %f seconds and returned %d results\n\n' % ( qo.rapid_array(ar1)  )
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


