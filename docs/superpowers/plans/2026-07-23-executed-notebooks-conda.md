# Executed Notebooks and Conda Environment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce separate English and Chinese dataset-presentation notebooks with safe saved outputs, plus an ignored local notebook containing authorised real-row previews, all executed reproducibly in a dedicated Conda environment.

**Architecture:** A deterministic Python builder creates two language variants that share identical analysis code and one output-free local audit template. Conda executes the public variants in place and writes the real-row meeting execution to an ignored local directory; automated tests enforce the publication boundary before changes are merged and pushed directly to `main`.

**Tech Stack:** Conda, Python 3.12, JupyterLab, ipykernel, nbformat, nbclient, nbconvert, pandas, matplotlib, `unittest`, Git.

## Global Constraints

- The Conda environment name is `dissertation-display`.
- Public notebooks may save real aggregate statistics and synthetic outputs only.
- No public notebook output may contain a row copied from a licensed CSV.
- `notebooks/dataset_audit_local.ipynb` remains committed without outputs.
- `/.local-notebooks/` contains the executed real-row meeting copy and is never tracked.
- English and Chinese public notebooks must use identical code-cell sources.
- Publish by updating `main` directly; do not create a new pull request.
- Close draft pull request #2 after `origin/main` is verified.

---

## File map

- `environment.yml`: exact reproducible Conda environment.
- `scripts/build_dataset_notebooks.py`: build English and Chinese public notebooks plus the local audit template.
- `notebooks/dataset_overview_en.ipynb`: executed English public presentation.
- `notebooks/dataset_overview_zh.ipynb`: executed Chinese public presentation.
- `notebooks/dataset_audit_local.ipynb`: output-free real-data meeting template.
- `.local-notebooks/dataset_audit_with_output.ipynb`: ignored executed meeting copy.
- `tests/test_dataset_materials.py`: environment declaration, notebook parity, output, and safety checks.
- `.gitignore`: ignore the local executed-notebook directory.
- `DATASET.md`: link and execution instructions for the English notebook.
- `DATASET.zh-CN.md`: link and execution instructions for the Chinese notebook.

### Task 1: Reproducible Conda environment declaration

**Files:**
- Create: `environment.yml`
- Modify: `tests/test_dataset_materials.py`

**Interfaces:**
- Produces: Conda environment `dissertation-display`
- Provides: commands `python`, `jupyter`, `jupyter-execute`, and `jupyter-nbconvert`
- Provides: importable pandas, matplotlib, nbformat, nbclient, and nbconvert packages

- [ ] **Step 1: Write a failing environment-file test**

Add a `CondaEnvironmentTest` that reads `environment.yml` as text and asserts:

```python
self.assertIn("name: dissertation-display", content)
for dependency in (
    "python=3.12",
    "jupyterlab",
    "ipykernel",
    "nbformat",
    "nbclient",
    "nbconvert",
    "pandas",
    "matplotlib",
):
    self.assertIn(f"  - {dependency}", content)
```

- [ ] **Step 2: Run the test and confirm failure**

Run:

```bash
python3 -m unittest \
  tests.test_dataset_materials.CondaEnvironmentTest -v
```

Expected: FAIL because `environment.yml` is absent.

- [ ] **Step 3: Add the environment definition**

Create:

```yaml
name: dissertation-display
channels:
  - conda-forge
dependencies:
  - python=3.12
  - jupyterlab
  - ipykernel
  - nbformat
  - nbclient
  - nbconvert
  - pandas
  - matplotlib
```

- [ ] **Step 4: Run the environment-file test**

Run the command from Step 2.

Expected: PASS.

- [ ] **Step 5: Commit Task 1**

```bash
git add environment.yml tests/test_dataset_materials.py
git commit -m "Define dissertation display environment"
```

### Task 2: Language-specific public notebook generation

**Files:**
- Modify: `scripts/build_dataset_notebooks.py`
- Modify: `tests/test_dataset_materials.py`
- Delete: `notebooks/dataset_overview_public.ipynb`
- Create: `notebooks/dataset_overview_en.ipynb`
- Create: `notebooks/dataset_overview_zh.ipynb`
- Modify: `notebooks/dataset_audit_local.ipynb`

**Interfaces:**
- Produces: `public_notebook(language: str) -> dict`
- Produces: `dataset_overview_en.ipynb` and `dataset_overview_zh.ipynb`
- Consumes: aggregate profile, matching dictionary, and synthetic option CSV

- [ ] **Step 1: Replace old notebook tests with failing language-parity tests**

Tests must assert:

```python
self.assertTrue(ENGLISH_NOTEBOOK.is_file())
self.assertTrue(CHINESE_NOTEBOOK.is_file())
self.assertFalse(OLD_PUBLIC_NOTEBOOK.exists())
self.assertEqual(english_code_sources, chinese_code_sources)
self.assertEqual(english["metadata"]["kernelspec"]["name"], "dissertation-display")
self.assertEqual(chinese["metadata"]["kernelspec"]["name"], "dissertation-display")
```

