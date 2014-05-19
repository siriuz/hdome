import os
import sys
import datetime
from django.utils.timezone import utc
from django.db.models import Q
from db_ops import dbtools

PROJ_NAME = 'hdome'
APP_NAME = 'pepsite'

CURDIR = os.path.dirname( os.path.abspath( __file__ ) )

#print CURDIR

sys.path.append( CURDIR + '/../..' ) # gotta hit settings.py for site

SS = os.path.abspath( os.path.join( CURDIR, '../../background/eg_sheet_01.csv' ) )

#print SS

SF = ( 
			( ( 'HLA', 1 ), ( ( 'A*01:01:01:01', 'A1' ), ('B*08:01:01', 'B8'), ('C*08:01:01', 'Cw7'), ), 
			('pan', 'anti-HLA class-1 non-selective'), ("unknown SA male", 'caucasoid|male|consanguineous|homozygous', 'South Africa' ),
			(('human', 'homo sapiens', True),), ( '9022', 'adapted from human tissue', 'unknown' ) ),
	)


SELECTIVITIES = ( 
			( (( 'HLA', 1 ), ('HLA', 2),), ( ( 'A*01:01:01:01', False), ('A1', True ), ('B*08:01:01', False), ('B8', True), ('C*08:01:01', False), ('Cw7', True), ), 
			('pan', 'anti-HLA class-1 non-selective') ), 
			( ( 'HLA', 2 ), ( ( 'A*01:01:01:01', 'A1' ), ('B*08:01:01', 'B8'), ('C*08:01:01', 'Cw7'), ), 
			('pan', 'anti-HLA class-1 non-selective') ), 
	)

GENES =  (( 'HLA A', 1 ), ('HLA B', 1), ('HLA C', 1), ('HLA E', 1), ('HLA F', 1), ('HLA G', 1), ('HLA DR', 2), ('HLA DQ', 2), ('HLA DP', 2),)

#ALLS = ( ( 'A*01:01:01:01', False), ('A1', True ), ('B*08:01:01', False), ('B8', True), ('C*08:01:01', False), ('Cw7', True), )

ANBS= 	( ('pan', 'anti-HLA class-1 non-selective', ['HLA A', 'HLA B', 'HLA C'],), ('anti-DR', 'anti-HLA DR selective', ['HLA DR'],), ('anti-DQ', 'anti-HLA DQ selective', ['HLA DQ'],),  ('anti-DP', 'anti-HLA DP selective', ['HLA DP'],),  ) 

ENTITIES = ( ( 'human', 'homo sapiens', 'Unhairy ape', True), )

CELL_LINES = ( ( '9022', 'EBV transformed B lymphoblastoid cell line', '9022 anonymous donor', True), 
               ( '9013', 'EBV transformed B lymphoblastoid cell line', '9013 anonymous donor', True),
               ( '9031', 'EBV transformed B lymphoblastoid cell line', '9031 anonymous donor', True),
               ( '9087', 'EBV transformed B lymphoblastoid cell line', '9087 anonymous donor', True),

		)


INDIVIDUALS = (
		( '9022 anonymous donor', True, True, 'male|caucasoid|homozygous|consanguineous', 'South Africa', 'http://www.ebi.ac.uk/cgi-bin/ipd/imgt/hla/fetch_cell.cgi?10429', 'human' ),
		( '9013 anonymous donor', True, True, 'male|caucasoid|non-consanguinueous', 'France', 'http://www.ebi.ac.uk/cgi-bin/ipd/imgt/hla/fetch_cell.cgi?11647', 'human' ),
		( '9031 anonymous donor', True, True, 'male|caucasoid|consanguineous', 'Sweden', 'http://www.ebi.ac.uk/cgi-bin/ipd/imgt/hla/fetch_cell.cgi?10329', 'human' ),
		( '9087 anonymous donor', True, True, 'female|caucasoid|non-consanguineous', 'France', 'http://www.ebi.ac.uk/cgi-bin/ipd/imgt/hla/fetch_cell.cgi?11648', 'human' ),
		)

SHEET_LIST = ( 
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9022_class1.csv' ) ), ['pan'], '9022', 'Trial Expt 9022 pan', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9022_DP.csv' ) ), ['anti-DP'], '9022', 'Trial Expt 9022 DP', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9022_DQ.csv' ) ), ['anti-DQ'], '9022', 'Trial Expt 9022 DQ', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9022_DR.csv' ) ), ['anti-DR'], '9022', 'Trial Expt 9022 DR', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9013_class1.csv' ) ), ['pan'], '9013', 'Trial Expt 9013 pan', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9013_DP.csv' ) ), ['anti-DP'], '9013', 'Trial Expt 9013 DP', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9013_DQ.csv' ) ), ['anti-DQ'], '9013', 'Trial Expt 9013 DQ', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9013_DR.csv' ) ), ['anti-DR'], '9013', 'Trial Expt 9013 DR', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9031_class1.csv' ) ), ['pan'], '9031', 'Trial Expt 9031 pan', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9031_DP.csv' ) ), ['anti-DP'], '9031', 'Trial Expt 9031 DP', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9031_DQ.csv' ) ), ['anti-DQ'], '9031', 'Trial Expt 9031 DQ', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9031_DR.csv' ) ), ['anti-DR'], '9031', 'Trial Expt 9031 DR', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9087_class1.csv' ) ), ['pan'], '9087', 'Trial Expt 9087 pan', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9087_DP.csv' ) ), ['anti-DP'], '9087', 'Trial Expt 9087 DP', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9087_DQ.csv' ) ), ['anti-DQ'], '9087', 'Trial Expt 9087 DQ', ),
		 ( os.path.abspath( os.path.join( CURDIR, '../../background/9087_DR.csv' ) ), ['anti-DR'], '9087', 'Trial Expt 9087 DR', ),
		 )
