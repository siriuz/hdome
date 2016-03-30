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
import django_tables2 as tables
from django_tables2   import RequestConfig


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
            upload_dict = {'uldict': ul.uldict,
                           'uniprot_ids': ul.uniprot_ids,
                           'expt_id': ul.expt_id,
                           'expt_title': ul.expt_title,
                           'publications': ul.publications,
                           'public': ul.public,
                           'antibody_ids': ul.antibody_ids,
                           'lodgement_title': ul.lodgement_title,
                           'lodgement': ul.lodgement,
                           'dataset_nos': ul.dataset_nos,
                           'instrument_id': ul.instrument_id,
                           'cell_line_id': ul.cell_line_id,
                           'expt_id': ul.expt_id,
                           'lodgement_filename': ul.lodgement_filename,
                           'expt_desc': ul.expt_desc,
                           'allfields': ul.allfields,
                           'singlerows': ul.singlerows,
                           'singlerows_header': ul.singlerows_header}

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


@login_required
def add_cell_line(request):
    """
    View for adding a new cell line
    """

    if request.method == 'POST':
        form = AddCellLineForm(request.POST)

        if form.is_valid():
            alleles = form.cleaned_data.pop('alleles')
            new_cellline = form.save()

            for allele in alleles:
                Expression.objects.create(cell_line=new_cellline, allele=allele)

    cellline_form = AddCellLineForm()

    celllines_table = CellLineTable(CellLine.objects.all())
    RequestConfig(request).configure(celllines_table)

    context = {'cellline_form': cellline_form, 'celllines_table': celllines_table}
    return render(request, 'pepsite/add_cell_line_form.html', context)

# def add_gene(request):
#     """
#     Add a new gene
#     """
#
#     if request.method == 'POST':
#         pass



class CellLineTable(tables.Table):
    class Meta:
        model = CellLine
        attrs = {"class": "table"}


@login_required
def add_instrument(request):
    """
    View for adding a new instrument
    """

    if request.method == 'POST':
        form = AddInstrumentForm(request.POST)

        if form.is_valid():
            form.save()

    instrument_form = AddInstrumentForm()

    instrument_table = InstrumentTable(Instrument.objects.all())
    RequestConfig(request).configure(instrument_table)

    context = {'instrument_form': instrument_form, 'instrument_table': instrument_table}
    return render(request, 'pepsite/add_instrument_form.html', context)


class InstrumentTable(tables.Table):
    class Meta:
        model = Instrument
        attrs = {"class": "table"}


@login_required
def add_manufacturer(request):
    """
    View for adding a new manufacturer
    """

    if request.method == 'POST':
        form = AddManufacturerForm(request.POST)

        if form.is_valid():
            form.save()

    manufacturer_form = AddManufacturerForm()

    manufacturer_table = ManufacturerTable(Manufacturer.objects.all())
    RequestConfig(request).configure(manufacturer_table)

    context = {'manufacturer_form': manufacturer_form, 'manufacturer_table': manufacturer_table}
    return render(request, 'pepsite/add_manufacturer_form.html', context)


class ManufacturerTable(tables.Table):
    class Meta:
        model = Manufacturer
        attrs = {"class": "table"}


@login_required
def add_antibody(request):
    """
    View for adding a new Antibody
    """

    if request.method == 'POST':
        form = AddAntibodyForm(request.POST)

        if form.is_valid():
            form.save()

    antibody_form = AddAntibodyForm()

    antibody_table = AntibodyTable(Antibody.objects.all())
    RequestConfig(request).configure(antibody_table)

    context = {'antibody_form': antibody_form, 'antibody_table': antibody_table}
    return render(request, 'pepsite/add_antibody_form.html', context)


class AntibodyTable(tables.Table):
    class Meta:
        model = Antibody
        attrs = {"class": "table"}


@login_required
def add_gene(request):
    """
    View for adding a new Gene
    """

    if request.method == 'POST':
        form = AddGeneForm(request.POST)

        if form.is_valid():
            form.save()

    gene_form = AddGeneForm()

    gene_table = GeneTable(Gene.objects.all())
    RequestConfig(request).configure(gene_table)

    context = {'gene_form': gene_form, 'gene_table': gene_table}
    return render(request, 'pepsite/add_gene_form.html', context)


class GeneTable(tables.Table):
    class Meta:
        model = Gene
        attrs = {"class": "table"}


@login_required
def add_allele(request):
    """
    View for adding a new Allele
    """

    if request.method == 'POST':
        form = AddAlleleForm(request.POST)

        if form.is_valid():
            form.save()

    allele_form = AddAlleleForm()

    allele_table = AlleleTable(Allele.objects.all())
    RequestConfig(request).configure(allele_table)

    context = {'allele_form': allele_form, 'allele_table': allele_table}
    return render(request, 'pepsite/add_allele_form.html', context)


class AlleleTable(tables.Table):
    class Meta:
        model = Allele
        attrs = {"class": "table"}
