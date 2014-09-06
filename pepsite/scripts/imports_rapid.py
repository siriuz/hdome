import os
import sys
import datetime
from django.utils.timezone import utc
from django.db.models import Q
from django.db.models import *
from django.db import IntegrityError, transaction

PROJ_NAME = 'hdome'
APP_NAME = 'pepsite'

CURDIR = os.path.dirname( os.path.abspath( __file__ ) )

#print CURDIR

sys.path.append( CURDIR + '/../..' ) # gotta hit settings.py for site

os.environ[ 'DJANGO_SETTINGS_MODULE' ] = '%s.settings' %( PROJ_NAME )

import django #required
django.setup() #required

from django.contrib.auth.models import User
from pepsite.models import *
from pepsite import dbtools
import pepsite.uploaders
import time


BGFILE = os.path.join( CURDIR, '../../background/newdata_with_files_correct.csv' )


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
            #description += ' %s %s' %( rowdic['Tissue/cell type'], 'tissue' )
            #title += '%s %s %s' %( rowdic['Species'], rowdic['Tissue/cell type'], 'tissue' )
            tissue_type = rowdic['Tissue/cell type']
        description += ' %s' %( rowdic['Tissue/cell type'] )
        title = rowdic['Cell line name']
        defaults = { 'description' : description, 'isTissue' : isTissue,
                'tissue_type' : tissue_type }
        cl, _ = CellLine.objects.update_or_create( name = title, defaults = defaults )
        if host_ind:
            cl.individuals.add( host_ind )
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

    def insert_alleles(self, rowdic, delimiter = ',', cl_obj = None ):
        """docstring for insert_alleles"""
        keys = rowdic.keys()
        for k in keys:
            codes = rowdic[k].split(delimiter)
            if k.strip().upper() == 'HLA A*B*C*' and bool( rowdic[k].strip() ):
                gene, _ = Gene.objects.get_or_create(  name = 'HLA Class I', gene_class=1, description = 'Human HLA class I'   )
                for code in codes:
                    allele, _ = Allele.objects.update_or_create( code = code.strip(), gene = gene, isSer = False )
                    expr, _ = Expression.objects.get_or_create( allele = allele, cell_line = cl_obj ) #expression assumed 100%
            if k.strip().upper() == 'HLA CLASS I SEROLOGY' and bool( rowdic[k].strip() ):
                gene, _ = Gene.objects.get_or_create(  name = 'HLA Class I', gene_class=1, description = 'Human HLA class I'   )
                for code in codes:
                    allele, _ = Allele.objects.update_or_create( code = code.strip(), gene = gene, isSer = True )
                    expr, _ = Expression.objects.get_or_create( allele = allele, cell_line = cl_obj ) #expression assumed 100%
            elif k.strip().upper() == 'HLA DR,DQ,DP' and bool( rowdic[k].strip() ):
                gene, _ = Gene.objects.get_or_create(  name = 'HLA Class II', gene_class=2, description = 'Human HLA class II'  )
                for code in codes:
                    allele, _ = Allele.objects.update_or_create( code = code.strip(), gene = gene, isSer = False )
                    expr, _ = Expression.objects.get_or_create( allele = allele, cell_line = cl_obj ) #expression assumed 100%
            elif k.strip().upper() == 'HLA CLASS II SEROLOGY' and bool( rowdic[k].strip() ):
                gene, _ = Gene.objects.get_or_create(  name = 'HLA Class II', gene_class=2, description = 'Human HLA cLass II'  )
                for code in codes:
                    allele, _ = Allele.objects.update_or_create( code = code.strip(), gene = gene, isSer = True )
                    expr, _ = Expression.objects.get_or_create( allele = allele, cell_line = cl_obj ) #expression assumed 100%
            elif k.strip().upper() == 'H2 CLASS I' and bool( rowdic[k].strip() ):
                gene, _ = Gene.objects.get_or_create(  name = 'H2 Class I', gene_class=1, description = 'Mouse H2 Class I'  )
                for code in codes:
                    allele, _ = Allele.objects.update_or_create( code = code.strip(), gene = gene, isSer = True )
                    expr, _ = Expression.objects.get_or_create( allele = allele, cell_line = cl_obj ) #expression assumed 100%
            elif k.strip().upper() == 'H2 CLASS II' and bool( rowdic[k].strip() ):
                gene, _ = Gene.objects.get_or_create(  name = 'H2 Class I', gene_class=2, description = 'Mouse H2 Class II'  )
                for code in codes:
                    allele, _ = Allele.objects.update_or_create( code = code.strip(), gene = gene, isSer = True )
                    expr, _ = Expression.objects.get_or_create( allele = allele, cell_line = cl_obj ) #expression assumed 100%
            elif k.strip().upper() == 'H2 D' and bool( rowdic[k].strip() ):
                gene, _ = Gene.objects.get_or_create(  name = 'H2 ', description = 'Mouse H2 D'  )
                for code in codes:
                    allele, _ = Allele.objects.update_or_create( code = code.strip(), gene = gene, isSer = True )
                    expr, _ = Expression.objects.get_or_create( allele = allele, cell_line = cl_obj ) #expression assumed 100%
            elif k.strip().upper() == 'H2 L' and bool( rowdic[k].strip() ):
                gene, _ = Gene.objects.get_or_create(  name = 'H2 L', description = 'Mouse H2 L'  )
                for code in codes:
                    allele, _ = Allele.objects.update_or_create( code = code.strip(), gene = gene, isSer = True )
                    expr, _ = Expression.objects.get_or_create( allele = allele, cell_line = cl_obj ) #expression assumed 100%
            elif k.strip().upper() == 'H2 IA' and bool( rowdic[k].strip() ):
                gene, _ = Gene.objects.get_or_create(  name = 'H2 IA', description = 'Mouse H2 IA'  )
                for code in codes:
                    allele, _ = Allele.objects.update_or_create( code = code.strip(), gene = gene, isSer = True )
                    expr, _ = Expression.objects.get_or_create( allele = allele, cell_line = cl_obj ) #expression assumed 100%
            elif k.strip().upper() == 'H2 IE' and bool( rowdic[k].strip() ):
                gene, _ = Gene.objects.get_or_create(  name = 'H2 IE', description = 'Mouse H2 IE'  )
                for code in codes:
                    allele, _ = Allele.objects.update_or_create( code = code.strip(), gene = gene, isSer = True )
                    expr, _ = Expression.objects.get_or_create( allele = allele, cell_line = cl_obj ) #expression assumed 100%

    def insert_update_antibodies(self, rowdic, delimiter = ',' ):
        """docstring for insert_antibodies"""
        ab_name = rowdic['Elution Ab'] #eventually, we could be dealing with plural Abs here
        url = rowdic['Link to Ab info']
        ab1, _ = Antibody.objects.get_or_create( name = ab_name )
        #print rowdic.keys()
        for allele_code in rowdic['Ab binds in these samples (allele)'].strip().split( delimiter ):
            if allele_code.strip():
                ## HACK ALERT!!!
                try:
                    allele = Allele.objects.get( code = allele_code.strip(), isSer = False )
                    ab1.alleles.add( allele )
                except:
                    pass
        for sero_code in rowdic['Ab binds in these samples (serological)'].strip().split( delimiter ):
            if sero_code.strip():
                ## HACK ALERT!!!
                try:
                    sero = Allele.objects.get( code = sero_code.strip(), isSer = True )
                    ab1.alleles.add( sero )
                except:
                    pass

    def create_experiment(self, rowdic, cl ):
        """docstring for create_experiment"""
        ab_name = rowdic['Elution Ab'] #eventually, we could be dealing with plural Abs here
        ab1, _ = Antibody.objects.get_or_create(  name = ab_name )
        expt, _ = Experiment.objects.update_or_create( title = rowdic['Experiment name'], defaults =
                { 'description' : rowdic['Experiment description'],  'cell_line' : cl } )
        ab1.experiments.add( expt )

    #########################################################################################

    def dummy_boilerplate(self):
        """docstring for dummy_boilerplate"""
        self.user1 = User.objects.get( id = 1 )
        self.man1 = self.get_model_object( Manufacturer, name = 'MZTech' )
        self.man1.save()
        self.inst1 = self.get_model_object( Instrument, name = 'HiLine-Pro', description = 'MS/MS Spectrometer', manufacturer = self.man1 )
        self.inst1.save()
        self.uniprot = self.get_model_object( ExternalDb, db_name = 'UniProt', url_stump = 'http://www.uniprot.org/uniprot/')
        self.uniprot.save()



    def import_ss(self):
        """docstring for import_ss"""
        pass

       
    def process_ss_list( self, ss_list ):
	for ss in ss_list:
	    self.create_all_entries( ss )
 
    def create_all_entries(self, full_options ):
	    dt1 = datetime.datetime.utcnow().replace(tzinfo=utc)
	    #with open( full_options['filepath'], 'rb' ) as f:
	    #    spreadsheet = [b.strip() for b in f ][1:]
	    ab_list, cl_name = full_options['Abs'], full_options['cell_line']
	    cl1 = self.get_model_object( CellLine, name = cl_name)
	    cl1.save()
            lodgement_new = self.get_model_object( Lodgement, title = full_options['lodgement'], isFree = False)
            lodgement_new.datetime = dt1
            lodgement_new.user = self.user1
            lodgement_new.save()
	    expt_new = self.get_model_object( Experiment, title = full_options['expt'], cell_line = cl1 )
	    expt_new.save()
            ds1 = self.get_model_object(Dataset, lodgement = lodgement_new, instrument = self.inst1, datetime = dt1, gradient_duration = 80., gradient_max = 95., gradient_min = 10., title = full_options['dataset'] )
	    for ab in ab_list:
		ab_obj = self.get_model_object( Antibody, name = ab )
		ab_obj.save()
	    	self.add_if_not_already( ab_obj, expt_new.antibody_set )
	        #expt_new.antibody_set.add( ab_obj ) 
	    for i in range(len(spreadsheet)):
	        #print csv_ss + ',' + str(expt_new) + ',' + str( i ) +',',
	        self.process_row( spreadsheet[i], expt_new, ds1 )
	


    def process_row(self, rowstring, expt_obj, dataset_obj, delim = ',' ):
	row = rowstring.strip().split( delim )
	prot1 = self.get_model_object( Protein, description = row[3])#, description = row[3] )
        code1 = self.get_model_object( LookupCode, code = row[2], protein = prot1, externaldb = self.uniprot )
	pep1 = self.get_model_object( Peptide, sequence = row[0], mass = 999.99 ) #, protein = prot1 )
        p2p1 = self.get_model_object(PepToProt, peptide = pep1, protein = prot1)
	ion1 = self.get_model_object(Ion, charge_state = int(row[6]), precursor_mass = row[7], retention_time = 999.99 )
	if row[1]:
	    ptm = self.get_model_object( Ptm, description = row[1], mass_change = -22.2 )
	    id1 = self.get_model_object(IdEstimate, peptide = pep1, ptm = ptm, ion = ion1, delta_mass = float(row[5]), confidence = row[4] )
	    print ',' + ptm.description + ',',
	else:
	    id1 = self.get_model_object(IdEstimate, peptide = pep1, ion = ion1, delta_mass = float(row[5]), confidence = row[4] )
	    id1.save()
	    print ',BLANK,',
	self.add_if_not_already( expt_obj, ion1.experiments )
	self.add_if_not_already( dataset_obj, ion1.dataset_set )
	#id1 = self.get_model_object(IdEstimate, peptide = pep1, ion = ion1, delta_mass = float(row[5]), confidence = row[4] )
	#id1.save()
	print ',' + prot1.name + ',' + pep1.sequence + ',' + str( ion1.charge_state ) + ','



    def upload_ss_single( self, user_id, fileobj, expt_id, ab_ids, lodgement_title, cf_cutoff = 99.0, publication_objs = [], public = False ):
        user = self.get_model_object( User, id = user_id )
        ul = pepsite.uploaders.Uploads( user = user )
        inst, _ = Instrument.objects.get_or_create( name = 'HiLine-Pro' )
        metadata = { 'expt1' : expt_id, 'expt2' : None, 'pl1' : publication_objs, 'ab1' : ab_ids, 'ldg' : lodgement_title, 'inst' : inst.id, 'filename' : fileobj.name  }
        if public:
            metadata['rel'] = True
        ul = pepsite.uploaders.Uploads( user = user )
	ul.preview_ss_simple( metadata )
	ul.preprocess_ss_simple( fileobj )
        ul.add_cutoff_mappings( {'cf_' : cf_cutoff} )
        #ul.get_protein_metadata(  )
        print 'preparing upload'
        ul.prepare_upload_simple( )
        print 'uploading'
        #ul.upload_simple()
        ul.upload_megarapid()

    #@transaction.atomic
    def single_upload_from_ss(self, username, local, lodgement_title, filepath):
        """docstring for single_upload_from_ss"""
        t0 = time.time()
        with open( filepath, 'rb' ) as f:
            cf_cutoff = float( local['5% FDR'] )
            expt_obj = self.get_model_object( Experiment, title = local['Experiment name'] )
            expt_id = expt_obj.id
            ab_ids = []
            for ab_name in local['Elution Ab'].strip().split(','):
                ab_ids.append( self.get_model_object( Antibody, name = ab_name.strip() ).id )
            user_id = self.get_model_object( User, username = username ).id
            print 'done user_id = %d, file = %s, expt_id = %s, ab_ids = %s, lodgement_title = %s, cf_cutoff = %f' % ( user_id, f.name.split('/')[-1], expt_id, ab_ids, lodgement_title, cf_cutoff )
            self.upload_ss_single( user_id, f, expt_id, ab_ids, lodgement_title, cf_cutoff = cf_cutoff )
            t1 = time.time()
            return t1 -t0

            



