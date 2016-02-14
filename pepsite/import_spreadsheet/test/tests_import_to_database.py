import datetime
import subprocess

import os
import sys
from django.contrib.auth.models import User
from django.utils.timezone import utc

from ..import_to_database import *
from ..spreadsheet_to_dataframe import read_csv
from django.test import TestCase

from pepsite.models import Protein, Manufacturer, Instrument, ExternalDb, Lodgement
from pepsite.scripts.imports_rapid import \
    BackgroundImports  # Borrowing experiments index parsing code for now because I don't fully understand it
from pepsite.tests import MDIC

current_directory = os.path.dirname(os.path.realpath(__file__))
PROTEINPILOT_V5_TEST_FILE = os.path.join(current_directory, "test_protein_pilot_v5_spreadsheet.txt")
PROTEINPILOT_V5_BIG_TEST_FILE = os.path.join(current_directory, "test_protein_pilot_v5_spreadsheet_long.txt")

TEST_PROTEINS_TUPLES = {(u'P0CG05', u'Ig lambda-2 chain C regions OS=Homo sapiens GN=IGLC2 PE=1 SV=1'),
                        (u'P04222',
                         u'HLA class I histocompatibility antigen, Cw-3 alpha chain OS=Homo sapiens GN=HLA-C PE=1 SV=2'),
                        (u'P0CF74', u' Ig lambda-6 chain C region OS=Homo sapiens GN=IGLC6 PE=4 SV=1'),
                        (u'P13284',
                         u'Gamma-interferon-inducible lysosomal thiol reductase OS=Homo sapiens GN=IFI30 PE=1 SV=3')}

TEST_PEPTIDES = {u'AAVVVPSGEEQRYT', u'NKYAASSYLSLTP', u'QKWAAVVVPSGEE', u'LDFFGNGPPVNYKT', u'LDFFGNGPPVNYK'}

TEST_PTMS = {u'Gln->pyro-Glu@N-term'}

TEST_IONS_TUPLES = [
    {'charge_state': 2, u'dataset_id': 1, 'retention_time': 36.32075, 'spectrum': u'1.1.1.3740.19', u'experiment_id': 1,
     'precursor_mass': 1504.7507324219, u'id': 1, 'mz': 753.3826},
    {'charge_state': 2, u'dataset_id': 1, 'retention_time': 51.91103, 'spectrum': u'1.1.1.4016.15', u'experiment_id': 1,
     'precursor_mass': 1381.6898193359, u'id': 2, 'mz': 691.8522},
    {'charge_state': 2, u'dataset_id': 1, 'retention_time': 49.23435, 'spectrum': u'1.1.1.3969.11', u'experiment_id': 1,
     'precursor_mass': 1413.7156982422, u'id': 3, 'mz': 707.8651},
    {'charge_state': 2, u'dataset_id': 1, 'retention_time': 54.27973, 'spectrum': u'1.1.1.4058.10', u'experiment_id': 1,
     'precursor_mass': 1466.720703125, u'id': 4, 'mz': 734.3676},
    {'charge_state': 2, u'dataset_id': 1, 'retention_time': 54.74555, 'spectrum': u'1.1.1.4066.15', u'experiment_id': 1,
     'precursor_mass': 1567.7677001953, u'id': 5, 'mz': 784.8911}]


class TestProteinCache(TestCase):
    def test_init_proteincache(self):
        protein_object = Protein.objects.create(prot_id="P10126",
                                                description="Elongation factor 1-alpha 1 "
                                                            "OS=Mus musculus GN=Eef1a1 PE=1 SV=3")
        pc = ProteinCache()
        assert pc.get_protein_object("P10126") == protein_object

    def test_get_protein_object_fail(self):
        pc = ProteinCache()
        with self.assertRaises(KeyError):
            pc.get_protein_object("123567")

    def test_no_refresh_proteincache(self):
        pc = ProteinCache()
        protein_object = Protein.objects.create(prot_id="P10126",
                                                description="Elongation factor 1-alpha 1 "
                                                            "OS=Mus musculus GN=Eef1a1 PE=1 SV=3")
        with self.assertRaises(KeyError):
            pc.get_protein_object("P10126")

    def test_refresh_proteincache(self):
        pc = ProteinCache()
        protein_object = Protein.objects.create(prot_id="P10126",
                                                description="Elongation factor 1-alpha 1 "
                                                            "OS=Mus musculus GN=Eef1a1 PE=1 SV=3")
        pc.refresh_cache()
        assert pc.get_protein_object("P10126") == protein_object

    def test_insert_database_query_proteincache(self):
        """ Ensures that cache was hit """
        protein_object = Protein.objects.create(prot_id="P10126",
                                                description="Elongation factor 1-alpha 1 "
                                                            "OS=Mus musculus GN=Eef1a1 PE=1 SV=3")
        pc = ProteinCache()
        from django.db import connection
        assert len(connection.queries) == 0
        assert pc.get_protein_object("P10126") == protein_object
        assert len(connection.queries) == 0


