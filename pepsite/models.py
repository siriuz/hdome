from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils.timezone import utc
import re
import os
from django.utils.encoding import force_unicode

NOW = models.DateTimeField( default = datetime.datetime.utcnow().replace(tzinfo=utc) )


def fname():
    """docstring for fname"""
    pass

def yello():
	"""docstring for yello"""
	pass

class Gene(models.Model):
    name = models.CharField(max_length=200)
    gene_class = models.IntegerField( null = True, blank = True )
    description = models.TextField( default = '' , blank = True )

    def __str__(self):
	return self.name + '|Class-' + str(self.gene_class)

class Allele(models.Model):
    gene = models.ForeignKey( Gene, null = True, blank = True )
    code = models.CharField(max_length=200)
    #dna_type = models.CharField(max_length=200)
    #ser_type = models.CharField(max_length=200)
    isSer = models.BooleanField( default = False )
    description = models.TextField( default = '' , blank = True, null=True )

    def get_summary( self ):
	pass

    def get_class( self ):
	return self.__class__

    def __str__(self):
	return self.code

    class Meta:
    	unique_together = ( ('gene', 'code'), )

    def get_experiments( self ):
	return Experiment.objects.filter( cell_line__alleles = self, antibody__alleles = self  ).distinct()



class Entity(models.Model):
    common_name = models.CharField(max_length=200)
    sci_name = models.CharField(max_length=200, blank=True, null=True )
    description = models.TextField( default = '', blank = True, null=True  )
    isOrganism = models.BooleanField( default = False )

    def __str__(self):
	return self.common_name

    def find_cell_lines( self ):
	return CellLine.objects.filter( individuals__entity = self ).distinct()


class Individual(models.Model):
    identifier = models.CharField(max_length=200, unique = True )
    description = models.TextField( default = '' , blank = True, null=True )
    nation_origin = models.CharField(max_length=200, blank=True, null=True )
    entity = models.ForeignKey( Entity, blank=True, null=True )
    isHost = models.BooleanField( default = False )
    isAnonymous = models.BooleanField( default = True )
    web_ref = models.CharField(max_length=200, default = '', null = True, blank=True )




    def __str__(self):
	return self.identifier

class CellLine(models.Model):
    name = models.CharField(max_length=200)
    tissue_type = models.CharField(max_length=200, blank=True, null=True)
    isTissue = models.BooleanField(default=False)
    description = models.TextField( default = '',blank=True, null=True )
    #host = models.ForeignKey( Organism, related_name = 'HostCell' )
    #infecteds = models.ManyToManyField( Organism, related_name = 'Infections' )
    individuals = models.ManyToManyField( Individual )
    alleles = models.ManyToManyField( Allele, through='Expression' )
    parent = models.ForeignKey( 'self', null = True, blank = True )
    #antibodies = models.ManyToManyField( Antibody )

    class Meta:
        """docstring for Meta"""
        #unique_together = ('name', 'description')
            

    def __str__(self):
	return self.name

    def get_antibodies_targeting( self ):
	return Antibody.objects.filter( alleles__cellline = self, experiments__cell_line = self ).distinct()

    def get_antibodies( self ):
	return Antibody.objects.filter( experiments__cell_line = self ).distinct()

    def get_experiments( self ):
	return Experiment.objects.filter( cell_line = self ).distinct()

    def get_organisms( self ):
	return Entity.objects.filter( isOrganism = True, individual__cellline = self )


class Expression(models.Model):
    """docstring for Expression"""
    cell_line = models.ForeignKey( CellLine )
    allele = models.ForeignKey( Allele )
    isSilenced = models.BooleanField( default = False )
    expression_level = models.FloatField( default = 100.0 )

    def __str__(self):
        """docstring for __str__"""
        return self.cell_line.name + '|' + self.allele.code
        

class Lodgement(models.Model):
    """docstring for Lodgement"""
    datetime = models.DateTimeField( )
    title = models.CharField( max_length = 300, unique = True )
    user = models.ForeignKey(User)
    datafilename = models.CharField(max_length=400,blank=True, null=True)
    isFree = models.BooleanField( default = False )

    def __str__(self):
        return self.datetime.strftime("%Y-%m-%d %H:%M:%S")

    def filename(self):
        return os.path.basename(self.datafile.name)

    class Meta:
        permissions = (
                ( 'view_lodgement', 'can view lodgement' ),
                ( 'edit_lodgement', 'can edit lodgement' ),
                )

    def get_experiment(self):
        try:
            return Experiment.objects.filter( dataset__lodgement = self ).distinct()[0]
        except:
            return None