Before execution, generated code cells must have `execution_count is None` and
empty outputs. Narrative cells must contain `Dataset overview` in English and
`数据集概览` in Chinese.

- [ ] **Step 2: Run notebook tests and confirm failure**

Run:

```bash
python3 -m unittest \
  tests.test_dataset_materials.NotebookSafetyTest -v
```

Expected: failures because the two language-specific notebook files are absent.

- [ ] **Step 3: Refactor the builder**

Define one ordered code-cell list shared by both variants. Use a translation
dictionary for titles, explanations, table headings, and figure labels. Public
code will:

1. use pandas to load aggregate JSON into a coverage table;
2. show per-table missingness summaries without reading `/data/`;
3. load the synthetic option example;
4. draw the synthetic volatility smile with matplotlib;
5. print a visible statement that all contract rows are synthetic.

Set kernel metadata to:

```python
{
    "display_name": "Python (dissertation-display)",
    "language": "python",
    "name": "dissertation-display",
}
```

Generate both new notebooks, regenerate the local template, and delete the old
public notebook with `apply_patch`.

- [ ] **Step 4: Run generation and tests**

Run:

```bash
python3 scripts/build_dataset_notebooks.py
python3 -m unittest \
  tests.test_dataset_materials.NotebookSafetyTest -v
```

Expected: all pre-execution notebook tests pass.

- [ ] **Step 5: Commit Task 2**

```bash
git add scripts/build_dataset_notebooks.py tests/test_dataset_materials.py notebooks
git commit -m "Generate separate bilingual dataset notebooks"
```

### Task 3: Create Conda environment and execute public notebooks

**Files:**
- Modify: `notebooks/dataset_overview_en.ipynb`
- Modify: `notebooks/dataset_overview_zh.ipynb`
- Modify: `tests/test_dataset_materials.py`

**Interfaces:**
- Consumes: `environment.yml`
- Produces: executed public notebooks with safe saved outputs

- [ ] **Step 1: Add failing executed-output tests**

For each public notebook assert:

```python
code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
self.assertTrue(all(cell["execution_count"] is not None for cell in code_cells))
self.assertTrue(any(cell["outputs"] for cell in code_cells))
```

Scan serialized outputs and reject `/Users/`, known real-row fragments,
credentials, `data/option price.csv`, and MIME attachments larger than 2 MiB.

- [ ] **Step 2: Run output tests and confirm failure**

Run:

```bash
python3 -m unittest \
  tests.test_dataset_materials.NotebookOutputTest -v
```

Expected: FAIL because the notebooks are not executed.

- [ ] **Step 3: Create the Conda environment**

Run:

```bash
conda env create -f environment.yml
conda run -n dissertation-display \
  python -m ipykernel install --user \
  --name dissertation-display \
  --display-name "Python (dissertation-display)"
```

If an environment with the exact name already exists, remove only that
environment with `conda env remove -n dissertation-display`, then rerun the
creation command.

- [ ] **Step 4: Verify imports**

Run:

```bash
conda run -n dissertation-display python -c \
  "import pandas, matplotlib, nbformat, nbclient; print('environment ready')"
```

Expected: `environment ready`.

- [ ] **Step 5: Execute both public notebooks in place**

Run:

```bash
conda run -n dissertation-display jupyter execute \
  notebooks/dataset_overview_en.ipynb --inplace
conda run -n dissertation-display jupyter execute \
  notebooks/dataset_overview_zh.ipynb --inplace
```

Expected: both commands exit zero and preserve output cells.

- [ ] **Step 6: Run output tests**

Run the command from Step 2.

Expected: PASS.

- [ ] **Step 7: Commit Task 3**

```bash
git add notebooks/dataset_overview_en.ipynb \
  notebooks/dataset_overview_zh.ipynb tests/test_dataset_materials.py
git commit -m "Save safe outputs in bilingual notebooks"
```

### Task 4: Ignored real-data meeting execution

**Files:**
- Modify: `.gitignore`
- Create locally only: `.local-notebooks/dataset_audit_with_output.ipynb`
- Modify: `tests/test_dataset_materials.py`

**Interfaces:**
- Consumes: output-free `notebooks/dataset_audit_local.ipynb`
- Produces: ignored local executed copy containing five-row previews

- [ ] **Step 1: Add failing local-output boundary tests**

Assert:

```python
self.assertIn("/.local-notebooks/", ignore_text)
self.assertTrue(LOCAL_EXECUTED_NOTEBOOK.is_file())
self.assertTrue(any(cell.get("outputs") for cell in local_code_cells))
self.assertNotIn(
    ".local-notebooks/dataset_audit_with_output.ipynb",
    tracked_paths,
)
```

