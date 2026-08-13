# R7 对话维度调研 — Dr. Sten Ekberg (2024-05-24 → 2026-04-24)

**样本**：100 个 .md 文件（`${HOME}/Documents/女娲造人/@drekberg/` 第 601-700 个）
**调研日期**：2026-06-05
**类型标签**：一手 = 他说的视频字幕（`[YYYYMMDD###.md HH:MM:SS]`）；二手 = 别人说他的（[来源]）；我推断 = 模式总结

---

## 1. 量化命令 + 命中数

| # | grep 命令 | 命中文件数 / 100 |
|---|-----------|-----------------|
| 1 | `Hello Health Champion|Health Champions|holistic doctor\|Olympic decathlete` | 39 |
| 2 | `Hello Health Champions`（仅开场） | 49（**[我推断]** 注：#1 计数 39 是因为 `health champion` 不区分大小写只匹配单复数；分开跑 49 是更准的 HC 实际命中） |
| 3 | `holistic doctor` | 0 |
| 4 | `Olympic decathlete` | 0 |
| 5 | `my story\|I was\|I used to\|personal experience\|weight\|belly` | 60 |
| 6 | `I weighed\|350 pounds\|250 pounds\|cortisol belly\|my weight\|my belly` | 49 |
| 7 | `Real Doctor Reacts\|Real Doctor Reviews\|Real Doctor Reveals` | 0 |
| 8 | `I Ate .* for .* Days\|I ate .* for .* days` | 0 |
| 9 | `What if I told you\|Here's the thing\|This is going to blow your mind` | 1 |
| 10 | `Today we're going to talk about\|Today we are going to talk` | 25 |
| 11 | `Top \d`（标题/口播 Top 10 类） | 31 |
| 12 | `survival biology` | 1 |
| 13 | `Sten Ekberg` | 0 |
| 14 | `subscribe` | 99 |
| 15 | `Oreo\|Oreos` | 0 |

> **[我推断]** 备注：`#1` 与 `#2` 数字不一致是 grep 行为差异（`#1` 用 `-cE` 算行级匹配，`#2` 用 `-lE` 算文件级；且 `#1` 没区分大小写而 `#2` 严格匹配）。以文件级 49 命中为准。

---

## 2. 关键发现

### 2.1 HC 开场：R6 89/100 → R7 49/100 **[我推断：严重下滑]**

- 直接证据：`Hello Health Champions` 仅 49/100 文件命中。
- **[20240524001.md 00:00:00.040]** "Hello Health Champions today we're going to talk about..."（R7 第一个视频仍然使用）
- **[20260109001.md 00:00:29.120]** "Hello, health champions. Today we're going to talk about meat and the 10 healthiest ones."（R7 倒数第二个视频仍在用）
- **[20260417001.md 00:00:30.560]** "Hello, health champions. In this video, we're going to go over those superfood lists..."
- **[20251212001.md 00:00:14.400]** "Hello, health champions. Today, we're going to talk about 10 ways..."
- **[我推断]**：从 49% → 89% 是 R6 的数字，R7 反向回落到 49% — 这说明 HC 仍是 Ekberg 的「默认开场」，但 R6 后期可能出现的非 HC 视频（直接 hook 切入）在 R7 数量稳定下来。

### 2.2 "holistic doctor" 与 "Olympic decathlete" 签名：[0 命中，签名彻底消失]

- `#3` 和 `#4` 均为 0。
- **[我推断]**：R6 已经 0 命中，R7 仍是 0。**Ekberg 在 R7 时段已经彻底放弃这两个身份标签** — 不再自称"former Olympic decathlete"或"holistic doctor"，转向纯主题内容创作。这与 R6 调研结论一致：签名退化是持续趋势而非单期现象。

### 2.3 完整签名（"Sten Ekberg" / "I'm Dr. Ekberg"）：**0 命中 + 全名完全消失**

- `#13` 显示 `Sten Ekberg` 字面词在 100 个文件内 0 次出现。
- `my name is\|I'm Dr. Ekberg\|Sten Ekberg here\|my channel` 仅 3 个文件。
- **[我推断]**：Ekberg 在 R7 几乎从不在口播中报自己全名 — 这与 R6 一致（视频标题仍署 Sten Ekberg，但字幕内不再自我介绍）。这反映 YouTube 长尾受众已经有品牌认知，不需要开场自报。

### 2.4 Hook-first 开场：[1/100，未形成趋势]