def create_views_better():
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

class Experiment( models.Model ):
    title = models.CharField(max_length=200)
    description = models.TextField( default = '',blank=True, null=True )
    #date_time = models.DateTimeField('date run')
    #data = models.FileField()
    cell_line = models.ForeignKey( CellLine )
    #lodgement = models.ForeignKey( Lodgement )
    notes = models.TextField( default = '',blank=True, null=True )
    #morenotes = models.TextField( default = '',blank=True, null=True )
    #proteins = models.ManyToManyField( 'Protein', blank=True, null=True )

    class Meta:
        permissions = (
                ( 'view_experiment', 'can view experiment' ),
                ( 'view_experiment_disallowed', 'can view all experiment entries' ),
                ( 'edit_experiment', 'can edit experiment' ),
                )

    def __str__(self):
	return self.title

    def get_common_alleles( self ):
	return Allele.objects.filter( antibody__experiments = self, cellline__experiment = self )

    def get_proteins(self):
        """docstring for get_proteins"""
        return Protein.objects.filter( peptide__ion__experiments = self )

    def get_publications(self):
        """docstring for get_publications"""
        return list( set( Publication.objects.filter( lodgements__dataset__experiment = self ) ) )

    @property
    def publications(self):
        """docstring for get_publications"""
        return list( set( Publication.objects.filter( lodgements__dataset__experiment = self ) ) )

    def get_lodgements(self):
        return Lodgement.objects.filter( dataset__experiment__id = self.id ).distinct().order_by('datafilename')




class Antibody(models.Model):
    name = models.CharField(max_length=200, unique = True )
    link = models.CharField(max_length=400, blank=True, null=True)
    description = models.TextField( default = '',blank=True, null=True )
    alleles = models.ManyToManyField( Allele, blank=True, null=True )
    experiments = models.ManyToManyField( Experiment, blank=True, null=True)

    def __str__(self):
	return self.name

    def get_cell_lines_targeted( self ):
	return CellLine.objects.filter( alleles__antibody = self, experiment__antibody = self ).distinct()

