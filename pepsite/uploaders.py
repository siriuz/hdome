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
                'peptide_sequence' : { 'matches' : [ 'Peptide', 'Sequence' ], 'order' : 0, 'display' : 'Peptide Sequence' },
                'proteins' : { 'matches' : [ 'Names', 'protein', 'description' ], 'order' : 1, 'display' : 'Protein(s)' },
                'uniprot_ids' : { 'matches' : [ 'uniprot', 'Accessions' ], 'order' : 2, 'display' : 'UniProt code(s)' },
                'ptms' : { 'matches' : [ 'modification', 'ptm' ], 'order' : 3, 'display' : 'PTM(s)' },
                'confidence' : { 'matches' : [ 'confidence', 'Conf' ], 'order' : 4, 'display' : 'Confidence' },
                'charge' : { 'matches' : [ 'Theor z', 'charge' ], 'order' : 5, 'display' : 'Charge State' },
                'delta_mass' : { 'matches' : [ 'dMass' ], 'order' : 6, 'display' : 'Delta Mass (Da)' },
                'precursor_mass' : { 'matches' : [ 'Prec MW' ], 'order' : 8, 'display' : 'Precursor Mass (Da)' },
                'mz' : { 'matches' : [ 'Prec m/z' ], 'order' : 7, 'display' : 'Precursor m/z' },
                'dataset_id' : { 'matches' : [ 'Spectrum' ], 'order' : 9, 'display' : 'Dataset' },
                'retention_time' : { 'matches' : [ 'Time'], 'order' : 10, 'display' : 'Restention Time (min)' },
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
        #for no in self.dataset_nos:
        #    mdic[no] = {}
        #for k in post_dic.keys():
        #    for no in self.dataset_nos:
        #        if k == dm_prefix + no:
        #            mdic[no]['dm_cutoff'] = post_dic[k]
        #        elif k == cf_prefix + no:
        #            mdic[no]['cf_cutoff'] = post_dic[k]
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

    def preprocess_multiple_simple(self, filelist):
        """docstring for preprocess_multiple_simple"""
        self.uldict = {}
        allstr = '<table id=\"cssTable\" class=\"table table-striped tablesorter\">'
        headers = filelist[0].readline().split( self.delim )
        self.translate_headers( headers )
        self.counter = 0
        allstr += '<thead><tr>'
        for i, k, m in self.indexmap:
           allstr += '<th>' + self.match_dict[m]['display'] + '</th>'
        
        allstr += '<th>Lodgement</th></tr></thead><tbody>'
        self.allstr = allstr
        for i in range(len(filelist)):
            fileobj = filelist[i]
            ldg_name = 'Auto Lodgement #%d from Bulk Lodgement: %s' % ( i + 1, self.lodgement_title )
            ldg_no = i
            self.ldg_details.append( [ ldg_no, ldg_name, fileobj.name ] )
            self.preprocess_ss_from_bulk( fileobj, ldg_name, ldg_no )
        self.allstr += '</tbody></table>'

    def preprocess_ss_from_bulk( self, fileobj, ldg_name, ldg_no ):
        #with open( ss_files
        #allstr = '<table id=\"cssTable\" class=\"table table-striped tablesorter\">'
        #headers = fileobj.readline().split( self.delim )
        #self.translate_headers( headers )
        #allstr += '<thead><tr>'
        #for i, k, m in self.indexmap:
        #   allstr += '<th>' + self.match_dict[m]['display'] + '</th>'
        #allstr += '</tr></thead><tbody>'
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


                        elif m == 'uniprot_ids' and len(elements[k].strip().split('|')) > 1: #not in ( 'Segment', 'RRRRRSegment' ):
                            
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
                        elif m not in ('uniprot_ids'):
                            allstr += '<td>' + elements[k] + '</td>'
                            uldict[j][m] = elements[k]
                        else:
                            allstr += '<td></td>'
                            uldict[j][m] = ['']

                    else:
                        entries = []
                        allstr += '<td>'
                        loclist = [ b.strip() for b in elements[k].split(';') if b.strip() != 'Segment' ]
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
                singlerows.append( [ uldict[j]['peptide_sequence'], uldict[j]['charge'], uldict[j]['precursor_mass'], 
                        uldict[j]['retention_time'], uldict[j]['mz'], uldict[j]['confidence'], uldict[j]['delta_mass'], uldict[j]['spectrum'], uldict[j]['dataset'] ] )
            j += 1
        allstr += '</tbody></table>'
        self.allstr = allstr
        self.uldict = uldict
        self.allfields = { 'peptidefields' : peptidefields, 'proteinfields' : proteinfields, 'datasetfields' : datasetfields, 
                'ionfields' : ionfields, 'idestimatefields' : idestimatefields, 'ptmfields' : ptmfields } 
        self.singlerows = singlerows
        self.dataset_nos = sorted( self.dataset_nos )


    #@transaction.atomic
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
                    datetime = self.now, title = self.entitle_ds(dsno, self.filename), 
                    confidence_cutoff = self.cutoff_mappings['cf_cutoff'] )
            assign_perm('view_dataset', self.user, ds)
            assign_perm('edit_dataset', self.user, ds)
            for group in self.user.groups.all():
                assign_perm('view_dataset', group, ds)
            if self.public:
                assign_perm('view_dataset', User.objects.get( id = -1 ), ds)


            self.datasets.append( ds )
    
    def entitle_ds(self, dsno, filename):
        return 'Dataset #%s from %s' % ( dsno, filename )

    def prepare_upload_simple_multiple(self ):
        for ldg_no, ldg_name, filename in self.ldg_details:
            self.prepare_ind_lodgement( ldg_no, ldg_name, filename )

    def prepare_ind_lodgement(self, ldg_no, ldg_name, filename ):
        """docstring for fname(self, cleaned_data"""
        self.instrument = Instrument.objects.get( id = self.instrument_id )
        self.cell_line = CellLine.objects.get( id = self.cell_line_id )
        if not self.expt_id:
            self.expt, _ = Experiment.objects.get_or_create( cell_line = self.cell_line, title = self.expt_title, description = self.expt_desc )
        else:
            self.expt = Experiment.objects.get( id = self.expt_id )
        assign_perm('view_experiment', self.user, self.expt)
        for ab in self.antibodies:
                self.expt.antibody_set.add( ab )
        lodgement, _ = Lodgement.objects.get_or_create( user = self.user, title = ldg_name, datetime = self.now, datafilename=filename )
        if self.publications:
            for pl in self.publications:
                    pbln = Publication.objects.get( id=pl )
                    lodgement.publication_set.add( pl )
        print 'ldg_ds_mappings here:', self.ldg_ds_mappings
        for dsno in self.ldg_ds_mappings[str(ldg_no)]:
            ds, _ = Dataset.objects.get_or_create( instrument = self.instrument, lodgement = lodgement, experiment = self.expt,
                    datetime = self.now, title = 'Dataset #%s from %s' % ( dsno, ldg_name ), 
                    #dmass_cutoff = self.cutoff_mappings[ldg_no]['dm_cutoff'], 
                    confidence_cutoff = self.cutoff_mappings[ldg_no]['cf_cutoff'] )
            print 'cutoffs here for dataset: %s, in lodgement %s, dm cutoff: %s, cf cutoff: %s' % ( ds.title, lodgement.title, ds.dmass_cutoff, ds.confidence_cutoff ) 
            assign_perm('view_dataset', self.user, ds)
            assign_perm('edit_dataset', self.user, ds)
            for group in self.user.groups.all():
                assign_perm('view_dataset', group, ds)
            if self.public:
                assign_perm('view_dataset', User.objects.get( id = -1 ), ds)


            self.datasets.append( ds )

    def get_protein_metadata( self ):
        self.uniprot_data = uniprot.batch_uniprot_metadata( self.uniprot_ids )
        

    @transaction.atomic
    def old_upload_simple( self ):
        """None -> None
        """
        i = 0
        for k in self.uldict.keys():
            i += 1
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
                    datetime = self.now, title = self.entitle_ds( dsno, self.filename )  )
            dataset.save()
            ## object permissions:
            assign_perm('view_dataset', self.user, dataset)
            assign_perm('view_experiment', self.user, self.expt)
            assign_perm('edit_lodgement', self.user, self.lodgement)
            for group in self.user.groups.all():
                assign_perm('view_dataset', group, dataset)
            if self.public:
                assign_perm('view_dataset', User.objects.get( id = -1 ), dataset)
            
            ##
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
                ex2pr = self.get_model_object( PepToProt, peptide = pep, protein = protein )
                p2p.save()
            #print 'uploaded ion #%d from Experiment: %s, ion: %s' % ( i, self.expt.title, ion.__str__() )

    @transaction.atomic
    def upload_simple( self ):
        """None -> None
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
                pep, _ = Peptide.objects.get_or_create( sequence = local['peptide_sequence'] )
                proteins = []
                ptms = []
                for prt, unp in zip( local['proteins'], local['uniprot_ids'] ):
                    pr1, _ = Protein.objects.get_or_create(  prot_id = unp, description = prt, name = prt )
                    proteins.append( pr1 )
                for ptm_desc in local['ptms']:
                    ptm, _ = Ptm.objects.get_or_create( description = ptm_desc, name = ptm_desc )
                    ptms.append( ptm )
                dsno = local['dataset']
                dataset, _ = Dataset.objects.get_or_create( instrument = self.instrument, lodgement = self.lodgement, experiment = self.expt,
                        datetime = self.now, title = 'Dataset #%s from %s' % ( dsno, self.lodgement_title )  )
                ion, _ = Ion.objects.get_or_create(  charge_state = local['charge'], precursor_mass = local['precursor_mass'],
                        retention_time = local['retention_time'], mz = local['mz'], experiment = self.expt, dataset = dataset, spectrum = local['spectrum'] )
                ide, _ = IdEstimate.objects.get_or_create( ion = ion, peptide = pep, confidence = local['confidence'], delta_mass = local['delta_mass'] )
                for ptm in ptms:
                    ide.ptms.add( ptm )
                for protein in proteins:
                    p2p, _ = PepToProt.objects.get_or_create( peptide = pep, protein = protein )
                    self.expt.proteins.add(protein) 
        t1 = time.time()
        tt = t1-t0
        print 'upload time taken =%f' % (tt) 


    def reformat_to_str(self, iterable ):
        retstr = '('
        for elem in iterable:
            if not elem:
                retstr += 'NULL, '

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
                    retstr += 'E\'%s\', ' % elem.replace('\'', '\\\'')
        retstr = retstr.strip(', ') + ' ), '
        return retstr



    def upload_megarapid(self):
        """docstring for upload_rapid"""


        proteinstr = ''
        for b in self.allfields['proteinfields']:
            for x in range( len(b) ):
                if b[x][0]:
                    proteinstr += '(E\'%s\', E\'%s\'), ' % ( b[x][1].replace('\'', '\\\''), b[x][0].replace('\'', '\\\'') )
                else:
                    proteinstr += '( E\'%s\', NULL ), ' % ( b[x][1].replace('\'', '\\\'') )
        proteinstr = proteinstr.strip(', ')

        peptidestr = ''
        for b in self.allfields['peptidefields']:
            peptidestr += '(\'%s\'), ' % ( b )
        peptidestr = peptidestr.strip(', ')

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
        for d in self.allfields['datasetfields']:
            title = self.entitle_ds( c, self.filename )
            dsstr += '(\'%s\', %d), ' % (title, self.expt.id) 
        dsstr = dsstr.strip(', ')

        cursor = connection.cursor()

        for row in self.singlerows:
            row.append( self.expt.id )

        sqldsfind = 'WITH f AS \
                (SELECT t2.id AS dataset_id FROM \
                (VALUES %s) AS ds(ds_title, expt_id) \
                LEFT JOIN pepsite_dataset t2 \
                ON (ds.ds_title = t2.title AND t2.experiment_id = ds.expt_id ) ) \
                SELECT dataset_id FROM f \
                ' % dsstr
        cursor.execute( sqldsfind )
        newmastercol = cursor.fetchall()
        for row, new in zip( self.singlerows, [b[0] for b in newmastercol ] ) :
            row.append( new )

        cursor.execute( 'SELECT COUNT(*) FROM pepsite_protein' )
        print 'protein', cursor.fetchall()
        #print proteinstr
        sqlprot = 'INSERT INTO pepsite_protein (description, name, prot_id)\
                SELECT DISTINCT i.field1 description, i.field1 \"name\", i.field2 prot_id \
                FROM (VALUES %s) AS i(field1, field2) \
                LEFT JOIN pepsite_protein as existing \
                ON (existing.description = i.field1 AND existing.prot_id = i.field2) \
                WHERE existing.id IS NULL \
                ' % ( proteinstr )
        sqlprot = 'WITH f AS \
                ( SELECT DISTINCT ON (description) i.description, i.description AS \"name\", i.prot_id \
                FROM (VALUES %s) AS i(description, prot_id) \
                ORDER BY description, prot_id ) \
                INSERT INTO pepsite_protein (description, \"name\", prot_id) \
                SELECT f.description, f.\"name\", f.prot_id FROM f \
                LEFT JOIN pepsite_protein as existing \
                ON (existing.description = f.description ) \
                WHERE existing.id IS NULL \
                ' % ( proteinstr )
        cursor.execute( sqlprot )
        cursor.execute( 'SELECT COUNT(*) FROM pepsite_protein' )
        print 'protein', cursor.fetchall()



        cursor.execute( 'SELECT COUNT(*) FROM pepsite_peptide' )
        print 'peptide', cursor.fetchall()
        sqlpep = 'INSERT INTO pepsite_peptide (\"sequence\") \
        SELECT DISTINCT i.field1 \"sequence\" \
            FROM (VALUES %s) AS i(field1) \
            LEFT JOIN pepsite_peptide as existing \
            ON (existing.\"sequence\" = i.field1) \
            WHERE existing.id IS NULL \
            ' % ( peptidestr )
        cursor.execute( sqlpep )
        cursor.execute( 'SELECT COUNT(*) FROM pepsite_peptide' )
        print 'peptide', cursor.fetchall()

        sqlpepsfind = 'WITH f AS \
                (SELECT t2.id AS peptide_id FROM \
                (VALUES %s) AS peps(peptide_sequence) \
                LEFT JOIN pepsite_peptide t2 \
                ON (peps.peptide_sequence = t2.sequence ) ) \
                SELECT peptide_id FROM f \
                ' % peptidestr
        cursor.execute( sqlpepsfind )
        newmastercol = cursor.fetchall()
        #print newmastercol
        for row, new in zip( self.singlerows, [b[0] for b in newmastercol ] ) :
            row.append( new )
        
        cursor.execute( 'SELECT COUNT(*) FROM pepsite_ptm' )
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

        sqlion_new = 'WITH f AS \
            (SELECT foo.* FROM  (VALUES %s ) AS foo(peptide_sequence, charge_state, precursor_mass, \
            retention_time, mz, confidence, delta_mass, spectrum, dataset_title, experiment_id, dataset_id, peptide_id ) ) \
            INSERT INTO pepsite_ion (charge_state, precursor_mass, retention_time, mz, spectrum, dataset_id, experiment_id) \
            SELECT f.charge_state, f.precursor_mass, f.retention_time, f.mz, f.spectrum, f.dataset_id, f.experiment_id \
            FROM f LEFT JOIN pepsite_ion AS existing \
            ON (f.dataset_id = existing.dataset_id AND f.charge_state = existing.charge_state AND f.retention_time = existing.retention_time \
            AND f.mz = existing.mz AND f.spectrum = existing.spectrum AND f.experiment_id = existing.experiment_id) \
            where existing.id IS NULL\
            ' % ( masterstr )
        cursor.execute( sqlion_new )
        cursor.execute( 'SELECT COUNT(*) FROM pepsite_ion' )
        print 'ion', cursor.fetchall()

        sqlionfind = 'WITH f AS \
            (SELECT foo.* FROM  (VALUES %s ) AS foo(peptide_sequence, charge_state, precursor_mass, \
            retention_time, mz, confidence, delta_mass, spectrum, dataset_title, experiment_id, dataset_id, peptide_id ) ) \
            SELECT existing.id \
            FROM f LEFT JOIN pepsite_ion AS existing \
            ON (f.dataset_id = existing.dataset_id AND f.charge_state = existing.charge_state AND f.retention_time = existing.retention_time \
            AND f.mz = existing.mz AND f.spectrum = existing.spectrum AND f.experiment_id = existing.experiment_id) \
            ' % ( masterstr )
        cursor.execute( sqlionfind )
        newmastercol = cursor.fetchall()
        for row, new in zip( self.singlerows, [b[0] for b in newmastercol ] ) :
            row.append( new )

        print self.singlerows[:5]

        cursor.execute( 'SELECT COUNT(*) FROM pepsite_idestimate' )
        print 'idestimate', cursor.fetchall()

        masterstr = self.reformat_to_str(self.singlerows).strip(', ')[1:-1]

        sqlide_new = 'WITH f AS \
                (SELECT * FROM  (VALUES %s ) AS foo(peptide_sequence, charge_state, precursor_mass, \
                retention_time, mz, confidence, delta_mass, spectrum, dataset_title, experiment_id, dataset_id, peptide_id, ion_id ),  \
                (VALUES ( false, false )) AS goo(\"isRemoved\", \"isValid\") ) \
                INSERT INTO pepsite_idestimate (peptide_id, ion_id, delta_mass, confidence, \"isRemoved\", \"isValid\") \
                select f.peptide_id, f.ion_id, f.delta_mass, f.confidence, f.\"isRemoved\", f.\"isValid\" \
                from f \
                LEFT JOIN pepsite_idestimate AS existing \
                ON (f.peptide_id = existing.peptide_id AND f.ion_id = existing.ion_id AND f.confidence = existing.confidence \
                AND f.delta_mass = existing.delta_mass ) \
                where existing.id IS NULL\
                ' % ( masterstr )
        cursor.execute( sqlide_new )
        cursor.execute( 'SELECT COUNT(*) FROM pepsite_idestimate' )
        print 'idestimate', cursor.fetchall()

        sqlidefind = 'WITH f AS \
                (SELECT * FROM  (VALUES %s ) AS foo(peptide_sequence, charge_state, precursor_mass, \
                retention_time, mz, confidence, delta_mass, spectrum, dataset_title, experiment_id, dataset_id, peptide_id, ion_id ) )  \
                SELECT existing.id \
                from f \
                LEFT JOIN pepsite_idestimate AS existing \
                ON (f.peptide_id = existing.peptide_id AND f.ion_id = existing.ion_id AND f.confidence = existing.confidence \
                AND f.delta_mass = existing.delta_mass ) \
                ' % ( masterstr )
        cursor.execute( sqlidefind )
        newmastercol = cursor.fetchall()
        for row, new in zip( self.singlerows, [b[0] for b in newmastercol ] ) :
            row.append( new )

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
                SELECT f.idestimate_id, f.protein_id \
                FROM f LEFT JOIN pepsite_idestimate_proteins existing \
                ON ( f.idestimate_id = existing.idestimate_id AND f.protein_id = existing.protein_id ) \
                WHERE existing.id IS NULL \
                ' % ideprotstr
        cursor.execute( idetoprotsql )
        cursor.execute( 'SELECT COUNT(*) FROM pepsite_idestimate_proteins' )
        print 'idetoprot', cursor.fetchall()

    def junk_old_views(self ):
        """docstring for simple_expt_query"""
        t0 = time.time()
        cursor = connection.cursor()
        cursor.execute( "DROP VIEW IF EXISTS \"allowedides\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"suppavail\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"prot_expt\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"semi_master\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"grand_master\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"master_allowed\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"master_disallowed\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"allowed_comparisons\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"disallowed_comparisons\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"all_compares\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"master_compare_allowed\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"suppcorrect\"" )
        cursor.execute( "DROP VIEW IF EXISTS \"sv2\"" )
    

    def create_views(self ):
        """docstring for simple_expt_query"""
        t0 = time.time()
        cursor = connection.cursor()
        cursor.execute( "DROP VIEW IF EXISTS \"allowedides\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"suppavail\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"prot_expt\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"semi_master\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"grand_master\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"master_allowed\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"master_disallowed\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"allowed_comparisons\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"disallowed_comparisons\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"all_compares\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"master_compare_allowed\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"suppcorrect\"" )
        cursor.execute( "DROP VIEW IF EXISTS \"sv2\"" )
        # Generate SQL for finding idestimate-ptms combo with lowest possible abs(delta_mass) [per experiment] 
        # NOTE: This contins one row per IdEstimate - it can be a starting point for a 'master' view
        qq2 = "CREATE VIEW suppavail AS SELECT foo.id, foo.ptmstr, foo.experiment_id, \
                min(abs(foo.delta_mass)) minadm, foo.ptmarray, foo.ptmidarray, foo.ptmdescarray, foo.ptmdescstr FROM \
                ( select t1.id, t1.peptide_id, t3.experiment_id, \
                t1.delta_mass, array_to_string(array_agg(t2.ptm_id order by t2.ptm_id),'+') AS ptmstr, \
                array_to_string(array_agg(t4.description order by t2.ptm_id),',') AS ptmdescstr, \
                array_agg((t2.ptm_id, t4.description)::text order by t2.ptm_id) AS ptmarray, \
                array_agg(t2.ptm_id order by t2.ptm_id) AS ptmidarray, \
                array_agg(t4.description order by t2.ptm_id) AS ptmdescarray \
                FROM pepsite_idestimate t1 \
                LEFT OUTER JOIN pepsite_idestimate_ptms t2 \
                ON (t2.idestimate_id = t1.id) \
                LEFT OUTER JOIN pepsite_ptm t4 \
                ON ( t2.ptm_id = t4.id ) \
                INNER JOIN pepsite_ion t3 \
                ON ( t1.ion_id = t3.id ) \
                GROUP BY t1.id, t1.peptide_id, t3.experiment_id \
                ) AS foo \
                GROUP BY foo.id, foo.ptmstr, foo.ptmarray, foo.ptmdescarray, foo.ptmdescstr, foo.ptmidarray, foo.experiment_id \
                "
        # Find peptide-ptms combo with lowest possible abs(delta_mass) [per experiment]
        qq3 = "CREATE VIEW suppcorrect AS SELECT DISTINCT \
                foo.peptide_id, foo.ptmstr, foo.experiment_id, min(abs(foo.delta_mass)) as minadm \
                FROM (select t1.id, t1.confidence, t1.peptide_id, t1.delta_mass, \
                t3.experiment_id, \
                array_to_string(array_agg(t2.ptm_id order by t2.ptm_id),'+') AS ptmstr \
                FROM pepsite_idestimate t1 \
                LEFT OUTER JOIN pepsite_idestimate_ptms t2 \
                ON (t2.idestimate_id = t1.id) \
                INNER JOIN pepsite_ion t3 \
                ON (t1.ion_id = t3.id ) \
                GROUP BY t1.id, t3.experiment_id \
                ) AS foo \
                GROUP BY foo.peptide_id, foo.ptmstr, foo.experiment_id"
        # Assign correct protein identifications and peptide positionings on a per experiment basis
        qqprot = "CREATE VIEW prot_expt AS SELECT DISTINCT \
                t1.id as p2p_id, t1.peptide_id, t1.protein_id, array_agg(t2.position_id ORDER BY t2.position_id) as posnarray, \
                array_to_string( array_agg( CAST(t3.initial_res AS text) || '-' || CAST(t3.final_res AS text) ORDER BY t3.initial_res ), ' ') as posnstr, \
                t4.description AS protein_description, t4.prot_id as protein_uniprot_code \
                FROM pepsite_peptoprot t1 \
                LEFT OUTER JOIN pepsite_peptoprot_positions t2 \
                ON ( t1.id = t2.peptoprot_id  ) \
                LEFT OUTER JOIN pepsite_position t3 \
                ON ( t2.position_id = t3.id ) \
                LEFT OUTER JOIN pepsite_protein t4 \
                ON ( t1.protein_id = t4.id ) \
                GROUP BY t1.id, t1.peptide_id, t1.protein_id, t4.description, t4.prot_id \
                "
        # now let us create a master view which contains prepackaged peptide data for display
        qqsemimaster = "CREATE VIEW semi_master AS \
                SELECT t1.*, t2.peptide_id, t2.delta_mass, abs( t2.delta_mass ) as abdm, \
                t2.confidence, t2.\"isRemoved\",  t2.ion_id, \
                t3.title as experiment_title, t4.sequence as peptide_sequence, \
                char_length( t4.sequence ) as peptide_length, \
                t5.charge_state, t5.retention_time, t5.dataset_id, \
                t5.mz, t5.precursor_mass, \
                t6.confidence_cutoff \
                FROM \
                suppavail t1 \
                INNER JOIN pepsite_idestimate t2 \
                ON ( t1.id = t2.id ) \
                INNER JOIN pepsite_experiment t3 \
                ON ( t1.experiment_id = t3.id ) \
                INNER JOIN pepsite_peptide t4 \
                ON ( t2.peptide_id = t4.id ) \
                INNER JOIN pepsite_ion t5 \
                ON ( t5.id = t2.ion_id ) \
                INNER JOIN pepsite_dataset t6 \
                ON ( t6.id = t5.dataset_id ) \
                "
        qqmaster = "CREATE MATERIALIZED VIEW grand_master AS \
                SELECT t1.*, \
                t3.protein_id, t3.posnarray, t3.posnstr, \
                t3.protein_description, t3.protein_uniprot_code \
                FROM semi_master t1 \
                INNER JOIN pepsite_experiment_proteins t2 \
                ON ( t1.experiment_id = t2.experiment_id ) \
                INNER JOIN prot_expt t3 \
                ON ( t3.protein_id = t2.protein_id AND t3.peptide_id = t1.peptide_id ) \
                "
        qqallowed = "CREATE MATERIALIZED VIEW master_allowed AS \
                SELECT DISTINCT ON (t1.peptide_id, t1.ptmstr, t1.experiment_id, t1.protein_id) t1.* \
                FROM grand_master t1 \
                INNER JOIN suppcorrect t2 \
                ON (t1.peptide_id = t2.peptide_id AND t1.ptmstr = t2.ptmstr \
                AND t1.abdm = t2.minadm ) \
                WHERE t1.confidence > t1.confidence_cutoff and t1.\"isRemoved\" = false \
                ORDER BY t1.peptide_id, t1.ptmstr, t1.experiment_id, t1.protein_id, t1.ion_id \
                "
        qqdisallowed = "CREATE MATERIALIZED VIEW master_disallowed AS \
                SELECT t1.* \
                FROM grand_master t1 \
                WHERE t1.confidence < t1.confidence_cutoff AND t1.\"isRemoved\" = false \
                "
        qqallowcompare = "CREATE VIEW allowed_comparisons AS \
                SELECT t1.peptide_id, t1.ptmstr, array_agg( DISTINCT t1.experiment_id ORDER BY t1.experiment_id ) AS allowed_array  \
                FROM master_allowed t1 \
                GROUP BY t1.peptide_id, t1.ptmstr \
                "
        qqdisallowcompare = "CREATE VIEW disallowed_comparisons AS \
                SELECT t1.peptide_id, t1.ptmstr, array_agg( DISTINCT t1.experiment_id ORDER BY t1.experiment_id ) AS disallowed_array \
                FROM master_disallowed t1 \
                GROUP BY t1.peptide_id, t1.ptmstr \
                "
        qqallcompares = "CREATE MATERIALIZED VIEW allcompares AS \
                SELECT t1.*, t2.allowed_array, t3.disallowed_array \
                FROM grand_master t1 \
                LEFT OUTER JOIN allowed_comparisons t2 \
                ON ( t1.peptide_id = t2.peptide_id AND t1.ptmstr = t2.ptmstr ) \
                LEFT OUTER JOIN disallowed_comparisons t3 \
                ON ( t1.peptide_id = t3.peptide_id AND t1.ptmstr = t3.ptmstr ) \
                "
        qqcompallowed = "CREATE MATERIALIZED VIEW master_compare_allowed AS \
                SELECT DISTINCT ON (t1.peptide_id, t1.ptmstr, t1.experiment_id, t1.protein_id) t1.* \
                FROM allcompares t1 \
                INNER JOIN suppcorrect t2 \
                ON (t1.peptide_id = t2.peptide_id AND t1.ptmstr = t2.ptmstr \
                AND t1.abdm = t2.minadm ) \
                WHERE t1.confidence > t1.confidence_cutoff and t1.\"isRemoved\" = false \
                ORDER BY t1.peptide_id, t1.ptmstr, t1.experiment_id, t1.protein_id, t1.ion_id \
                "
        qqcompdisallowed = "CREATE MATERIALIZED VIEW master_compare_disallowed AS \
                SELECT * \
                FROM allcompares t1 \
                EXCEPT \
                SELECT * \
                FROM master_compare_allowed t2 \
                "
        cursor.execute( qq2 )
        cursor.execute( 'SELECT COUNT(*) FROM suppavail' )
        print 'suppavail', cursor.fetchall(  )
        cursor.execute( qq3 )
        cursor.execute( 'SELECT COUNT(*) FROM suppcorrect' )
        print 'suppcorrect', cursor.fetchall(  )
        cursor.execute( qqprot )
        cursor.execute( 'SELECT COUNT(*) FROM prot_expt' )
        print 'prot_expt', cursor.fetchall(  )
        cursor.execute( qqsemimaster )
        cursor.execute( 'SELECT COUNT(*) FROM semi_master' )
        print 'semi_master', cursor.fetchall(  )
        cursor.execute( qqmaster )
        cursor.execute( 'SELECT COUNT(*) FROM grand_master' )
        print 'grand_master', cursor.fetchall(  )
        cursor.execute( qqallowed )
        cursor.execute( 'SELECT COUNT(*) FROM master_allowed' )
        print 'master_allowed', cursor.fetchall(  )
        cursor.execute( qqdisallowed )
        cursor.execute( 'SELECT COUNT(*) FROM master_disallowed' )
        print 'master_disallowed', cursor.fetchall(  )
        cursor.execute( qqallowcompare )
        cursor.execute( 'SELECT COUNT(*) FROM allowed_comparisons' )
        print 'allowed_comparisons', cursor.fetchall(  )
        cursor.execute( qqdisallowcompare )
        cursor.execute( 'SELECT COUNT(*) FROM disallowed_comparisons' )
        print 'disallowed_comparisons', cursor.fetchall(  )
        cursor.execute( qqallcompares )
        cursor.execute( 'SELECT COUNT(*) FROM allcompares' )
        print 'allcompares', cursor.fetchall(  )
        cursor.execute( qqcompallowed )
        cursor.execute( 'SELECT COUNT(*) FROM master_compare_allowed' )
        print 'master_compare_allowed', cursor.fetchall(  )
        cursor.execute( qqcompdisallowed )
        cursor.execute( 'SELECT COUNT(*) FROM master_compare_disallowed' )
        print 'master_compare_disallowed', cursor.fetchall(  )
        cursor.close()
        t1 = time.time()
        tt = t1 - t0
        print '\n\nview update time taken = %f seconds\n\n' % tt


    def create_views_rapid(self ):
        """docstring for simple_expt_query"""
        t0 = time.time()
        cursor = connection.cursor()
        #cursor.execute( "DROP MATERIALIZED VIEW IF EXISTS \"mega_unagg\" CASCADE" )
        cursor.execute( "DROP MATERIALIZED VIEW IF EXISTS \"mega_unagg\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"mega_posns\" CASCADE" )
        cursor.execute( "DROP MATERIALIZED VIEW IF EXISTS \"mega_comparisons\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"mega_comparisons\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"clean_comparisons\" CASCADE" )
        cursor.execute( "DROP VIEW IF EXISTS \"notclean_comparisons\" CASCADE" )
        # Generate SQL for finding idestimate-ptms combo with lowest possible abs(delta_mass) [per experiment] 
        # NOTE: This contins one row per IdEstimate - it can be a starting point for a 'master' view
        sqlmega_unagg = 'CREATE MATERIALIZED VIEW mega_unagg AS \
                SELECT t1.id as idestimate_id, t1.\"isRemoved\", t1.\"isValid\", t1.reason, t1.confidence, t1.delta_mass, ABS(t1.delta_mass) AS absdm, \
                t2.id as ion_id, t2.charge_state, t2.mz, t2.precursor_mass, t2.retention_time, t2.spectrum, \
                t3.id as dataset_id, t3.title as dataset_title, t3.confidence_cutoff, \
                t3a.id as lodgement_id, t3a.title as lodgement_title, t3a.datafilename, t3a.\"isFree", \
                t4.id AS experiment_id, t4.title AS experiment_title, \
                t5.id as peptide_id, t5.sequence AS peptide_sequence, \
                t7.id AS ptm_id, t7.description as ptm_description, t7.\"name\" as \"ptm_name\", \
                t10.id as protein_id, t10.description AS protein_description, t10.prot_id AS uniprot_code, \
                t12.initial_res, t12.final_res \
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
                INNER JOIN pepsite_idestimate_ptms t6 \
                ON (t1.id = t6.idestimate_id ) \
                LEFT JOIN pepsite_ptm t7 \
                ON (t7.id = t6.ptm_id ) \
                INNER JOIN pepsite_experiment_proteins t8 \
                ON (t8.experiment_id = t4.id ) \
                INNER JOIN pepsite_peptoprot t9 \
                ON (t9.peptide_id = t5.id ) \
                INNER JOIN pepsite_protein t10 \
                ON (t10.id = t9.protein_id AND t10.id = t8.protein_id ) \
                LEFT JOIN pepsite_peptoprot_positions t11 \
                ON (t11.peptoprot_id = t9.id) \
                LEFT JOIN pepsite_position t12 \
                ON (t12.id = t11.position_id ) \
                '
        cursor.execute( sqlmega_unagg )
        #cursor.execute( 'SELECT COUNT(t1.idestimate_id) FROM mega_unagg t1' )
        #print 'mega_unagg', cursor.fetchall(  )
        print 'mega_unagg done' #, cursor.fetchall(  )
        sqlmega_agg2 = 'CREATE VIEW mega_posns AS \
                SELECT DISTINCT t2.*, foo1.proteinarray, foo1.ptmarray, foo1.ptmstr, foo1.proteinstr, foo1.uniprotstr FROM \
                ( SELECT idestimate_id, \
                array_agg( DISTINCT (t1.protein_id, \'|||\' || t1.protein_description || \'|||\', t1.uniprot_code)::text ORDER BY  (t1.protein_id, \'|||\' || t1.protein_description || \'|||\', t1.uniprot_code)::text  ) AS proteinarray, \
                array_to_string(array_agg(t1.protein_description order by t1.protein_description),\'; \') AS proteinstr, \
                array_to_string(array_agg(t1.uniprot_code order by t1.protein_description),\'; \') AS uniprotstr, \
                array_agg( DISTINCT (t1.ptm_id, t1.ptm_description)::text order by (t1.ptm_id, t1.ptm_description)::text ) AS ptmarray, \
                array_to_string(array_agg(t1.ptm_description order by t1.ptm_description),\'; \') AS ptmstr \
                FROM mega_unagg t1 \
                GROUP BY idestimate_id ) as foo1 \
                LEFT JOIN mega_unagg t2 \
                ON ( t2.idestimate_id = foo1.idestimate_id ) \
                ORDER BY t2.ptm_id \
                '
        cursor.execute( sqlmega_agg2 )
        #cursor.execute( 'SELECT COUNT(*) FROM mega_posns t1' )
        #print 'mega_posns', cursor.fetchall(  )
        print 'mega_posns done' #, cursor.fetchall(  )
        sqlcompare = 'CREATE VIEW mega_comparisons AS \
                SELECT t1.*, foo1.allowed_array, foo2.disallowed_array \
                FROM mega_posns t1 \
                LEFT JOIN \
                ( SELECT \
                t2.peptide_id, \
                t2.ptmarray, \
                array_agg( DISTINCT t2.experiment_id ORDER BY t2.experiment_id ) AS allowed_array \
                FROM \
                ( select * FROM mega_posns mp WHERE mp.\"isRemoved\" = false AND mp.confidence > mp.confidence_cutoff ) AS t2 \
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
                ( select * FROM mega_posns mp2 WHERE mp2.\"isRemoved\" = true OR mp2.confidence <= mp2.confidence_cutoff ) AS t3 \
                GROUP BY \
                t3.peptide_id, \
                t3.ptmarray \
                ) \
                AS foo2 \
                ON ( t1.peptide_id = foo2.peptide_id AND t1.ptmarray = foo2.ptmarray ) \
                '
        cursor.execute( sqlcompare )
        #cursor.execute( 'SELECT COUNT(*) FROM mega_comparisons' )
        #print 'mega_comparisons', cursor.fetchall(  )
        print 'mega_comparisons done ' # cursor.fetchall(  )
        sqlcleancompare = 'CREATE VIEW clean_comparisons AS \
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
        cursor.execute( sqlcleancompare )
        #cursor.execute( 'SELECT COUNT(*) FROM clean_comparisons' )
        #print 'clean_comparisons', cursor.fetchall(  )
        print 'clean_comparisons done' #, cursor.fetchall(  )
        sqlnotcleancompare = 'CREATE VIEW notclean_comparisons AS \
                SELECT * FROM mega_comparisons \
                EXCEPT SELECT * FROM clean_comparisons \
                '
        cursor.execute( sqlnotcleancompare )
        #cursor.execute( 'SELECT COUNT(*) FROM notclean_comparisons' )
        #print 'notclean_comparisons', cursor.fetchall(  )
        print 'notclean_comparisons done' #, cursor.fetchall(  )
        cursor.close()
        t1 = time.time()
        tt = t1 - t0
        print '\n\nview update time taken = %f seconds\n\n' % tt


    def refresh_materialized_views( self ):
        t0 = time.time()
        cursor = connection.cursor()
        for view in ( 'grand_master', 'master_allowed', 'master_disallowed', 'allcompares', 'master_compare_allowed', 'master_compare_disallowed'  ):
            refreshsql = "REFRESH MATERIALIZED VIEW %s" % (view)
            cursor.execute( refreshsql )
        t1 = time.time()
        tt = t1 - t0
        print 'time taken to refresh materialized views = %f' % (tt)
                
    def drop_materialized_views( self ):
        t0 = time.time()
        cursor = connection.cursor()
        for view in ( 'grand_master', 'master_allowed', 'master_disallowed', 'allcompares', 'master_compare_allowed', 'master_compare_disallowed'  ):
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
            #pep.save()
            proteins = []
            ptms = []
            #for prt, unp in zip( local['proteins'], local['uniprot_ids'] ):
            #    pr1 = self.get_model_object( Protein,  prot_id = unp, description = prt, name = prt )
            #    try:
            #        sequence = self.uniprot_data[ unp ]['sequence']
            #        pr1.sequence = sequence
            #        pr1.save()
            #    except:
            #        pr1.save()
            #    proteins.append( pr1 )
            for ptm_desc in local['ptms']:
                ptm, _ = Ptm.objects.get_or_create( description = ptm_desc, name = ptm_desc )
                #ptm.save()
                ptms.append( ptm )
            dsno = local['dataset']
            if True:
                dataset, _ = Dataset.objects.get_or_create( lodgement = ldg_obj,
                    title = 'Dataset #%s from %s' % ( dsno, ldg_obj.title )  )
                ion, _ = Ion.objects.get_or_create( charge_state = local['charge'], precursor_mass = local['precursor_mass'],
                    retention_time = local['retention_time'], dataset = dataset )
                #ion.save()
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
            else:
                pass