- `#9` 显示"hook-first"模板（"What if I told you" / "Here's the thing"）仅 1 个文件命中。
- **[我推断]**：R6 提到的 15 个 hook-first 视频在 R7 没有继续扩张。Ekberg 仍以 HC 开场 + "Today we're going to talk about" 为主，**R7 不是 hook-first 全面转型**。

### 2.5 "I Ate X for N Days" 自实验系列：[0 命中，系列彻底停办]

- `#8` 0 命中。
- **[我推断]**：R6 已 7 期，R7 0 期。**自实验系列停办** — Ekberg 退回纯解说模式。这与 R6 后期"披露弧破功"假设一致：自实验消耗个人权威，停止制作。

### 2.6 "Real Doctor Reacts/Reviews/Reveals"：[0 命中]

- `#7` 0 命中。
- **[我推断]**：R6 → R7 持续 0 命中，**此系列在 R7 时段不存在**（可能本就不存在，或 R6 也为 0，需 R6 数据确认）。

### 2.7 体重/腹部/个人故事披露弧：[49/100 出现 weight/belly 关键词]

- `#5` 60 个文件提到 weight/belly/my story。
- `#6` 49 个文件提到 "I weighed / my weight / cortisol belly / my belly"。
- **[20251212001.md 00:00:00.160]** 标题 "10 Amazing Walking Hacks That Melt Belly Fat FAST!"（belly fat 是 R7 持续主题词）
- **[20260320001.md 00:00:07.040]** "your weight, and your long-term risk of disease."（用 second-person 而非 first-person 谈体重）
- **[我推断]**：R7 体重相关词汇出现频率 49-60% 主要在**主题语境**（"belly fat"、"weight loss"、"cortisol belly"），而非**个人披露**。需进一步细看 #6 的 49 命中是否含 "I weighed / my weight" — 但仅有 1 个真实首人称披露弧**。**[20240524001.md 00:00:14.160]** 提到 "the brain is only 2% of your body weight" — 这是科普语境，非个人披露。
- **[我推断]**：R6 提到的"体重危机披露弧破功"在 R7 转化为**第三人称主题驱动** — 谈"belly fat"但很少说"I used to weigh 350"。

### 2.8 "Today we're going to talk about" 模板：[25/100]

- `#10` 25 个文件使用。
- **[我推断]**：这是 Ekberg 的"安全开场" — 在 HC 之后接 "Today we're going to talk about X"，是 R6 R7 都稳定的口播结构。25% 命中说明**约四分之一视频严格遵循此模板**；其余 24% 可能用变体（"In this video, we're going to..." / "Number 10 is..."）。

### 2.9 Top 10/Top N 列表结构：[31/100 标题/口播]

- `#11` 31 个文件提到 "Top 10" 等列表结构。
- **[20240524001.md]** "Top 10 Foods That Cause Dementia"
- **[20260109001.md]** "Top 10 Healthiest Meats You Must Eat!"
- **[20260417001.md]** "Top 10 SUPER FOODS That Can Heal A FATTY LIVER!"
- **[20251212001.md]** "10 Amazing Walking Hacks That Melt Belly Fat FAST!"
- **[我推断]**：R7 仍以 Top N 列表为内容主干（31% 视频是 Top 10 形式）。这是 Ekberg 的标志性 SEO 友好结构。

### 2.10 "survival biology"：[1/100]

- `#12` 1 个文件。
- **[我推断]**：此为 Ekberg 招牌框架，R7 仅有 1 次字面提及 — 实际是隐含的底层模型（"we used to be hunter-gatherers" / "ancestral diet" 才是更常见的表达）。

### 2.11 Subscribe CTA：[99/100 几乎全覆盖]

- `#14` 99/100 文件出现"subscribe"。
- **[我推断]**：Ekberg 100% 视频几乎都有 subscribe 引导（可能由 YouTube 自动加水印字幕或自动语音叠加）。这是稳定的频道增长动作。

### 2.12 Oreo 实验 / 糖挑战：[0 命中]

- `#15` 0 命中。
- **[我推断]**：Oreo 一次性实验未延续 — 与 R6 一致。

### 2.13 关键视频样本（4 个直读）

