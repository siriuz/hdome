from django.shortcuts import render, get_object_or_404
from pepsite.pepsite_forms import *
from pepsite.make_searches import *
from pepsite.models import *
import sys
import os, tempfile, zipfile
from django.core.servers.basehttp import FileWrapper
from django.conf import settings
import mimetypes

import datetime
from django.http import HttpResponse
import tempfile

import pepsite.uploaders

import zipfile

from django.contrib.auth.decorators import login_required

import re

import pickle

#@login_required
def index( request ):
	return render( request, 'pepsite/index.html', {})

#@login_required
def formdump( request ):
        context = { 'post' : request.POST.dict() }
	return render( request, 'pepsite/formdump.html', context )

#@login_required
def comp_results( request ):
        post = request.POST.dict()
        newdic = {}
        for k in post.keys():
            #newdic[k] = post[k]
            if 'input' in str(k) and str(k[-2:]) == '_1':
                qtype = post[k]
                qstring = post[ k[:-2] + '_2' ]
                ordinal =  k.split('_')[1]
                newdic[ordinal] = { 'qtype' : qtype, 'qstring' : qstring }
        ndkeys = sorted( newdic.keys(), key = lambda a: int(a) )
        cs = CompositeSearch()
        expts = cs.make_qseries( newdic, ndkeys )

        #context = { 'post' : expts }
        #return render( request, 'pepsite/formdump.html', context )
        context = { 'msg' : expts, 'search' : True, 'heading' : 'Composite' }
        return render( request, 'pepsite/composite_results.html', context )



#@login_required
def allele_browse( request ):
	alleles = Allele.objects.all().distinct()
	context = { 'alleles' : alleles }
	return render( request, 'pepsite/allele_browse.html', context)

def experiment_browse( request ):
	experiments = Experiment.objects.all().distinct()
	context = { 'experiments' : experiments }
	return render( request, 'pepsite/experiment_browse.html', context)

#@login_required
def protein_browse( request ):
	proteins = Protein.objects.all().distinct()
	context = { 'proteins' : proteins }
	return render( request, 'pepsite/protein_browse.html', context)

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

#@login_required
def model_info( request, model_type, model_id ):
        context = {}
	module = 'pepsite.models'
        if model_type == 'Serotype':
            model_type = 'Allele'
        elif model_type == 'Organism':
            model_type = 'Entity'
	model = getattr(sys.modules[ module ], model_type  )
	instance = get_object_or_404( model, id = model_id )
        if model_type == 'Peptide':
            context['pep_ptms'] = instance.get_ptms
            context['pep_prots'] = instance.get_proteins
	def get_class2( obj ):
	    return obj.__class__
	instance.get_class2 = get_class2
	context['model_type'] = model_type
        context['instance'] = instance
        context['model_id'] = model_id 
	return render( request, 'pepsite/model_info.html', context)

#@login_required
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

@login_required
def upload_ss_form( request ):
    user = request.user
    if request.method == 'POST': # If the form has been submitted...
        form = UploadSSForm(request.POST, request.FILES) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            ul = pepsite.uploaders.Uploads( user = user )
            ss = request.FILES['ss']
            formdata = form.cleaned_data
	    #ul.upload_ss_simple( form.cleaned_data.dict() )
	    ul.preview_ss_simple( formdata )
	    ul.preprocess_ss_simple( ss )
            #request.session['ss'] = ss
            upload_dict = { 'uldict' : ul.uldict, 'uniprot_ids' : ul.uniprot_ids, 'expt_id' : ul.expt_id, 'expt_title' : ul.expt_title, 'publications' : ul.publications, 'public' : ul.public,
                    'antibody_ids' : ul.antibody_ids, 'lodgement_title' : ul.lodgement_title, 'lodgement' : ul.lodgement, 'dataset_nos' : ul.dataset_nos,
                    'instrument_id' : ul.instrument_id, 'cell_line_id' : ul.cell_line_id, 'expt_id' : ul.expt_id, 'lodgement_filename' : ul.lodgement_filename, 'expt_desc' : ul.expt_desc }
            request.session['ul'] = ul.uldict
            request.session['proteins'] = ul.uniprot_ids
            #context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'CellLine', 'search' : True, 'heading' : 'Cell Line'  }
            #return render( request, 'pepsite/upload_preview.html', { 'upload' : ul, 'ss' : ss, 'formdata' : formdata, 'filled_form' : form } ) # Redirect after POST
            return render( request, 'pepsite/upload_preview.html', { 'upload' : ul, 'ss' : ss, 'formdata' : formdata, 'filled_form' : form, 'ul_supp' : upload_dict }  ) # Redirect after POST
	else:
            ul = pepsite.uploaders.Uploads( user = user )
            ss = request.FILES['ss']
            formdata = request.POST
	    #ul.upload_ss_simple( form.cleaned_data.dict() )
	    ul.preview_ss_simple( formdata )
	    ul.preprocess_ss_simple( ss )
            #request.session['ss'] = ss
            upload_dict = { 'uldict' : ul.uldict, 'uniprot_ids' : ul.uniprot_ids, 'expt_id' : ul.expt_id, 'expt_title' : ul.expt_title, 'publications' : ul.publications, 'public' : ul.public,
                    'antibody_ids' : ul.antibody_ids, 'lodgement_title' : ul.lodgement_title, 'lodgement' : ul.lodgement, 'dataset_nos' : ul.dataset_nos,
                    'instrument_id' : ul.instrument_id, 'cell_line_id' : ul.cell_line_id, 'expt_id' : ul.expt_id, 'lodgement_filename' : ul.lodgement_filename, 'expt_desc' : ul.expt_desc  }
            request.session['ul'] = ul.uldict
            request.session['proteins'] = ul.uniprot_ids
            request.session['ul_supp'] = upload_dict
            #return HttpResponse( 'poo' )
            return render( request, 'pepsite/upload_preview.html', { 'upload' : ul, 'ss' : ss, 'formdata' : formdata, 'filled_form' : form, 'ul_supp' : upload_dict }  ) # Redirect after POST
 
    else:
        textform = UploadSSForm()
        context = { 'textform' : textform }
        return render( request, 'pepsite/upload_ss_form.html', context)

