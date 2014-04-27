from django import forms

class TextOnlyForm(forms.Form):
    text_input = forms.CharField()
