from django.conf.urls import patterns, include, url

from pepsite import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^allele_search$', views.allele_search, name='allele_search'),
    url(r'^allele_results$', views.allele_results, name='allele_results'),
    url(r'^expt/(?P<expt_id>\d+)$', views.expt, name='expt'),
    url(r'^expt2/(?P<expt_id>\d+)$', views.expt2, name='expt2'),
    url(r'^send_expt_csv/(?P<expt_id>\d+)$', views.send_expt_csv, name='send_expt_csv'),
    url(r'^peptide_expts/(?P<peptide_id>\d+)$', views.peptide_expts, name='peptide_expts'),
    url(r'^protein_expts/(?P<protein_id>\d+)$', views.protein_expts, name='protein_expts'),
    # Examples:
    # url(r'^$', 'hdome.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

)
