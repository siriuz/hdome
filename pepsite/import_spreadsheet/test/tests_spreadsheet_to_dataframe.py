from pepsite.import_spreadsheet.spreadsheet_to_dataframe import *
from django.test import TestCase


class IdentifyProteinpilotCsvVersion(TestCase):
    def setUp(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))

        self.PROTEINPILOT_V5_TEST_FILE = os.path.join(current_directory,
                                                      "20160118_Amanda_QC6_QC6_01012016_afternewloading"
                                                      "pumpbuffer_PeptideSummary.txt")
        self.PROTEINPILOT_V4_TEST_FILE = os.path.join(current_directory, "rj_test_protein_pilot_spreadsheet.txt")

    def test_identify_proteinpilot_v5(self):
        assert identify_proteinpilot_csv_version(self.PROTEINPILOT_V4_TEST_FILE) == 4

    def test_identify_proteinpilot_v4(self):
        assert identify_proteinpilot_csv_version(self.PROTEINPILOT_V5_TEST_FILE) == 5

    def test_identify_fail(self):
        with self.assertRaises(ValueError):
            identify_proteinpilot_csv_version(__file__)
