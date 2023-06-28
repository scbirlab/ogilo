from collections import Counter

from .utils import n_found

import streq as sq


def re_sites(row, seq):

    allowed_re_sites = Counter(seq.name.split('_')[0] 
                               for seq in row if seq.type == 're')
    found_allowed_re_sites = Counter({n: n_found(sq.sequences.re_sites[n], seq, with_rc=True) 
                                      for n in allowed_re_sites})
    residual = found_allowed_re_sites - allowed_re_sites
    re_sites = set(sq.which_re_sites(seq)) - set(site for site in allowed_re_sites if residual[site] == 0)

    return re_sites