import csv
import json
import subprocess
import unittest
from pathlib import Path

from scripts.profile_datasets import EXPECTED_SCHEMAS


ROOT = Path(__file__).resolve().parents[1]
ENGLISH_DICTIONARY = ROOT / "docs" / "data" / "data_dictionary_en.csv"
CHINESE_DICTIONARY = ROOT / "docs" / "data" / "data_dictionary_zh.csv"
SYNTHETIC_OPTIONS = ROOT / "examples" / "synthetic_option_data.csv"
OLD_PUBLIC_NOTEBOOK = ROOT / "notebooks" / "dataset_overview_public.ipynb"
ENGLISH_NOTEBOOK = ROOT / "notebooks" / "dataset_overview_en.ipynb"
CHINESE_NOTEBOOK = ROOT / "notebooks" / "dataset_overview_zh.ipynb"
LOCAL_NOTEBOOK = ROOT / "notebooks" / "dataset_audit_local.ipynb"
LOCAL_EXECUTED_NOTEBOOK = (
    ROOT / ".local-notebooks" / "dataset_audit_with_output.ipynb"
)
ENGLISH_GUIDE = ROOT / "DATASET.md"
CHINESE_GUIDE = ROOT / "DATASET.zh-CN.md"
CONDA_ENVIRONMENT = ROOT / "environment.yml"


def read_dictionary(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class CondaEnvironmentTest(unittest.TestCase):
    def test_display_environment_declares_required_packages(self):
        self.assertTrue(CONDA_ENVIRONMENT.is_file())
        if not CONDA_ENVIRONMENT.is_file():
            return
        content = CONDA_ENVIRONMENT.read_text(encoding="utf-8")

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
            "font-ttf-noto-cjk",
        ):
            self.assertIn(f"  - {dependency}", content)


class DictionaryIntegrityTest(unittest.TestCase):
    def test_bilingual_dictionaries_cover_every_source_field(self):
        self.assertTrue(ENGLISH_DICTIONARY.is_file())
        self.assertTrue(CHINESE_DICTIONARY.is_file())
        english = read_dictionary(ENGLISH_DICTIONARY)
        chinese = read_dictionary(CHINESE_DICTIONARY)
        english_pairs = [(row["table"], row["field"]) for row in english]
        chinese_pairs = [(row["table"], row["field"]) for row in chinese]
        expected_pairs = [
            (table, field)
            for table, fields in EXPECTED_SCHEMAS.items()
            for field in fields
        ]

        self.assertEqual(english_pairs, chinese_pairs)
        self.assertEqual(english_pairs, expected_pairs)
        self.assertTrue(all(row["description"].strip() for row in english + chinese))
        self.assertTrue(all(row["type_or_unit"].strip() for row in english + chinese))
        self.assertTrue(all(row["dissertation_use"].strip() for row in english + chinese))


class SyntheticDataSafetyTest(unittest.TestCase):
    def test_synthetic_options_match_schema_and_are_clearly_marked(self):
        self.assertTrue(SYNTHETIC_OPTIONS.is_file())
        with SYNTHETIC_OPTIONS.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)

        self.assertEqual(
            reader.fieldnames,
            list(EXPECTED_SCHEMAS["option price.csv"]),
        )
        self.assertGreaterEqual(len(rows), 6)
        self.assertTrue(
            all(row["symbol_flag"] == "synthetic_only" for row in rows)
        )
        self.assertTrue(all(row["ticker"] == "SYNTHETIC_SPX" for row in rows))

    def test_synthetic_file_contains_no_known_real_row_fragments(self):
        self.assertTrue(SYNTHETIC_OPTIONS.is_file())
        if not SYNTHETIC_OPTIONS.is_file():
            return
        content = SYNTHETIC_OPTIONS.read_text(encoding="utf-8")

        self.assertNotIn("098A3.1A", content)
        self.assertNotIn("64881510", content)
        self.assertNotIn("24.75,25.75,150,5633", content)