def bulk_main(username, ss_master, datadir):
    tini = time.time()
    bi1 = BackgroundImports()
    bi1.create_full_dic( ss_master )
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    for en in sorted( bi1.mdict.keys(), key = lambda(a) : int(a) ):
        bi1.dummy_boilerplate()
        cl = bi1.get_cell_line( bi1.mdict[en] )
        bi1.insert_alleles( bi1.mdict[en], cl_obj = cl )
        bi1.insert_update_antibodies( bi1.mdict[en] )
        bi1.create_experiment( bi1.mdict[en], cl )
        #pass
    for en in sorted( bi1.mdict.keys(), key = lambda(a) : int(a) ):
        expt_name = bi1.mdict[en]['Experiment name'].strip() 
        filepath = os.path.join( datadir, bi1.mdict[en]['File name'] )
        if os.path.isfile( filepath ): # and bi1.mdict[en]['File name'][:2] != 'RS':
            print 'FILE FOUND:', filepath
            #cf_cutoff = float( bi1.mdict[en]['5% FDR'] )
            #expt_obj = bi1.get_model_object( Experiment, title = bi1.mdict[en]['Experiment name'] )
            #expt_id = expt_obj.id
            #ab_ids = []
            #for ab_name in bi1.mdict[en]['Elution Ab'].strip().split(','):
            #    ab_ids.append( bi1.get_model_object( Antibody, name = ab_name.strip() ).id )
            #print 'got here'
            #lodgement_title = 'Auto Lodgement for %s at datetime = %s' % ( bi1.mdict[en]['Experiment name'], datetime.datetime.utcnow().replace(tzinfo=utc).__str__() )
            lodgement_title = 'Filename = \"%s\", Datetime = %s, Lodgement for Experiment = \"%s\"' % ( os.path.split(filepath)[-1], now, bi1.mdict[en]['Experiment name']  )
            print 'WORKING ON:', bi1.mdict[en]['Experiment name'] 
            t1 = bi1.single_upload_from_ss( username, bi1.mdict[en], lodgement_title, filepath )
            print '\n\nUpload of Experiment: %s took %f seconds\n\n' % ( bi1.mdict[en]['Experiment name'].strip(), t1 )
        else:
            print 'FILE NOT FOUND FO REAL:', filepath
    tfin = time.time()
    tt = tfin - tini
    print '\n\n\nFull import of db took %f seconds\n\n\n' % tt


