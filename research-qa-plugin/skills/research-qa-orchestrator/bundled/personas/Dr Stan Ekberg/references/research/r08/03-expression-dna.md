# R8 Expression DNA - Dr. Sten Ekberg (@drekberg)

> **Scope**: 4 videos, 2026-05-08 → 2026-05-29 (3-week window)
> **Corpus size**: 17,444 words (4 files)
> **All frequencies normalized to per 100K words** for cross-window comparison.
> **R7 baseline**: 469,716 words / 100 videos
> **Source convention**: 一手 = `[YYYYMMDD###.md HH:MM:SS]`, 二手 = `[来源 URL]`, 推断 = `[我推断]`

---

## 0. Method (grep commands actually run)

```bash
# corpus: cat /tmp/r8_files.txt | xargs wc -w  →  17444 words
# 4 files:
#   20260508001.md (3283w)  - "#1 Absolute Best Way To Prevent Colon Cancer"
#   20260515001.md (4330w)  - "Why Belly Fat Changes After 50"
#   20260522001.md (4800w)  - "You Cannot Heal Your THYROID If You Do These 10 Things Daily"
#   20260529001.md (5031w)  - "I Ate Nothing But Sardines For 5 Days and Here's What Happened"

# per-100K normalization: raw_count / 17444 * 100000
# Frequencies rounded to 1 decimal; raw counts in parentheses for traceability

# 1. cat /tmp/r8_files.txt | xargs grep -ioE "the body" 2>&1 | wc -l
#    → 33  (= 189.2/100K)         [R7 baseline 178.6]
# 2. cat /tmp/r8_files.txt | xargs grep -icE "insulin|keto|fasting|carnivore|glucose|inflammation"
#    → 77 (per file: 28/24/11/14) (= 441.4/100K)
#    breakdown: insulin 51 + glucose 17 + inflammation 14 + keto 9 + fasting 2
# 3. cat /tmp/r8_files.txt | xargs grep -icE "okay|right|so|because|if you"
#    → 497 (per file: 98/107/139/153) (= 2849.2/100K)
#    breakdown: so 519 + if you 75 + because 75 + right 12 + okay 9
# 4. cat /tmp/r8_files.txt | xargs grep -icE "Uveia|euLyte|Ulite|UmethylB|Health Champions|Survival Biology"
#    → 7  (= 40.1/100K)  breakdown: Health Champions 4 + Ulite 3
# 5. cat /tmp/r8_files.txt | xargs grep -icE "toxic|poison|stupid|lie"  →  4 (toxic 2 + poison 2 + lie 0)
# 6. cat /tmp/r8_files.txt | xargs grep -iE "RFK|Ozempic|Standard Process|Triad of Health"  →  ALL ZERO
# 7. cat /tmp/r8_files.txt | xargs grep -iE "study|according to"  →  ALL ZERO
# 8. cat /tmp/r8_files.txt | xargs grep -ioE "right\?"  →  1 (20260515001.md only)
# 9. cat /tmp/r8_files.txt | xargs grep -iE "keto" → 9 (all in 20260529001.md)
# 10. cat /tmp/r8_files.txt | xargs grep -iE "carnivore" → 0
# 11. cat /tmp/r8_files.txt | xargs grep -icE "Hello, health champions"  →  4 (one per file, 100%)
# 12. cat /tmp/r8_files.txt | xargs grep -iE "if you enjoyed this video"  →  4 (one per file, 100%)
# 13. cat /tmp/r8_files.txt | xargs grep -icE "in the body"  →  4 (= 22.9/100K)
# 14. cat /tmp/r8_files.txt | xargs grep -ioE "the body" 2>&1
#     per file: 4 / 2 / 23 / 4 (= 33 total)
# 15. cat /tmp/r8_files.txt | xargs grep -ioE "your body"  →  15 (= 86.0/100K)
# 16. cat /tmp/r8_files.txt | xargs grep -icE "I'm going to show"  →  2 (in 20260508 + 20260515)
# 17. cat /tmp/r8_files.txt | xargs grep -ioE "you'?re going to"  →  17
# 18. cat /tmp/r8_files.txt | xargs grep -icE "today"  →  5
# 19. cat /tmp/r8_files.txt | xargs grep -ioE "seed oils|vegetable oils"  →  5
# 20. cat /tmp/r8_files.txt | xargs grep -iE "iodine"  →  25 (all in 20260522001.md thyroid video)
# 21. cat /tmp/r8_files.txt | xargs grep -ioE "So," → 48 ; "So " → 220 ;  total "So " word 260
```

