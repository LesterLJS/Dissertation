#!/usr/bin/env python3
"""Build deterministic bilingual dataset presentation notebooks."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"
KERNELSPEC = {
    "display_name": "Python (dissertation-display)",
    "language": "python",
    "name": "dissertation-display",
}


def _source(text: str) -> list[str]:
    return text.strip("\n").splitlines(keepends=True)


def markdown_cell(cell_id: str, text: str) -> dict:
    return {
        "cell_type": "markdown",
        "id": cell_id,
        "metadata": {},
        "source": _source(text),
    }


def code_cell(cell_id: str, code: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": cell_id,
        "metadata": {},
        "outputs": [],
        "source": _source(code),
    }


def notebook(cells: list[dict], language: str) -> dict:
    return {
        "cells": cells,
        "metadata": {
            "dataset_language": language,
            "kernelspec": KERNELSPEC,
            "language_info": {"name": "python", "version": "3.12"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


PUBLIC_TEXT = {
    "en": {
        "title": """
# Dataset overview

This executed notebook presents the four dissertation datasets using
repository-safe aggregate statistics and fully synthetic option records.
Licensed OptionMetrics rows are never loaded here.
""",
        "coverage": """
## Coverage and scale

The table below is generated from the aggregate-only profile.
""",
        "quality": """
## Data quality

Missingness is calculated from per-column missing counts in the aggregate
profile. No source row is required.
""",
        "dictionary": """
## Data dictionary

The first entries illustrate how source fields are used in the dissertation.
""",
        "synthetic": """
## Synthetic option example

Every contract below is invented and marked `synthetic_only`.
""",
        "smile": """
## Illustrative volatility smile

This figure is generated only from the synthetic example and is not an
empirical result.
""",
    },
    "zh": {
        "title": """
# 数据集概览

本已执行 Notebook 使用可公开的汇总统计和完全合成的期权记录展示论文的四张
数据表，不会在此加载受许可保护的 OptionMetrics 真实记录。
""",
        "coverage": """
## 覆盖范围与规模

下表仅根据不含单条观测的汇总概况生成。
""",
        "quality": """
## 数据质量

缺失率根据汇总概况中的逐列缺失数量计算，不需要读取任何原始记录。
""",
        "dictionary": """
## 数据字典

以下条目说明主要源字段及其在论文中的用途。
""",
        "synthetic": """
## 合成期权示例

以下所有合约均为人工构造，并标记为 `synthetic_only`。
""",
        "smile": """
## 波动率微笑示意

该图只使用合成示例生成，不属于论文的实证结果。
""",
    },
}


PUBLIC_CODE = [
    (
        "public-setup",
        """
from pathlib import Path
import json
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from IPython.display import display


def find_repository_root():
    for candidate in (Path.cwd(), *Path.cwd().parents):
        if (candidate / "docs" / "data" / "dataset_profile.json").is_file():
            return candidate
    raise FileNotFoundError("Run this notebook from inside the repository.")


ROOT = find_repository_root()
LANGUAGE = os.environ.get("DATASET_NOTEBOOK_LANGUAGE", "en")
if LANGUAGE not in {"en", "zh"}:
    raise ValueError("DATASET_NOTEBOOK_LANGUAGE must be 'en' or 'zh'")

