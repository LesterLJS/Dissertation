我认真思考了一下，我觉得**我们现在应该停止讨论模型，开始做论文设计（Research Design）**。

因为你已经有：

* ✅ 数据（OptionMetrics 四张表）
* ✅ 基础模型（BS、MLP、MoE）
* ✅ Notebook
* ✅ 一个不错的想法

**现在缺的是一个完整的 Dissertation Story。**

而一篇好的论文不是：

> 我做了一个模型。

而是：

> 我发现了一个问题 → 提出假设 → 设计方法 → 做实验验证。

---

# 我建议的 Dissertation Title（暂定）

> **An Interpretable Mixture-of-Experts Framework for Representing the SPX Implied Volatility Surface**

或者更保守一点：

> **Learning Local Structures in SPX Option Pricing using Financially Interpretable Mixture of Experts**

注意。这里：

**MoE不是重点。**

重点其实是：

> **Representing the IV Surface**

---

# 整体研究问题（Research Question）

> **Can a single global approximation adequately represent the implied-volatility surface, or can an interpretable mixture of local Black–Scholes experts provide a better representation?**

中文：

> **一个统一的全局模型是否足以表示整个 IV Surface？还是多个具有金融意义的 Black–Scholes 专家能够更好地表示它？**

---

# Research Hypothesis

不是：

> MoE一定更好。

而是：

## H0：

> A single global approximation is sufficient.

（一个全局模型已经足够。）

## H1：

> The IV surface exhibits heterogeneous local structures, making specialised experts more suitable.

（IV Surface 存在局部异质结构，因此局部专家更加合适。）

注意：这是：

**Hypothesis**

不是：结论。

---

# 整体论文结构

## Chapter 1 Introduction

回答三个问题：

### 1

为什么：Option Pricing 重要？

例如：

* Market Making
* Risk Management
* Derivatives Pricing

### 2

为什么：IV Surface 重要？

例如：

Market真正讨论的是：IV。

不是：Price。

### 3

Research Gap

已有：

> BS
>
> ↓
>
> Heston
>
> ↓
>
> NN
>
> ↓
>
> Transformer

都：学习：一个：Global Mapping。

但是：有没有可能：整个：IV Surface 其实：存在：多个：局部规律？

这是：你的：Gap。

---

## Chapter 2 Literature Review

建议：不要：按模型分类。

建议：按问题分类。

例如：

### 2.1 Classical Pricing Models

* Black-Scholes
* Local Vol
* Heston

他们：共同特点：Global Model。

### 2.2 Neural Pricing

例如：

* Deep Pricing
* Neural Surrogate
* Calibration

特点：还是：Global NN。

### 2.3 Ensemble Learning

讲：MoE Ensemble Router。

这里：主要：Machine Learning。不是：金融。

### 2.4 Research Gap

这里：引出：你的：Hypothesis。

---

## Chapter 3 Methodology

这里：就是：你：Notebook。但是：要升级。

### Step1

Black-Scholes Baseline

### Step2

Linear IV

### Step3

MLP

### Step4

Static Ensemble

例如：平均：几个：BS。

证明：只是：Average。不够。

### Step5

Fixed BS Experts

就是：你：现在：Notebook。

### Step6

Trainable BS Experts

也是：Notebook。

### Step7

Residual Experts（建议加）

以后：真实数据：建议：不要：预测：Price。而是：预测：Residual。

例如：

\[
Residual=P_{Market}-P_{BS}
\]

这样：解释性：最好。

---

## Chapter 4 Synthetic Experiments

这里：全部：Synthetic。

### Experiment1

Smile Recovery

### Experiment2

不同 Experts。

例如：

```text
M=1

M=2

M=4

M=8
```

看看：什么时候：最好。

### Experiment3

不同 Smile。

例如：不是：一个：Quadratic。

建议：设计：至少：四种。

例如：

* Flat
* Smile
* Skew
* Bump

看看：MoE：是不是：一直：更好。

### Experiment4

可解释性。

画：每个：Expert：Weight。

例如：ATM：喜欢：Expert2。OTM：喜欢：Expert4。

---

## Chapter 5 Real SPX Experiment

这里：才：真正：用：OptionMetrics。

### Data

四张表。Merge。

### Features

例如：

Input：

\[
\log(K/F)
\]

\[
T
\]

