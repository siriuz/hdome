from django.test import TestCase
from django.contrib.auth.models import User
from pepsite.models import *
from pepsite.uploaders import Uploads
from pepsite.scripts.imports_rapid import BackgroundImports, bulk_main, bulk_with_extra
import os
import datetime
from django.utils.timezone import utc

CURDIR = os.path.dirname( os.path.abspath( __file__ ) )

MDIC = {'# peptides': '1468',
 '5% FDR': '98.5',
 'Ab binds in these samples (allele)': 'A*03:01,B*07:02,C*07:02',
 'Ab binds in these samples (serological)': 'A3,B7,Cw7',
 'Age of animal': '',
 'Alternative Name': 'SCHU',
 'Cell line name': '9013',
 'Depositor': 'Nadine',
 'Drug/cytokine treatment': '',
 'Elution Ab': 'w6/32 (pan class I)',
 'Experiment description': 'Elution from triplicate cell pellets (1x10^9), each column 10mg w632 on 1ml protein A GE, 5cm rod',
 'Experiment name': 'Time Trial Import4',
 'File name': 'Time_Trial_Import4',
 'H2 class I': '',
 'H2 class II': '',
 'HLA A*B*C*': 'A*03:01,B*07:02,C*07:02',
 'HLA Class I serology': 'A3,B7,Cw7',
 'HLA Class II serology': 'DR15,DR51,DQ6,DP4',
 'HLA DR,DQ,DP': 'DRA1*01:02,DRB1*15:01,DRB5*01:01,DQA1*01:02:01,DQB1*06:02,DPA1*01,DPB1*04:02',
 'How many individual elutions': '4',
 'IMGT/HLA link for parental line': 'http://www.ebi.ac.uk/cgi-bin/ipd/imgt/hla/fetch_cell.cgi?11647',
 'Link to Ab info': 'http://www.atcc.org/Products/All/HB-95.aspx',
 'Mutant (parental)': '',
 'Parental cell line': '',
 'Publication included sequences?': '',
 'Purcell lab publication': '',
 'Species': 'Human',
 'Tissue or cell line': 'Cell line',
 'Tissue/cell type': 'EBV transformed B lymphoblastoid',
 'Transfectant Y/N': '',
 'Transfected alelle (s)': ''}


