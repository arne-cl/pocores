pocores
=======

`pocores` is a rule-based coreference resolution system for German using the
*filters and preferences* approach (Lappin and Leass 1994; Stuckardt 2001).
It requires dependency parsed input sentences in CoNLL 2009/2010 format, which can i.a. be produced by [mate-tools](http://code.google.com/p/mate-tools/) (Bohnet 2010).

The code was originally written by Tobias Günther for his Bachelor's thesis (Günther 2011),
but has been heavily refactored and is now based on the
[discoursegraphs](https://github.com/arne-cl/discoursegraphs) library (Neumann, to appear).


References
----------

Bohnet, B. (2010).  
Very high accuracy and fast dependency parsing is not a contradiction. In *Proceedings of the 23rd International Conference on Computational Linguistics* (pp. 89-97). Association for Computational Linguistics.

Günther, T. (2011).  
Automatische Anaphernresolution im Deutschen: Entwurf und Implementierung. Bsc thesis. Universität Potsdam, Germany.

Neumann, A. (to appear).  
discoursegraphs: A Graph-Based Merging Tool and Converter for Multilayer Annotated Corpora. In *Proceedings of the 20th Nordic Conference of Computational Linguistics* (Nodalida 2015). Northern European Association for Language Technology.

Lappin, S., & Leass, H. J. (1994).  
An algorithm for pronominal anaphora resolution. *Computational linguistics*, 20(4), 535-561.

Stuckardt, R. (2001).  
Design and enhanced evaluation of a robust anaphor resolution algorithm. *Computational Linguistics*, 27(4), 479-506.
