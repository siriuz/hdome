from django.contrib import admin
from pepsite.models import *
from guardian.admin import GuardedModelAdmin

#admin.site.register( Allele )


class AllAbInline(admin.TabularInline):
    model = Antibody.alleles.through

class AlleleAdmin(admin.ModelAdmin):
    inlines = [
        AllAbInline,
    ]

class AntibodyAdmin(admin.ModelAdmin):
    inlines = [
        AllAbInline,
    ]
    exclude = ('alleles',)

class ExpressionInLine(admin.StackedInline):
    model = Expression
    extra = 3

class AlleleInLine(admin.StackedInline):
    model = Allele
    extra = 1
    
class GeneAdmin(admin.ModelAdmin):
    inlines = [
        AlleleInLine,
    ]

class LookCellInLine(admin.TabularInline):
    model = LookupCode.cell_lines.through

class LookupCodeAdmin(admin.ModelAdmin):
    inlines = [
        LookCellInLine,
    ]
    exclude = ( 'cell_lines',)

class PlCellInLine(admin.StackedInline):
    model = Publication.cell_lines.through

class PlLodgeInLine(admin.TabularInline):
    model = Publication.lodgements.through

class PublicationAdmin(admin.ModelAdmin):
    inlines = [
        PlCellInLine,
        PlLodgeInLine,
    ]
    exclude = ( 'cell_lines',
            'lodgements',)

class ClIndInLine(admin.TabularInline):
    model = CellLine.individuals.through

class CellLineAdmin(admin.ModelAdmin):
    inlines = [
        ExpressionInLine,
        LookCellInLine,
        PlCellInLine,
        ClIndInLine,
    ]
    exclude = (
            'individuals',
            )

class DatasetInLine(admin.StackedInline):
    model = Dataset
    extra = 1
    exclude = (
            'ions',
            )

class InstrumentInLine(admin.StackedInline):
    model = Instrument
    extra = 1
    exclude = (
            #'ions',
            )

class LodgementAdmin(GuardedModelAdmin):
    inlines = [
        DatasetInLine,
        PlLodgeInLine,
    ]

class DatasetAdmin(GuardedModelAdmin):
    inlines = [
        #DatasetInLine,
        #PlLodgeInLine,
    ]
    exclude = (
            'ions',
            )
class InstrumentAdmin(admin.ModelAdmin):
    inlines = [
        DatasetInLine,
        #PlLodgeInLine,
    ]

class ManufacturerAdmin(admin.ModelAdmin):
    inlines = [
            InstrumentInLine,
            ]


class ExpAbInline(admin.TabularInline):
    model = Antibody.experiments.through

class ExpIonInline(admin.TabularInline):
    model = Ion.experiments.through

class DsIonInline(admin.TabularInline):
    model = Dataset.ions.through

class LcClInline(admin.TabularInline):
    model = LookupCode.cell_lines.through

class IdEstimateInLine(admin.StackedInline):
    model = IdEstimate
    extra = 1

class LookupCodeInLine(admin.StackedInline):
    model = LookupCode
    extra = 1
    exclude = (
            'cell_lines',
            )

class IonAdmin(admin.ModelAdmin):
    inlines = [
        ExpIonInline,
        DsIonInline,
        IdEstimateInLine,
    ]
    exclude = ('experiments',)

class ExperimentAdmin(admin.ModelAdmin):
    inlines = [
        ExpAbInline,
        #ExpIonInline,
        DatasetInLine,
    ]

class IdEstimateAdmin(admin.ModelAdmin):
    pass
    inlines = [
        #ExpAbInline,
        #ExpIonInline,
        #DatasetInLine,
    ]

class LookupCodeAdmin(admin.ModelAdmin):
    inlines = [
        LcClInline,
        #ExpIonInline,
        #DatasetInLine,
    ]
    exclude = (
            'cell_lines',
            )

class ExternalDbAdmin(admin.ModelAdmin):
    pass
    inlines = [
        ]

class PtmAdmin(admin.ModelAdmin):
    pass

class PepToProtInLine(admin.StackedInline):
    model = PepToProt
    extra = 1

class PeptideAdmin( admin.ModelAdmin):
    inlines = [
            PepToProtInLine,
            ]

class PositionAdmin( admin.ModelAdmin):
    inlines = [
            #PepToProtInLine,
            ]

class ProteinAdmin( admin.ModelAdmin ):
    inlines = [
            PepToProtInLine,
            LookupCodeInLine,
            ]

class IndividualAdmin( admin.ModelAdmin ):
    pass

class IndividualInLine( admin.StackedInline ):
    model = Individual
    extra = 1

class EntityAdmin( admin.ModelAdmin ):
    inlines = [
            IndividualInLine,
            ]

admin.site.register(Allele, AlleleAdmin)
admin.site.register(Antibody, AntibodyAdmin)
admin.site.register(CellLine, CellLineAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(Lodgement, LodgementAdmin)
admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(Ion, IonAdmin)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(Instrument, InstrumentAdmin)
admin.site.register(Manufacturer, ManufacturerAdmin)
admin.site.register(Gene, GeneAdmin)
admin.site.register(IdEstimate, IdEstimateAdmin)
admin.site.register(LookupCode, LookupCodeAdmin)
admin.site.register(ExternalDb, ExternalDbAdmin)
admin.site.register(Ptm, PtmAdmin)
admin.site.register(Peptide, PeptideAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Protein, ProteinAdmin)
admin.site.register(Individual, IndividualAdmin)
admin.site.register(Entity, EntityAdmin)

# Register your models here.
