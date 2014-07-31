# -*- coding: utf-8 -*-

"""
The ``filters`` module provides functions that filter the set of antecedent
candidates.
"""

from discoursegraphs.readwrite.conll import traverse_dependencies_up

import preferences


# TODO: review expletive verbs. (ex. "es ist neu; es gibt keine Milch")
EXPLETIVE_VERBS = {"sein", "regnen", "gelingen", "bestehen", "geben"}


def get_filtered_candidates(pocores, cand_list, (sent, word), sentence_dist,
                            verbose=False):
    """
    applies several filters to the list of potential antecedents.

    Parameters
    ----------
    pocores : Pocores
        an instance of the Pocores class
    cand_list : list of (int, int) tuples
        a list of potential antecedents, represented as
        (sentence index, word index) tuples
    (sent, word) : tuple of (int, int)
        the (sentence index, word index tuple) of the anaphora
    sentence_dist : int
        number of preceding sentences that will be looked at, i.e. the
        sentences that contain potential antecedents

    Returns
    -------
    filtered candidates : list of (int, int) tuples
        list of likely antecedents, represented as
        (sentence index, word index) tuples
    """
    raise NotImplementedError

def check_agreement(pocores, antecedent, anaphora):
    """
    Checks if an anaphora and a potential antecedent have morphological
    agreement.
    If the anaphora is a possessive, only the features person and gender are
    checked, otherwise gender, person and number.

    :param pocores: an instance of the Pocores class
    :type pocores: ``Pocores``
    :param antecedent: the antecedent's (sentence index, word index) tuple
    :type antecedent: ``tuple`` of (``int``, ``int``)
    :param anaphora: the anaphora's (sentence index, word index) tuple
    :type anaphora: ``tuple`` of (``int``, ``int``)

    :return: True, if antecedent and anaphora agree in gender,
    person (and number); False otherwise.
    :rtype: ``bool``
    """
    def check_feat(antecedent_dict, anaphora_dict, feat): #TODO add doctest
        """
        Checks if anaphora and antecedent share the same feature. The
        principle of underspecification is used, i.e. only if both words have a
        certain feature and disagree in it the agreement check is False.

        :param antecedent_dict: the feature dictionary of the antecedent
        :type antecedent_dict: ``dict`` with ``str`` keys and ``str`` or ``int``
         values
        :param anaphora_dict: the feature dictionary of the anaphora
        :type anaphora_dict: ``dict`` with ``str`` keys and ``str`` or ``int``
         values
        :return: False, if antecedent and anaphora disagree in a feature;
        True otherwise.
        :rtype: ``bool``
        """
        raise NotImplementedError
    raise NotImplementedError

def check_binding(pocores, antecedent, anaphor):
    """
    Checks if two words can be anaphora and antecedent by the binding
    principles of chomsky.
    The binding category is considered the (sub)clause of the anaphora.

    :param pocores: an instance of the Pocores class
    :type pocores: ``Pocores``
    :param antecedent: the antecedent's (sentence index, word index) tuple
    :type antecedent: ``tuple`` of (``int``, ``int``)
    :param anaphora: the anaphora's (sentence index, word index) tuple
    :type anaphora: ``tuple`` of (``int``, ``int``)

    :return: True, if antecedent can be bound by anaphora; False otherwise.
    :rtype: ``bool``
    """
    def get_binding_category(a): #TODO: describe binding categories better
        """
        Grammatical notions used by this function:

            - Deprel: dependency relation to the HEAD. the set of possible
            deprels depends on the original treebank annotation
                - PUNC: punctuation ("," or sentence final ".")
                - CD: relation involving conjunctions (e.g. und, doch, aber)?
        """
        raise NotImplementedError
    raise NotImplementedError

def check_semantik(pocores, antecedent, anaphor):
    """
    Placeholder
    """
    raise NotImplementedError

def is_coreferent(docgraph, antecedent_node, anaphora_node,
                  lemma_attrib='plemma'):
    """
    So far: checks if two words have the same lemma. (We're using this for
    basic anaphora resolution.)

    TODO: add real coreference resolution.

    Paramters
    ---------
    docgraph : ConllDocumentGraph
        document graph which contains the token
    antecedent_node : str
        the node ID of the antecedent
    anaphora_node : str
        the node ID of the anaphora (candidate)
    lemma_attrib : str
        the name of the CoNLL token column that contains the lemma information
        (usually ``phead``, but sometimes ``head`` depending on the version
        of mate-tools used to generate the input

    returns
    -------
    is_coreferent : bool
        True, if antecedent and anaphora share the same lemma. False
        otherwise.
    """
    return docgraph.node[antecedent_node][lemma_attrib] == \
        docgraph.node[anaphora_node][lemma_attrib]


def is_expletive(docgraph, token_node, lemma_attrib='plemma'):
    """
    Checks if a given token is an expletive.

    Paramters
    ---------
    docgraph : ConllDocumentGraph
        document graph which contains the token
    token_node : str
        the node ID of the token
    lemma_attrib : str
        the name of the CoNLL token column that contains the lemma information
        (usually ``phead``, but sometimes ``head`` depending on the version
        of mate-tools used to generate the input

    Returns
    -------
    is_expletive : bool
    """
    if docgraph.get_token(token_node) in (u'es', u'Es'):
        for lemma in traverse_dependencies_up(docgraph, token_node,
                                              node_attribute=lemma_attrib):
            if lemma in EXPLETIVE_VERBS:
                return True
    return False
