from django.conf.urls import patterns, include, url

from pepsite import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^allele_search$', views.allele_search, name='allele_search'),
    url(r'^allele_results$', views.allele_results, name='allele_results'),
    url(r'^(?P<expt_id>\d+)/expt$', views.expt, name='expt'),
    url(r'^(?P<peptide_id>\d+)/peptide_expts$', views.peptide_expts, name='peptide_expts'),
    url(r'^(?P<protein_id>\d+)/protein_expts$', views.protein_expts, name='protein_expts'),
    # Examples:
    # url(r'^$', 'hdome.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

)