@login_required
def upload_multiple_ss_form( request ):
    user = request.user
    if request.method == 'POST': # If the form has been submitted...
        form = UploadMultipleSSForm(request.POST, request.FILES) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            ul = pepsite.uploaders.Uploads( user = user )
            ss = request.FILES.getlist( 'mfiles' )
            formdata = form.cleaned_data
	    #ul.upload_ss_simple( form.cleaned_data.dict() )
	    ul.preview_ss_simple( formdata )
	    ul.preprocess_multiple_simple( ss )
            upload_dict = { 'uldict' : ul.uldict, 'uniprot_ids' : ul.uniprot_ids, 'expt_id' : ul.expt_id, 'expt_title' : ul.expt_title, 'publications' : ul.publications, 'public' : ul.public,
                    'antibody_ids' : ul.antibody_ids, 'lodgement_title' : ul.lodgement_title, 'lodgement' : ul.lodgement, 'dataset_nos' : ul.dataset_nos,
                    'instrument_id' : ul.instrument_id, 'cell_line_id' : ul.cell_line_id, 'expt_id' : ul.expt_id, 'ldg_details' : ul.ldg_details,
                    'ldg_ds_mappings' : ul.ldg_ds_mappings, 'expt_desc' : ul.expt_desc }
            request.session['ul'] = ul.uldict
            request.session['proteins'] = ul.uniprot_ids
            request.session['ul_supp'] = upload_dict
            #return HttpResponse( 'poo' )
            return render( request, 'pepsite/upload_preview_multiple.html', { 'upload' : ul, 'ss' : ss, 'formdata' : formdata, 'filled_form' : form, 'ul_supp' : upload_dict }  ) # Redirect after POST
            #request.session['ss'] = ss
            upload_dict = { 'uldict' : ul.uldict, 'uniprot_ids' : ul.uniprot_ids, 'expt_id' : ul.expt_id, 'expt_title' : ul.expt_title, 'publications' : ul.publications, 'public' : ul.public,
                    'antibody_ids' : ul.antibody_ids, 'lodgement_title' : ul.lodgement_title, 'lodgement' : ul.lodgement, 'dataset_nos' : ul.dataset_nos,
                    'instrument_id' : ul.instrument_id, 'cell_line_id' : ul.cell_line_id, 'expt_id' : ul.expt_id }
            request.session['ul'] = ul.uldict
            request.session['proteins'] = ul.uniprot_ids
            #context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'CellLine', 'search' : True, 'heading' : 'Cell Line'  }
            #return render( request, 'pepsite/upload_preview.html', { 'upload' : ul, 'ss' : ss, 'formdata' : formdata, 'filled_form' : form } ) # Redirect after POST
            return render( request, 'pepsite/upload_preview.html', { 'upload' : ul, 'ss' : ss, 'formdata' : formdata, 'filled_form' : form, 'ul_supp' : upload_dict }  ) # Redirect after POST
	else:
            ul = pepsite.uploaders.Uploads( user = user )
            ss = request.FILES.getlist('mfiles')
            formdata = request.POST
	    ul.preview_ss_simple( formdata )
	    ul.preprocess_multiple_simple( ss )
            #return render( request, 'pepsite/formdump.html', { 'ul' : ul, 'ss' : ss, 'formdata' : formdata } )
	    #ul.upload_ss_simple( form.cleaned_data.dict() )
	    #ul.preview_ss_simple( formdata )
	    #ul.preprocess_multiple_simple( ss )
            #request.session['ss'] = ss
            upload_dict = { 'uldict' : ul.uldict, 'uniprot_ids' : ul.uniprot_ids, 'expt_id' : ul.expt_id, 'expt_title' : ul.expt_title, 'publications' : ul.publications, 'public' : ul.public,
                    'antibody_ids' : ul.antibody_ids, 'lodgement_title' : ul.lodgement_title, 'lodgement' : ul.lodgement, 'dataset_nos' : ul.dataset_nos,
                    'instrument_id' : ul.instrument_id, 'cell_line_id' : ul.cell_line_id, 'expt_id' : ul.expt_id, 'ldg_details' : ul.ldg_details,
                    'ldg_ds_mappings' : ul.ldg_ds_mappings, 'expt_desc' : ul.expt_desc }
            request.session['ul'] = ul.uldict
            request.session['proteins'] = ul.uniprot_ids
            request.session['ul_supp'] = upload_dict
            #return HttpResponse( 'poo' )
            return render( request, 'pepsite/upload_preview_multiple.html', { 'upload' : ul, 'ss' : ss, 'formdata' : formdata, 'filled_form' : form, 'ul_supp' : upload_dict }  ) # Redirect after POST
 
    else:
        textform = UploadMultipleSSForm()
        context = { 'textform' : textform }
        return render( request, 'pepsite/multiple_upload.html', context)

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
	    ul.auto_curation(  )
            return render( request, 'pepsite/curation_outcome.html', { 'upload' : ul }  ) # Redirect after POST
	else:
            ul = pepsite.uploaders.Curate( user = user )
            cur = request.FILES['cur']
            formdata = request.POST
	    ul.setup_curation( formdata, cur )
	    ul.auto_curation(  )
            #request.session['ss'] = ss
            #upload_dict = { 'uldict' : ul.uldict, 'uniprot_ids' : ul.uniprot_ids, 'expt_id' : ul.expt_id, 'expt_title' : ul.expt_title, 'publications' : ul.publications, 'public' : ul.public,
            #        'antibody_ids' : ul.antibody_ids, 'lodgement_title' : ul.lodgement_title, 'lodgement' : ul.lodgement, 'dataset_nos' : ul.dataset_nos,
            #        'instrument_id' : ul.instrument_id, 'cell_line_id' : ul.cell_line_id, 'expt_id' : ul.expt_id }
            #request.session['ul'] = ul.uldict
            #request.session['proteins'] = ul.uniprot_ids
            #request.session['ul_supp'] = upload_dict
            #return HttpResponse( 'poo' )
            return render( request, 'pepsite/curation_outcome.html', { 'upload' : ul }  ) # Redirect after POST
 
    else:
        textform = CurationForm(user=user)
        lodgements_avail = True
        textform.fields['ldg'].choices = [ [b.id, '%s from Experiment: %s' %( b.title, b.get_experiment().title )] for b in Lodgement.objects.all() if user.has_perm( 'edit_lodgement', b )]
        if not textform.fields['ldg'].choices:
            lodgements_avail = False
        context = { 'textform' : textform, 'ldz' : lodgements_avail }
        return render( request, 'pepsite/curation_form.html', context)