\[
r
\]

\[
q
\]

Call/Put。

不要：直接：输入：Market IV。否则：Leakage。

### Labels

Mid Price：

\[
\frac{Bid+Ask}{2}
\]

### Split

不要 Random。

例如：

* Train：2016-2021
* Validation：2022
* Test：2023-2025

---

## Chapter 6 Analysis

这是：很多论文：没有：认真做。

我建议：重点：放这里。

### Analysis1

不同 Maturity。

例如：

```text
0DTE

1-7

8-30

31-90

90+
```

是不是：Experts：不同。

### Analysis2

不同 Moneyness。

例如：ATM。OTM。ITM。

### Analysis3

Volatility。

例如：VIX：高。VIX：低。

### Analysis4

Experts。

例如：看看：Weight。是不是：真的：形成：分工。而不是：Collapse。

---

## Chapter 7 Conclusion

回答：不是：MoE。而是：Research Question。

例如：是不是：真的：需要：多个：Experts。

---

# Timeline（10 周）

| Week | 内容 | Deliverable |
| ---: | --- | --- |
| 1 | 文献综述，明确 Hypothesis | Research proposal |
| 2 | 整理 OptionMetrics 四张表 | Clean dataset |
| 3 | 完善 Synthetic 实验（多种 smile） | Synthetic results |
| 4 | 实现完整 MoE（固定 + trainable） | Baseline comparison |
| 5 | 增加静态 Ensemble、Residual baseline、消融实验 | Ablation study |
| 6 | 构建真实 SPX 数据集，完成特征工程 | Training dataset |
| 7 | 真实 SPX 实验（BS、MLP、MoE） | Main results |
| 8 | 分析不同期限、moneyness、市场状态 | Analysis chapter |
| 9 | 撰写 Methodology 与 Results | Draft dissertation |
| 10 | 修改、补充讨论与结论 | Final dissertation |

---

# 但是，我最后想给你一个建议（也是我认为论文能不能"上一个档次"的关键）

我建议你**不要把最终贡献写成：**

> **We propose a Mixture-of-Experts model.**

因为这句话几乎所有 AI 论文都能说。

我建议你的贡献写成三点：

## Contribution 1（金融）

> 提出一个可检验的研究假设：**IV Surface 是否存在局部异质结构，以至于单一全局表示不足？**

## Contribution 2（方法）

> 提出一种**具有金融可解释性的 Black–Scholes Expert Mixture**，而不是完全黑箱的神经网络。

## Contribution 3（实证）

> 在**Synthetic + Real SPX** 两个层面验证这种表示是否优于单一全局模型，并分析专家是否真正形成了与期限（maturity）、价内外程度（moneyness）和市场状态相关的分工。

---

## 我还有一个建议，我认为会让你的论文更像"研究"

在接下来的一周里，**不要急着写代码**。

先花时间回答下面这五个问题，每个问题最好都能找到文献支持：

1. **为什么金融界长期使用一个全局模型（BS、Heston、Local Vol）来表示整个 IV Surface？**
2. **已有文献是否已经证明不同区域（strike、maturity）存在异质性？**
3. **已有研究为什么仍然使用一个统一模型？它们的理由是什么？**
4. **有没有论文尝试过局部建模、分区建模或专家模型？成功和不足分别是什么？**
5. **如果我的假设成立，它会改变什么？是改善局部定价、提高可解释性，还是提供一种新的 IV Surface 表示方式？**

**这五个问题的答案，将决定你的论文是"应用一个 AI 模型"，还是"提出一个新的金融建模观点"。我认为，后者会更有研究价值。**



我结合我们过去几天所有讨论（**Deep Learning、SPX、OptionMetrics、0DTE、MoE、工业界 pain point**），我觉得你的研究问题已经逐渐从一个"模型问题"演化成了一个"系统设计问题"。

我按照**研究成熟度**给你整理一下。

---

# Version 1：最开始（已经不建议）

最开始你的想法其实是：

> **Can deep learning outperform the Black–Scholes model in option pricing?**

中文：

> 深度学习是否能够比 Black-Scholes 定价更准确？

这个问题的问题是：

* 太多人做过
* 学术贡献弱
* 工业价值不明显

如果论文只是：

> BS vs MLP

导师大概率会问：

> **"为什么？"**

---

# Version 2：现在比较成熟

