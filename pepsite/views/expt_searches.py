__author__ = 'rimmer'



from django.shortcuts import render, get_object_or_404
from pepsite.pepsite_forms import * # need to comment this out during migrations
from pepsite.make_searches import *
from pepsite.models import *
import sys
import os, tempfile, zipfile
from django.core.servers.basehttp import FileWrapper
from django.conf import settings
import mimetypes
from django.db import IntegrityError, transaction
from django.contrib.auth.models import User
# celery tasks:
from celery import chain
from pepsite.tasks import *
import datetime
from django.http import HttpResponse
import tempfile
import pepsite.uploaders
import zipfile
from django.contrib.auth.decorators import login_required
import re
from django.core.mail import send_mail
import pickle



def cell_line_expts( request, cell_line_id ):
    cl1 = CellLine.objects.get( id = cell_line_id )
    text_input = cl1.name
    expts = Experiment.objects.filter( cell_line = cl1 )
    context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'CellLine', 'query_obj' : cl1  }
    return render( request, 'pepsite/searched_expts.html', context)

def gene_expts( request, gene_id ):
    g1 = Gene.objects.get( id = gene_id )
    text_input = g1.name
    expts = Experiment.objects.filter( cell_line__alleles__gene = g1, antibody__alleles__gene = g1 ).distinct()
    context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'Gene', 'query_obj' : g1  }
    return render( request, 'pepsite/searched_expts.html', context)

def entity_expts( request, entity_id ):
    en1 = Entity.objects.get( id = entity_id )
    text_input = en1.common_name
    expts = Experiment.objects.filter( cell_line__individuals__entity = en1 )
    context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'Entity', 'query_obj' : en1  }
    if en1.isOrganism:
        context['query_on'] = 'Organism'
    return render( request, 'pepsite/searched_expts.html', context)


def composite_search( request ):
    if request.method == 'POST': # If the form has been submitted...
        form = TextOnlyForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            text_input = form.cleaned_data['text_input']
            s1 = CellLineSearch()
            expts = s1.get_experiments_basic( text_input )
            context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'CellLine', 'search' : True, 'heading' : 'Composite'  }
            return render( request, 'pepsite/searched_expts.html', context ) # Redirect after POST
        else:
            textform = TextOnlyForm()
            context = { 'search_message' : True, 'textform' : textform }
            return render( request, 'pepsite/composite_search.html', context ) # Redirect after POST

    else:
        textform = TextOnlyForm()
        context = { 'textform' : textform }
        return render( request, 'pepsite/composite_search.html', context)


def cell_line_search( request ):
    if request.method == 'POST': # If the form has been submitted...
        form = TextOnlyForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            text_input = form.cleaned_data['text_input']
            s1 = CellLineSearch()
            expts = s1.get_experiments_basic( text_input )
            context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'CellLine', 'search' : True, 'heading' : 'Cell Line'  }
            return render( request, 'pepsite/searched_expts.html', context ) # Redirect after POST
        else:
            textform = TextOnlyForm()
            context = { 'search_message' : True, 'textform' : textform }
            return render( request, 'pepsite/cell_line_search.html', context ) # Redirect after POST

    else:
        textform = TextOnlyForm()
        context = { 'textform' : textform }
        return render( request, 'pepsite/cell_line_search.html', context)

def ptm_search( request ):
    if request.method == 'POST': # If the form has been submitted...
        form = TextOnlyForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            text_input = form.cleaned_data['text_input']
            s1 = PtmSearch()
            expts = s1.get_experiments_basic( text_input )
            context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'Ptm', 'search' : True, 'heading' : 'PTM'  }
            return render( request, 'pepsite/searched_expts.html', context ) # Redirect after POST
        else:
            textform = TextOnlyForm()
            context = { 'search_message' : True, 'textform' : textform }
            return render( request, 'pepsite/ptm_search.html', context ) # Redirect after POST

    else:
        textform = TextOnlyForm()
        context = { 'textform' : textform }
        return render( request, 'pepsite/ptm_search.html', context)

