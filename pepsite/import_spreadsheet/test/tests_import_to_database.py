import os

from ..import_to_database import *
from ..spreadsheet_to_dataframe import read_csv
from django.test import TestCase

from pepsite.models import Protein

current_directory = os.path.dirname(os.path.realpath(__file__))
PROTEINPILOT_V5_TEST_FILE = os.path.join(current_directory, "test_protein_pilot_v5_spreadsheet.txt")

V5_PROTEINS_TUPLES = {(u'P0CG05', u'Ig lambda-2 chain C regions OS=Homo sapiens GN=IGLC2 PE=1 SV=1'),
                      (u'P04222', u'HLA class I histocompatibility antigen, Cw-3 alpha chain OS=Homo sapiens GN=HLA-C PE=1 SV=2'),
                      (u'P0CF74', u' Ig lambda-6 chain C region OS=Homo sapiens GN=IGLC6 PE=4 SV=1'),
                      (u'P13284', u'Gamma-interferon-inducible lysosomal thiol reductase OS=Homo sapiens GN=IFI30 PE=1 SV=3')}

V5_PEPTIDES = {u'AAVVVPSGEEQRYT', u'NKYAASSYLSLTP', u'QKWAAVVVPSGEE', u'LDFFGNGPPVNYKT', u'LDFFGNGPPVNYK'}

V5_PTMS = {u'Gln->pyro-Glu@N-term'}


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


# class TestPeptideCache(TestCase):
# class TestIonCache(TestCase):

class TestInsertProteins(TestCase):
    def setUp(self):
        self.v5_dataframe = read_csv(PROTEINPILOT_V5_TEST_FILE)

    def test_check_proteins_in_database(self):
        insert_proteins(self.v5_dataframe)
        assert V5_PROTEINS_TUPLES == set(Protein.objects.all().values_list('prot_id', 'description'))


class TestInsertPeptides(TestCase):
    def setUp(self):
        self.v5_dataframe = read_csv(PROTEINPILOT_V5_TEST_FILE)

    def test_check_proteins_in_database(self):
        insert_peptides(self.v5_dataframe)
        assert V5_PEPTIDES == set(Peptide.objects.all().values_list('sequence', flat=True))


class TestInsertPtms(TestCase):
    def setUp(self):
        self.v5_dataframe = read_csv(PROTEINPILOT_V5_TEST_FILE)

    def test_check_proteins_in_database(self):
        insert_ptms(self.v5_dataframe)
        assert V5_PTMS == set(Ptm.objects.all().values_list('description', flat=True))