class TestPeptideCache(TestCase):
    def test_init_peptidecache(self):
        peptide_object = Peptide.objects.create(sequence="AAVVVPSGEEQRYT")
        pc = PeptideCache()
        assert pc.get_peptide_object("AAVVVPSGEEQRYT") == peptide_object

    def test_get_peptide_object_fail(self):
        pc = PeptideCache()
        with self.assertRaises(KeyError):
            pc.get_peptide_object("DFSDFH")

    def test_no_refresh_peptidecache(self):
        pc = PeptideCache()
        peptide_object = Peptide.objects.create(sequence="AAVVVPSGEEQRYT")
        with self.assertRaises(KeyError):
            pc.get_peptide_object("AAVVVPSGEEQRYT")

    def test_refresh_peptidecache(self):
        pc = PeptideCache()
        peptide_object = Peptide.objects.create(sequence="AAVVVPSGEEQRYT")
        pc.refresh_cache()
        assert pc.get_peptide_object("AAVVVPSGEEQRYT") == peptide_object

    def test_insert_database_query_peptidecache(self):
        """ Ensures that cache was hit """
        peptide_object = Peptide.objects.create(sequence="AAVVVPSGEEQRYT")
        pc = PeptideCache()
        from django.db import connection
        assert len(connection.queries) == 0
        assert pc.get_peptide_object("AAVVVPSGEEQRYT") == peptide_object
        assert len(connection.queries) == 0


class TestPtmCache(TestCase):
    def test_init_ptmcache(self):
        ptm_object = Ptm.objects.create(description="Gln->pyro-Glu@N-term")
        pc = PtmCache()
        assert pc.get_ptm_object("Gln->pyro-Glu@N-term") == ptm_object

    def test_get_ptm_object_fail(self):
        pc = PtmCache()
        with self.assertRaises(KeyError):
            pc.get_ptm_object("Gln->pyro-Glu@N-term")

    def test_no_refresh_ptmcache(self):
        pc = PtmCache()
        ptm_object = Ptm.objects.create(description="Gln->pyro-Glu@N-term")
        with self.assertRaises(KeyError):
            pc.get_ptm_object("Gln->pyro-Glu@N-term")

    def test_refresh_ptmcache(self):
        pc = PtmCache()
        ptm_object = Ptm.objects.create(description="Gln->pyro-Glu@N-term")
        pc.refresh_cache()
        assert pc.get_ptm_object("Gln->pyro-Glu@N-term") == ptm_object

    def test_insert_database_query_peptidecache(self):
        """ Ensures that cache was hit """
        ptm_object = Ptm.objects.create(description="Gln->pyro-Glu@N-term")
        pc = PtmCache()
        from django.db import connection
        assert len(connection.queries) == 0
        assert pc.get_ptm_object("Gln->pyro-Glu@N-term") == ptm_object
        assert len(connection.queries) == 0


# class TestIonCache(TestCase):


class TestInsertProteins(TestCase):
    def setUp(self):
        self.v5_dataframe = read_csv(PROTEINPILOT_V5_TEST_FILE)

    def test_check_proteins_in_database(self):
        insert_proteins(self.v5_dataframe)
        assert TEST_PROTEINS_TUPLES == set(Protein.objects.all().values_list('prot_id', 'description'))


