"""Command-line interface for ogilo."""

from typing import TextIO
from collections.abc import Sequence
import argparse
from collections import Counter
import csv
from itertools import groupby
import sys
import textwrap

import nemony as nm
import streq as sq
from tqdm import tqdm

from .utils import _get_pcr_handles, Input, _Sequence


def _get_col_from_file(f: TextIO, 
                       col: str, 
                       sep: str = '\t') -> Sequence[str]:

    if col.isdigit():

        c = csv.reader(f, delimiter=sep)
        col = int(col) - 1

    else:

        c = csv.DictReader(f, delimiter=sep)

    return tuple(map(lambda x: x[col], c))


def _parse_inputs(inputs=Sequence[str], 
                  sep='\t') -> Sequence[Sequence[_Sequence]]:

    parsed = []

    for _input in inputs:

        splits = _input.split(':')

        if len(splits) == 1:

            raise ValueError(f'Input {_input} has no colons. '
                             'Please indicate input type using '
                             '<type>:<value>, for example '
                             'file:oligos.csv:1:2:3 seq:ATCGTAT')
        
        this_input = Input(*splits)

        if this_input.type == 'file':

            filename = this_input.seq            
            file_content = _get_col_from_file(open(filename, 'r'), 
                                              this_input.f1 or 1, 
                                              sep=sep)
            
            if this_input.f2 is not None:
                names = _get_col_from_file(open(filename, 'r'), 
                                           this_input.f2, 
                                           sep=sep)
            else:
                names = map(str, range(1, len(file_content) + 1))
                
            if this_input.f3 is not None:
                groups =  _get_col_from_file(open(filename, 'r'), 
                                             this_input.f3, 
                                             sep=sep)
            else:
                groups = [None] * len(file_content)

            this_input = (_Sequence(name=name, 
                                    seq=seq, 
                                    group=group, 
                                    type='file') 
                          for seq, name, group in zip(file_content, names, groups))

        elif this_input.type == 'seq':

            this_input = _Sequence(name=this_input.f1, 
                                   seq=this_input.seq, 
                                   group=None, 
                                   type=this_input.type)

        elif this_input.type == 're':

            seq = sq.sequences.re_sites[this_input.seq]

            if this_input.f1.casefold() == 'r':

                seq = sq.reverse_complement(seq)

            this_input = _Sequence(name=this_input.seq + '_' + this_input.f1.casefold(), 
                                   seq=seq, 
                                   group=None, 
                                   type=this_input.type)

        else:

            raise ValueError(f'Type {this_input.type} is not supported. '
                             'Allowed types: seq, file, re.')
        
        parsed.append(this_input)

    return parsed
        

def  _generate_combos(x: Sequence[Sequence[_Sequence]]) -> Sequence[Sequence[_Sequence]]:

    x = tuple(tuple([_x]) if isinstance(_x, _Sequence) 
              else tuple(_x) for _x in x)

    max_len = max(len(_x) for _x in x)

    x = tuple(_x * max_len if len(_x) == 1 else _x for _x in x)

    is_max_len = tuple(len(_x) == max_len for _x in x)

    assert all(is_max_len), \
        f'A sequence list is shorter than the maximum length ({max_len}):'\
        + ', '.join(_x.name for _x, is_max in zip(x, is_max_len) if not is_max)

    return tuple(zip(*x))


def _findall(p, s):
    '''Yields all the positions of
    the pattern p in the string s.'''
    s = s.upper()
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)


def _n_found(p, s, with_rc=True):

    n_found = len(list(_findall(p, s)))

    if with_rc:

        n_found += len(list(_findall(sq.reverse_complement(p), s)))

    return n_found

    
def check_re_sites(row, seq):

    allowed_re_sites = Counter(seq.name.split('_')[0] 
                               for seq in row if seq.type == 're')
    found_allowed_re_sites = Counter({n: _n_found(sq.sequences.re_sites[n], seq, with_rc=True) 
                                      for n in allowed_re_sites})
    residual = found_allowed_re_sites - allowed_re_sites
    re_sites = set(sq.which_re_sites(seq)) - set(site for site in allowed_re_sites if residual[site] == 0)

    return re_sites


def _write_constructs(x: Sequence[Sequence[_Sequence]],
                      output: TextIO) -> None:

    c = csv.DictWriter(output, 
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

            re_sites = check_re_sites(row, seq)
            group = _keyfun(row)

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
                            restriction_sites=';'.join(re_sites), 
                            oligo_name=name, 
                            oligo_sequence=seq))

    except BrokenPipeError:

        pass

    return None


def _keyfun(x: Sequence[_Sequence]) -> str:

    return '-'.join(map(lambda y: y.group, 
                        filter(lambda y: y.group is not None, x)))