class NotebookSafetyTest(unittest.TestCase):
    def _load_notebook(self, path):
        self.assertTrue(path.is_file())
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _code_sources(notebook):
        return [
            "".join(cell["source"])
            for cell in notebook["cells"]
            if cell["cell_type"] == "code"
        ]

    def test_language_notebooks_exist_and_old_public_notebook_is_removed(self):
        self.assertTrue(ENGLISH_NOTEBOOK.is_file())
        self.assertTrue(CHINESE_NOTEBOOK.is_file())
        self.assertFalse(OLD_PUBLIC_NOTEBOOK.exists())

    def test_notebooks_are_valid_v4_with_display_kernel(self):
        for path in (ENGLISH_NOTEBOOK, CHINESE_NOTEBOOK, LOCAL_NOTEBOOK):
            with self.subTest(path=path.name):
                notebook = self._load_notebook(path)
                if notebook is None:
                    continue
                self.assertEqual(notebook["nbformat"], 4)
                ids = [cell["id"] for cell in notebook["cells"]]
                self.assertEqual(len(ids), len(set(ids)))
                self.assertEqual(
                    notebook["metadata"]["kernelspec"]["name"],
                    "dissertation-display",
                )

    def test_language_notebooks_share_identical_code(self):
        english = self._load_notebook(ENGLISH_NOTEBOOK)
        chinese = self._load_notebook(CHINESE_NOTEBOOK)
        if english is None or chinese is None:
            return

        self.assertEqual(self._code_sources(english), self._code_sources(chinese))
        english_markdown = "\n".join(
            "".join(cell["source"])
            for cell in english["cells"]
            if cell["cell_type"] == "markdown"
        )
        chinese_markdown = "\n".join(
            "".join(cell["source"])
            for cell in chinese["cells"]
            if cell["cell_type"] == "markdown"
        )
        self.assertIn("Dataset overview", english_markdown)
        self.assertIn("数据集概览", chinese_markdown)

    def test_builder_creates_output_free_notebook_templates(self):
        from scripts.build_dataset_notebooks import local_notebook, public_notebook

        try:
            generated = [
                public_notebook("en"),
                public_notebook("zh"),
                local_notebook(),
            ]
        except TypeError as exc:
            self.fail(f"language-aware notebook builder is not implemented: {exc}")

        for notebook in generated:
            code_cells = [
                cell for cell in notebook["cells"] if cell["cell_type"] == "code"
            ]
            self.assertTrue(code_cells)
            self.assertTrue(all(cell.get("outputs", []) == [] for cell in code_cells))
            self.assertTrue(
                all(cell.get("execution_count") is None for cell in code_cells)
            )

    def test_notebooks_contain_no_absolute_path_or_real_row_fragment(self):
        for path in (ENGLISH_NOTEBOOK, CHINESE_NOTEBOOK, LOCAL_NOTEBOOK):
            with self.subTest(path=path.name):
                notebook = self._load_notebook(path)
                if notebook is None:
                    continue
                encoded = json.dumps(notebook, ensure_ascii=False)
                self.assertNotIn("/Users/", encoded)
                self.assertNotIn("098A3.1A", encoded)
                self.assertNotIn("64881510", encoded)

    def test_public_notebooks_use_only_repository_safe_inputs(self):
        for path in (ENGLISH_NOTEBOOK, CHINESE_NOTEBOOK):
            with self.subTest(path=path.name):
                notebook = self._load_notebook(path)
                if notebook is None:
                    continue
                code = "\n".join(self._code_sources(notebook))

                self.assertNotIn('Path("data")', code)
                self.assertIn("synthetic_option_data.csv", code)
                self.assertIn("dataset_profile.json", code)

    def test_local_notebook_is_output_free_and_limits_preview_to_five_rows(self):
        notebook = self._load_notebook(LOCAL_NOTEBOOK)
        if notebook is None:
            return
        code_cells = [
            cell for cell in notebook["cells"] if cell["cell_type"] == "code"
        ]
        code = "\n".join(self._code_sources(notebook))

        self.assertTrue(all(cell.get("outputs", []) == [] for cell in code_cells))
        self.assertIn("itertools.islice(reader, 5)", code)
        self.assertIn('Path("data")', code)