class TestInsertPeptides(TestCase):
    def setUp(self):
        self.v5_dataframe = read_csv(PROTEINPILOT_V5_TEST_FILE)

    def test_check_proteins_in_database(self):
        insert_peptides(self.v5_dataframe)
        assert TEST_PEPTIDES == set(Peptide.objects.all().values_list('sequence', flat=True))


class TestInsertPtms(TestCase):
    def setUp(self):
        self.v5_dataframe = read_csv(PROTEINPILOT_V5_TEST_FILE)

    def test_check_proteins_in_database(self):
        insert_ptms(self.v5_dataframe)
        assert TEST_PTMS == set(Ptm.objects.all().values_list('description', flat=True))

# TODO: TestDatasetCache
# TODO: TestInsertDataset


class TestInsertIons(TestCase):
    def setUp(self):
        self.v5_dataframe = read_csv(PROTEINPILOT_V5_TEST_FILE)

        """ Below block borrowed from legacy test code """
        user1 = User.objects.create()
        user1.set_password('f')
        user1.username = 'u1'
        user1.save()
        self.user1 = user1
        self.man1 = Manufacturer.objects.create(name='MZTech')
        self.inst1 = Instrument.objects.create(name='HiLine-Pro', description='MS/MS Spectrometer',
                                               manufacturer=self.man1)
        self.uniprot = ExternalDb.objects.create(db_name='UniProt', url_stump='http://www.uniprot.org/uniprot/')
        bi1 = BackgroundImports()
        cl = bi1.get_cell_line(MDIC)
        bi1.insert_alleles(MDIC, cl_obj=cl)
        bi1.insert_update_antibodies(MDIC)
        bi1.create_experiment(MDIC, cl)
        self.bi1 = bi1
        """ End of borrowed block """
        test_experiment = Experiment.objects.first()
        test_user = user1
        lodgement_filename = "test.txt"
        now = datetime.datetime.utcnow().replace(tzinfo=utc)

        test_lodgement, _ = Lodgement.objects.get_or_create(user=test_user,
                                                            title=lodgement_filename,
                                                            datetime=now,
                                                            datafilename=lodgement_filename)

        self.lodgement = test_lodgement
        self.test_experiment = test_experiment

    def test_check_ions_in_database_default_manager(self):
        insert_datasets(dataframe=self.v5_dataframe,
                        confidence_cutoff=0.971,
                        experiment=self.test_experiment,
                        instrument=self.inst1,
                        lodgement=self.lodgement)

        ERROR_MARGIN = 0.0000000001
        insert_ions(self.v5_dataframe, experiment=self.test_experiment)
        assert Ion.objects.all().count() == 5
        for test_ion in TEST_IONS_TUPLES:
            retrieved_ion_object = Ion.objects.get(experiment=self.test_experiment,
                                                   charge_state__exact=test_ion['charge_state'],
                                                   retention_time__range=(test_ion['retention_time'] - ERROR_MARGIN,
                                                                          test_ion['retention_time'] + ERROR_MARGIN),
                                                   spectrum__exact=test_ion['spectrum'],
                                                   precursor_mass__range=(test_ion['precursor_mass'] - ERROR_MARGIN,
                                                                          test_ion['precursor_mass'] + ERROR_MARGIN),
                                                   mz__range=(test_ion['mz'] - ERROR_MARGIN,
                                                              test_ion['mz'] + ERROR_MARGIN))
            assert type(retrieved_ion_object) == Ion

    def test_check_ions_in_database_floats_manager(self):
        insert_datasets(dataframe=self.v5_dataframe,
                        confidence_cutoff=0.971,
                        experiment=self.test_experiment,
                        instrument=self.inst1,
                        lodgement=self.lodgement)
        insert_ions(self.v5_dataframe, experiment=self.test_experiment)
        assert Ion.objects.all().count() == 5
        for test_ion in TEST_IONS_TUPLES:
            retrieved_ion_object = Ion.objects.retrieve_by_floats(experiment=self.test_experiment,
                                                                  charge_state=test_ion['charge_state'],
                                                                  retention_time=test_ion['retention_time'],
                                                                  spectrum__exact=test_ion['spectrum'],
                                                                  precursor_mass=test_ion['precursor_mass'],
                                                                  mz=test_ion['mz'])
            assert type(retrieved_ion_object) == Ion