def bulk_with_extra(username, ss_master, datadir):
    tini = time.time()
    bi1 = BackgroundImports()
    bi1.create_full_dic( ss_master )
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    for en in sorted( bi1.mdict.keys(), key = lambda(a) : int(a) ):
        bi1.dummy_boilerplate()
        cl = bi1.get_cell_line( bi1.mdict[en] )
        bi1.insert_alleles( bi1.mdict[en], cl_obj = cl )
        bi1.insert_update_antibodies( bi1.mdict[en] )
        bi1.create_experiment( bi1.mdict[en], cl )
        #pass
    for en in sorted( bi1.mdict.keys(), key = lambda(a) : int(a) ):
        expt_name = bi1.mdict[en]['Experiment name'].strip() 
        filepath = os.path.join( datadir, bi1.mdict[en]['File name'] )
        if os.path.isfile( filepath ): # and bi1.mdict[en]['File name'][:2] != 'RS':
            print 'FILE FOUND:', filepath
            #cf_cutoff = float( bi1.mdict[en]['5% FDR'] )
            #expt_obj = bi1.get_model_object( Experiment, title = bi1.mdict[en]['Experiment name'] )
            #expt_id = expt_obj.id
            #ab_ids = []
            #for ab_name in bi1.mdict[en]['Elution Ab'].strip().split(','):
            #    ab_ids.append( bi1.get_model_object( Antibody, name = ab_name.strip() ).id )
            #print 'got here'
            #lodgement_title = 'Auto Lodgement for %s at datetime = %s' % ( bi1.mdict[en]['Experiment name'], datetime.datetime.utcnow().replace(tzinfo=utc).__str__() )
            lodgement_title = 'Filename = \"%s\", Datetime = %s, Lodgement for Experiment = \"%s\"' % ( os.path.split(filepath)[-1], now, bi1.mdict[en]['Experiment name']  )
            print 'WORKING ON:', bi1.mdict[en]['Experiment name'] 
            t1 = bi1.single_upload_from_ss( username, bi1.mdict[en], lodgement_title, filepath )
            print '\n\nUpload of Experiment: %s took %f seconds\n\n' % ( bi1.mdict[en]['Experiment name'].strip(), t1 )
        else:
            print 'FILE NOT FOUND FO REAL:', filepath
    tfin = time.time()
    tt = tfin - tini
    print '\n\n\nFull import of db took %f seconds\n\n\n' % tt
    ul = pepsite.uploaders.Uploads()
    ul.create_views()

