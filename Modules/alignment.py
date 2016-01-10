from enum import Enum
import numpy as np
import pickle

__author__ = 'Gyfis'


class ScoringMatrix(Enum):
    BLOSUM62 = 1
    PAM40 = 5
    PAM80 = 6
    PAM120 = 7
    PAM250 = 8

    def gap_opening_penalty(self):
        return {
            ScoringMatrix.BLOSUM62: -11,
            ScoringMatrix.PAM40: -10,
            ScoringMatrix.PAM80: -10,
            ScoringMatrix.PAM120: -11,
            ScoringMatrix.PAM250: -12,
        }[self]

    def gap_extension_penalty(self):
        return {
            ScoringMatrix.BLOSUM62: -4,
            ScoringMatrix.PAM40: -2,
            ScoringMatrix.PAM80: -2,
            ScoringMatrix.PAM120: -8,
            ScoringMatrix.PAM250: -4
        }[self]

    def get_matrix(self):
        return pickle.load(open({
            ScoringMatrix.BLOSUM62: 'scoring_matrices/blosum62.p',
            ScoringMatrix.PAM40: 'scoring_matrices/pam40.p',
            ScoringMatrix.PAM80: 'scoring_matrices/pam80.p',
            ScoringMatrix.PAM120: 'scoring_matrices/pam120.p',
            ScoringMatrix.PAM250: 'scoring_matrices/pam250.p',
        }[self], 'rb'))


__default_alignment_width = 100


def find_global_alignment_scoring_matrix(sequence_a, sequence_b, scoring_matrix='pam120', alignment_print_width=__default_alignment_width):
    scoring_matrix = ScoringMatrix[scoring_matrix.upper()]
    return _find_global_alignment(sequence_a, sequence_b,
                                  scoring_matrix.gap_opening_penalty(),
                                  scoring_matrix.gap_extension_penalty(),
                                  scoring_matrix.get_matrix(),
                                  None,
                                  None,
                                  alignment_print_width=alignment_print_width)


def find_global_alignment_scoring_matrix_gaps(sequence_a, sequence_b, scoring_matrix='pam120', go=-11, ge=-8, alignment_print_width=__default_alignment_width):
    scoring_matrix = ScoringMatrix[scoring_matrix.upper()]
    return _find_global_alignment(sequence_a, sequence_b, go, ge, scoring_matrix.get_matrix(), None, None, alignment_print_width=alignment_print_width)


def find_global_alignment_match_mismatch(sequence_a, sequence_b, match, mismatch, go, ge, alignment_print_width=__default_alignment_width):
    return _find_global_alignment(sequence_a, sequence_b, go, ge, None, match, mismatch, alignment_print_width=alignment_print_width)


def _find_global_alignment(sequence_a, sequence_b, go, ge, scoring_matrix, match, mismatch, alignment_print_width):
    infinity = -100000

    lenA = len(sequence_a) + 1
    lenB = len(sequence_b) + 1

    table = np.zeros((lenA, lenB, 2), dtype=np.int)
    backtrace = np.zeros((lenA, lenB, 2, 3), dtype=np.int)

    table[0, 0, 0] = 0
    table[0, 0, 1] = infinity

    for i in xrange(1, lenA):
        table[i, 0, 0] = infinity
        table[i, 0, 1] = go + ge * (i - 1)

    for j in xrange(1, lenB):
        table[0, j, 0] = infinity
        table[0, j, 1] = go + ge * (j - 1)

    for i in xrange(1, lenA):
        for j in xrange(1, lenB):
            si = i - 1
            sj = j - 1

            score = scoring_matrix[sequence_a[si], sequence_b[sj]] if match is None else match if sequence_a[si] == sequence_b[sj] else mismatch

            table[i, j, 0] = max(table[i - 1, j - 1, 0] + score, table[i - 1, j - 1, 1] + score)
            table[i, j, 1] = max(table[i - 1, j, 0] + go, table[i - 1, j, 1] + ge, table[i, j - 1, 0] + go, table[i, j - 1, 1] + ge)

            max_score = table[i - 1, j - 1, 0] + score
            backtrace[i, j, 0] = [i - 1, j - 1, 0]
            if table[i - 1, j - 1, 1] + score > max_score:
                backtrace[i, j, 0] = [i - 1, j - 1, 1]

            max_score = table[i - 1, j, 0] + go
            backtrace[i, j, 1] = [i - 1, j, 0]
            if table[i - 1, j, 1] + ge > max_score:
                max_score = table[i - 1, j, 1] + ge
                backtrace[i, j, 1] = [i - 1, j, 1]
            if table[i, j - 1, 0] + go > max_score:
                max_score = table[i, j - 1, 0] + go
                backtrace[i, j, 1] = [i, j - 1, 0]
            if table[i, j - 1, 1] + ge > max_score:
                backtrace[i, j, 1] = [i, j - 1, 1]

    i = lenA - 1
    j = lenB - 1
    k = 0 if table[i, j, 0] > table[i, j, 1] else 1

    score = table[i, j, k]
    alignment = []
    while (i, j) != (0, 0):

        pi, pj, pk = tuple(backtrace[i, j, k])

        if pi == i:
            alignment.append(('-', sequence_b[j - 1]))
        elif pj == j:
            alignment.append((sequence_a[i - 1], '-'))
        else:
            alignment.append((sequence_a[i - 1], sequence_b[j - 1]))

        if pi == 0 and pj != 0:
            j = pj - 1
            while j != 0:
                alignment.append(('-', sequence_b[j - 1]))
                j -= 1
            break

        if pj == 0 and pi != 0:
            i = pi - 1
            while i != 0:
                alignment.append((sequence_a[i - 1], '-'))
                i -= 1
            break

        if pi == 0 and pj == 0:
            break

        i, j, k = pi, pj, pk

    alignment = alignment[::-1]

    curent_print_width = 0

    s_alignment = ''

    while curent_print_width < len(alignment):
        s_alignment += '<br><br></br></br>' + ''.join([a for a, b in alignment[curent_print_width:curent_print_width + alignment_print_width]])
        s_alignment += '<br></br>' + ''.join([b for a, b in alignment[curent_print_width:curent_print_width + alignment_print_width]])
        curent_print_width += alignment_print_width

    return alignment, s_alignment, score