def _add_pcr_handles(seqs: Sequence[Sequence[_Sequence]], 
                     handle_set: str = 'all',
                     grouped: bool = False) -> Sequence[Sequence[_Sequence]]:
    
    _pcr_handles = _get_pcr_handles(handle_set)

    if not grouped:
        return tuple((_pcr_handles[0].f, ) + seq + (_pcr_handles[0].r, ) for seq in seqs)
    else:
        seqs = sorted(seqs, key=_keyfun)
        grouped_seqs = tuple((k, tuple(g)) 
                             for k, g in groupby(seqs, _keyfun))

        n_groups = len(grouped_seqs)
        n_handles = len(_pcr_handles)

        assert n_groups <= n_handles, f"More groups ({n_groups}) than available PCR handles ({n_handles})."

        return tuple((handle.f, ) + seq + (handle.r, ) 
                     for handle, (_, group) in zip(_pcr_handles, grouped_seqs) 
                     for seq in group)


def _assemble(args: argparse.Namespace) -> None:

    sep = dict(TSV='\t', CSV=',')[args.format]

    constructs = _parse_inputs(args.inputs, sep)

    constructs = _generate_combos(constructs)

    if args.pcr_handles:
        constructs = _add_pcr_handles(constructs, 
                                      handle_set=args.handle_set, 
                                      grouped=True)

    _write_constructs(constructs, args.output)

    return None


def main() -> None:

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''
    Automated construction of oligo library sequences for oligo array synthesis.

    The sequences to concatenate must be provided in the following format:

    <type>:<value>[:<f1>[:<f2>[:<f3>]]]

    For example, file:oligos.csv:2 would instruct ogilo to take sequences from column 2 of 
    the file oligos.csv, and seq:ATCCCGAGAG:spacer would add the sequence ATCCCGAGAG and 
    include "spacer" in the oligo name. For more, see below.

    The output is a TSV-formatted table with the following columns:
        group: 
            The group of oligos sharing the same PCR handles.
        pcr_handles: 
            The name of the PCR handle pair used (if any).
        length: 
            Total oligo length.
        mnemonic: 
            Adjective-noun mnemonic of oligo sequence.
        restriction_sites: 
            Type IIS restriction sites which happen to be in the oligo even though they
            weren't requested.
        oligo_name: 
            Name for the oligo, constricted by concatenating the names of the sequence components.
        oligo_sequence: 
            Sequence for the oligo.

    For example:
    $ ogilo re:BsmBI:f file:test/guides-RLC12_mapped-tiny.tsv:guide_sequence:Name:ann_gene_biotype re:BsmBI:r -p
    group   pcr_handles   length  mnemonic     restriction_sites  oligo_name                                    oligo_sequence
    rRNA    sans18a         74      brief_nadia             BsmBI_f-_up-rrs-1471818-ultimate_parody-BsmBI_r  AGGCACTTGCTCGTACGACGcgtctcAACCCAAACACTCCCTTTGGAAgagacgATGTGGGCCCGGCACCTTAA
    rRNA    sans18a         73      rancid_kayak            BsmBI_f-_up-rrs-1471818-nostalgic_sonata-BsmBI_r AGGCACTTGCTCGTACGACGcgtctcACCCAAACACTCCCTTTGGAAgagacgATGTGGGCCCGGCACCTTAA

    These are the allowed values of <type>:
        file:<filename>[:<seq_col>[:<name_col>[:<group_col>]]]
            Take sequences from file <filename>. If <seq_col> is provided, ogilo will use this column,
            otherwise assumes column 1 (and that the first line is not a header line). 
            <seq_col>, <name_col>, <group_col> can be column names (in which 
            case, the first line will be skipped) or integers (in which case, the first line will be 
            included). 
            Do not mix column names and integers. If your file has a header, use column names.
            If <group_col> is provided, and PCR handles are requested, then different PCR handles will 
            be added to each group.

        seq:<sequence>[:<name>]
            An explicit sequence given in <sequence>, optionally with a <name>.

        re:<enzyme_name>:(f|r)
            A named Type IIS restriction enzyme site. "f" and "r" determine whether the site should be
            in a forward or reverse orientation. This does not take care of overhangs for you; these can
            be added as a seq component.

    ---------------------------------------------------------------------------------------------------------
    '''))

    parser.set_defaults(func=_assemble)

    parser.add_argument('inputs',
                        type=str,
                        default=[],
                        nargs='*',
                        help='Input(s). Format is <type>:<value>[:<f1>[:<f2>[:<f3>]]], for example: file:oligos.csv:2 seq:ATCGTAT.')
    parser.add_argument('--pcr_handles', '-p', 
                        action='store_true',
                        help='Requests PCR handles to be added either side of final sequences.')
    parser.add_argument('--handle_set', '-s', 
                        type=str,
                        default='all',
                        help='Which set of PCR handles to use. Either "all", "sanson2018", "illumina", or '
                             'a path to a CSV with column headings pcr_handle_id, pcr_handle_f, pcr_handle_r. '
                             'Default: %(default)s')
    parser.add_argument('--format', '-f', 
                        type=str,
                        default='TSV',
                        choices=['TSV', 'CSV'],
                        help='Format of files. Default: %(default)s')
    parser.add_argument('--output', '-o', 
                        type=argparse.FileType('w'),
                        default=sys.stdout,
                        help='Output file. Default: STDOUT')
    
    args = parser.parse_args()
    args.func(args)

    return None


if __name__ == '__main__':

    main()