def check_files(master_ss, datadir):
    bi1 = BackgroundImports()
    bi1.create_full_dic( master_ss )
    now = datetime.datetime.utcnow().replace(tzinfo=utc)
    exptz = Experiment.objects.annotate(num_ions=Count('ion')).filter(num_ions__gt=0)
    titles = [ b.title for b in exptz ]

    for en in sorted( bi1.mdict.keys(), key = lambda(a) : int(a) ):
        expt_name = bi1.mdict[en]['Experiment name'].strip() 
        filepath = os.path.join( datadir, bi1.mdict[en]['File name'] )
        if os.path.isfile( filepath ):
            pass
            #print 'FILE FOUND:', filepath
        else:
            print '%s\t%s' % ( os.path.split(filepath)[-1], bi1.mdict[en]['Depositor'] ) 

def bulk_import_with_boilerplate( username, master_ss, datadir ):
    Manufacturer.objects.all().delete()
    Instrument.objects.all().delete()
    ExternalDb.objects.all().delete()
    man1, _ = Manufacturer.objects.get_or_create( name = 'MZTech' )
    inst1, _ = Instrument.objects.get_or_create( name = 'HiLine-Pro', description = 'MS/MS Spectrometer', manufacturer = man1 )
    uniprot, _ = ExternalDb.objects.get_or_create( db_name = 'UniProt', url_stump = 'http://www.uniprot.org/uniprot/')
    #bi1 = BackgroundImports()
    #cl = bi1.get_cell_line( MDIC )
    #bi1.insert_alleles( MDIC, cl_obj = cl )
    #bi1.insert_update_antibodies( MDIC )
    #bi1.create_experiment( MDIC, cl )
    bulk_main( username, master_ss, datadir )

if __name__ == '__main__':
    check_files(os.path.join( CURDIR, '../../background/all_bulk_04.csv'), os.path.join(CURDIR, '../../background/all_august') )
    bulk_import_with_boilerplate( 'admin', os.path.join( CURDIR, '../../background/test_bulk_01.csv'), os.path.join(CURDIR, '../../background/all_august') )
    ul = pepsite.uploaders.Uploads()
    ul.create_views()



        
        

