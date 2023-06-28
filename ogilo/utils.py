"""Miscellaneous utilities used in ogilo."""

from typing import Sequence
import csv
import os

import streq as sq

from .types import Oligo, PCRHandle, Seq

PCR_HANDLE_SETS = ('sanson2018', 'illumina')

def _load_pcr_handles(filename: str) -> Sequence[PCRHandle]:

    with open(filename, 'r') as f:
    
        c = csv.DictReader(f, delimiter=',')

        pcr_handles0 = tuple(PCRHandle(name=row['pcr_handle_id'],
                                       f=row['pcr_handle_f'],
                                       r=row['pcr_handle_r']) 
                             for row in c)
    pcr_handles = []

    for handle in pcr_handles0:

        pcr_handles.append(handle._replace(f=Seq(group=None,
                                                 seq=handle.f,
                                                 name=handle.name + '_f',
                                                 type='handle',
                                                 reverse=False),
                                           r=Seq(group=None,
                                                 seq=handle.r,
                                                 name=handle.name + '_r',
                                                 type='handle',
                                                 reverse=False)))
    return tuple(pcr_handles)   


def _get_pcr_handles(handle_set: str) -> Sequence[PCRHandle]:

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


def find_all(p: str, 
             s: str) -> Sequence[int]:
    
    """Find all instances of pattern p in the string s.

    Parameters
    ----------
    p : str
        Pattern to find
    s : str
        String in which to find pattern

    Yields
    ------
    int
        Position in `s` of each instance of `p`

    """

    s = s.upper()
    i = s.find(p)

    while i != -1:

        yield i

        i = s.find(p, i + 1)


def n_found(p: str, 
            s: str, 
            with_rc: bool = True) -> int:
    
    """Count the occurences of a pattern in a string.
    
    Parameters
    ----------
    p : str
        Pattern to find
    s : str
        String in which to find pattern
    with_rc : bool
        Whether to also search the reverse complement of `s`

    Returns
    -------
    int
        The number of occurences of `p` in `s`
        
    """

    n = len(list(find_all(p, s)))

    if with_rc:

        n += len(list(find_all(sq.reverse_complement(p), s)))

    return n


def grouping_key(x: Oligo) -> str:

    """Use as `key` parameter for `sort()` or `itertools.groupby()`
    to sort a list of list of `Seq` objects by their group attribute.

    When the group attribute is not set for a given `Seq` object, then
    it is ignored.

    The group strings within the inner list of `Seq` objects are 
    concatenated to allow sorting.

    Parameters
    ----------
    x : list of Seq objects

    Returns
    -------
    str
        Concatenated group attributes, where the group is not `None`
    
    """

    return '-'.join(map(lambda y: y.group, 
                        filter(lambda y: y.group is not None, x)))