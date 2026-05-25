# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

`GENeSYS_MOD.data` — the input data set for the GENeSYS-MOD energy system
model. It holds per-parameter CSV files and a Python conversion pipeline that
combines them into the Excel files the model (`GENeSYS_MOD.jl`) reads.

## Layout

- `Data/Parameters/Par_X/Par_X.csv` — master CSV for each parameter
  (long format). Scenario subfolders (`Europe_EnVis_*`, `MiddleEarth`, ...)
  hold scenario-specific overrides.
- `Data/Parameters/00_Sets&Tags/` — `Sets_*.csv` (set members) and tag tables.
- `Data/Timeseries/TS_X/TS_X.csv` — wide format: `HOUR` column + one column
  per region. Row 0 is a `Source:` metadata line.
- `Conversion Script/` — Python pipeline (CSV → Excel) and run scripts.
- `Output/output_excel/` — generated `RegularParameters_*.xlsx` /
  `Timeseries_*.xlsx`.

## Conversion pipeline

- Run scripts: `script_eu_envis.py`, `script_middleearth.py`,
  `script_northamerica.py` — each sets a `Set_filter_file*.xlsx`, a
  `scenario_option`, and a `data_base_region`, then calls `master_function`.
- `Set_filter_file.xlsx` is the **universal** filter (every set member present);
  per-region presets (`Set_filter_file_MiddleEarth.xlsx`,
  `Set_filter_file_NorthAmerica.xlsx`) enable a chosen subset.
- A `scenario_option` must match an existing scenario subfolder name, or be
  `'None'`. A folder with only a `dummy.txt` marker is enough to register a
  scenario whose data lives entirely in the base CSVs.

## Conventions & gotchas

- Parameter CSVs are long-format: `<index cols...>, Value, <blank>, Unit,
  Source, Updated at, Updated by`. Index columns are everything left of `Value`.
- Trade parameters carry two region columns: `Region` and `Region.1`.
- The `Year` column may be a specific year or the literal `All`.
- All CSVs are **UTF-8** with **LF** line endings — preserve both on write
  (`open(..., encoding="utf-8", newline="")`, explicit `lineterminator`).
  Pandas `to_csv` defaults to the OS line ending / locale encoding — do not
  rely on the defaults.
- Files are git-tracked: review changes with `git diff`, revert with
  `git checkout`.

## Relationship to the models

Two model repositories consume the Excel files produced here:

- `GENeSYS_MOD.gms` — the original GAMS model (the reference implementation).
- `GENeSYS_MOD.jl` — the Julia/JuMP port.

Region/year sets, parameter coverage, and naming must stay consistent with what
both models expect. Set-member names here are the canonical identifiers used in
both models' code.
