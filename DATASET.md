# Dissertation dataset guide

[中文版本](DATASET.zh-CN.md)

## Purpose

This repository documents the data used to study SPX option pricing and implied
volatility. It separates public research materials from licensed source data:

- GitHub contains code, schemas, aggregate statistics, and invented examples.
- The ignored local `data/` directory contains the authorised OptionMetrics
  extracts.
- No row copied from the source extracts is published in this repository.

## Source and access

The four extracts were obtained from OptionMetrics through an institutional
subscription and are treated as licensed research data. Repository access,
private GitHub visibility, or Git LFS does not grant permission to redistribute
them. An authorised researcher should retrieve the same tables independently
through their institution rather than request a copy from this repository.

Do not commit WRDS credentials, account details, signed links, or notebook
outputs that display real rows.

## Dataset inventory

The aggregate profile was generated from the local extracts on 23 July 2026.

| Local table | Role | Rows | Observation dates |
|---|---|---:|---|
| `Index Dividend Yield.csv` | Daily SPX dividend-yield input | 7,463 | 1996-01-04 to 2025-08-29 |
| `Zero Coupon Yield Curve.csv` | Maturity-dependent risk-free rates | 304,301 | 1996-01-02 to 2025-08-29 |
| `option price.csv` | Option quotes and OptionMetrics analytics | 48,335,273 | 1996-01-04 to 2025-08-29 |
| `security price.csv` | Daily SPX underlying prices and returns | 7,465 | 1996-01-02 to 2025-08-29 |

The machine-readable aggregate profile is
[`docs/data/dataset_profile.json`](docs/data/dataset_profile.json). It contains
file size, row count, schema, date range, missing-value counts, and selected
numeric summaries. It contains no individual observations.

## Public presentation materials

- English dictionary:
  [`docs/data/data_dictionary_en.csv`](docs/data/data_dictionary_en.csv)
- Chinese dictionary:
  [`docs/data/data_dictionary_zh.csv`](docs/data/data_dictionary_zh.csv)
- Invented 38-column example:
  [`examples/synthetic_option_data.csv`](examples/synthetic_option_data.csv)
- Executed English overview:
  [`notebooks/dataset_overview_en.ipynb`](notebooks/dataset_overview_en.ipynb)
- Executed Chinese overview:
  [`notebooks/dataset_overview_zh.ipynb`](notebooks/dataset_overview_zh.ipynb)
- Local meeting audit:
  [`notebooks/dataset_audit_local.ipynb`](notebooks/dataset_audit_local.ipynb)

The synthetic file uses non-real identifiers, 2030 dates, ticker
`SYNTHETIC_SPX`, and `symbol_flag=synthetic_only`. It is for demonstrating the
schema and an illustrative volatility smile; it is not an empirical sample.

## Conda environment

The reproducible environment is declared in
[`environment.yml`](environment.yml) and is named `dissertation-display`.
Create and open it with:

```bash
conda env create -f environment.yml
conda activate dissertation-display
jupyter lab
```

The two public notebooks are committed with safe executed outputs. To rebuild
and execute them:

```bash
python3 scripts/build_dataset_notebooks.py
DATASET_NOTEBOOK_LANGUAGE=en conda run -n dissertation-display \
  jupyter execute notebooks/dataset_overview_en.ipynb --inplace
DATASET_NOTEBOOK_LANGUAGE=zh conda run -n dissertation-display \
  jupyter execute notebooks/dataset_overview_zh.ipynb --inplace
```

## Reproducing the aggregate profile

Place the authorised extracts at:

```text
data/
├── Index Dividend Yield.csv
├── Zero Coupon Yield Curve.csv
├── option price.csv
└── security price.csv
```

Then run:

```bash
python3 scripts/profile_datasets.py \
  --data-dir data \
  --output docs/data/dataset_profile.json \
  --batch-size 100000
```

The profiler uses only the Python standard library. It validates the exact
headers and scans in bounded batches. It does not retain observations or print
rows. On the development machine, profiling all four files took about
four-and-a-half minutes.

## Five-minute supervisor presentation

1. **Research provenance — 30 seconds.** State that the study uses licensed
   OptionMetrics SPX data obtained through institutional access.
2. **Coverage — 45 seconds.** Show the four-table inventory and the 1996–2025
   observation period.
3. **Structure — 60 seconds.** Open the bilingual dictionary and explain the
   joins through `secid` and `date`.
4. **Quality — 60 seconds.** Use the aggregate profile to discuss sample size,
   missingness, and selected variable ranges.
5. **Safe example — 45 seconds.** Open
   `notebooks/dataset_overview_en.ipynb` or
   `notebooks/dataset_overview_zh.ipynb` and show its saved aggregate tables
   and synthetic volatility smile.
6. **Real-data check — 60 seconds.** On the authorised local machine only,
   open `.local-notebooks/dataset_audit_with_output.ipynb` to show five rows
   from each table.

`notebooks/dataset_audit_local.ipynb` is the output-free tracked template.
The executed `.local-notebooks/dataset_audit_with_output.ipynb` contains
licensed rows and must never be uploaded.

## Suggested citation

Adapt the following wording to the dissertation's required citation style and
the exact institutional subscription:

> OptionMetrics. *IvyDB US: Historical option prices and implied volatility
> data*. Accessed through Wharton Research Data Services under an institutional
> subscription.

The citation acknowledges the source but does not replace the applicable data
licence or the institution's required attribution.

## Validation

Run the repository checks with:

```bash
conda run -n dissertation-display python -m unittest discover -s tests -v
python3 -m json.tool notebooks/dataset_overview_en.ipynb >/dev/null
python3 -m json.tool notebooks/dataset_overview_zh.ipynb >/dev/null
python3 -m json.tool notebooks/dataset_audit_local.ipynb >/dev/null
```

The tests verify schema coverage, synthetic-data markers, safe public outputs,
an output-free local template, repository-relative paths, and exclusion of raw
datasets, local meeting outputs, PDFs, and ZIP archives.
