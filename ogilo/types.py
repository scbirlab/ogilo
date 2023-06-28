"""Custom types and objects used in ogilo."""

from typing import Sequence
from collections import namedtuple

PCRHandle = namedtuple('PCRHandle',
                       'name f r')

Input = namedtuple('Input', 
                   'type seq f1 f2 f3 reverse',
                   defaults=(None, ) * 5 + (False, ))

Seq = namedtuple('Seq', 
                 'name type seq group reverse')

Oligo = Sequence[Seq]