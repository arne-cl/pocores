#!/usr/bin/env python
# -*- coding: utf-8 -*-

from discoursegraphs.readwrite.conll import traverse_dependencies_up

def check_parallelism(pocores, (sent1, word1), (sent2, word2)):
    """
    Checks syntactical role parallelism between two given words.

    :param (sent1, word1): a word index
    :type (sent1, word1): (int, int) ``tuple``
    :param (sent2, word2): a word index
    :type (sent2, word2): (int, int) ``tuple``

    :return: True if parallelism is found, False otherwise.
    :rtype: ``boolean``
    """
    raise NotImplementedError


def check_role(pocores, antecedent, role):
    """
    Checks if a given word has a given syntactic role.
    """
    raise NotImplementedError


def get_chain_length(pocores, antecedent_id):
    """
    Returns the count of known mentions of the discourse referent of the
    given word.
    """
    first_mention = pocores.mentions[antecedent_id]
    return len(pocores.entities[first_mention])


def get_depth(pocores, token_id):
    """
    Returns number of dependency edges from a given word to root of the
    sentence.
    """
    return len(list(traverse_dependencies_up(pocores.document, token_id)))