#@login_required
def compare_expt_form( request ):
    user = request.user
    if request.method == 'POST': # If the form has been submitted...
            form = CompareExptForm(request.POST) # A form bound to the POST data
            expt1 = request.POST['expt1']
            exptz = request.POST.getlist('exptz' )
            #exptz = formdata['exptz']
            context = { 'exptz' : exptz, 'expt1' : expt1  }
            proteins = list(set(Protein.objects.filter( peptide__ion__experiment__id = expt1)))
            expt = get_object_or_404( Experiment, id = expt1 )
            all_exp = [ expt ]
            #publications = expt.get_publications()
            lodgements = Lodgement.objects.filter( dataset__experiment = expt )
            comp_exz = {}
            for ex in exptz:
                ex_obj = get_object_or_404( Experiment, id = ex )
                comp_exz[ ex_obj ] = []
                all_exp.append( ex_obj )
                #publications.append( ex_obj.get_publications() )
            publications = Publication.objects.filter( lodgements__dataset__experiment__in = all_exp ).distinct()
            compare_ds = []
            for exp_cm in comp_exz:
                for ds in exp_cm.dataset_set.all().distinct().order_by('title'):
                    if user.has_perm( 'view_dataset', ds ):
                        compare_ds.append( ds )
                        comp_exz[ exp_cm ].append( ds )
            if not( len(lodgements)):
                lodgements = False
            s1 = ExptArrayAssemble()
            rows = s1.get_peptide_array_from_protein_expt( proteins, expt, user, compare = True, comparators = compare_ds, cutoffs=True )
            return render( request, 'pepsite/compare_expt_results.html', {"proteins": proteins, 'expt' : expt, 'lodgements' : lodgements, 'publications' : publications, 'rows' : rows, 'paginate' : False, 'expt_cm' : comp_exz, 'compare_ds' : compare_ds  })
    else:
        compare_form = CompareExptForm()
        context = { 'compare_form' : compare_form }
        return render( request, 'pepsite/compare_expt_form.html', context)

