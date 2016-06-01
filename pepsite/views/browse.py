__author__ = 'rimmer'


from django.shortcuts import render, get_object_or_404
from pepsite.pepsite_forms import * # need to comment this out during migrations
from pepsite.make_searches import *
from pepsite.models import *
from pepsite.tasks import *
from django.contrib.auth.decorators import login_required

def index( request ):
    return render( request, 'pepsite/index.html', {})

def allele_browse( request ):
    alleles = Allele.objects.all().distinct().order_by('code')
    context = { 'alleles' : alleles }
    return render( request, 'pepsite/allele_browse.html', context)

def experiment_browse( request ):
    experiments = Experiment.objects.all().distinct()
    context = { 'experiments' : experiments }
    return render( request, 'pepsite/experiment_browse.html', context)

def protein_browse( request ):
    proteins = Protein.objects.all().distinct()
    context = { 'proteins' : proteins }
    return render( request, 'pepsite/protein_browse.html', context)

def protein_browse_ajax( request ):
    user = request.user
    if user.id is None:
        user = User.objects.get( id = -1 )
    complete = True
    for expt in Experiment.objects.all():
        if not user.has_perm( 'view_experiment', expt ):
            complete = False
            break
    return render( request, 'pepsite/protein_browse_ajax.html', {'complete' : complete})

def browsable_proteins_render(request):
    """docstring for browsable_proteins_render"""
    print '\n\nActivated!!!\n\n'
    proteins = Protein.objects.all().distinct()
    context = { 'proteins' : proteins }
    return render( request, 'pepsite/render_proteins_for_browse.html', context)

def browsable_proteins_render_quicker(request):
    """docstring for browsable_proteins_render"""
    print '\n\nActivated QUICKER!!!\n\n'
    s1 = ExptArrayAssemble()
    rows = s1.protein_browse()
    context = { 'rows' : rows }
    return render( request, 'pepsite/render_proteins_for_browse_quicker.html', context)


#@login_required
def cell_line_browse( request ):
    cell_lines = CellLine.objects.all().distinct()
    context = { 'cell_lines' : cell_lines }
    return render( request, 'pepsite/cell_line_browse.html', context)

#@login_required
def cell_line_tissue_browse( request ):
    cell_lines = CellLine.objects.all(  ).distinct().order_by( 'tissue_type' )
    context = { 'cell_lines' : cell_lines }
    return render( request, 'pepsite/cell_line_tissue_browse.html', context)


@login_required
def stats_dashboard(request):
    protein_count = Protein.objects.all().count()
    peptide_count = Peptide.objects.all().count()
    allele_count = Allele.objects.all().count()
    lodgement_count = Lodgement.objects.all().count()
    cellline_count = CellLine.objects.all().count()
    idestimate_count = IdEstimate.objects.all().count()

    return render(request,
                  'pepsite/stats_dashboard.html',
                  {'protein_count': protein_count,
                   'allele_count': allele_count,
                   'peptide_count': peptide_count,
                   'lodgement_count': lodgement_count,
                   'idestimate_count': idestimate_count,
                   'cellline_count': cellline_count,})