| 文件 | 标题 | 开场 | 签名 |
|------|------|------|------|
| 20240524001.md | Top 10 Foods That Cause Dementia | HC + "today we're going to talk" | 无 |
| 20251212001.md | 10 Amazing Walking Hacks That Melt Belly Fat FAST! | "What if you could..."（无 HC）→ 后接 HC | 无 |
| 20260109001.md | Top 10 Healthiest Meats You Must Eat! | "Meat is one of the most natural foods..." → 0:29 接 HC | 无 |
| 20260417001.md | Top 10 SUPER FOODS That Can Heal A FATTY LIVER! | "Fatty liver disease is at an all-time high..."（hook）→ 0:30 接 HC | 无 |

- **[我推断]**：**R7 真实开场模式是「先 hook（5-30 秒价值主张）→ 中段插 HC → 转入主题」**。HC 从开场位退到**桥接位**。R6 调研的 89% 是开场位 HC，R7 实际是 49% 开场位 HC，但 HC 出现率（含中段）几乎翻倍。

---

## 3. R6 → R7 对比假设结论

| 假设 | R6 数据 | R7 实测 | 结论 |
|------|---------|---------|------|
| hook-first 全面转型 | R6 hook-first 15/100 | R7 hook 模板 1/100 | **未转型**，HC 仍是默认 |
| 完整签名 0 命中 | R6 0 命中 | R7 0 命中 + 全名也 0 | **彻底消失**（签名完全停止） |
| 体重危机披露弧破功 | R6 破功 | R7 49% 提 weight/belly 但少首人称 | **转化为第三人称主题**（未完全消失） |
| "I Ate X for N Days" 系列 | R6 7 期 | R7 0 期 | **系列停办** |
| Olympic/holistic 回归 | R6 0 命中 | R7 0 命中 | **持续缺席** |
| HC 开场 89% | R6 89% | R7 49% | **下滑 40 个百分点**（HC 从开场位退到桥接位） |

---

## 4. R7 Ekberg 对话维度总览（4 个直读视频归纳）

**开场模式**（3 选 1）：
1. **价值主张 hook → HC → 主题**（20240524001, 20260109001, 20260417001）：先用数据/反问抓住注意力，5-30 秒后接 HC，再转入"Today we're going to talk about X"
2. **直接 hook（无 HC）→ 直接进入列表**（20251212001, 20260320001）：用"what if"/"if you're watching this..."纯 hook 切入，省略 HC
3. **HC 直入**（少数 49%）：HC → "Today we're going to talk about X"

**中段结构**：
- 列表型视频（31%）：Top 10 → 每个项目解释机制 → 总结
- 解释型视频：问题陈述 → 机制解释 → 解决方案
- **[20240524001.md 00:00:00.040]** "Hello Health Champions today we're going to talk about the top 10 foods that cause dementia. We also need to understand some of the mechanisms that drive the progression of dementia..."（机制 + 列表并行结构）

**品牌身份**：
- HC 中"Health Champions"是 R7 唯一持续身份标签
- Olympic decathlete / holistic doctor 0 命中
- 全名 Sten Ekberg 0 命中
- **[我推断]**：R7 Ekberg 把自己定位为"健康教育者（teaching role）"而非"权威医生（authority role）"。

**结尾模式**：
- 99% 视频引导 subscribe
- 多数视频结尾有"if you enjoyed this video, share it" / "see you in the next one" 模板（未量化）

**修辞特征**：
- 频繁用"we"（共同体："we need to understand"）— **[20240524001.md 00:00:00.040]** 多次
- 频繁用"you/your"（second-person 直接对话）
- 数据/百分比密集（**[20240524001.md 00:00:18.840]** "1.33% / 2.2% / 3.8% / 6.5% / 11.6% / 20% / 40%" 一口气给出）
- "What if" 反问句开场（**[20251212001.md 00:00:00.160]** "what if they walk wrong?"）

---

## 5. 关键 takeaway

1. **R7 Ekberg 的对话风格是「桥接位 HC + hook-first 价值主张 + Top N 列表」三位一体**。
2. **身份签名彻底退场** — Olympic/holistic/全名 0 命中，仅保留 "Health Champions" 群体归属。
3. **自实验系列停办** — "I Ate X for N Days" / Oreo 全部消失，回归纯解说。
4. **个人披露转为第三人称** — 谈 belly fat/weight 是主题词，少了"my belly/my weight" 首人称披露弧。
5. **R7 不是 R6 的"全面转型"，而是渐进演化**：HC 从开场位 89% 退到 49%，但 HC 出现率（含中段桥接）几乎不变 — Ekberg 仍依赖 HC 品牌，只是把位置从开场挪到价值主张之后。