后来我们讨论到：

SPX

↓

不同期限

↓

不同市场机制

↓

不同模型。

于是问题变成：

> **Does the pricing performance of deep learning models vary across different maturity regions, especially for zero-days-to-expiration (0DTE) SPX options?**

中文：

> 深度学习模型在不同剩余期限（尤其是0DTE）上的定价能力是否存在显著差异？

这个已经开始有研究价值。

因为：

不是：

> NN > BS

而是：

> 哪里好？

为什么好？

---

# Version 3：工业界版本（我最喜欢）

后来你提出：

> 我希望找到工业界真正的 pain point。

于是研究问题其实发生了变化。

工业界真正的问题不是：

> 准确率提高1%。

而是：

> **市场是不是应该用同一个模型定所有期权？**

于是：

你的问题可以变成：

> **Should different SPX option maturity regions be priced by different specialised models rather than a single universal pricing model?**

中文：

> 不同期限的SPX期权是否应该采用不同的专门模型，而不是统一模型进行定价？

注意。

这里：

已经不是：

Deep Learning。

而是：

Pricing Architecture。

---

# Version 4：MoE版本（目前我最推荐）

然后我们聊到了：

Mixture of Experts。

于是：

真正的问题变成：

> **Can a maturity-aware Mixture-of-Experts pricing framework improve both pricing accuracy and robustness compared with a single pricing model?**

中文：

> 一个考虑期限特征的Mixture-of-Experts框架，是否能够比单一模型在定价准确率和鲁棒性方面表现更好？

这里：

Expert：

不是：

多个一样的NN。

而是：

例如：

```text
Black-Scholes Expert

↓

Short Maturity Expert

↓

Medium Maturity Expert

↓

Long Maturity Expert

↓

High Volatility Expert
```

然后：

Gate：

自动：

选择。

---

# 如果再结合工业界

我觉得：

真正的研究问题应该写成：

> **Can an adaptive pricing engine automatically select the most appropriate pricing expert for different market regimes and maturity regions?**

中文：

> 是否能够设计一个自适应定价引擎，根据市场状态和期权特征自动选择最适合的定价专家？

这里：

工业价值：

一下就出来了。

因为：

实际上：

很多：

Market Maker。

每天：

都在：

Routing。

只是：

他们：

Routing：

的是：

Order。

你：

Routing：

的是：

Pricing Model。

---

# 但是，我觉得还有一步可以继续深入

这是我今天想到的。

也是我觉得你真正应该研究的。

我们一直假设：

> 不同期限。

应该：

不同Expert。

但是：

为什么？

其实：

可能：

真正决定模型表现的：

不是：

期限。

而是：

Market Regime。

例如：

输入：

```text
T=1

IV=80%

Spread=10

Volume=100000
```

应该：

走：

Expert A。

而：

```text
T=300

IV=15%

Spread=0.1
```

应该：

Expert B。

所以：

Gate：

其实：

不是：

DTE。

而是：

整个：

Market State。

这就非常像：

LLM：

Mixture of Experts。

---

# 如果让我给你的论文一句话

我会写：

> **This dissertation investigates whether a maturity-aware and market-adaptive Mixture-of-Experts pricing framework can better address the heterogeneous pricing characteristics of SPX options than a single universal pricing model.**

中文就是：

> **本论文研究一个考虑期限特征和市场状态的 Mixture-of-Experts 定价框架，是否能够比统一定价模型更好地刻画 SPX 不同期权的异质性定价特征。**

---

# 我认为真正值得继续思考的问题（也是你接下来最应该投入精力的）

到目前为止，我们已经确定了：

* **数据**：OptionMetrics（SPX）
* **基准模型**：Black–Scholes
* **候选模型**：神经网络 / Mixture of Experts

但还有一个更关键的问题没有回答：

> **工业界为什么需要这个框架？**

这里我建议不要停留在“提高准确率”。

你可以进一步寻找一个具体的业务痛点，例如：

* 为什么统一模型在某些市场状态下表现不稳定？
* 为什么交易系统需要自动选择不同定价模型？
* 为什么不同期限或不同流动性的期权需要不同的建模方式？

如果你能把这个工业界的具体需求讲清楚，你的论文就会从“提出一个新模型”变成“解决一个真实问题”，这也是学术和工业界都更容易认可的方向。
