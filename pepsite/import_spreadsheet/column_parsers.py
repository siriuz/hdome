""" Parsers that are applied (using pandas) on a column-wise basis when importing Protein Pilot files """

#  Mapping of header column names to internal data field identifiers
v5header_datafield_mappings = {
            "Accessions": "protein_uniprot_ids",
                 "Names": "protein_descriptions",
                  "Conf": "idestimate_confidence",
              "Sequence": "peptide_sequence",
         "Modifications": "ptms_description",
                 "dMass": "ion_delta_mass",
                "Obs MW": "idestimate_precursor_mass",
               "Obs m/z": "ion_mz",
               "Theor z": "ion_charge",
              "Spectrum": "ion_spectrum",
              "Acq Time": "ion_retention_time"
}


def accessions_to_uniprot_list(input_string):
    """
    Converts a proteinpilot accession cell contents to a list of uniprot IDs
    If cell has a ; in it, multiple accession numbers are assumed

    http://www.uniprot.org/help/accession_numbers
    """

    output_list = []
    accession_list = input_string.split(';')
    for accession in accession_list:
        #  Checks that there are actually uniprot IDs to add
        if (len(accession.split('|')) > 1) and (len(accession.split('|')[1])):
            output_list.append(accession.split('|')[1]) # Return the uniprot ID which lies between the | |

    return output_list


def names_to_protein_descriptions(input_string):
    """
    Converts a ProteinPilot names cell contents to a list of protein descriptions
    If cell has a ; in it, multiple proteins are assumed
    """

    output_list = []
    protein_list = input_string.split(';')
    for protein in protein_list:
        if (len(protein)):
            output_list.append(protein)

    return output_list


def modifications_to_ptms_descriptions(input_string):
    """
    Converts a proteinpilot modifications cell contents to a list of protein modifications descriptions
    If cell has a ; in it, multiple proteins modifications are assumed
    """

    output_list = []
    modifications_list = input_string.split(';')
    for modification in modifications_list:
        if len(modification) > 0:
            output_list.append(modification)

    return output_list