def compare_expt_form_ajax( request ):
    user = request.user
    if request.GET.items(): # If the form has been submitted...
        form = CompareExptForm(request.GET) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            
	    expt1 = form.cleaned_data['expt1'] 
	    exptz = form.cleaned_data['exptz'] 
            print 'exptz =', exptz
            exptz2 = [ int(b) for b in exptz ]
            expt = get_object_or_404( Experiment, id = expt1 )
            all_exp = [ expt ]
            lodgements = Lodgement.objects.filter( dataset__experiment = expt )
            for ex in exptz:
                ex_obj = get_object_or_404( Experiment, id = ex )
                all_exp.append( ex_obj )
            publications = Publication.objects.filter( lodgements__dataset__experiment__in = all_exp ).distinct()
            if not( len(lodgements)):
                lodgements = False
            return render( request, 'pepsite/render_compare_expt_results_ajax.html', { 'expt' : expt, 'expt1' : expt1, 'exptz' : exptz2, 'lodgements' : lodgements, 'publications' : publications  })
            exptz2 = [ int(b) for b in exptz ]
            expt = get_object_or_404( Experiment, id = expt1 )
            all_exp = [ expt ]
            lodgements = Lodgement.objects.filter( dataset__experiment = expt )
            for ex in exptz:
                ex_obj = get_object_or_404( Experiment, id = ex )
                all_exp.append( ex_obj )
            publications = Publication.objects.filter( lodgements__dataset__experiment__in = all_exp ).distinct()
            if not( len(lodgements)):
                lodgements = False
            return render( request, 'pepsite/render_compare_expt_results_ajax.html', { 'expt' : expt, 'expt1' : expt1, 'exptz' : exptz2, 'lodgements' : lodgements, 'publications' : publications  })
	else:
            context = {}
            for f in form.fields.keys():
                if f in form.data.keys():
                    context[f] = form.data.getlist(f)
                else:
                    context[f] = form.fields[f].initial
	    expt1 = context['expt1'][0]
	    exptz = context['exptz']
            exptz2 = [ int(b) for b in exptz ]
            print 'invalid exptz =', exptz
            expt = get_object_or_404( Experiment, id = expt1 )
            all_exp = [ expt ]
            lodgements = Lodgement.objects.filter( dataset__experiment = expt )
            for ex in exptz:
                ex_obj = get_object_or_404( Experiment, id = ex )
                all_exp.append( ex_obj )
            publications = Publication.objects.filter( lodgements__dataset__experiment__in = all_exp ).distinct()
            if not( len(lodgements)):
                lodgements = False
            return render( request, 'pepsite/render_compare_expt_results_ajax.html', { 'expt' : expt, 'expt1' : expt1, 'exptz' : exptz2, 'lodgements' : lodgements, 'publications' : publications  })
    elif request.method == 'POST': # If the form has been submitted...
            form = CompareExptForm(request.POST) # A form bound to the POST data
            expt1 = request.POST['expt1']
            exptz = request.POST.getlist('exptz' )
            exptz2 = [ int(b) for b in exptz ]
            #exptz = formdata['exptz']
            context = { 'exptz' : exptz, 'expt1' : expt1  }
            #proteins = Protein.objects.filter( peptide__ion__experiment__id = expt1).distinct()
            #protein_ids = [b.id for b in proteins][:25]
            expt = get_object_or_404( Experiment, id = expt1 )
            all_exp = [ expt ]
            #publications = expt.get_publications()
            lodgements = Lodgement.objects.filter( dataset__experiment = expt )
            #comp_exz = {}
            for ex in exptz:
                ex_obj = get_object_or_404( Experiment, id = ex )
                #comp_exz[ ex_obj ] = []
                all_exp.append( ex_obj )
            publications = Publication.objects.filter( lodgements__dataset__experiment__in = all_exp ).distinct()
            if not( len(lodgements)):
                lodgements = False
            return render( request, 'pepsite/render_compare_expt_results_ajax.html', { 'expt' : expt, 'expt1' : expt1, 'exptz' : exptz2, 'lodgements' : lodgements, 'publications' : publications  })
    else:
        compare_form = CompareExptForm()
        context = { 'compare_form' : compare_form }
        return render( request, 'pepsite/compare_expt_form_ajax.html', context)

def comparison_peptides_render( request ):
  user = request.user
  #return HttpResponse( 'Hello!' )
  if request.POST.has_key( 'expt' ) and request.POST.has_key( 'exptz[]' ):
            
            expt1 = request.POST['expt']
            expt = get_object_or_404( Experiment, id = expt1 )
            exptz = request.POST.getlist('exptz[]' )
            print 'expt =', expt.id, 'exptz =', exptz
            #return HttpResponse( 'Something!!!' + str( request.POST.keys() )  )
            #exptz = formdata['exptz']
            s1 = ExptArrayAssemble()
            rows = s1.mkiii_compare_query( expt1, exptz, user.id ) 
            return render( request, 'pepsite/compare_peptides_render.html', { 'rows' : rows, 'compare_ds' : s1.compare_ds, 'expt' : expt  })
            context = { 'exptz' : exptz, 'expt1' : expt1  }
            proteins = Protein.objects.filter( peptide__ion__experiment__id = expt1).distinct()
            protein_ids = [b.id for b in proteins][:25]
            expt = get_object_or_404( Experiment, id = expt1 )
            all_exp = [ expt ]
            #publications = expt.get_publications()
            lodgements = Lodgement.objects.filter( dataset__experiment = expt )
            comp_exz = {}
            for ex in exptz:
                ex_obj = get_object_or_404( Experiment, id = ex )
                comp_exz[ ex_obj ] = []
                all_exp.append( ex_obj )
                #publications.append( ex_obj.get_publications() )
            publications = Publication.objects.filter( lodgements__dataset__experiment__in = all_exp ).distinct()
            compare_ds = []
            for exp_cm in comp_exz:
                for ds in exp_cm.dataset_set.all().distinct().order_by('title'):
                    if user.has_perm( 'view_dataset', ds ):
                        compare_ds.append( ds )
                        comp_exz[ exp_cm ].append( ds )
            if not( len(lodgements)):
                lodgements = False
            s1 = ExptArrayAssemble()
            rows = s1.get_peptide_array_from_protein_expt( proteins, expt, user, compare = True, comparators = compare_ds, cutoffs=True )
            return render( request, 'pepsite/compare_peptides_render.html', {"proteins": proteins, 'expt' : expt, 'expt1' : expt1, 'exptz' : exptz, 'protein_ids' : protein_ids, 'lodgements' : lodgements, 'publications' : publications, 'rows' : rows, 'paginate' : False, 'expt_cm' : comp_exz, 'compare_ds' : compare_ds  })
  else:
      return HttpResponse( 'Nothing!!!' + str( request.POST.keys() )  )


