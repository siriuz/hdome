from django.conf.urls import patterns, include, url

from pepsite import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^formdump$', views.formdump, name='formdump'),
    url(r'^upload_ss_form$', views.upload_ss_form, name='upload_ss_form'),
    url(r'^comp_results$', views.comp_results, name='comp_results'),
    url(r'^model_info/(?P<model_type>(Protein|Peptide|IdEstimate|Ptm|Ion|Experiment|Antibody|CellLine|Allele|Serotype|Gene|Individual|Entity|Organism))/(?P<model_id>\d+)/$', views.model_info, name='model_info'),
    url(r'^composite_search$', views.composite_search, name='composite_search'),
    url(r'^allele_search$', views.allele_search, name='allele_search'),
    url(r'^mass_search$', views.mass_search, name='mass_search'),
    url(r'^protein_search$', views.protein_search, name='protein_search'),
    url(r'^cell_line_search$', views.cell_line_search, name='cell_line_search'),
    url(r'^cell_line_tissue_search$', views.cell_line_tissue_search, name='cell_line_tissue_search'),
    url(r'^allele_browse$', views.allele_browse, name='allele_browse'),
    url(r'^protein_browse$', views.protein_browse, name='protein_browse'),
    url(r'^cell_line_browse$', views.cell_line_browse, name='cell_line_browse'),
    url(r'^cell_line_tissue_browse$', views.cell_line_tissue_browse, name='cell_line_tissue_browse'),
    url(r'^allele_results$', views.allele_results, name='allele_results'),
    url(r'^footer$', views.footer, name='footer'),
    url(r'^nav_buttons_allele$', views.nav_buttons_allele, name='nav_buttons_allele'),
    url(r'^nav_buttons$', views.nav_buttons, name='nav_buttons'),
    url(r'^trial_table$', views.trial_table, name='trial_table'),
    #url(r'^expt/(?P<expt_id>\d+)$', views.expt, name='expt'),ot
    url(r'^expt2/(?P<expt_id>\d+)$', views.expt2, name='expt2'),
    url(r'^send_expt_csv/(?P<expt_id>\d+)$', views.send_expt_csv, name='send_expt_csv'),
    url(r'^peptide_expts/(?P<peptide_id>\d+)$', views.peptide_expts, name='peptide_expts'),
    url(r'^gene_expts/(?P<gene_id>\d+)$', views.gene_expts, name='gene_expts'),
    url(r'^protein_full_listing/(?P<protein_id>\d+)$', views.protein_full_listing, name='protein_full_listing'),
    url(r'^cell_line_expts/(?P<cell_line_id>\d+)$', views.cell_line_expts, name='cell_line_expts'),
    url(r'^entity_expts/(?P<entity_id>\d+)$', views.entity_expts, name='entity_expts'),
    url(r'^antibody_expts/(?P<antibody_id>\d+)$', views.antibody_expts, name='antibody_expts'),
    url(r'^allele_expts/(?P<allele_id>\d+)$', views.allele_expts, name='allele_expts'),
    url(r'^ptm_expts/(?P<ptm_id>\d+)$', views.ptm_expts, name='ptm_expts'),
    url(r'^ptm_peptides/(?P<ptm_id>\d+)$', views.ptm_peptides, name='ptm_peptides'),
    url(r'^protein_peptides/(?P<protein_id>\d+)$', views.protein_peptides, name='protein_peptides'),
    url(r'^peptide_peptides/(?P<peptide_id>\d+)$', views.peptide_peptides, name='peptide_peptides'),
    # Examples:
    # url(r'^$', 'hdome.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

)