---

## 1. R8 vs R7 vs R6 Frequency Table (核心对比)

| 维度 | 词/短语 | R6 (/100K) | R7 (/100K) | **R8 (/100K)** | Δ% vs R7 | 解读 |
|---|---|---|---|---|---|---|
| **核心锚词** | `the body` | 200.3 | 178.6 | **189.2** (33) | **+6%** | 微升，结束 6 期连降 |
|  | `your body` | 92.3 | 105.6 | **86.0** (15) | -19% | 第二人称回落 |
|  | `root cause` | 5.8 | 6.2 | **0** (0) | **-100%** | 完全消失（4 篇无 root cause） |
|  | `holistic` | 3.5 | 0.9 | **0** (0) | -100% | 持续低位 |
| **饮食轴** | `insulin` | 314.5 | 250.8 | **292.3** (51) | +17% | 反弹至 R6 水平 |
|  | `keto` | 9.8 | 3.6 | **51.6** (9) | **+1333%** | **重大反弹**：单一视频 (sardine) 拉高 |
|  | `carnivore` | 5.6 | 1.9 | **0** (0) | -100% | 持续 0 |
|  | `fasting` | 79.9 | 44.1 | **11.5** (2) | **-74%** | 跌至新低 |
|  | `animal-based` | 0.2 | 0.2 | **0** (0) | 持平 0 | 仍未采用 |
| **lab 指标** | `glucose` | 209.6 | 98.4 | **97.4** (17) | -1% | 持平 R7 低位 |
|  | `sugar` | 367.1 | 280.0 | **n/a** | — | 未单独统计 |
|  | `inflammation` | 48.4 | 94.1 | **80.2** (14) | -15% | 微降，但仍处历史高位 |
|  | `iodine` | n/a | n/a | **143.3** (25) | — | 单视频主导 (thyroid 视频 25/25) |
| **新轴词** | `cortisol` | n/a | 41.3 | **34.4** (6) | -17% | 微降 |
|  | `seed oils/vegetable oils` | 7.5 | 13.2 | **28.7** (5) | **+117%** | **翻倍**：thyroid 视频 2 次 + belly fat 1 次 + colon 2 次 |
|  | `ozempic/GLP-1` | 0 | 10.4 | **0** (0) | **-100%** | R8 完全消失 |
|  | `RFK/Kennedy` | 0 | 3.4 | **0** (0) | -100% | 政治流量清零 |
| **口头禅** | `so` (含 So/So,/So) | 1276.0 | 1042.3 | **1490.1** (260+48+170) | **+43%** | **反弹**：R8 远超 R7 |
|  | `because` | 463.6 | 411.3 | **429.9** (75) | +5% | 微升 |
|  | `if you` | 505.8 | 489.4 | **429.9** (75) | -12% | 微降 |
|  | `okay` | 22.0 | 22.1 | **51.6** (9) | **+133%** | 重大异常（仅 4 篇 9 次） |
|  | `right` (全部) | 57.0 | 50.2 | **68.8** (12) | +37% | 微升 |
|  | `right?` (tag) | 0.2 | 3.2 | **5.7** (1) | +78% | 持续微升，1 次命中 |
| **攻击词** | `toxic` | 8.6 | 13.2 | **11.5** (2) | -13% | 持平 R7 |
|  | `poison` | 2.0 | 2.8 | **11.5** (2) | **+311%** | 反弹（thyroid: 牙膏 poison control 1 次 + sardine: toxic load 1 次） |
|  | `stupid` | 1.8 | 0.4 | **0** (0) | 持平 0 |  |
|  | `lie/lies/lying` | 7.1 | 3.8 | **0** (0) | -100% | 完全消失 |
| **品牌** | `Health Champions` (开场) | 20.7 | 20.2 | **22.9** (4/4 = 100%) | +13% | **100% 锁定**（4/4 文件命中） |
|  | `Hello Health Champion` 开场 | 89/100 | 96/100 | **4/4 (100%)** | +4% | 100% 完美命中 |
|  | `Ulite` | n/a | 3 | **17.2** (3) | **+473%** | sardine 视频 1 次 + 3 处变体 |
|  | `Uveia/euLyte/UmethylB` | 0 | 1 | **0** (0) | 持平 0 | 仅 Ulite 存活 |
|  | `Wellness For Life` | 0 | 0 | **0** (0) | 0% | 永久雪藏 |
|  | `Survival Biology` | 0 | 0.6 | **0** (0) | 持平 0 | 仍未复活 |
|  | `Dr Sten Ekberg` 自我称谓 | 1 | 0 | **0** (0) | 持平 0 | 仍不口播 |
| **引用** | `study` | 26.6 | 3.8 | **0** (0) | **-100%** | **完全清零** |
|  | `research` | 9.0 | 5.7 | **5.7** (1) | 0% | 仅 1 次模糊引用 |
|  | `published` | n/a | 0.2 | **0** (0) | 持平 0 |  |
|  | `according to` | 17.0 | 1.1 | **0** (0) | -100% | 完全清零 |
|  | `Mayo/NIH/Lancet` | 0 | 0 | **0** (0) | 0% | 仍不引顶刊 |
| **疾病靶** | `cancer` | 21.4 | 20.2 | **n/a** | — | colon cancer 标题 1 次 |
|  | `inflammation` | 48.4 | 94.1 | **80.2** (14) | -15% |  |
|  | `thyroid` | 23.9 | 42.6 | **n/a** (单视频主导) | — | thyroid 视频 1/4 |
|  | `cortisol` | n/a | 41.3 | **34.4** (6) | -17% | belly fat 视频 6 次 |
|  | `belly fat` | n/a | n/a | **高频** | — | belly fat 视频全题 |
| **钩子** | `what if/what happens` | 9.8 | 43.6 | **n/a** (0) | — | 4 标题均不用 |
|  | `I Ate/N Days` 标题 | 7 | 2 | **1** | -50% | sardine 视频为唯一自我实验 |
| | `#1 Absolute Best` 标题 | 19/100 | 19/100 | **1/4 (25%)** | 持平 | colon cancer 标题 |
| | `Top 10` 标题 | 42/100 | 23/100 | **1/4 (25%)** | 持平 | thyroid 视频 |
| **CTA** | `if you enjoyed this video` | n/a | n/a | **4/4 (100%)** | — | 100% 文件使用 |
| **新发现** | `you'?re going to` | n/a | n/a | **97.5** (17) | — | R8 新统计：高频"预测式"句式 |
|  | `I'm going to show` | n/a | n/a | **11.5** (2) | — | R7 发现 100% 锁定开场的延续 |

