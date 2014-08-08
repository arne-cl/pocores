#!/usr/bin/env python
# -*- coding: utf-8 -*-
# needs python 2.7 or later version

import sys

from discoursegraphs.readwrite import ConllDocumentGraph


if __name__ == '__main__':
    conll_file = sys.argv[1]
    pocoresgraph = ConllDocumentGraph(conll_file, conll_format='2010')
