# Usage

Call **ogilo** with a set of sequence directives and other options:

```
ogilo file:guide-rnas.csv:sequence:guide_name:essentiality seq:ATCGGGC:spacer re:BsmBI:f --format CSV
```

You tell **ogilo** which sequences to concatenate using the following directive format:

```
[@]<type>:<value>[:<f1>[:<f2>[:<f3>]]]
```

For example, file:oligos.csv:2 would instruct ogilo to take sequences from column 2 of 
the file oligos.csv, and seq:ATCCCGAGAG:spacer would add the sequence ATCCCGAGAG and 
include "spacer" in the oligo name. 

If you prepend the directive with `@`, then reverse complement sequences will be 
automatically generated.

The allowed values of `<type>` are as follows.

## Files

```
[@]file:<filename>[:<seq_col>[:<name_col>[:<group_col>]]]
```

Take sequences from file `<filename>`. If `<seq_col>` is provided, **ogilo** will use this column,
otherwise assumes column 1. 

`<seq_col>`, `<name_col>`, `<group_col>` can be column names (in which 
case, the first line will be skipped) or integers (in which case, the first line will be 
included). 

**Do not mix column names and integers.** If your file has a header, **use column names**.
If `<group_col>` is provided, and PCR handles are requested, then different PCR handles will 
be added to each group.

For example:

```
file:guide-rnas.tsv:sequence:guide_name:essentiality
```

would load sequences from the file `guide-rnas.tsv`, using column `sequence` for sequences, 
`guide_name` for the names, and `essentiality` for the groups (if you want different PCR handles
for each group). 

## Constant sequences

```
[@]seq:<sequence>[:<name>]
```

An explicit sequence given in `<sequence>`, optionally with a `<name>`.

For example:

```
@seq:ATCGGGC:spacer
```

## Type IIS restriction enzyme sites

```
[@]re:<enzyme_name>
```

A named Type IIS restriction enzyme site. This does not take care of overhangs for you; these can
be added as a seq component.

For example:

```
re:BsmBI
```

## Output

The output is a TSV-formatted table with the following columns:
- `group`: The group of oligos sharing the same PCR handles.
- `pcr_handles`: The name of the PCR handle pair used (if any).
- `length`: Total oligo length.
- `mnemonic`: Adjective-noun mnemonic of oligo sequence.
- `restriction_sites`: Type IIS restriction sites which happen to be in the oligo even though they weren't requested.
- `oligo_name`: Name for the oligo, constricted by concatenating the names of the sequence components.
- `oligo_sequence`: Sequence for the oligo. Each concatenated section alternates case to allow visual checks.

## Examples

Simple example showing parts being concatenated. Note that group and pcr_handles columns are empty.

```bash
$ ogilo seq:ATCG:s1 re:BsmBI seq:GGCCTTAA:main @re:BsaI seq:CATG:s2
group   pcr_handles     length  mnemonic        restriction_sites       oligo_name      oligo_sequence
                28      dim_lesson              s1-BsmBI_f-main-BsaI_r-s2       ATCGcgtctcGGCCTTAAgagaccCATG
```

You can ask for a seqment to be reverse complemented by prepending the directive with `@`.

```bash
$ ogilo @seq:ATCG:s1 re:BsmBI seq:GGCCTTAA:main @re:BsaI seq:CATG:s2
group   pcr_handles     length  mnemonic        restriction_sites       oligo_name      oligo_sequence
                28      dim_lesson              s1-BsmBI_f-main-BsaI_r-s2       ATCGcgtctcGGCCTTAAgagaccCATG
```

You can request PCR handles. These are the outermost sections of the sequence.

```bash
$ ogilo seq:ATCG:s1 re:BsmBI seq:GGCCTTAA:main @re:BsaI seq:CATG:s2 --pcr_handles
group   pcr_handles     length  mnemonic        restriction_sites       oligo_name      oligo_sequence
        sans18a 68      defeated_active         s1-BsmBI_f-main-BsaI_r-s2       AGGCACTTGCTCGTACGACGatcgCGTCTCggccttaaGAGACCcatgATGTGGGCCCGGCACCTTAA
```

