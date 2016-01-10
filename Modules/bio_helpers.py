__author__ = 'Gyfis'


def reverse_complement(s):
    return complement(reverse(s))


def reverse(s):
    return s[::-1]


def complement(s):
    return s.replace('A', 'B').replace('C', 'D').replace('G', 'C').replace('T', 'A').replace('D', 'G').replace('B', 'T')


def translate(s, table, i):
    splits = [s[k:k+i] for k in range(0, len(s) - i, i)]
    transl = ''
    for c in splits:
        transl += table[c]

    return transl


def dna2prot(dna):
    if len(dna) / 3.0 - len(dna) / 3 != 0:
        return False

    import tables

    prot = ''
    for a, b, c in zip(dna[::3], dna[1::3], dna[2::3]):
        prot += tables.dna2prot[a + b + c]
    return prot


def rna2prot(rna):
    if len(rna) / 3.0 - len(rna) / 3 != 0:
        return False

    import tables

    prot = ''
    for a, b, c in zip(rna[::3], rna[1::3], rna[2::3]):
        prot += tables.dna2prot[a + b + c]
    return prot


def rna2dna(rna):
    return rna.replace('U', 'T')


def dna2rna(dna):
    return dna.replace('T', 'U')
