# Dataset Presentation Materials Design

## Objective

Create a bilingual, supervisor-ready presentation layer for the four
OptionMetrics datasets used by the dissertation. The public GitHub repository
will explain the data and demonstrate the workflow without distributing
licensed records. A separate local workflow will inspect the real files during
supervision meetings.

## Audience and languages

The primary audience is the dissertation supervisor. Every narrative document
and data-dictionary entry will have separate English and Chinese versions.
Code, paths, and machine-readable field names will remain in English.

## Publication boundary

The repository may contain:

- dataset provenance, coverage, schema, and methodology;
- aggregate descriptive statistics suitable for academic reporting;
- synthetic records that reproduce the real column structure;
- code that profiles locally stored data.

The repository must not contain:

- records copied from the licensed OptionMetrics extracts;
- the four raw CSV files or fragments sampled from them;
- notebook outputs that display real rows;
- credentials, WRDS account details, or signed download links.

The existing `data/` ignore rule remains the primary safeguard. Private GitHub
or Git LFS will not be treated as permission to redistribute the source data.

## Components

### Bilingual dataset documentation

`DATASET.md` and `DATASET.zh-CN.md` will describe the source, four input tables,
their role in the dissertation, access restrictions, local directory layout,
profiling workflow, and reproduction instructions.

### Bilingual data dictionaries

`docs/data/data_dictionary_en.csv` and
`docs/data/data_dictionary_zh.csv` will contain one row per source field. Each
row will identify the source table, field name, meaning, expected type or unit,
and its use in the dissertation.

### Synthetic example

`examples/synthetic_option_data.csv` will contain a small set of invented SPX
option observations. Values will be clearly marked as synthetic and will be
constructed independently rather than copied or perturbed from a real row.

### Public overview notebook

`notebooks/dataset_overview_public.ipynb` will run solely from repository-safe
inputs. It will introduce the four tables, load the synthetic option example,
show representative schema checks, and visualise an illustrative volatility
smile. It must be runnable without access to WRDS or OptionMetrics.

### Local audit notebook

`notebooks/dataset_audit_local.ipynb` will locate the four ignored CSV files
under `data/`, display a temporary preview during a live meeting, and load a
precomputed profile. Cells that show real rows must be committed without
outputs.

### Profiling script

`scripts/profile_datasets.py` will scan CSV inputs in chunks so the 9.2 GB
option-price file does not need to fit in memory. It will calculate file size,
row count, column names, date range, per-column missing counts, and selected
numeric summaries. Its repository-safe aggregate output will be written to a
JSON file used by both notebooks.

## Data flow

1. The real CSV files remain under the ignored local `data/` directory.
2. The profiling script reads each CSV in chunks and produces aggregate JSON.
3. The local audit notebook reads the aggregate profile and may preview real
   rows without saving those outputs.
4. The public notebook reads only the aggregate profile and synthetic example.
5. Git checks reject any tracked path under `data/` and any notebook output
   containing a real-data preview.

## Error handling

The profiling script will:

- report a clear message when an expected input file is absent;
- process tables independently so one missing file does not conceal the status
  of the others;
- validate expected headers before profiling;
- write output only after a complete successful scan;
- avoid logging or copying individual real records.

The local notebook will explain how to run the profiler when the aggregate
profile is absent or stale.

## Verification

Verification will cover:

- Python syntax and a small synthetic-fixture run of the profiler;
- successful execution of the public notebook;
- JSON validation of both notebooks;
- confirmation that local-audit outputs are cleared;
- consistency between each CSV header and its bilingual dictionaries;
- a Git tracked-file check proving that `data/`, PDFs, and ZIPs remain absent;
- a scan for credentials, absolute user paths, and accidental real-data rows.

## Delivery

The work will be committed to `agent/upload-dissertation-materials`, pushed to
the existing remote branch, and added to draft pull request #1. The PR will
remain a draft for supervisor-facing review before it is merged into `main`.
