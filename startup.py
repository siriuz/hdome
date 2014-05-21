
PROJ_NAME = 'hdome'
APP_NAME = 'pepsite'

import os

CURDIR = os.path.dirname( os.path.abspath( __file__ ) )

os.environ[ 'DJANGO_SETTINGS_MODULE' ] = '%s.settings' %( PROJ_NAME )

import django #required
django.setup() #required

from django.contrib.auth.models import User
from pepsite.models import *


