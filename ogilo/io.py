from typing import Sequence, TextIO, Tuple, Union
import csv
import sys

import nemony as nm
from tqdm import tqdm

from .checks import re_sites
from .types import Oligo
from .utils import grouping_key

def extract_col(f: TextIO, 
                col: Union[str, int], 
                sep: str = '\t') -> Tuple[str]:
    
    """Get a column from a CSV or TSV by number or name.

    Reads a CSV or TSV file and returns the named or numbered column. 
    If a number is used, then it is assumed that there is no header,
    and the first line is included. If a column name is used, then
    it is assumed that there is a header, and the first line is skipped.

    Parameters
    ----------
    f : file or file-like
        File to read
    col : str or int
        The column to return
    sep : str
        Delimiter character for the columns

    Returns
    -------
    tuple of str
        The entries of the requested column
    
    """

    if col.isdigit():

        c = csv.reader(f, delimiter=sep)
        col = int(col) - 1

    else:

        c = csv.DictReader(f, delimiter=sep)

    return tuple(map(lambda x: x[col], c))


def write_constructs(x: Sequence[Oligo],
                     file: TextIO = sys.stdout) -> None:
    
    """Write oligos to a table.

    Takes a list of Oligo objects and writes them to a file, one per line.
    Properties are calculated and checks are carried out.

    Parameters
    ----------
    x : list 
        Oligo objects to write.
    file : file or file-like
        File to write to. Default STDOUT

    Returns
    -------
    None
    
    """

    c = csv.DictWriter(file, 
                       fieldnames=('group', 'pcr_handles', 'length', 'mnemonic', 
                                   'restriction_sites', 'oligo_name', 'oligo_sequence'),
                       delimiter='\t')
    c.writeheader()

    def upper_lower(x, i):

        return x.casefold() if i % 2 > 0 else x.upper()

    try:
        for row in tqdm(x, disable=len(x) < 100):
            
            seq = ''.join(upper_lower(seq.seq, i) 
                          for i, seq in enumerate(row))
            
            group = grouping_key(row)

            try:
                handles = list(set(seq.name.split('_')[0] 
                                   for seq in row if seq.type == 'handle'))[0]
            except IndexError:
                handles = None

            name = ('-'.join(seq.name for seq in row 
                             if seq.name is not None and seq.type != 'handle'))
            
            c.writerow(dict(group=group, 
                            pcr_handles=handles,
                            length=str(len(seq)), 
                            mnemonic=nm.encode(seq), 
                            restriction_sites=';'.join(re_sites(row, seq)), 
                            oligo_name=name, 
                            oligo_sequence=seq))

    except BrokenPipeError:

        pass

    return None