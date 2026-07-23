import csv
import unittest
from pathlib import Path

from scripts.profile_datasets import EXPECTED_SCHEMAS


ROOT = Path(__file__).resolve().parents[1]
ENGLISH_DICTIONARY = ROOT / "docs" / "data" / "data_dictionary_en.csv"
CHINESE_DICTIONARY = ROOT / "docs" / "data" / "data_dictionary_zh.csv"
SYNTHETIC_OPTIONS = ROOT / "examples" / "synthetic_option_data.csv"


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


if __name__ == "__main__":
    unittest.main()
