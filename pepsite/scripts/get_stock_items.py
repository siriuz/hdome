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
        { 'filepath' : os.path.abspath( os.path.join( CURDIR, '../../background/9013_class1.csv' ) ), 'expt' :'9013 Class I', 'cell_line' : '9013', 'Ab' : 'w6/32 (pan lass I)', 'dataset' : '9013 Class I combined dataset' },
        { 'filepath' : os.path.abspath( os.path.join( CURDIR, '../../background/9013_DP.csv' ) ), 'expt' : '9013 DP', 'cell_line' : '9013', 'Ab' : 'B721 (pan DP)', 'dataset' : '9013 DP combined dataset' },
        { 'filepath' : os.path.abspath( os.path.join( CURDIR, '../../background/9013_DQ.csv' ) ), 'expt' : '9013 DQ', 'cell_line' : '9013', 'Ab' : 'SPV-L3 (pan DQ)', 'dataset' : '9013 DQ combined dataset' },
        { 'filepath' : os.path.abspath( os.path.join( CURDIR, '../../background/9013_DR.csv' ) ), 'expt' : '9013 DR', 'cell_line' : '9013', 'Ab' : 'LB3.1 (pan DR)', 'dataset' : '9013 DR combined dataset' },
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
    def __init__(self, **kwargs):
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
        self.alleles = (
                'HLA A*',
                'HLA B*',
                'HLA C*',
                'HLA DPA1*',
                'HLA DPB1*',
                'HLA DQA1*',
                'HLA DQB1*',
                'HLA DRA1*',
                'HLA DRB1*',
                'HLA DRB3*:',
                'HLA DRB4*',
                'HLA DRB5*',
                )
        self.serotypes = (
                'H2 D',
                'H2 IA',
                'H2 IE',
                'H2 K',
                'H2 L',
                'HLA A',
                'HLA B',
                'HLA C',
                'HLA DP',
                'HLA DQ',
                'HLA DR',
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

    def insert_alleles(self, rowdic, cl_obj = None ):
        """docstring for insert_alleles"""
        keys = rowdic.keys()
        for k in keys:
            if k in self.alleles or k in self.serotypes:
                g1, a1 = k.split()
                gene = self.get_model_object( Gene, name = g1 )
                gene.save()
                if k in self.alleles:
                    allele = self.get_model_object( Allele, code = a1 + rowdic[k], gene = gene, isSer = False )
                    allele.save()
                    expr = self.get_model_object( Expression, allele = allele, cell_line = cl_obj ) #expression assumed 100%
                    expr.save()
                if k in self.serotypes:
                    allele = self.get_model_object( Allele, code = rowdic[k], gene = gene, isSer = True )
                    allele.save()
                    expr = self.get_model_object( Expression, allele = allele, cell_line = cl_obj ) #expression assumed 100%
                    expr.save()

    def insert_update_antibodies(self, rowdic ):
        """docstring for insert_antibodies"""
        ab_name = rowdic['Elution Ab'] #eventually, we could be dealing with plural Abs here
        ab1 = self.get_model_object( Antibody, name = ab_name )
        ab1.save()
        for allele_code in self.unpack_dual_delimited( rowdic['Ab binds in these samples (allele)'] ):
            if allele_code.strip():
                allele = self.get_model_object( Allele, code = allele_code, isSer = False )
                allele.save()
                self.add_if_not_already( allele, ab1.alleles )
                ab1.save()
        for sero_code in self.unpack_dual_delimited( rowdic['Ab binds in these samples(serological)'] ):
            if sero_code.strip():
                sero = self.get_model_object( Allele, code = sero_code, isSer = True )
                sero.save()
                self.add_if_not_already( sero, ab1.alleles )
                ab1.save()

    def create_experiment(self, rowdic, cl ):
        """docstring for create_experiment"""
        ab_name = rowdic['Elution Ab'] #eventually, we could be dealing with plural Abs here
        ab1 = self.get_model_object( Antibody, name = ab_name )
        ab1.save()
        expt = self.get_model_object( Experiment, title = rowdic['Experiment name'], cell_line = cl )
        expt.save()
        self.add_if_not_already( expt, ab1.experiments )



       



        

            


if __name__ == '__main__':
    bi1 = BackgroundImports()
    bi1.create_full_dic( BGFILE )
    #md1 = bi1.read_canonical_spreadsheet( BGFILE )
    for k in sorted( bi1.mdict[3].keys(), key = lambda(a) : a ):
        print '                \'' + k + '\',', bi1.mdict[3][k]
    for en in sorted( bi1.mdict.keys(), key = lambda(a) : int(a) ):
        ind, ent = bi1.get_host( bi1.mdict[en] )
        cl = bi1.get_cell_line( bi1.mdict[en], host_ind = ind )
        bi1.insert_alleles( bi1.mdict[en], cl_obj = cl )
        bi1.insert_update_antibodies( bi1.mdict[en] )
        bi1.create_experiment( bi1.mdict[en], cl )
        print cl.id, cl, ind.id, ind, ent.id, ent, cl.individuals.all(), cl.alleles.all()
    for ab in Antibody.objects.all():
        print ab.id, ab.name, ab.alleles.all()
    for expt in Experiment.objects.all():
        print expt.id, expt.title, expt.cell_line, expt.antibody_set.all()


        
        