class Ptm(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField( default = '',blank=True, null=True )
    mass_change = models.FloatField(null=True, blank=True)

    def fname(self):
        """docstring for fname"""
        pass

    def __str__(self):
	return self.description + '|' + str( self.mass_change )


class Protein(models.Model):
    prot_id = models.CharField(max_length=200, blank=True,null=True)
    name = models.TextField( default = '',blank=True, null=True ) #CharField(max_length=200)
    description = models.TextField( default = '',blank=True, null=True )
    sequence = models.TextField( default = '',blank=True, null=True )

    def get_uniprot_link(self):
        """docstring for get_uniprot_code"""
        externaldb = ExternalDb.objects.get( db_name = 'UniProt' )
        return externaldb.url_stump + self.prot_id + externaldb.url_suffix

    def get_uniprot_code(self):
        """docstring for get_uniprot_code"""
        lu = LookupCode.objects.get( protein = self, externaldb__db_name = 'UniProt' )
        return lu.code

    def __str__(self):
	return self.description
    
    def get_experiments( self ):
	return Experiment.objects.filter( ion__peptides__proteins = self ).distinct()


class Peptide(models.Model):
    sequence = models.CharField(max_length=200)
    mass = models.FloatField( null=True, blank=True )
    #ptms = models.ManyToManyField( Ptm )

    def __str__(self):
	return self.sequence

    def get_ptms(self):
        """docstring for get_ptms"""
        return Ptm.objects.filter( idestimate__peptide = self ).distinct() 

    def get_proteins(self):
        """docstring for get_ptms"""
        return Protein.objects.filter( peptoprot__peptide = self ).distinct() 


class Position(models.Model):
    """docstring for Position"""
    initial_res = models.IntegerField()
    final_res = models.IntegerField()

    def __str__(self):
        """docstring for __str__"""
        return "%d-%d" %( self.initial_res, self.final_res )
        



class Ion(models.Model):
    precursor_mass = models.FloatField()
    mz = models.FloatField()
    charge_state = models.IntegerField()
    retention_time = models.FloatField()
    experiment = models.ForeignKey(Experiment)
    spectrum = models.CharField( default = '',max_length=200, blank=True, null=True)
    dataset = models.ForeignKey('Dataset')
    peptides = models.ManyToManyField( Peptide, through='IdEstimate')
    #antibodies = models.ManyToManyField( Antibody )
    #cell_lines = models.ManyToManyField( CellLine )

    def __str__(self):
	return str(self.precursor_mass) + '|' + str(self.charge_state) + '|' + str(self.mz)


class IdEstimate(models.Model):
    peptide = models.ForeignKey(Peptide)
    ion = models.ForeignKey(Ion)
    ptms = models.ManyToManyField(Ptm)
    proteins = models.ManyToManyField( Protein )
    #experiment = models.ForeignKey(Experiment)
    delta_mass = models.FloatField()
    confidence = models.FloatField()
    isValid = models.BooleanField( default = False )
    #isRedundent = models.BooleanField( default = False )
    isRemoved = models.BooleanField( default = False )
    reason = models.TextField( default = '', blank=True, null=True )

    def check_ptm(self):
        """docstring for check_ptm"""
        if not self.ptm or self.ptm.description in ( '', ' ',
                '[undefined]', '[undefined] ' ):
            return False
        else:
            return True

    def __str__(self):
	return str(self.delta_mass) + '|' + str(self.confidence)

    def get_lodgement(self):
        """docstring for get_lodgement"""
        return Lodgement.objects.get( dataset__ions__idestimate = self )

    def get_dataset(self):
        """docstring for get_lodgement"""
        return Dataset.objects.get( ions__idestimate = self )





class Manufacturer(models.Model):
    """docstring for Manufacturer"""
    name = models.CharField(max_length=200)

    def __str__(self):
        """docstring for __str__"""
        return self.name
        

class Instrument(models.Model):
    """docstring for Instrument"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True,null=True)
    manufacturer = models.ForeignKey(Manufacturer,blank=True, null=True)

    def __unicode__(self):
        """docstring for __str__"""
        return force_unicode(self.name)
        

class Dataset(models.Model):
    """docstring for Dataset"""
    title = models.CharField(max_length=300, unique=True )
    rank = models.IntegerField( null=True, blank=True )
    datetime = models.DateTimeField( null=True, blank=True )
    data = models.FileField( blank = True, null=True )
    gradient_min = models.FloatField(null=True, blank=True)
    gradient_max = models.FloatField(null=True, blank=True)
    gradient_duration = models.FloatField(null=True, blank=True)
    instrument = models.ForeignKey(Instrument)
    lodgement = models.ForeignKey(Lodgement)
    experiment = models.ForeignKey(Experiment)
    notes = models.TextField( default = '', blank = True, null=True )
    confidence_cutoff = models.FloatField( null=True, blank=True )
    dmass_cutoff = models.FloatField( null=True, blank=True )

    class Meta:
        permissions = (
                ( 'view_dataset', 'can view dataset' ),
                ( 'edit_dataset', 'can edit dataset' ),
                )


    def __str__(self):
        """docstring for __str__"""
        return self.title

    def update_rank(self):
        """docstring for update_rank"""
        expt = Experiment.objects.get( dataset = self )
        curmax = max( [ b.rank for b in expt.dataset_set.all() ] )
        print curmax
        #if self.rank is not None:
        if curmax is not None:
            if self.rank is None:
                self.rank = curmax + 1
        else:
            self.rank = 0
        self.save()


        

class ExternalDb(models.Model):
    """docstring for ExternalDb"""
    db_name = models.CharField(max_length=200)
    url_stump = models.CharField(max_length=400)
    url_suffix = models.CharField(max_length=400, blank=True, null=True)

    def __str__(self):
        """docstring for __str__"""
        return self.db_name + '|' + self.url_stump
        

class LookupCode(models.Model):
    """docstring for Code"""
    code = models.CharField(max_length=200)
    externaldb = models.ForeignKey( ExternalDb )
    protein = models.ForeignKey( Protein, null=True, blank=True )
    cell_lines = models.ManyToManyField( CellLine )

    def __str__(self):
        """docstring for __str__"""
        return self.code + '|' + self.externaldb.db_name

class Publication(models.Model):
    """docstring for Publication"""
    title = models.TextField(blank=True, null=True)
    journal = models.TextField(blank=True, null=True)
    display = models.TextField(default='',blank=True, null=True)
    lodgements = models.ManyToManyField( Lodgement )
    cell_lines = models.ManyToManyField( CellLine )
    lookupcode = models.OneToOneField( LookupCode, null=True, blank=True )

    def __unicode__(self):
        """docstring for _"""
        return force_unicode(self.title) + '|' + force_unicode(self.journal)

    def refresh_display(self):
        """docstring for refresh_display
        idea is to get authors etc from PubMed and condense into string"""
        pass
        

        





