# R8 著作维度调研：Dr. Sten Ekberg（@drekberg）2026-05-08 → 2026-05-29

调研范围：${HOME}/Documents/女娲造人/@drekberg/ 第 701-704 个 .md 文件（共 4 个）
跨度：3 周（2026-05-08 → 2026-05-29）
工作流：grep-first（未读全文），时间窗 10 分钟硬限制

---

## 0. R8 四集基本信息

| 视频 ID | 发布日 | 标题 | 行数 |
|---|---|---|---|
| C7CKRkAIs3A | 20260508 | *#1 Absolute Best Way To Prevent Colon Cancer* | 179 |
| xivHL3Eo4oc | 20260515 | *Why Belly Fat Changes After 50* | 230 |
| m65Aq4H-oic | 20260522 | *You Cannot Heal Your THYROID If You Do These 10 Things Daily* | 253 |
| pLKMkkMt5P0 | 20260529 | *I Ate Nothing But Sardines For 5 Days and Here's What Happened* | 255 |

**跨度异常**：[我推断] R8 只覆盖 3 周（21 天），是研究分段中窗口最窄的——这意味着这是 R7 末段的延续，4 集可视为同一密集期样本。

---

## 1. 必查关键词命中数（grep 命令 + 命中数）

| 关键词 | 命中文件数 | 命中行数（粗略） |
|---|---|---|
| Survival Biology / survival biology | 0 | 0 |
| Uveia / euLyte | 0 | 0 |
| **Ulite** | 1 | 3（仅 20260529 sardine 集） |
| UmethylB | 0 | 0 |
| Nexus | 0 | 0 |
| Health Champions | 4/4 | 4（每集开场招呼） |
| Wellness For Life | 0 | 0 |
| carnivore / animal-based | 0 | 0 |
| Ozempic / Wegovy / GLP-1 | 0 | 0 |
| fasting-mimicking / FMD | 0 | 0 |
| autophagy / mTor / rapamycin | 0 | 0 |
| sirtuin / NAD+ / NMN | 0 | 0 |
| longevity | 1 | 2（仅 20260515 muscle=longevity 2 处） |
| RFK / Kennedy / MAHA | 0 | 0 |
| insulin resistance | 3 / 4 | 18（0508=7 / 0515=7 / 0522=4 / 0529=0 显式） |
| study / studies / research / published | 4 / 4 | 总计 5（每集 1-2 处，全部接近 0） |
| Standard Process / Triad of Health | 0 | 0 |
| Olympic / decathlete / holistic doctor | 0 | 0 |
| **insulin sensitive**（变体） | 1 | 1（[20260529001.md 17:13-17:20] [一手]） |
| "I Ate X for N Days" hook | 1 | 仅 0529 标题（sardines 5 days） |
| "What If / What Happens / This Happens" 子句 | 4 / 4 | 多处（每集 5+ 处连续叙述） |
| right? 尾反问 | 1 / 4 | 1（仅 0515） |
| toxic | 2 / 4 | 2（0522 + 0529） |

---

## 2. 五大发现

### 发现 1：**"Ulite" 单集首推（2026-05-29 sardine 集）——"my own brand of electrolytes called Ulite"**

R7 内 euLyte 是 R7 内主推商业产品（7 集显式推销）；R8 内 **"Ulite"** 是首次出现的新品牌命名（极可能 R7 末段 2026-04 期间已悄悄更名，但 R7 corpus 截止 2026-04-24，故 Ulite 在 R7 文件表 100 集内不出现）。

