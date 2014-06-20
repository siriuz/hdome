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
        self.delim = '\t'
        self.indexmap = []
        self.uldict = None
        self.valid = False
        self.match_dict = {
                'peptide_sequence' : { 'matches' : [ 'Peptide', 'Sequence' ], 'order' : 0, 'display' : 'Peptide Sequence' },
                'proteins' : { 'matches' : [ 'Names', 'protein', 'description' ], 'order' : 1, 'display' : 'Protein(s)' },
                'uniprot_ids' : { 'matches' : [ 'uniprot', 'Accessions' ], 'order' : 2, 'display' : 'UniProt code(s)' },
                'ptms' : { 'matches' : [ 'modification', 'ptm' ], 'order' : 3, 'display' : 'PTM(s)' },
                'confidence' : { 'matches' : [ 'confidence' ], 'order' : 4, 'display' : 'Confidence' },
                'charge' : { 'matches' : [ 'Theor z', 'charge' ], 'order' : 5, 'display' : 'Charge State' },
                'delta_mass' : { 'matches' : [ 'dMass' ], 'order' : 6, 'display' : 'Delta Mass (Da)' },
                'precursor_mass' : { 'matches' : [ 'Prec MW' ], 'order' : 7, 'display' : 'Precursor Mass (Da)' },
                'dataset_id' : { 'matches' : [ 'Spectrum' ], 'order' : 8, 'display' : 'Dataset' },
                'retention_time' : { 'matches' : [ 'Time'], 'order' : 9, 'display' : 'Restention Time (min)' },
                }

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

    def translate_headers( self, header ):
        coldic = {}
        headerdic = { b : [] for b in self.match_dict.keys() }
        valid = True
        for i in range(len( header )):
            coldic[header[i]] = []
            for k in self.match_dict.keys():
                v = self.match_dict[k][ 'matches' ]
                matching = False
                for trialstr in v:
                    if re.match( '\\w*%s' % ( trialstr ), header[i], flags = re.IGNORECASE ):
                        matching = True
                if matching:
                    coldic[header[i]].append(k)
                    headerdic[k].append(header[i])
                    self.indexmap.append([ self.match_dict[k]['order'], i, k ] )
        self.indexmap = sorted( self.indexmap, key = lambda a : a[0] )
        for k in coldic.keys():
            if len( coldic[k] ) != 1:
                valid = False
        for k in headerdic.keys():
            if len( headerdic[k] ) != 1:
                valid = False
        self.valid = valid

    def preprocess_ss_simple( self, fileobj ):
        #with open( ss_file
        allstr = '<table id=\"cssTable\" class=\"table table-striped tablesorter\">'
        headers = fileobj.readline().split( self.delim )
        self.translate_headers( headers )
        allstr += '<thead><tr>'
        for i, k, m in self.indexmap:
           allstr += '<th>' + self.match_dict[m]['display'] + '</th>'
        allstr += '</tr></thead><tbody>'
        j = 0
        uldict = {}
        for line in fileobj:
            if j:
                uldict[j] = {}
                elements = line.split(self.delim )
                allstr += '<tr>'
                for i, k, m in self.indexmap:
                    if ';' not in elements[k]:
                        if m == 'uniprot_id':
                            allstr += '<td><a href=\"http://www.uniprot.org/uniprot/' + elements[k].split('|')[1] + '\" target=\"_blank\">' + elements[k].split('|')[1] + '</a></td>'
                            uldict[j]['uniprot_id'] = [ elements[k].split('|')[1] ]
                        elif m in ( 'proteins', 'ptms' ):
                            if not elements[k]:
                                uldict[j][m] = []
                            else:
                                uldict[j][m] = [ elements[k] ]
                        else:
                            allstr += '<td>' + elements[k] + '</td>'
                            uldict[j][m] = elements[k]
                    else:
                        entries = []
                        allstr += '<td>'
                        for subel in elements[k].split(';'):
                            if m == 'uniprot_id':
                                allstr += '<a href=\"http://www.uniprot.org/uniprot/' + subel.split('|')[1] + '\" target=\"_blank\">' + subel.split('|')[1] + '</a>'
                                entries.append( subel.split('|')[1] )
                                #allstr += ' %u ' % ( u'{\% url \'http://www.uniprot.org/uniprot/%u\' \%}' % ( subel.split('|')[1] ) )
                            elif m in ( 'proteins', 'ptms' ):
                                if subel:
                                    entries.append( subel )

                            else:
                                allstr += ' %s ' % ( subel )
                                entries.append( subel[0] )
                        allstr += '</td>'
                        uldict[j][m] = entries
                allstr += '</tr>'
            j += 1
        allstr += '</tbody></table>'
        self.allstr = allstr
        self.uldict = uldict



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



        
