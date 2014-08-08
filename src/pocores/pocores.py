#!/usr/bin/env python
# -*- coding: utf-8 -*-
# needs python 2.7 or later version

import sys

from discoursegraphs.readwrite import ConllDocumentGraph

class Pocores(object):
    def __init__(self, document_graph):
        self.document = document_graph

        # ana_to_id maps from an anaphora (int sentence, int word) tuple
        # to its ID (int)
        self.ana_to_id = {}

        # TODO: explain self.entities ???
        # entities maps from a token ID (str) to a list of token IDs
        self.entities = {}

        # ana_to_ante maps from an anaphora token ID (str) to an antecedent token ID (str)
        self.ana_to_ante = {}

        # EXPLETIVE_VERBS: a list of german expletive verbs
        self.EXPLETIVE_VERBS = {"sein", "regnen", "gelingen", "bestehen", "geben"}

        # Class Variables # TODO: explain self.ref_id ???
        self.ref_id = 0 # Counter for Referents

        # contains the output of candidate filtering functions.
        # so far only used for debugging purposes
        self.filtered_results = OrderedDict()

        # entity grids (key: int sentence, value XXX
        # TODO: write entity grid description
        self.entity_grid = {}



if __name__ == '__main__':
    conll_file = sys.argv[1]
    pocoresgraph = ConllDocumentGraph(conll_file, conll_format='2010')