- 关键句 1：`[00:01:51.120] day of my own brand of electrolytes called Ulite. All in all, I ate 30 tins of sardines in the five [days]`（[20260529001.md 37] [一手]）
- 关键句 2：`[00:22:45.360] how the electrolyte, the ulite helped in my case, and it's important to understand this because if`（[20260529001.md 210] [一手]）
- 关键句 3：`[00:23:40.800] glycogen but from this mechanism as well. So in my case, the Ulite helped to compensate for`（[20260529001.md 218] [一手]）
- 推销密度：3 处在 sardine 5-day 单集内出现，且分散在 3 个不同时间点（01:51 / 22:45 / 23:40），不是"结尾一次念" 而是"叙述中夹带"。
- 解释机制：他把 Ulite 的功能性叙述嵌套进"sardine 5-day 缺纤维 → 缺 butyrate → 缺 short-chain fatty acid → 钠钾镁流失 → 胰岛素下降导致排钠 → 流失电解质" 的因果链中，[20260529001.md 23:12-23:26] [一手]。
- **意义**：[我推断] **品牌从 euLyte → Ulite 已完成切换**（R7 7 集推销 + R8 1 集集中推销）。这可能与 R7 中提到 UmethylB 升格类似的产品线延展（"eu" 前缀已切换为"U" 单字母化、更短促更易记）。

### 发现 2：**Survival Biology 命名在 R8 0 命中——未被升格为 doctrine**

R7 末段（2026-01-16 GLP-1 集）首次集中 3 次使用 "survival biology" 命名；R8 内 **0 命中**：

- `grep -iE "survival biology" 20260508001.md 20260515001.md 20260522001.md 20260529001.md` → 无任何输出。
- R8 4 集均未涉及 GLP-1 / Ozempic / 体重药物（`grep -iE "Ozempic|Wegovy|GLP-1"` → 0 命中）。
- [我推断] "Survival biology" 在 R7 是一次集中爆发（3 次 / 单集 22:00 内），但 4 个月后 R8 完全停用。这**不是 doctrine 升格**——它仍是 R7 单集单点使用的修辞武器，未扩展到他的胰岛素/酮症/长寿论述中。

### 发现 3：**长寿主轴收缩为"muscle=longevity"——attia 风的概念降级版**

R7 内 2026-01-02 mTor/rapamycin 突破 50+ 行深度论述，R7 末段 2026-04-24 *#1 Reason You Age Too Fast After 40* 进入抗衰题材标题；R8 内长寿只剩 1 集 2 处：

- 20260515 *Why Belly Fat Changes After 50* `[00:13:57.760] is that muscles equal longevity. Muscles equal quality of life. And the fact that muscles use up`（[20260515001.md 138] [一手]）
- 20260515 `[00:18:09.760] strength in particular. But muscles equal longevity and quality of life. Because if`（[20260515001.md 172] [一手]）
- 完全未提 mTor / rapamycin / sirtuin / NAD+ / NMN / resveratrol——`grep -ciE "mTor|rapamycin|sirtuin|NAD|NMN|resveratrol" 20260508001.md 20260515001.md 20260522001.md 20260529001.md` → 0/0/0/0。
- 全部归约为"muscles = longevity" 二元公式（直接搬用 Attia 的 "Muscle = the organ of longevity" 框架但**未命名 Attia**——`grep Attia` 4 文件 0 命中）。
- 20260515 同时把"长寿"框架嫁接到"50 岁后激素变化"主题：testosterone 每年 -1%（30 岁后累计）、cortisol 缓冲失效、visceral fat 内分泌化（[20260515001.md 03:17-04:56] [一手]）。
- **意义**：[我推断] R8 内长寿主轴**从 2026-01 的机制深论（mTor/rapamycin）收缩为 2026-05 的应用口号（muscle=longevity）**。这是 doctrine 化失败后的实用性退守：他没有用 mTor/rapamycin 体系占领长寿赛道，而是把长寿收编进"力量训练 + 维持肌肉" 的实操口诀。

### 发现 4：**FMD / autophagy / rapamycin / NAD+ / NMN 全部 0 命中——长寿/抗衰主轴回缩到 R6 水平**

R7 末段（2026-01-02 / 2026-02-28 / 2026-04-24）的长寿集中论述在 R8 内完全停摆：

