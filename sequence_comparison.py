import logging
import sys
import argparse
from argparse import RawDescriptionHelpFormatter

from Modules import source_parser, alignment, bio_helpers, basic, platypus

__author__ = 'Gyfis'

data_path = 'data'


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s @%(asctime)s: %(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="""Compare two sequences easily, with multiple parameters.

Possible sources: (name: id)
    """ + source_parser.sources() + """
Possible formats: (name: id)
    """ + source_parser.formats() + """
Supported matrices: pam40, pam80, pam120, pam250, blosum62

parameters for global and local alignment search. Possibilities are
  - matrix_name ('pam120')
    - uses the specified matrix with default gap opening and extension values
  - matrix_name::gap_open,gap_extension ('pam120::-3,-2')
    - uses the specified matrix along with the gap opening and extension values
  - match,mismatch::gap_open,gap_extension ('1,-1::-2,-1')
    - uses the match,mismatch values and gap opening and extension values
""",
        formatter_class=RawDescriptionHelpFormatter)

    # try to find gibbs sampling of given length - parametrized

    parser.add_argument('sequence_a',
                        nargs='?',
                        default='UPI0000000001',
                        help='ID of the sequence A. Default is UPI0000000001.')
    parser.add_argument('sequence_b',
                        nargs='?',
                        default='UPI0000000002',
                        help='ID of the sequence B. Default is UPI0000000002.')

    parser.add_argument('-sa', '--source_a',
                        dest='source_a',
                        type=str,
                        metavar='',
                        default='uniprot_uniparc',
                        choices=source_parser.choices(),
                        help='name or id of the source for the sequence a')

    parser.add_argument('-fa', '--format_a',
                        dest='format_a',
                        type=str,
                        metavar='',
                        default='fasta',
                        choices=source_parser.format_choices(),
                        help='name or id of the format of the sequence a')

    parser.add_argument('-sb', '--source_b',
                        dest='source_b',
                        type=str,
                        metavar='',
                        default='uniprot_uniparc',
                        choices=source_parser.choices(),
                        help='name or id of the source for the sequence b')

    parser.add_argument('-fb', '--format_b',
                        dest='format_b',
                        type=str,
                        metavar='',
                        default='fasta',
                        choices=source_parser.format_choices(),
                        help='name or id of the format of the sequence b')

    parser.add_argument('-ga', '--global_alignment',
                        dest='global_alignment',
                        type=str,
                        metavar='',
                        nargs='*',
                        default=[])

    parser.add_argument('-la', '--local alignment',
                        dest='local_alignment',
                        type=str,
                        metavar='',
                        nargs='*',
                        default=[])

    # parsing of the command-line arguments
    args = parser.parse_args()
    # print(args)

    # sequence ids as command line arguments
    sequence_a = args.sequence_a
    sequence_b = args.sequence_b

    logging.info('Validating sources.')
    source_a = source_parser.parse_source(args.source_a, 'A')
    source_b = source_parser.parse_source(args.source_b, 'B')

    logging.info('Validating formats.')
    sequence_format_a = source_parser.parse_format(args.format_a, 'A')
    sequence_format_b = source_parser.parse_format(args.format_b, 'B')

    # source of sequences - if they can be found
    # by default, the parsers convert the sequences to upper-case
    logging.info('Initializing download of sequence A.')
    parsed_sequence_a = source_parser.get(sequence_a, source_a.name + '_' + str(sequence_a) + '.' + sequence_format_a.name,
                                          data_path,
                                          database=source_a,
                                          data_format=sequence_format_a)[0]
    logging.info('Initializing download of sequence B.')
    parsed_sequence_b = source_parser.get(sequence_b, source_b.name + '_' + str(sequence_b) + '.' + sequence_format_b.name,
                                          data_path,
                                          database=source_b,
                                          data_format=sequence_format_b)[0]

    seq_a_data = parsed_sequence_a['data']
    seq_b_data = parsed_sequence_b['data']

    # types: 0 - DNA, 1 - RNA, 2 - protein strings
    a_type = 0
    b_type = 0

    logging.info('Checking sequence types (DNA/RNA/protein).')
    if 'M' in seq_a_data:  # protein check
        a_type = 2
    elif 'U' in seq_a_data:
        a_type = 1

    if 'M' in seq_b_data:
        b_type = 2
    elif 'U' in seq_b_data:
        b_type = 1

    # now we have the sources, we want to unify the type: dna,rna,protein
    if a_type == 2 and b_type != 2:
        seq_b_prot = bio_helpers.rna2prot(seq_b_data) if b_type == 1 else bio_helpers.dna2prot(seq_b_data)
        if not seq_b_prot:
            logging.error('Sequence B is not transformable to protein strings and thus not comparable to sequence A. Aborting.')
            sys.exit()
        logging.info('Sequence B successfully transformed to protein string. Continuing with the calculation.')
        seq_b_data = seq_b_prot
        b_type = 2

    if b_type == 2 and a_type != 2:
        seq_a_prot = bio_helpers.rna2prot(seq_a_data) if a_type == 1 else bio_helpers.dna2prot(seq_a_data)
        if not seq_a_prot:
            logging.error('Sequence A is not transformable to protein strings and thus not comparable to sequence A. Aborting.')
            sys.exit()
        logging.info('Sequence A successfully transformed to protein string. Continuing with the calculation.')
        seq_a_data = seq_a_prot
        a_type = 2

    if a_type == 0 and b_type == 1:
        seq_b_data = bio_helpers.rna2dna(seq_b_data)
        b_type = 0
        logging.info('Sequence B successfully transformed from rna to dna. Continuing with the calculation.')
    if b_type == 0 and a_type == 1:
        seq_a_data = bio_helpers.rna2dna(seq_a_data)
        a_type = 0
        logging.info('Sequence A successfully transformed from rna to dna. Continuing with the calculation.')

    # now we have the unified sources, so we can initialize platypus and start creating the pdf

    logging.info('////////////////////////////////////////////////////////////////////////////////////////////////////')
    logging.info('Generating histograms for sequences.')
    # I'll show histograms of the sequences and their length
    hist_a = basic.generate_histogram(seq_a_data, a_type)
    hist_b = basic.generate_histogram(seq_b_data, b_type)
    len_a = len(seq_a_data)
    len_b = len(seq_b_data)
    summary = [{'len': len_a, 'hist': hist_a}, {'len': len_b, 'hist': hist_b}]
    platypus.init_summary(sequence_a, sequence_b, source_a.name, source_b.name, sequence_format_a.name, sequence_format_b.name, summary)

    logging.info('////////////////////////////////////////////////////////////////////////////////////////////////////')
    logging.info('Parsing global alignment arguments.')
    gas = args.global_alignment
    # global alignment - can have form of
    # -ga pam120 (table only)
    # -ga pam120::3,4 (table+go,ge)
    # -ga 1,2::3,4 (match,mismatch+go,ge)

    if gas is []:
        logging.info('No global alignment arguments found. Proceeding.')

    for ga in gas:
        if not '::' in ga:  # only a matrix
            logging.info('Generating global alignment with matrix: %s' % ga)
            calculated_ga = alignment.find_global_alignment_scoring_matrix(seq_a_data, seq_b_data, scoring_matrix=ga)
            header = 'matrix: %s' % ga
            ga_string = calculated_ga[1]
            ga_score = calculated_ga[2]
            platypus.add_global_alignment({'header': header, 'string': ga_string, 'score': ga_score})

        else:  # two parts
            parts = ga.split('::')
            if ',' not in parts[0]:  # matrix with a go,ge score
                goe = [int(x) for x in parts[1].split(',')]
                logging.info('Generating global alignment with matrix: %s, gap open penalty: %s, gap extension penalty: %s' % (parts[0], goe[0], goe[1]))
                calculated_ga = alignment.find_global_alignment_scoring_matrix_gaps(seq_a_data, seq_b_data,
                                                                                    scoring_matrix=parts[0],
                                                                                    go=goe[0],
                                                                                    ge=goe[1])
                header = 'matrix: %s, go: %s, ge: %s' % (parts[0], goe[0], goe[1])
                ga_string = calculated_ga[1]
                ga_score = calculated_ga[2]
                platypus.add_global_alignment({'header': header, 'string': ga_string, 'score': ga_score})

            else:
                match = [int(x) for x in parts[0].split(',')]
                goe = [int(x) for x in parts[1].split(',')]
                logging.info('Generating global alignment with match score: %s, mismatch score: %s, gap open penalty: %s, gap extension penalty: %s' % (match[0], match[1], goe[0], goe[1]))
                calculated_ga = alignment.find_global_alignment_match_mismatch(seq_a_data, seq_b_data,
                                                                               match=match[0],
                                                                               mismatch=match[1],
                                                                               go=goe[0],
                                                                               ge=goe[1])
                header = 'match: %s, mismatch: %s, go: %s, ge: %s' % (match[0], match[1], goe[0], goe[1])
                ga_string = calculated_ga[1]
                ga_score = calculated_ga[2]
                platypus.add_global_alignment({'header': header, 'string': ga_string, 'score': ga_score})

    logging.info('////////////////////////////////////////////////////////////////////////////////////////////////////')
    logging.info('Parsing local alignment arguments.')
    las = args.local_alignment
    # local_alignment - can have form of
    # -la pam120 (table only)
    # -la pam120::3,4 (table+go,ge)
    # -la 1,2::3,4 (match,mismatch+go,ge)

    if las is []:
        logging.info('No local alignment arguments found. Proceeding.')

    for la in las:
        if not '::' in la:  # only a matrix
            logging.info('Generating local alignment with matrix: %s' % la)
            calculated_la = alignment.find_local_alignment_scoring_matrix(seq_a_data, seq_b_data, scoring_matrix=la)
            header = 'matrix: %s' % la
            la_string = calculated_la[1]
            la_score = calculated_la[2]
            platypus.add_local_alignment({'header': header, 'string': la_string, 'score': la_score})

        else:  # two parts
            parts = la.split('::')
            if ',' not in parts[0]:  # matrix with a go,ge score
                goe = [int(x) for x in parts[1].split(',')]
                logging.info('Generating local alignment with matrix: %s, gap open penalty: %s, gap extension penalty: %s' % (parts[0], goe[0], goe[1]))
                calculated_la = alignment.find_local_alignment_scoring_matrix_gaps(seq_a_data, seq_b_data,
                                                                                    scoring_matrix=parts[0],
                                                                                    go=goe[0],
                                                                                    ge=goe[1])
                header = 'matrix: %s, go: %s, ge: %s' % (parts[0], goe[0], goe[1])
                la_string = calculated_la[1]
                la_score = calculated_la[2]
                platypus.add_local_alignment({'header': header, 'string': la_string, 'score': la_score})

            else:
                match = [int(x) for x in parts[0].split(',')]
                goe = [int(x) for x in parts[1].split(',')]
                logging.info('Generating local alignment with match score: %s, mismatch score: %s, gap open penalty: %s, gap extension penalty: %s' % (match[0], match[1], goe[0], goe[1]))
                calculated_la = alignment.find_local_alignment_match_mismatch(seq_a_data, seq_b_data,
                                                                               match=match[0],
                                                                               mismatch=match[1],
                                                                               go=goe[0],
                                                                               ge=goe[1])
                header = 'match: %s, mismatch: %s, go: %s, ge: %s' % (match[0], match[1], goe[0], goe[1])
                la_string = calculated_la[1]
                la_score = calculated_la[2]
                platypus.add_local_alignment({'header': header, 'string': la_string, 'score': la_score})

    logging.info('////////////////////////////////////////////////////////////////////////////////////////////////////')
    logging.info('Building the output pdf.')

    platypus.build()
    logging.info('////////////////////////////////////////////////////////////////////////////////////////////////////')





