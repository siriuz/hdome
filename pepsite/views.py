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

@login_required
def index( request ):
	return render( request, 'pepsite/index.html', {})

@login_required
def formdump( request ):
        context = { 'post' : request.POST.dict() }
	return render( request, 'pepsite/formdump.html', context )

@login_required
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



@login_required
def allele_browse( request ):
	alleles = Allele.objects.all().distinct()
	context = { 'alleles' : alleles }
	return render( request, 'pepsite/allele_browse.html', context)

@login_required
def protein_browse( request ):
	proteins = Protein.objects.all().distinct()
	context = { 'proteins' : proteins }
	return render( request, 'pepsite/protein_browse.html', context)

@login_required
def cell_line_browse( request ):
	cell_lines = CellLine.objects.all().distinct()
	context = { 'cell_lines' : cell_lines }
	return render( request, 'pepsite/cell_line_browse.html', context)

@login_required
def cell_line_tissue_browse( request ):
	cell_lines = CellLine.objects.all(  ).distinct().order_by( 'tissue_type' )
	context = { 'cell_lines' : cell_lines }
	return render( request, 'pepsite/cell_line_tissue_browse.html', context)

@login_required
def model_info( request, model_type, model_id ):
	module = 'pepsite.models'
        if model_type == 'Serotype':
            model_type = 'Allele'
        if model_type == 'Organism':
            model_type = 'Entity'
	model = getattr(sys.modules[ module ], model_type  )
	instance = get_object_or_404( model, id = model_id )
	def get_class2( obj ):
	    return obj.__class__
	instance.get_class2 = get_class2
	context = { 'model_type' : model_type, 'instance' : instance, 'model_id' : model_id }
	return render( request, 'pepsite/model_info.html', context)

@login_required
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
            upload_dict = { 'uldict' : ul.uldict, 'uniprot_ids' : ul.uniprot_ids, 'expt_id' : ul.expt_id, 'expt_title' : ul.expt_title, 'publications' : ul.publications,
                    'antibody_ids' : ul.antibody_ids, 'lodgement_title' : ul.lodgement_title, 'lodgement' : ul.lodgement, 'dataset_nos' : ul.dataset_nos,
                    'instrument_id' : ul.instrument_id, 'cell_line_id' : ul.cell_line_id }
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
            upload_dict = { 'uldict' : ul.uldict, 'uniprot_ids' : ul.uniprot_ids, 'expt_id' : ul.expt_id, 'expt_title' : ul.expt_title, 'publications' : ul.publications,
                    'antibody_ids' : ul.antibody_ids, 'lodgement_title' : ul.lodgement_title, 'lodgement' : ul.lodgement, 'dataset_nos' : ul.dataset_nos,
                    'instrument_id' : ul.instrument_id, 'cell_line_id' : ul.cell_line_id }
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
def commit_upload_ss( request ):
    """
    """
    user = request.user
    elems = request.session['ul_supp']
    if request.method == 'POST':
        ul = pepsite.uploaders.Uploads( user = user )
        ul.repopulate( elems )
        context = { 'data' : request.POST['data'], 'ul' : ul }
        ul.get_protein_metadata(  )
        ul.prepare_upload_simple( )
        ul.upload_simple()
        return render( request, 'pepsite/ss_uploading.html', context)
    else:
        textform = UploadSSForm()
        context = { 'textform' : textform }
        return render( request, 'pepsite/upload_ss_form.html', context)


@login_required
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

@login_required
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

@login_required
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

@login_required
def mass_search( request ):
    user = request.user
    if request.GET.items(): # If the form has been submitted...
        form = MassSearchForm(request.GET) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
	    target_input = form.cleaned_data['target_input'] 
	    tolerance = form.cleaned_data['tolerance'] 
            context = { 'target_input' : target_input, 'tolerance' : tolerance }
	    s1 = MassSearch()
	    ides = s1.get_unique_peptide_ides_from_mass( float(target_input), float(tolerance), user )
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
	    ides = s1.get_unique_peptide_ides_from_mass( float(target_input), float(tolerance), user )
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

@login_required
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

@login_required
def allele_results( request ):
	context = { 'msg' : 'goodbye' }
	return render( request, 'pepsite/allele_results.html', context)

@login_required
def trial_table( request ):
	context = { 'msg' : 'goodbye' }
	return render( request, 'pepsite/eg_tablesort.html', context)

@login_required
def cell_line_expts( request, cell_line_id ):
	cl1 = CellLine.objects.get( id = cell_line_id )
	text_input = cl1.name
	expts = Experiment.objects.filter( cell_line = cl1 )
        context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'CellLine', 'query_obj' : cl1  }
	return render( request, 'pepsite/searched_expts.html', context)

@login_required
def gene_expts( request, gene_id ):
	g1 = Gene.objects.get( id = gene_id )
	text_input = g1.name
	expts = Experiment.objects.filter( cell_line__alleles__gene = g1, antibody__alleles__gene = g1 ).distinct()
        context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'Gene', 'query_obj' : g1  }
	return render( request, 'pepsite/searched_expts.html', context)

@login_required
def entity_expts( request, entity_id ):
	en1 = Entity.objects.get( id = entity_id )
	text_input = en1.common_name
	expts = Experiment.objects.filter( cell_line__individuals__entity = en1 )
        context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'Entity', 'query_obj' : en1  }
	if en1.isOrganism:
	    context['query_on'] = 'Organism'
	return render( request, 'pepsite/searched_expts.html', context)