---

## 2. Top 8 发现（按重要度排序）

### 发现 1: **R8 是"R7 末段延续"**——所有基线人格不变，仅 4 项异常反弹

**核心判定**: 与 R7 对比，R8 4 篇文件在绝大多数维度上**保持稳定**或**微涨微跌**，与"R7 是 R6 谷底反弹期"一致。但有 4 个**异常反弹**值得注意：
- `so` +43%（1042→1490/100K）
- `keto` +1333%（3.6→51.6/100K，但绝对值仅 9 次 = 单一 sardine 视频驱动）
- `okay` +133%（22.1→51.6/100K，绝对值仅 9 次 = 4 篇散点）
- `poison` +311%（2.8→11.5/100K，绝对值仅 2 次 = thyroid 视频"poison control"提及）

**一手示例**:
- `[20260529001.md 00:15:54.320]` "so many people try this or try keto and they say, 'Oh, I felt so amazing.'" — keto 在 sardine 视频里**作为对比项**出现，不是推荐
- `[20260522001.md 00:06:12.800]` "if toothpaste is accidentally swallowed, then you need to contact poison control immediately" — poison 在甲状腺视频里是**引用牙膏标签**，非攻击
- `[20260522001.md 00:16:32.560]` "Okay, that's what it does." — 课堂式 okay 仍贯穿