- `grep -iE "autophagy|mTor|rapamycin|sirtuin|NAD|NMN|fasting-mimicking|FMD|proLon|Valter Longo" 20260508001.md 20260515001.md 20260522001.md 20260529001.md` → 0 命中。
- `grep -iE "longevity|anti-aging|antiaging|aging"` → 仅 1 集 2 处（"muscle=longevity"），全集中于 20260515。
- 抗衰话题未完全消失但已**降级为应用口号**（muscle=longevity），不再做机制深论。
- **意义**：[我推断] Ekberg 的"长寿 / 抗衰"主轴在 R8 内**回缩到 R6 水平**——R6 内 0 标题、R7 出现 1 集 50+ 行机制深论 + 1 标题、R8 内只剩口号级 2 命中。这是一个**未完成的 doctrine 化尝试**：他用 mTor/rapamycin 入场，但 4 个月后 R8 退回纯代谢/胰岛素话语。

### 发现 5：**RFK Jr / 政治-医药双轴在 R8 0 命中——政治化操作彻底停摆**

R7 内 1 集（2025-05-09 RFK Jr Banned 集）单次借力 MAHA；R7 末段 2026-01-16 Ozempic 集 22 命中；R8 内 **0 命中**：

- `grep -iE "RFK|Kennedy|MAHA|Ozempic|Wegovy|GLP-1|Mounjaro|Zepbound|weight loss drug"` → 0 命中。
- 4 集全部回到"代谢病 + 自我实验 + 营养基础" 的纯健康话语：colon cancer prevention / belly fat 50+ / thyroid 10 habits / sardine 5-day。
- **意义**：[我推断] R7 末段曾试图搭 GLP-1 + RFK Jr 政治顺风车（2026-01-16 GLP-1 集 22 命中 + 2025-05-09 MAHA 单集 15 命中），但 R8 内**完全回退到代谢/胰岛素/肠道** 三大主轴。政治-医药双轴在 R8 是**断线状态**——他未把它升格为持续议题。

### 发现 6（次要）：**钩式标题占比 100% (4/4) —— "What If/What Happens" 子句 + 标题级 "I Ate X" 全部持续**

- 标题级钩：#1 Absolute Best Way... / Why Belly Fat... / You Cannot Heal... / I Ate Nothing But Sardines...——4/4 全部使用标题钩（其中"X for N Days"型 1 集）。
- 叙述子句钩："What happens" / "What happens now" / "What happens is" 在每集出现 5+ 次，[20260508001.md 02:48, 03:13 / 20260515001.md 03:29, 06:35, 06:58, 09:11, 12:31 / 20260522001.md 03:15, 09:09, 14:26, 20:13, 25:35 / 20260529001.md 17:54, 22:10, 22:30] [一手]。
- 20260529 自我实验者系列**继续运行**（sardine 5-day = R7 内 5+ 集 "X for N Days" 模式的延续）。
- "What If" 完整型钩：0 命中（R7 内" What If You" 钩式标题未在 R8 4 集标题中出现）。
- **意义**：[我推断] 钩式标题 / 子句策略在 R8 仍是核心手法（4/4 标题钩），但" What If You" 主型钩被替换为" You Cannot Heal Your THYROID If You..."（0522）、" Why Belly Fat..."（0515）、" I Ate Nothing But..."（0529）、" #1 Absolute Best..."（0508）四种变体。钩式品牌未集中化但持续滚动。

### 发现 7（次要）：**personal narrative 仅 1 集 2 段"小坦白"——健康危机未展开**

- 20260529 sardine 集是 R8 内唯一 personal narrative 集：
  - `[00:00:06.480] sardines for five straight days. But I'll be very honest with you, I did not feel amazing.`（[20260529001.md 21] [一手]）
  - `[00:15:07.840] And my mood and my attitude kind of shifted to if I have to choke down one more tin`（[20260529001.md 147] [一手]）
  - `[00:15:28.320] So, in my honest summary, I would have to say that I felt okay, but not amazing.`（[20260529001.md 150] [一手]）
  - `[00:16:45.360] I have to be honest, I was not perfectly fat adapted prior to going into this. I basically`（[20260529001.md 161] [一手]）
