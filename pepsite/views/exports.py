__author__ = 'rimmer'


from django.shortcuts import render, get_object_or_404
from pepsite.pepsite_forms import * # need to comment this out during migrations
from pepsite.make_searches import *
from pepsite.models import *
from django.core.servers.basehttp import FileWrapper
from pepsite.tasks import *
import datetime
from django.http import HttpResponse
import tempfile




def send_expt_csv(request, expt_id ):

    expt = get_object_or_404( Experiment, id = expt_id )
    filestump = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    download_name = filestump + "_HaploDome_download.csv"
    proteins = list(set(Protein.objects.filter( peptide__ion__experiments = expt)))


    with tempfile.NamedTemporaryFile() as f:
        f.write( 'Protein,Peptide,Modification,Delta Mass,Confidence,Charge State,Retention Time,Precursor Mass,\n' )
        for protein in proteins:
            for ide in IdEstimate.objects.filter( peptide__proteins = protein, ion__experiments = expt ):
                if ide.ptm is not None:
                    f.write( '%s,%s,%s,%f,%f,%d,%f,%f,\n' %( protein.prot_id, ide.peptide.sequence, ide.ptm.description, ide.delta_mass, ide.confidence,
                                                             ide.ion.charge_state, ide.ion.retention_time, ide.ion.precursor_mass ) )
                else:
                    f.write( '%s,%s,%s,%f,%f,%d,%f,%f,\n' %( protein.prot_id, ide.peptide.sequence, '', ide.delta_mass, ide.confidence,
                                                             ide.ion.charge_state, ide.ion.retention_time, ide.ion.precursor_mass ) )
        f.seek(0)
        wrapper      = FileWrapper( f )
        content_type = 'text/csv'
        response     = HttpResponse(wrapper,content_type=content_type)
        response['Content-Length']      = f.tell()
        response['Content-Disposition'] = "attachment; filename=%s"%download_name
        return response

def send_csv(request ):
    """
    """
    if request.POST.has_key( 'expt' ) and request.POST.has_key( 'exptz[]' ) and request.POST.has_key( 'param1' ):
        expt = request.POST[ 'expt' ]
        exptz = request.POST[ 'exptz[]' ].strip('[').strip(']').split(',')
        #exptz_ob = Experiment.objects.filter( id__in = exptz ).distinct().order_by('id')
        param = request.POST[ 'param1' ]
        print 'exptz =', exptz, type(exptz)
        filestump = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        download_name = filestump + "_HaploDome_download.csv"

        s1 = ExptArrayAssemble()
        allrows, header = [], []
        if param == 'compare':
            allrows, header = s1.all_peptides_compare_expt_query( expt, return_header = True )
        elif param == 'single':
            allrows, header = s1.all_peptides_expt_query( expt, return_header = True )

            #header, bodtrows = allrows[0], allrows[1:]
        with tempfile.NamedTemporaryFile() as f:
            f.write( 'Protein description\tUniProt code\tPeptide sequence\tPeptide length\
                    \tPTM(s)\tDelta mass\tConfidence\tm/z\tCharge state\tRetention time\tPrecursor mass\tExperiment\t')
            if param == 'compare':
                for exno in exptz:
                    f.write( 'Compare with: %s\t' % ( Experiment.objects.get( id = exno ).title ) )
            f.write('Display status\n')
            for row in allrows:
                f.write( '%s\t%s\t%s\t%d\t%s\t%f\t%f\t%f\t%f\t%f\t%f\t%s\t' % ( row['proteinstr'], row['uniprotstr'],
                                                                                row['peptide_sequence'], len(row['peptide_sequence']),
                                                                                row['ptmstr'], row['delta_mass'], row['confidence'], row['mz'], row['charge_state'], row['retention_time'],
                                                                                row['precursor_mass'], row['experiment_title'] ) )
                if param == 'compare':
                    for exid in exptz:
                        #print exid, row['allowed_array'], row['disallowed_array']
                        try:
                            assert(int(exid) in row['allowed_array'])
                            f.write( '2\t' )
                        except:
                            try:
                                assert(int(exid) in row['disallowed_array'])
                                f.write( '1\t' )
                            except:
                                f.write( '\t' )
                f.write( '%s\n' % row['spec'] )


                #f.write( str(row) + '\n' )
            f.seek(0)
            wrapper      = FileWrapper( f )
            content_type = 'text/csv'
            response     = HttpResponse(wrapper,content_type=content_type)
            response['Content-Length']      = f.tell()
            response['Content-Disposition'] = "attachment; filename=%s"%download_name
            return response
    else:
        return HttpResponse( '<h1>DIDN\'T WORK!!!</h1>' )