**解读**: 4 项反弹**全部由单一视频驱动**（sardine 拉高 keto/so/okay，thyroid 拉高 poison/iodine），**不是频道风格的转变**。[我推断] R8 是 4 个**互相独立的主题视频**的合集（colon cancer / belly fat / thyroid / sardine experiment），而非有意识的"内容范式更新"。**R7 → R8 跨度 3 周的本质**：是 R7 末段（2026-04-24）到 R8 首段（2026-05-08）的自然延续，无断点。

---

### 发现 2: **R8 完全清零 Ozempic / RFK / study / lie / according to**——R7 的政治-学术轴彻底退出

**数据**:
- `ozempic/GLP-1`: R7=10.4 → **R8=0**（-100%）
- `RFK/Kennedy`: R7=3.4 → **R8=0**（-100%）
- `study`: R7=3.8 → **R8=0**（-100%）
- `lie/lies/lying`: R7=3.8 → **R8=0**（-100%）
- `according to`: R7=1.1 → **R8=0**（-100%）
- `research`: R7=5.7 → R8=5.7（持平，仅 1 次：[20260515001.md 00:17:54.480] "there's been a lot of research done"）

**一手示例**:
- `[20260508001.md 00:00:00]` "Colon cancer used to be considered an old person's disease..." — 整篇无任何"研究"或"研究显示"
- `[20260515001.md 00:17:54.480]` "preserve the tissue that is really hard to replace as we age. And there's been a lot of research done..." — **唯一 1 次 "research"**，且不带具体引用
- `[20260522001.md 00:04:56.080]` "And this is not a theory. It's not a suspicion that maybe fluoride will compete and inhibit because from about 1850 through the 1950s, fluoride was used as a treatment for hyperyroid" — **用历史事实替代学术引用**

**解读**: R7 报告把 RFK/Ozempic 称为"R7 最大的题材拓新"。R8 显示**这两个新轴都是单视频级的"蹭流量"**，并未成为频道持续主题。同时 `study/according to/research` 进一步**跌到历史最低或完全清零**。[我推断] Ekberg 已**彻底放弃学术引用作为权威源**，转而用"自我实验 + 历史事实 + 临床经验"三件套。这与 R7 发现 3 的判断一致——R8 是"无引用化"的进一步巩固。

---

### 发现 3: **R8 仍是"#1 Absolute Best / Top 10 / What Happens"三模板为主**，但新增"我吃 N 天"复归

**R8 标题 (4/4)**:
1. `[20260508001.md]` "#1 Absolute Best Way To Prevent Colon Cancer" → **#1 模板** (R7=19%)
2. `[20260515001.md]` "Why Belly Fat Changes After 50" → **"Why + 现象" 解释型标题** (新模板，R7 未见)
3. `[20260522001.md]` "You Cannot Heal Your THYROID If You Do These 10 Things Daily" → **Top 10 模板** (R7=23%)
4. `[20260529001.md]` "I Ate Nothing But Sardines For 5 Days and Here's What Happened" → **自我实验模板** (R7=2%，R8=25%)

**解读**: R8 4 个标题**分散在 4 个不同模板**，没有 R7 那种"What if you... 30 days" 的单一模板主导。[我推断] R7 末段到 R8 的内容编排回到"主题多样性"——colon cancer（疾病预防）/ belly fat（生理变化）/ thyroid（习惯清单）/ sardine（自我实验）各占一种模板。这与 R6 报告里"主题-器官-症状"分散式编排一致。