class TestIonCache(TestCase):
    def setUp(self):
        self.v5_dataframe = read_csv(PROTEINPILOT_V5_TEST_FILE)

        """ Below block borrowed from legacy test code """
        user1 = User.objects.create()
        user1.set_password('f')
        user1.username = 'u1'
        user1.save()
        self.user1 = user1
        self.man1 = Manufacturer.objects.create(name='MZTech')
        self.inst1 = Instrument.objects.create(name='HiLine-Pro', description='MS/MS Spectrometer',
                                               manufacturer=self.man1)
        self.uniprot = ExternalDb.objects.create(db_name='UniProt', url_stump='http://www.uniprot.org/uniprot/')
        bi1 = BackgroundImports()
        cl = bi1.get_cell_line(MDIC)
        bi1.insert_alleles(MDIC, cl_obj=cl)
        bi1.insert_update_antibodies(MDIC)
        bi1.create_experiment(MDIC, cl)
        self.bi1 = bi1
        """ End of borrowed block """
        test_experiment = Experiment.objects.first()
        test_user = user1
        lodgement_filename = "test.txt"
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        test_instrument = self.inst1

        test_lodgement, _ = Lodgement.objects.get_or_create(user=test_user,
                                                            title=lodgement_filename,
                                                            datetime=now,
                                                            datafilename=lodgement_filename)

        test_dataset_title = "Test dataset title"

        test_dataset, _ = Dataset.objects.get_or_create(instrument=test_instrument,
                                                        lodgement=test_lodgement,
                                                        experiment=test_experiment,
                                                        datetime=now,
                                                        title=test_dataset_title,
                                                        confidence_cutoff=0.971)

        self.test_dataset = test_dataset
        self.test_experiment = test_experiment

    def test_init_ptmcache(self):
        ion_object = Ion.objects.create(charge_state=2,
                                        retention_time=36.32075,
                                        spectrum=u'1.1.1.3740.19',
                                        precursor_mass=1504.7507324219,
                                        mz=753.3826,
                                        dataset=self.test_dataset,
                                        experiment=self.test_experiment)
        ic = IonCache(experiment=self.test_experiment)
        assert ion_object == ic.get_ion_object(charge_state=2,
                                               precursor_mass=1504.7507324219,
                                               mz=753.3826,
                                               retention_time=36.32075)

    def test_get_ion_object_fail(self):
        ic = IonCache(experiment=self.test_experiment)
        with self.assertRaises(KeyError):
            ic.get_ion_object(charge_state=2,
                              precursor_mass=1504.7507324219,
                              mz=753.3826,
                              retention_time=36.32075)

    def test_no_refresh_ioncache(self):
        ic = IonCache(experiment=self.test_experiment)
        ion_object = Ion.objects.create(charge_state=2,
                                        retention_time=36.32075,
                                        spectrum=u'1.1.1.3740.19',
                                        precursor_mass=1504.7507324219,
                                        mz=753.3826,
                                        dataset=self.test_dataset,
                                        experiment=self.test_experiment)

        with self.assertRaises(KeyError):
            ic.get_ion_object(charge_state=2,
                              precursor_mass=1504.7507324219,
                              mz=753.3826,
                              retention_time=36.32075)

    def test_refresh_ioncache(self):
        ic = IonCache(experiment=self.test_experiment)
        ion_object = Ion.objects.create(charge_state=2,
                                        retention_time=36.32075,
                                        spectrum=u'1.1.1.3740.19',
                                        precursor_mass=1504.7507324219,
                                        mz=753.3826,
                                        dataset=self.test_dataset,
                                        experiment=self.test_experiment)
        ic.refresh_cache()
        assert ion_object == ic.get_ion_object(charge_state=2,
                                               precursor_mass=1504.7507324219,
                                               mz=753.3826,
                                               retention_time=36.32075)

    def test_insert_database_query_ioncache(self):
        """ Ensures that cache was hit """
        ion_object = Ion.objects.create(charge_state=2,
                                        retention_time=36.32075,
                                        spectrum=u'1.1.1.3740.19',
                                        precursor_mass=1504.7507324219,
                                        mz=753.3826,
                                        dataset=self.test_dataset,
                                        experiment=self.test_experiment)
        ic = IonCache(experiment=self.test_experiment)
        from django.db import connection
        assert len(connection.queries) == 0
        assert ion_object == ic.get_ion_object(charge_state=2,
                                               precursor_mass=1504.7507324219,
                                               mz=753.3826,
                                               retention_time=36.32075)
        assert len(connection.queries) == 0


