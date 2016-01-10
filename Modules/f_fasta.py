__author__ = 'Gyfis'


def load_file(f, close=True):
    pieces = []
    piece = {}

    for l in f:
        if l[0] == '>':
            if piece != {}:
                pieces.append(piece)
            piece = {
                'head': l[1:].strip(),
                'data': ''
            }
        else:
            piece['data'] += l.strip().upper()

    pieces.append(piece)

    if close:
        f.close()

    return pieces


def load_string(f):
    return load_file(f.strip().splitlines(), close=False)


class Node:

    def __init__(self, p_data):
        self.head = p_data['head']
        self.data = p_data['data']
        self.siblings = []

    def append(self, p_node):
        self.siblings.append(p_node)
