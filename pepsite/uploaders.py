"""Uploaders; a module for processing the various 
uploads and db updates required by 'hdome.pepsite'


"""
from guardian.shortcuts import assign_perm
import dbtools
from pepsite.models import *
import datetime
from django.utils.timezone import utc
import uniprot
from django.db.models import Count
from django.db import IntegrityError, transaction
import time
from django.db import connection


class Uploads(dbtools.DBTools):
    """docstring for Uploads"""
    def __init__(self, *args, **kwargs):
        #super(Uploads, self).__init__()
        #self.arg = arg
        self.user = None
        self.success = False
        self.data = None
        self.cell_line = None
        self.multiple = False
        self.antibodies = []
        self.antibody_ids = []
        self.publications = []
        self.dataset_nos = []
        self.ldg_details = []
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
        self.ldg_ds_mappings = {}
        self.lodgement_title = None
        self.public = False
        self.create_expt = True
        self.now = datetime.datetime.utcnow().replace(tzinfo=utc)
        self.nowstring = self.now.strftime('%H:%M:%S.%f %d %B %Y %Z')
        self.delim = '\t'
        self.indexmap = []
        self.allfields = None
        self.allstr = ''
        self.uldict = None
        self.valid = False
        self.match_dict = {
            'peptide_sequence': {
                'matches': ['Peptide', 'Sequence'],
                'order': 0,
                'display': 'Peptide Sequence'},

            'proteins': {
                'matches': ['Names', 'protein', 'description'],
                'order': 1,
                'display': 'Protein(s)'},

            'uniprot_ids': {
                'matches': ['uniprot', 'Accessions'],
                'order': 2,
                'display': 'UniProt code(s)'},

            'ptms': {
                'matches': ['modification', 'ptm'],
                'order': 3,
                'display': 'PTM(s)'},

            'confidence': {
                'matches': ['confidence', 'Conf'],
                'order': 4,
                'display': 'Confidence'},

            'charge': {
                'matches': ['Theor z', 'charge'],
                'order': 5,
                'display': 'Charge State'},

            'delta_mass': {
                'matches': ['dMass'],
                'order': 6,
                'display': 'Delta Mass (Da)'},

            'precursor_mass': {
                'matches': ['Prec MW'],
                'order': 8,
                'display': 'Precursor Mass (Da)'},

            'mz': {
                'matches': ['Prec m/z'],
                'order': 7,
                'display': 'Precursor m/z'},

            'dataset_id': {
                'matches': ['Spectrum'],
                'order': 9,
                'display': 'Dataset'},

            'retention_time': {
                'matches': ['Time'],
                'order': 10,
                'display': 'Restention Time (min)'},
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
        for k in post_dic.keys():
            if k == dm_prefix:
                pass
                #mdic['dm_cutoff'] = post_dic[k]
            elif k == cf_prefix:
                mdic['cf_cutoff'] = post_dic[k]
        self.cutoff_mappings = mdic
    
    def add_cutoff_mappings_multiple( self, post_dic, dm_prefix = 'dm_', cf_prefix = 'cf_' ):
        """docstring for add_cutoffs"""
        mdic = {}
        for no, name, filename in self.ldg_details:
            mdic[no] = {}
        for k in post_dic.keys():
            for no, name, filename in self.ldg_details:
                if k == dm_prefix + str(no):
                    pass
                    #mdic[no]['dm_cutoff'] = post_dic[k]
                elif k == cf_prefix + str(no):
                    mdic[no]['cf_cutoff'] = post_dic[k]
        self.cutoff_mappings = mdic
        print 'post_dic', post_dic, 'cutoff_mappings', self.cutoff_mappings

    def preview_ss_simple(self, cleaned_data):
        """docstring for preview_ss_simple"""
        if int(cleaned_data[ 'expt1' ]) != -1:
            self.expt = self.get_model_object( Experiment, id = cleaned_data[ 'expt1' ] )
            self.expt_desc = self.expt.description
            self.expt_title = self.expt.title
            self.expt_id = cleaned_data[ 'expt1' ] 
            self.instrument_id = cleaned_data[ 'inst' ] 
            self.instrument = self.get_model_object( Instrument, id = cleaned_data[ 'inst' ] )
            self.cell_line = self.expt.cell_line
            self.cell_line_id = self.expt.cell_line.id
        elif cleaned_data[ 'expt2' ].strip() != '':
            self.expt_title = cleaned_data[ 'expt2' ]
            if 'expt2_desc' in cleaned_data.keys():
                self.expt_desc = cleaned_data['expt2_desc']
            else:
                self.expt_desc = ''
            self.create_expt = True
            self.cell_line_id = cleaned_data[ 'cl1' ] 
            self.instrument_id = cleaned_data[ 'inst' ] 
            self.cell_line = self.get_model_object( CellLine, id = cleaned_data[ 'cl1' ] )
            self.instrument = self.get_model_object( Instrument, id = cleaned_data[ 'inst' ] )
            try:
                ab1 = cleaned_data.getlist( 'ab1')
            except:
                ab1 = cleaned_data[ 'ab1' ]
            for ab in ab1:
                ab_obj = self.get_model_object( Antibody, id = ab ) 
                self.antibodies.append( ab_obj )
                self.antibody_ids.append( ab )
        if 'pl1' in cleaned_data.keys():
            #for pl in cleaned_data.getlist( 'pl1' ):
            for pl in cleaned_data[ 'pl1' ]:
                self.publications.append( pl )
        try:
            self.lodgement_title = 'Filename = \"%s\", %s' % (  cleaned_data['filename'], cleaned_data[ 'ldg' ] )
        except:
            self.lodgement_title = 'Filename = \"%s\", Datetime = %s, Lodgement for Experiment = \"%s\"' % ( cleaned_data['filename'], self.nowstring, self.expt_title )
        self.dataset_title = 'Combined dataset for Lodgement: %s' % ( self.lodgement_title )
        try:
            a = cleaned_data[ 'rel' ]
            self.public = True
            print 'made public'
        except:
            pass
        try:
            self.filename = cleaned_data['filename']
        except:
            pass

    def translate_headers( self, header ):
        coldic = {}
        # Creates a new dictionary using the keys in match_dict (defined above)
        headerdic = { b : [] for b in self.match_dict.keys() }
        valid = True

        # Iterates over each item in the header
        for i in range(len( header )):

            # header[i] is simply the the i-th item in header
            coldic[header[i]] = []

            # For each key in match_dict do..
            for k in self.match_dict.keys():

                # Sets v to the matching strings for key k
                v = self.match_dict[k][ 'matches' ]
                matching = False

                # For each matching string do a regex to see if it is in the header item
                for trialstr in v:
                    if re.match( '\\w*%s' % ( trialstr ), header[i], flags = re.IGNORECASE ):
                        matching = True

                # If there is a match then add this key to the coldic
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

    def preprocess_ss_from_bulk( self, fileobj, ldg_name, ldg_no ):
        j = self.counter
        lc = 0
        uldict = {}
        allstr = self.allstr
        fileobj.readline()
        self.ldg_ds_mappings[ ldg_no ] = []

        for line in fileobj:
            if lc:
                uldict[j] = {}
                elements = line.split(self.delim )
                allstr += '<tr>'
                for i, k, m in self.indexmap:
                    if ';' not in elements[k]:
                        if m == 'dataset_id':
                            ds_no = elements[k].split('.')[0]
                            uldict[j][ 'spectrum' ] = elements[k]
                            uldict[j][ 'dataset' ] = ds_no
                            uldict[j][ 'ldg_name' ] = ldg_name
                            uldict[j][ 'ldg_no' ] = ldg_no
                            allstr += '<td>' + ds_no + '</td>'
                            if ds_no not in self.ldg_ds_mappings[ldg_no]:
                                self.dataset_nos.append( ds_no )
                                self.ldg_ds_mappings[ldg_no].append( ds_no )


                        elif m == 'uniprot_ids':
                            #print elements[k]
          
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
                allstr += '<td>%s</td>' % ( ldg_name )
                allstr += '</tr>'
            j += 1
            lc += 1
            self.counter = j
        #allstr += '</tbody></table>'
        self.allstr = allstr
        self.uldict = uldict
        self.dataset_nos = sorted( self.dataset_nos )

    def preprocess_ss_simple( self, fileobj ):
        #with open( ss_files
        self.lodgement_filename = fileobj.name
        allstr = '<table id=\"cssTable\" class=\"table table-striped tablesorter\">'
        headers = fileobj.readline().split( self.delim )
        self.translate_headers( headers )
        allstr += '<thead><tr>'
        for i, k, m in self.indexmap:
           allstr += '<th>' + self.match_dict[m]['display'] + '</th>'
        allstr += '</tr></thead><tbody>'
        j = 0
        uldict = {}
        proteinfields = []
        peptidefields = []
        datasetfields = []
        ionfields = []
        idestimatefields = []
        ptmfields = []
        singlerows = []
        rawlines = []
        row_indices = []

        for line in fileobj:
            if j:
                row_indices.append(j)
                rawlines.append(line)
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


                        elif m == 'uniprot_ids' and len(elements[k].strip().split('|')) > 1: #not in ( 'segment', 'rrrrrsegment' ):
                            
                            #print 'element = %s' % elements[k]
          
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
                        elif m in ('precursor_mass', 'confidence', 'delta_mass'):
                            allstr += '<td>' + elements[k] + '</td>'
                            uldict[j][m] = str(round(float(elements[k]), 5))
                        elif m not in ('uniprot_ids'):
                            allstr += '<td>' + elements[k] + '</td>'
                            uldict[j][m] = elements[k]
                        else:
                            allstr += '<td></td>'
                            uldict[j][m] = ['']

                    else:
                        entries = []
                        allstr += '<td>'
                        loclist = [ b.strip() for b in elements[k].split(';') if b.strip() != 'segment' ]
                        for subel in loclist:
                            if m == 'uniprot_ids' and len(subel.split('|')) > 1:
                                allstr += ' <a href=\"http://www.uniprot.org/uniprot/' + subel.split('|')[1] + '\" target=\"_blank\">' + subel.split('|')[1] + '</a> '
                                entries.append( subel.split('|')[1] )
                                #uldict[j]['uniprot_ids'] = [ elements[k].split('|')[1] ]
                                if subel.split('|')[1] not in self.uniprot_ids:
                                    self.uniprot_ids.append( subel.split('|')[1] ) 
                                #allstr += ' %u ' % ( u'{\% url \'http://www.uniprot.org/uniprot/%u\' \%}' % ( subel.split('|')[1] ) )
                            elif m in ( 'proteins', 'ptms' ):
                                if subel:
                                    entries.append( subel )
                                    allstr += ' %s ' % ( subel )

                            elif m not in ('uniprot_ids'):
                                allstr += ' %s ' % ( loclist[0] )
                                entries.append( loclist[0] )
                            else:
                                allstr += ' '
                                entries.append( '' )

                        allstr += '</td>'
                        uldict[j][m] = entries
                allstr += '</tr>'
                ## tuples for bulk sql inserts later
                peptidefields.append( uldict[j]['peptide_sequence'] )
                proteinfields.append( [ [x[0], x[1]] for x in zip(uldict[j]['uniprot_ids'], uldict[j]['proteins']) ]   )
                datasetfields.append( uldict[j]['dataset'] )
                ionfields.append( ( uldict[j]['charge'], uldict[j]['precursor_mass'], uldict[j]['retention_time'], uldict[j]['mz'], uldict[j]['spectrum'] ) ) 
                idestimatefields.append( ( uldict[j]['confidence'], uldict[j]['delta_mass'] ) )
                ptmfields.append( [ b for b in uldict[j]['ptms'] ] )
                ##
                singlerows.append( [j,  uldict[j]['peptide_sequence'], uldict[j]['charge'], uldict[j]['precursor_mass'],
                        uldict[j]['retention_time'], uldict[j]['mz'], uldict[j]['confidence'], uldict[j]['delta_mass'], uldict[j]['spectrum'], uldict[j]['dataset'] ] )
                self.singlerows_header = ['rownum', 'peptide_sequence', 'charge', 'precursor_mass', 'retention_time', 'mz', 'confidence', 'delta_mass', 'spectrum', 'dataset']
            j += 1
        allstr += '</tbody></table>'
        self.allstr = allstr
        self.uldict = uldict
        self.allfields = { 'row_indices' : row_indices, 'peptidefields' : peptidefields, 'proteinfields' : proteinfields, 'datasetfields' : datasetfields,
                'ionfields' : ionfields, 'idestimatefields' : idestimatefields, 'ptmfields' : ptmfields } 
        self.singlerows = singlerows
        self.rawlines = rawlines
        self.dataset_nos = sorted( self.dataset_nos )
        return self.allfields

    def prepare_upload_simple(self):
        """docstring for fname(self, cleaned_data"""
        self.instrument = Instrument.objects.get( id = self.instrument_id )
        self.cell_line = CellLine.objects.get( id = self.cell_line_id )
        if not self.expt_id:
            self.expt, _ = Experiment.objects.get_or_create( cell_line = self.cell_line, title = self.expt_title, description = self.expt_desc )
        else:
            self.expt = Experiment.objects.get( id = self.expt_id )
        assign_perm('view_experiment', self.user, self.expt)
        assign_perm('edit_experiment', self.user, self.expt)
        for group in self.user.groups.all():
            assign_perm('view_experiment', group, self.expt)
        for ab in self.antibodies:
                self.expt.antibody_set.add( ab )
        if not self.lodgement:
            self.lodgement, _ = Lodgement.objects.get_or_create( user = self.user, title = self.lodgement_filename, datetime = self.now, datafilename=self.lodgement_filename )
            if self.publications:
                for pl in self.publications:
                    pbln = Publication.objects.get( id=pl )
                    self.lodgement.publication_set.add( pl )
        print 'cf_cutoff = %s' % self.cutoff_mappings['cf_cutoff']
        for dsno in self.dataset_nos:
            ds, _ = Dataset.objects.get_or_create( instrument = self.instrument, lodgement = self.lodgement, experiment = self.expt,
                    datetime = self.now, title = self.entitle_ds(dsno, self.lodgement_filename),
                    confidence_cutoff = self.cutoff_mappings['cf_cutoff'] )
            assign_perm('view_dataset', self.user, ds)
            assign_perm('edit_dataset', self.user, ds)
            for group in self.user.groups.all():
                assign_perm('view_dataset', group, ds)
            if self.public:
                assign_perm('view_dataset', user.objects.get( id = -1 ), ds)


            self.datasets.append( ds )
    
    def entitle_ds(self, dsno, filename):
        return 'dataset #%s from %s' % ( dsno, filename )

    def prepare_upload_simple_multiple(self ):
        for ldg_no, ldg_name, filename in self.ldg_details:
            self.prepare_ind_lodgement( ldg_no, ldg_name, filename )

    def prepare_ind_lodgement(self, ldg_no, ldg_name, filename ):
        """docstring for fname(self, cleaned_data"""
        self.instrument = instrument.objects.get( id = self.instrument_id )
        self.cell_line = cellline.objects.get( id = self.cell_line_id )
        if not self.expt_id:
            self.expt, _ = experiment.objects.get_or_create( cell_line = self.cell_line, title = self.expt_title, description = self.expt_desc )
        else:
            self.expt = experiment.objects.get( id = self.expt_id )
        assign_perm('view_experiment', self.user, self.expt)
        for ab in self.antibodies:
                self.expt.antibody_set.add( ab )
        lodgement, _ = lodgement.objects.get_or_create( user = self.user, title = ldg_name, datetime = self.now, datafilename=filename.split('/')[-1] )
        if self.publications:
            for pl in self.publications:
                    pbln = publication.objects.get( id=pl )
                    lodgement.publication_set.add( pl )
        print 'ldg_ds_mappings here:', self.ldg_ds_mappings
        for dsno in self.ldg_ds_mappings[str(ldg_no)]:
            ds, _ = dataset.objects.get_or_create( instrument = self.instrument, lodgement = lodgement, experiment = self.expt,
                    datetime = self.now, title = 'dataset #%s from %s' % ( dsno, ldg_name ),
                    #dmass_cutoff = self.cutoff_mappings[ldg_no]['dm_cutoff'], 
                    confidence_cutoff = self.cutoff_mappings[ldg_no]['cf_cutoff'] )
            print 'cutoffs here for dataset: %s, in lodgement %s, dm cutoff: %s, cf cutoff: %s' % ( ds.title, lodgement.title, ds.dmass_cutoff, ds.confidence_cutoff ) 
            assign_perm('view_dataset', self.user, ds)
            assign_perm('edit_dataset', self.user, ds)
            for group in self.user.groups.all():
                assign_perm('view_dataset', group, ds)
            if self.public:
                assign_perm('view_dataset', user.objects.get( id = -1 ), ds)


            self.datasets.append( ds )

    def get_protein_metadata( self ):
        self.uniprot_data = uniprot.batch_uniprot_metadata( self.uniprot_ids )
        

    @transaction.atomic
    def upload_simple( self ):
        """none -> none
        """
        i = 0
        t0 = time.time()
        assign_perm( 'edit_lodgement', self.user, self.lodgement )
        print 'edit_lodgement, user = %s, lodgement = %s' % ( self.user.username, self.lodgement.title )
        for k in self.uldict.keys():
            with transaction.atomic():
                i += 1
                print i
                local = self.uldict[k]
                pep, _ = peptide.objects.get_or_create( sequence = local['peptide_sequence'] )
                proteins = []
                ptms = []
                for prt, unp in zip( local['proteins'], local['uniprot_ids'] ):
                    pr1, _ = protein.objects.get_or_create(  prot_id = unp, description = prt, name = prt )
                    proteins.append( pr1 )
                for ptm_desc in local['ptms']:
                    ptm, _ = ptm.objects.get_or_create( description = ptm_desc, name = ptm_desc )
                    ptms.append( ptm )
                dsno = local['dataset']
                dataset, _ = dataset.objects.get_or_create( instrument = self.instrument, lodgement = self.lodgement, experiment = self.expt,
                        datetime = self.now, title = 'dataset #%s from %s' % ( dsno, self.lodgement_title )  )
                ion, _ = ion.objects.get_or_create(  charge_state = local['charge'], precursor_mass = local['precursor_mass'],
                        retention_time = local['retention_time'], mz = local['mz'], experiment = self.expt, dataset = dataset, spectrum = local['spectrum'] )
                ide, _ = idestimate.objects.get_or_create( ion = ion, peptide = pep, confidence = local['confidence'], delta_mass = local['delta_mass'] )
                for ptm in ptms:
                    ide.ptms.add( ptm )
                for protein in proteins:
                    p2p, _ = peptoprot.objects.get_or_create( peptide = pep, protein = protein )
                    self.expt.proteins.add(protein) 
        t1 = time.time()
        tt = t1-t0
        print 'upload time taken =%f' % (tt) 


    def reformat_to_str(self, iterable ):
        retstr = '('
        for elem in iterable:
            if not elem:
                retstr += 'null, '

            elif type( elem ) in ( list, tuple ):
                retstr += self.reformat_to_str(elem)
            elif type( elem ) == int:
                retstr += '%s, ' % elem
            elif elem.isdigit():
                retstr += '%s, ' % elem
            else:
                try:
                    retstr += '%f, ' % float(elem)
                except ValueError:
                    retstr += 'e\'%s\', ' % elem.replace('\'', '\\\'')
        retstr = retstr.strip(', ') + ' ), '
        return retstr



    def upload_megarapid(self):
        """docstring for upload_rapid"""
        self.filename = self.lodgement_filename

        dfile = 'logfile_data.csv.tmp'
        open(dfile, 'wb').close()

        proteinstr = ''
        for b in self.allfields['proteinfields']:
            for x in range( len(b) ):
                if b[x][0]:
                    proteinstr += '(e\'%s\', e\'%s\'), ' % ( b[x][1].replace('\'', '\\\''), b[x][0].replace('\'', '\\\'') )
                else:
                    proteinstr += '( e\'%s\', null ), ' % ( b[x][1].replace('\'', '\\\'') )
        proteinstr = proteinstr.strip(', ')

        peptidestr = ''
        peptide_find_str = ''
        for b, c in zip(self.allfields['peptidefields'], self.allfields['row_indices']):
            peptidestr += '(\'%s\'), ' % ( b )
            peptide_find_str += '(\'%s\', %d), ' % ( b, c )
        peptidestr = peptidestr.strip(', ')
        peptide_find_str = peptide_find_str.strip(', ')

        ptmstr = ''
        for b in self.allfields['ptmfields']:
            if b:
                for x in b:
                    ptmstr += '(\'%s\'), ' % x
        ptmstr = ptmstr.strip(', ')

        ionstr = ''
        for b, c in zip(self.allfields['ionfields'], self.allfields['datasetfields']):
            title = self.entitle_ds( c, self.filename )
            ionstr += '(%d, %f, %f, %f, \'%s\', \'%s\', %d ), ' % ( int(b[0]), float(b[1]), float(b[2]), float(b[3]), b[4], title, int(self.expt.id) )

        ionstr = ionstr.strip(', ')

        
        dsstr = ''
        ds_find_str = ''
        for c, d in zip(self.allfields['row_indices'],  self.allfields['datasetfields']):
            title = self.entitle_ds( d, self.filename )
            dsstr += '(\'%s\', %d), ' % (title, self.expt.id)
            ds_find_str += '(%d, \'%s\', %d), ' % (c, title, self.expt.id)
        dsstr = dsstr.strip(', ')
        ds_find_str = ds_find_str.strip(', ')

        cursor = connection.cursor()

        for row in self.singlerows:
            row.append( self.expt.id )
        self.singlerows_header.append( 'experiment_id' )

        sqldsfind = 'with f as \
                (select t2.id as dataset_id, rownum from \
                (values %s) as ds(rownum, ds_title, expt_id) \
                left join pepsite_dataset t2 \
                on (ds.ds_title = t2.title and t2.experiment_id = ds.expt_id ) ) \
                select dataset_id from f \
                order by rownum \
                ' % ds_find_str
        cursor.execute( sqldsfind )
        newmastercol = cursor.fetchall()
        for row, new in zip( self.singlerows, [b[0] for b in newmastercol ] ) :
            row.append( new )
        self.singlerows_header.append( 'dataset_id' )

        cursor.execute( 'select count(*) from pepsite_protein' )
        print 'protein', cursor.fetchall()
        sqlprot = 'with f as \
                ( select distinct on (description) i.description, i.description as \"name\", i.prot_id \
                from (values %s) as i(description, prot_id) \
                order by description, prot_id ) \
                insert into pepsite_protein (description, \"name\", prot_id) \
                select f.description, f.\"name\", f.prot_id from f \
                left join pepsite_protein as existing \
                on (existing.description = f.description ) \
                where existing.id is null \
                ' % ( proteinstr )
        cursor.execute( sqlprot )
        cursor.execute( 'select count(*) from pepsite_protein' )
        print 'protein', cursor.fetchall()



        cursor.execute( 'select count(*) from pepsite_peptide' )
        print 'peptide', cursor.fetchall()
        sqlpep = 'insert into pepsite_peptide (\"sequence\") \
        select distinct i.field1 \"sequence\" \
            from (values %s) as i(field1) \
            left join pepsite_peptide as existing \
            on (existing.\"sequence\" = i.field1) \
            where existing.id is null \
            ' % ( peptidestr )
        cursor.execute( sqlpep )
        cursor.execute( 'select count(*) from pepsite_peptide' )
        print 'peptide', cursor.fetchall()

        sqlpepsfind = 'with f as \
                (select t2.id as peptide_id, rownum from \
                (values %s) as peps( peptide_sequence, rownum) \
                left join pepsite_peptide t2 \
                on (peps.peptide_sequence = t2.sequence ) ) \
                select peptide_id from f \
                order by rownum \
                ' % peptide_find_str
        cursor.execute( sqlpepsfind )
        newmastercol = cursor.fetchall()
        #print newmastercol
        for row, new in zip( self.singlerows, [b[0] for b in newmastercol ] ) :
            row.append( new )
        self.singlerows_header.append( 'peptide_id' )

        cursor.execute( 'select count(*) from pepsite_ptm' )
        print 'ptm', cursor.fetchall()
        sqlptm = 'INSERT INTO pepsite_ptm (\"description\", \"name\") \
                SELECT DISTINCT i.field1 \"description\", i.field1 \"name\" \
                FROM (VALUES %s) AS i(field1) \
                LEFT JOIN pepsite_ptm as existing \
                ON (existing.\"description\" = i.field1) \
                WHERE existing.id IS NULL \
                ' % ( ptmstr )
        cursor.execute( sqlptm )
        cursor.execute( 'SELECT COUNT(*) FROM pepsite_ptm' )
        print 'ptm', cursor.fetchall()[0]

        cursor.execute( 'SELECT COUNT(*) FROM pepsite_ion' )
        print 'ion', cursor.fetchall()

        masterstr = self.reformat_to_str(self.singlerows).strip(', ')[1:-1]
        print self.singlerows[:5]

        with open(dfile, 'a') as f:
            for line in masterstr:
                f.write(line)

        sqlion_new = 'WITH f AS \
            (SELECT foo.* FROM  (VALUES %s ) AS foo(rownum, peptide_sequence, charge_state, precursor_mass, \
            retention_time, mz, confidence, delta_mass, spectrum, dataset_title, experiment_id, dataset_id, peptide_id ) ) \
            INSERT INTO pepsite_ion (charge_state, precursor_mass, retention_time, mz, spectrum, dataset_id, experiment_id) \
            SELECT DISTINCT f.charge_state, f.precursor_mass, f.retention_time, f.mz, f.spectrum, f.dataset_id, f.experiment_id \
            FROM f LEFT JOIN pepsite_ion AS existing \
            ON (f.dataset_id = existing.dataset_id AND f.charge_state = existing.charge_state AND f.retention_time = existing.retention_time \
            AND f.mz = existing.mz AND f.spectrum = existing.spectrum AND f.experiment_id = existing.experiment_id) \
            where existing.id IS NULL\
            ' % ( masterstr )
        print '\n\n%s\n\n' % sqlion_new
        cursor.execute( sqlion_new )
        cursor.execute( 'SELECT COUNT(*) FROM pepsite_ion' )
        print 'ion', cursor.fetchall()

        sqlionfind = 'WITH f AS \
            (SELECT foo.* FROM  (VALUES %s ) AS foo(rownum, peptide_sequence, charge_state, precursor_mass, \
            retention_time, mz, confidence, delta_mass, spectrum, dataset_title, experiment_id, dataset_id, peptide_id ) ) \
            SELECT existing.id \
            FROM f INNER JOIN pepsite_ion AS existing \
            ON (f.dataset_id = existing.dataset_id AND f.charge_state = existing.charge_state AND f.retention_time = existing.retention_time \
            AND f.mz = existing.mz AND f.spectrum = existing.spectrum AND f.experiment_id = existing.experiment_id) \
            ORDER BY rownum \
            ' % ( masterstr )
        print '\n\n%s\n\n' % sqlionfind
        cursor.execute( sqlionfind )
        ionsfound = cursor.fetchall()
        print '\n\nionsfound:\n\n%s\n\n' % str(ionsfound[:5])
        newmastercol = [b[-1] for b in ionsfound]
        for row, new in zip( self.singlerows, newmastercol ) :
            row.append( new )
        self.singlerows_header.append( 'ion_id' )

        print self.singlerows[:5]

        cursor.execute( 'SELECT COUNT(*) FROM pepsite_idestimate' )
        print 'idestimate', cursor.fetchall()

        masterstr = self.reformat_to_str(self.singlerows).strip(', ')[1:-1]
        #masterstr = str(ionsfound)[1:-1]
        print '\nmasterstr\n', masterstr, '\n'
        #print 'masterstr: %s' % self.reformat_to_str(self.singlerows[:5]).strip(', ')[1:-1]

        sqlide_new = 'WITH f AS \
                (SELECT * FROM  (VALUES %s ) AS foo(rownum, peptide_sequence, charge_state, precursor_mass, \
                retention_time, mz, confidence, delta_mass, spectrum, dataset_title, experiment_id, dataset_id, peptide_id, ion_id ) ) \
                INSERT INTO pepsite_idestimate (peptide_id, ion_id, delta_mass, confidence, \"isRemoved\", \"isValid\") \
                select f.peptide_id, f.ion_id, f.delta_mass, f.confidence, false, false \
                from f \
                LEFT JOIN pepsite_idestimate AS existing \
                ON (f.peptide_id = existing.peptide_id AND f.ion_id = existing.ion_id AND f.confidence = existing.confidence \
                AND f.delta_mass = existing.delta_mass ) \
                where existing.id IS NULL \
                ' % ( masterstr )
        print '\n\n%s\n\n' % sqlide_new
        cursor.execute( sqlide_new )
        cursor.execute( 'SELECT COUNT(*) FROM pepsite_idestimate' )
        print 'idestimate', cursor.fetchall()

        sqlidefind = 'WITH f AS \
                (SELECT * FROM  (VALUES %s ) AS foo(rownum, peptide_sequence, charge_state, precursor_mass, \
                retention_time, mz, confidence, delta_mass, spectrum, dataset_title, experiment_id, dataset_id, peptide_id, ion_id ) ORDER BY rownum)  \
                SELECT id \
                from f \
                LEFT JOIN pepsite_idestimate AS existing \
                ON (f.peptide_id = existing.peptide_id AND f.ion_id = existing.ion_id AND f.confidence = existing.confidence \
                AND f.delta_mass = existing.delta_mass ) \
                ORDER BY rownum \
                ' % ( masterstr )
        cursor.execute( sqlidefind )
        newmastercol = cursor.fetchall()
        for row, new in zip( self.singlerows, [b[0] for b in newmastercol ] ) :
            row.append( new )
        self.singlerows_header.append( 'idestimate_id' )

        ideptmlist = []
        idetoprotlist = []
        for row, ptms, prots in zip( self.singlerows, self.allfields['ptmfields'], self.allfields['proteinfields'] ):
            if ptms:
                for ptm in ptms:
                    ideptmlist.append( [ row[-1], ptm ] )
            if prots:
                for prot in prots:
                    idetoprotlist.append( [ row[-1], prot[0], prot[1] ] )

        ideptmstr = self.reformat_to_str(ideptmlist).strip(', ')[1:-1]
        ideprotstr = self.reformat_to_str(idetoprotlist).strip(', ')[1:-1]

        cursor.execute( 'SELECT COUNT(*) FROM pepsite_idestimate_ptms' )
        print 'idestimate_ptms', cursor.fetchall()
        ideptmsql = 'WITH f as  \
                (SELECT foo.idestimate_id, goo.id AS ptm_id FROM (VALUES %s ) AS foo(idestimate_id, ptm_description ) \
                INNER JOIN pepsite_ptm AS goo ON ( foo.ptm_description = goo.description ) ) \
                INSERT INTO pepsite_idestimate_ptms ( idestimate_id, ptm_id ) \
                SELECT DISTINCT f.idestimate_id, f.ptm_id \
                FROM f LEFT JOIN pepsite_idestimate_ptms existing \
                ON ( f.idestimate_id = existing.idestimate_id AND f.ptm_id = existing.ptm_id ) \
                WHERE existing.id IS NULL \
                ' % ideptmstr
        cursor.execute( ideptmsql )
        cursor.execute( 'SELECT COUNT(*) FROM pepsite_idestimate_ptms' )
        print 'idestimate_ptms', cursor.fetchall()


        cursor.execute( 'SELECT COUNT(*) FROM pepsite_idestimate_proteins' )
        print 'idetoprot', cursor.fetchall()
        idetoprotsql = 'WITH f as  \
                (SELECT foo.idestimate_id, goo.id AS protein_id FROM (VALUES %s ) AS foo(idestimate_id, \
                prot_id, description  ) \
                INNER JOIN pepsite_protein AS goo ON ( foo.description = goo.description \
                AND foo.prot_id = goo.prot_id ) ) \
                INSERT INTO pepsite_idestimate_proteins ( idestimate_id, protein_id ) \
                SELECT DISTINCT f.idestimate_id, f.protein_id \
                FROM f LEFT JOIN pepsite_idestimate_proteins existing \
                ON ( f.idestimate_id = existing.idestimate_id AND f.protein_id = existing.protein_id ) \
                WHERE existing.id IS NULL \
                ' % ideprotstr
        cursor.execute( idetoprotsql )
        cursor.execute( 'SELECT COUNT(*) FROM pepsite_idestimate_proteins' )
        print 'idetoprot', cursor.fetchall()

    def create_views_rapid(self):
        t0 = time.time()
        cursor = connection.cursor()
        cursor.execute('DROP MATERIALIZED VIEW IF EXISTS mega_unagg CASCADE')
        cursor.execute('DROP MATERIALIZED VIEW IF EXISTS mega_posns CASCADE')
        cursor.execute('DROP MATERIALIZED VIEW IF EXISTS mega_comparisons CASCADE')
        cursor.execute('DROP MATERIALIZED VIEW IF EXISTS clean_comparisons CASCADE')
        cursor.execute('DROP MATERIALIZED VIEW IF EXISTS notclean_comparisons CASCADE')
        sqlcreate1 = 'CREATE MATERIALIZED VIEW mega_unagg AS \
                    SELECT t1.id as idestimate_id, t1.\"isRemoved\", t1.\"isValid\", t1.reason, t1.confidence, t1.delta_mass, ABS(t1.delta_mass) AS absdm, \
                    t2.id as ion_id, t2.charge_state, t2.mz, t2.precursor_mass, t2.retention_time, t2.spectrum, \
                    t3.id as dataset_id, t3.title as dataset_title, t3.confidence_cutoff, \
                    t3a.id as lodgement_id, t3a.title as lodgement_title, t3a.datafilename, t3a.\"isFree", \
                    t4.id AS experiment_id, t4.title AS experiment_title, \
                    t5.id as peptide_id, t5.sequence AS peptide_sequence, \
                    t7.id AS ptm_id, t7.description as ptm_description, t7.\"name\" as \"ptm_name\", \
                    t10.id as protein_id, t10.description AS protein_description, t10.prot_id AS uniprot_code \
                    FROM \
                    pepsite_idestimate t1 \
                    INNER JOIN pepsite_ion t2 \
                    ON (t1.ion_id = t2.id) \
                    INNER JOIN pepsite_dataset t3 \
                    ON (t2.dataset_id = t3.id) \
                    INNER JOIN pepsite_lodgement t3a \
                    ON (t3.lodgement_id = t3a.id ) \
                    INNER JOIN pepsite_experiment t4 \
                    ON (t4.id = t3.experiment_id) \
                    INNER JOIN pepsite_peptide t5 \
                    ON (t5.id = t1.peptide_id ) \
                    INNER JOIN pepsite_idestimate_proteins t9 \
                    ON (t9.idestimate_id = t1.id ) \
                    INNER JOIN pepsite_protein t10 \
                    ON (t10.id = t9.protein_id AND t10.id = t9.protein_id ) \
                    LEFT JOIN pepsite_idestimate_ptms t6 \
                    ON (t1.id = t6.idestimate_id ) \
                    LEFT JOIN pepsite_ptm t7 \
                    ON (t7.id = t6.ptm_id ) \
                    '
        sqlq2 = 'SELECT COUNT(*) \
                    FROM \
                    pepsite_idestimate t1 \
                    INNER JOIN pepsite_ion t2 \
                    ON (t1.ion_id = t2.id) \
                    INNER JOIN pepsite_dataset t3 \
                    ON (t2.dataset_id = t3.id) \
                    INNER JOIN pepsite_lodgement t3a \
                    ON (t3.lodgement_id = t3a.id ) \
                    INNER JOIN pepsite_experiment t4 \
                    ON (t4.id = t3.experiment_id) \
                    INNER JOIN pepsite_peptide t5 \
                    ON (t5.id = t1.peptide_id ) \
                    INNER JOIN pepsite_idestimate_proteins t9 \
                    ON (t9.idestimate_id = t1.id ) \
                    INNER JOIN pepsite_protein t10 \
                    ON (t10.id = t9.protein_id AND t10.id = t9.protein_id ) \
                    LEFT JOIN pepsite_idestimate_ptms t6 \
                    ON (t1.id = t6.idestimate_id ) \
                    LEFT JOIN pepsite_ptm t7 \
                    ON (t7.id = t6.ptm_id ) \
                    '
        morestuff = ' \
                    LEFT JOIN pepsite_peptoprot_positions t11 \
                    ON (t11.peptoprot_id = t9.id) \
                    LEFT JOIN pepsite_position t12 \
                    ON (t12.id = t11.position_id ) \
                    '
        sqlmega_agg2 = 'CREATE MATERIALIZED VIEW mega_posns AS \
                    SELECT foo1.idestimate_id, foo1.\"isRemoved\", foo1.\"isValid\", foo1.reason, foo1.confidence, foo1.delta_mass, ABS(foo1.delta_mass) AS absdm, \
                    foo1.ion_id, foo1.charge_state, foo1.mz, foo1.precursor_mass, foo1.retention_time, foo1.spectrum, \
                    foo1.dataset_id, foo1.dataset_title, foo1.confidence_cutoff, \
                    foo1.lodgement_id, foo1.lodgement_title, foo1.datafilename, foo1.\"isFree", \
                    foo1.experiment_id, foo1.experiment_title, \
                    foo1.peptide_id, foo1.peptide_sequence, \
                    foo1.proteinarray, foo1.ptmarray, foo1.ptmstr, foo1.proteinstr, foo1.uniprotstr , \
                    foo1.ptmidarray, foo1.proteinidarray FROM \
                    ( SELECT t1.idestimate_id, t1.\"isRemoved\", t1.\"isValid\", t1.reason, t1.confidence, t1.delta_mass, \
                    t1.ion_id, t1.charge_state, t1.mz, t1.precursor_mass, t1.retention_time, t1.spectrum, \
                    t1.dataset_id, t1.dataset_title, t1.confidence_cutoff, \
                    t1.lodgement_id, t1.lodgement_title, t1.datafilename, t1.\"isFree", \
                    t1.experiment_id, t1.experiment_title, \
                    t1.peptide_id, t1.peptide_sequence, \
                    array_agg( DISTINCT (t1.protein_id, \'|||\' || t1.protein_description || \'|||\', t1.uniprot_code)::text ORDER BY  (t1.protein_id, \'|||\' || t1.protein_description || \'|||\', t1.uniprot_code)::text  ) AS proteinarray, \
                    array_to_string(array_agg( DISTINCT t1.protein_description order by t1.protein_description),\'; \') AS proteinstr, \
                    array_to_string(array_agg( DISTINCT t1.uniprot_code order by t1.uniprot_code),\'; \') AS uniprotstr, \
                    array_agg( DISTINCT (t1.ptm_id, t1.ptm_description)::text order by (t1.ptm_id, t1.ptm_description)::text ) AS ptmarray, \
                    array_to_string(array_agg( DISTINCT t1.ptm_description order by t1.ptm_description),\'; \') AS ptmstr, \
                    array_agg( DISTINCT t1.ptm_id order by t1.ptm_id) AS ptmidarray, \
                    array_agg( DISTINCT t1.protein_id order by t1.protein_id) AS proteinidarray \
                    FROM mega_unagg t1 \
                    GROUP BY t1.idestimate_id, t1.\"isRemoved\", t1.\"isValid\", t1.reason, t1.confidence, t1.delta_mass, \
                    t1.ion_id, t1.charge_state, t1.mz, t1.precursor_mass, t1.retention_time, t1.spectrum, \
                    t1.dataset_id, t1.dataset_title, t1.confidence_cutoff, \
                    t1.lodgement_id, t1.lodgement_title, t1.datafilename, t1.\"isFree", \
                    t1.experiment_id, t1.experiment_title, \
                    t1.peptide_id, t1.peptide_sequence \
                    ) as foo1 \
                    \
                    '
        sqlcompare = 'CREATE MATERIALIZED VIEW mega_comparisons AS \
                    SELECT t1.*, foo1.allowed_array, foo2.disallowed_array \
                    FROM mega_posns t1 \
                    LEFT JOIN \
                    ( SELECT \
                    t2.peptide_id, \
                    t2.ptmarray, \
                    array_agg( DISTINCT t2.experiment_id ORDER BY t2.experiment_id ) AS allowed_array \
                    FROM \
                    ( select * FROM mega_posns mp WHERE mp.\"isRemoved\" = false AND mp.confidence >= mp.confidence_cutoff ) AS t2 \
                    GROUP BY \
                    t2.peptide_id, \
                    t2.ptmarray \
                    ) \
                    AS foo1 \
                    ON ( t1.peptide_id = foo1.peptide_id AND t1.ptmarray = foo1.ptmarray ) \
                    LEFT JOIN \
                    ( SELECT \
                    t3.peptide_id, \
                    t3.ptmarray, \
                    array_agg( DISTINCT t3.experiment_id ORDER BY t3.experiment_id ) AS disallowed_array \
                    FROM \
                    ( select * FROM mega_posns mp2 WHERE mp2.\"isRemoved\" = true OR mp2.confidence < mp2.confidence_cutoff ) AS t3 \
                    GROUP BY \
                    t3.peptide_id, \
                    t3.ptmarray \
                    ) \
                    AS foo2 \
                    ON ( t1.peptide_id = foo2.peptide_id AND t1.ptmarray = foo2.ptmarray ) \
                    '
        sqlcleancompare = 'CREATE MATERIALIZED VIEW clean_comparisons AS \
                    SELECT DISTINCT ON (peptide_id, ptmarray, experiment_id ) t2.* \
                    FROM \
                    (SELECT t1.peptide_id, t1.ptmarray, \
                    MIN( t1.absdm ) AS minabsdm \
                    FROM mega_comparisons t1 \
                    GROUP BY t1.peptide_id, t1.ptmarray, experiment_id ) as foo1 \
                    LEFT JOIN \
                    mega_comparisons t2 \
                    ON (foo1.peptide_id = t2.peptide_id AND foo1.ptmarray = t2.ptmarray AND foo1.minabsdm = t2.absdm ) \
                    '
        sqlnotcleancompare = 'CREATE MATERIALIZED VIEW notclean_comparisons AS \
                    SELECT * FROM mega_comparisons \
                    EXCEPT SELECT * FROM clean_comparisons \
                    '
        cursor.execute( sqlcreate1 )
        cursor.execute('SELECT COUNT(*) FROM mega_unagg')
        print 'mega_unagg count:', cursor.fetchall()
        cursor.execute( sqlmega_agg2 )
        cursor.execute('SELECT COUNT(*) FROM mega_posns')
        print 'mega_posns count:', cursor.fetchall()
        cursor.execute( sqlcompare )
        cursor.execute('SELECT COUNT(*) FROM mega_comparisons')
        print 'mega_comparisons count:', cursor.fetchall()
        cursor.execute( sqlcleancompare )
        cursor.execute( 'SELECT COUNT(*) FROM clean_comparisons' )
        print 'clean_comparisons', cursor.fetchall(  )
        cursor.execute( sqlnotcleancompare )
        cursor.execute( 'SELECT COUNT(*) FROM notclean_comparisons' )
        print 'notclean_comparisons', cursor.fetchall(  )

        t1 = time.time()
        tt = t1 -t0
        print 'time taken %f seconds' % tt


    def refresh_materialized_views( self ):
        t0 = time.time()
        cursor = connection.cursor()
        #for view in ( 'grand_master', 'master_allowed', 'master_disallowed', 'allcompares', 'master_compare_allowed', 'master_compare_disallowed'  ):
        for view in ( 'mega_unagg', 'mega_posns', 'mega_comparisons', 'clean_comparisons', 'notclean_comparisons' ):
            refreshsql = "REFRESH MATERIALIZED VIEW %s" % (view)
            cursor.execute( refreshsql )
        t1 = time.time()
        tt = t1 - t0
        print 'time taken to refresh materialized views = %f' % (tt)
                
    def drop_materialized_views( self ):
        t0 = time.time()
        cursor = connection.cursor()
        #for view in ( 'grand_master', 'master_allowed', 'master_disallowed', 'allcompares', 'master_compare_allowed', 'master_compare_disallowed'  ):
        for view in ( 'mega_unagg', 'mega_posns', 'mega_comparisons', 'clean_comparisons', 'notclean_comparisons' ):
            refreshsql = "DROP MATERIALIZED VIEW IF EXISTS %s CASCADE" % (view)
            cursor.execute( refreshsql )
        t1 = time.time()
        tt = t1 - t0
        print 'time taken to drop all materialized views = %f' % (tt)


    def upload_simple_multiple( self ):
        """None -> None
        """
        for k in self.uldict.keys():
            local = self.uldict[k]
            pep, _ = Peptide.objects.get_or_create( sequence = local['peptide_sequence'] )
            proteins = []
            ptms = []
            for prt, unp in zip( local['proteins'], local['uniprot_ids'] ):
                pr1, _ = Protein.objects.get_or_create(  prot_id = unp, description = prt, name = prt )
                try:
                    sequence = self.uniprot_data[ unp ]['sequence']
                    pr1.sequence = sequence
                    pr1.save()
                except:
                    pass
                proteins.append( pr1 )
            for ptm_desc in local['ptms']:
                ptm, _ = Ptm.objects.get_or_create( description = ptm_desc, name = ptm_desc )
                ptms.append( ptm )
            dsno = local['dataset']
            lodgement, _ = Lodgement.objects.get_or_create( user = self.user, title = local['ldg_name'], datetime = self.now )

            dataset, _ = Dataset.objects.get_or_create( instrument = self.instrument, lodgement = lodgement, experiment = self.expt,
                    datetime = self.now, title = 'Dataset #%s from %s' % ( dsno, lodgement.title )  )
            ion = self.get_model_object( Ion,  charge_state = local['charge'], precursor_mass = local['precursor_mass'],
                    retention_time = local['retention_time'], mz = local['mz'], experiment = self.expt, dataset = dataset, spectrum = local['spectrum'] )
            ion.save()
            ide = self.get_model_object( IdEstimate, ion = ion, peptide = pep, confidence = local['confidence'], delta_mass = local['delta_mass'] )
            ide.save()
            for ptm in ptms:
                self.add_if_not_already( ptm, ide.ptms )
                #ide.save()
            for protein in proteins:
                p2p = self.get_model_object( PepToProt, peptide = pep, protein = protein )
                p2p.save()


 
class Curate( Uploads ):


    def __init__(self, *args, **kwargs):
        super( Curate, self).__init__( *args, **kwargs )
        self.lodgements = []
        self.lodgement_ids = []


    def setup_curation(self, cleaned_data, fileobj):
        """docstring for preview_ss_simple"""
        #if int(
        #for ldg_id in cleaned_data.getlist( 'ldg'):
        for ldg_id in cleaned_data[ 'ldg' ]:
            ldg_obj = Lodgement.objects.get( id = ldg_id ) 
            self.lodgements.append( ldg_obj )
            self.lodgement_ids.append( ldg_id )
        self.preprocess_ss_simple( fileobj )

    def auto_curation(self):
        for ldg_id in self.lodgement_ids:
            self.curation_simple( ldg_id )

    def curation_simple( self, ldg_id ):
        """None -> None
        """
        ldg_obj = Lodgement.objects.get( id = ldg_id )
        for k in self.uldict.keys():
            local = self.uldict[k]
            pep, _ = Peptide.objects.get_or_create( sequence = local['peptide_sequence'] )
            proteins = []
            ptms = []
            for ptm_desc in local['ptms']:
                ptm, _ = Ptm.objects.get_or_create( description = ptm_desc, name = ptm_desc )
                #ptm.save()
                ptms.append( ptm )
            dsno = local['dataset']
            dstitle = self.entitle_ds(dsno, ldg_obj.datafilename)
            try:
                dataset = Dataset.objects.get( lodgement_id = ldg_obj.id,
                    title = dstitle ) #title = 'Dataset #%s from %s' % ( dsno, ldg_obj.title )  )
                print 'Dataset retrieval: %s, %s, %d' % ( dataset.title, dataset.id )
            except:
                print 'Dataset retrieval failed for lodgement__id = %d and title = %s' % (ldg_obj.id, dstitle)
            try:
                ion = Ion.objects.get( charge_state = local['charge'], precursor_mass = local['precursor_mass'],
                    retention_time = local['retention_time'], mz = local['mz'], dataset = dataset )
                print 'Ion retrieval succeded'
            except:
                print 'Ion retrieval failed'
                #ion.save()
            try:
                td = []
                count = 0
                if not ptms:
                    td = [ {'ptms__isnull' : True}, {'peptide' : pep }, {'ion' : ion } ]
                else:
                    for ptm in ptms:
                        td.append( { 'ptms__id' : ptm.id } )
                    td += [ {'peptide' : pep }, {'ion' : ion } ]
                a = IdEstimate.objects.all().annotate( count = Count('ptms'))
                for dic in td:
                    a = a.filter( **dic )
                try:
                    ide = a.filter(count = len(ptms)).distinct()[0]
                    ide.isRemoved = True
                    ide.save()
                except:
                    pass
            except:
                pass


