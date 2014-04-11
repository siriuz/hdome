
import os
import sys
import datetime
import json


PROJ_NAME = 'hdome'
APP_NAME = 'pepsite'

CURDIR = os.path.dirname( os.path.abspath( __file__ ) )

print CURDIR

sys.path.append( CURDIR + '/../..' ) # gotta hit settings.py for site

os.environ[ 'DJANGO_SETTINGS_MODULE' ] = '%s.settings' %( PROJ_NAME )

import django #required
django.setup() #required

from django.contrib.auth.models import User
from pepsite.models import *

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class NonUniqueError(Error):
    def __init__(self, msg = 'Query yielded more than one class instance' ):
        self.msg = msg

    def __str__(self):
	return repr( self.msg )

class ClassNotFoundError(Error):
    def __init__(self, msg = 'Query yielded zero class instances' ):
        self.msg = msg

    def __str__(self):
	return repr( self.msg )



    


class Checker( object ):

    def add_attrs( self, **attrs ):

	for att in attrs:
		print att

    def set_attrs( self, **attrs ):

	for att in attrs:
		self.__setattr__( att, attrs[att] )
		print 'att =', attrs[att]

def check_condition(  obj_type, **conditions ):
	
	if not len( obj_type.objects.filter( **conditions ) ):
	    return obj_type( **conditions )
	    raise ClassNotFoundError( )
	elif len( obj_type.objects.filter( **conditions ) ) == 1:
	    return obj_type.objects.filter( **conditions )[0]
	else:
	    raise NonUniqueError(  )
	
def create_obj( obj_type, **conditions ):
	
	obj_type( **conditions )
 
 

if __name__ == '__main__':

    ch1 = Checker()
    ch1.add_attrs( killer = 'af', kfed = 'kr' )	
    ch1.add_attrs( biggsy = 'bb', gav = 'gs' )
    print check_condition( Allele, dna_type = 'A*01:01:01:01', ser_type = 'A1' )	
    print check_condition( Allele, description = 'hello' )	
    print check_condition( Allele, description = '' )	