def render_full_comparison_ajax(request):
    """docstring for render_full_comparison_ajax"""
    pass


def clean_compare_expt_form( request ):
    user = request.user
    if request.method == 'POST': # If the form has been submitted...
            form = CompareExptForm(request.POST) # A form bound to the POST data
            expt1 = request.POST['expt1']
            exptz = request.POST.getlist('exptz' )
            #exptz = formdata['exptz']
            context = { 'exptz' : exptz, 'expt1' : expt1  }
            proteins = list(set(Protein.objects.filter( peptide__ion__experiment__id = expt1)))
            expt = get_object_or_404( Experiment, id = expt1 )
            all_exp = [ expt ]
            #publications = expt.get_publications()
            lodgements = Lodgement.objects.filter( dataset__experiment = expt )
            comp_exz = {}
            for ex in exptz:
                ex_obj = get_object_or_404( Experiment, id = ex )
                comp_exz[ ex_obj ] = []
                all_exp.append( ex_obj )
                #publications.append( ex_obj.get_publications() )
            publications = Publication.objects.filter( lodgements__dataset__experiment__in = all_exp ).distinct()
            compare_ds = []
            for exp_cm in comp_exz:
                for ds in exp_cm.dataset_set.all().distinct().order_by('title'):
                    if user.has_perm( 'view_dataset', ds ):
                        compare_ds.append( ds )
                        comp_exz[ exp_cm ].append( ds )
            if not( len(lodgements)):
                lodgements = False
            s1 = ExptArrayAssemble()
            rows = s1.get_peptide_array_from_protein_expt( proteins, expt, user, compare = True, comparators = compare_ds, cutoffs=True )
            return render( request, 'pepsite/compare_expt_results.html', {"proteins": proteins, 'expt' : expt, 'lodgements' : lodgements, 'publications' : publications, 'rows' : rows, 'paginate' : False, 'expt_cm' : comp_exz, 'compare_ds' : compare_ds  })
    else:
        compare_form = CompareExptForm()
        context = { 'compare_form' : compare_form }
        return render( request, 'pepsite/compare_expt_form.html', context)

@login_required
def commit_upload_ss( request ):
    """
    """
    user = request.user
    elems = request.session['ul_supp']
    if request.method == 'POST':
        keys = request.POST.keys()
        ul = pepsite.uploaders.Uploads( user = user )
        ul.repopulate( elems )
        ul.add_cutoff_mappings( request.POST )
        #with open( '/home/rimmer/praccie/hdome/background/trial_ul_01.pickle', 'wb' ) as f:
        #    pickle.dump( ul, f )
        context = { 'data' : request.POST['data'], 'ul' : ul, 'keys' : keys }
        ul.get_protein_metadata(  )
        ul.prepare_upload_simple( )
        ul.upload_simple()
        return render( request, 'pepsite/ss_uploading.html', context)
    else:
        textform = UploadSSForm()
        context = { 'textform' : textform }
        return render( request, 'pepsite/upload_ss_form.html', context)

@login_required
def commit_upload_multiple_ss( request ):
    """
    """
    user = request.user
    elems = request.session['ul_supp']
    if request.method == 'POST':
        keys = request.POST.keys()
        ul = pepsite.uploaders.Uploads( user = user )
        ul.repopulate( elems )
        ul.add_cutoff_mappings_multiple( request.POST )
        #with open( '/home/rimmer/praccie/hdome/background/trial_ul_01.pickle', 'wb' ) as f:
        #    pickle.dump( ul, f )
        context = { 'data' : request.POST['data'], 'ul' : ul, 'keys' : keys }
        ul.get_protein_metadata(  )
        ul.prepare_upload_simple_multiple( )
        ul.upload_simple_multiple()
        return render( request, 'pepsite/ss_uploading.html', context)
    else:
        textform = UploadSSForm()
        context = { 'textform' : textform }
        return render( request, 'pepsite/upload_ss_form.html', context)