class TimeBigIonCache(TestCase):
    """
    Test case for measuring run times
    """
    def setUp(self):
        self.v5_dataframe = read_csv(PROTEINPILOT_V5_BIG_TEST_FILE)

        """ Below block borrowed from legacy test code """
        user1 = User.objects.create()
        user1.set_password('f')
        user1.username = 'u1'
        user1.save()
        self.user1 = user1
        self.man1 = Manufacturer.objects.create(name='MZTech')
        self.inst1 = Instrument.objects.create(name='HiLine-Pro', description='MS/MS Spectrometer',
                                               manufacturer=self.man1)
        self.uniprot = ExternalDb.objects.create(db_name='UniProt', url_stump='http://www.uniprot.org/uniprot/')
        bi1 = BackgroundImports()
        cl = bi1.get_cell_line(MDIC)
        bi1.insert_alleles(MDIC, cl_obj=cl)
        bi1.insert_update_antibodies(MDIC)
        bi1.create_experiment(MDIC, cl)
        self.bi1 = bi1
        """ End of borrowed block """
        test_experiment = Experiment.objects.first()
        test_user = user1
        lodgement_filename = "test.txt"
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        test_instrument = self.inst1

        self.test_lodgement, _ = Lodgement.objects.get_or_create(user=test_user,
                                                                 title=lodgement_filename,
                                                                 datetime=now,
                                                                 datafilename=lodgement_filename)

        self.test_experiment = test_experiment

    # def test_insert_and_populate_cache(self):
    #     """
    #     This is commented out because it takes a long time to run and is only for benchmarking purposes
    #     """
    #     insert_ions_row_by_row(self.v5_dataframe, dataset=self.test_dataset, experiment=self.test_experiment)
    #     ic = IonCache(dataset=self.test_dataset, experiment=self.test_experiment)

    def test_bulk_insert_and_populate_cache(self):
        insert_datasets(dataframe=self.v5_dataframe,
                        confidence_cutoff=0.971,
                        experiment=self.test_experiment,
                        instrument=self.inst1,
                        lodgement=self.test_lodgement)

        insert_ions(self.v5_dataframe, experiment=self.test_experiment)
        IonCache(experiment=self.test_experiment)


