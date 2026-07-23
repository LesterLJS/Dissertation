#!/usr/bin/env python3
"""Create aggregate-only profiles of the local dissertation datasets."""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import os
from pathlib import Path
from typing import Iterable


EXPECTED_SCHEMAS: dict[str, tuple[str, ...]] = {
    "Index Dividend Yield.csv": (
        "secid",
        "date",
        "cusip",
        "ticker",
        "sic",
        "index_flag",
        "exchange_d",
        "class",
        "issue_type",
        "industry_group",
        "rate",
    ),
    "Zero Coupon Yield Curve.csv": ("date", "days", "rate"),
    "option price.csv": (
        "secid",
        "date",
        "symbol",
        "symbol_flag",
        "exdate",
        "last_date",
        "cp_flag",
        "strike_price",
        "best_bid",
        "best_offer",
        "volume",
        "open_interest",
        "impl_volatility",
        "delta",
        "gamma",
        "vega",
        "theta",
        "optionid",
        "cfadj",
        "am_settlement",
        "contract_size",
        "ss_flag",
        "forward_price",
        "expiry_indicator",
        "root",
        "suffix",
        "cusip",
        "ticker",
        "sic",
        "index_flag",
        "exchange_d",
        "class",
        "issue_type",
        "industry_group",
        "issuer",
        "div_convention",
        "exercise_style",
        "am_set_flag",
    ),
    "security price.csv": (
        "secid",
        "date",
        "cusip",
        "ticker",
        "sic",
        "index_flag",
        "exchange_d",
        "class",
        "issue_type",
        "industry_group",
        "low",
        "high",
        "open",
        "close",
        "volume",
        "return",
        "cfadj",
        "shrout",
        "cfret",
    ),
}

NUMERIC_COLUMNS: dict[str, tuple[str, ...]] = {
    "Index Dividend Yield.csv": ("rate",),
    "Zero Coupon Yield Curve.csv": ("days", "rate"),
    "option price.csv": (
        "strike_price",
        "best_bid",
        "best_offer",
        "volume",
        "open_interest",
        "impl_volatility",
        "delta",
        "gamma",
        "vega",
        "theta",
        "contract_size",
        "forward_price",
    ),
    "security price.csv": (
        "low",
        "high",
        "open",
        "close",
        "volume",
        "return",
        "shrout",
        "cfret",
    ),
}


class DatasetProfileError(RuntimeError):
    """Base error for safe dataset profiling."""


class SchemaError(DatasetProfileError):
    """Raised when a CSV header differs from the documented extract schema."""


class DataValueError(DatasetProfileError):
    """Raised when a non-empty numeric value cannot be parsed."""


def _batches(reader: Iterable[dict[str, str]], batch_size: int):
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")
    iterator = iter(reader)
    while batch := list(itertools.islice(iterator, batch_size)):
        yield batch


def _empty_numeric_state(columns: tuple[str, ...]) -> dict[str, dict[str, float | int | None]]:
    return {
        column: {"count": 0, "sum": 0.0, "min": None, "max": None}
        for column in columns
    }


def profile_csv(
    path: Path,
    expected_columns: tuple[str, ...],
    numeric_columns: tuple[str, ...],
    batch_size: int,
) -> dict:
    """Profile one CSV without retaining or returning individual observations."""
    path = Path(path)
    missing_counts = {column: 0 for column in expected_columns}
    numeric_state = _empty_numeric_state(numeric_columns)
    row_count = 0
    date_min = None
    date_max = None

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        actual_columns = tuple(reader.fieldnames or ())
        if actual_columns != expected_columns:
            raise SchemaError(
                f"{path.name}: expected {len(expected_columns)} columns, "
                f"found {len(actual_columns)}"
            )

        for batch in _batches(reader, batch_size):
            for row in batch:
                if None in row:
                    raise SchemaError(f"{path.name}: row contains extra fields")
                row_count += 1
                for column in expected_columns:
                    value = (row.get(column) or "").strip()
                    if value == "":
                        missing_counts[column] += 1

                date_value = (row.get("date") or "").strip()
                if date_value:
                    date_min = date_value if date_min is None else min(date_min, date_value)
                    date_max = date_value if date_max is None else max(date_max, date_value)

                for column in numeric_columns:
                    raw_value = (row.get(column) or "").strip()
                    if raw_value == "":
                        continue
                    try:
                        value = float(raw_value)
                    except ValueError as exc:
                        raise DataValueError(
                            f"{path.name}: non-numeric value in {column}"
                        ) from exc
                    state = numeric_state[column]
                    state["count"] += 1
                    state["sum"] += value
                    state["min"] = value if state["min"] is None else min(state["min"], value)
                    state["max"] = value if state["max"] is None else max(state["max"], value)

    numeric_summary = {}
    for column, state in numeric_state.items():
        count = int(state["count"])
        numeric_summary[column] = {
            "count": count,
            "min": state["min"],
            "max": state["max"],
            "mean": (state["sum"] / count) if count else None,
        }

    return {
        "file_name": path.name,
        "file_size_bytes": path.stat().st_size,
        "row_count": row_count,
        "columns": list(expected_columns),
        "date_range": {"min": date_min, "max": date_max},
        "missing_counts": missing_counts,
        "numeric_summary": numeric_summary,
    }


def profile_directory(data_dir: Path, batch_size: int = 100_000) -> dict:
    """Profile every available expected table and report absent files."""
    data_dir = Path(data_dir)
    tables = {}
    missing_files = []
    for file_name, schema in EXPECTED_SCHEMAS.items():
        path = data_dir / file_name
        if not path.is_file():
            missing_files.append(file_name)
            continue
        tables[file_name] = profile_csv(
            path,
            schema,
            NUMERIC_COLUMNS[file_name],
            batch_size,
        )
    return {
        "profile_version": 1,
        "source": "Local licensed OptionMetrics extracts",
        "tables": tables,
        "missing_files": missing_files,
    }


def write_profile(profile: dict, output: Path) -> None:
    """Atomically write a completed aggregate profile."""
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f"{output.name}.tmp")
    try:
        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(profile, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, output)
    finally:
        if temporary.exists():
            temporary.unlink()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create aggregate-only profiles of local OptionMetrics CSV files."
    )
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=100_000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        profile = profile_directory(args.data_dir, args.batch_size)
        write_profile(profile, args.output)
    except (DatasetProfileError, OSError, ValueError, csv.Error) as exc:
        print(f"Profiling failed: {exc}")
        return 1

    print(f"Profiled {len(profile['tables'])} table(s).")
    if profile["missing_files"]:
        print("Missing files: " + ", ".join(profile["missing_files"]))
    print(f"Aggregate profile written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
