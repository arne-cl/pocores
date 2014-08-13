# -*- coding: utf-8 -*-

"""
The ``filters`` module provides functions that filter the set of antecedent
candidates.
"""

import re

from discoursegraphs.readwrite.conll import traverse_dependencies_up


# TODO: review expletive verbs. (ex. "es ist neu; es gibt keine Milch")
EXPLETIVE_VERBS = {"sein", "regnen", "gelingen", "bestehen", "geben"}
SENT_REGEX = re.compile('s(\d+)_t\d+')


def get_filtered_candidates(pocores, candidates, anaphora, sentence_dist,
                            verbose=False, pos_attrib='ppos'):
    """
    applies several filters to the list of potential antecedents.

    Parameters
    ----------
    pocores : Pocores
        an instance of the Pocores class
    candidates : list of str
        a list of potential antecedents, represented by their token node IDs
    anaphora : str
        token node ID of the anaphora
    sentence_dist : int
        number of preceding sentences that will be looked at, i.e. the
        sentences that contain potential antecedents

    Returns
    -------
    filtered candidates : list of (int, int) tuples
        list of likely antecedents, represented as
        (sentence index, word index) tuples
    """
    results_dict = pocores.filtered_results[anaphora] = {}

    nearby_cands = (can for can in candidates
                               if distance(can, anaphora) <= sentence_dist)
    results_dict["distance"] = (nearby_cands,
        "Candidates mentioned no more than %i sentences ago" % sentence_dist)

    non_reflexive = (can for can in nearby_cands
                 if pocores.node_attrs(can)[pos_attrib] != "PRF")
    results_dict["non_reflexive"] = (non_reflexive,
        ("Candidates that don't represent reflexive personal pronouns, "
         "e.g. sich, einander, dich, mir"))

    agreeing_cands = (can for can in non_reflexive
                                if morph_agreement(pocores, can, anaphora))
    results_dict["agreement"] = (agreeing_cands,
    ("Candidates in morphological agreement with the anaphora"))

    bound_cands = (can for can in agreeing_cands
                        if is_bound(pocores, can, anaphora))
    results_dict["binding"] = (bound_cands,
        "Candidates that can be bound by the anaphora")

    if verbose == True:
        print ("\n\n*** potential candidates for the anaphora "
                "'{0}' ({1}) in the sentence '{2}'"
                "***\n".format(pocores._get_word(anaphora),
                               anaphora, pocores._get_sentence(sent)))
        for filter_name in results_dict.keys():
            candidate_list, filter_description = results_dict[filter_name]
            print "{0}:\n\t{1}\n".format(filter_description,
                    pocores._get_wordlist(candidate_list, verbose=True))
    # we need to return a list instead of a generator, because generators are
    # considered ``True`` even if they're 'empty'!
    return list(bound_cands)


def distance(token_node_id1, token_node_id2):
    """
    Returns sentence distance between to given words.

    >>> get_distance('s1_t2', 's5_t4')
    4
    >>> get_distance('s1_t2', 's1_t9')
    0
    """
    sent1 = int(SENT_REGEX.match(token_node_id1).groups()[0])
    sent2 = int(SENT_REGEX.match(token_node_id2).groups()[0])
    return abs(sent1 - sent2)


def morph_agreement(pocores, antecedent_node, anaphora_node):
    """
    Checks if an anaphora and a potential antecedent have morphological
    agreement.
    If the anaphora is a possessive, only the features person and gender are
    checked, otherwise gender, person and number.

    Parameters
    ----------
    pocores : Pocores
        an instance of the Pocores class
    antecedent_node : str
        the node ID of the antecedent
    anaphora_node : str
        the node ID of the anaphora (candidate)

    Returns
    -------
    agreement : bool
        True, iff there's morphological agreement between the two tokens
    """
    antecedent = pocores.node_attrs(antecedent_node)
    anaphora = pocores.node_attrs(anaphora_node)

    def feature_agreement(antecedent_dict, anaphora_dict, feat):
        """
        Checks if anaphora and antecedent share the same feature. The
        principle of underspecification is used, i.e. only if both words have a
        certain feature and disagree in it the agreement check is False.

        Parameters
        ----------
        antecedent_dict : dict
            dict containing the features of the antecedent token node
        anaphora_dict : dict
            dict containing the features of the anaphora token node
        feat : str
            the name of the feature whose values shall be compared

        Returns
        -------
        feature_agreement : bool
            False, if antecedent and anaphora disagree in a feature;
            True otherwise.
        """
        if (feat in antecedent_dict and feat in anaphora_dict):
            # TODO: fix issue #1 (underspecified features)
            if antecedent_dict[feat] != anaphora_dict[feat]:
                return False
        return True

    #TODO: implement discoursegraphs issue #71 to make this work
    for feat in ("gender", "person", "number"):
        if not feature_agreement(antecedent, anaphora, feat):
            return False
    return True


