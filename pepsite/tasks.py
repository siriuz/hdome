
from __future__ import absolute_import

from celery import shared_task
import pepsite.uploaders

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from pepsite.models import *
import uniprot

@shared_task
def test():
    return 'test complete'

@shared_task
def test2_old(param):
    return send_mail('You just visited HaploDome.com search site', 'This is how to send a gmail via smtp using django.mail and settings.py\nparam=%s\n\nBest Regards,\n\nThe HaploDome Team\nwww.haplodome.com' % (param), 'kieranrimmer@gmail.com', ['kieranrimmer@gmail.com'], fail_silently=False)


@shared_task
def protein_seq_update_celery( function, full_batch = False ):
    proteins = None # Protein.objects.extra(where=["CHAR_LENGTH(sequence) = 0"])
    if full_batch:
        proteins = Protein.objects.all()
    else:
        proteins = Protein.objects.extra(where=["CHAR_LENGTH(sequence) = 0"])
    uniprot_data = uniprot.batch_uniprot_metadata( [ b.prot_id for b in proteins ]  )
    for key in uniprot_data.keys():
        defaults = {}
        try:
            defaults['sequence'] = uniprot_data[key]['sequence']
        except:
            pass
        try:
            defaults['description'] = uniprot_data[key]['description']
        except:
            pass
        prot, _ = Protein.objects.update_or_create( prot_id = key, defaults = defaults )
    return function

@shared_task
def protein_seq_update_celery_nofunction( full_batch = False ):
    proteins = None # Protein.objects.extra(where=["CHAR_LENGTH(sequence) = 0"])
    if full_batch:
        proteins = Protein.objects.all()
    else:
        proteins = Protein.objects.extra(where=["CHAR_LENGTH(sequence) = 0"])
    uniprot_data = uniprot.batch_uniprot_metadata( [ b.prot_id for b in proteins ]  )
    for key in uniprot_data.keys():
        defaults = {}
        try:
            defaults['sequence'] = uniprot_data[key]['sequence']
        except:
            pass
        try:
            defaults['description'] = uniprot_data[key]['description']
        except:
            pass
        prot, _ = Protein.objects.update_or_create( prot_id = key, defaults = defaults )
    return 'Protein sequences updated'

@shared_task
def upload_ss_celery( userid, elems, postdic ):
    user = User.objects.get( id = userid ) 
    admin = User.objects.get( username = 'admin' )
    ul = pepsite.uploaders.Uploads( user = user )
    ul.repopulate( elems )
    ul.user = user
    ul.add_cutoff_mappings( postdic )
    ul.prepare_upload_simple( )
    ul.lodgement_filename = os.path.join(settings.BASE_DIR, 'uploads/', ul.lodgement_filename)
    ul.upload_megarapid_rewrite()
    protein_seq_update_celery_nofunction.delay()
    ul.refresh_materialized_views()
    return send_mail('Your data upload is complete', 'The HaploDome database has been updated following your spreadsheet upload for lodgement \"%s\" - all new data should now be visible as prescribed.\n\nBest Regards,\n\nThe HaploDome Team\nwww.haplodome.com' % ( ul.lodgement.title ), admin.email, [ user.email ], fail_silently=False)


@shared_task
def curate_ss_celery( userid, elems ):
    user = User.objects.get( id = userid ) 
    admin = User.objects.get( username = 'admin' )
    ul = pepsite.uploaders.Curate( user = user )
    ul.repopulate( elems )
    ul.user = user
    lodgement_titles = [ Lodgement.objects.get( id = b ).title for b in elems['lodgement_ids'] ] 
    ul.auto_curation(  )
    ul.refresh_materialized_views()
    return send_mail('Your data curations are complete', 'The HaploDome database has been updated following your curations for lodgement(s) \"%s\" -  data visibility should now be altered as prescribed.\n\nBest Regards,\n\nThe HaploDome Team\nwww.haplodome.com' % ( ', '.join(lodgement_titles ) ), admin.email, [ user.email ], fail_silently=False)
    
@shared_task
def test2(param):
    protein_seq_update_celery_nofunction.delay()
    return 'test2 complete'
    return protein_seq_update_celery.delay( send_mail('You just visited HaploDome.com search site', 'This is how to send a gmail via smtp using django.mail and settings.py\n\nBest Regards,\n\nThe HaploDome Team\nwww.haplodome.com', 'kieranrimmer@gmail.com', ['kieranrimmer@gmail.com'], fail_silently=False) )
    return send_mail('You just visited HaploDome.com search site', 'This is how to send a gmail via smtp using django.mail and settings.py\n\nBest Regards,\n\nThe HaploDome Team\nwww.haplodome.com', 'kieranrimmer@gmail.com', ['kieranrimmer@gmail.com'], fail_silently=False)
    return 'The test task executed with argument2 "%s" ' % param
