# Executed Notebook and Conda Environment Design

## Objective

Replace the current output-free public dataset overview with two
supervisor-ready executed notebooks: one in English and one in Chinese.
Reproduce their outputs in a dedicated Conda environment. Keep any output that
contains licensed source rows strictly local and untracked.

## Environment

The repository will include `environment.yml` defining the
`dissertation-display` environment with:

- Python 3.12;
- JupyterLab and ipykernel;
- nbformat and nbclient;
- pandas;
- matplotlib.

The environment will be created with Conda and registered as the
`Python (dissertation-display)` Jupyter kernel. Notebook execution and
verification commands will use `conda run -n dissertation-display` so they do
not depend on the active shell environment.

## Public notebooks

One deterministic builder will generate:

- `notebooks/dataset_overview_en.ipynb`;
- `notebooks/dataset_overview_zh.ipynb`.

Both notebooks will share the same analysis code and differ only in narrative
language, headings, table labels, and figure labels. They will read:

- `docs/data/dataset_profile.json`, which contains aggregate statistics only;
- `docs/data/data_dictionary_en.csv` or
  `docs/data/data_dictionary_zh.csv`;
- `examples/synthetic_option_data.csv`, which contains invented records.

The notebooks will be executed in the Conda environment and committed with
outputs. Their outputs may contain:

- real aggregate row counts, date ranges, file sizes, missing-value rates, and
  selected numeric summaries;
- bilingual data-quality tables;
- charts derived from aggregate statistics;
- tables and volatility-smile charts derived from synthetic option records.

They must not contain a row copied from a licensed CSV, an absolute user path,
credentials, or an embedded copy of the raw files.

## Local meeting notebook

`notebooks/dataset_audit_local.ipynb` remains a tracked template with cleared
outputs. It may preview five real rows from each authorised local CSV when
executed.

The executed meeting copy will be written to:

`/.local-notebooks/dataset_audit_with_output.ipynb`

The entire `/.local-notebooks/` directory will be ignored by Git. Tests will
verify that the template has no outputs, the local executed copy has outputs,
and no path under `.local-notebooks/` is tracked.

## Data flow

1. The four licensed extracts remain under the ignored `/data/` directory.
2. The existing streaming profiler creates aggregate-only JSON.
3. The notebook builder creates language-specific public notebooks and the
   output-free local template.
4. Conda executes both public notebooks in place and saves their safe outputs.
5. Conda executes the local template into the ignored `.local-notebooks/`
   destination.
6. Automated checks inspect all committed notebook outputs for restricted
   fragments and absolute paths.

## Error handling

- Environment creation must stop if dependency solving or installation fails.
- Notebook execution must stop on the first failing cell.
- The public notebooks must report a clear missing-file error when repository
  inputs are absent.
- The local notebook must report missing local CSV files without copying
  partial results into a tracked notebook.
- Direct publication to `main` occurs only after tests pass on the merged
  `main` worktree state.

## Verification

The verification suite will confirm:

- the Conda environment imports every declared Python package;
- both public notebooks use the `dissertation-display` kernel metadata;
- both public notebooks contain executed code-cell outputs;
- the English and Chinese notebooks use identical code-cell sources;
- all public outputs contain only aggregate or synthetic content;
- the local template contains no output;
- the ignored local meeting copy exists and contains executed output;
- no raw dataset, PDF, ZIP, `.local-notebooks/` path, credential, or absolute
  user path is tracked;
- the test suite passes before and after integration into `main`.

## Publication workflow

After verification:

1. update local `main` from `origin/main`;
2. merge the completed feature commits into local `main`;
3. rerun the full verification suite on `main`;
4. push `main` directly to `origin/main`;
5. close draft pull request #2 without merging it;
6. verify the remote `main` SHA and tracked file list.

No new pull request will be created.
