.. ogilo documentation master file, created by
   sphinx-quickstart on Wed May 31 16:38:00 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

⛓️ ogilo
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   api

Automating construction of oligo library sequences for oligo array synthesis.

**ogilo** takes your table of sequences (such as a library of guide RNAs) and concatenates them  
with any other nucleotide sequences you provide, Type IIS restriction sites, and PCR handles.

If your table of sequences contains a column indicating subsets or groups, you can use this column to
instruct **ogilo** to add distinct PCR handles to each group. This allows you to order multiple
libraries as one oligo pool and selectively PCR each one as needed.



Source
------

View source at `GitHub <https://github.com/scbirlab/ogilo>`_.
