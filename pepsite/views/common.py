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
    elif model_type == 'Experiment':
        context['lodgements'] = instance.get_lodgements
    def get_class2( obj ):
        return obj.__class__
    instance.get_class2 = get_class2
    context['model_type'] = model_type
    context['instance'] = instance
    context['model_id'] = model_id
    return render( request, 'pepsite/model_info.html', context)

def compare_expt_form_ajax( request ):
    user = request.user
    if request.GET.items(): # If the form has been submitted...
        form = CompareExptForm(request.GET) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            
            expt1 = form.cleaned_data['expt1']
            exptz = form.cleaned_data['exptz']
            print 'exptz =', exptz
            exptz2 = [ int(b) for b in exptz ]
            exptz2_objs = Experiment.objects.filter( id__in = exptz2 ).distinct().order_by('title')
            print 'invalid exptz =', exptz
            expt = get_object_or_404( Experiment, id = expt1 )
            all_exp = [ expt ]
            lodgements = Lodgement.objects.filter( dataset__experiment = expt )
            for ex in exptz:
                ex_obj = get_object_or_404( Experiment, id = ex )
                all_exp.append( ex_obj )
            publications = Publication.objects.filter( lodgements__dataset__experiment__in = all_exp ).distinct()
            complete = True
            if not( len(lodgements)):
                lodgements = False
            message2 = '<p><h1 class=\"text-danger\">You do not have permission to view comparison Experiments:<ul>'
            for experiment in exptz2_objs:
                if ( not user.has_perm( 'view_experiment', experiment ) ):
                    complete = False
                    message2 += '<li class=\"text-info\">' + experiment.title + '</li>'
                    exptz2_objs = exptz2_objs.exclude( id = experiment.id )
            exptz3 = [b.id for b in exptz2_objs ]
            message2 += '</ul></h1></p>'
            view_disallowed = False
            if user.has_perm('pepsite.view_experiment_disallowed'):
                view_disallowed = True
            if ( not user.has_perm( 'view_experiment', expt ) ):
                message = '<h1 class=\"text-danger\"><p>You do not have permission to view primary Experiment: <span class=\"text-info\">%s</span>' % ( expt.title )
                if not complete:
                    message += "</h1></p>" + message2
                return render( request, 'pepsite/render_compare_expt_results_ajax.html', { 'expt' : expt, 'expt1' : expt1, 'view_disallowed' : view_disallowed, 'exptz' : exptz3, 'lodgements' : lodgements, 'publications' : publications, 'message' : message, 'complete' : complete, 'exptz_objs' : exptz2_objs  })
            return render( request, 'pepsite/render_compare_expt_results_ajax.html', { 'complete' : complete, 'view_disallowed' : view_disallowed, 'expt' : expt, 'expt1' : expt1, 'exptz' : exptz3, 'lodgements' : lodgements, 'publications' : publications, 'exptz_objs' : exptz2_objs   })
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
            #exptz2_objs = [ Experiment.objects.get( id = b ) for b in exptz2 ]
            exptz2_objs = Experiment.objects.filter( id__in = exptz2 ).distinct().order_by('title')
            print 'invalid exptz =', exptz
            expt = get_object_or_404( Experiment, id = expt1 )
            all_exp = [ expt ]
            lodgements = Lodgement.objects.filter( dataset__experiment = expt )
            for ex in exptz:
                ex_obj = get_object_or_404( Experiment, id = ex )
                all_exp.append( ex_obj )
            publications = Publication.objects.filter( lodgements__dataset__experiment__in = all_exp ).distinct()
            complete = True
            if not( len(lodgements)):
                lodgements = False
            message2 = '<p><h1 class=\"text-danger\">You do not have permission to view comparison Experiments:<ul>'
            for experiment in exptz2_objs:
                if ( not user.has_perm( 'view_experiment', experiment ) ):
                    complete = False
                    message2 += '<li class=\"text-info\">' + experiment.title + '</li>'
                    exptz2_objs = exptz2_objs.exclude( id = experiment.id )
            exptz3 = [b.id for b in exptz2_objs ]
            message2 += '</ul></h1></p>'
            view_disallowed = False
            if user.has_perm('pepsite.view_experiment_disallowed'):
                view_disallowed = True
            if ( not user.has_perm( 'view_experiment', expt ) ):
                message = '<h1 class=\"text-danger\"><p>You do not have permission to view primary Experiment: <span class=\"text-info\">%s</span>' % ( expt.title )
                if not complete:
                    message += "</h1></p>" + message2
                return render( request, 'pepsite/render_compare_expt_results_ajax.html', { 'expt' : expt, 'expt1' : expt1, 'view_disallowed' : view_disallowed, 'exptz' : exptz3, 'lodgements' : lodgements, 'publications' : publications, 'message' : message, 'complete' : complete, 'exptz_objs' : exptz2_objs   })
            return render( request, 'pepsite/render_compare_expt_results_ajax.html', { 'complete' : complete, 'view_disallowed' : view_disallowed, 'expt' : expt, 'expt1' : expt1, 'exptz' : exptz3, 'lodgements' : lodgements, 'publications' : publications, 'exptz_objs' : exptz2_objs   })
    else:
        compare_form = CompareExptForm()
        context = { 'compare_form' : compare_form }
        return render( request, 'pepsite/compare_expt_form_ajax.html', context)



