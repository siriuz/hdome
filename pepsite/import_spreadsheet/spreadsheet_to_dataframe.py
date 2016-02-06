import csv

from pepsite.models import *
from column_parsers import *
import pandas as pandas


class HeaderToDataFieldMappings:
    """Mapping of header column names (keys) to internal data field identifiers (values)"""
    ProteinPilotV5 = {
                "Accessions": "protein_uniprot_ids",
                     "Names": "protein_descriptions",
                      "Conf": "idestimate_confidence",
                  "Sequence": "peptide_sequence",
             "Modifications": "ptms_description",
                     "dMass": "idestimate_delta_mass",
                    "Obs MW": "ion_precursor_mass",
                   "Obs m/z": "ion_mz",
                   "Theor z": "ion_charge",
                  "Spectrum": "ion_spectrum",
                  "Acq Time": "ion_retention_time"
    }

    ProteinPilotV4 = {
                "Accessions": "protein_uniprot_ids",
                     "Names": "protein_descriptions",
                      "Conf": "idestimate_confidence",
                  "Sequence": "peptide_sequence",
             "Modifications": "ptms_description",
                     "dMass": "idestimate_delta_mass",
                   "Prec MW": "ion_precursor_mass",
                  "Prec m/z": "ion_mz",
                   "Theor z": "ion_charge",
                  "Spectrum": "ion_spectrum",
                      "Time": "ion_retention_time"
    }


def read_csv(spreadsheet_filepath):
    """ Reads a ProteinPilot spreadsheet and returns a Pandas DataFrame

    Uses Pandas' read_csv to parse the spreadsheet into a DataFrame for more efficient column/row operations.
    pandas.read_csv uses a dictionary of converters which applies functions to matching column names.
    These functions are defined in column_parsers.py. The functions also convert multiple-element cells to
    Python lists. Refer to spreadsheet specifications document for more information.

    :param spreadsheet_filepath: String with path to ProteinPilot V5 spreadsheet
    :return: Pandas DataFrame with column headers renamed to match internal data field identifiers
    """
    spreadsheet_version = identify_proteinpilot_csv_version(spreadsheet_filepath)
    if spreadsheet_version == 5:
        column_mapping = HeaderToDataFieldMappings.ProteinPilotV5
    elif spreadsheet_version == 4:
        column_mapping = HeaderToDataFieldMappings.ProteinPilotV4

    dataframe = pandas.read_csv(spreadsheet_filepath,
                                usecols=column_mapping.keys(),
                                delimiter='\t',
                                converters={"Accessions": accessions_to_uniprot_list,
                                            "Names": names_to_protein_descriptions,
                                            "Modifications": modifications_to_ptms_descriptions})

    # Rename the column names to match models
    dataframe.rename(columns=column_mapping, inplace=True)
    return dataframe


def identify_proteinpilot_csv_version(spreadsheet_filepath):
    """
    Reads the csv header to identify the version of ProteinPilot that produced the file
    Raises a ValueError if the file headers do not match ProteinPilot V4 or V5 files

    :param spreadsheet_filepath: Path to spreadsheet to be identified
    :return: Version of ProteinPilot as an integer (4 or 5)
    """

    with open(spreadsheet_filepath, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter='\t')

        file_header_fields = set(csvreader.fieldnames)
        v5_spec_fields = set(HeaderToDataFieldMappings.ProteinPilotV5.keys())
        v4_spec_fields = set(HeaderToDataFieldMappings.ProteinPilotV4.keys())

        if file_header_fields.issuperset(v5_spec_fields):
            version = 5
        elif file_header_fields.issuperset(v4_spec_fields):
            version = 4
        else:
            raise ValueError('File headers do not match ProteinPilot V4 or V5 fields')

    return version