class TestInsertIdEstimate(TestCase):
    def setUp(self):
        self.v5_dataframe = read_csv(PROTEINPILOT_V5_BIG_TEST_FILE)

        """ Below block borrowed from legacy test code """
        user1 = User.objects.create()
        user1.set_password('f')
        user1.username = 'u1'
        user1.save()
        self.user1 = user1
        self.man1 = Manufacturer.objects.create(name='MZTech')
        self.inst1 = Instrument.objects.create(name='HiLine-Pro', description='MS/MS Spectrometer',
                                               manufacturer=self.man1)
        self.uniprot = ExternalDb.objects.create(db_name='UniProt', url_stump='http://www.uniprot.org/uniprot/')
        bi1 = BackgroundImports()
        cl = bi1.get_cell_line(MDIC)
        bi1.insert_alleles(MDIC, cl_obj=cl)
        bi1.insert_update_antibodies(MDIC)
        bi1.create_experiment(MDIC, cl)
        self.bi1 = bi1
        """ End of borrowed block """
        test_experiment = Experiment.objects.first()
        test_user = user1
        lodgement_filename = "test.txt"
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        test_instrument = self.inst1

        self.test_lodgement, _ = Lodgement.objects.get_or_create(user=test_user,
                                                                 title=lodgement_filename,
                                                                 datetime=now,
                                                                 datafilename=lodgement_filename)

        self.test_experiment = test_experiment

    def test_insert_idestimate(self):
        # Insert stuff into the database. This is the code we're testing!
        insert_proteins(self.v5_dataframe)
        insert_peptides(self.v5_dataframe)
        insert_ptms(self.v5_dataframe)
        insert_datasets(dataframe=self.v5_dataframe,
                        confidence_cutoff=0.971,
                        experiment=self.test_experiment,
                        instrument=self.inst1,
                        lodgement=self.test_lodgement)
        insert_ions(self.v5_dataframe, self.test_experiment)
        insert_idestimates(self.v5_dataframe, self.test_experiment)

        # Database dump to reconstruct the input rows
        original_stdout = sys.stdout
        output_file = open(os.path.join(current_directory, "py_output"), 'w')
        sys.stdout = output_file
        for n in IdEstimate.objects.all(): self.idestimate_to_row(n.id)
        sys.stdout = original_stdout
        output_file.close()

        original_wd = os.getcwd()  # keeping track of this just in case someone was using the current working directory
        os.chdir(current_directory)

        # I apologise if you have to debug this..
        # Basically what this test does is goes through every
        # IdEstimate that has been inserted and reconstructs
        # the rows based on its database relations.

        # A (well commented!) gawk script applies a few transforms
        # to get the proteins and ptms cleaned up.
        # The gawk script is necessary as I cannot reconstruct the
        # bits of the Accession column that are discarded

        # These two outputs are then compared to make sure they
        # are exactly identical (less whitespace)

        # If this test is failing the first thing check is whether gawk
        # is installed and available on your system path

        # gawkoutput is pre-generated now because sorting behavior differs between gawk 3.18 and 4
        # subprocess.call('''./test_script.sh''', shell=True)
        total_lines = subprocess.check_output('''( cat gawkoutput; cat py_output ) | awk '{$1=$1};1' |  wc -l ''',
                                    shell=True)

        total_lines = int(total_lines.rstrip())

        unique_lines = subprocess.check_output(
            '''( cat gawkoutput; cat py_output ) | awk '{$1=$1};1' | sort | uniq -u | wc -l''',
            shell=True)

        unique_lines = int(unique_lines.rstrip())

        os.chdir(original_wd)
        # If total lines == 2*source and unique lines == 0, and there were no duplicates in each file
        # it follows that every line has a copy and the two program outputs were identical
        assert total_lines == len(self.v5_dataframe.index)*2
        assert unique_lines == 0

    def idestimate_to_row(self, idestimate_id):
        idobj = IdEstimate.objects.filter(id=idestimate_id)\
            .select_related()\
            .prefetch_related('peptide')\
            .prefetch_related('ptms')\
            .first()

        print '%s %.8f %.8f' % (idobj.peptide.sequence, idobj.confidence, idobj.delta_mass),
        print '%.8f %.4f %d %s %.5f' % (idobj.ion.precursor_mass, idobj.ion.mz, idobj.ion.charge_state, idobj.ion.spectrum, idobj.ion.retention_time),
        print " ".join([p.prot_id for p in idobj.proteins.all()]), " ".join(sorted([ptms.description for ptms in idobj.ptms.all()])) if len(idobj.ptms.all()) else " "

    def verify_row(self, row_tuple):
        JITTER = 0.000000000001
        for protein_id in row_tuple.protein_uniprot_ids:
            result_row = IdEstimate.objects.filter(
                    proteins__prot_id__exact=protein_id,
                    peptide__sequence__exact=row_tuple.peptide_sequence,
                    ion__charge_state__exact=row_tuple.ion_charge,
                    ion__precursor_mass__range=(row_tuple.ion_precursor_mass - JITTER,
                                                row_tuple.ion_precursor_mass + JITTER),
                    ion__mz__range=(row_tuple.ion_mz - JITTER,
                                    row_tuple.ion_mz + JITTER),
                    ion__retention_time__range=(row_tuple.ion_retention_time - JITTER,
                                                row_tuple.ion_retention_time + JITTER),
                    delta_mass__range=(row_tuple.idestimate_delta_mass - JITTER,
                                       row_tuple.idestimate_delta_mass + JITTER),
                    confidence__range=(row_tuple.idestimate_confidence - JITTER,
                                       row_tuple.idestimate_confidence + JITTER))

            assert len(result_row) > 0  # it turns out that you can have duplicate lines in the protein pilot files