def protein_search( request ):
    if request.method == 'POST': # If the form has been submitted...
        form = TextOnlyForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            text_input = form.cleaned_data['text_input']
            s1 = ProteinsSearch()
            expts, proteins = s1.get_experiments_basic( text_input )
            context = { 'msg' : expts, 'text_input' : text_input, 'proteins' : proteins, 'query_on' : 'Protein', 'search' : True }
            return render( request, 'pepsite/protein_searched_expts.html', context ) # Redirect after POST
        else:
            textform = TextOnlyForm()
            context = { 'search_message' : True, 'textform' : textform }
            return render( request, 'pepsite/protein_search.html', context ) # Redirect after POST

    else:
        textform = TextOnlyForm()
        context = { 'textform' : textform }
        return render( request, 'pepsite/protein_search.html', context)

#@login_required
def cell_line_tissue_search( request ):
    if request.method == 'POST': # If the form has been submitted...
        form = TextOnlyForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            text_input = form.cleaned_data['text_input']
            s1 = CellLineTissueSearch()
            expts = s1.get_experiments_basic( text_input )
            context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'CellLine', 'search' : True, 'heading' : 'Tissue type' }
            return render( request, 'pepsite/searched_expts.html', context ) # Redirect after POST
        else:
            text_input = request.POST['text_input']
            context = { 'msg' : text_input }
            return render( request, 'pepsite/searched_expts.html', context ) # Redirect after POST

    else:
        textform = TextOnlyForm()
        context = { 'textform' : textform }
        return render( request, 'pepsite/cell_line_tissue_search.html', context)

def allele_search( request ):
    if request.method == 'POST': # If the form has been submitted...
        form = TextOnlyForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            text_input = form.cleaned_data['text_input']
            s1 = AlleleSearch()
            expts = s1.get_experiments_basic( text_input )
            context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'Allele', 'search' : True }
            return render( request, 'pepsite/searched_expts.html', context ) # Redirect after POST
        else:
            text_input = request.POST['text_input']
            context = { 'msg' : text_input }
            return render( request, 'pepsite/searched_expts.html', context ) # Redirect after POST

    else:
        textform = TextOnlyForm()
        context = { 'textform' : textform }
        return render( request, 'pepsite/allele_search.html', context)

#@login_required
def peptide_expts( request, peptide_id ):
    peptide = get_object_or_404( Peptide, id = peptide_id )
    ptms = peptide.get_ptms()
    text_input = peptide.sequence
    expts = Experiment.objects.filter( ion__peptides = peptide ).distinct()
    context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'Peptide', 'query_obj' : peptide, 'pep_ptms' : ptms  }
    return render( request, 'pepsite/searched_expts.html', context)

#@login_required
def antibody_expts( request, antibody_id ):
    ab1 = get_object_or_404( Antibody, id = antibody_id )
    text_input = ab1.name
    expts = Experiment.objects.filter( antibody = ab1 ).distinct()
    context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'Antibody', 'query_obj' : ab1  }
    return render( request, 'pepsite/searched_expts.html', context)

#@login_required
def ptm_expts( request, ptm_id ):
    ptm1 = get_object_or_404( Ptm, id = ptm_id )
    text_input = ptm1.description
    expts = Experiment.objects.filter( ion__idestimate__ptms = ptm1 ).distinct()
    context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'Ptm', 'query_obj' : ptm1 }
    return render( request, 'pepsite/searched_expts.html', context)

def allele_expts( request, allele_id ):
    al1 = get_object_or_404( Allele, id = allele_id )
    text_input = al1.code
    expts = Experiment.objects.filter( cell_line__alleles = al1, antibody__alleles = al1 )
    context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'Allele', 'query_obj' : al1 }
    if al1.isSer:
        context['query_on'] = 'Serotype'
    return render( request, 'pepsite/searched_expts.html', context)


