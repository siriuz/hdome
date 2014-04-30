from django.shortcuts import render, get_object_or_404
from pepsite.pepsite_forms import *
from pepsite.make_searches import *

import os, tempfile, zipfile
from django.core.servers.basehttp import FileWrapper
from django.conf import settings
import mimetypes

import datetime
from django.http import HttpResponse 
import tempfile 

import zipfile

def index( request ):
	return render( request, 'pepsite/index.html', {})

def allele_search( request ):
    if request.method == 'POST': # If the form has been submitted...
        form = TextOnlyForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
	    text_input = form.cleaned_data['text_input']
	    s1 = AlleleSearch()
	    expts = s1.get_experiments_basic( text_input )
	    context = { 'msg' : expts, 'text_input' : text_input }
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

def protein_expts( request, protein_id ):
    prot = get_object_or_404( Protein, id = protein_id )
    s1 = ProteinSearch()
    expts = s1.get_experiments_from_protein( prot )
    context = { 'msg' : expts, 'protein' : prot }
    return render( request, 'pepsite/protein_expts.html', context)

def expt( request, expt_id ):
    expt = get_object_or_404( Experiment, id = expt_id )
    s1 = ExptAssemble()
    details = s1.get_peptide_info( expt )
    alleles = s1.get_common_alleles( expt )
    context = { 'details' : details, 'expt' : expt, 'alleles' : alleles }
    return render( request, 'pepsite/expt.html', context)


def expt3( request, expt_id ):
    proteins = set(Protein.objects.filter( peptide__ion__experiments__id = expt_id))
    
    context = { 'proteins' : proteins,  }
    return render( request, 'pepsite/expt2.html', context)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def expt2( request, expt_id ):
    proteins = list(set(Protein.objects.filter( peptide__ion__experiments__id = expt_id)))
    expt = get_object_or_404( Experiment, id = expt_id )
    paginator = Paginator(proteins, 25 ) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        proteins = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        proteins = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        proteins = paginator.page(paginator.num_pages)
    return render( request, 'pepsite/expt2.html', {"proteins": proteins, 'expt' : expt })

def expt2_alternate( request, expt_id ):
    proteins = list(set(Protein.objects.filter( peptide__ion__experiments__id = expt_id)))
    expt = get_object_or_404( Experiment, id = expt_id )
    paginator = Paginator(proteins, 25 ) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        proteins = paginator.page(page)
	#s1 = ExptAssemble()
	#proteins = s1.get_ancillaries( proteins, expt )
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        proteins = paginator.page(1)
	#s1 = ExptAssemble()
	#proteins = s1.get_ancillaries( proteins, expt )
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        proteins = paginator.page(paginator.num_pages)

    s1 = ExptAssemble()
    entries = s1.get_ancillaries( proteins, expt )

    return render( request, 'pepsite/new_expt2.html', {"proteins": proteins, 'entries' : entries, 'expt' : expt })


def send_expt_csv(request, expt_id ):
	
    expt = get_object_or_404( Experiment, id = expt_id )
    filestump = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    download_name = filestump + "_HaploDome_download.csv"
    proteins = list(set(Protein.objects.filter( peptide__ion__experiments = expt)))
    

    with tempfile.NamedTemporaryFile() as f:
	f.write( 'Protein,Peptide,Modification,Delta Mass,Confidence,Charge State,Retention Time,Precursor Mass,\n' )
	for protein in proteins:
	    for ide in IdEstimate.objects.filter( peptide__proteins = protein, ion__experiments = expt ):
		if ide.ptm is not None:
		    f.write( '%s,%s,%s,%f,%f,%d,%f,%f,\n' %( protein.prot_id, ide.peptide.sequence, ide.ptm.description, ide.delta_mass, ide.confidence,
			ide.ion.charge_state, ide.ion.retention_time, ide.ion.precursor_mass ) )
		else:
		    f.write( '%s,%s,%s,%f,%f,%d,%f,%f,\n' %( protein.prot_id, ide.peptide.sequence, '', ide.delta_mass, ide.confidence,
			ide.ion.charge_state, ide.ion.retention_time, ide.ion.precursor_mass ) )
	f.seek(0)
        wrapper      = FileWrapper( f )
        content_type = 'text/csv'
        response     = HttpResponse(wrapper,content_type=content_type)
        response['Content-Length']      = f.tell()   
        response['Content-Disposition'] = "attachment; filename=%s"%download_name
        return response