You can specify the subset of PCR handles to use. The current options are `illumina` for P5/P7 or NextEra i5/i7 primers, 
or `sanson2018` for the primers used in [Sanson et al., _Nat. Commun._, 2018](https://doi.org/10.1038/s41467-018-07901-8). 
Here, we request `illumina`, and **ogilo** detects the extra BbsI site in the P5/P7 PCR handles.

```bash
$ ogilo seq:ATCG:s1 re:BsmBI seq:GGCCTTAA:main @re:BsaI seq:CATG:s2 --pcr_handles --handle_set illumina
group   pcr_handles     length  mnemonic        restriction_sites       oligo_name      oligo_sequence
        p5p7    69      vivid_stereo    BbsI    s1-BsmBI_f-main-BsaI_r-s2       AATGATACGGCGACCACCGAatcgCGTCTCggccttaaGAGACCcatgTCAAGCAGAAGACGGCATACG
```

**ogilo** will check for other spurious Type IIS restriction sites that emerge *after* sequences have been concatenated. It ignores the ones you've requested.

```bash
$ ogilo seq:ATCG:s1 re:BsmBI seq:ACCTGC:quasi_paqCI @re:BsaI seq:CATG:s2 --pcr_handles --handle_set illumina
group   pcr_handles     length  mnemonic        restriction_sites       oligo_name      oligo_sequence
        p5p7    67      muddy_method    BbsI;PaqCI      s1-BsmBI_f-quasi_paqCI-BsaI_r-s2        AATGATACGGCGACCACCGAatcgCGTCTCacctgcGAGACCcatgTCAAGCAGAAGACGGCATACGA
```

Files containing sequences can also be used, so long as you specify which column the sequence is coming from.

```bash
$ ogilo re:BsmBI seq:AATTA:s1 file:test/guides-RLC12_mapped-tiny.tsv:guide_sequence seq:ATGCG:s2 @re:BsmBI --pcr_handles
group   pcr_handles     length  mnemonic        restriction_sites       oligo_name      oligo_sequence
        sans18a 84      festive_enigma          BsmBI_f-s1-1-s2-BsmBI_r AGGCACTTGCTCGTACGACGcgtctcAATTAaacccaaacactccctttggaaATGCGgagacgATGTGGGCCCGGCACCTTAA
        sans18a 83      tipsy_classic           BsmBI_f-s1-2-s2-BsmBI_r AGGCACTTGCTCGTACGACGcgtctcAATTAacccaaacactccctttggaaATGCGgagacgATGTGGGCCCGGCACCTTAA
       ...
        sans18a 79      tidy_isotope            BsmBI_f-s1-19-s2-BsmBI_r        AGGCACTTGCTCGTACGACGcgtctcAATTAaacactggtgcgcgataATGCGgagacgATGTGGGCCCGGCACCTTAA
        sans18a 78      wistful_liquid          BsmBI_f-s1-20-s2-BsmBI_r        AGGCACTTGCTCGTACGACGcgtctcAATTAacactggtgcgcgataATGCGgagacgATGTGGGCCCGGCACCTTAA
```

**ogilo** interprets the `.csv` or `.tsv` file extnsion to indicate that your file is either comma- or tab-delimited, 
but if the file extension is misleading you can force to read either CSV or TSV instead with the `--format` option.

```bash
$ ogilo re:BsmBI seq:AATTA:s1 file:test/guides-RLC12_mapped-tiny.txt:guide_sequence seq:ATGCG:s2 @re:BsmBI --pcr_handles --format CSV
group   pcr_handles     length  mnemonic        restriction_sites       oligo_name      oligo_sequence
        sans18a 84      festive_enigma          BsmBI_f-s1-1-s2-BsmBI_r AGGCACTTGCTCGTACGACGcgtctcAATTAaacccaaacactccctttggaaATGCGgagacgATGTGGGCCCGGCACCTTAA
        sans18a 83      tipsy_classic           BsmBI_f-s1-2-s2-BsmBI_r AGGCACTTGCTCGTACGACGcgtctcAATTAacccaaacactccctttggaaATGCGgagacgATGTGGGCCCGGCACCTTAA
       ...
        sans18a 79      tidy_isotope            BsmBI_f-s1-19-s2-BsmBI_r        AGGCACTTGCTCGTACGACGcgtctcAATTAaacactggtgcgcgataATGCGgagacgATGTGGGCCCGGCACCTTAA
        sans18a 78      wistful_liquid          BsmBI_f-s1-20-s2-BsmBI_r        AGGCACTTGCTCGTACGACGcgtctcAATTAacactggtgcgcgataATGCGgagacgATGTGGGCCCGGCACCTTAA
```

Optionally, a column to take names from can be specified. Here, we're using the column called `pam_offset`.

```bash
$ ogilo re:BsmBI seq:AATTA:s1 file:test/guides-RLC12_mapped-tiny.tsv:guide_sequence:pam_offset seq:ATGCG:s2 @re:BsmBI --pcr_handles
group   pcr_handles     length  mnemonic        restriction_sites       oligo_name      oligo_sequence
        sans18a 84      festive_enigma          BsmBI_f-s1-25-s2-BsmBI_r        AGGCACTTGCTCGTACGACGcgtctcAATTAaacccaaacactccctttggaaATGCGgagacgATGTGGGCCCGGCACCTTAA
        sans18a 83      tipsy_classic           BsmBI_f-s1-25-s2-BsmBI_r        AGGCACTTGCTCGTACGACGcgtctcAATTAacccaaacactccctttggaaATGCGgagacgATGTGGGCCCGGCACCTTAA
       ...
        sans18a 79      tidy_isotope            BsmBI_f-s1-58-s2-BsmBI_r        AGGCACTTGCTCGTACGACGcgtctcAATTAaacactggtgcgcgataATGCGgagacgATGTGGGCCCGGCACCTTAA
        sans18a 78      wistful_liquid          BsmBI_f-s1-58-s2-BsmBI_r        AGGCACTTGCTCGTACGACGcgtctcAATTAacactggtgcgcgataATGCGgagacgATGTGGGCCCGGCACCTTAA
```

A column to indicate grouping for different PCR handles can also be specified in addition. Here, we're using the column called `ann_gene_biotype`.
The different values in this column are matched with a different PCR handle pair.

```bash
$ ogilo re:BsmBI seq:AATTA:s1 file:test/guides-RLC12_mapped-tiny.tsv:guide_sequence:pam_offset:ann_gene_biotype seq:ATGCG:s2 @re:BsmBI --pcr_handles
group   pcr_handles     length  mnemonic        restriction_sites       oligo_name      oligo_sequence
rRNA    sans18a 84      festive_enigma          BsmBI_f-s1-25-s2-BsmBI_r        AGGCACTTGCTCGTACGACGcgtctcAATTAaacccaaacactccctttggaaATGCGgagacgATGTGGGCCCGGCACCTTAA
rRNA    sans18a 83      tipsy_classic           BsmBI_f-s1-25-s2-BsmBI_r        AGGCACTTGCTCGTACGACGcgtctcAATTAacccaaacactccctttggaaATGCGgagacgATGTGGGCCCGGCACCTTAA
        ...
tRNA    sans18b 79      good_iceberg            BsmBI_f-s1-58-s2-BsmBI_r        GTGTAACCCGTAGGGCACCTcgtctcAATTAaacactggtgcgcgataATGCGgagacgGTCGAGAGCAGTCCTTCGAC
tRNA    sans18b 78      damp_index              BsmBI_f-s1-58-s2-BsmBI_r        GTGTAACCCGTAGGGCACCTcgtctcAATTAacactggtgcgcgataATGCGgagacgGTCGAGAGCAGTCCTTCGAC
```

## Command line options

```
usage: ogilo [-h] [--input INPUT] [--pcr_handles] [--column COLUMN] [--pcr_group PCR_GROUP] [--format {TSV,CSV}] [--output OUTPUT] [inputs ...]

Automated construction of oligo library sequences for oligo array synthesis.

positional arguments:
  inputs                Further input(s). Format is <type>:<value>:<seq_col>[:<name_col>:<group_col>], for example file:oligos.csv:2 seq:ATCGTAT.

options:
  -h, --help            show this help message and exit
  --input INPUT         Single input file. Default: STDIN
  --pcr_handles, -p     Requests PCR handles to be added either side of final sequences.
  --column COLUMN, -c COLUMN
                        Column number to take from input as sequence. Default: 1
  --pcr_group PCR_GROUP, -g PCR_GROUP
                        Column heading containing groups to give different PCR handles to.
  --format {TSV,CSV}, -f {TSV,CSV}
                        Format of files. Default: TSV
  --output OUTPUT, -o OUTPUT
                        Output file. Default: STDOUT
```