#@login_required
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
            context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'CellLine', 'search' : True, 'heading' : 'Cell Line'  }
            return render( request, 'pepsite/searched_expts.html', context ) # Redirect after POST
	else:
            textform = TextOnlyForm()
            context = { 'search_message' : True, 'textform' : textform }
            return render( request, 'pepsite/ptm_search.html', context ) # Redirect after POST

    else:
        textform = TextOnlyForm()
        context = { 'textform' : textform }
        return render( request, 'pepsite/cell_line_search.html', context)

#@login_required
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

#@login_required
def mass_search( request ):
    user = request.user
    if request.GET.items(): # If the form has been submitted...
        form = MassSearchForm(request.GET) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
	    target_input = form.cleaned_data['target_input'] 
	    tolerance = form.cleaned_data['tolerance'] 
            context = { 'target_input' : target_input, 'tolerance' : tolerance }
	    s1 = MassSearch()
	    ides = s1.get_unique_peptide_ides( 'mass',  [float(target_input), float(tolerance), user] )
	    #ides = s1.get_ides_from_mass( target_input, tolerance )
            desc = u'mass %s \u00B1 %s' % ( target_input, tolerance ) 
            context = { 'rows' : ides, 'search' : True, 'query_on' : 'Peptide', 'text_input' : desc }
	    #context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'Allele', 'search' : True }
            return render( request, 'pepsite/found_peptides.html', context ) # Redirect after POST
	else:
            context = {}
            for f in form.fields.keys():
                if f in form.data.keys():
                    context[f] = form.data[f]
                else:
                    context[f] = form.fields[f].initial
	    target_input = context['target_input']
	    tolerance = context['tolerance'] 
            context = { 'target_input' : target_input, 'tolerance' : tolerance }
	    s1 = MassSearch()
	    ides = s1.get_unique_peptide_ides( 'mass', [ float(target_input), float(tolerance), user ] )
	    #ides = s1.get_ides_from_mass( target_input, tolerance )
            desc = u'mass %s \u00B1 %s' % ( target_input, tolerance ) 
            context = { 'rows' : ides, 'search' : True, 'query_on' : 'Peptide', 'text_input' : desc }
	    #target = request.get['target_input']
	    #context = { 'msg' : text_input }
            return render( request, 'pepsite/found_peptides.html', context ) # Redirect after POST

    else:
        textform = MassSearchForm()
        context = { 'massform' : textform }
        return render( request, 'pepsite/mass_search.html', context)

def mz_search( request ):
    user = request.user
    if request.GET.items(): # If the form has been submitted...
        form = MzSearchForm(request.GET) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
	    target_input = form.cleaned_data['target_input'] 
	    tolerance = form.cleaned_data['tolerance'] 
            context = { 'target_input' : target_input, 'tolerance' : tolerance }
	    s1 = MassSearch()
	    ides = s1.get_unique_peptide_ides( 'mz', [float(target_input), float(tolerance), user] )
	    #ides = s1.get_ides_from_mass( target_input, tolerance )
            desc = u'm/z %s \u00B1 %s' % ( target_input, tolerance ) 
            context = { 'rows' : ides, 'search' : True, 'query_on' : 'Peptide', 'text_input' : desc }
	    #context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'Allele', 'search' : True }
            return render( request, 'pepsite/found_peptides.html', context ) # Redirect after POST
	else:
            context = {}
            for f in form.fields.keys():
                if f in form.data.keys():
                    context[f] = form.data[f]
                else:
                    context[f] = form.fields[f].initial
	    target_input = context['target_input']
	    tolerance = context['tolerance'] 
            context = { 'target_input' : target_input, 'tolerance' : tolerance }
	    s1 = MassSearch()
	    ides = s1.get_unique_peptide_ides( 'mz', [float(target_input), float(tolerance), user] )
	    #ides = s1.get_ides_from_mass( target_input, tolerance )
            desc = u'm/z %s \u00B1 %s' % ( target_input, tolerance ) 
            context = { 'rows' : ides, 'search' : True, 'query_on' : 'Peptide', 'text_input' : desc }
	    #target = request.get['target_input']
	    #context = { 'msg' : text_input }
            return render( request, 'pepsite/found_peptides.html', context ) # Redirect after POST

    else:
        textform = MzSearchForm()
        context = { 'massform' : textform }
        return render( request, 'pepsite/mz_search.html', context)

def sequence_search( request ):
    user = request.user
    if request.GET.items(): # If the form has been submitted...
        form = SequenceSearchForm(request.GET) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
	    target_input = form.cleaned_data['target_input'] 
	    #tolerance = form.cleaned_data['tolerance'] 
            context = { 'target_input' : target_input } #, 'tolerance' : tolerance }
	    s1 = MassSearch()
	    ides = s1.get_unique_peptide_ides( 'sequence', [target_input, user] )
	    #ides = s1.get_ides_from_mass( target_input, tolerance )
            desc = u'sequence %s' % ( target_input.upper() ) 
            context = { 'rows' : ides, 'search' : True, 'query_on' : 'Peptide', 'text_input' : desc }
	    #context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'Allele', 'search' : True }
            return render( request, 'pepsite/found_peptides.html', context ) # Redirect after POST
	else:
            context = {}
            for f in form.fields.keys():
                if f in form.data.keys():
                    context[f] = form.data[f]
                else:
                    context[f] = form.fields[f].initial
	    target_input = context['target_input']
	    #tolerance = context['tolerance'] 
            context = { 'target_input' : target_input } #, 'tolerance' : tolerance }
	    s1 = MassSearch()
	    ides = s1.get_unique_peptide_ides_from_mz( target_input, user )
	    #ides = s1.get_ides_from_mass( target_input, tolerance )
            desc = u'sequence %s' % ( target_input.upper() ) 
            context = { 'rows' : ides, 'search' : True, 'query_on' : 'Peptide', 'text_input' : desc }
	    #target = request.get['target_input']
	    #context = { 'msg' : text_input }
            return render( request, 'pepsite/found_peptides.html', context ) # Redirect after POST

    else:
        textform = SequenceSearchForm()
        context = { 'massform' : textform }
        return render( request, 'pepsite/sequence_search.html', context)