LABELS = {
    "en": {
        "table": "Table",
        "rows": "Rows",
        "period": "Observation period",
        "size": "Size (MiB)",
        "columns": "Columns",
        "missing": "Overall missing cells (%)",
        "date": "Date",
        "symbol": "Symbol",
        "type": "Type",
        "strike": "Strike",
        "iv": "Synthetic IV",
        "chart_title": "Synthetic volatility smile",
        "x_axis": "Strike",
        "y_axis": "Implied volatility",
        "notice": "All displayed option contracts are synthetic.",
    },
    "zh": {
        "table": "数据表",
        "rows": "行数",
        "period": "观测区间",
        "size": "大小（MiB）",
        "columns": "列数",
        "missing": "总体缺失单元格（%）",
        "date": "日期",
        "symbol": "合约代码",
        "type": "类型",
        "strike": "执行价",
        "iv": "合成隐含波动率",
        "chart_title": "合成波动率微笑",
        "x_axis": "执行价",
        "y_axis": "隐含波动率",
        "notice": "所有展示的期权合约均为合成记录。",
    },
}
labels = LABELS[LANGUAGE]
if LANGUAGE == "zh":
    cjk_font_path = Path(sys.prefix) / "fonts" / "NotoSansCJKsc-VF.ttf"
    if not cjk_font_path.is_file():
        raise RuntimeError(
            "Chinese notebook requires the font-ttf-noto-cjk Conda package"
        )
    font_manager.fontManager.addfont(cjk_font_path)
    cjk_font_name = font_manager.FontProperties(fname=cjk_font_path).get_name()
    plt.rcParams["font.family"] = cjk_font_name
    plt.rcParams["axes.unicode_minus"] = False
profile = json.loads(
    (ROOT / "docs" / "data" / "dataset_profile.json").read_text(encoding="utf-8")
)
dictionary_path = ROOT / "docs" / "data" / (
    "data_dictionary_en.csv" if LANGUAGE == "en" else "data_dictionary_zh.csv"
)
synthetic_path = ROOT / "examples" / "synthetic_option_data.csv"
""",
    ),
    (
        "public-coverage",
        """
coverage_rows = []
for name, table in profile["tables"].items():
    coverage_rows.append({
        labels["table"]: name,
        labels["rows"]: table["row_count"],
        labels["period"]: (
            f'{table["date_range"]["min"]} – {table["date_range"]["max"]}'
        ),
        labels["size"]: round(table["file_size_bytes"] / (1024 ** 2), 2),
    })
coverage = pd.DataFrame(coverage_rows)
display(coverage.style.format({labels["rows"]: "{:,.0f}", labels["size"]: "{:,.2f}"}))
""",
    ),
    (
        "public-quality",
        """
quality_rows = []
for name, table in profile["tables"].items():
    total_cells = table["row_count"] * len(table["columns"])
    missing_cells = sum(table["missing_counts"].values())
    quality_rows.append({
        labels["table"]: name,
        labels["columns"]: len(table["columns"]),
        labels["missing"]: 100 * missing_cells / total_cells if total_cells else 0,
    })
quality = pd.DataFrame(quality_rows)
display(quality.style.format({labels["missing"]: "{:.3f}"}))
""",
    ),
    (
        "public-dictionary",
        """
dictionary = pd.read_csv(dictionary_path)
display(dictionary.head(12))
""",
    ),
    (
        "public-synthetic",
        """
synthetic = pd.read_csv(synthetic_path)
if not synthetic["symbol_flag"].eq("synthetic_only").all():
    raise ValueError("Synthetic example contains an unmarked row")
synthetic_view = pd.DataFrame({
    labels["date"]: synthetic["date"],
    labels["symbol"]: synthetic["symbol"],
    labels["type"]: synthetic["cp_flag"],
    labels["strike"]: synthetic["strike_price"] / 1000,
    labels["iv"]: synthetic["impl_volatility"],
})
print(labels["notice"])
display(synthetic_view.style.format({
    labels["strike"]: "{:,.0f}",
    labels["iv"]: "{:.1%}",
}))
""",
    ),
    (
        "public-smile",
        """