#print SF[0][:]

os.environ[ 'DJANGO_SETTINGS_MODULE' ] = '%s.settings' %( PROJ_NAME )

import django #required
django.setup() #required

from django.contrib.auth.models import User
from pepsite.models import *


#Allele.objects.all().delete()
#Gene.objects.all().delete()
#Antibody.objects.all().delete()
#Protein.objects.all().delete()
#Peptide.objects.all().delete()
#Ion.objects.all().delete()
#Organism.objects.all().delete()
#Individual.objects.all().delete()
#CellLine.objects.all().delete()
#IdEstimate.objects.all().delete()



#from pfm          import settings          #your project settings file
#from django.core.management  import setup_environ     #environment setup function

#setup_environ(settings)

#print Allele.objects.all(), Antibody.objects.all()


ROW = 'VADVVKDAY,,sp|Q15120|PDK3_HUMAN,[Pyruvate dehydrogenase [lipoamide]] kinase isozyme 3; mitochondrial ,99,0.0064,2,978.5087'


BGFILE = os.path.join( CURDIR, '../../background/reformatted_elution__experiment_info_02.csv' )


class BackgroundImports(dbtools.DBTools):
    """docstring for BackgroundImports"""
    def create_canonical_attr(self, **kwargs):
        """docstring for read_canonical_spreadsheet"""
        self.standards = (
                'ATCC code for parental line',
                'ATCC link for parental line',
                'Ab binds in these samples (allele)',
                'Ab binds in these samples(serological)',
                'Age of animal',
                'Alternative Name',
                'Depositor',
                'Drug/cytokine treatment',
                'Elution Ab',
                'Experiment name',
                'H2 D',
                'H2 IA',
                'H2 IE',
                'H2 K',
                'H2 L',
                'HLA A',
                'HLA A*',
                'HLA B',
                'HLA B*',
                'HLA C',
                'HLA C*',
                'HLA DP',
                'HLA DPA1*',
                'HLA DPB1*',
                'HLA DQ',
                'HLA DQA1*',
                'HLA DQB1*',
                'HLA DR',
                'HLA DRA1*',
                'HLA DRB1*',
                'HLA DRB3*:',
                'HLA DRB4*',
                'HLA DRB5*',
                'How many individual elutions',
                'IMGT/HLA code for parental line',
                'IMGT/HLA link for parental line',
                'Link to Ab info',
                'Mutant (parental)',
                'Parental cell line',
                'Publication included sequences?',
                'Pubmed code for reference on parental line',
                'Purcell lab publication',
                'Purcell lab publication pubmed code',
                'Species',
                'Tissue or cell line',
                'Tissue/cell type',
                'Transfectant Y/N',
                'Transfected alelle(s)',
                )

    def create_full_dic(self, filepath ):
        """docstring for read_spreadsheet"""
        self.mdict = self.read_canonical_spreadsheet( filepath )

    def get_cell_line(self, rowdic, host_ind = None ):
        """docstring for get_cell_line"""
        #title = ''
        isTissue = False
        tissue_type = ''
        #if rowdic['Parental cell line'].strip():
        #    title = rowdic['Parental cell line']
        #    if rowdic['Mutant (parental)'].lower() == 'y':
        #        title += ' mutant'
        description = rowdic['Species']
        if rowdic['Tissue or cell line'].lower() == 'tissue':
            isTissue = True
            description += ' %s %s' %( rowdic['Tissue/cell type'], 'tissue' )
            #title += '%s %s %s' %( rowdic['Species'], rowdic['Tissue/cell type'], 'tissue' )
            tissue_type = rowdic['Tissue/cell type']
        else:
            description += ' %s' %( rowdic['Tissue/cell type'] )
        title = rowdic['Unique Identifier for Cell Line / Tissue']
        cl = self.get_model_object( CellLine, name = title )
        cl.description = description
        cl.isTissue = isTissue
        cl.tissue_type = tissue_type
        cl.save()
        if host_ind:
            self.add_if_not_already( host_ind, cl.individuals )
        cl.save()
        return cl

    def get_host(self, rowdic ):
        """docstring for get_entity"""
        entity = self.get_model_object( Entity, common_name = rowdic['Species'] )
        entity.isOrganism = True
        entity.save()
        ind = self.get_model_object( Individual, identifier = rowdic['Unique Identifier for Host'], entity = entity  )
        ind.isHost = True
        if ind.identifier.strip() != '':
            ind.isAnonymous = False
        ind.save()
        return (ind, entity)

            


if __name__ == '__main__':
    bi1 = BackgroundImports()
    bi1.create_full_dic( BGFILE )
    #md1 = bi1.read_canonical_spreadsheet( BGFILE )
    for k in sorted( bi1.mdict[3].keys(), key = lambda(a) : a ):
        print '                \'' + k + '\',', bi1.mdict[3][k]
    for en in sorted( bi1.mdict.keys(), key = lambda(a) : int(a) ):
        ind, ent = bi1.get_host( bi1.mdict[en] )
        cl = bi1.get_cell_line( bi1.mdict[en], host_ind = ind )
        print cl.id, cl, ind.id, ind, ent.id, ent, cl.individuals.all()


        
        

