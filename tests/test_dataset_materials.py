import contextlib
import csv
import io
import json
import subprocess
import unittest
from pathlib import Path

from scripts.profile_datasets import EXPECTED_SCHEMAS


ROOT = Path(__file__).resolve().parents[1]
ENGLISH_DICTIONARY = ROOT / "docs" / "data" / "data_dictionary_en.csv"
CHINESE_DICTIONARY = ROOT / "docs" / "data" / "data_dictionary_zh.csv"
SYNTHETIC_OPTIONS = ROOT / "examples" / "synthetic_option_data.csv"
PUBLIC_NOTEBOOK = ROOT / "notebooks" / "dataset_overview_public.ipynb"
LOCAL_NOTEBOOK = ROOT / "notebooks" / "dataset_audit_local.ipynb"
ENGLISH_GUIDE = ROOT / "DATASET.md"
CHINESE_GUIDE = ROOT / "DATASET.zh-CN.md"


def read_dictionary(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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

    def test_both_notebooks_are_valid_v4_and_have_no_saved_outputs(self):
        for path in (PUBLIC_NOTEBOOK, LOCAL_NOTEBOOK):
            with self.subTest(path=path.name):
                notebook = self._load_notebook(path)
                if notebook is None:
                    continue
                self.assertEqual(notebook["nbformat"], 4)
                code_cells = [
                    cell for cell in notebook["cells"] if cell["cell_type"] == "code"
                ]
                self.assertTrue(code_cells)
                self.assertTrue(
                    all(cell.get("outputs", []) == [] for cell in code_cells)
                )
                self.assertTrue(
                    all(cell.get("execution_count") is None for cell in code_cells)
                )
                ids = [cell["id"] for cell in notebook["cells"]]
                self.assertEqual(len(ids), len(set(ids)))

    def test_notebooks_contain_no_absolute_path_or_real_row_fragment(self):
        for path in (PUBLIC_NOTEBOOK, LOCAL_NOTEBOOK):
            with self.subTest(path=path.name):
                notebook = self._load_notebook(path)
                if notebook is None:
                    continue
                encoded = json.dumps(notebook, ensure_ascii=False)
                self.assertNotIn("/Users/", encoded)
                self.assertNotIn("098A3.1A", encoded)
                self.assertNotIn("64881510", encoded)

    def test_public_notebook_uses_only_repository_safe_inputs(self):
        notebook = self._load_notebook(PUBLIC_NOTEBOOK)
        if notebook is None:
            return
        code = "\n".join(
            "".join(cell["source"])
            for cell in notebook["cells"]
            if cell["cell_type"] == "code"
        )

        self.assertNotIn('Path("data")', code)
        self.assertIn("synthetic_option_data.csv", code)
        self.assertIn("dataset_profile.json", code)

    def test_public_notebook_executes_without_optional_packages(self):
        notebook = self._load_notebook(PUBLIC_NOTEBOOK)
        if notebook is None:
            return
        namespace = {}
        with contextlib.redirect_stdout(io.StringIO()):
            for index, cell in enumerate(notebook["cells"], start=1):
                if cell["cell_type"] != "code":
                    continue
                source = "".join(cell["source"])
                exec(
                    compile(source, f"{PUBLIC_NOTEBOOK.name} cell {index}", "exec"),
                    namespace,
                )

    def test_local_notebook_limits_live_preview_to_five_rows(self):
        notebook = self._load_notebook(LOCAL_NOTEBOOK)
        if notebook is None:
            return
        code = "\n".join(
            "".join(cell["source"])
            for cell in notebook["cells"]
            if cell["cell_type"] == "code"
        )

        self.assertIn("itertools.islice(reader, 5)", code)
        self.assertIn('Path("data")', code)


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
            "docs/data/dataset_profile.json",
            "docs/data/data_dictionary_en.csv",
            "docs/data/data_dictionary_zh.csv",
            "examples/synthetic_option_data.csv",
            "notebooks/dataset_overview_public.ipynb",
            "notebooks/dataset_audit_local.ipynb",
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