#@login_required
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
def allele_results( request ):
	context = { 'msg' : 'goodbye' }
	return render( request, 'pepsite/allele_results.html', context)

#@login_required
def trial_table( request ):
	context = { 'msg' : 'goodbye' }
	return render( request, 'pepsite/eg_tablesort.html', context)

#@login_required
def cell_line_expts( request, cell_line_id ):
	cl1 = CellLine.objects.get( id = cell_line_id )
	text_input = cl1.name
	expts = Experiment.objects.filter( cell_line = cl1 )
        context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'CellLine', 'query_obj' : cl1  }
	return render( request, 'pepsite/searched_expts.html', context)

#@login_required
def gene_expts( request, gene_id ):
	g1 = Gene.objects.get( id = gene_id )
	text_input = g1.name
	expts = Experiment.objects.filter( cell_line__alleles__gene = g1, antibody__alleles__gene = g1 ).distinct()
        context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'Gene', 'query_obj' : g1  }
	return render( request, 'pepsite/searched_expts.html', context)

#@login_required
def entity_expts( request, entity_id ):
	en1 = Entity.objects.get( id = entity_id )
	text_input = en1.common_name
	expts = Experiment.objects.filter( cell_line__individuals__entity = en1 )
        context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'Entity', 'query_obj' : en1  }
	if en1.isOrganism:
	    context['query_on'] = 'Organism'
	return render( request, 'pepsite/searched_expts.html', context)


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

#@login_required
def ptm_peptides( request, ptm_id ):
    user = request.user
    ptm1 = get_object_or_404( Ptm, id = ptm_id )
    text_input = ptm1.description
    s1 = MassSearch()
    ides = s1.get_peptide_array_from_ptm( ptm1, user )
    context = { 'text_input' : text_input, 'query_on' : 'Ptm', 'query_obj' : ptm1, 'rows' : ides, 'search' : False }
    return render( request, 'pepsite/found_peptides.html', context)

#@login_required
def protein_peptides( request, protein_id ):
    user = request.user
    prot1 = get_object_or_404( Protein, id = protein_id )
    text_input = prot1.description
    s1 = MassSearch()
    ides = s1.get_peptide_array_from_protein( prot1, user )
    context = { 'text_input' : text_input, 'query_on' : 'Protein', 'query_obj' : prot1, 'rows' : ides, 'search' : False }
    return render( request, 'pepsite/found_peptides.html', context)

#@login_required
def peptide_peptides( request, peptide_id ):
    user = request.user
    pep = get_object_or_404( Peptide, id = peptide_id )
    text_input = pep.sequence
    s1 = MassSearch()
    ides = s1.get_peptide_array_from_peptide( pep, user )
    context = { 'text_input' : text_input, 'query_on' : 'Peptide', 'query_obj' : pep, 'rows' : ides }
    return render( request, 'pepsite/found_peptides.html', context)

#@login_required
def allele_expts( request, allele_id ):
    al1 = get_object_or_404( Allele, id = allele_id )
    text_input = al1.code
    expts = Experiment.objects.filter( cell_line__alleles = al1, antibody__alleles = al1 )
    context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'Allele', 'query_obj' : al1 }
    if al1.isSer:
	context['query_on'] = 'Serotype'
    return render( request, 'pepsite/searched_expts.html', context)

#@login_required
def protein_full_listing( request, protein_id ):
    prot = get_object_or_404( Protein, id = protein_id )
    s1 = ProteinSearch()
    expts = s1.get_experiments_from_protein( prot )
    context = { 'msg' : expts, 'protein' : prot }
    return render( request, 'pepsite/protein_full_listing.html', context)

#@login_required
def expt( request, expt_id ):
    expt = get_object_or_404( Experiment, id = expt_id )
    s1 = ExptAssemble()
    details = s1.get_peptide_info( expt )
    alleles = s1.get_common_alleles( expt )
    context = { 'details' : details, 'expt' : expt, 'alleles' : alleles }
    return render( request, 'pepsite/expt.html', context)


#@login_required
def expt3( request, expt_id ):
    proteins = set(Protein.objects.filter( peptide__ion__experiments__id = expt_id))

    context = { 'proteins' : proteins,  }
    return render( request, 'pepsite/expt2.html', context)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#@login_required
