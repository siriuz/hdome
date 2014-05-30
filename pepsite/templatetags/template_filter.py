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

@register.assignment_tag
def query_lodgement( **kwargs ):
    """ template tag which allows queryset filtering. Usage:
          {% query books author=author as mybooks %}
          {% for book in mybooks %}
            ...
          {% endfor %}
    """
    return Lodgement.objects.get( **kwargs )

@register.assignment_tag
def query_dataset( **kwargs ):
    """ template tag which allows queryset filtering. Usage:
          {% query books author=author as mybooks %}
          {% for book in mybooks %}
            ...
          {% endfor %}
    """
    return Dataset.objects.get( **kwargs )

@register.assignment_tag
def query_peptoprot( **kwargs ):
    """ template tag which allows queryset filtering. Usage:
          {% query books author=author as mybooks %}
          {% for book in mybooks %}
            ...
          {% endfor %}
    """
    return PepToProt.objects.get( **kwargs )

@register.assignment_tag
def query_data_perms( user, expt ):
    """ template tag which allows queryset filtering. Usage:
          {% query books author=author as mybooks %}
          {% for book in mybooks %}
            ...
          {% endfor %}
    """
    complete = True
    for dataset in expt.dataset_set.all():
        if ( not user.has_perm( 'pepsite.view_dataset', dataset ) ) and ( not user.has_perm( 'pepsite.view_lodgement', dataset.lodgement ) ):
            complete = False
    return complete
