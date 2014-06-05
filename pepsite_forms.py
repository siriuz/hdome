from django import forms
from pepsite.models import Experiment, Antibody, CellLine
from django.core.urlresolvers import reverse

class TextOnlyForm(forms.Form):
    text_input = forms.CharField()

class UploadSSForm(forms.Form):
    expt1 = forms.ChoiceField( label = 'Select an existing Experiment', choices = [[-1, u'ADD NEW EXPERIMENT']] + [ [b.id, b.title] for b in Experiment.objects.all()] )
    expt2 = forms.CharField( label = 'New Experiment Name' )
    ab1 = forms.ChoiceField( label = 'Select an existing Antibody', choices = [ [b.id, b.name] for b in Antibody.objects.all()],
            help_text = 'Don\'t see the Antibody you want? Create one <a href = \"%s\">here</a>' % ( reverse('pepsite:cell_line_search')) )
    cl1 = forms.ChoiceField( label = 'Select an existing Cell Line', choices = [ [b.id, b.name] for b in CellLine.objects.all()] )
    ds = forms.CharField( label = 'Dataset Name' )
    ss = forms.FileField( label = 'Spreadsheet for upload' )

class AjaxForm(forms.Form):
    """
    """
    def __init__(self):
        """docstring for fname"""
        self.text_input = forms.CharField()
        

