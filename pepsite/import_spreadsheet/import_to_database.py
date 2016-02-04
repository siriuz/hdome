import itertools

from pepsite.models import Protein, Peptide, Ptm


def make_models(dataframe):
    """
    Create models from dataframe
    """
    insert_proteins(dataframe)

# IdEstimate needs pks of Protein, Peptide, Ptm (if any)
# protein - populate dict with prot_id,pk


def insert_proteins(dataframe):
    protein_ids = concatenate_lists(dataframe['protein_uniprot_ids'])
    protein_descriptions = concatenate_lists(dataframe['protein_descriptions'])

    protein_tuples_list = itertools.izip(protein_ids, protein_descriptions)

    for prot_id, prot_description in protein_tuples_list:
        Protein.objects.get_or_create(prot_id=prot_id, description=prot_description)


def insert_peptides(dataframe):
    peptide_sequence_list = concatenate_lists(dataframe['peptide_sequence'])

    for peptide_sequence in peptide_sequence_list:
        Peptide.objects.get_or_create(sequence=peptide_sequence)

def insert_ptms(dataframe):
    modifications_list = concatenate_lists(dataframe['ptms_description'])

    for modification in modifications_list:
        Ptm.objects.get_or_create(description=modification)

def concatenate_lists(series):
    """
    Helper method for concatenating a list of lists into a single list
    :param series: A list of lists
    :return: A list containing all the elements in the input
    """
    return list(itertools.chain(series))