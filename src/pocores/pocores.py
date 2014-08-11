#!/usr/bin/env python
# -*- coding: utf-8 -*-
# needs python 2.7 or later version

import sys
from collections import defaultdict

from discoursegraphs.util import natural_sort_key
from discoursegraphs.readwrite import ConllDocumentGraph

class Pocores(object):
    def __init__(self, document_graph):
        self.document = document_graph

        # ana_to_id maps from an anaphora (int sentence, int word) tuple
        # to its ID (int)
        self.ana_to_id = {}

        # TODO: explain self.entities ???
        # entities maps from a token ID (str) to a list of token IDs
        self.entities = defaultdict(str)

        # ana_to_ante maps from an anaphora token ID (str) to an antecedent token ID (str)
        self.ana_to_ante = {}

        # EXPLETIVE_VERBS: a list of german expletive verbs
        self.EXPLETIVE_VERBS = {"sein", "regnen", "gelingen", "bestehen", "geben"}

        # Class Variables # TODO: explain self.ref_id ???
        # TODO: I'm trying to get rid of ref_ids altogether, check if there
        #       are any issues
        #~
        #~ self.ref_id = 0 # Counter for Referents

        # contains the output of candidate filtering functions.
        # so far only used for debugging purposes
        self.filtered_results = OrderedDict()

        # entity grids (key: int sentence, value XXX
        # TODO: write entity grid description
        self.entity_grid = {}

    def _get_candidates(self):
        """
        Returns list of all known discourse entities.

        TODO: implement `self.entities`, issue #2
        TODO: check if natural_sort_key also works for ``s1_t23``-like keys

        Returns
        -------
        candidates : list of str
            a sorted list of token node IDs
        """
        candidates = []
        for entity_node_id in self.entities:
            candidates += self.entities[entity_node_id]
        return sorted(candidates, key=natural_sort_key)

    def _store_new_referent(self, entity_node_id):
        """
        Adds a new discourse entity (represented by its token node ID) to the
        map of known entities.

        TODO: get rid of this function after refactoring! alternatively,
              rename it to add_new_entity()
        """
        self.entities[entity_node_id] = []
        return entity_node_id

    def _store_old_referent(self, token_node_id, entity_node_id):
        """
        Registers a token under the ID of an already known discourse
        entity.

        TODO: get rid of this function after refactoring! alternatively,
              rename it to add_token_to_entity()

        Params
        ------
        token_node_id : str
            ID of the token node to be added to an existing entity
        entity_node_id : str
            ID of the first token node that references this entity
        """
        self.entities[entity_node_id].append(token_node_id)
        return entity_node_id

    def _get_children(self, token_node_id):
        """
        Given a token (node ID), returns this token and all its children in the
        dependency structure (list of token node IDs).

        Parameters
        ----------
        token_node_id : str
            ID of the toke node whose children will be fetched
        """
        return sorted(traverse_dependencies_down(self.document, node_id),
                      key=natural_sort_key)
def traverse_dependencies_down(docgraph, node_id):
    """
    TODO: convert docgraph from multidigraph into digraph to avoid having
    to iterate over a single edge_id.
    """
    yield node_id
    for target in docgraph.edge[node_id]:
        if any(edge_attr['edge_type'] == EdgeTypes.dominance_relation
               for edge_id, edge_attr in docgraph.edge[node_id][target].iteritems()):
            for target_id in traverse_dependencies_down(docgraph, target):
                yield target_id


if __name__ == '__main__':
    conll_file = sys.argv[1]
    pocoresgraph = ConllDocumentGraph(conll_file, conll_format='2010')