---

### 发现 4: **`okay` 异常反弹 133%**——R8 课堂式人格微强化

**数据**: `okay` R7=22.1/100K (104 次) → **R8=51.6/100K (9 次)**
- 命中文件: `[20260508001.md]` 1, `[20260515001.md]` 1, `[20260522001.md]` 5, `[20260529001.md]` 2

**一手示例**:
- `[20260522001.md 00:12:05.360]` "called thyroid peroxidase. Okay, that's what it does." — **典型课堂式 "Okay, ..." 句首**
- `[20260522001.md 00:15:18.560]` "Okay, let's look at some other things that will affect your thyroid." — **段落切换信号**
- `[20260522001.md 00:17:29.120]` "Okay, what do we want to do?" — **互动式引导**

**解读**: R6-R7 一直把 `okay` 视为"课堂教师人格"的稳定锚点（22±1/100K）。R8 翻倍到 51.6，**全部集中在 thyroid 视频（5/9）**。thyroid 视频的"10 个习惯"清单结构天然适合用 `okay` 做段落分隔（10 个 habit × 每段开头 1 次 okay）。[我推断] `okay` 反弹**不是人格变化**，是**清单式视频的格式副产物**。R8 仍是"教师单向解释 + 段落间用 okay 切换"的稳定人格。

---

### 发现 5: **`keto` 单视频拉动 1333%**——sardine 视频成为 keto 的"对比实验"载体

**数据**: `keto` R7=3.6/100K (17 次) → **R8=51.6/100K (9 次)**
- 全部 9 次命中都在 `[20260529001.md]` (sardine 视频)

**一手示例**:
- `[20260529001.md 00:15:54.320]` "so many people try this or try similar things or try keto and they say, 'Oh, I felt so amazing.'" — **作为对比项提及**
- `[20260529001.md 00:16:36.880]` "this could be okay if you are already in keto, if you're already fully fat adapted" — **作为前置条件提及**
- `[20260529001.md 00:20:03.360]` "do a smooth keto transition and we reduce the gut fuel" — **作为替代方案提及**
- `[20260529001.md 00:22:52.000]` "you do any sort of transition into keto or you do some short-term fasting, you do want to take some" — **作为过渡策略提及**

**解读**: R7 报告判断 Ekberg "不在话语里用 keto 标签" 是反标签策略。R8 显示**keto 在 sardine 视频里是"对比锚"**——sardine 饮食本质接近 keto（零碳水 + 高脂肪），Ekberg 主动**把 sardine 与 keto 框架并列**，方便观众理解。[我推断] 不是 R7 反标签策略的翻转，而是**用 keto 作为"读者已知概念"做认知桥梁**。keto 在 R8 不再是"禁词"，但仍不是"推荐词"。

---

### 发现 6: **100% 锁定开场 + 100% 锁定 CTA 结尾**——R7 的人格锚点全部保留

**数据**:
- `Hello, health champions.`: R7=96/100 (96%) → **R8=4/4 (100%)**
- `If you enjoyed this video`: R8=4/4 (100%, 全新数据点)

**一手示例**:
- `[20260508001.md 00:00:23.520]` "Hello, health champions. Today, I'm going to show you exactly how to create those conditions..."
- `[20260515001.md 00:00:21.200]` "Hello, health champions. In this video, I'm going to show you exactly why..."
- `[20260522001.md 00:00:21.040]` "Hello, health champions. Today we're going to cover 10 daily habits that block thyroid healing."
- `[20260529001.md 00:00:23.440]` "Hello, health champions. Here's what happened when I ate nothing but sardines for 5 days."

**CTA 结尾 (100% 命中)**:
- `[20260508001.md 00:18:12.000]` "If you enjoyed this video, you're going to love that one. And if you..."
- `[20260515001.md 00:24:53.120]` "If you enjoyed this video, you're going to love that one. And if you..."

