
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


def mass_search( request ):
    user = request.user
    if request.GET.items(): # If the form has been submitted...
        form = MzSearchForm(request.GET) # A form bound to the POST data
        search_type, query_on = 'mass', 'Precursor Mass'
        target_input, tolerance = 0.0, 0.0
        desc = 'empty'
        if form.is_valid(): # All validation rules pass
            target_input = form.cleaned_data['target_input']
            tolerance = form.cleaned_data['tolerance']
            desc = u'mass = %s \u00B1 %s Da' % ( target_input, tolerance )
        else:
            context = {}
            for f in form.fields.keys():
                if f in form.data.keys():
                    context[f] = form.data[f]
                else:
                    context[f] = form.fields[f].initial
            target_input = context['target_input']
            tolerance = context['tolerance']
            desc = u'mass = %s \u00B1 %s Da' % ( target_input, tolerance )
        context = { 'search' : True, 'query_on' : query_on, 'text_input' : desc, 'search_type' : search_type, 'search_args' : [target_input, tolerance] }
        return render( request, 'pepsite/find_peptides_ajax.html', context ) # Redirect after POST
    else:
        textform = MassSearchForm()
        context = { 'massform' : textform }
        return render( request, 'pepsite/mass_search.html', context)

def mz_search( request ):
    user = request.user
    if request.GET.items(): # If the form has been submitted...
        form = MzSearchForm(request.GET) # A form bound to the POST data
        search_type, query_on = 'mz', 'Ion m/z'
        target_input, tolerance = 0.0, 0.0
        desc = 'empty'
        if form.is_valid(): # All validation rules pass
            target_input = form.cleaned_data['target_input']
            tolerance = form.cleaned_data['tolerance']
            desc = u'm/z = %s \u00B1 %s' % ( target_input, tolerance )
        else:
            context = {}
            for f in form.fields.keys():
                if f in form.data.keys():
                    context[f] = form.data[f]
                else:
                    context[f] = form.fields[f].initial
            target_input = context['target_input']
            tolerance = context['tolerance']
            desc = u'm/z = %s \u00B1 %s' % ( target_input, tolerance )
        context = { 'search' : True, 'query_on' : query_on, 'text_input' : desc, 'search_type' : search_type, 'search_args' : [target_input, tolerance] }
        return render( request, 'pepsite/find_peptides_ajax.html', context ) # Redirect after POST

    else:
        textform = MzSearchForm()
        context = { 'massform' : textform }
        return render( request, 'pepsite/mz_search.html', context)

def sequence_search( request ):
    user = request.user
    if request.GET.items(): # If the form has been submitted...
        form = MzSearchForm(request.GET) # A form bound to the POST data
        search_type, query_on = 'sequence', 'Peptide sequence'
        target_input = ''
        desc = 'empty'
        if form.is_valid(): # All validation rules pass
            target_input = str(form.cleaned_data['target_input'])
            desc = target_input
        else:
            context = {}
            for f in form.fields.keys():
                if f in form.data.keys():
                    context[f] = form.data[f]
                else:
                    context[f] = form.fields[f].initial
            target_input = str(context['target_input'])
            desc = target_input.upper()
        context = { 'search' : True, 'query_on' : query_on, 'text_input' : desc, 'search_type' : search_type, 'search_args' : [target_input] }
        return render( request, 'pepsite/find_peptides_ajax.html', context ) # Redirect after POST
    else:
        textform = SequenceSearchForm()
        context = { 'massform' : textform }
        return render( request, 'pepsite/sequence_search.html', context)

def ptm_peptide_search( request ):
    user = request.user
    if request.GET.items(): # If the form has been submitted...
        form = MzSearchForm(request.GET) # A form bound to the POST data
        search_type, query_on = 'ptm', 'PTM description'
        target_input = ''
        desc = 'empty'
        if form.is_valid(): # All validation rules pass
            target_input = str(form.cleaned_data['target_input'])
            desc = target_input
        else:
            context = {}
            for f in form.fields.keys():
                if f in form.data.keys():
                    context[f] = form.data[f]
                else:
                    context[f] = form.fields[f].initial
            target_input = str(context['target_input'])
            desc = target_input.upper()
        context = { 'search' : True, 'query_on' : query_on, 'text_input' : desc, 'search_type' : search_type, 'search_args' : [target_input] }
        return render( request, 'pepsite/find_peptides_ajax.html', context ) # Redirect after POST
    else:
        textform = PtmSearchForm()
        context = { 'massform' : textform }
        return render( request, 'pepsite/ptm_peptide_search.html', context)

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

def ptm_peptides( request, ptm_id ):
    user = request.user
    ptm1 = get_object_or_404( Ptm, id = ptm_id )
    complete = True
    excluded_ids = []
    for expt in Experiment.objects.filter( ion__idestimate__ptms__id = ptm_id ):
        if ( not user.has_perm( 'view_experiment', expt ) ):
            complete = False
            excluded_ids.append( expt.id )
    text_input = ptm1.description
    s1 = ExptArrayAssemble()
    rows = s1.ptm_peptides( ptm_id, excluded_ids )
    context = { 'text_input' : text_input, 'query_on' : 'Ptm', 'query_obj' : ptm1, 'rows' : rows, 'search' : False, 'complete' : complete }
    return render( request, 'pepsite/found_peptides_rapid.html', context)

def protein_peptides( request, protein_id ):
    user = request.user
    prot1 = get_object_or_404( Protein, id = protein_id )
    complete = True
    excluded_ids = []
    for expt in Experiment.objects.filter( ion__idestimate__proteins = protein_id ):
        if ( not user.has_perm( 'view_experiment', expt ) ):
            complete = False
            excluded_ids.append( expt.id )
    text_input = prot1.description
    s1 = ExptArrayAssemble()
    rows = s1.protein_peptides( protein_id, excluded_ids )
    context = { 'text_input' : text_input, 'query_on' : 'Protein', 'query_obj' : prot1, 'rows' : rows, 'search' : False, 'complete' : complete }
    return render( request, 'pepsite/found_peptides_rapid.html', context)

def peptide_peptides( request, peptide_id ):
    user = request.user
    pep = get_object_or_404( Peptide, id = peptide_id )
    complete = True
    excluded_ids = []
    for expt in Experiment.objects.filter( ion__idestimate__peptide__id = peptide_id ).distinct():
        if ( not user.has_perm( 'view_experiment', expt ) ):
            complete = False
            excluded_ids.append( expt.id )
    print 'excluded =', excluded_ids
    text_input = pep.sequence
    s1 = ExptArrayAssemble()
    rows = s1.peptide_peptides( peptide_id, excluded_ids  )
    context = { 'text_input' : text_input, 'query_on' : 'Peptide', 'query_obj' : pep, 'rows' : rows, 'complete' : complete  }
    return render( request, 'pepsite/found_peptides_rapid.html', context)
