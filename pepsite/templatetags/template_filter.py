from django import template

register = template.Library()

from pepsite.models import *

@register.assignment_tag
def query_peptide( **kwargs):
    """ template tag which allows queryset filtering. Usage:
          {% query books author=author as mybooks %}
          {% for book in mybooks %}
            ...
          {% endfor %}
    """
    return Peptide.objects.filter(**kwargs)

@register.assignment_tag
def query_idestimate( **kwargs):
    """ template tag which allows queryset filtering. Usage:
          {% query books author=author as mybooks %}
          {% for book in mybooks %}
            ...
          {% endfor %}
    """
    return IdEstimate.objects.filter(**kwargs)