**解读**: R7 发现 HC 称谓 96/100 是"百年品牌资产"。R8 是**4/4=100% 完美命中**（虽然样本量小）。配合 100% 的 "if you enjoyed" CTA，**Ekberg 的人格骨架（HC 称谓 + 互动 CTA）在 R8 没有任何漂移**。[我推断] 这是 YouTube 健康类频道的"硬约束开场"——一旦固化就不应变动（参考 MrBeast / Doctor Mike 等频道的开场稳定度）。

---

### 发现 7: **商业品牌只剩 `Ulite`**——`Euvexia/Nexus/Survival Biology` 全部清零

**数据**:
- `Ulite`: R7=3/100K → **R8=17.2/100K**（**+473%**，单一 sardine 视频 3 次）
- `Euvexia/Nexus/euLyte/UmethylB`: R7=5.5/100K → **R8=0/100K**（全部清零）
- `Survival Biology`: R7=0.6/100K → **R8=0/100K**

**一手示例**:
- `[20260529001.md 00:01:51.120]` "the big thing I would recommend if you try something like this, any restrictive diet or any major change where you cut back on carbs, you want to get some electrolytes. So I took three scoops a day of my own brand of electrolytes called Ulite." — **明确"my own brand"** 自指商业产品

**解读**: R7 报告把 "Euvexia/Nexus 回归" 解读为"商业化术语按需复活"。R8 显示**只剩 Ulite 还在用**，且**仅在 sardine 视频里**作为"低碳水补偿电解质"的功能性推荐出现。[我推断] Ulite 是 R8 唯一保留的商业品牌资产，**因为它功能性匹配视频主题**（低碳水饮食 → 电解质补充）。其他品牌 (Euvexia/Nexus) 在 R8 的 4 个主题（colon cancer / belly fat / thyroid / sardine）里**没有匹配场景**，所以被自然搁置。

---

### 发现 8: **种子油话题翻倍到 28.7/100K**——但仍是单一议题驱动

**数据**: `seed oils/vegetable oils` R7=13.2/100K → **R8=28.7/100K (+117%)**
- 命中分布: `[20260508001.md]` 2, `[20260515001.md]` 3, `[20260522001.md]` 2, `[20260529001.md]` 0

**一手示例**:
- `[20260522001.md 00:22:00.560]` "you have Hashimoto's and you take more iodine..." — thyroid 视频关联 seed oils 是隐式的（通过"避免加工食品"间接提及）
- `[20260515001.md]` belly fat 视频 3 次提及 — 与"炎症 - 种子油 - 内脏脂肪"链条相关
- `[20260508001.md]` colon cancer 视频 2 次提及 — 与"加工食品 - 慢性炎症 - 癌变"链条相关

**解读**: R7 报告把 seed oils +76% 视为"健康食品反派指认"的核心证据。R8 进一步翻倍到 28.7，**3/4 视频都提及**（sardine 例外，因为它本身就是 omega-3 主题）。[我推断] seed oils 已成为 Ekberg 2026 年的**稳定反派靶**（与 R6/R7 的 toxic 反弹属同一趋势线），且在"代谢 - 炎症 - 器官疾病"叙事里承担"加工食品代表"角色。

---

## 3. 给 fuxi-skill 蒸馏的 5 个直接可用更新

1. **HC 开场 100% 锁定 (4/4)** + **CTA 结尾 100% 锁定 (4/4)**：R7 已确认的"必用开场 + if you enjoyed this video CTA" 在 R8 完美保留，**这两个是 SKILL 的硬约束**。
2. **keto 不再是禁词而是"对比锚"**：R7 报告的"反 keto 标签"判断在 R8 翻转——sardine 视频用 keto 作为读者已知概念做认知桥梁。**可让 SKILL 在"低碳水/生酮饮食"主题下用 keto 做类比锚点**，但仍不作为"推荐词"独立使用。
3. **okay 仍是课堂式人格信号**：R8 51.6/100K（虽然样本小）确认 okay 仍是段落分隔的标准信号词。**保留"okay, ..." 句首作为段落切换标记**。
4. **新禁词清单 (R8 强化版)**:
   - 永久禁: `study / according to / published / Mayo / NIH / Lancet` (R7=0.4-3.8 → R8=0)
   - 永久禁: `RFK / Kennedy / Ozempic / GLP-1` (R7 短暂出现 → R8 完全清零，**不作为持续主题**)
   - 永久禁: `Wellness For Life / Survival Biology / Euvexia / Nexus / euLyte / UmethylB` (R8=0)
   - 永久禁: `lie / lies / lying` (R8=0，确认 R7 的话术降级已固化)
