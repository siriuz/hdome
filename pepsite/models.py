from django.db import models
from django.contrib.auth.models import User


class Gene(models.Model):
    name = models.CharField(max_length=200)
    gene_class = models.IntegerField()
    description = models.TextField( default = '' )

    def __str__(self):
	return self.name + '|Class-' + str(self.gene_class)

class Allele(models.Model):
    gene = models.ForeignKey( Gene )
    code = models.CharField(max_length=200)
    #dna_type = models.CharField(max_length=200)
    #ser_type = models.CharField(max_length=200)
    isSer = models.BooleanField( default = False )
    description = models.TextField( default = '' )

    def __str__(self):
	return self.code
    class Meta:
    	unique_together = ( ('gene', 'code'), )



class Entity(models.Model):
    common_name = models.CharField(max_length=200)
    sci_name = models.CharField(max_length=200, unique = True )
    description = models.TextField( default = '' )
    isOrganism = models.BooleanField( default = False )

    def __str__(self):
	return self.sci_name


class Individual(models.Model):
    identifier = models.CharField(max_length=200, unique = True )
    description = models.TextField( default = '' )
    nation_origin = models.CharField(max_length=200 )
    entity = models.ForeignKey( Entity, blank=True, null=True )
    isHost = models.BooleanField( default = False )
    isAnonymous = models.BooleanField( default = True )
    web_ref = models.CharField(max_length=200, unique = True )


    

    def __str__(self):
	return self.identifier

class CellLine(models.Model):
    name = models.CharField(max_length=200)
    tissue_type = models.CharField(max_length=200)
    description = models.TextField( default = '' )
    #host = models.ForeignKey( Organism, related_name = 'HostCell' )
    #infecteds = models.ManyToManyField( Organism, related_name = 'Infections' )
    individuals = models.ManyToManyField( Individual )
    alleles = models.ManyToManyField( Allele )
    #antibodies = models.ManyToManyField( Antibody )

    def __str__(self):
	return self.name


class Experiment( models.Model ):
    title = models.CharField(max_length=200)
    description = models.TextField( default = '' )    
    date_time = models.DateTimeField('date run')
    data = models.FileField()
    cell_line = models.ForeignKey( CellLine )

    def __str__(self):
	return self.title + '|' + str(self.date_time)


class Antibody(models.Model):
    name = models.CharField(max_length=200, unique = True )
    description = models.TextField( default = '' )
    alleles = models.ManyToManyField( Allele )
    experiments = models.ManyToManyField( Experiment )

    def __str__(self):
	return self.name


class Ptm(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField( default = '' )
    mass_change = models.FloatField()

    def __str__(self):
	return self.description + '|' + str( self.mass_change )


class Protein(models.Model):
    prot_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    description = models.TextField( default = '' )

    def __str__(self):
	return self.prot_id + '|' + self.name

class Peptide(models.Model):
    sequence = models.CharField(max_length=200)
    mass = models.FloatField()
    proteins = models.ManyToManyField( Protein )
    ptms = models.ManyToManyField( Ptm )

    def __str__(self):
	return self.sequence


class Ion(models.Model):
    precursor_mass = models.FloatField()
    charge_state = models.IntegerField()
    retention_time = models.FloatField()
    experiments = models.ManyToManyField(Experiment)
    peptides = models.ManyToManyField( Peptide, through='IdEstimate')
    #antibodies = models.ManyToManyField( Antibody )
    #cell_lines = models.ManyToManyField( CellLine )

    def __str__(self):
	return str(self.precursor_mass) + '|' + str(self.charge_state)


class IdEstimate(models.Model):
    peptide = models.ForeignKey(Peptide)
    ion = models.ForeignKey(Ion)
    #experiment = models.ForeignKey(Experiment)
    delta_mass = models.FloatField()
    confidence = models.FloatField()

    def __str__(self):
	return str(self.delta_mass) + '|' + str(self.confidence)





