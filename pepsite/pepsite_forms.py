from django import forms
from pepsite.models import Experiment, Antibody, CellLine, Publication
import os, sys
from django.forms.util import ValidationError as FormValidationError

from django.db.models.fields import URLField, CharField
from django.db import models



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

class TextOnlyForm(forms.Form):
    text_input = forms.CharField()

class UploadSSForm(forms.Form):
    #expt1 = forms.ChoiceField( label = 'Select an existing Experiment', choices = [[-1, u'ADD NEW EXPERIMENT']] + [ [b.id, b.title] for b in Experiment.objects.all()] )
    expt1 = append_choicefield( label = 'Select an existing Experiment', choices = [[-1, u'ADD NEW EXPERIMENT']] + [ [b.id, b.title] for b in Experiment.objects.all()], urltext = 'Need a different experiment?', urlstr = 'pepsite:cell_line_search' )
    #expt1.urltest = 'Need a different experiment?'
    #expt1.urlstr = 'pepsite:cell_line_search' 
    expt2 = forms.CharField( label = 'New Experiment Name' )
    #expt2 = LinkField( label = 'New Experiment Name' )
    ab1 = forms.ChoiceField( label = 'Select existing Antibody(ies)', widget = forms.SelectMultiple, choices = [ [b.id, b.name] for b in Antibody.objects.all()] )
    cl1 = forms.ChoiceField( label = 'Select an existinng Cell Line', choices = [ [b.id, b.name] for b in CellLine.objects.all()] )
    pl1 = forms.ChoiceField( label = 'Select Publication(s)', widget = forms.SelectMultiple, choices = [ [b.id, b.display] for b in Publication.objects.all()] )
    rel = forms.BooleanField( label = 'Data publically available?' )
    ldg = forms.CharField( label = 'Name for this Lodgement' )
    ss = forms.FileField( label = 'Spreadsheet for upload' )

class AjaxForm(forms.Form):
    """
    """
    def __init__(self):
        """docstring for fname"""
        self.text_input = forms.CharField()
        

