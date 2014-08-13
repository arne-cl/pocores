#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
pocores.py

Originally written by Tobias Günther.

Copyright (C) 2011 Tobias Günther, Christian Dittrich.
Copyright (C) 2012 Jonathan Sonntag, Arne Neumann.
Copyright (C) 2014 Arne Neumann. (major rewrite)

This program is free software;
you can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation;
either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, see <http://www.gnu.org/licenses/>.
"""

import sys
from collections import defaultdict, OrderedDict

from discoursegraphs import EdgeTypes, tokens2text
from discoursegraphs.util import natural_sort_key
from discoursegraphs.readwrite import ConllDocumentGraph

from pocores import cli, filters
from pocores import preferences as prefs


# TODO: evaluate weights
WEIGHTS = [8, 2, 8, 3, 2, 7, 0]
MAX_SENT_DIST = 4


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

        TODO: make noun_tags, pronoun_tags set constants for effienciency
        TODO: convert weights into a namedtuple
        """
        assert isinstance(weights, list), \
            'Weights should be a list, not a "{0}"'.format(type(weights))
        assert all([isinstance(weight, int) for weight in weights]), \
            'All weights should be integers, got "{0}" instead'.format(weights)
        assert len(weights) == 7, \
            'There should be 7 weights, not {0}'.format(len(weights))

        # TODO: explain/show, why these structures have to be reset
        self.entities.clear()
        self.ana_to_ante.clear()

        noun_tags = ("NN", "NE")
        pronoun_tags = ("PPER", "PRELS", "PRF", "PPOSAT", "PDS")

        for sent_id in self.document.sentences:
            for token_id in self.document.node[sent_id]['tokens']:
                tok_attrs = self.document.node[token_id]
                # Treatment of Nominals
                if (tok_attrs[pos_attrib] in noun_tags
                   and tok_attrs[deprel_attrib] != "PNC"):
                    self._resolve_nominal_anaphora(token_id)

                # Treatment of Pronominals
                elif (tok_attrs[pos_attrib] in pronoun_tags
                      and not filters.is_expletive(self.document, token_id)):
                    self._resolve_pronominal_anaphora(token_id, weights,
                                                      max_sent_dist)

    def _resolve_nominal_anaphora(self, anaphora):
        """
        Tries to resolve a given nominal anaphora.
        If this fails the given word is registered as a new discourse entity.

        Parameters
        ----------
        anaphora : str
            ID of the token node that represents the anaphora

        Returns
        -------
        anaphora_or_antecedent : str
            Returns the token node ID of the antecedent, iff an antecedent
            was found. Otherwise the input (i.e. the token node ID of the
            anaphora) is returned.
        """
        candidates_list = self._get_candidates()
        # iterate over antecedent candidates, starting from the closest
        # preceding one to the left-most one
        candidates_list.reverse()
        for antecedent in candidates_list:
            if filters.is_coreferent(self, antecedent, anaphora):
                self.entities[antecedent].append(anaphora)
                return antecedent

        if anaphora not in self.entities:
            self.entities[anaphora] = []
            return anaphora

    def _resolve_pronominal_anaphora(self, anaphora, weights, max_sent_dist, pos_attrib='ppos'):
        """
        Tries to resolve a given pronominal anaphora by applying different
        filters and preferences.
        For the weighting of the different preferences a list of weights has to
        be passed to the function. If resolution fails, the given pronoun is
        registered as a new discourse entity.

        This method relies on these grammatical categories:

            - PRELS: substitutive relative pronoun, e.g. [der Hund ,] der
            - PDS: substitutive demonstrative pronoun, e.g. dieser, jener

            - PPER: irreflexive personal pronoun, e.g. ich, er, ihm, mich, dir
            - PRF: reflexive personal pronoun, e.g. sich, einander, dich, mir
            - PPOSAT: attributive possesive pronoung, e.g. mein [Buch], deine [Mutter]

        @type anaphora: C{tuple} of (C{int}, C{int})
        @type weights: C{list} of 7 C{int}
        @param max_sent_dist: number of preceding sentences that will be looked at,
        i.e. the sentences that contain potential antecedents
        @type max_sent_dist: C{int}

        TODO: implement filters.get_filtered_candidates() to make this work
        TODO: provide documentation for scoring and/or convert weights into a namedtuple
        """
        cand_list = self._get_candidates()
        filtered_candidates = filters.get_filtered_candidates(self, cand_list, anaphora, max_sent_dist)

        if not filtered_candidates:
            self.entities[anaphora] = []
            return anaphora

        # Preferences
        candidate_dict = dict.fromkeys(filtered_candidates, 0)
        anaphora_pos = self.document.node[anaphora][pos_attrib]
        if anaphora_pos in set(["PRELS", "PDS"]):
            # chooses the most recent candidate, if the word is a substitutive
            # demonstrative/relative pronoun
            can = max(candidate_dict)

        if anaphora_pos in set(["PPER", "PRF", "PPOSAT"]):
            # scores the candidates, if the word is a personal pronoun or an
            # attributive possessive pronoun
            for can in candidate_dict:
                if prefs.check_parallelism(self, can, anaphora):
                    candidate_dict[can] += weights[0]
                if prefs.check_role(self, can, "SB"):
                    candidate_dict[can] += weights[1]
                if prefs.check_role(self, can, "OA"):
                    candidate_dict[can] += weights[2]
                if prefs.check_role(self, can, "DA"):
                    candidate_dict[can] += weights[3]
                candidate_dict[can] += weights[4] * math.log(prefs.get_chain_length(self, can))
                candidate_dict[can] -= weights[5] * prefs.get_distance(can, anaphora)
                candidate_dict[can] -= weights[6] * prefs.get_depth(self, can)
                # NOTE: additional preferences can be added here

            # Pick candidate with highest Score. If there are candidates with
            # the same score, pick closest
            antecedent = sorted([(v, k) for k, v in candidate_dict.iteritems()],
                         reverse=True)[0][1] # TODO: debug this after _get_candidates() works

        # TODO: add other pronoun resolution algorithm
        # if anaphora_pos in [OTHER PRONOUNS]:
            # antecedent = Result of OTHER PRONOUN RESOLUTION

        # Store Result
        self.ana_to_ante[anaphora] = antecedent # for Evaluation
        self.entities[antecedent].append(anaphora)
        return antecedent


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


def run_pocores_with_cli_arguments():
    parser, args = cli.parse_options()
    if args.input == None:
        parser.print_help()
        sys.exit(0)
    assert args.informat in ('2009', '2010')
    assert args.outformat in ('bracketed')

    docgraph = ConllDocumentGraph(args.input, conll_format=args.informat)
    pocores = Pocores(docgraph)

    weights = WEIGHTS
    if args.weights: # if set, use command line weights.
        weight_str_list = args.weights.split(',')
        try:
            weights = [int(weight) for weight in weight_str_list]
        except ValueError as e:
            print "Can't convert all weights to integers. {0}".format(e)

    max_sent_dist = MAX_SENT_DIST
    if args.max_sent_dist: # if set, use sentence distance set via cli
        try:
            max_sent_dist = int(args.max_sent_dist)
        except ValueError as e:
            print "max_sent_dist must be an integer. {0}".format(e)

    pocores.resolve_anaphora(weights, max_sent_dist)

    # currently, there's only one output format
    if args.outformat == 'bracketed':
        args.output_file.write(output_with_brackets(pocores))


if __name__ == '__main__':
    """
    parses command line arguments, runs coreference analysis and produdes output
    (stdout or file(s)).
    """
    run_pocores_with_cli_arguments()
