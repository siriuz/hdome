import itertools

from decimal import Decimal

import datetime

from django.utils.timezone import utc

from pepsite.models import Protein, Peptide, Ptm, Ion, IdEstimate, Dataset, Experiment


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

    def get_peptide_object(self, peptide_sequence):
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


class IonCache:
    """
    Maintains a cache that maps Ion float tuples to its database object. This cache is limited
    to a specific experiment as these values are also part of the uniqueness constraint on the
    Ion model.
    """
    def __init__(self, experiment):
        self.experiment = experiment
        self.ion_object_cache = dict()
        self.refresh_cache()

    def refresh_cache(self):
        for ion in Ion.objects.filter(experiment=self.experiment):
            self.ion_object_cache[(ion.charge_state,
                                   round(ion.precursor_mass, 11),
                                   round(ion.mz, 4),
                                   round(ion.retention_time, 5))] = ion

    def get_primary_key(self, charge_state, precursor_mass, mz, retention_time):
        return self.ion_object_cache[(charge_state,
                                      round(precursor_mass, 11),
                                      round(mz, 4),
                                      round(retention_time, 5))].id

    def get_ion_object(self, charge_state, precursor_mass, mz, retention_time):
        return self.ion_object_cache[(charge_state,
                                      round(precursor_mass, 11),
                                      round(mz, 4),
                                      round(retention_time, 5))]


class DatasetCache:
    """ Maintains a cache that maps its dataset number to a dataset object
    This cache is specific to an experiment.
    """

    def __init__(self, experiment):
        self.experiment = experiment
        self.dataset_object_cache = dict()
        self.refresh_cache()

    def refresh_cache(self):
        for dataset in Dataset.objects.filter(experiment=self.experiment):
            self.dataset_object_cache[dataset.dataset_number] = dataset

    def get_primary_key(self, dataset_number):
        return self.dataset_object_cache[dataset_number].id

    def get_dataset_object(self, dataset_number):
        return self.dataset_object_cache[dataset_number]


def insert_proteins(dataframe):
    protein_ids = concatenate_lists(dataframe['protein_uniprot_ids'])
    protein_descriptions = concatenate_lists(dataframe['protein_descriptions'])

    protein_tuples_list = itertools.izip(protein_ids, protein_descriptions)

    for prot_id, prot_description in protein_tuples_list:
        Protein.objects.get_or_create(prot_id=prot_id,
                                      description=prot_description,
                                      name=prot_description)


def insert_peptides(dataframe):
    peptide_sequence_set = set(dataframe['peptide_sequence'])

    for peptide_sequence in peptide_sequence_set:
        Peptide.objects.get_or_create(sequence=peptide_sequence)


def insert_ptms(dataframe):
    modifications_list = concatenate_lists(dataframe['ptms_description'])

    for modification in modifications_list:
        Ptm.objects.get_or_create(description=modification)


def insert_datasets(dataframe, instrument, lodgement, experiment, confidence_cutoff):
    datasets = dataframe['ion_spectrum'].apply(spectrum_to_dataset_number)
    datasets.drop_duplicates()
    now = datetime.datetime.utcnow().replace(tzinfo=utc)

    for dataset_number in datasets:
        Dataset.objects.get_or_create(instrument=instrument,
                                      lodgement=lodgement,
                                      experiment=experiment,
                                      datetime=now,
                                      title=entitle_ds(dataset_number, lodgement.filename),
                                      confidence_cutoff=confidence_cutoff)


def entitle_ds(dsno, filename):
    return 'dataset #%s from %s' % (dsno, filename)


