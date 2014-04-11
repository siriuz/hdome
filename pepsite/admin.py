from django.contrib import admin
from pepsite.models import *

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

admin.site.register(Allele, AlleleAdmin)
admin.site.register(Antibody, AntibodyAdmin)

# Register your models here.
