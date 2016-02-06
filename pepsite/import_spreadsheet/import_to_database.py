import itertools

from pepsite.models import Protein, Peptide, Ptm, Ion, IdEstimate


class ProteinCache:
    """
    Maintains a cache that maps protein uniprot strings to its database object
    """
    def __init__(self):
        self.protein_key_cache = dict(Protein.objects.all().values_list('prot_id', 'pk'))
        self.protein_object_cache = Protein.objects.in_bulk(self.protein_key_cache.values())

    def refresh_cache(self):
        self.__init__()

    def get_primary_key(self, protein_uniprot):
        return self.protein_key_cache[protein_uniprot]

    def get_protein_object(self, protein_uniprot):
        return self.protein_object_cache[self.get_primary_key(protein_uniprot)]


class PeptideCache:
    """
    Maintains a cache that maps peptide sequences to its database object
    """
    def __init__(self):
        self.peptide_key_cache = dict(Peptide.objects.all().values_list('sequence', 'pk'))
        self.peptide_object_cache = Peptide.objects.in_bulk(self.peptide_key_cache.values())

    def refresh_cache(self):
        self.__init__()

    def get_primary_key(self, peptide_sequence):
        return self.peptide_key_cache[peptide_sequence]

    def get_protein_object(self, peptide_sequence):
        return self.peptide_object_cache[self.get_primary_key(peptide_sequence)]


class PtmCache:
    """
    Maintains a cache that maps ptms to its database object
    """
    def __init__(self):
        self.ptm_key_cache = dict(Ptm.objects.all().values_list('description', 'pk'))
        self.ptm_object_cache = Ptm.objects.in_bulk(self.ptm_key_cache.values())

    def refresh_cache(self):
        self.__init__()

    def get_primary_key(self, ptm_description):
        return self.ptm_key_cache[ptm_description]

    def get_ptm_object(self, ptm_description):
        return self.ptm_object_cache[self.get_primary_key(ptm_description)]


class IonCache(object):
    pass


def insert_proteins(dataframe):
    protein_ids = concatenate_lists(dataframe['protein_uniprot_ids'])
    protein_descriptions = concatenate_lists(dataframe['protein_descriptions'])

    protein_tuples_list = itertools.izip(protein_ids, protein_descriptions)

    for prot_id, prot_description in protein_tuples_list:
        Protein.objects.get_or_create(prot_id=prot_id, description=prot_description)


def insert_peptides(dataframe):
    peptide_sequence_set = set(dataframe['peptide_sequence'])

    for peptide_sequence in peptide_sequence_set:
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
    return list(itertools.chain.from_iterable(series))

# def insert_row(row_tuple):
#
#     for protein in itertools.izip(row_tuple.protein_uniprot_ids, row_tuple.protein_description):
#         Protein.objects.get_or_create()
#     Ptm.objects.get_or_create()
#     Peptide.objects.get_or_create(sequence=)
#
#     Ion.objects.get_or_create()



def insert_ions(dataframe, dataset, experiment):
    pass


def insert_idestimates(dataframe):
    """
    populating the foreign keys of each IdEstimate
    :param dataframe:
    :return:
    """
    df = dataframe.itertuples()
    protein_cache = ProteinCache()
    ptm_cache = PtmCache()

    for row_tuple in df:
        proteins = [protein_cache.get_protein_object(protein_id) for protein_id in row_tuple.protein_uniprot_ids]
        ptms = [ptm_cache.get_ptm_object(ptm) for ptm in row_tuple.ptm_objs]

        peptide = row_tuple.peptide_objs
        ion = row_tuple.ion_objs

        delta_mass = row_tuple.idestimate_delta_mass
        confidence = row_tuple.idestimate_confidence

        row_idestimate = IdEstimate.objects.create(delta_mass=delta_mass,
                                                   confidence=confidence,
                                                   peptide=peptide,
                                                   ion=ion)
        row_idestimate.proteins.add(proteins)
        if len(ptms):
            row_idestimate.ptms.add(ptms)

        row_idestimate.save()





class ImportLodgement:
    """
    This class keeps track of a lodgement
    """
    def __init__(self, dataset, experiment, dataframe):
        self.dataset = dataset
        self.experiment = experiment
        self.dataframe = dataframe
        self.protein_cache = ProteinCache()
        self.peptide_cache = PeptideCache()
        self.ion_cache = IonCache()

    def _import_proteins(self):
        insert_proteins(self.dataframe)
        self.protein_cache.refresh_cache()
        add_protein_objects_column(self.dataframe)

    def _import_ptms(self):
        insert_ptms(self.dataframe)


    def _import_peptides(self):
        insert_peptides(self.dataframe)
        self.peptide_cache.refresh_cache()

    def _import_ions(self):
        insert_ions(self.dataframe, self.dataset, self.experiment)
        self.ion_cache.refresh_cache()

    def _import_idestimates(self):
        insert_idestimates(self.dataframe)

    def run_import(self):
        self._import_proteins()
        self._import_peptides()
        self._import_ptms()
        self._import_ions()
        self._import_idestimates()