smile = synthetic.assign(strike=synthetic["strike_price"] / 1000).sort_values("strike")
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(
    smile["strike"],
    smile["impl_volatility"],
    color="#2563eb",
    marker="o",
    linewidth=2.5,
)
ax.set_title(labels["chart_title"])
ax.set_xlabel(labels["x_axis"])
ax.set_ylabel(labels["y_axis"])
ax.yaxis.set_major_formatter(lambda value, position: f"{value:.0%}")
ax.grid(alpha=0.25)
fig.tight_layout()
plt.show()
""",
    ),
]


def public_notebook(language: str) -> dict:
    if language not in PUBLIC_TEXT:
        raise ValueError("language must be 'en' or 'zh'")
    text = PUBLIC_TEXT[language]
    cells = [
        markdown_cell("public-title", text["title"]),
        code_cell(*PUBLIC_CODE[0]),
        markdown_cell("public-coverage-heading", text["coverage"]),
        code_cell(*PUBLIC_CODE[1]),
        markdown_cell("public-quality-heading", text["quality"]),
        code_cell(*PUBLIC_CODE[2]),
        markdown_cell("public-dictionary-heading", text["dictionary"]),
        code_cell(*PUBLIC_CODE[3]),
        markdown_cell("public-synthetic-heading", text["synthetic"]),
        code_cell(*PUBLIC_CODE[4]),
        markdown_cell("public-smile-heading", text["smile"]),
        code_cell(*PUBLIC_CODE[5]),
    ]
    return notebook(cells, language)


def local_notebook() -> dict:
    cells = [
        markdown_cell(
            "local-intro",
            """
# Local dataset audit / 本地数据检查

This template reads authorised local OptionMetrics files. Keep this tracked
template output-free. Execute it only into the ignored `.local-notebooks/`
directory.

本模板读取获得授权的本地 OptionMetrics 文件。提交的模板必须保持无输出，并且
只能将执行结果保存到被忽略的 `.local-notebooks/` 目录。
""",
        ),
        code_cell(
            "local-setup",
            """
from pathlib import Path
import csv
import itertools
import json
from IPython.display import display


def find_repository_root():
    for candidate in (Path.cwd(), *Path.cwd().parents):
        if (candidate / ".git").exists():
            return candidate
    raise FileNotFoundError("Run this notebook from inside the repository.")


ROOT = find_repository_root()
DATA_DIR = ROOT / Path("data")
PROFILE_PATH = ROOT / "docs" / "data" / "dataset_profile.json"
EXPECTED_FILES = [
    "Index Dividend Yield.csv",
    "Zero Coupon Yield Curve.csv",
    "option price.csv",
    "security price.csv",
]
""",
        ),
        markdown_cell(
            "local-status-heading",
            """
## Local file status / 本地文件状态
""",
        ),
        code_cell(
            "local-status",
            """
file_status = []
for name in EXPECTED_FILES:
    path = DATA_DIR / name
    file_status.append({
        "file": name,
        "present": path.is_file(),
        "size_gib": round(path.stat().st_size / (1024 ** 3), 3) if path.is_file() else None,
    })
display(file_status)
""",
        ),
        markdown_cell(
            "local-preview-heading",
            """
## Five-row licensed preview / 五行真实数据预览

The output below is licensed and must never be committed.

以下输出受数据许可保护，严禁提交。
""",
        ),
        code_cell(
            "local-preview",
            """
preview = {}
for name in EXPECTED_FILES:
    path = DATA_DIR / name
    if not path.is_file():
        preview[name] = {"error": "missing local file"}
        continue
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        preview[name] = list(itertools.islice(reader, 5))
display(preview)
""",
        ),
        markdown_cell(
            "local-profile-heading",
            """
## Aggregate profile / 汇总概况
""",
        ),
        code_cell(
            "local-profile",
            """
profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
summary = {
    name: {
        "rows": table["row_count"],
        "date_range": table["date_range"],
        "columns": len(table["columns"]),
    }
    for name, table in profile["tables"].items()
}
display(summary)
""",
        ),
    ]
    return notebook(cells, "local")


def write_notebook(path: Path, content: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(content, handle, ensure_ascii=False, indent=1)
        handle.write("\n")


def main() -> None:
    write_notebook(
        NOTEBOOK_DIR / "dataset_overview_en.ipynb",
        public_notebook("en"),
    )
    write_notebook(
        NOTEBOOK_DIR / "dataset_overview_zh.ipynb",
        public_notebook("zh"),
    )
    write_notebook(
        NOTEBOOK_DIR / "dataset_audit_local.ipynb",
        local_notebook(),
    )
    print("Built English, Chinese, and local dataset notebooks with cleared outputs.")


if __name__ == "__main__":
    main()
