# 论文数据集说明

[English version](DATASET.md)

## 目的

本仓库说明用于研究 SPX 期权定价和隐含波动率的数据，并将公开研究材料与受许可
保护的原始数据严格分开：

- GitHub 仅包含代码、表结构、汇总统计和人工合成示例。
- 已被忽略的本地 `data/` 目录保存获得授权的 OptionMetrics 提取文件。
- 本仓库不会发布任何从原始提取文件复制的真实记录。

## 数据来源与访问

四张表通过机构订阅从 OptionMetrics 获取，应作为受许可保护的研究数据处理。
GitHub 私有仓库、访问权限或 Git LFS 均不等同于获得再分发许可。具备相应授权的
研究人员应通过自己的机构账户独立提取相同数据，而不是从本仓库索取副本。

不得提交 WRDS 登录信息、账户资料、带签名的下载链接，或显示真实记录的 Notebook
输出。

## 数据集清单

以下汇总概况于 2026 年 7 月 23 日根据本地提取文件生成。

| 本地数据表 | 用途 | 行数 | 观测日期 |
|---|---|---:|---|
| `Index Dividend Yield.csv` | SPX 每日股息率输入 | 7,463 | 1996-01-04 至 2025-08-29 |
| `Zero Coupon Yield Curve.csv` | 不同期限的无风险利率 | 304,301 | 1996-01-02 至 2025-08-29 |
| `option price.csv` | 期权报价及 OptionMetrics 分析变量 | 48,335,273 | 1996-01-04 至 2025-08-29 |
| `security price.csv` | SPX 每日价格和收益率 | 7,465 | 1996-01-02 至 2025-08-29 |

机器可读的汇总文件为
[`docs/data/dataset_profile.json`](docs/data/dataset_profile.json)。它只包含
文件大小、行数、表结构、日期范围、缺失值数量和部分数值摘要，不包含单条观测。

## 公开展示材料

- 英文数据字典：
  [`docs/data/data_dictionary_en.csv`](docs/data/data_dictionary_en.csv)
- 中文数据字典：
  [`docs/data/data_dictionary_zh.csv`](docs/data/data_dictionary_zh.csv)
- 人工构造的 38 列示例：
  [`examples/synthetic_option_data.csv`](examples/synthetic_option_data.csv)
- 公开数据概览：
  [`notebooks/dataset_overview_public.ipynb`](notebooks/dataset_overview_public.ipynb)
- 会议本地检查：
  [`notebooks/dataset_audit_local.ipynb`](notebooks/dataset_audit_local.ipynb)

合成文件使用虚构标识符、2030 年日期、`SYNTHETIC_SPX` 代码以及
`symbol_flag=synthetic_only` 标志。它只用于说明字段结构和波动率微笑，不属于
实证样本。

## 重新生成汇总概况

将获得授权的文件放在：

```text
data/
├── Index Dividend Yield.csv
├── Zero Coupon Yield Curve.csv
├── option price.csv
└── security price.csv
```

运行：

```bash
python3 scripts/profile_datasets.py \
  --data-dir data \
  --output docs/data/dataset_profile.json \
  --batch-size 100000
```

分析器只使用 Python 标准库，验证完整表头后以有界批次顺序扫描文件。它不会保存
单条观测，也不会输出真实记录。在当前开发设备上，完整扫描四张表约需四分半钟。

如修改 Notebook 生成器，可运行：

```bash
python3 scripts/build_dataset_notebooks.py
```

## 五分钟导师展示流程

1. **数据来源——30 秒。** 说明论文使用通过机构授权取得的 OptionMetrics SPX
   数据。
2. **覆盖范围——45 秒。** 展示四张表及 1996–2025 年的观测区间。
3. **字段结构——60 秒。** 打开双语数据字典，说明如何通过 `secid` 和 `date`
   连接各表。
4. **数据质量——60 秒。** 使用汇总概况说明样本量、缺失情况和主要变量范围。
5. **安全示例——45 秒。** 运行
   `notebooks/dataset_overview_public.ipynb`，展示合成字段和示意波动率微笑。
6. **真实数据检查——60 秒。** 仅在获授权的本地设备上运行
   `notebooks/dataset_audit_local.ipynb`，临时展示每张表前五行。

会议结束后，保存前必须清除本地检查 Notebook 的全部输出，绝不能提交真实记录
预览。

## 建议引用方式

请根据论文要求和学校订阅协议调整以下格式：

> OptionMetrics. *IvyDB US: Historical option prices and implied volatility
> data*. Accessed through Wharton Research Data Services under an institutional
> subscription.

引用用于说明数据来源，但不能替代适用的数据许可或学校要求的正式致谢。

## 验证

运行：

```bash
python3 -m unittest discover -s tests -v
python3 -m json.tool notebooks/dataset_overview_public.ipynb >/dev/null
python3 -m json.tool notebooks/dataset_audit_local.ipynb >/dev/null
```

测试会检查字段覆盖、合成数据标志、Notebook 输出清理、相对路径，以及原始数据、
PDF 和 ZIP 文件是否保持未跟踪状态。