class ImportSpeedTest(TestCase):

    def setUp(self):
        """docstring for setup"""        
        user1 = User.objects.create( )
        user1.set_password( 'f' )
        user1.username = 'u1'
        user1.save()
        self.user1 = user1
        self.man1 = Manufacturer.objects.create( name = 'MZTech' )
        self.inst1 = Instrument.objects.create( name = 'HiLine-Pro', description = 'MS/MS Spectrometer', manufacturer = self.man1 )
        self.uniprot = ExternalDb.objects.create( db_name = 'UniProt', url_stump = 'http://www.uniprot.org/uniprot/')
        bi1 = BackgroundImports()
        cl = bi1.get_cell_line( MDIC )
        bi1.insert_alleles( MDIC, cl_obj = cl )
        bi1.insert_update_antibodies( MDIC )
        bi1.create_experiment( MDIC, cl )
        #self.filepath = os.path.join( CURDIR, 'scripts/Time_Trial_Import4_PeptideSummary.trial' )
        self.filepath = os.path.join( CURDIR, 'scripts/sample_large_ss.csv' )
        #self.filepath = os.path.join( CURDIR, 'scripts/twentyk_trial.csv' )
        self.BGFILE = os.path.join( CURDIR, '../../background/newdata_with_files_correct.csv' )
        self.bi1 = bi1

    def test_ion_write(self):
        zz = [(3, 2192.08813476563, 45.0244, 731.7033, u'7.1.1.3747.4', 1, 22), (2, 1435.80944824219, 41.9072, 718.912, u'13.1.1.6524.16', 1, 5), (3, 1295.75793457031, 13.6884, 432.9266, u'18.1.1.2089.14', 1, 10), (2, 1158.69287109375, 23.1558, 580.3537, u'2.1.1.2770.31', 1, 12), (2, 1079.44030761719, 41.0175, 540.7274, u'21.1.1.10245.3', 1, 14)]

    def test_user1( self):
        #user1 = User.objects.get( id = 1 )
        self.assertEqual( self.user1.username, 'u1' )

    def old_test_file_process(self):
        """docstring for test_file_process"""
        lodgement_title = 'Auto Lodgement for %s at datetime = %s' % ( MDIC['Experiment name'], datetime.datetime.utcnow().replace(tzinfo=utc).__str__() )
        print 'WORKING ON:', MDIC['Experiment name'] 
        t1 = self.bi1.single_upload_from_ss( self.user1.username, MDIC, lodgement_title, self.filepath )
        print '\n\nUpload of Experiment: %s took %f seconds\n\n' % ( MDIC['Experiment name'].strip(), t1 )
        self.assertEqual( os.path.isfile( self.filepath ), True )

    def dormant_test_bulk_rapid_upload(self):
        ss_master = os.path.join( CURDIR, '../background/all_bulk_02.csv')
        datadir = os.path.join(CURDIR, '../background/all_august')
        bulk_main(self.user1.username, ss_master, datadir)

    def test_bulk_rapid_upload(self):
        ss_master = os.path.join( CURDIR, '../background/test_bulk_small.csv')
        datadir = os.path.join(CURDIR, '../background/all_august')
        bulk_with_extra(self.user1.username, ss_master, datadir)

    def test_single_import(self):
        filepath = os.path.join( CURDIR, 'scripts/small_trial.csv' )
        filepath = os.path.join( CURDIR, 'scripts/Time_Trial_Import4_PeptideSummary.trial4' )
        filepath = os.path.join( CURDIR, 'scripts/small.trial4' )
        filepath = os.path.join( CURDIR, 'scripts/tiny.trial4' )
        if True: # os.path.isfile( filepath ): # and bi1.mdict[en]['File name'][:2] != 'RS':
            print 'FILE FOUND:', filepath
            print 'WORKING ON:', MDIC['Experiment name']
            with open( filepath, 'rb' ) as f:
                cf_cutoff = float( MDIC['5% FDR'] )
                expt_obj = self.bi1.get_model_object( Experiment, title = MDIC['Experiment name'] )
                expt_id = expt_obj.id
                ab_ids = []
                for ab_name in MDIC['Elution Ab'].strip().split(','):
                    ab_ids.append( self.bi1.get_model_object( Antibody, name = ab_name.strip() ).id )
                user_id = self.user1.id

                # ul = Uploads( user = self.user1 )
                inst, _ = Instrument.objects.get_or_create( name = 'HiLine-Pro' )
                metadata = { 'expt1' : expt_id, 'expt2' : None, 'pl1' : [], 'ab1' : ab_ids, 'ldg' : 'dummy lodgement', 'inst' : self.inst1.id, 'filename' : f.name  }
                ul = Uploads( user = self.user1 )
                ul.preview_ss_simple( metadata )
                allfields = ul.preprocess_ss_simple( f )
                ul.add_cutoff_mappings( {'cf_' : cf_cutoff} )
                print 'preparing upload'
                ul.prepare_upload_simple( )
                for b, c in zip(allfields['peptidefields'], sorted(ul.uldict.keys())):
                    ori = ul.uldict[c]['peptide_sequence']
                    #fin = b
                    #print b, ori
                    self.assertEqual( b, ori  )
                print 'uploading'
                ul.upload_megarapid()
                sr_header = ul.singlerows_header
                ion_index = sr_header.index('ion_id')
                ide_index = sr_header.index('idestimate_id')
                peptide_index = sr_header.index('peptide_id')
                ds_index = sr_header.index('dataset_id')
                srhl = len(sr_header)
                i = 0
                #for ion in Ion.objects.all().order_by('id'):
                #    print ion.id, ion.precursor_mass, ion.mz, ion.charge_state, ion.retention_time
                with open('qtest.csv',  'wb') as f:
                    for a, b in zip(ul.singlerows, ul.rawlines):
                        f.write(str(a) + '\n')
                        f.write(b + '\n')

                for b, c, d, f in zip(allfields['peptidefields'], sorted(ul.uldict.keys()), ul.singlerows, ul.rawlines ):
                    i += 1
                    print 'row: %d' % i
                    print 'other row', c
                    print 'inferred row', ul.uldict[c]
                    print 'rawline', f

                    ori = ul.uldict[c]['peptide_sequence']
                    fin = d[1]
                    #fin = b
                    #print b, ori, fin
                    print ul.uldict[c]
                    print d, ion_index, d[ion_index]
                    self.assertEqual( fin, ori  )
                    self.assertEqual( len(d), srhl  )
                    ion = Ion.objects.get(id = d[ion_index])
                    print ion
                    self.assertEqual(int(ul.uldict[c]['charge']), ion.charge_state)
                    self.assertEqual(float(ul.uldict[c]['mz']), ion.mz)
                    self.assertEqual(float(ul.uldict[c]['precursor_mass']), ion.precursor_mass)
                    ide = IdEstimate.objects.get(id = d[ide_index])
                    self.assertEqual(float(ul.uldict[c]['confidence']), ide.confidence)
                    pep = Peptide.objects.get(id = ide.peptide_id)
                    pep2 = Peptide.objects.get(id = d[peptide_index])
                    print ori, fin, pep.sequence, pep2.sequence
                    ds = Dataset.objects.get(id = d[ds_index])
                    print ds.title
                    self.assertEqual(ori, pep.sequence)
                    self.assertEqual(ori, ide.peptide.sequence)


                    print ion

                #self.bi1.upload_ss_single( user_id, f, expt_id, ab_ids, 'dummy lodgement', cf_cutoff = cf_cutoff )
            print 'upload complete'
            #print ul.singlerows