Continue asserting that every code cell in the tracked local template has an
empty `outputs` list.

- [ ] **Step 2: Run boundary tests and confirm failure**

Run:

```bash
python3 -m unittest \
  tests.test_dataset_materials.LocalMeetingNotebookTest -v
```

Expected: FAIL because the ignored execution has not been created.

- [ ] **Step 3: Add the ignore rule**

Add:

```gitignore
/.local-notebooks/
```

- [ ] **Step 4: Execute to the ignored destination**

Run:

```bash
mkdir -p .local-notebooks
conda run -n dissertation-display jupyter nbconvert \
  --to notebook \
  --execute notebooks/dataset_audit_local.ipynb \
  --output dataset_audit_with_output.ipynb \
  --output-dir .local-notebooks \
  --ExecutePreprocessor.timeout=120
```

Expected: an executed notebook with five-row previews exists only in the
ignored directory.

- [ ] **Step 5: Run boundary tests**

Run the command from Step 2.

Expected: PASS.

- [ ] **Step 6: Commit Task 4**

```bash
git add .gitignore tests/test_dataset_materials.py
git commit -m "Keep executed real-data audit local"
```

### Task 5: Documentation and full safety verification

**Files:**
- Modify: `DATASET.md`
- Modify: `DATASET.zh-CN.md`
- Modify: `tests/test_dataset_materials.py`

**Interfaces:**
- Documents: Conda creation, public notebook execution, and local meeting flow

- [ ] **Step 1: Add failing guide-link tests**

Require both guides to mention `environment.yml`,
`dissertation-display`, both public notebook paths, the local template path,
and `.local-notebooks/dataset_audit_with_output.ipynb`.

- [ ] **Step 2: Run guide tests and confirm failure**

Run:

```bash
python3 -m unittest \
  tests.test_dataset_materials.RepositorySafetyTest -v
```

Expected: guide-link assertions fail.

- [ ] **Step 3: Update both guides**

Document exact commands for:

```bash
conda env create -f environment.yml
conda activate dissertation-display
jupyter lab
```

Explain which notebooks are safe to share and which executed local copy must
never be uploaded.

- [ ] **Step 4: Run complete verification**

Run:

```bash
conda run -n dissertation-display python -m unittest discover -s tests -v
python3 -m json.tool notebooks/dataset_overview_en.ipynb >/dev/null
python3 -m json.tool notebooks/dataset_overview_zh.ipynb >/dev/null
python3 -m json.tool notebooks/dataset_audit_local.ipynb >/dev/null
git diff --check
git ls-files | rg '^(data/|\\.local-notebooks/|.*\\.(pdf|zip)$)' && exit 1 || true
```

Expected: all tests and JSON checks pass; no restricted tracked path.

- [ ] **Step 5: Commit Task 5**

```bash
git add DATASET.md DATASET.zh-CN.md tests/test_dataset_materials.py
git commit -m "Document executed notebook workflow"
```

### Task 6: Directly update main and close PR #2

**Files:**
- No new files

**Interfaces:**
- Publishes: verified commits directly to `origin/main`
- Closes: draft pull request #2 without merging

- [ ] **Step 1: Verify the feature branch**

Run:

```bash
git status --short --branch
conda run -n dissertation-display python -m unittest discover -s tests -v
```

Expected: clean feature branch and all tests pass.

- [ ] **Step 2: Update and merge into local main**

Run:

```bash
git fetch origin main
git switch main
git merge --ff-only origin/main
git merge --no-ff agent/upload-dissertation-materials \
  -m "Merge safe executed dataset notebooks"
```

Expected: merge succeeds without conflicts.

- [ ] **Step 3: Verify the merged main state**

Run:

```bash
conda run -n dissertation-display python -m unittest discover -s tests -v
git diff --check origin/main...HEAD
git ls-files | rg '^(data/|\\.local-notebooks/|.*\\.(pdf|zip)$)' && exit 1 || true
```

Expected: tests pass and no restricted path is tracked.

- [ ] **Step 4: Push main directly**

Run:

```bash
git push origin main
```

Expected: `origin/main` advances to the verified merge commit.

- [ ] **Step 5: Close PR #2 without merging**

Use the GitHub connector to set pull request #2 state to `closed` and replace
its body with a short note that the verified work was published directly to
`main` at the final SHA.

- [ ] **Step 6: Verify remote completion**

Run:

```bash
git fetch origin main
test "$(git rev-parse main)" = "$(git rev-parse origin/main)"
gh pr view 2 --repo LesterLJS/Dissertation \
  --json state,mergedAt,isDraft,url
```

Expected: local and remote `main` SHAs match; PR #2 is closed and unmerged.
