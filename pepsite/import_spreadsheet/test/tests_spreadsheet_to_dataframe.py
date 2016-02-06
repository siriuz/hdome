from pepsite.import_spreadsheet.spreadsheet_to_dataframe import *
from django.test import TestCase

current_directory = os.path.dirname(os.path.realpath(__file__))

PROTEINPILOT_V5_TEST_FILE = os.path.join(current_directory, "test_protein_pilot_v5_spreadsheet.txt")
PROTEINPILOT_V4_TEST_FILE = os.path.join(current_directory, "test_protein_pilot_v4_spreadsheet.txt")


class IdentifyProteinpilotCsvVersion(TestCase):
    def test_identify_proteinpilot_v5(self):
        assert identify_proteinpilot_csv_version(PROTEINPILOT_V4_TEST_FILE) == 4

    def test_identify_proteinpilot_v4(self):
        assert identify_proteinpilot_csv_version(PROTEINPILOT_V5_TEST_FILE) == 5

    def test_identify_fail(self):
        with self.assertRaises(ValueError):
            identify_proteinpilot_csv_version(__file__)


class TestV4ReadCsv(TestCase):
    def setUp(self):
        self.protein_pilot_v4_dataframe = read_csv(PROTEINPILOT_V4_TEST_FILE)

    def test_check_v4_dataframe_column_names(self):
        df_columns = set(self.protein_pilot_v4_dataframe.columns)
        mapping_columns = set(HeaderToDataFieldMappings.ProteinPilotV4.values())
        assert df_columns == mapping_columns

    def test_check_v4_dataframe_length(self):
        with open(PROTEINPILOT_V4_TEST_FILE, 'r') as csvfile:
            row_count = sum(1 for row in csvfile) - 1  # -1 because header isn't in the dataframe

        assert self.protein_pilot_v4_dataframe.size == \
               (row_count * len(HeaderToDataFieldMappings.ProteinPilotV4.values()))  # (rows * columns)


class TestV5ReadCsv(TestCase):
    def setUp(self):
        self.protein_pilot_v5_dataframe = read_csv(PROTEINPILOT_V5_TEST_FILE)

    def test_check_v5_dataframe_column_names(self):
        df_columns = set(self.protein_pilot_v5_dataframe.columns)
        mapping_columns = set(HeaderToDataFieldMappings.ProteinPilotV5.values())
        assert df_columns == mapping_columns

    def test_check_v5_dataframe_length(self):
        with open(PROTEINPILOT_V5_TEST_FILE, 'r') as csvfile:
            row_count = sum(1 for row in csvfile) - 1  # -1 because header isn't in the dataframe

        assert self.protein_pilot_v5_dataframe.size == \
               (row_count * len(HeaderToDataFieldMappings.ProteinPilotV5.values()))  # (rows * columns)
