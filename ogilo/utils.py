"""Miscellaneous utilities used in ogilo."""

from collections import namedtuple
from collections.abc import Sequence
import csv
import os


PCR_HANDLE_SETS = ('sanson2018', 'illumina')

_PCRHandle = namedtuple('PcrHandle',
                        'name f r')
Input = namedtuple('Input', 
                   'type seq f1 f2 f3',
                   defaults=(None, ) * 5)
_Sequence = namedtuple('Sequence', 
                       'name type seq group')

def _load_pcr_handles(filename: str) -> Sequence[_PCRHandle]:

    with open(filename, 'r') as f:
    
        c = csv.DictReader(f, delimiter=',')

        pcr_handles0 = tuple(_PCRHandle(name=row['pcr_handle_id'],
                                        f=row['pcr_handle_f'],
                                        r=row['pcr_handle_r']) 
                             for row in c)
    pcr_handles = []

    for handle in pcr_handles0:

        pcr_handles.append(handle._replace(f=_Sequence(group=None,
                                                    seq=handle.f,
                                                    name=handle.name + '_f',
                                                    type='handle'),
                                        r=_Sequence(group=None,
                                                    seq=handle.r,
                                                    name=handle.name + '_r',
                                                    type='handle')))
    return tuple(pcr_handles)   


def _get_pcr_handles(handle_set: str) -> Sequence[_PCRHandle]:

    if handle_set in PCR_HANDLE_SETS:

        this_data_path = os.path.join(os.path.dirname(__file__), 
                                    f'{handle_set}-pcr-handles.csv')
        pcr_handles = _load_pcr_handles(this_data_path)
    
    elif handle_set == 'all':

        pcr_handles = tuple()

        for handle_set in PCR_HANDLE_SETS:
            pcr_handles += _get_pcr_handles(handle_set)

    else:

        if handle_set.endswith('.csv') and os.path.exists(handle_set):
             pcr_handles = _load_pcr_handles(handle_set)
        else:
            raise ValueError(f'The PCR handle set {handle_set} does not exist.')

    return pcr_handles