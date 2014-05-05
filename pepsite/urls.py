from django.conf.urls import patterns, include, url

from pepsite import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^model_info/(?P<model_type>\w+)/(?P<model_id>\d+)/$', views.model_info, name='model_info'),
    url(r'^allele_search$', views.allele_search, name='allele_search'),
    url(r'^allele_browse$', views.allele_browse, name='allele_browse'),
    url(r'^allele_results$', views.allele_results, name='allele_results'),
    url(r'^footer$', views.footer, name='footer'),
    url(r'^trial_table$', views.trial_table, name='trial_table'),
    #url(r'^expt/(?P<expt_id>\d+)$', views.expt, name='expt'),
    url(r'^expt2/(?P<expt_id>\d+)$', views.expt2, name='expt2'),
    url(r'^send_expt_csv/(?P<expt_id>\d+)$', views.send_expt_csv, name='send_expt_csv'),
    url(r'^peptide_expts/(?P<peptide_id>\d+)$', views.peptide_expts, name='peptide_expts'),
    url(r'^protein_full_listing/(?P<protein_id>\d+)$', views.protein_full_listing, name='protein_full_listing'),
    url(r'^cell_line_expts/(?P<cell_line_id>\d+)$', views.cell_line_expts, name='cell_line_expts'),
    url(r'^entity_expts/(?P<entity_id>\d+)$', views.entity_expts, name='entity_expts'),
    url(r'^antibody_expts/(?P<antibody_id>\d+)$', views.antibody_expts, name='antibody_expts'),
    url(r'^allele_expts/(?P<allele_id>\d+)$', views.allele_expts, name='allele_expts'),
    url(r'^ptm_expts/(?P<ptm_id>\d+)$', views.ptm_expts, name='ptm_expts'),
    # Examples:
    # url(r'^$', 'hdome.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

)
