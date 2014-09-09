from django.test import TestCase
from django.contrib.auth.models import User
from pepsite.models import *
from scripts.imports_rapid import BackgroundImports, bulk_main, bulk_with_extra
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
        ss_master = os.path.join( CURDIR, '../background/test_bulk_02.csv')
        datadir = os.path.join(CURDIR, '../background/all_august')
        bulk_with_extra(self.user1.username, ss_master, datadir)
