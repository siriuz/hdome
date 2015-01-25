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

@login_required
def upload_ss_form( request ):
    user = request.user
    if request.method == 'POST': # If the form has been submitted...
        form = UploadSSForm(request.POST, request.FILES) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            ul = pepsite.uploaders.Uploads( user = user )
            ss = request.FILES['ss']
            formdata = form.cleaned_data
            formdata['filename'] = ss.name
            ul.preview_ss_simple( formdata )
            ul.preprocess_ss_simple( ss )
            upload_dict = { 'uldict' : ul.uldict, 'uniprot_ids' : ul.uniprot_ids, 'expt_id' : ul.expt_id, 'expt_title' : ul.expt_title, 'publications' : ul.publications, 'public' : ul.public,
                            'antibody_ids' : ul.antibody_ids, 'lodgement_title' : ul.lodgement_title, 'lodgement' : ul.lodgement, 'dataset_nos' : ul.dataset_nos,
                            'instrument_id' : ul.instrument_id, 'cell_line_id' : ul.cell_line_id, 'expt_id' : ul.expt_id, 'lodgement_filename' : ul.lodgement_filename, 'expt_desc' : ul.expt_desc, 'allfields' : ul.allfields, 'singlerows' : ul.singlerows, 'singlerows_header' : ul.singlerows_header }
            request.session['ul'] = ul.uldict
            request.session['proteins'] = ul.uniprot_ids
            return render( request, 'pepsite/upload_preview.html', { 'upload' : ul, 'ss' : ss, 'formdata' : formdata, 'filled_form' : form, 'ul_supp' : upload_dict }  ) # Redirect after POST
        else:
            ul = pepsite.uploaders.Uploads( user = user )
            ss = request.FILES['ss']
            formdata = request.POST
            formdata['filename'] = ss.name
            ul.preview_ss_simple( formdata )
            ul.preprocess_ss_simple( ss )
            upload_dict = { 'uldict' : ul.uldict, 'uniprot_ids' : ul.uniprot_ids, 'expt_id' : ul.expt_id, 'expt_title' : ul.expt_title, 'publications' : ul.publications, 'public' : ul.public,
                            'antibody_ids' : ul.antibody_ids, 'lodgement_title' : ul.lodgement_title, 'lodgement' : ul.lodgement, 'dataset_nos' : ul.dataset_nos,
                            'instrument_id' : ul.instrument_id, 'cell_line_id' : ul.cell_line_id, 'expt_id' : ul.expt_id, 'lodgement_filename' : ul.lodgement_filename, 'expt_desc' : ul.expt_desc, 'allfields' : ul.allfields, 'singlerows' : ul.singlerows, 'singlerows_header' : ul.singlerows_header  }
            request.session['ul'] = ul.uldict
            request.session['proteins'] = ul.uniprot_ids
            request.session['ul_supp'] = upload_dict
            return render( request, 'pepsite/upload_preview.html', { 'upload' : ul, 'ss' : ss, 'formdata' : formdata, 'filled_form' : form, 'ul_supp' : upload_dict }  ) # Redirect after POST

    else:
        textform = UploadSSForm()
        context = { 'textform' : textform }
        return render( request, 'pepsite/upload_ss_form.html', context)

@login_required
def upload_manual_curations( request ):
    user = request.user
    if request.method == 'POST': # If the form has been submitted...
        form = CurationForm(request.POST, request.FILES,user=user) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            ul = pepsite.uploaders.Curate( user = user )
            cur = request.FILES['cur']
            formdata = form.cleaned_data
            ul.setup_curation( formdata, cur )
            ul_supp = { 'lodgement_ids' : ul.lodgement_ids, 'uldict' : ul.uldict, 'dataset_nos' : ul.dataset_nos, 'allstr' : ul.allstr }
            curate_ss_celery.delay( user.id, ul_supp )
            return render( request, 'pepsite/curation_outcome.html', { 'upload' : ul }  ) # Redirect after POST
        else:
            ul = pepsite.uploaders.Curate( user = user )
            cur = request.FILES['cur']
            formdata = request.POST
            ul.setup_curation( formdata, cur )
            ul_supp = { 'lodgement_ids' : ul.lodgement_ids, 'uldict' : ul.uldict, 'dataset_nos' : ul.dataset_nos, 'allstr' : ul.allstr }
            curate_ss_celery.delay( user.id, ul_supp )
            return render( request, 'pepsite/curation_outcome.html', { 'upload' : ul }  ) # Redirect after POST
    else:
        textform = CurationForm(user=user)
        lodgements_avail = True
        textform.fields['ldg'].choices = [ [b.id, '%s from Experiment: %s' %( b.title, b.get_experiment().title )] for b in Lodgement.objects.all() if user.has_perm( 'edit_lodgement', b )]
        if not textform.fields['ldg'].choices:
            lodgements_avail = False
        context = { 'textform' : textform, 'ldz' : lodgements_avail }
        return render( request, 'pepsite/curation_form.html', context)


@login_required
@transaction.atomic
def commit_upload_ss( request ):
    """
    """
    user = request.user
    elems = request.session['ul_supp']
    if request.method == 'POST':
        upload_ss_celery.delay( user.id, elems, request.POST )
        keys = request.POST.keys()
        ul = pepsite.uploaders.Uploads( user = user )
        ul.repopulate( elems )
        ul.add_cutoff_mappings( request.POST )
        context = { 'data' : request.POST['data'], 'ul' : ul, 'keys' : keys }
        return render( request, 'pepsite/ss_uploading.html', context)
    else:
        textform = UploadSSForm()
        context = { 'textform' : textform }
        return render( request, 'pepsite/upload_ss_form.html', context)
