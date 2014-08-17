
from __future__ import absolute_import

from celery import shared_task
import pepsite.uploaders

from django.core.mail import send_mail

@shared_task
def test(param):
    return send_mail('You just visited HaploDome.com search site', 'This is how to send a gmail via smtp using django.mail and settings.py', 'kieranrimmer@gmail.com', ['kieranrimmer@gmail.com'], fail_silently=False)
    return 'The test task executed with argument2 "%s" ' % param


@shared_task
def upload_ss_celery( user, elems, postdic ):
    #ul = pepsite.uploaders.Uploads( user = user )
    #ul.repopulate( elems )
    #ul.add_cutoff_mappings( postdic )
    return 'upload_ss_celery complete'
