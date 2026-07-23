# Chinese Thesis Draft Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce an approximately 25-page plain-Chinese thesis draft grounded in `bs_expert.ipynb` without inventing unobserved evidence.

**Architecture:** Create one standalone Markdown thesis. Separate completed synthetic evidence from proposed real-data validation, and organize the argument as research question, background, methodology, results, interpretation, limitations, and conclusion.

**Tech Stack:** Markdown, equations already defined in the notebook, numerical outputs from `bs_expert.ipynb`.

## Global Constraints

- Write in accessible Chinese.
- Target approximately 10,000–13,000 Chinese characters for about 25 pages after typesetting.
- Preserve all reported numerical results exactly as shown in the notebook.
- Do not present synthetic single-seed evidence as real-market or final evidence.
- Do not fabricate citations; use explicit citation placeholders only where literature must later be added.

---

### Task 1: Build the thesis narrative and front matter

**Files:**
- Create: `thesis_chinese_draft.md`

- [ ] Write the title, abstract, keywords, introduction, motivation, research question, hypotheses, contributions, and chapter roadmap.
- [ ] Check that all claims distinguish motivation from evidence.

### Task 2: Explain theory and methodology

**Files:**
- Modify: `thesis_chinese_draft.md`

- [ ] Explain Black–Scholes, implied volatility, volatility smile, MLP, ensemble learning, gating, fixed experts, and trainable experts in plain Chinese.
- [ ] Document the synthetic dataset, five models, loss, IV inversion, and evaluation metrics exactly from the notebook.

### Task 3: Report and interpret results

**Files:**
- Modify: `thesis_chinese_draft.md`

- [ ] Add the five-model comparison table and expert-count sensitivity results.
- [ ] Explain expert weights, optimization behavior, and what can and cannot be inferred.

### Task 4: Add limitations, future empirical design, and conclusion

**Files:**
- Modify: `thesis_chinese_draft.md`

- [ ] State single-maturity, synthetic-data, single-seed, no-holdout, and no-real-market limitations.
- [ ] Describe multi-seed, strike holdout, multiple smile shapes, maturity extension, and real SPX validation as future work.
- [ ] Write a cautious conclusion that answers the current research question only at the preliminary-evidence level.

### Task 5: Verify the artifact

**Files:**
- Verify: `thesis_chinese_draft.md`

- [ ] Compare every numerical result against notebook outputs.
- [ ] Scan for unsupported claims, empty sections, malformed Markdown, unbalanced equations, and accidental claims of completed real-data tests.
- [ ] Report character count and estimated typeset length.
