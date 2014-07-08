"""Python classes for creation and manipulation
of Django object instances



"""


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


class DBTools(object):
    """docstring for DBCreate"""
    def add_if_not_already( self, obj1, obj2_lookup ):
        """<Django model ob>, <Django model obj> -> None
        """
        if obj1 not in obj2_lookup.all():
            obj2_lookup.add( obj1 )

    def fname(self):
        """docstring for fname"""
        pass

    
    def get_model_object( self, obj_type, **conditions ):
        """(DBTools, <arbitrary Django model object>) -> 
        <unsaved arbitrary Django model object> |  
        <saved arbitrary Django model object> | Error
        """
        if not len( obj_type.objects.filter( **conditions ) ):
            return obj_type( **conditions )
        elif len( obj_type.objects.filter( **conditions ) ) == 1:
            return obj_type.objects.get( **conditions )
        else:
            raise NonUniqueError(  )

    def unpack_dual_delimited( self, readstr, delim1 = ';', delim2 = '/', trim_whitespace = False ):
        """
        """
        bloated_list = [ b.split( delim1 ) for b in readstr.split( delim2 ) ]
        if trim_whitespace:
            return ( [item.strip() for sublist in bloated_list for item in sublist] )
        else:
            return ( [item for sublist in bloated_list for item in sublist] )



    def read_canonical_spreadsheet(self, csvfile):
        """docstring for read_canonical_spreadsheet"""
        with open( csvfile, 'rb' ) as f:
            info = [ b.strip().split(',') for b in f ] 
            header = [ b.strip() for b in info[0] ]
            mdict = {}
            for i in range(1, len(info)):
                mdict[i] = {}
                for j in range(len(header)):
                    mdict[i][ header[j] ] = info[ i ][ j ].strip()
        return mdict



        







