from django.shortcuts import render, get_object_or_404
from pepsite.pepsite_forms import *
from pepsite.make_searches import *



def index( request ):
	return render( request, 'pepsite/index.html', {})

def allele_search( request ):
    if request.method == 'POST': # If the form has been submitted...
        form = TextOnlyForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
	    text_input = form.cleaned_data['text_input']
	    s1 = AlleleSearch()
	    expts = s1.get_experiments_basic( 'DQ2' )
	    context = { 'msg' : expts }
            return render( request, 'pepsite/allele_results.html', context ) # Redirect after POST
	else:
	    text_input = request.POST['text_input']
	    context = { 'msg' : text_input }
            return render( request, 'pepsite/allele_results.html', context ) # Redirect after POST

    else:
        textform = TextOnlyForm()
        context = { 'textform' : textform }
        return render( request, 'pepsite/allele_search.html', context)

def allele_results( request ):
	context = { 'msg' : 'goodbye' }
	return render( request, 'pepsite/allele_results.html', context)

def peptide_expts( request, peptide_id ):
    peptide = get_object_or_404( Peptide, id = peptide_id )
    s1 = PeptideSearch()
    expts = s1.get_experiments_from_peptide( peptide )
    context = { 'msg' : expts, 'peptide' : peptide }
    return render( request, 'pepsite/peptide_expts.html', context)

def expt( request, expt_id ):
    expt = get_object_or_404( Experiment, id = expt_id )
    s1 = ExptAssemble()
    details = s1.get_peptide_info( expt )
    context = { 'details' : details, 'expt' : expt }
    return render( request, 'pepsite/expt.html', context)
