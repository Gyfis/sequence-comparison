import logging
import sys
import os
from f_fasta import load_file
from files import download_file
from enum import Enum


__author__ = 'Gyfis'


class DataFormat(Enum):
    fasta = 1

    def extension(self):
        if self is DataFormat.fasta:
            return '.fasta'

    def parse(self, filepath):
        if self is DataFormat.fasta:
            return load_file(open(filepath))


class Databases(Enum):
    uniprot = 1
    uniprot_uniprot = 1.1
    uniprot_uniparc = 1.2

    ncbi = 2
    ncbi_nuccore = 2.1

    ebi = 3
    ebi_ena = 3.1
    ebi_interpro = 3.2

    ddbj = 4

    def url(self, data_id, data_format):
        if self is Databases.uniprot_uniprot or self is Databases.uniprot:
            return 'http://www.uniprot.org/uniprot/' + str(data_id) + data_format.extension()
        elif self is Databases.uniprot_uniparc:
            return 'http://www.uniprot.org/uniparc/' + str(data_id) + data_format.extension()
        elif self is Databases.ncbi_nuccore or self is Databases.ncbi:
            return 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=%s&rettype=%s' % (data_id, data_format.name)
        elif self is Databases.ebi_ena or self is Databases.ebi:
            return 'http://www.ebi.ac.uk/ena/data/view/%s&display=%s' % (data_id, data_format.name)
        elif self is Databases.ebi_interpro:
            return 'http://www.ebi.ac.uk/interpro/protein/%s?export=%s' % (data_id, data_format.name)
        elif self is Databases.ddbj:
            return 'http://getentry.ddbj.nig.ac.jp/getentry/na/%s/?format=%s' % (data_id, data_format.name)


def get(data_id, filename, path, data_format, database):
    url = database.url(data_id, data_format)
    filepath = download_file(url, filename, path)
    return data_format.parse(filepath)


def sources():
    s = """"""
    choices = []
    for database in Databases:
        if '_' in database.name:
            if database.name.split('_')[0] not in choices:
                choices.append(database.name.split('_')[0])
                s += database.name.split('_')[0] + ': ' + str(database.value).split('.')[0] + """
    """
        if database.name not in choices:
            choices.append(database.name)
            s += database.name + ': ' + str(database.value) + """
    """
    return s


def formats():
    s = """"""
    for format in DataFormat:
        s += format.name + ': ' + str(format.value) + """
    """
    return s


def choices():
    choices = []
    for database in Databases:
        name = database.name
        value = database.value
        if '_' in name:
            split_name = name.split('_')
            if split_name[0] not in choices:
                choices.append(split_name[0])
            split_value = str(value).split('.')[0]
            if split_value not in choices:
                choices.append(split_value)
        choices.append(name)
        choices.append(str(value))
    return choices


def format_choices():
    choices = []
    for f in DataFormat:
        choices.append(f.name)
        choices.append(str(f.value))
    return choices


def parse_source(source, name):
    if source not in choices():
        logging.error('Source %s not supported. Aborting.' % name)
        sys.exit()
    if source.isdigit():
        source = Databases(int(source))
    elif '.' in source:
        source = Databases(float(source))
    else:
        source = Databases[source]
    return source


def parse_format(sequence_format, name):
    if sequence_format not in format_choices():
        logging.error('Format %s not supported. Aborting.' % name)
        sys.exit()
    if sequence_format.isdigit():
        sequence_format = DataFormat(int(sequence_format))
    else:
        sequence_format = DataFormat[sequence_format]
    return sequence_format
