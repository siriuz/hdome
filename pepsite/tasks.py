
from __future__ import absolute_import

from celery import shared_task
import pepsite.uploaders

from django.core.mail import send_mail
from django.contrib.auth.models import User
from pepsite.models import *

@shared_task
def test(param):
    return send_mail('You just visited HaploDome.com search site', 'This is how to send a gmail via smtp using django.mail and settings.py\n\nBest Regards,\n\nThe HaploDome Team\nwww.haplodome.com', 'kieranrimmer@gmail.com', ['kieranrimmer@gmail.com'], fail_silently=False)
    return 'The test task executed with argument2 "%s" ' % param


@shared_task
def upload_ss_celery( userid, elems, postdic ):
    user = User.objects.get( id = userid ) 
    admin = User.objects.get( username = 'admin' )
    ul = pepsite.uploaders.Uploads( user = user )
    ul.repopulate( elems )
    ul.add_cutoff_mappings( postdic )
    ul.prepare_upload_simple( )
    ul.upload_simple()
    ul.refresh_materialized_views()
    return send_mail('Your data upload is complete', 'The HaploDome database has been updated following your spreadsheet upload for lodgement \"%s\" - all new data should now be visible as prescribed.\n\nBest Regards,\n\nThe HaploDome Team\nwww.haplodome.com' % ( ul.lodgement.title ), admin.email, [ user.email ], fail_silently=False)


@shared_task
def curate_ss_celery( userid, elems ):
    user = User.objects.get( id = userid ) 
    admin = User.objects.get( username = 'admin' )
    ul = pepsite.uploaders.Curate( user = user )
    ul.repopulate( elems )
    lodgement_titles = [ Lodgement.objects.get( id = b ).title for b in elems['lodgement_ids'] ] 
    ul.auto_curation(  )
    ul.refresh_materialized_views()
    return send_mail('Your data curations are complete', 'The HaploDome database has been updated following your curations for lodgement(s) \"%s\" -  data visibility should now be altered as prescribed.\n\nBest Regards,\n\nThe HaploDome Team\nwww.haplodome.com' % ( ', '.join(lodgement_titles ) ), admin.email, [ user.email ], fail_silently=False)