def is_bound(pocores, entity_map, antecedent_id, anaphora_id,
             deprel_attrib='pdeprel', pos_attrib='ppos'):
    """
    Checks if two words can be anaphora and antecedent by the binding
    principles of chomsky.
    The binding category is considered the (sub)clause of the anaphora.

    TODO: fix #2 to make this work

    Parameters
    ----------
    pocores : Pocores
        an instance of the Pocores class
    antecedent_id : str
        the node ID of the antecedent
    anaphora_id : str
        the node ID of the anaphora (candidate)

    Returns
    -------
    agreement : bool
        True, iff there's morphological agreement between the two tokens
    """
    antecedent = pocores.node_attrs(antecedent_node)
    anaphora = pocores.node_attrs(anaphora_node)

    def anaphora_boundaries(anaphora, entity_map, deprel_attrib,
                            pos_attrib):
        """
        TODO: describe binding categories better

        Parameters
        ----------
        anaphora : dict
            dict that contains features of the anaphora (candidate)

        Returns
        -------
        boundaries : (str, str) tuple
            tuple referencing the word positions of the anaphora's boundaries
            (left boundary token ID, right boundary token ID)

        Grammatical notions used by this function:

            - Deprel: dependency relation to the HEAD. the set of possible
            deprels depends on the original treebank annotation
                - PUNC: punctuation ("," or sentence final ".")
                - CD: relation involving conjunctions (e.g. und, doch, aber)?
        """
        ana_sent_id, ana_word_pos = anaphora['sent_pos'], anaphora['word_pos']
        sent_length = len(pocores.node_attrs('s{}'.format(ana_sent_id)]['tokens']))
        begin = 1
        end = sent_length

        # find left boundary of the anaphora
        # by iterating backwards from the anaphora's word position to the
        # beginning of the sentence
        for word_pos in range(ana_word_pos, 0, -1):
            token_id = tokentuple2id(ana_sent_id, word_pos)
            if pocores.node_attrs(token_id)[deprel_attrib] in ("PUNC", "CD"):
                begin = word_pos
                break

        # find right boundary of the anaphora
        # by iterating from the anaphora's word position to the end of the
        # sentence
        for word_pos in range(ana_word_pos, sent_length, 1):
            token_id = tokentuple2id(ana_sent_id, word_pos)
            if pocores.node_attrs(token_id)[deprel_attrib] in ("PUNC", "CD"):
                end = word_pos
                break

        left_limit = tokentuple2id(ana_sent_id, begin)
        right_limit = tokentuple2id(ana_sent_id, end)
        return (left_limit, right_limit)

    left_limit, right_limit = anaphora_boundaries(anaphora, deprel_attrib)

    # binding principle 1
    if anaphora[pos_attrib] == "PRF":
        if ((anaphora['sent_pos'] != antecedent['sent_pos'])
           or (antecedent['word_pos'] not in range(left_limit, right_limit))):
            return False

    # binding principle 2
    if (anaphora[pos_attrib] == "PPER"
       and antecedent[pos_attrib] not in ("PRF", "PPOSAT")):
        for candidate_node_id in entity_map[antecedent_node_id]:
            candidate = pocores.node_attrs(candidate_node_id)
            if ((anaphora['sent_pos'] == candidate['sent_pos'])
               and (candidate['word_pos'] in range(left_limit, right_limit))):
                return False

    # binding principle 3
    if anaphora[pos_attrib] in ("NN", "NE"):
        for candidate_node_id in entity_map[antecedent_node_id]:
            candidate = pocores.node_attrs(candidate_node_id)
            if anaphora['sent_pos'] == candidate['sent_pos']:
                return False
    return True


def tokentuple2id(sent_pos, word_pos):
    """
    generates a token node ID (str) from a sentence index (int) and word pos
    (int).
    """
    return 's{}_t{}'.format(sent_pos, word_pos)


def is_coreferent(pocores, antecedent, anaphora,
                  lemma_attrib='plemma'):
    """
    So far: checks if two words have the same lemma. (We're using this for
    basic anaphora resolution.)

    TODO: add real coreference resolution.

    Paramters
    ---------
    pocores : Pocores
        an instance of the Pocores class
    antecedent : str
        the node ID of the antecedent
    anaphora : str
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
    return pocores.node_attrs(antecedent)[lemma_attrib] == \
        pocores.node_attrs(anaphora)[lemma_attrib]


def is_expletive(pocores, token_node, lemma_attrib='plemma'):
    """
    Checks if a given token is an expletive.

    Paramters
    ---------
    pocores : Pocores
        an instance of the Pocores class
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
    if pocores.document.get_token(token_node) in (u'es', u'Es'):
        for lemma in traverse_dependencies_up(pocores.document, token_node,
                                              node_attribute=lemma_attrib):
            if lemma in EXPLETIVE_VERBS:
                return True
    return False