def comparison_peptides_render_rapid( request ):
  user = request.user
  print 'engaging comparison_peptides_render_rapid'
  if user.id is None:
    user = User.objects.get( id = -1 )
  #return HttpResponse( 'Hello!' )
  if request.POST.has_key( 'expt' ) and request.POST.has_key( 'exptz[]' ):
            
            expt1 = request.POST['expt']
            expt = get_object_or_404( Experiment, id = expt1 )
            exptz = request.POST.getlist('exptz[]' )
            exptz2 = Experiment.objects.filter( id__in = exptz ).distinct()
            print 'expt =', expt.id, 'exptz =', exptz
            #return HttpResponse( 'Something!!!' + str( request.POST.keys() )  )
            #exptz = formdata['exptz']
            complete = True
            if ( not user.has_perm( 'view_experiment', expt ) ):
                message = 'You do not have permission to view Experiment: %s' % ( expt.title )
                return render( request, 'pepsite/compare_peptides_render_rapid.html', { 'rows' : [], 'compare_expts' : exptz2, 'expt' : expt, 'complete' : complete  })
            message = 'You do not have permission to view comparison Experiments: '
            for experiment in exptz2:
                if ( not user.has_perm( 'view_experiment', experiment ) ):
                    complete = False
                    message += experiment.title + ' '
                    exptz2 = exptz2.exclude( id = experiment.id ) 
            s1 = ExptArrayAssemble()
            rows = s1.new_basic_compare_expt_query( expt1 ) 
            allrows = s1.all_peptides_compare_expt_query( expt1 ) 
            view_disallowed = False
            if user.has_perm('pepsite.view_experiment_disallowed'):
                view_disallowed = True
            final_compar = [ b.id for b in exptz2 ]
            params = [ 'compare', expt1, final_compar ]
            context = { 'rows' : rows, 'params' : params, 'allrows' : allrows, 'view_disallowed' : view_disallowed, 'compare_expts' : exptz2, 'expt' : expt, 'complete' : complete  }
            if not complete:
                context['message'] = message
            return render( request, 'pepsite/compare_peptides_render_rapid.html', context ) #{ 'rows' : rows, 'compare_expts' : exptz2, 'expt' : expt, 'complete' : complete  })

def comparison_peptides_render( request ):
  user = request.user
  if user.id is None:
    user = User.objects.get( id = -1 )
  #return HttpResponse( 'Hello!' )
  if request.POST.has_key( 'expt' ) and request.POST.has_key( 'exptz[]' ):
            
            expt1 = request.POST['expt']
            expt = get_object_or_404( Experiment, id = expt1 )
            exptz = request.POST.getlist('exptz[]' )
            print 'expt =', expt.id, 'exptz =', exptz
            complete = True
            for dataset in Dataset.objects.filter( experiment__id__in =  exptz + [ expt1 ] ):
                if ( not user.has_perm( 'view_dataset', dataset ) ):
                    complete = False
            s1 = ExptArrayAssemble()
            rows = s1.mkiii_compare_query( expt1, exptz, user.id ) 
            return render( request, 'pepsite/compare_peptides_render.html', { 'rows' : rows, 'compare_ds' : s1.compare_ds, 'expt' : expt, 'complete' : complete  })
  else:
      return HttpResponse( 'Nothing!!!' + str( request.POST.keys() )  )

def searched_peptides_render_quicker( request ):
    user = request.user
    complete = True
    excluded_ids = []
    for expt in Experiment.objects.all().distinct():
        if ( not user.has_perm( 'view_experiment', expt ) ):
            complete = False
            excluded_ids.append( expt.id )
    if request.POST.has_key( 'stype' ) and request.POST.has_key( 'sargs[]' ):
            
            stype = request.POST['stype']
            sargs = request.POST.getlist('sargs[]' )
            sargs.append( excluded_ids )
            print 'stype =', stype, 'sargs =', sargs
            s1 = MassSearch()
            rows = s1.get_unique_peptide_ides_views( stype, sargs ) 
            return render( request, 'pepsite/peptides_render_rapid_views.html', { 'rows' : rows  })

