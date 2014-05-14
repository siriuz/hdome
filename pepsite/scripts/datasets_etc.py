import os
import sys
import datetime
from django.utils.timezone import utc
from django.db.models import Q

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

NOW = datetime.datetime.utcnow().replace(tzinfo=utc)

u1 = User.objects.get(id=1)

man1 = Manufacturer( name = 'MZTech' )
man1.save()

inst1 = Instrument( name = 'HiLine-Pro', description = 'MS/MS Spectrometer', manufacturer = man1 )
inst1.save()

lodg1 = Lodgement( title = 'Dummy Lodgement 01', datetime = NOW, user = u1 )
lodg1.save()

ds1 = Dataset( lodgement = lodg1, instrument = inst1, datetime = NOW, gradient_duration = 80., gradient_max = 95., gradient_min = 10. )
ds1.save()