class NotebookOutputTest(unittest.TestCase):
    def _load(self, path):
        return json.loads(path.read_text(encoding="utf-8"))

    def test_public_notebooks_have_saved_execution_outputs(self):
        for path in (ENGLISH_NOTEBOOK, CHINESE_NOTEBOOK):
            with self.subTest(path=path.name):
                notebook = self._load(path)
                code_cells = [
                    cell for cell in notebook["cells"] if cell["cell_type"] == "code"
                ]

                self.assertTrue(code_cells)
                self.assertTrue(
                    all(cell.get("execution_count") is not None for cell in code_cells)
                )
                self.assertTrue(any(cell.get("outputs") for cell in code_cells))

    def test_public_outputs_contain_no_restricted_content(self):
        forbidden = (
            "/Users/",
            "098A3.1A",
            "64881510",
            "24.75,25.75,150,5633",
            "data/option price.csv",
            "api_key",
            "client_secret",
            "password",
            "bearer ",
        )
        for path in (ENGLISH_NOTEBOOK, CHINESE_NOTEBOOK):
            with self.subTest(path=path.name):
                notebook = self._load(path)
                outputs = [
                    output
                    for cell in notebook["cells"]
                    if cell["cell_type"] == "code"
                    for output in cell.get("outputs", [])
                ]
                encoded = json.dumps(outputs, ensure_ascii=False).lower()

                for fragment in forbidden:
                    self.assertNotIn(fragment.lower(), encoded)
                self.assertLess(len(encoded.encode("utf-8")), 2 * 1024 * 1024)

    def test_saved_output_language_matches_notebook(self):
        english_outputs = json.dumps(
            [
                cell.get("outputs", [])
                for cell in self._load(ENGLISH_NOTEBOOK)["cells"]
            ],
            ensure_ascii=False,
        )
        chinese_outputs = json.dumps(
            [
                cell.get("outputs", [])
                for cell in self._load(CHINESE_NOTEBOOK)["cells"]
            ],
            ensure_ascii=False,
        )

        self.assertIn("All displayed option contracts are synthetic.", english_outputs)
        self.assertIn("所有展示的期权合约均为合成记录。", chinese_outputs)


class LocalMeetingNotebookTest(unittest.TestCase):
    def test_local_execution_is_ignored_and_untracked(self):
        ignore_text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        tracked = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()

        self.assertIn("/.local-notebooks/", ignore_text)
        self.assertNotIn(
            ".local-notebooks/dataset_audit_with_output.ipynb",
            tracked,
        )

    def test_local_executed_copy_exists_and_contains_outputs(self):
        self.assertTrue(LOCAL_EXECUTED_NOTEBOOK.is_file())
        if not LOCAL_EXECUTED_NOTEBOOK.is_file():
            return
        notebook = json.loads(
            LOCAL_EXECUTED_NOTEBOOK.read_text(encoding="utf-8")
        )
        code_cells = [
            cell for cell in notebook["cells"] if cell["cell_type"] == "code"
        ]

        self.assertTrue(code_cells)
        self.assertTrue(any(cell.get("outputs") for cell in code_cells))


class RepositorySafetyTest(unittest.TestCase):
    def test_restricted_source_files_are_not_tracked(self):
        tracked = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        restricted = [
            path
            for path in tracked
            if path.startswith("data/")
            or path.lower().endswith(".pdf")
            or path.lower().endswith(".zip")
        ]

        self.assertEqual(restricted, [])

    def test_ignore_rules_protect_local_and_temporary_materials(self):
        ignore_text = (ROOT / ".gitignore").read_text(encoding="utf-8")

        self.assertIn("/data/", ignore_text)
        self.assertIn("*.pdf", ignore_text)
        self.assertIn("*.zip", ignore_text)
        self.assertIn(".ipynb_checkpoints/", ignore_text)
        self.assertIn("docs/data/*.tmp", ignore_text)

    def test_bilingual_guides_link_every_presentation_artifact(self):
        required_paths = [
            "environment.yml",
            "dissertation-display",
            "docs/data/dataset_profile.json",
            "docs/data/data_dictionary_en.csv",
            "docs/data/data_dictionary_zh.csv",
            "examples/synthetic_option_data.csv",
            "notebooks/dataset_overview_en.ipynb",
            "notebooks/dataset_overview_zh.ipynb",
            "notebooks/dataset_audit_local.ipynb",
            ".local-notebooks/dataset_audit_with_output.ipynb",
        ]
        for guide in (ENGLISH_GUIDE, CHINESE_GUIDE):
            with self.subTest(guide=guide.name):
                self.assertTrue(guide.is_file())
                if not guide.is_file():
                    continue
                content = guide.read_text(encoding="utf-8")
                for path in required_paths:
                    self.assertIn(path, content)


if __name__ == "__main__":
    unittest.main()
