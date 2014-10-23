#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: Jonathan Sonntag, Arne Neumann

"""
This module implements the command line interface of pocores.
"""

import sys
from argparse import ArgumentParser, FileType


def parse_options():
    """
    @author: Jonathan Sonntag
    @author: Arne Neumann
    """
    parser = ArgumentParser(prog='pocores')

    input_options = parser.add_argument_group("Input Options",
        "These options allow you to specify input options")
    input_options.add_argument('-i', '--input', default=sys.stdin,
        type=FileType('r'), dest='input',
        help='Specify the input file', metavar='FILENAME')
    input_options.add_argument('-c', '--input_format', dest='informat',
        default='2009',
        help=('Specify the CoNLL input file format: 2009 or 2010. '
              'default: 2009'))

    coref_options = parser.add_argument_group("Coreference Options",
        "Change coreference resolution parameters without touching the code.")
    coref_options.add_argument('-w', '--weights', dest='weights',
        help=('Specify the coreference filter weights (7 comma separated'
              ' integers, e.g. "8,2,8,3,2,7,0"'))
    coref_options.add_argument('-d', '--max_sent_dist', dest='max_sent_dist',
        help=('Specify how many preceding sentences will be considered for'
            ' finding antecedents'))

    output_options = parser.add_argument_group("Output Options",
        "These options allow you to specify various output options")
    output_options.add_argument('-o', '--output', dest='output_dest',
        nargs='?', default=sys.stdout,
        help=('Specify the output file (output folder in case of brat) to write to.'),
        metavar='FILENAME')
    output_options.add_argument('-f', '--output_format', dest='outformat',
        default='bracketed',
        help=('Specify format the output shall be printed in. Format can be one'
        ' of the following: bracketed, brat'),
        metavar='OUTFORMAT')

    eval_options = parser.add_argument_group("Evaluation/Debug Options")
    eval_options.add_argument('--debug', action='store_true',
        help=('print additional debugging information'))
    eval_options.add_argument('-e', '--eval', dest='eval_file',
        help=(('evaluate Pocores coreference resolution against *.mmax gold '
               'standard file')))

    return parser, parser.parse_args(sys.argv[1:])

if __name__ == '__main__':
    parser, args = parse_options()
    print args
