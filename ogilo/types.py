from typing import Sequence
from collections import namedtuple

PCRHandle = namedtuple('PCRHandle',
                       'name f r')

Input = namedtuple('Input', 
                   'type seq f1 f2 f3',
                   defaults=(None, ) * 5)

Seq = namedtuple('Seq', 
                 'name type seq group')

Oligo = Sequence[Seq]