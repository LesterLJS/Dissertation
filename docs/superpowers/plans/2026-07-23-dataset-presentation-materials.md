# Dataset Presentation Materials Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build bilingual public dataset documentation and a safe local workflow for presenting the four dissertation OptionMetrics extracts to a supervisor.

**Architecture:** A dependency-free Python profiler streams ignored CSV files in bounded batches and emits aggregate JSON. Repository-safe documentation, synthetic data, and a public notebook use only metadata and invented observations; a separate output-free notebook previews local real data during meetings.

**Tech Stack:** Python 3 standard library, `unittest`, CSV, JSON, Jupyter Notebook JSON format, Markdown, inline SVG.

## Global Constraints

- Never track records copied from the four licensed OptionMetrics CSV files.
- Keep all real extracts under the ignored `data/` directory.
- Commit local-audit notebooks with all code-cell outputs cleared.
- Produce separate English and Chinese narrative documents and dictionaries.
- Keep the public notebook runnable without WRDS, OptionMetrics, pandas, or matplotlib.
- Store only aggregate statistics suitable for academic reporting.

---

## File map

- `scripts/profile_datasets.py`: validate and stream the four local CSV files; write aggregate JSON atomically.
- `tests/test_profile_datasets.py`: verify schema validation, batch processing, missing values, dates, numeric summaries, and safe output.
- `tests/fixtures/data/*.csv`: invented fixtures with the four expected schemas.
- `docs/data/dataset_profile.json`: aggregate profile produced from local real files.
- `docs/data/data_dictionary_en.csv`: English definitions for all source columns.
- `docs/data/data_dictionary_zh.csv`: Chinese definitions for the same source columns.
- `examples/synthetic_option_data.csv`: invented option observations using the 38-column option schema.
- `scripts/build_dataset_notebooks.py`: deterministically build both notebooks without `nbformat`.
- `tests/test_dataset_materials.py`: verify dictionaries, synthetic markers, notebook safety, and tracked-file boundaries.
- `notebooks/dataset_overview_public.ipynb`: public, dependency-free overview and synthetic smile visualisation.
- `notebooks/dataset_audit_local.ipynb`: local real-data preview and aggregate-profile walkthrough, saved without outputs.
- `DATASET.md`: English guide.
- `DATASET.zh-CN.md`: Chinese guide.

### Task 1: Streaming dataset profiler

**Files:**
- Create: `scripts/profile_datasets.py`
- Create: `tests/test_profile_datasets.py`
- Create: `tests/fixtures/data/Index Dividend Yield.csv`
- Create: `tests/fixtures/data/Zero Coupon Yield Curve.csv`
- Create: `tests/fixtures/data/option price.csv`
- Create: `tests/fixtures/data/security price.csv`

**Interfaces:**
- Produces: `profile_csv(path: Path, expected_columns: tuple[str, ...], numeric_columns: tuple[str, ...], batch_size: int) -> dict`
- Produces: `profile_directory(data_dir: Path, batch_size: int = 100_000) -> dict`
- Produces: CLI `python3 scripts/profile_datasets.py --data-dir DIR --output FILE --batch-size N`

- [ ] **Step 1: Write failing profiler tests**

Create `unittest` cases that import the script and assert:

```python
profile = profile_csv(fixture, expected_columns, ("rate",), batch_size=2)
self.assertEqual(profile["row_count"], 3)
self.assertEqual(profile["date_range"], {"min": "2020-01-02", "max": "2020-01-06"})
self.assertEqual(profile["missing_counts"]["rate"], 1)
self.assertEqual(profile["numeric_summary"]["rate"]["count"], 2)
self.assertAlmostEqual(profile["numeric_summary"]["rate"]["mean"], 1.25)
```

Add tests proving a changed header raises `SchemaError`, a missing table is
reported in `profile_directory()["missing_files"]`, and output JSON contains no
fixture row values such as the invented symbol `SYNTH_ROW_SENTINEL`.

- [ ] **Step 2: Run tests and confirm the expected failure**

Run:

```bash
python3 -m unittest tests/test_profile_datasets.py -v
```

Expected: failure because `scripts/profile_datasets.py` does not exist.

- [ ] **Step 3: Implement the profiler**

Define exact schemas from the current CSV headers. Use `csv.DictReader`,
`itertools.islice`, and a loop over batches so memory use is bounded. Track:

```python
{
    "file_name": path.name,
    "file_size_bytes": path.stat().st_size,
    "row_count": int,
    "columns": list[str],
    "date_range": {"min": str | None, "max": str | None},
    "missing_counts": dict[str, int],
    "numeric_summary": {
        column: {"count": int, "min": float | None, "max": float | None, "mean": float | None}
    },
}
```

Use running count, sum, minimum, and maximum values; do not store observations.
Write JSON to a sibling temporary file and replace the destination only after
all available tables finish successfully. The CLI exits nonzero for schema or
parsing errors and prints missing filenames without exposing row contents.

- [ ] **Step 4: Run the profiler tests**

Run:

```bash
python3 -m unittest tests/test_profile_datasets.py -v
```

