__author__ = 'Gyfis'


dna = ['A', 'C', 'G', 'T', '*']
rna = ['A', 'C', 'G', 'U', '*']
protein = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y', '*']

rna2prot = {
    'GCA': 'A', 'GCC': 'A', 'GCG': 'A', 'GCU': 'A',
    'UGC': 'C', 'UGU': 'C',
    'GAC': 'D', 'GAU': 'D',
    'GAA': 'E', 'GAG': 'E',
    'UUC': 'F', 'UUU': 'F',
    'GGA': 'G', 'GGC': 'G', 'GGG': 'G', 'GGU': 'G',
    'CAC': 'H', 'CAU': 'H',
    'AUA': 'I', 'AUC': 'I', 'AUU': 'I',
    'AAA': 'K', 'AAG': 'K',
    'CUA': 'L', 'CUC': 'L', 'CUG': 'L', 'CUU': 'L', 'UUA': 'L', 'UUG': 'L',
    'AUG': 'M',
    'AAC': 'N', 'AAU': 'N',
    'CCA': 'P', 'CCC': 'P', 'CCG': 'P', 'CCU': 'P',
    'CAA': 'Q', 'CAG': 'Q',
    'AGA': 'R', 'AGG': 'R', 'CGA': 'R', 'CGC': 'R', 'CGG': 'R', 'CGU': 'R',
    'AGU': 'S', 'AGC': 'S', 'UCA': 'S', 'UCC': 'S', 'UCG': 'S', 'UCU': 'S',
    'ACA': 'T', 'ACC': 'T', 'ACG': 'T', 'ACU': 'T',
    'GUA': 'V', 'GUC': 'V', 'GUG': 'V', 'GUU': 'V',
    'UGG': 'W',
    'UAC': 'Y', 'UAU': 'Y',
    'UAA': '*', 'UAG': '*', 'UGA': '*'
}

dna2prot = {
    'GCA': 'A', 'GCC': 'A', 'GCG': 'A', 'GCT': 'A',
    'TGC': 'C', 'TGT': 'C',
    'GAC': 'D', 'GAT': 'D',
    'GAA': 'E', 'GAG': 'E',
    'TTC': 'F', 'TTT': 'F',
    'GGA': 'G', 'GGC': 'G', 'GGG': 'G', 'GGT': 'G',
    'CAC': 'H', 'CAT': 'H',
    'ATA': 'I', 'ATC': 'I', 'ATT': 'I',
    'AAA': 'K', 'AAG': 'K',
    'CTA': 'L', 'CTC': 'L', 'CTG': 'L', 'CTT': 'L', 'TTA': 'L', 'TTG': 'L',
    'ATG': 'M',
    'AAC': 'N', 'AAT': 'N',
    'CCA': 'P', 'CCC': 'P', 'CCG': 'P', 'CCT': 'P',
    'CAA': 'Q', 'CAG': 'Q',
    'AGA': 'R', 'AGG': 'R', 'CGA': 'R', 'CGC': 'R', 'CGG': 'R', 'CGT': 'R',
    'AGT': 'S', 'AGC': 'S', 'TCA': 'S', 'TCC': 'S', 'TCG': 'S', 'TCT': 'S',
    'ACA': 'T', 'ACC': 'T', 'ACG': 'T', 'ACT': 'T',
    'GTA': 'V', 'GTC': 'V', 'GTG': 'V', 'GTT': 'V',
    'TGG': 'W',
    'TAC': 'Y', 'TAT': 'Y',
    'TAA': '*', 'TAG': '*', 'TGA': '*'
}

monoiso_prot = {
    'A': 71.03711,
    'C': 103.00919,
    'D': 115.02694,
    'E': 129.04259,
    'F': 147.06841,
    'G': 57.02146,
    'H': 137.05891,
    'I': 113.08406,
    'K': 128.09496,
    'L': 113.08406,
    'M': 131.04049,
    'N': 114.04293,
    'P': 97.05276,
    'Q': 128.05858,
    'R': 156.10111,
    'S': 87.03203,
    'T': 101.04768,
    'V': 99.06841,
    'W': 186.07931,
    'Y': 163.06333
}

monoisotopic_water_mass = 18.01056