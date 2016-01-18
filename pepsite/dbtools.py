"""Python classes for creation and manipulation
of Django object instances



"""

from django.db import IntegrityError, transaction

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class NonUniqueError(Error):
    def __init__(self, msg = 'Query yielded more than one class instance' ):
        self.msg = msg

    def __str__(self):
	return repr( self.msg )

class ObjectUnreadyError(Error):
    def __init__(self, msg = 'The object is unready!' ):
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
        if not obj2_lookup.filter( id = obj1.id ).exists():
            obj2_lookup.add( obj1 )

    def fname(self):
        """docstring for fname"""
        pass


    def old_get_model_object( self, obj_type, **conditions ):
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

    def get_model_object( self, obj_type, **conditions ):
        """(DBTools, <arbitrary Django model object>) -> 
        <unsaved arbitrary Django model object> |  
        <saved arbitrary Django model object> | Error
        """
        try:
            with transaction.atomic():
                return obj_type.objects.get( **conditions )
        except IntegrityError:
            try:
                with transaction.atomic():
                    return obj_type.objects.create( **conditions )
            except IntegrityError:
                if not len( obj_type.objects.filter( **conditions ) ):
                    raise NonUniqueError(  )
                elif len( obj_type.objects.filter( **conditions ) ) > 1:
                    raise ClassNotFoundError(  )
                else:
                    raise ObjectUnreadyError()




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



    def read_canonical_spreadsheet(self, csvfile, delimiter = '\t'):
        """
        Parses a .csv spreadsheet into a line-by-line representation inside a dictionary.
        (This function can probably be replaced with the DictReader function in the csv module -- RJ)
        """
        with open(csvfile, 'rb') as current_file:
            all_lines = [line.strip().split(delimiter) for line in current_file]
            header = [column.strip() for column in all_lines[0]]  # Tokenize header
            current_spreadsheet = {}
            for line_count in range(1, len(all_lines)):  # Iterate over all lines after header
                current_spreadsheet[line_count] = {}
                for column_count in range(len(header)):
                    try:
                        # Some cells in the spreadsheet are empty and this is OK
                        cell_value = all_lines[line_count][column_count].strip()
                        if cell_value:
                            current_spreadsheet[line_count][header[column_count]] = cell_value
                        else:
                            current_spreadsheet[line_count][header[column_count]] = ''

                    except:
                        print "Error parsing column %s of line %s" % (column_count, line_count)
                        pass
        return current_spreadsheet