Expected: all profiler tests pass.

- [ ] **Step 5: Commit Task 1**

```bash
git add scripts/profile_datasets.py tests/test_profile_datasets.py tests/fixtures/data
git commit -m "Add safe streaming dataset profiler"
```

### Task 2: Bilingual dictionaries and synthetic example

**Files:**
- Create: `docs/data/data_dictionary_en.csv`
- Create: `docs/data/data_dictionary_zh.csv`
- Create: `examples/synthetic_option_data.csv`
- Create: `tests/test_dataset_materials.py`

**Interfaces:**
- Consumes: `EXPECTED_SCHEMAS` exported by `scripts/profile_datasets.py`
- Produces: dictionaries with columns `table,field,description,type_or_unit,dissertation_use`
- Produces: a 38-column synthetic option CSV containing a `synthetic_only` marker value

- [ ] **Step 1: Write failing material-integrity tests**

Add `unittest` cases that:

```python
self.assertEqual(english_pairs, chinese_pairs)
self.assertEqual(english_pairs, expected_schema_pairs)
self.assertEqual(synthetic_reader.fieldnames, list(EXPECTED_SCHEMAS["option price.csv"]))
self.assertGreaterEqual(len(list(synthetic_reader)), 6)
self.assertTrue(all(row["symbol_flag"] == "synthetic_only" for row in rows))
```

Also assert that no value from the first real option row appears as a complete
row in the synthetic file.

- [ ] **Step 2: Run the new tests and confirm failure**

Run:

```bash
python3 -m unittest tests/test_dataset_materials.py -v
```

Expected: failure because dictionaries and synthetic data are absent.

- [ ] **Step 3: Create the dictionaries**

Write one entry for every column in each source table. Preserve field names
exactly. Explain units explicitly where known, including `strike_price`
scaling, rates and implied volatility, option Greeks, dates, identifiers,
prices, returns, volume, open interest, contract size, and security metadata.
Use `unknown/not documented` and `原始提取文件未注明` instead of inventing a
definition where the extract is ambiguous.

- [ ] **Step 4: Create synthetic option observations**

Create at least six invented call and put rows across strikes 4000–5000 and
expiries in 2030. Use non-real identifiers beginning with `SYN`, ticker
`SYNTHETIC_SPX`, and `symbol_flag=synthetic_only`. Values should form a
plausible illustrative smile but must not derive from a real record.

- [ ] **Step 5: Run material-integrity tests**

Run:

```bash
python3 -m unittest tests/test_dataset_materials.py -v
```

Expected: all current tests pass.

- [ ] **Step 6: Commit Task 2**

```bash
git add docs/data examples/synthetic_option_data.csv tests/test_dataset_materials.py
git commit -m "Add bilingual dictionaries and synthetic data"
```

### Task 3: Deterministic public and local notebooks

**Files:**
- Create: `scripts/build_dataset_notebooks.py`
- Create: `notebooks/dataset_overview_public.ipynb`
- Create: `notebooks/dataset_audit_local.ipynb`
- Modify: `tests/test_dataset_materials.py`

**Interfaces:**
- Consumes: `docs/data/dataset_profile.json`
- Consumes: `examples/synthetic_option_data.csv`
- Produces: valid notebook format version 4 JSON with stable cell IDs

- [ ] **Step 1: Add failing notebook-safety tests**

Verify:

```python
self.assertEqual(notebook["nbformat"], 4)
self.assertTrue(all(cell.get("outputs", []) == [] for cell in code_cells))
self.assertNotIn("/Users/", json.dumps(notebook))
self.assertNotIn("option price.csv\\n108105,1996-01-04", json.dumps(notebook))
```

Assert that the public notebook never opens `data/`, and the local notebook
limits previews with `itertools.islice(reader, 5)`.

- [ ] **Step 2: Run the notebook tests and confirm failure**

Run:

```bash
python3 -m unittest tests/test_dataset_materials.py -v
```

Expected: notebook-file-not-found failures.

- [ ] **Step 3: Implement the notebook builder**

Build notebooks as plain dictionaries and serialize with
`json.dump(..., ensure_ascii=False, indent=1)`. The public notebook will:

1. explain the licensing boundary in English and Chinese;
2. load aggregate JSON and render a compact Markdown table;
3. load the synthetic example with `csv.DictReader`;
4. create an inline SVG volatility-smile chart from synthetic strikes and IVs.

The local notebook will:

1. verify all expected files under repository-relative `data/`;
2. read only five preview rows per file;
3. load aggregate JSON;
4. show commands for refreshing the profile.

Set `execution_count` to `null` and `outputs` to `[]` in every code cell.

- [ ] **Step 4: Generate and validate notebooks**

Run:

```bash
python3 scripts/build_dataset_notebooks.py
python3 -m json.tool notebooks/dataset_overview_public.ipynb >/dev/null
python3 -m json.tool notebooks/dataset_audit_local.ipynb >/dev/null
python3 -m unittest tests/test_dataset_materials.py -v
```

Expected: both JSON validations and all tests pass.