def expt2( request, expt_id ):
  user = request.user
  if not request.POST.has_key( 'full_list' ) :
    proteins = Protein.objects.filter( peptide__ion__experiment__id = expt_id).distinct()
    expt = get_object_or_404( Experiment, id = expt_id )
    publications = expt.get_publications()
    lodgements = Lodgement.objects.filter( dataset__experiment = expt )
    if not( len(lodgements)):
        lodgements = False
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
    s1 = ExptArrayAssemble()
    rows = s1.get_peptide_array_from_protein_expt( proteins, expt, user, cutoffs = True )
    return render( request, 'pepsite/expt2.html', {"proteins": proteins, 'expt' : expt, 'lodgements' : lodgements, 'publications' : publications, 'rows' : rows, 'paginate' : True })
  else:
    proteins = list(set(Protein.objects.filter( peptide__ion__experiment__id = expt_id)))
    expt = get_object_or_404( Experiment, id = expt_id )
    publications = expt.get_publications()
    lodgements = Lodgement.objects.filter( dataset__experiment = expt )
    if not( len(lodgements)):
        lodgements = False
    s1 = ExptArrayAssemble()
    rows = s1.get_peptide_array_from_protein_expt( proteins, expt, user, cutoffs=True )
    return render( request, 'pepsite/expt2.html', {"proteins": proteins, 'expt' : expt, 'lodgements' : lodgements, 'publications' : publications, 'rows' : rows, 'paginate' : False })

def expt2_ajax( request, expt_id ):
    user = request.user
    #initial_quota = 25
    #proteins = Protein.objects.filter( peptide__ion__experiment__id = expt_id).distinct()
    expt = get_object_or_404( Experiment, id = expt_id )
    publications = expt.get_publications()
    lodgements = Lodgement.objects.filter( dataset__experiment = expt )
    if not( len(lodgements)):
        lodgements = False
    #paginator = Paginator(proteins, 25 ) # Show 25 contacts per page

    #page = request.GET.get('page')
    #try:
    #    proteins = paginator.page(page)
    #except PageNotAnInteger:
    #    # If page is not an integer, deliver first page.
    #    proteins = paginator.page(1)
    #except EmptyPage:
    #    # If page is out of range (e.g. 9999), deliver last page of results.
    #    proteins = paginator.page(paginator.num_pages)
    #s1 = ExptArrayAssemble()
    #rows = s1.get_peptide_array_from_protein_expt( proteins[:initial_quota], expt, user, cutoffs = True )
    #protein_ids_total = [ b.id for b in proteins ]
    #protein_ids_initial = protein_ids_total[:][:initial_quota] 
    #for pid in protein_ids_total:
    #    if pid in protein_ids_initial:
    #        protein_ids_total.remove(pid)
    #protein_ids = protein_ids_total[initial_quota:] 
    return render( request, 'pepsite/expt2_ajax.html', { 'expt' : expt, 'lodgements' : lodgements, 'publications' : publications, 'paginate' : False })

def peptides_render( request, expt_id ):
    user = request.user
    print 'user = ', user, user.id, user.username
    if user.id is None:
        user = User.objects.get( id = -1 )
    print 'user = ', user, user.id, user.username
    #return HttpResponse( 'Hello!' )
    #if request.POST.has_key( 'expt_id' ):
    proteins = Protein.objects.filter( peptide__ion__experiment__id = expt_id ).distinct()
    #print protein_ids
    #proteins = Protein.objects.filter( id__in = protein_ids).distinct()
    expt = get_object_or_404( Experiment, id = expt_id )
    #publications = expt.get_publications()
    #lodgements = Lodgement.objects.filter( dataset__experiment = expt )
    #if not( len(lodgements)):
    #    lodgements = False
    #paginator = Paginator(proteins, 25 ) # Show 25 contacts per page

    #page = request.GET.get('page')
    #try:
    #    proteins = paginator.page(page)
    #except PageNotAnInteger:
    #    # If page is not an integer, deliver first page.
    #    proteins = paginator.page(1)
    #except EmptyPage:
    #    # If page is out of range (e.g. 9999), deliver last page of results.
    #    proteins = paginator.page(paginator.num_pages)
    s1 = ExptArrayAssemble()
    #rows = s1.get_peptide_array_from_protein_expt( proteins, expt, user, cutoffs = True )
    rows = s1.mkiii_expt_query(  expt.id, user.id )
    print len(rows)
    #protein_ids = [ b.id for b in proteins ]
    return render( request, 'pepsite/peptides_render_rapid.html', { 'expt' : expt, 'rows' : rows }) 
    return HttpResponse( [ b['expt'].title for b in rows] )
    return HttpResponse( [ b['expt'].title for b in rows] )
    #else:
    #  return HttpResponse( 'Nothing!!!' + str( request.POST.keys() )  )





#@login_required
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


#@login_required
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


#@login_required
def footer( request ):
    return render( request, 'pepsite/footer.html', {})

#@login_required
def nav_buttons_allele( request ):
    return render( request, 'pepsite/nav_buttons_allele.html', {})

#@login_required
def nav_buttons( request  ):
    return render( request, 'pepsite/nav_buttons.html', {})
