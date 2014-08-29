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
            self.ldg_details.append( [ ldg_no, ldg_name, fileobj.__str__() ] )
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
        self.lodgement_filename = fileobj.__str__()
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
                ## tuples for bulk sql inserts later
                peptidefields.append( ( uldict[j]['peptide_sequence'], ) )
                proteinfields.append( [ [x[0], x[1]] for x in zip(uldict[j]['uniprot_ids'], uldict[j]['proteins']) ]   )
                datasetfields.append( uldict[j]['dataset'] )
                ionfields.append( ( uldict[j]['charge'], uldict[j]['precursor_mass'], uldict[j]['retention_time'], uldict[j]['mz'], uldict[j]['spectrum'] ) ) 
                idestimatefields.append( ( uldict[j]['confidence'], uldict[j]['delta_mass'] ) )
                ptmfields.append( [ b for b in uldict[j]['ptms'] ] )
                ##
            j += 1
        allstr += '</tbody></table>'
        self.allstr = allstr
        self.uldict = uldict
        self.allfields = { 'peptidefields' : peptidefields, 'proteinfields' : proteinfields, 'datasetfields' : datasetfields, 
                'ionfields' : ionfields, 'idestimatefields' : idestimatefields, 'ptmfields' : ptmfields } 
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
            self.lodgement, _ = Lodgement.objects.get_or_create( user = self.user, title = self.lodgement_title, datetime = self.now, datafilename=self.lodgement_filename )
            if self.publications:
                for pl in self.publications:
                    pbln = Publication.objects.get( id=pl )
                    self.lodgement.publication_set.add( pl )
        for dsno in self.dataset_nos:
            ds, _ = Dataset.objects.get_or_create( instrument = self.instrument, lodgement = self.lodgement, experiment = self.expt,
                    datetime = self.now, title = 'Dataset #%s from %s' % ( dsno, self.lodgement_title ), 
                    confidence_cutoff = self.cutoff_mappings['cf_cutoff'] )
            assign_perm('view_dataset', self.user, ds)
            assign_perm('edit_dataset', self.user, ds)
            for group in self.user.groups.all():
                assign_perm('view_dataset', group, ds)
            if self.public:
                assign_perm('view_dataset', User.objects.get( id = -1 ), ds)


            self.datasets.append( ds )
            

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
                    datetime = self.now, title = 'Dataset #%s from %s' % ( dsno, self.lodgement_title )  )
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

    def upload_rapid(self):
        """docstring for upload_rapid"""
        cursor = connection.cursor()
        cursor.execute( 'SELECT COUNT(*) FROM pepsite_protein' )
        print cursor.fetchall()
        for b in self.allfields['proteinfields']:
            for x in range( len(b) ):
                proteinstr = '(\'%s\', \'%s\')' % ( b[x][1], b[x][0] )
                sqlprot = 'INSERT INTO pepsite_protein (description, name, prot_id)\
                SELECT i.field1 description, i.field1 \"name\", i.field2 prot_id \
                FROM (VALUES %s) AS i(field1, field2) \
                LEFT JOIN pepsite_protein as existing \
                ON (existing.description = i.field1 AND existing.prot_id = i.field2) \
                WHERE existing.id IS NULL \
                ' % ( proteinstr )
                cursor.execute( sqlprot )
        cursor.execute( 'SELECT \"description\", \"prot_id\" FROM pepsite_protein' )
        print cursor.fetchall()

        cursor.execute( 'SELECT COUNT(*) FROM pepsite_protein' )
        print cursor.fetchall()

        cursor.execute( 'SELECT COUNT(*) FROM pepsite_peptide' )
        print cursor.fetchall()
        for b in self.allfields['peptidefields']:
            peptidestr = '(\'%s\')' % b
            sqlpep = 'INSERT INTO pepsite_peptide (\"sequence\") \
            SELECT i.field1 \"sequence\" \
            FROM (VALUES %s) AS i(field1) \
            LEFT JOIN pepsite_peptide as existing \
            ON (existing.\"sequence\" = i.field1) \
            WHERE existing.id IS NULL \
            ' % ( peptidestr )
            cursor.execute( sqlpep )
        cursor.execute( 'SELECT COUNT(*) FROM pepsite_peptide' )
        print cursor.fetchall()
        
        cursor.execute( 'SELECT COUNT(*) FROM pepsite_ptm' )
        print cursor.fetchall()
        for b in self.allfields['ptmfields']:
            if b:
                ptmstr = ''
                for x in b:
                    ptmstr += '(\'%s\'), ' % x
                ptmstr = ptmstr.strip(', ')
                sqlptm = 'INSERT INTO pepsite_ptm (\"description\", \"name\") \
                SELECT i.field1 \"description\", i.field1 \"name\" \
                FROM (VALUES %s) AS i(field1) \
                LEFT JOIN pepsite_ptm as existing \
                ON (existing.\"description\" = i.field1) \
                WHERE existing.id IS NULL \
                ' % ( ptmstr )
                cursor.execute( sqlptm )
        cursor.execute( 'SELECT COUNT(*) FROM pepsite_ptm' )
        print cursor.fetchall()[0]

        cursor.execute( 'SELECT COUNT(*) FROM pepsite_ion' )
        print cursor.fetchall()
        for b, c in zip(self.allfields['ionfields'], self.allfields['datasetfields']):
            title = 'Dataset #%s from %s' % ( c, self.lodgement_title )
            cursor.execute('SELECT id FROM pepsite_dataset WHERE \"title\" = \'%s\'' % title  )
            dsid = cursor.fetchall()[0][0]
            ionstr = '(%s, %s, %s, %s, \'%s\', %s, %s)' % ( b[0], b[1], b[2], b[3], b[4], dsid, self.expt.id )
            sqlion = 'INSERT INTO pepsite_ion (\"charge_state\", \"precursor_mass\", \"retention_time\", \"mz\", \
                    \"spectrum\", \"dataset_id\", \"experiment_id\" ) \
            SELECT i.field1 \"charge_state\", i.field2 \"precursor_mass\", i.field3 \"retention_time\", i.field4 \"mz\", \
            i.field5 \"spectrum\", i.field6 \"dataset_id\", i.field7 \"experiment_id\"  \
            FROM (VALUES %s) AS i(field1, field2, field3, field4, field5, field6, field7) \
            LEFT JOIN pepsite_ion as existing \
            ON (existing.\"charge_state\" = i.field1 AND existing.\"precursor_mass\" = i.field2 AND existing.\"retention_time\" = i.field3 AND \
            existing.\"mz\" = i.field4 AND existing.\"spectrum\" = i.field5 AND existing.\"dataset_id\" = i.field6 \
            AND existing.\"experiment_id\" = i.field7 ) \
            WHERE existing.id IS NULL \
            ' % ( ionstr )
            cursor.execute( sqlion )
        cursor.execute( 'SELECT COUNT(*) FROM pepsite_ion' )
        print cursor.fetchall()

        cursor.execute( 'SELECT COUNT(*) FROM pepsite_idestimate' )
        print cursor.fetchall()
        for b, c, d, f in zip(self.allfields['ionfields'], self.allfields['datasetfields'], self.allfields['peptidefields'], self.allfields['idestimatefields']):
            title = 'Dataset #%s from %s' % ( c, self.lodgement_title )
            cursor.execute('SELECT id FROM pepsite_dataset WHERE \"title\" = \'%s\'' % title  )
            dsid = cursor.fetchall()[0][0]
            ionsql = 'SELECT id FROM pepsite_ion WHERE \
                pepsite_ion.\"charge_state\" = %s AND pepsite_ion.\"precursor_mass\" = %s AND pepsite_ion.\"retention_time\" = %s AND \
                pepsite_ion.\"mz\" = %s AND pepsite_ion.\"spectrum\" = \'%s\' AND pepsite_ion.\"dataset_id\" = %s \
                AND pepsite_ion.\"experiment_id\" = %s \
                ' % ( b[0], b[1], b[2], b[3], b[4], dsid, self.expt.id )
            cursor.execute( ionsql )
            ionid = cursor.fetchall()[0][0]
            cursor.execute( 'SELECT id FROM pepsite_peptide WHERE \"sequence\" = \'%s\'' % ( d ) )
            peptideid = cursor.fetchall()[0][0]
            idestimatestr = '(%s, %s, %s, %s, %s, %s)' % ( f[0], f[1], ionid, peptideid, 'false', 'false' )
            sqlidestimate = 'INSERT INTO pepsite_idestimate (\"confidence\", \"delta_mass\", \"ion_id\", \"peptide_id\", \
            \"isRemoved\", \"isValid\") \
            SELECT i.field1 \"confidence\", i.field2 \"delta_mass\", i.field3 \"ion_id\", i.field4 \"peptide_id\", \
            i.field5 \"isRemoved\", i.field6 \"isValid\" \
            FROM (VALUES %s) AS i(field1, field2, field3, field4, field5, field6) \
            LEFT JOIN pepsite_idestimate as existing \
            ON (existing.\"confidence\" = i.field1 AND existing.\"delta_mass\" = i.field2 AND existing.\"ion_id\" = i.field3 AND \
            existing.\"peptide_id\" = i.field4 )\
            WHERE existing.id IS NULL \
            ' % ( idestimatestr )
            cursor.execute( sqlidestimate )
        cursor.execute( 'SELECT COUNT(*) FROM pepsite_idestimate' )
        print cursor.fetchall()

        cursor.execute( 'SELECT COUNT(*) FROM pepsite_peptoprot' )
        print cursor.fetchall()
        cursor.execute( 'SELECT COUNT(*) FROM pepsite_experiment_proteins' )
        print cursor.fetchall()
        for b, c, d, f, g, h in zip(self.allfields['ionfields'], self.allfields['datasetfields'], self.allfields['peptidefields'], self.allfields['idestimatefields'], self.allfields['ptmfields'], self.allfields['proteinfields'] ):
            title = 'Dataset #%s from %s' % ( c, self.lodgement_title )
            cursor.execute('SELECT id FROM pepsite_dataset WHERE \"title\" = \'%s\'' % title  )
            dsid = cursor.fetchall()[0][0]
            ionsql = 'SELECT id FROM pepsite_ion WHERE \
                pepsite_ion.\"charge_state\" = %s AND pepsite_ion.\"precursor_mass\" = %s AND pepsite_ion.\"retention_time\" = %s AND \
                pepsite_ion.\"mz\" = %s AND pepsite_ion.\"spectrum\" = \'%s\' AND pepsite_ion.\"dataset_id\" = %s \
                AND pepsite_ion.\"experiment_id\" = %s \
                ' % ( b[0], b[1], b[2], b[3], b[4], dsid, self.expt.id )
            cursor.execute( ionsql )
            ionid = cursor.fetchall()[0][0]
            cursor.execute( 'SELECT id FROM pepsite_peptide WHERE \"sequence\" = \'%s\'' % ( d ) )
            peptideid = cursor.fetchall()[0][0]
            #idestimatestr = '(%s, %s, %s, %s)' % ( f[0], f[1], ionid, peptideid )
            sqlidestimate = 'SELECT id FROM pepsite_idestimate \
            WHERE \"confidence\" = %s AND \"delta_mass\" = %s AND \"ion_id\" = %s AND \
            \"peptide_id\" = %s \
            ' % ( f[0], f[1], ionid, peptideid ) #( idestimatestr )
            cursor.execute( sqlidestimate )
            idestimateid = cursor.fetchall()[0][0]
            proteinstr = ''
            for pr in h:
                proteinstr += '(\'%s\', \'%s\'), ' % ( pr[0], pr[1] )
            proteinstr = proteinstr.strip(', ')
            #print proteinstr
            peptoprotsql = 'WITH g(\"prot_id\", \"description\") AS\
                    (SELECT * FROM (VALUES %s) AS foo) \
                    INSERT INTO pepsite_peptoprot ( \"protein_id\", \"peptide_id\" ) \
                    SELECT foo2.id as \"protein_id\", foo2.\"peptide_id\" \
                    FROM (SELECT * FROM pepsite_protein t1 \
                    LEFT JOIN g \
                    ON (t1.\"prot_id\" = g.\"prot_id\" AND\
                    t1.\"description\" = g.\"description\" ) \
                    , ( VALUES(%s) ) AS h(\"peptide_id\") ) AS foo2 \
                    LEFT JOIN pepsite_peptoprot existing \
                    ON ( foo2.id = existing.\"protein_id\" AND foo2.\"peptide_id\" = existing.\"peptide_id\"  ) \
                    WHERE existing.id IS NULL \
                    ' % ( proteinstr, peptideid )
            cursor.execute( peptoprotsql )
            exptprotsql = 'WITH g(\"prot_id\", \"description\") AS\
                    (SELECT * FROM (VALUES %s) AS foo) \
                    INSERT INTO pepsite_experiment_proteins ( \"protein_id\", \"experiment_id\" ) \
                    SELECT foo2.id as \"protein_id\", foo2.\"experiment_id\" \
                    FROM (SELECT * FROM pepsite_protein t1 \
                    LEFT JOIN g \
                    ON (t1.\"prot_id\" = g.\"prot_id\" AND\
                    t1.\"description\" = g.\"description\" ) \
                    , ( VALUES(%s) ) AS h(\"experiment_id\") ) AS foo2 \
                    LEFT JOIN pepsite_experiment_proteins existing \
                    ON ( foo2.id = existing.\"protein_id\" AND foo2.\"experiment_id\" = existing.\"experiment_id\"  ) \
                    WHERE existing.id IS NULL \
                    ' % ( proteinstr, self.expt.id )
            cursor.execute( exptprotsql )
        cursor.execute( 'SELECT COUNT(*) FROM pepsite_peptoprot' )
        print cursor.fetchall()
        cursor.execute( 'SELECT COUNT(*) FROM pepsite_experiment_proteins' )
        print cursor.fetchall()
        
        #        peptidefields.append( ( uldict[j]['peptide_sequence'], ) )
        #        proteinfields.append( [ [x[0], x[1]] for x in zip(uldict[j]['uniprot_ids'], uldict[j]['proteins']) ]   )
        #        datasetfields.append( ( uldict[j]['dataset'], ) )
        #        ionfields.append( ( uldict[j]['charge'], uldict[j]['precursor_mass'], uldict[j]['retention_time'], uldict[j]['mz'], uldict[j]['spectrum'] ) ) 
        #        idestimatefields.append( ( uldict[j]['confidence'], uldict[j]['delta_mass'] ) )
        #        ptmfields.append( [ b for b in uldict[j]['ptms'] ] )

    def refresh_materialized_views( self ):
        t0 = time.time()
        cursor = connection.cursor()
        for view in ( 'grand_master', 'master_allowed', 'master_disallowed', 'allcompares', 'master_compare_allowed', 'master_compare_disallowed'  ):
            refreshsql = "REFRESH MATERIALIZED VIEW %s" % (view)
            cursor.execute( refreshsql )
        t1 = time.time()
        tt = t1 - t0
        print 'time taken to refresh materialized views = %f' % (tt)
                

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


