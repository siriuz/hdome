from django import forms
from pepsite.models import Experiment, Antibody, CellLine, Publication, Instrument, Lodgement
import os, sys
from django.forms.util import ValidationError as FormValidationError

from django.db.models.fields import URLField, CharField
from django.db import models
from django.db.models import *



class LinkField( forms.CharField ):
    """

    """
    def __init__(self, *args, **kwargs):
        """docstring for __init__"""
        self.url = ''
        if 'url' in kwargs.keys():
            self.url = kwargs.pop('url')
        super(LinkField, self).__init__(*args, **kwargs)


    def clean(self, value):
        value = super(CharField, self).clean(value)
        #if len(value.split(':')) != 2:
        #    raise FormValidationError('Data entered must be in format MM:SS')
        return value

class LinkChoiceField( forms.ChoiceField ):
    """

    """
    urlstr = 'pepsite:cell_line_search'
    urltext = 'Find more here: '
    def __init__(self, *args, **kwargs):
        """docstring for __init__"""
        self.urlstr = ''
        self.urltext = ''
        self.crap = 'poo'
        kwargs['help_text'] = "welcome"
        if 'urlstr' in kwargs.keys():
            self.urlstr = kwargs.pop('urlstr')
            #setattr( super(LinkChoiceField, self), 'urlstr', self.urlstr )
        if 'urltext' in kwargs.keys():
            self.urltext = kwargs.pop('urltext')
            #setattr(super(LinkChoiceField, self), 'urltext', self.urltext )
        super(LinkChoiceField, self).__init__(*args, **kwargs)


    def clean(self, value):
        value = super(ChoiceField, self).clean(value)
        return value

class SimpleDurationField(CharField):
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        """docstring for __init__"""
        self.urlstr = ''
        self.urltext = ''
        self.crap = 'poo'
        kwargs['help_text'] = "welcome"
        if 'urlstr' in kwargs.keys():
            self.urlstr = kwargs.pop('urlstr')
            #setattr( super(LinkChoiceField, self), 'urlstr', self.urlstr )
        if 'urltext' in kwargs.keys():
            self.urltext = kwargs.pop('urltext')
            #setattr(super(LinkChoiceField, self), 'urltext', self.urltext )
        super(SimpleDurationField, self).__init__(*args, **kwargs)
    

    def to_python(self, value):
        if not value:
            return None
        return value

    def get_db_prep_value(self, value):
        return value

    def value_to_string(self, instance):
        urlstr = getattr(instance, self.name)
        return urlstr

    def formfield(self, form_class=LinkChoiceField, **kwargs):
        defaults = {"help_text": "Enter duration in the format: MM:SS"}
        defaults.update(kwargs)
        return form_class(**defaults)


class KRField( forms.ChoiceField ):
    """

    """
    def __init__(self, *args, **kwargs):
        urlstr = ''
        urltext = ''
        crap = 'poo'
        kwargs['help_text'] = "welcome"
        if 'urlstr' in kwargs.keys():
            urlstr = kwargs.pop('urlstr')
        if 'urltext' in kwargs.keys():
            urltext = kwargs.pop('urltext')
        super(KRField, self).__init__(*args, **kwargs)
        self.urlstr = urlstr
        self.urltext = urltext
        self.crap = 'crap'


def append_choicefield( **kwargs ):
    urlstr = ''
    urltext = ''
    crap = 'poo'
    if 'urlstr' in kwargs.keys():
        urlstr = kwargs.pop('urlstr')
    if 'urltext' in kwargs.keys():
        urltext = kwargs.pop('urltext')
    cf = forms.ChoiceField( **kwargs )
    cf.urlstr = urlstr
    cf.urltext = urltext
    cf.crap = 'crap'
    return cf




from hdome import settings
from django.core.urlresolvers import reverse


def get_my_cell_lines():
    """docstring for get_my_cell_line"""
    return [ [b.id, b.name] for b in CellLine.objects.all()]

def get_my_antibodies():
    """docstring for get_my_cell_line"""
    return [ [b.id, b.name] for b in Antibody.objects.all()]

def get_my_instruments():
    """docstring for get_my_cell_line"""
    return [ [b.id, b.name] for b in Instrument.objects.all()]