- [ ] **Step 5: Commit Task 3**

```bash
git add scripts/build_dataset_notebooks.py notebooks tests/test_dataset_materials.py
git commit -m "Add public and local dataset notebooks"
```

### Task 4: Real aggregate profile

**Files:**
- Create: `docs/data/dataset_profile.json`

**Interfaces:**
- Consumes: ignored local files under `data/`
- Produces: aggregate-only JSON consumed by both notebooks

- [ ] **Step 1: Profile the four real extracts**

Run:

```bash
python3 scripts/profile_datasets.py \
  --data-dir data \
  --output docs/data/dataset_profile.json \
  --batch-size 100000
```

Expected: four profiled tables, zero missing files, no printed records.

- [ ] **Step 2: Validate the aggregate output**

Run:

```bash
python3 -m json.tool docs/data/dataset_profile.json >/dev/null
rg -n '098A3\\.1A|24\\.75,25\\.75|64881510' docs/data/dataset_profile.json
```

Expected: valid JSON and no matches for known real-row fragments.

- [ ] **Step 3: Rebuild notebooks against the real profile**

Run:

```bash
python3 scripts/build_dataset_notebooks.py
python3 -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 4: Commit Task 4**

```bash
git add docs/data/dataset_profile.json notebooks
git commit -m "Add aggregate dataset profile"
```

### Task 5: Bilingual supervisor guides and final safety gate

**Files:**
- Create: `DATASET.md`
- Create: `DATASET.zh-CN.md`
- Modify: `.gitignore`
- Modify: `tests/test_dataset_materials.py`

**Interfaces:**
- Consumes: profiler CLI, notebooks, dictionaries, synthetic example
- Produces: complete English and Chinese usage instructions

- [ ] **Step 1: Add failing repository-safety tests**

Use `git ls-files` in a test subprocess and fail if a tracked path starts with
`data/` or ends in `.pdf` or `.zip`. Assert `.gitignore` contains `data/`,
`*.pdf`, `*.zip`, and notebook checkpoint rules. Assert both guides link to
the profile, dictionaries, synthetic file, and both notebooks.

- [ ] **Step 2: Run safety tests and confirm guide-related failure**

Run:

```bash
python3 -m unittest tests/test_dataset_materials.py -v
```

Expected: failure because the bilingual guides do not yet exist.

- [ ] **Step 3: Write English and Chinese guides**

Each guide will cover:

- provenance and the four-table inventory;
- licensing and non-redistribution notice;
- aggregate profile and synthetic-example interpretation;
- exact profiler command;
- public-notebook and live-meeting workflows;
- a five-minute supervisor presentation sequence;
- citation wording for OptionMetrics/WRDS;
- instructions for authorised researchers to obtain data independently.

- [ ] **Step 4: Strengthen ignore rules**

Keep `data/` ignored and add:

```gitignore
docs/data/*.tmp
notebooks/.ipynb_checkpoints/
```

- [ ] **Step 5: Run the full verification suite**

Run:

```bash
python3 -m unittest discover -s tests -v
python3 -m json.tool notebooks/dataset_overview_public.ipynb >/dev/null
python3 -m json.tool notebooks/dataset_audit_local.ipynb >/dev/null
git diff --check
git ls-files | rg '^(data/|.*\\.(pdf|zip)$)' && exit 1 || true
rg -n -i '(api[_-]?key|secret|password|bearer|/Users/)' \
  DATASET.md DATASET.zh-CN.md docs/data examples notebooks scripts
```

Expected: tests and JSON validation pass; no tracked restricted files,
credentials, or absolute user paths.

- [ ] **Step 6: Commit Task 5**

```bash
git add .gitignore DATASET.md DATASET.zh-CN.md tests/test_dataset_materials.py
git commit -m "Document bilingual dataset presentation workflow"
```

### Task 6: Publish and update draft PR

**Files:**
- No new files

**Interfaces:**
- Publishes: local branch commits to `origin/agent/upload-dissertation-materials`
- Updates: draft PR #1

- [ ] **Step 1: Verify branch state and complete diff**

Run:

```bash
git status --short --branch
git diff origin/main...HEAD --stat
git log --oneline origin/main..HEAD
```

Expected: clean working tree and only intended commits.

- [ ] **Step 2: Push the branch**

Run:

```bash
git push origin agent/upload-dissertation-materials
```

Expected: remote branch advances to local `HEAD`.

- [ ] **Step 3: Update PR #1**

Update the draft PR body with the bilingual guides, safe profiling workflow,
synthetic example, aggregate profile, verification commands, and explicit
confirmation that raw OptionMetrics data remain excluded.

- [ ] **Step 4: Verify remote state**

Run:

```bash
test "$(git rev-parse HEAD)" = \
  "$(git rev-parse origin/agent/upload-dissertation-materials)"
gh pr view 1 --repo LesterLJS/Dissertation \
  --json isDraft,state,headRefOid,files,url
```

Expected: local and remote SHAs match; PR #1 is open and draft; its file list
contains no path under `data/` and no PDF or ZIP.
