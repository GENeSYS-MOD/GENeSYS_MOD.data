#!/usr/bin/env python3
"""
find_missing_source.py

Place this file in:
  root_folder/.github/find_missing_source.py

It will automatically scan:
  root_folder/Data

and write output next to the script (in .github/) by default.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd


def detect_source_column(columns) -> Optional[str]:
    """Return the actual column name whose stripped lowercase equals 'source'."""
    for c in columns:
        if str(c).strip().lower() == "source":
            return c
    return None


def read_csv_robust(path: Path) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Read CSV with delimiter sniffing and tolerant parsing."""
    try:
        df = pd.read_csv(
            path,
            sep=None,               # sniff delimiter
            engine="python",        # required for sep=None
            dtype=str,              # keep as strings
            keep_default_na=True,
            on_bad_lines="skip",
            encoding_errors="replace",
        )
        return df, None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def is_missing_source(series: pd.Series) -> pd.Series:
    """True if value is NaN or only whitespace after stripping."""
    s = series.astype("string")
    return s.isna() | (s.str.strip() == "")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        type=str,
        default="missing_sources.xlsx",
        help="Output file name (.csv or .xlsx). Default: missing_sources.xlsx",
    )
    ap.add_argument(
        "--include-errors",
        action="store_true",
        help="Also write a *_errors.csv listing unreadable CSVs and reasons.",
    )
    args = ap.parse_args()

    # Script is in root_folder/.github/
    script_dir = Path(__file__).resolve().parent              # root_folder/.github
    root_folder = script_dir.parent                           # root_folder
    data_dir = root_folder / "Data"                           # root_folder/Data

    if not data_dir.exists() or not data_dir.is_dir():
        raise SystemExit(f'Expected folder not found: "{data_dir}"')

    out_path = (script_dir / args.out).resolve()

    missing_rows = []
    errors = []

    for dirpath, _, filenames in os.walk(data_dir):
        for fn in filenames:
            if not fn.lower().endswith(".csv"):
                continue

            csv_path = Path(dirpath) / fn
            df, err = read_csv_robust(csv_path)
            if df is None:
                errors.append({"file": str(csv_path), "error": err})
                continue

            source_col = detect_source_column(df.columns)
            if source_col is None:
                # No source column; skip silently (or record as error if you want)
                continue

            mask = is_missing_source(df[source_col])
            if not mask.any():
                continue

            hit = df.loc[mask].copy()

            # Add traceability columns
            # Store path relative to root_folder for cleaner output
            rel_path = csv_path.relative_to(root_folder)
            hit.insert(0, "__file__", str(rel_path))

            # Row number in original file: +2 to account for header being row 1
            hit.insert(1, "__row__", (hit.index.to_series() + 2).astype(int))

            missing_rows.append(hit)

    if missing_rows:
        result = pd.concat(missing_rows, ignore_index=True)
    else:
        result = pd.DataFrame(columns=["__file__", "__row__"])

    # Write main output
    if out_path.suffix.lower() == ".xlsx":
        with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
            result.to_excel(writer, index=False, sheet_name="missing_source")
    else:
        result.to_csv(out_path, index=False, encoding="utf-8")

    # Optionally write errors
    if args.include_errors:
        err_path = out_path.with_name(out_path.stem + "_errors.csv")
        pd.DataFrame(errors).to_csv(err_path, index=False, encoding="utf-8")

    print(f"Script location: {script_dir}")
    print(f"Scanning folder:  {data_dir}")
    print(f"Missing rows:     {len(result)}")
    print(f"Wrote output:     {out_path}")
    if args.include_errors:
        print(f"Wrote errors:     {err_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