- "诚实坦白"叙述 4 次（"I'll be very honest" / "in my honest summary" / "I have to be honest"），但内容是**自我实验的具体体感**（mood 转变 / 失去 5-6 磅 / fat adapted 不足），**不是健康危机或过往病史**。
- 20260529 体重数据：`[00:15:15.440] of sardines, then blank. Now, during these five days, I lost about 5 to six pounds, which a lot of`（[20260529001.md 148] [一手]）；`[00:20:39.040] but I probably lost about two pounds of actual fat tissue, and the rest of it I lost one pound`（[20260529001.md 192] [一手]）。
- **意义**：[我推断] R8 内 personal narrative **未延展**到"健康危机/过往病史"4 段弧。他继续用"小坦白"（对自我实验体感的诚实描述）作为权威建立工具，但仍未揭出"为什么我在意这些"的个人健康根源。

### 发现 8（次要）：**身份话语完全不变（0 Olympic / 0 decathlete / 0 holistic doctor）**

- `grep -iE "Olympic|decathlete|holistic doctor|former|World Championships"` → 0 命中（4 文件 0 命中）。
- "Health Champions" 开场招呼持续 4/4 集（[20260508001.md 23 / 20260515001.md 23 / 20260522001.md 23 / 20260529001.md 23] [一手]）。
- **意义**：[我推断] R8 内身份认同继续走"观众群认同"（Health Champions）而非"个人履历认同"（Olympic / decathlete）路线，R7 末段 2025-02→06 集中回归 Olympic 身份的话语在 R8 完全消失。

### 发现 9（次要）：**学术引用完全清零（5 行总计，每集 1-2 处，0 处来自"study/research/published" 命名研究）**

- `grep -ciE "study |studies |research|published|journal" 20260508001.md 20260515001.md 20260522001.md 20260529001.md` → 1 / 2 / 1 / 1（4 集共 5 行）。
- R7 末段"study -86% / according to -94%" 学术清零的减法在 R8 持续。
- 完全没出现具体研究 / 具体人名 / 具体期刊。
- **意义**：[我推断] R7 末段的"去学术引用化" 修辞策略在 R8 完全延续。Ekberg 维持的是"机制 / 生理学 / 临床直觉" 论据来源，不引研究文献。

### 发现 10（次要）：**R7 末段确立的"种子油 / 糖 / 加工食品"三件套 100% 持续**

- 20260515 完整攻击点：sugar + processed foods + seed oils + refined carbs（[20260515001.md 14:43-14:51] [一手]）。
- 20260522 完整攻击点：seed oils (omega-6) + fluoride/chlorine/iodine 竞争 + soy isoflavones + reverse T3 + blue light + gluten（10 大习惯列表，[20260522001.md 04:14-18:02] [一手]）。
- 20260529 攻击点：saturated fats/sodium/cholesterol "those are bad" 的话语（[20260529001.md 05:39-05:45] [一手]）+ omega-6:omega-3 比例失衡（[20260529001.md 03:51-04:26] [一手]）。
- **意义**：[我推断] 这是 R8 最稳定的话语主轴——"糖 / 种子油 / omega-6 失衡 / 加工食品"攻击 4/4 集无死角存在。

---

## 3. R7 → R8 演化对比