def find_local_alignment_scoring_matrix(sequence_a, sequence_b, scoring_matrix='pam120', alignment_print_width=__default_alignment_width):
    scoring_matrix = ScoringMatrix[scoring_matrix.upper()]
    return _find_local_alignment(sequence_a, sequence_b,
                                  scoring_matrix.gap_opening_penalty(),
                                  scoring_matrix.gap_extension_penalty(),
                                  scoring_matrix.get_matrix(),
                                  None,
                                  None,
                                  alignment_print_width=alignment_print_width)


def find_local_alignment_scoring_matrix_gaps(sequence_a, sequence_b, scoring_matrix='pam120', go=-11, ge=-8, alignment_print_width=__default_alignment_width):
    scoring_matrix = ScoringMatrix[scoring_matrix.upper()]
    return _find_local_alignment(sequence_a, sequence_b, go, ge, scoring_matrix.get_matrix(), None, None, alignment_print_width=alignment_print_width)


def find_local_alignment_match_mismatch(sequence_a, sequence_b, match, mismatch, go, ge, alignment_print_width=__default_alignment_width):
    return _find_local_alignment(sequence_a, sequence_b, go, ge, None, match, mismatch, alignment_print_width=alignment_print_width)


def _find_local_alignment(sequence_a, sequence_b, go, ge, scoring_matrix, match, mismatch, alignment_print_width):
    infinity = -100000

    lenA = len(sequence_a) + 1
    lenB = len(sequence_b) + 1

    table = np.zeros((lenA, lenB, 2), dtype=np.int)
    backtrace = np.zeros((lenA, lenB, 2, 3), dtype=np.int)

    table[0, 0, 0] = 0
    table[0, 0, 1] = infinity

    for i in xrange(1, lenA):
        table[i, 0, 0] = infinity
        table[i, 0, 1] = go + ge * (i - 1)

    for j in xrange(1, lenB):
        table[0, j, 0] = infinity
        table[0, j, 1] = go + ge * (j - 1)

    for i in xrange(1, lenA):
        for j in xrange(1, lenB):
            si = i - 1
            sj = j - 1

            score = scoring_matrix[sequence_a[si], sequence_b[sj]] if match is None else match if sequence_a[si] == sequence_b[sj] else mismatch

            table[i, j, 0] = max(table[i - 1, j - 1, 0] + score, table[i - 1, j - 1, 1] + score, 0)
            table[i, j, 1] = max(table[i - 1, j, 0] + go, table[i - 1, j, 1] + ge, table[i, j - 1, 0] + go, table[i, j - 1, 1] + ge, 0)

            max_score = table[i - 1, j - 1, 0] + score
            backtrace[i, j, 0] = [i - 1, j - 1, 0]
            if table[i - 1, j - 1, 1] + score > max_score:
                backtrace[i, j, 0] = [i - 1, j - 1, 1]

            max_score = table[i - 1, j, 0] + go
            backtrace[i, j, 1] = [i - 1, j, 0]
            if table[i - 1, j, 1] + ge > max_score:
                max_score = table[i - 1, j, 1] + ge
                backtrace[i, j, 1] = [i - 1, j, 1]
            if table[i, j - 1, 0] + go > max_score:
                max_score = table[i, j - 1, 0] + go
                backtrace[i, j, 1] = [i, j - 1, 0]
            if table[i, j - 1, 1] + ge > max_score:
                backtrace[i, j, 1] = [i, j - 1, 1]

    max_score = -1
    max_i = 0
    max_j = 0
    max_k = 0
    for i in xrange(len(sequence_a)):
        for j in xrange(len(sequence_b)):
            if max_score < table[i, j, 0]:
                max_score = table[i, j, 0]
                max_i, max_j, max_k = i, j, 0
            if max_score < table[i, j, 1]:
                max_score = table[i, j, 1]
                max_i, max_j, max_k = i, j, 1

    i = max_i
    j = max_j
    k = max_k

    alignment = []
    while table[i, j, k] > 0:

        pi, pj, pk = tuple(backtrace[i, j, k])

        if pk == 0:
            alignment.append((sequence_a[i - 1], sequence_b[j - 1]))
        elif pi == i:
            alignment.append(('-', sequence_b[j - 1]))
        else:
            alignment.append((sequence_a[i - 1], '-'))

        if pi == 0 and pj != 0:
            while pj != 0:
                alignment.append(('-', sequence_b[pj - 1]))
                pj -= 1
            break

        if pj == 0 and pi != 0:
            while pi != 0:
                alignment.append((sequence_a[pi - 1], '-'))
                pi -= 1
            break

        if pi == 0 and pj == 0:
            break

        i, j, k = pi, pj, pk

    alignment = alignment[::-1]

    curent_print_width = 0

    s_alignment = ''

    while curent_print_width < len(alignment):
        s_alignment += '<br><br></br></br>' + ''.join([a for a, b in alignment[curent_print_width:curent_print_width + alignment_print_width]])
        s_alignment += '<br></br>' + ''.join([b for a, b in alignment[curent_print_width:curent_print_width + alignment_print_width]]) + '\n'
        curent_print_width += alignment_print_width

    return alignment, s_alignment, max_score



