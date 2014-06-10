"""Uploaders; a module for processing the various 
uploads and db updates required by 'hdome.pepsite'


"""
from db_ops import dbtools
from pepsite.models import *
import datetime
from django.utils.timezone import utc



class Uploads(dbtools.DBTools):
    """docstring for Uploads"""
    def __init__(self, *args, **kwargs):
        #super(Uploads, self).__init__()
        #self.arg = arg
        self.success = False
        self.data = None
        self.cell_line = None
        self.antibodies = []
        self.publications = []
        self.expt = None
        self.public = False
        self.now = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.nowstring = self.now.strftime('%H:%M:%S.%f %d %B %Y %Z')
        pass

    def preview_ss_simple(self, cleaned_data):
        """docstring for preview_ss_simple"""
        if int(cleaned_data[ 'expt1' ]) != -1: 
	    self.expt = self.get_model_object( Experiment, id = cleaned_data[ 'expt1' ] )
            self.expt_title = self.expt.title
        elif cleaned_data[ 'expt2' ].strip() != '':
            self.expt_title = cleaned_data[ 'expt2' ]
            self.cell_line = self.get_model_object( CellLine, id = cleaned_data[ 'cl1' ] )
        for ab in cleaned_data.getlist( 'ab1'):
            ab_obj = self.get_model_object( Antibody, id = ab ) 
            self.antibodies.append( ab_obj )
        for pl in cleaned_data.getlist( 'pl1' ):
            self.publications.append( self.get_model_object( Publication, id = pl ) )
        try:
            self.lodgement_title = cleaned_data[ 'ldg' ]
        except:
            self.lodgement_title = '%s Lodgement for %s' % ( self.nowstring, self.expt_title )
        self.dataset_title = 'Combined dataset for Lodgement: %s' % ( self.lodgement_title )
        try:
            cleaned_data[ 'rel' ]
            self.public = True
        except:
            pass

    def preprocess_ss_simple( self, fileobj ):
        #with open( ss_file
        allstr = ''
        for line in fileobj:
            allstr += line[0]
        self.allstr = allstr



    def upload_ss_simple(self, cleaned_data):
        """docstring for fname(self, cleaned_data"""
        self.success = True
        self.data = cleaned_data
        
        if int(cleaned_data[ 'expt1' ]) != -1: 
	    self.expt = self.get_model_object( Experiment, id = cleaned_data[ 'expt1' ] )
        elif cleaned_data[ 'expt2' ].strip() != '':
	    self.cell_line = self.get_model_object( CellLine, id = cleaned_data[ 'cl1' ] )
	    self.expt = self.get_model_object( Experiment, title = cleaned_data[ 'expt2' ], cell_line = self.cell_line )
            self.expt.save()
            for ab in cleaned_data.getlist( 'ab1'):
                ab_obj = self.get_model_object( Antibody, id = ab ) 
                self.antibodies.append( ab_obj )
                self.add_if_not_already(  ab_obj, self.expt.antibody_set )
        else:
            self.expt = None
        for pl in cleaned_data.getlist( 'pl1' ):
            self.publications.append( self.get_model_object( Publication, id = pl ) )



        