| 维度 | R7 (2024-05 → 2026-04) | R8 (2026-05-08 → 2026-05-29) | 演化方向 |
|---|---|---|---|
| **品牌** | euLyte 7 集主推 | **Ulite 首次显式 1 集 3 命中** | 品牌从 euLyte → **Ulite 切换** |
| **Survival Biology 命名** | 1 集 3 次（20260116） | 0 命中 | **未升格为 doctrine** |
| **mTor/rapamycin 长寿** | 1 集 50+ 行（20260102） | 0 命中 | **机制深论停摆** |
| **"muscle=longevity" 口号** | 0 | 1 集 2 处 | 升格为应用口号（替换 mTor 体系） |
| **FMD / autophagy** | 1 集 2 段（20241227）+ 1 集 50+（20260102） | 0 命中 | **完全回退到 R6 水平** |
| **RFK Jr / MAHA** | 1 集 15 命中（20250509） | 0 命中 | **政治化操作停摆** |
| **Ozempic / GLP-1** | 1 集 22 命中（20260116） | 0 命中 | 完全回退 |
| **"What If You" 钩式标题** | 87/100 = 87% | 0/4 标题级 | 钩式变体滚动（"#1" / "Why" / "You Cannot" / "I Ate"） |
| **"I Ate X" 自我实验** | 5+ 集 | 1 集（0529 sardines） | 持续运行 |
| **"I was / personal crisis" 叙事** | 0 健康危机 | 0 健康危机（仅 1 集 4 段"小坦白"） | 持续未揭出个人根源 |
| **Olympic / decathlete 身份** | 0 | 0 | 持续不强化 |
| **Health Champions 共同体招呼** | 96/100 | 4/4 = 100% | 100% 强化 |
| **学术引用（study/research）** | -86% / -94% 清零 | 5 命中（4 集 1-2 处） | **完全清零延续** |
| **种子油 / 糖 / omega-6 攻击** | 主轴级 | 4/4 集 = 100% 持续 | **R8 最稳定主轴** |
| **节目形式扩展（new show/podcast/course）** | 0 | 0 | 持续无新节目形式 |
| **Carnivore 立场** | 工具性、有限承认 | 0 命中 | 立场不变、不主推 |
| **Standard Process / Triad of Health** | 8 次 / 3 次 | 0 命中 | 持续无品牌归属 |

---

## 4. 未发现（明确）

- **0 个 "Survival Biology" 命名**：R8 内 0 命中。
- **0 个 mTor / rapamycin / autophagy / FMD / NAD+ / NMN / sirtuin**：R8 内 0 命中。
- **0 个 RFK / Kennedy / MAHA / Ozempic / Wegovy / GLP-1 / Mounjaro / Zepbound**：R8 内 0 命中。
- **0 个 Olympic / decathlete / holistic doctor 身份话语**：R8 内 0 命中。
- **0 个 Valter Longo / proLon / Standard Process / Triad of Health / Euvexia**：R8 内 0 命中。
- **0 个 "Animal-based"**：R8 内 0 命中。
- **0 个 new show / podcast / new course / membership / community**：R8 内 0 命中。
- **0 个 carnivore**：R8 内 0 命中。
- **0 个 Baker / Chaffee / Norwitz / Attia 引用**：R8 内 0 命中。
- **0 个个人健康危机叙事**：R8 内未延展"健康危机" 4 段弧（仅 sardine 集有"小坦白"）。
- **0 个 explicit "study" 学术引用**：R8 内 5 命中（4 集 1-2 处）延续 R7 末段清零策略。

---

## 5. R8 核心叙事（用于 R8 总结）

R8 是 R7 末段的延续，但具有以下三个特征性反转：
1. **品牌升级（euLyte → Ulite）** 是 R8 内最重要的新信息点——商业化品牌完成切换。
2. **长寿主轴收缩**（mTor/rapamycin 机制深论 → muscle=longevity 口号）显示"长寿" 主轴 doctrine 化失败、退守应用。
3. **政治-医药双轴完全断线**（RFK / Ozempic 全 0 命中）显示他主动回退到"代谢/胰岛素/肠道" 三大主轴的安全区。

R8 4 集全部建立在"代谢/胰岛素/肠道/激素" 四大主轴之上，未出现新的 doctrine 突破。

---

## 6. 备注

- 本调研严格遵循 grep-first 协议，未读任何文件全文；所有时间戳引用均直接来自 grep 输出。
- R8 仅 4 集，跨度 21 天，是 R 系列中最窄窗口；这意味着 R8 是 R7 末段的密集延伸，而非独立段落。
- R7 末段→R8 时间窗内（2026-04-24 → 2026-05-08）没有新数据点；R7 末段 = 20260424 唯一文件，R8 起始 = 20260508。