@login_required
def peptide_expts( request, peptide_id ):
    peptide = get_object_or_404( Peptide, id = peptide_id )
    text_input = peptide.sequence
    expts = Experiment.objects.filter( ion__peptides = peptide )
    context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'Peptide', 'query_obj' : peptide  }
    return render( request, 'pepsite/searched_expts.html', context)

@login_required
def antibody_expts( request, antibody_id ):
    ab1 = get_object_or_404( Antibody, id = antibody_id )
    text_input = ab1.name
    expts = Experiment.objects.filter( antibody = ab1 )
    context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'Antibody', 'query_obj' : ab1  }
    return render( request, 'pepsite/searched_expts.html', context)

@login_required
def ptm_expts( request, ptm_id ):
    ptm1 = get_object_or_404( Ptm, id = ptm_id )
    text_input = ptm1.description
    expts = Experiment.objects.filter( ion__idestimate__ptm = ptm1 ).distinct()
    context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'Ptm', 'query_obj' : ptm1 }
    return render( request, 'pepsite/searched_expts.html', context)

@login_required
def ptm_peptides( request, ptm_id ):
    user = request.user
    ptm1 = get_object_or_404( Ptm, id = ptm_id )
    text_input = ptm1.description
    s1 = MassSearch()
    ides = s1.get_peptide_array_from_ptm( ptm1, user )
    context = { 'text_input' : text_input, 'query_on' : 'Ptm', 'query_obj' : ptm1, 'rows' : ides, 'search' : False }
    return render( request, 'pepsite/found_peptides.html', context)

@login_required
def protein_peptides( request, protein_id ):
    user = request.user
    prot1 = get_object_or_404( Protein, id = protein_id )
    text_input = prot1.description
    s1 = MassSearch()
    ides = s1.get_peptide_array_from_protein( prot1, user )
    context = { 'text_input' : text_input, 'query_on' : 'Protein', 'query_obj' : prot1, 'rows' : ides, 'search' : False }
    return render( request, 'pepsite/found_peptides.html', context)

@login_required
def peptide_peptides( request, peptide_id ):
    user = request.user
    pep = get_object_or_404( Peptide, id = peptide_id )
    text_input = pep.sequence
    s1 = MassSearch()
    ides = s1.get_peptide_array_from_peptide( pep, user )
    context = { 'text_input' : text_input, 'query_on' : 'Peptide', 'query_obj' : pep, 'rows' : ides }
    return render( request, 'pepsite/found_peptides.html', context)

@login_required
def allele_expts( request, allele_id ):
    al1 = get_object_or_404( Allele, id = allele_id )
    text_input = al1.code
    expts = Experiment.objects.filter( cell_line__alleles = al1, antibody__alleles = al1 )
    context = { 'msg' : expts, 'text_input' : text_input, 'query_on' : 'Allele', 'query_obj' : al1 }
    if al1.isSer:
	context['query_on'] = 'Serotype'
    return render( request, 'pepsite/searched_expts.html', context)

@login_required
def protein_full_listing( request, protein_id ):
    prot = get_object_or_404( Protein, id = protein_id )
    s1 = ProteinSearch()
    expts = s1.get_experiments_from_protein( prot )
    context = { 'msg' : expts, 'protein' : prot }
    return render( request, 'pepsite/protein_full_listing.html', context)

@login_required
def expt( request, expt_id ):
    expt = get_object_or_404( Experiment, id = expt_id )
    s1 = ExptAssemble()
    details = s1.get_peptide_info( expt )
    alleles = s1.get_common_alleles( expt )
    context = { 'details' : details, 'expt' : expt, 'alleles' : alleles }
    return render( request, 'pepsite/expt.html', context)


@login_required
def expt3( request, expt_id ):
    proteins = set(Protein.objects.filter( peptide__ion__experiments__id = expt_id))

    context = { 'proteins' : proteins,  }
    return render( request, 'pepsite/expt2.html', context)

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def expt2( request, expt_id ):
  user = request.user
  if not ( request.POST.has_key( 'full_list' ) and request.POST['full_list'] ):
    proteins = list(set(Protein.objects.filter( peptide__ion__experiments__id = expt_id)))
    expt = get_object_or_404( Experiment, id = expt_id )
    lodgements = Lodgement.objects.filter( dataset__experiment = expt_id )
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
    rows = s1.get_peptide_array_from_protein_expt( proteins, expt, user )
    return render( request, 'pepsite/expt2.html', {"proteins": proteins, 'expt' : expt, 'lodgements' : lodgements, 'rows' : rows, 'paginate' : True })
  else:
    proteins = list(set(Protein.objects.filter( peptide__ion__experiments__id = expt_id)))
    expt = get_object_or_404( Experiment, id = expt_id )
    lodgements = Lodgement.objects.filter( dataset__experiment = expt_id )
    if not( len(lodgements)):
        lodgements = False
    s1 = ExptArrayAssemble()
    rows = s1.get_peptide_array_from_protein_expt( proteins, expt, user )
    return render( request, 'pepsite/expt2.html', {"proteins": proteins, 'expt' : expt, 'lodgements' : lodgements, 'rows' : rows, 'paginate' : False })



@login_required
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


@login_required
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


@login_required
def footer( request ):
    return render( request, 'pepsite/footer.html', {})

@login_required
def nav_buttons_allele( request ):
    return render( request, 'pepsite/nav_buttons_allele.html', {})

@login_required
def nav_buttons( request  ):
    return render( request, 'pepsite/nav_buttons.html', {})
