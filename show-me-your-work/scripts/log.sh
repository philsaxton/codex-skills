#!/usr/bin/env bash
# Append one decision entry. One writer must own each log.
# Usage: log.sh <logfile> <run> <phase> <decision> <why> <evidence> <result>
set -euo pipefail

if [ "$#" -ne 7 ]; then
    printf 'usage: log.sh <logfile> <run> <phase> <decision> <why> <evidence> <result>\n' >&2
    exit 1
fi

logfile="$1"
shift
clean() {
    local value separator
    value=$1
    # Byte-preserving substitutions avoid locale-sensitive external filters.
    for separator in $'\t' $'\n' $'\r' $'\v' $'\f' $'\x1c' $'\x1d' $'\x1e' \
        $'\xc2\x85' $'\xe2\x80\xa8' $'\xe2\x80\xa9'; do
        value=${value//"$separator"/ }
    done
    # Also catch formula prefixes hidden behind leading whitespace.
    if [[ "$value" =~ ^[[:space:]]*[=+@-] ]]; then
        value="'$value"
    fi
    # Quote-aware TSV readers must recover literal quotes, including at cell start.
    if [[ "$value" == *\"* ]]; then
        value=${value//\"/\"\"}
        printf '"%s"' "$value"
    else
        printf '%s' "$value"
    fi
}

# Top-level assignments propagate failures before creating or appending a log.
cells=()
for cell in "$@"; do
    encoded=$(clean "$cell")
    cells+=("$encoded")
done
timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
header=$'ts\trun\tphase\tdecision\twhy\tevidence\tresult'

if [ -s "$logfile" ]; then
    first_line=''
    IFS= read -r first_line < "$logfile" || true
    if [ "$first_line" != "$header" ]; then
        printf 'refusing to append: unexpected log header\n' >&2
        exit 1
    fi
    if [ "$(tail -c 1 < "$logfile" | wc -l | tr -d ' ')" != 1 ]; then
        printf 'refusing to append: log has an incomplete final line\n' >&2
        exit 1
    fi
else
    mkdir -p -- "$(dirname -- "$logfile")"
    printf '%s\n' "$header" >> "$logfile"
fi

printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$timestamp" "${cells[@]}" >> "$logfile"
