#!/usr/bin/env python
# -*- coding: utf-8 -*-

from discoursegraphs.readwrite.conll import traverse_dependencies_up


def check_parallelism(pocores, antecedent_id, anaphora_id,
                      deprel_attrib='pdeprel'):
    """
    Checks syntactical role parallelism between two given words.

    Parameters
    ----------
    pocores : Pocores
        an instance of the Pocores class
    antecedent_id : str
        the node ID of the antecedent
    anaphora_id : str
        the node ID of the anaphora

    Returns
    -------
    parallel : bool
    True, if parallelism is found, False otherwise.
    """
    ant = pocores.node_attrs(antecedent_id)
    ana = pocores.node_attrs(anaphora_id)
    if (ant[deprel_attrib] == ana[deprel_attrib]
       and ant[deprel_attrib] in ("SB", "OA", "DA")):
        return True
    return False


def check_role(pocores, antecedent_id, role, deprel_attr='pdeprel'):
    """
    Checks if a given word has a given syntactic role.

    antecedent_id : str
        the node ID of the antecedent
    """
    ant = pocores.node_attrs(antecedent_id)
    if ant[deprel_attr] == role:
        return True
    return False


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
    return len(traverse_dependencies_up(pocores.document, token_id))
