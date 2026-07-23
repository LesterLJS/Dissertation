#!/usr/bin/env python3
"""Build deterministic repository-safe dataset presentation notebooks."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"


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


def notebook(cells: list[dict]) -> dict:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def public_notebook() -> dict:
    return notebook(
        [
            markdown_cell(
                "public-intro",
                """
# Dissertation dataset overview

This notebook presents repository-safe metadata and a fully synthetic option
sample. It does **not** contain or download licensed OptionMetrics records.

# 论文数据集概览

本 Notebook 仅展示可公开的汇总元数据和完全合成的期权样本，不包含、下载或
复制任何受许可保护的 OptionMetrics 原始记录。
""",
            ),
            code_cell(
                "public-locate",
                """
from pathlib import Path
import csv
import html
import json

try:
    from IPython.display import Markdown, SVG, display
except ModuleNotFoundError:
    class Markdown(str):
        pass

    class SVG(str):
        pass

    def display(value):
        print(str(value))


def find_repository_root():
    for candidate in (Path.cwd(), *Path.cwd().parents):
        if (candidate / "examples" / "synthetic_option_data.csv").is_file():
            return candidate
    raise FileNotFoundError("Run this notebook from inside the repository.")


ROOT = find_repository_root()
PROFILE_PATH = ROOT / "docs" / "data" / "dataset_profile.json"
SYNTHETIC_PATH = ROOT / "examples" / "synthetic_option_data.csv"
""",
            ),
            markdown_cell(
                "public-profile-heading",
                """
## Aggregate profile / 汇总概况

The profile contains file-level counts, date ranges, missing-value counts, and
selected numeric summaries only. It contains no individual observations.

该概况仅包含文件级行数、日期范围、缺失值数量和部分数值摘要，不包含单条观测。
""",
            ),
            code_cell(
                "public-profile",
                """
if PROFILE_PATH.is_file():
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    lines = [
        "| Table | Rows | Period | Size (MiB) |",
        "|---|---:|---|---:|",
    ]
    for name, table in profile["tables"].items():
        period = f'{table["date_range"]["min"]} to {table["date_range"]["max"]}'
        size_mib = table["file_size_bytes"] / (1024 ** 2)
        lines.append(f'| {name} | {table["row_count"]:,} | {period} | {size_mib:,.2f} |')
    display(Markdown("\\n".join(lines)))
else:
    display(Markdown(
        "**Aggregate profile not generated yet.** Run "
        "`python3 scripts/profile_datasets.py --data-dir data "
        "--output docs/data/dataset_profile.json` locally."
    ))
""",
            ),
            markdown_cell(
                "public-synthetic-heading",
                """
## Synthetic option sample / 合成期权样本

Every row below is invented for demonstration. The `synthetic_only` marker and
2030 dates distinguish it from the dissertation extracts.

以下记录均为演示而人工构造；`synthetic_only` 标志和 2030 年日期用于明确区分
论文使用的真实提取数据。
""",
            ),
            code_cell(
                "public-load-synthetic",
                """
with SYNTHETIC_PATH.open("r", encoding="utf-8", newline="") as handle:
    synthetic_rows = list(csv.DictReader(handle))

preview_fields = ["date", "symbol", "cp_flag", "strike_price", "impl_volatility"]
lines = [
    "| Date | Symbol | Type | Strike | Synthetic IV |",
    "|---|---|:---:|---:|---:|",
]
for row in synthetic_rows:
    strike = float(row["strike_price"]) / 1000
    lines.append(
        f'| {row["date"]} | {row["symbol"]} | {row["cp_flag"]} | '
        f'{strike:,.0f} | {float(row["impl_volatility"]):.1%} |'
    )
display(Markdown("\\n".join(lines)))
""",
            ),
            markdown_cell(
                "public-smile-heading",
                """
## Illustrative volatility smile / 波动率微笑示意

The chart is generated from the synthetic rows and is not an empirical result.

该图完全由合成记录生成，不属于论文的实证结果。
""",
            ),
            code_cell(
                "public-smile",
                """
points = sorted(
    (
        float(row["strike_price"]) / 1000,
        float(row["impl_volatility"]),
    )
    for row in synthetic_rows
)
width, height = 700, 360
left, right, top, bottom = 70, 25, 35, 55
x_min, x_max = min(x for x, _ in points), max(x for x, _ in points)
y_min, y_max = 0.17, 0.26


def x_pixel(value):
    return left + (value - x_min) / (x_max - x_min) * (width - left - right)


def y_pixel(value):
    return top + (y_max - value) / (y_max - y_min) * (height - top - bottom)