def get_my_publications():
    """docstring for get_my_cell_line"""
    return [ [b.id, b.display] for b in Publication.objects.all()]

def get_my_experiments():
    """docstring for get_my_cell_line"""
    return ( [[-1, u'ADD NEW EXPERIMENT']] + [ [b.id, b.title] for b in Experiment.objects.all()] )

def get_my_lodgements(user):
    """docstring for get_my_cell_line"""
    return [ [b.id, '%s, source file = %s' % ( b.title, b.datafilename ) ] for b in Lodgement.objects.all() if user.has_perm('edit_lodgement', b )]

class TextOnlyForm(forms.Form):
    text_input = forms.CharField()

class MassSearchForm(forms.Form):
    target_input = forms.FloatField( label = 'Enter a mass (Da)')
    tolerance = forms.FloatField(label = 'Tolerance for mass search (Da)', initial = 0.1 )

class MzSearchForm(forms.Form):
    target_input = forms.FloatField( label = 'Enter m/z')
    tolerance = forms.FloatField(label = 'Tolerance for mass search (Da)', initial = 0.1 )

class SequenceSearchForm(forms.Form):
    target_input = forms.CharField( label = 'Enter a peptide sequence')

class UploadSSForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(UploadSSForm, self).__init__(*args, **kwargs)
        clz = choices = get_my_cell_lines()
        expts = choices = get_my_experiments()
        anbs =  get_my_antibodies()
        insts = get_my_instruments()
        pbz = get_my_publications()
        self.fields['cl1'] = forms.ChoiceField( choices=clz, label = 'Select an existing Cell Line' )
        self.fields['expt1'] = forms.ChoiceField( label = 'Select an existing Experiment', choices = expts )
        self.fields['ab1'] = forms.MultipleChoiceField( label = 'Select Existing Antibody(s)', choices = anbs )
        self.fields['inst'] = forms.ChoiceField( label = 'Select an existing instrument', choices = insts )
        self.fields['pl1'] = forms.MultipleChoiceField( label = 'Select Publication(s)', choices = pbz )
        self.fields['ab1'].widget.attrs.update({'size' : min( 4, len(anbs)) })
        self.fields['pl1'].widget.attrs.update({'size' : min( 4, len(pbz) ) })

    expt1 = append_choicefield( label = 'Select an existing Experiment', choices = [[-1, u'ADD NEW EXPERIMENT']] + [ [b.id, b.title] for b in Experiment.objects.all()], urltext = 'Need a different experiment?', urlstr = 'pepsite:cell_line_search' )
    #expt1.urltest = 'Need a different experiment?'
    #expt1.urlstr = 'pepsite:cell_line_search' 
    expt2 = forms.CharField( label = 'New Experiment Name' )
    expt2_desc = forms.CharField( label = 'New Experiment Description', widget = forms.Textarea )
    #expt2 = LinkField( label = 'New Experiment Name' )
    ab1 = forms.ChoiceField( label = 'Select existing Antibody(ies)', widget = forms.SelectMultiple, choices = [ [b.id, b.name] for b in Antibody.objects.all()] )
    cl1 = forms.ChoiceField( label = 'Select an existing Cell Line', choices = [ [b.id, b.name] for b in CellLine.objects.all()] )
    inst = forms.ChoiceField( label = 'Select an existing Instrument', choices = [ [b.id, b.name] for b in Instrument.objects.all()] )
    pl1 = forms.MultipleChoiceField( label = 'Select Publication(s)', widget = forms.SelectMultiple, choices = [ [b.id, b.display] for b in Publication.objects.all()] )
    rel = forms.BooleanField( label = 'Data publically available?' )
    ldg = forms.CharField( label = 'Name for this Lodgement' )
    ss = forms.FileField( label = 'Spreadsheet for upload' )

class UploadMultipleSSForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(UploadMultipleSSForm, self).__init__(*args, **kwargs)
        clz = choices = get_my_cell_lines()
        expts = choices = get_my_experiments()
        anbs =  get_my_antibodies()
        insts = get_my_instruments()
        pbz = get_my_publications()
        self.fields['cl1'] = forms.ChoiceField( choices=clz, label = 'Select an existing Cell Line' )
        self.fields['expt1'] = forms.ChoiceField( label = 'Select an existing Experiment', choices = expts )
        self.fields['ab1'] = forms.MultipleChoiceField( label = 'Select Existing Antibody(s)', choices = anbs )
        self.fields['inst'] = forms.ChoiceField( label = 'Select an existing instrument', choices = insts )
        self.fields['pl1'] = forms.MultipleChoiceField( label = 'Select Publication(s)', choices = pbz )
        self.fields['ab1'].widget.attrs.update({'size' : min( 4, len(anbs)) })
        self.fields['pl1'].widget.attrs.update({'size' : min( 4, len(pbz) ) })
    #expt1 = forms.ChoiceField( label = 'Select an existing Experiment', choices = [[-1, u'ADD NEW EXPERIMENT']] + [ [b.id, b.title] for b in Experiment.objects.all()] )
    expt1 = append_choicefield( label = 'Select an existing Experiment', choices = [[-1, u'ADD NEW EXPERIMENT']] + [ [b.id, b.title] for b in Experiment.objects.all()], urltext = 'Need a different experiment?', urlstr = 'pepsite:cell_line_search' )
    #expt1.urltest = 'Need a different experiment?'
    #expt1.urlstr = 'pepsite:cell_line_search' 
    expt2 = forms.CharField( label = 'New Experiment Name' )
    expt2_desc = forms.CharField( label = 'New Experiment Description', widget = forms.Textarea )
    #expt2 = LinkField( label = 'New Experiment Name' )
    ab1 = forms.ChoiceField( label = 'Select existing Antibody(ies)', widget = forms.SelectMultiple, choices = [ [b.id, b.name] for b in Antibody.objects.all()] )
    cl1 = forms.ChoiceField( label = 'Select an existing Cell Line', choices = [ [b.id, b.name] for b in CellLine.objects.all()] )
    inst = forms.ChoiceField( label = 'Select an existing Instrument', choices = [ [b.id, b.name] for b in Instrument.objects.all()] )
    pl1 = forms.ChoiceField( label = 'Select Publication(s)', widget = forms.SelectMultiple, choices = [ [b.id, b.display] for b in Publication.objects.all()] )
    rel = forms.BooleanField( label = 'Data publically available?' )
    ldg = forms.CharField( label = 'Prefix for these Lodgements' )
    #ss = forms.FileField( label = 'Spreadsheet for upload' )

class CurationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        try:
            user = kwargs.pop('user')
        except:
            user = user.objects.get(id=1)
        super(CurationForm, self).__init__(*args, **kwargs)
        self.fields['ldg'] = forms.MultipleChoiceField( choices=get_my_lodgements(user), label = 'Select Lodgement(s)' )
        self.fields['ldg'].widget.attrs.update({'class' : 'niceMultiple'})
    #def __init__(self,*args,**kwargs):
    #    self.user = kwargs.pop('user')
    #    super(CurationForm, self).__init__(*args,**kwargs)
    #    self.fields['ldg'].choices = [ [b.id, '%s from Experiment: %s' %( b.title, b.get_experiment().title )] for b in Lodgement.objects.all() if self.user.has_perm( 'edit_lodgement', b )]
    ldg = forms.MultipleChoiceField( label = 'Select Lodgement(s)', widget = forms.SelectMultiple, choices = [ [b.id, '%s from Experiment: %s' %( b.title, b.get_experiment().title )] for b in Lodgement.objects.all()] )
    cur = forms.FileField( label = 'Spreadsheet of peptides to be curated out' )


    # code...

class CompareExptForm( forms.Form ):
    expt1 = forms.ChoiceField( label = 'Select an existing Experiment', choices = [ [b.id, b.title] for b in Experiment.objects.annotate(num_ions=Count('ion')).filter(num_ions__gt=0).order_by('title')] )
    exptz = forms.ChoiceField( label = 'Select Experiment(s) for comparison', widget = forms.SelectMultiple, choices = [ [b.id, b.title] for b in Experiment.objects.annotate(num_ions=Count('ion')).filter(num_ions__gt=0).order_by('title')] )

class AjaxForm(forms.Form):
    """
    """
    def __init__(self):
        """docstring for fname"""
        self.text_input = forms.CharField()
        

