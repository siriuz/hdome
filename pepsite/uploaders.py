"""Uploaders; a module for processing the various 
uploads and db updates required by 'hdome.pepsite'


"""
from guardian.shortcuts import assign_perm
import dbtools
from pepsite.models import *
import datetime
from django.utils.timezone import utc
import uniprot


class Uploads(dbtools.DBTools):
    """docstring for Uploads"""
    def __init__(self, *args, **kwargs):
        #super(Uploads, self).__init__()
        #self.arg = arg
        self.user = None
        self.success = False
        self.data = None
        self.cell_line = None
        self.antibodies = []
        self.antibody_ids = []
        self.publications = []
        self.dataset_nos = []
        self.datasets = []
        self.uniprot_ids = []
        self.ptms = []
        self.expt = None
        self.expt_title = None
        self.expt_id = None
        self.instrument = None
        self.instrument_id = None
        self.cell_line = None
        self.cell_line_id = None
        self.lodgement = None
        self.lodgement_title = None
        self.public = False
        self.create_expt = True
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
                'confidence' : { 'matches' : [ 'confidence', 'Conf' ], 'order' : 4, 'display' : 'Confidence' },
                'charge' : { 'matches' : [ 'Theor z', 'charge' ], 'order' : 5, 'display' : 'Charge State' },
                'delta_mass' : { 'matches' : [ 'dMass' ], 'order' : 6, 'display' : 'Delta Mass (Da)' },
                'precursor_mass' : { 'matches' : [ 'Prec MW' ], 'order' : 7, 'display' : 'Precursor Mass (Da)' },
                'dataset_id' : { 'matches' : [ 'Spectrum' ], 'order' : 8, 'display' : 'Dataset' },
                'retention_time' : { 'matches' : [ 'Time'], 'order' : 9, 'display' : 'Restention Time (min)' },
                }
        if 'user' in kwargs.keys():
            self.user = kwargs['user']

    def repopulate(self, dic):
        """docstring for repopulate"""
        for k in dic.keys():
            setattr( self, k, dic[k] )
    
    def add_cutoff_mappings( self, post_dic, dm_prefix = 'dm_', cf_prefix = 'cf_' ):
        """docstring for add_cutoffs"""
        mdic = {}
        for no in self.dataset_nos:
            mdic[no] = {}
        for k in post_dic.keys():
            for no in self.dataset_nos:
                if k == dm_prefix + no:
                    mdic[no]['dm_cutoff'] = post_dic[k]
                elif k == cf_prefix + no:
                    mdic[no]['cf_cutoff'] = post_dic[k]
        self.cutoff_mappings = mdic



    def preview_ss_simple(self, cleaned_data):
        """docstring for preview_ss_simple"""
        if int(cleaned_data[ 'expt1' ]) != -1: 
	    self.expt = self.get_model_object( Experiment, id = cleaned_data[ 'expt1' ] )
            self.expt_title = self.expt.title
            self.expt_id = cleaned_data[ 'expt1' ] 
            self.instrument_id = cleaned_data[ 'inst' ] 
            self.instrument = self.get_model_object( Instrument, id = cleaned_data[ 'inst' ] )
            self.cell_line = self.expt.cell_line
            self.cell_line_id = self.expt.cell_line.id
        elif cleaned_data[ 'expt2' ].strip() != '':
            self.expt_title = cleaned_data[ 'expt2' ]
            self.create_expt = True
            self.cell_line_id = cleaned_data[ 'cl1' ] 
            self.instrument_id = cleaned_data[ 'inst' ] 
            self.cell_line = self.get_model_object( CellLine, id = cleaned_data[ 'cl1' ] )
            self.instrument = self.get_model_object( Instrument, id = cleaned_data[ 'inst' ] )
        for ab in cleaned_data.getlist( 'ab1'):
            ab_obj = self.get_model_object( Antibody, id = ab ) 
            self.antibodies.append( ab_obj )
            self.antibody_ids.append( ab )
        for pl in cleaned_data.getlist( 'pl1' ):
            self.publications.append( pl )
        try:
            self.lodgement_title = cleaned_data[ 'ldg' ]
        except:
            self.lodgement_title = '%s Lodgement for %s' % ( self.nowstring, self.expt_title )
        self.dataset_title = 'Combined dataset for Lodgement: %s' % ( self.lodgement_title )
        try:
            a = cleaned_data[ 'rel' ]
            self.public = True
            print 'made public'
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
        #with open( ss_files
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
                        if m == 'dataset_id':
                            ds_no = elements[k].split('.')[0]
                            uldict[j][ 'spectrum' ] = elements[k]
                            uldict[j][ 'dataset' ] = ds_no
                            allstr += '<td>' + ds_no + '</td>'
                            if ds_no not in self.dataset_nos:
                                self.dataset_nos.append( ds_no )


                        elif m == 'uniprot_ids':
          
                            allstr += '<td><a href=\"http://www.uniprot.org/uniprot/' + elements[k].split('|')[1] + '\" target=\"_blank\">' + elements[k].split('|')[1] + '</a></td>'
                            uldict[j]['uniprot_ids'] = [ elements[k].split('|')[1] ]
                            if elements[k].split('|')[1] not in self.uniprot_ids:
                                self.uniprot_ids.append( elements[k].split('|')[1] )
                        elif m in ( 'proteins', 'ptms' ):
                            if not elements[k]:
                                uldict[j][m] = []
                                allstr += '<td/>'
                            else:
                                uldict[j][m] = [ elements[k] ]
                                allstr += '<td>%s</td>' % ( elements[k] )
                        else:
                            allstr += '<td>' + elements[k] + '</td>'
                            uldict[j][m] = elements[k]
                    else:
                        entries = []
                        allstr += '<td>'
                        loclist = [ b.strip() for b in elements[k].split(';') ]
                        for subel in loclist:
                            if m == 'uniprot_ids':
                                allstr += ' <a href=\"http://www.uniprot.org/uniprot/' + subel.split('|')[1] + '\" target=\"_blank\">' + subel.split('|')[1] + '</a> '
                                entries.append( subel.split('|')[1] )
                                if subel.split('|')[1] not in self.uniprot_ids:
                                    self.uniprot_ids.append( subel.split('|')[1] ) 
                                #allstr += ' %u ' % ( u'{\% url \'http://www.uniprot.org/uniprot/%u\' \%}' % ( subel.split('|')[1] ) )
                            elif m in ( 'proteins', 'ptms' ):
                                if subel:
                                    entries.append( subel )
                                    allstr += ' %s ' % ( subel )

                            else:
                                allstr += ' %s ' % ( loclist[0] )
                                entries.append( loclist[0] )
                        allstr += '</td>'
                        uldict[j][m] = entries
                allstr += '</tr>'
            j += 1
        allstr += '</tbody></table>'
        self.allstr = allstr
        self.uldict = uldict
        self.dataset_nos = sorted( self.dataset_nos )

    def prepare_upload_simple(self):
        """docstring for fname(self, cleaned_data"""
        self.instrument = self.get_model_object( Instrument, id = self.instrument_id )
        self.cell_line = self.get_model_object( CellLine, id = self.cell_line_id )
        if not self.expt_id:
            self.expt = self.get_model_object( Experiment, cell_line = self.cell_line, title = self.expt_title )
            self.expt.save()
        else:
            self.expt = self.get_model_object( Experiment, id = self.expt_id )
            self.expt.save()
        for ab in self.antibodies:
                self.add_if_not_already(  ab, self.expt.antibody_set )
        if not self.lodgement:
            self.lodgement = self.get_model_object( Lodgement, user = self.user, title = self.lodgement_title, datetime = self.now )
            self.lodgement.save()
            if self.publications:
                for pl in self.publications:
                    pbln = self.get_model_object( Publication, id=pl )
                    self.add_if_not_already(  pl, self.lodgement.publication_set )
        for dsno in self.dataset_nos:
            ds = self.get_model_object( Dataset, instrument = self.instrument, lodgement = self.lodgement, experiment = self.expt,
                    datetime = self.now, title = 'Dataset #%s from %s' % ( dsno, self.lodgement_title ), 
                    dmass_cutoff = self.cutoff_mappings[dsno]['dm_cutoff'], confidence_cutoff = self.cutoff_mappings[dsno]['cf_cutoff'] )
            ds.save()
            assign_perm('view_dataset', self.user, ds)
            for group in self.user.groups.all():
                assign_perm('view_dataset', group, ds)
            if self.public:
                assign_perm('view_dataset', User.objects.get( id = -1 ), ds)


            self.datasets.append( ds )

    def get_protein_metadata( self ):
        self.uniprot_data = uniprot.batch_uniprot_metadata( self.uniprot_ids )
        

    def upload_simple( self ):
        """None -> None
        """
        for k in self.uldict.keys():
            local = self.uldict[k]
            pep = self.get_model_object( Peptide, sequence = local['peptide_sequence'] )
            pep.save()
            proteins = []
            ptms = []
            for prt, unp in zip( local['proteins'], local['uniprot_ids'] ):
                pr1 = self.get_model_object( Protein,  prot_id = unp, description = prt, name = prt )
                try:
                    sequence = self.uniprot_data[ unp ]['sequence']
                    pr1.sequence = sequence
                    pr1.save()
                except:
                    pr1.save()
                proteins.append( pr1 )
            for ptm_desc in local['ptms']:
                ptm = self.get_model_object( Ptm, description = ptm_desc, name = ptm_desc )
                ptm.save()
                ptms.append( ptm )
            dsno = local['dataset']
            dataset = self.get_model_object( Dataset, instrument = self.instrument, lodgement = self.lodgement, experiment = self.expt,
                    datetime = self.now, title = 'Dataset #%s from %s' % ( dsno, self.lodgement_title )  )
            dataset.save()
            ## object permissions:
            assign_perm('view_dataset', self.user, dataset)
            for group in self.user.groups.all():
                assign_perm('view_dataset', group, dataset)
            if self.public:
                assign_perm('view_dataset', User.objects.get( id = -1 ), dataset)
            
            ##
            ion = self.get_model_object( Ion,  charge_state = local['charge'], precursor_mass = local['precursor_mass'],
                    retention_time = local['retention_time'], experiment = self.expt, dataset = dataset )
            ion.save()
            ide = self.get_model_object( IdEstimate, ion = ion, peptide = pep, confidence = local['confidence'], delta_mass = local['delta_mass'] )
            ide.save()
            for ptm in ptms:
                self.add_if_not_already( ptm, ide.ptms )
                #ide.save()
            for protein in proteins:
                p2p = self.get_model_object( PepToProt, peptide = pep, protein = protein )
                p2p.save()


 



