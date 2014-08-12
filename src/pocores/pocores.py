#!/usr/bin/env python
# -*- coding: utf-8 -*-
# needs python 2.7 or later version

import sys
from collections import defaultdict, OrderedDict

from discoursegraphs import EdgeTypes, tokens2text
from discoursegraphs.util import natural_sort_key
from discoursegraphs.readwrite import ConllDocumentGraph

from pocores import filters


class Pocores(object):
    def __init__(self, document_graph):
        self.document = document_graph

        # TODO: explain self.entities ???
        # entities maps from a token ID (str) to a list of token IDs
        self.entities = defaultdict(str)

        # ana_to_ante maps from an anaphora token ID (str) to an
        # antecedent token ID (str)
        self.ana_to_ante = {}

        # EXPLETIVE_VERBS: a list of german expletive verbs
        self.EXPLETIVE_VERBS = {"sein", "regnen", "gelingen", "bestehen",
                                "geben"}

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

    def _get_children(self, token_node_id):
        """
        Given a token (node ID), returns this token and all its children in the
        dependency structure (list of token node IDs).

        Parameters
        ----------
        token_node_id : str
            ID of the toke node whose children will be fetched
        """
        return sorted(traverse_dependencies_down(self.document, token_node_id),
                      key=natural_sort_key)

    def _get_word(self, token_node_id):
        """
        returns the token (string) that a token node ID represents.

        TODO: rename to get_token()
        """
        return self.document.get_token(token_node_id)

    def _get_wordlist(self, token_node_ids, verbose=False):
        """
        Returns a list of tokens, either as a list of word strings or as a list
        of (token string, token node ID) tuples.
        """
        if not verbose:
            return (self._get_word(tni) for tni in token_node_ids)
        else:
            return ((self._get_word(tni), tni) for tni in token_node_ids)

    def _get_sentence(self, sent_id):
        """
        returns the sentence (string) that is referred to by a sentence ID

        Parameters
        ----------
        sent_id : int or str
            the node ID of a sentence (e.g. 's1') or the equivalent sentence
            index (e.g. 1)
        """
        assert isinstance(sent_id, (int, str))
        sid = sent_id if isinstance(sent_id, str) else 's{}'.format(sent_id)
        return tokens2text(self.document, self.document.node[sid]['tokens'])

    def _get_coref_chains(self):
        """
        returns the coreference chain for each anaphora/entity.

        Returns
        -------
        coref_chains : list of lists of (str, str) tuples
            a list of coreference chain lists. each coreference chain is
            represented by an ordered list of (token string, token node ID)
            tuples

        TODO: implement self.entities; issue #2
        """
        return [self._get_wordlist(self.entities[i], verbose=True)
                for i in self.entities.keys()]

    def print_entity_grid(self, min_coref_chain_length=2,
                          deprel_attrib='pdeprel'):
        """
        prints all coreference chains, including the grammatical function of
        anaphora and potential antecedents.

        TODO: implement self.entities; issue #2
        """
        for coref_chain in self._get_coref_chains():
            if len(coref_chain) >= min_coref_chain_length:
                # node ID of the first token in the chain
                print "\n\nEntity '{0}':".format(coref_chain[0][1])
                for (token, node_id) in coref_chain:
                    token_dict = self.document.node[node_id]
                    sent_index = token_dict['sent_pos']
                    deprel = token_dict[deprel_attrib]
                    print ("\t{0} in sentence {1} with function "
                           "'{2}'".format(token, sent_index, deprel))

    def _get_entity_grid(self, min_coref_chain_length=2,
                         deprel_attrib='pdeprel'):
        """
        returns the entity grid as a dictionary.

        TODO: describe the entity grid
        """
        coref_chains = [chain for chain in self._get_coref_chains()
                        if len(chain) >= min_coref_chain_length]
        for sent_id in self.document.sentences:
            self.entity_grid[sent_id] = defaultdict(list)

        for chain_index, coref_chain in enumerate(coref_chains):
            for (token, node_id) in coref_chain:
                token_dict = self.document.node[node_id]
                sent_index = token_dict['sent_pos']
                deprel = token_dict[deprel_attrib]
                self.entity_grid[sent_index][chain_index].append(deprel)
        return self.entity_grid, coref_chains

    def resolve_anaphora(self, weights, max_sent_dist=4, pos_attrib='ppos',
                         deprel_attrib='pdeprel'):
        """
        Resolves all nominal and pronominal anaphora in the text (stored in the
        classes sentence dictionary).
        Takes a list of weights as argument, which is passed on to the function
        for pronominal resolution.

        Parameters
        ----------
        weights : list of int
            list of 7 weights that will be used for ranking anaphora candidates
        max_sent_dist: int
            number of preceding sentences that will be looked at, i.e. the
            sentences that contain potential antecedents
        """
        assert isinstance(weights, list), \
            'Weights should be a list, not a "{0}"'.format(type(weights))
        assert all([isinstance(weight, int) for weight in weights]), \
            'All weights should be integers, got "{0}" instead'.format(weights)
        assert len(weights) == 7, \
            'There should be 7 weights, not {0}'.format(len(weights))

        self.entities.clear()
        self.ana_to_ante.clear()

        noun_tags = ("NN", "NE")
        pronoun_tags = ("PPER", "PRELS", "PRF", "PPOSAT", "PDS")

        for sent_id in self.document.sentences:
            for token_id in self.document.sentences[sent_id]['tokens']:
                tok_attrs = self.document.node[token_id]
                # Treatment of Nominals
                if (tok_attrs[pos_attrib] in noun_tags
                   and tok_attrs[deprel_attrib] != "PNC"):
                    self._resolve_nominal_anaphora(token_id)

                # Treatment of Pronominals
                elif (tok_attrs[pos_attrib] in pronoun_tags
                      and not filters.is_expletive(self, token_id)):
                    self._resolve_pronominal_anaphora(token_id, weights,
                                                      max_sent_dist)


def traverse_dependencies_down(docgraph, node_id):
    """
    TODO: convert docgraph from multidigraph into digraph to avoid having
    to iterate over a single edge_id.
    """
    yield node_id
    out_edges = docgraph.edge[node_id]
    for target in out_edges:
        if any(edge_attr['edge_type'] == EdgeTypes.dominance_relation
               for edge_id, edge_attr in out_edges[target].iteritems()):
            for target_id in traverse_dependencies_down(docgraph, target):
                yield target_id


if __name__ == '__main__':
    conll_file = sys.argv[1]
    pocoresgraph = ConllDocumentGraph(conll_file, conll_format='2010')