def insert_ions_row_by_row(dataframe, dataset, experiment):
    """ Deprecated - keeping around for benchmark comparison purposes
     Use insert_ions() instead which uses bulk_create
    """
    if not isinstance(dataset, Dataset):
        raise ValueError('dataset parameter needs to be of type Pepsite.models.Dataset')
    if not isinstance(experiment, Experiment):
        raise ValueError('dataset parameter needs to be of type Pepsite.models.Experiment')

    df = dataframe.itertuples()

    for row_tuple in df:
        Ion.objects.get_or_create(precursor_mass=row_tuple.ion_precursor_mass,
                                  mz=row_tuple.ion_mz,
                                  charge_state=row_tuple.ion_charge,
                                  spectrum=row_tuple.ion_spectrum,
                                  retention_time=row_tuple.ion_retention_time,
                                  experiment=experiment,
                                  dataset=dataset)


def insert_ions(dataframe, experiment):
    if not isinstance(experiment, Experiment):
        raise ValueError('dataset parameter needs to be of type Pepsite.models.Experiment')
    #  Abusing pandas function to remove duplicate ions - i.e mimicking get_or_create()
    dedup = dataframe[['ion_precursor_mass', 'ion_mz', 'ion_charge', 'ion_spectrum', 'ion_retention_time']]
    dedup.drop_duplicates(inplace=True)
    df = dedup.itertuples()
    ions_bulk_list = []

    dataset_cache = DatasetCache(experiment=experiment)

    for row_tuple in df:
        dataset = dataset_cache.get_dataset_object(spectrum_to_dataset_number(row_tuple.ion_spectrum))

        new_ion = Ion(precursor_mass=row_tuple.ion_precursor_mass,
                      mz=row_tuple.ion_mz,
                      charge_state=row_tuple.ion_charge,
                      spectrum=row_tuple.ion_spectrum,
                      retention_time=row_tuple.ion_retention_time,
                      experiment=experiment,
                      dataset=dataset)

        ions_bulk_list.append(new_ion)

    Ion.objects.bulk_create(ions_bulk_list)


def insert_idestimates(dataframe, experiment):
    """
    populating the foreign keys of each IdEstimate
    :param dataframe:
    :return:
    """
    df = dataframe.itertuples()
    protein_cache = ProteinCache()
    ptm_cache = PtmCache()
    peptide_cache = PeptideCache()
    ion_cache = IonCache(experiment=experiment)

    idestimate_list = []
    for row_tuple in df:
        proteins = [protein_cache.get_protein_object(protein_id)
                    for protein_id in row_tuple.protein_uniprot_ids]

        ptms = [ptm_cache.get_ptm_object(ptm) for ptm in row_tuple.ptms_description]

        peptide = peptide_cache.get_peptide_object(row_tuple.peptide_sequence)
        ion = ion_cache.get_ion_object(charge_state=row_tuple.ion_charge,
                                       mz=row_tuple.ion_mz,
                                       precursor_mass=row_tuple.ion_precursor_mass,
                                       retention_time=row_tuple.ion_retention_time)

        delta_mass = row_tuple.idestimate_delta_mass
        confidence = row_tuple.idestimate_confidence

        row_idestimate = IdEstimate.objects.create(delta_mass=delta_mass,
                                                   confidence=confidence,
                                                   peptide=peptide,
                                                   ion=ion)  # 2.

        for protein in proteins:
            row_idestimate.proteins.add(protein)

        if len(ptms):  # ptms are optional
            for ptm in ptms:
                row_idestimate.ptms.add(ptm)

        idestimate_list.append(row_idestimate)


def concatenate_lists(series):
    """
    Helper method for concatenating a list of lists into a single list
    :param series: A list of lists
    :return: A list containing all the elements in the input
    """
    return list(itertools.chain.from_iterable(series))


def spectrum_to_dataset_number(spectrum):
    """ Helper method that returns the dataset number for an experiment, given a spectrum string """
    return spectrum.split('.')[0]


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
        self.ptm_cache = PtmCache()
        self.ion_cache = IonCache()

    def _import_proteins(self):
        insert_proteins(self.dataframe)
        self.protein_cache.refresh_cache()

    def _import_ptms(self):
        insert_ptms(self.dataframe)
        self.ptm_cache.refresh_cache()

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


