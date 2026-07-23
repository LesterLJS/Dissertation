import json
import shutil
import tempfile
import unittest
from pathlib import Path

try:
    from scripts.profile_datasets import (
        EXPECTED_SCHEMAS,
        SchemaError,
        profile_csv,
        profile_directory,
        write_profile,
    )
    IMPORT_ERROR = None
except ModuleNotFoundError as exc:
    EXPECTED_SCHEMAS = {}
    SchemaError = RuntimeError
    profile_csv = None
    profile_directory = None
    write_profile = None
    IMPORT_ERROR = exc


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "data"


class ProfilerAvailabilityTest(unittest.TestCase):
    def test_profiler_module_exists(self):
        self.assertIsNone(IMPORT_ERROR, "scripts.profile_datasets is not implemented")


@unittest.skipIf(IMPORT_ERROR is not None, "profiler is not implemented")
class ProfileCsvTest(unittest.TestCase):
    def test_profiles_rows_dates_missing_values_and_numeric_mean(self):
        path = FIXTURE_DIR / "Index Dividend Yield.csv"

        profile = profile_csv(
            path,
            EXPECTED_SCHEMAS[path.name],
            ("rate",),
            batch_size=2,
        )

        self.assertEqual(profile["row_count"], 3)
        self.assertEqual(
            profile["date_range"],
            {"min": "2020-01-02", "max": "2020-01-06"},
        )
        self.assertEqual(profile["missing_counts"]["rate"], 1)
        self.assertEqual(profile["numeric_summary"]["rate"]["count"], 2)
        self.assertAlmostEqual(profile["numeric_summary"]["rate"]["mean"], 1.25)

    def test_rejects_changed_header(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "Index Dividend Yield.csv"
            path.write_text("date,unexpected\n2020-01-02,value\n", encoding="utf-8")

            with self.assertRaises(SchemaError):
                profile_csv(
                    path,
                    EXPECTED_SCHEMAS[path.name],
                    ("rate",),
                    batch_size=2,
                )

    def test_reports_missing_tables_without_hiding_available_profiles(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            data_dir = Path(temporary_directory)
            for source in FIXTURE_DIR.glob("*.csv"):
                if source.name != "security price.csv":
                    shutil.copyfile(source, data_dir / source.name)

            result = profile_directory(data_dir, batch_size=2)

        self.assertEqual(result["missing_files"], ["security price.csv"])
        self.assertEqual(len(result["tables"]), 3)

    def test_aggregate_json_does_not_copy_source_rows(self):
        result = profile_directory(FIXTURE_DIR, batch_size=2)
        encoded = json.dumps(result)

        self.assertNotIn("SYNTH_ROW_SENTINEL", encoded)
        self.assertNotIn("SYNTHETIC_SPX", encoded)

    def test_write_profile_is_valid_json_and_uses_no_absolute_data_path(self):
        result = profile_directory(FIXTURE_DIR, batch_size=2)
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "profile.json"
            write_profile(result, output)
            decoded = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(decoded, result)
        self.assertNotIn(str(FIXTURE_DIR.resolve()), json.dumps(decoded))


if __name__ == "__main__":
    unittest.main()
