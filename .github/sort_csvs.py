"""Sort the rows of the parameter CSVs by column order (column A, then B, then C, ...).

Usage (from the repository root):
    python .github/sort_csvs.py           # sort all files in place
    python .github/sort_csvs.py --check   # report unsorted files, exit 1 if any

Scope: every CSV below Data/Parameters except the Sets_*.csv lists, whose
order is meaningful (the model takes e.g. the first year as base year).
Data/Timeseries is not touched (rows are hours; first line is a Source note).

Comparison per cell: numbers compare numerically and before text
(2018 < 2020 < All); text compares case-insensitively, ties broken by the
exact text. Rows are moved as they are (original text, quoting and line
endings unchanged); the header stays first; rows without any content are
dropped. Encoding (incl. a BOM) and the final newline are preserved.
"""
import argparse
import csv
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARAMS = ROOT / "Data" / "Parameters"


def in_scope(path):
    return path.suffix.lower() == ".csv" and not path.name.startswith("Sets_")


def split_records(text, eol):
    """Split text into raw records; a quoted field may span several lines."""
    records, buf, quotes = [], [], 0
    for line in text.split(eol):
        buf.append(line)
        quotes += line.count('"')
        if quotes % 2 == 0:
            records.append(eol.join(buf))
            buf, quotes = [], 0
    if buf:
        records.append(eol.join(buf))
    return records


def cell_key(cell):
    s = cell.strip()
    try:
        x = float(s)
        if math.isfinite(x):
            return (0, x, "", s)
    except ValueError:
        pass
    return (1, 0.0, s.casefold(), s)


def row_key(record):
    fields = next(csv.reader([record]), [])
    return tuple(cell_key(c) for c in fields)


def is_empty(record):
    return not any(c.strip() for c in next(csv.reader([record]), []))


def sorted_text(raw):
    bom = raw.startswith("﻿")
    text = raw[1:] if bom else raw
    eol = "\r\n" if "\r\n" in text else "\n"
    trailing = text.endswith(eol)
    if trailing:
        text = text[: -len(eol)]
    records = split_records(text, eol)
    header, body = records[0], [r for r in records[1:] if not is_empty(r)]
    body.sort(key=row_key)
    out = eol.join([header] + body) + (eol if trailing else "")
    return ("﻿" if bom else "") + out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="only report unsorted files")
    args = ap.parse_args()

    unsorted = []
    for path in sorted(p for p in PARAMS.rglob("*.csv") if in_scope(p)):
        raw = path.read_bytes().decode("utf-8")
        new = sorted_text(raw)
        if new != raw:
            unsorted.append(path.relative_to(ROOT).as_posix())
            if not args.check:
                path.write_bytes(new.encode("utf-8"))

    verb = "not sorted" if args.check else "sorted"
    for p in unsorted:
        print(f"{verb}: {p}")
    print(f"{len(unsorted)} file(s) {verb}.")
    if args.check and unsorted:
        print("Run `python .github/sort_csvs.py` and commit the result.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