polyline = " ".join(f"{x_pixel(x):.1f},{y_pixel(y):.1f}" for x, y in points)
circles = "".join(
    f'<circle cx="{x_pixel(x):.1f}" cy="{y_pixel(y):.1f}" r="5" fill="#2563eb"/>'
    for x, y in points
)
x_labels = "".join(
    f'<text x="{x_pixel(x):.1f}" y="{height - 20}" text-anchor="middle" '
    f'font-size="12">{x:,.0f}</text>'
    for x, _ in points
)
y_ticks = [0.18, 0.20, 0.22, 0.24, 0.26]
y_labels = "".join(
    f'<text x="{left - 10}" y="{y_pixel(y) + 4:.1f}" text-anchor="end" '
    f'font-size="12">{y:.0%}</text>'
    for y in y_ticks
)
svg = f'''
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <rect width="100%" height="100%" fill="white"/>
  <line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#475569"/>
  <line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#475569"/>
  <polyline points="{html.escape(polyline)}" fill="none" stroke="#2563eb" stroke-width="3"/>
  {circles}
  {x_labels}
  {y_labels}
  <text x="{width/2}" y="18" text-anchor="middle" font-size="16">Synthetic volatility smile</text>
  <text x="{width/2}" y="{height-2}" text-anchor="middle" font-size="13">Strike</text>
  <text x="16" y="{height/2}" text-anchor="middle" font-size="13"
        transform="rotate(-90 16 {height/2})">Implied volatility</text>
</svg>
'''
display(SVG(svg))
""",
            ),
        ]
    )


def local_notebook() -> dict:
    return notebook(
        [
            markdown_cell(
                "local-intro",
                """
# Local dataset audit for supervision meetings

This notebook reads the ignored local OptionMetrics extracts. Run it only on an
authorised machine. Before committing, keep every code-cell output cleared.

# 导师会议本地数据检查

本 Notebook 读取已被 Git 忽略的本地 OptionMetrics 文件。仅应在获得授权的
设备上运行；提交前必须清除全部代码单元输出。
""",
            ),
            code_cell(
                "local-setup",
                """
from pathlib import Path
import csv
import itertools
import json

try:
    from IPython.display import Markdown, display
except ModuleNotFoundError:
    class Markdown(str):
        pass

    def display(value):
        print(str(value))


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
                "local-file-check-heading",
                """
## Local file check / 本地文件检查

This cell reports file presence and size without reading individual rows.

本单元仅报告文件是否存在及文件大小，不读取单条记录。
""",
            ),
            code_cell(
                "local-file-check",
                """
file_status = []
for name in EXPECTED_FILES:
    path = DATA_DIR / name
    file_status.append({
        "file": name,
        "present": path.is_file(),
        "size_gib": round(path.stat().st_size / (1024 ** 3), 3) if path.is_file() else None,
    })
file_status
""",
            ),
            markdown_cell(
                "local-preview-heading",
                """
## Temporary five-row preview / 临时五行预览

This output may contain licensed observations. Use it during the meeting and
clear the notebook output before saving or committing.

该输出可能包含受许可保护的真实观测。仅在会议中临时展示，保存或提交前必须清除。
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
preview
""",
            ),
            markdown_cell(
                "local-profile-heading",
                """
## Aggregate profile / 汇总概况

Generate or refresh the aggregate profile before the meeting:

```bash
python3 scripts/profile_datasets.py \
  --data-dir data \
  --output docs/data/dataset_profile.json \
  --batch-size 100000
```
""",
            ),
            code_cell(
                "local-profile",
                """
if not PROFILE_PATH.is_file():
    display(Markdown("Run the profiling command above before the meeting."))
else:
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    summary = {
        name: {
            "rows": table["row_count"],
            "date_range": table["date_range"],
            "columns": len(table["columns"]),
        }
        for name, table in profile["tables"].items()
    }
    summary
""",
            ),
            markdown_cell(
                "local-cleanup",
                """
## Before committing / 提交前

Use **Kernel → Restart & Clear Output**, save the notebook, and confirm that
every code cell has an empty `outputs` list.

请选择 **Kernel → Restart & Clear Output**，保存后确认所有代码单元的
`outputs` 均为空。
""",
            ),
        ]
    )


def write_notebook(path: Path, content: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(content, handle, ensure_ascii=False, indent=1)
        handle.write("\n")


def main() -> None:
    write_notebook(
        NOTEBOOK_DIR / "dataset_overview_public.ipynb",
        public_notebook(),
    )
    write_notebook(
        NOTEBOOK_DIR / "dataset_audit_local.ipynb",
        local_notebook(),
    )
    print("Built 2 dataset notebooks with cleared outputs.")


if __name__ == "__main__":
    main()