def searched_peptides_render( request ):
  user = request.user
  if request.POST.has_key( 'stype' ) and request.POST.has_key( 'sargs[]' ):
            stype = request.POST['stype']
            sargs = request.POST.getlist('sargs[]' )
            sargs.append( user )
            print 'stype =', stype, 'sargs =', sargs
            s1 = MassSearch()
            rows = s1.get_unique_peptide_ides( stype, sargs ) 
            return render( request, 'pepsite/peptides_render_rapid.html', { 'rows' : rows  })
  else:
      return HttpResponse( 'Nothing!!!' + str( request.POST.keys() )  )


def protein_full_listing( request, protein_id ):
    prot = get_object_or_404( Protein, id = protein_id )
    s1 = ProteinSearch()
    expts = s1.get_experiments_from_protein( prot )
    context = { 'msg' : expts, 'protein' : prot }
    return render( request, 'pepsite/protein_full_listing.html', context)

def expt2_ajax( request, expt_id ):
    user = request.user
    #initial_quota = 25
    #proteins = Protein.objects.filter( peptide__ion__experiment__id = expt_id).distinct()
    expt = get_object_or_404( Experiment, id = expt_id )
    publications = expt.get_publications()
    lodgements = Lodgement.objects.filter( dataset__experiment = expt )
    complete = True
    for dataset in expt.dataset_set.all():
        if ( not user.has_perm( 'view_dataset', dataset ) ):
            complete = False
    if not( len(lodgements)):
        lodgements = False
    return render( request, 'pepsite/expt2_ajax.html', { 'expt' : expt, 'lodgements' : lodgements, 'complete' : complete, 'publications' : publications, 'paginate' : False })

def expt2_ajax_rapid( request, expt_id ):
    user = request.user
    #initial_quota = 25
    #proteins = Protein.objects.filter( peptide__ion__experiment__id = expt_id).distinct()
    expt = get_object_or_404( Experiment, id = expt_id )
    publications = expt.get_publications()
    lodgements = Lodgement.objects.filter( dataset__experiment = expt )
    complete = True
    for dataset in expt.dataset_set.all():
        if ( not user.has_perm( 'view_dataset', dataset ) ):
            complete = False
    if not( len(lodgements)):
        lodgements = False
    view_disallowed = False
    if user.has_perm('pepsite.view_experiment_disallowed'):
        view_disallowed = True
    return render( request, 'pepsite/expt2_ajax_rapid.html', { 'expt' : expt, 'view_disallowed': view_disallowed, 'lodgements' : lodgements, 'complete' : complete, 'publications' : publications, 'paginate' : False })

def peptides_render( request, expt_id ):
    user = request.user
    print 'user = ', user, user.id, user.username
    if user.id is None:
        user = User.objects.get( id = -1 )
    print 'user = ', user, user.id, user.username
    expt = get_object_or_404( Experiment, id = expt_id )
    s1 = ExptArrayAssemble()
    rows = s1.mkiii_expt_query(  expt.id, user.id )
    print len(rows)
    return render( request, 'pepsite/peptides_render_rapid.html', { 'expt' : expt, 'rows' : rows })

def peptides_render_rapid( request, expt_id ):
    user = request.user
    print 'user = ', user, user.id, user.username
    if user.id is None:
        user = User.objects.get( id = -1 )
    print 'user = ', user, user.id, user.username
    expt = get_object_or_404( Experiment, id = expt_id )
    rows = []
    if user.has_perm( 'view_experiment', expt ):
        print 'permission granted for Expt# %d' % expt.id
        s1 = ExptArrayAssemble()
        rows = s1.basic_expt_query(  expt.id )
    else:
        print 'permission denied'
    print len(rows)
    if len(rows) > 4:
        print rows[:4]
    else:
        print 'dud rows'
    return render( request, 'pepsite/peptides_render_rapid_views.html', { 'expt' : expt, 'rows' : rows })

def footer( request ):
    return render( request, 'pepsite/footer.html', {})

def nav_buttons_allele( request ):
    return render( request, 'pepsite/nav_buttons_allele.html', {})

def nav_buttons( request  ):
    return render( request, 'pepsite/nav_buttons.html', {})
