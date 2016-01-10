import tables
__author__ = 'Gyfis'


def generate_histogram(sequence, type=0):
    table = tables.dna if type == 0 else tables.rna if type == 1 else tables.protein
    hist = {c: 0 for c in table}
    for c in sequence:
        hist[c] += 1
    return {c: hist[c] / float(len(sequence)) for c in hist}
