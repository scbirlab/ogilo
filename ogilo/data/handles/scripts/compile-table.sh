#!/usr/bin/env bash

sort_table () {
    local sep=${3:-,}
    local field=$(get_column_number "$1" $2)
    cat <(head -n1 "$1") <(tail -n+2 "$1" | sort -k"$field" -t"$sep")
}

set -e
set -x

script_dir="$(dirname $0)"
inputs=("$script_dir"/../raw/*.csv)
output_dir="$script_dir"/..
temp_dir="$script_dir"/../temp

mkdir -p "$temp_dir"

for inp in "${inputs[@]}"
do
    inp_id=$(basename "$inp" .csv)
    this_output_file="$output_dir"/"$inp_id"-pcr-handles.csv
    pp_seq_file="$temp_dir"/"$inp_id"-preprocessed.csv
    fw_seq_file="$temp_dir"/"$inp_id"-fw.csv
    rv_seq_file="$temp_dir"/"$inp_id"-rv.csv

    cat "$inp" | sed '1s/^\xEF\xBB\xBF//' | tr -d $'\r' | grep -v '^#' > "$pp_seq_file"
    cat \
        <(paste -d, \
            <(head -n1 "$pp_seq_file") \
            <(echo "reverse_complement")) \
        <(paste -d, \
            <(tail -n+2 "$pp_seq_file") \
            <(tail -n+2 "$pp_seq_file" | cut -d, -f4 | tr ATCG TAGC | rev)) \
    > "$pp_seq_file".temp && mv "$pp_seq_file".temp "$pp_seq_file"

    awk -F, -v OFS=, \
        'NR == 1 { print $0 } (NR > 1 && $3 == "yes") { $(NF-1)=$NF; print $0 } (NR > 1 && $3 == "no") { print $0 }' \
        "$pp_seq_file" \
    | awk -F, -v OFS=, \
        '{ print "__join__",$1,$2,$(NF-1) }' \
    >> "$pp_seq_file".temp && mv "$pp_seq_file".temp "$pp_seq_file"

    awk -F, -v OFS=, \
        'NR == 1 { print $1,$2,"pcr_handle_f" } (NR > 1 && $3 == "yes") { print $1,$2,$NF }' \
        "$pp_seq_file" \
    > "$fw_seq_file"

    awk -F, -v OFS=, \
        'NR == 1 { print $1,$2,"pcr_handle_r" } (NR > 1 && $3 == "no") { print $1,$2,$NF }' \
        "$pp_seq_file" \
    > "$rv_seq_file"

    join --header -1 1 -2 1 -t, \
        "$fw_seq_file" "$rv_seq_file" \
    | cut -d, -f2- \
    | awk -F, -v OFS=, -v inp_id="$inp_id" \
        'NR == 1 { print $1,$2,$4 } NR > 1 { print inp_id"-"$1"."$3,$2,$4 }' \
    > "$this_output_file"

done

rm -r "$temp_dir"