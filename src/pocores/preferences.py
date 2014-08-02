# -*- coding: utf-8 -*-


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


def get_distance((sent1, word1), (sent2, word2)):
    """
    Returns sentence distance between to given words.

    >>> get_distance((1, 2), (5, 4))
    4
    >>> get_distance((1, 2), (1, 9))
    0
    """
    raise NotImplementedError


def check_role(pocores, antecedent, role):
    """
    Checks if a given word has a given syntactic role.
    """
    raise NotImplementedError


def get_chain_length(pocores, antecedent):
    """
    Returns the count of known mentions of the discourse referent of the
    given word.
    """
    raise NotImplementedError


def get_depth(pocores, (sent, word)):
    """
    Returns number of dependency edges from given word to root of the
    sentence.
    """
    raise NotImplementedError
