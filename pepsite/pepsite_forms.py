from django import forms

class TextOnlyForm(forms.Form):
    text_input = forms.CharField()


class AjaxForm(forms.Form):
    """
    """
    def __init__(self):
        """docstring for fname"""
        self.text_input = forms.CharField()
        