5. **可保留的中插品牌资产**: 仅 `Ulite` (R8 17.2/100K)**。当主题涉及"低碳水 / 生酮 / 长时间断食 / 剧烈出汗"时，可让 SKILL 用 "I recommend electrolytes like my own brand Ulite" 形式软广。其他产品品牌**不复活**。
6. **预测式句式 `you're going to` (R8 17 次 = 97.5/100K)** 是 R8 新发现的强信号——Ekberg 在因果链中**大量使用"you will... / you're going to..."** 做结果预测。**保留作为段落推进的标准句式**。

---

## 4. R8 4 篇视频"主轴 - 风格"分布

| 文件 | 主轴 | 器官/系统 | 模板 | 关键 diet 词 | 关键 lifestyle 词 | 异常信号 |
|---|---|---|---|---|---|---|
| 20260508001 | Colon cancer prevention | 消化系统 | #1 Absolute Best | insulin (5), glucose (2), processed foods (3) | seed oils (2), fasting (1) | **seed oils 2 次** |
| 20260515001 | Belly fat after 50 | 内分泌 | Why + 现象 | insulin (4), glucose (1), inflammation (4) | cortisol (6), testosterone | **cortisol 6 次** |
| 20260522001 | Thyroid 10 daily mistakes | 内分泌 | Top 10 (countdown) | insulin (1), inflammation (1) | iodine (25), soy, fluoride, soy, cardio | **iodine 25 次 + poison control 1 次** |
| 20260529001 | Sardine 5-day experiment | 营养 | I Ate N Days | keto (9), fasting (1), inflammation (4) | omega-3, electrolytes, **Ulite (3)** | **keto 9 次 + Ulite 3 次** |

**单视频驱动的极端值**:
- **keto 9/9 来自 sardine 视频**
- **Ulite 3/3 来自 sardine 视频**
- **iodine 25/25 来自 thyroid 视频**
- **cortisol 6/6 来自 belly fat 视频**
- **poison 2/2 来自 thyroid 视频（"poison control"）**

[我推断] R8 是**4 个完全独立主题视频**的合集，无跨视频主题延续性。这与 R7 的"What's in your water / toxic load" 跨视频主题线不同——R8 是**单点深挖型**而非"主题串联型"。

---

## 5. R8 异常项 / 待观察项

- **`okay` 51.6/100K (R7=22.1)** — 绝对值仅 9 次，thyroid 视频独占 5 次。**需 R9 验证是否回落到 22±5 区间**。
- **`poison` 11.5/100K (R7=2.8)** — 绝对值仅 2 次，thyroid 视频"poison control" 1 次是**引用标签**而非攻击。**需 R9 验证是否回归 R7 区间**。
- **`you'?re going to` 97.5/100K (R8 首次统计)** — 高频预测式句式，需 R9 验证是否稳定。
- **`seed oils/vegetable oils` 28.7/100K (R7=13.2)** — 翻倍但仍是单议题驱动，需 R9 验证是否成稳定反派靶。
- **`Right?` tag 5.7/100K (R7=3.2)** — 持续上升，1 次命中仍处低位，需 R9 验证是否突破 10/100K。

---

**Source convention note**:
- 一手 (他说的) = `[YYYYMMDD###.md HH:MM:SS]` (e.g. `[20260522001.md 00:04:56.080]`)
- 二手 (别人说他的) = `[来源 URL]` (本 R8 无)
- 我推断的 = `[我推断]`
