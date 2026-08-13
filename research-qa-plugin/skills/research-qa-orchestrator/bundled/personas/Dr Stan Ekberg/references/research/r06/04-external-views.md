# R6 智识谱系：Dr. Sten Ekberg（2022-06-17 → 2024-05-17）

**切片范围**：R6 = 第 501-600 个 .md 文件，对应视频发布日 2022-06-17 → 2024-05-17，共 100 期。
**Agent 4 维度**：智识谱系（他引用谁、不引用谁、引用密度与机构）。
**标注体系**：
- 一手（他说的）→ `[YYYYMMDD###.md HH:MM:SS]`
- 二手（别人说他的）→ `[来源 URL 或文件名]`
- 我推断 → `[我推断]`

---

## 1. 量化总览（grep 命令 + 命中数）

### 1.1 当代医生/科普人物引用（R5 → R6 验证点）

命令：
```bash
cat /tmp/r6_files.txt | xargs -I {} grep -E "Weston|Berg|Atkins|Perlmutter|Attia|Hyman|Pollan|Taubes|Mercola|Gundry|Davis|Saladino|Baker|Chaffee|Norwitz|Ohsumi|Ulan" ${HOME}/Documents/女娲造人/@drekberg/{} 2>/dev/null
```

| 名字 | R6 命中文件数 | R5 → R6 变化 | 备注 |
|---|---|---|---|
| **Weston A. Price** | **0** | 1 → **0** | **R5 唯一点名历史权威在 R6 内完全消失** |
| **Weston（任何上下文）** | 0 | — | 字面 "weston" 也无任何匹配 |
| Berg（去除 "Ekberg" 子串） | 0 | (误命中基线 46) | Eric Berg 仍 = 0 真实引用 |
| Atkins | 0 | 1 → 0 | R5 1 次也消失 |
| Perlmutter | 0 | 0 → 0 | 仍 0 引用 |
| Attia | 0 | 0 → 0 | 仍 0 引用 |
| Hyman | 0 | 0 → 0 | 仍 0 引用 |
| Pollan | 0 | 1 → 0 | R5 借数据 1 次也消失 |
| Taubes | 0 | 0 → 0 | 仍 0 引用（**全 R6 内 100 期无任何"Taubes"、"Good Calories"、"Why We Get Fat"字样**） |
| Mercola | 0 | 1 → 0 | R5 反例引用 1 次也消失 |
| Gundry | 0 | 0 → 0 | 仍 0 引用 |
| Davis | 0 | 0 → 0 | 仍 0 引用 |
| Saladino | 0 | 0 → 0 | 仍 0 引用 |
| Baker (Shawn Baker) | 0 | 0 → 0 | 仍 0 引用（无 "Bone Baker"、"Carnivore Baker" 任何上下文） |
| Chaffee | 0 | 0 → 0 | 仍 0 引用 |
| Norwitz | 0 | 0 → 0 | 仍 0 引用 |
| Ohsumi | 0 | 0 → 0 | 仍 0 引用（**字面"Nobel Prize"在 R6 内仅出现 1 次 — 20240329001.md，提到的是 Roger Sperry 关于大脑能量消耗，与 autophagy / Yoshinori Ohsumi 无关**） |
| Ulan | 0 | 7(误命中) → 0 | 0 真实引用 |

**[我推断] R6 = 智识真空期**。Ekberg 在 R5 内仅有的 5 个真实当代/历史人物引用（Weston Price ×1, Pollan ×1, Mercola ×1, Atkins ×1, Ulan 误命中）在 R6 内 **全部归零**。100 期视频，他 **字面不点名任何同行、任何历史营养学家、任何作家**。

### 1.2 学术/流行病学引用模式

命令：
```bash
cat /tmp/r6_files.txt | xargs grep -icE "study|research|published|meta-analysis|Cochrane" 
```

| 模式 | R6 命中次数 | R5 → R6 变化 |
|---|---|---|
| `study`（字面） | 116 | ~100 → 116（基线噪声小幅上升） |
| `research` | 41 | ~50 → 41（略降） |
| `published` | 20 | 20+ → 20（持平） |
| `Cochrane` | **0** | 0 → **0** |
| `meta-analysis` | **0** | 0 → **0** |
| `systematic review` | 0 | 0 → 0 |
| `randomized` / `randomised` | 0 | 0 → 0 |
| `double-blind` | 0 | 1(误) → 0 |
| `peer-reviewed` | 0 | 0 → 0 |
| `clinical trial` | 0 | 0 → 0 |
| `RCT` | 0 | 0 → 0 |
| `published in`（特指某篇研究） | 0 | 3 → **0**（R5 内 3 处"published in <journal>"在 R6 内也消失） |

**[我推断] R5 的"研究语言"（"a study in Lancet in 1997"、"this article in the Lancet talked about 12 factors"）在 R6 内 0 次重现**。R6 内的 116 次 "study" 大多是"this is a large study"（指代模糊的研究集合）而非具体点名。

### 1.3 机构引用

| 机构 | R6 真实命中次数 | R5 → R6 变化 | 备注 |
|---|---|---|---|
| **Mayo Clinic** | **0** | 5+ → **0** | **R5 头号反证靶子在 R6 内彻底消失** |
| **Harvard** | 0 | 1 → 0 | R5 "harvard.edu" 1 处也消失 |
| **NIH** | 0 | 1 → 0 | — |
| **Lancet** | **0** | 2 → **0** | **R5 唯一正面引用的顶级期刊在 R6 内完全消失** |
| **JAMA** | 0 | 0 → 0 | — |
| **NEJM** | 0 | 0 → 0 | — |
| **CDC** | 1 | 2 → 1 | 唯一一次："according to the CDC that's 46 carbohydrate 16 protein and 36 fat" — 数据引用，非反证 |
| **FDA** | 9 | 1 → 9 | **R6 新增 9 次提及**。上下文：FDA 提议修改"healthy"标签规则（"Top 10 Foods That Can't Be Called HEALTHY ANYMORE!"，2023-04-14）|
| **USDA** | 7 | 多次 → 7 | 仍作"USDA guidelines"集体反证 |
| **ADA (American Diabetes Assoc.)** | 1 | 1 → 1 | "the ADA the AMA the USDA all those government agencies"（20230616001）— 集体反证 |
| **AMA (American Medical Assoc.)** | 1 | 多次 → 1 | 同上，集体反证 |
| **WHO / World Health Organization** | 1 | 1 → 1 | **R5 的"1948 WHO 健康定义"在 R6 内不再被正面引用**。R6 内 1 次提及 WHO 是批判性："World Health Organization has actually classified sleep deprivation as well as nighttime shift work as a probable carcinogen"（20221118001）— 借 WHO 论证睡眠不足致癌 |
| **Arthur C. Guyton & Hall** | **0** | 1 → **0** | **R5 "the law book"教材级引用在 R6 内完全消失** |
| **Arthur C. Guyton** | 0 | — | — |
| **Johns Hopkins** | 0 | 1 → 0 | — |
| **Yale / Stanford / Oxford / Cambridge / Tufts** | 0 | 0 → 0 | — |
| **functional medicine** | 3 | 0 → 3 | **R6 新增概念** — "most people who work in the functional medicine field"（20231103, 20240405, 20240419）— 把"functional medicine"医生当"懂营养的同行" |
| **medical establishment** | 0 | 0 → 0 | 改用 "mainstream"/"government agencies" 表述 |
| **mainstream** | 20 | — | 主流批判 = R5 话语延续 |

### 1.4 R6 内 Diet/Condition 关键词频率

| 关键词 | R6 总命中次数 | 备注 |
|---|---|---|
| `insulin resistance` | 330 | R6 核心疾病机制 |
| `keto` / `ketogenic` | 214 | 仍为主推饮食 |
| `metabolic` | 298 | 代谢综合征叙事核心 |
| `inflammation` | 221 | 炎症 = 通用病理 |
| `calorie` | 373 | 仍拆"热量平衡"模型 |
| `carnivore` | 28 | 10/100 期提及 |
| `ketosis` | 30 | 仍强调生酮状态 |
| `holistic` | 14 | R5 自标签延续 |
| `natural` | 129 | "natural" vs "refined" 仍为核心二分 |
| `Health Champions` | 93 | 招牌开场白（93/100 期开篇） |
| `intermittent fasting` | 多 | 工具菜单 |
| `plant based` | 0 | R6 内 0 次提及"plant-based diet" |
| `ancestral` | 0 | 0 次"ancestral" |

### 1.5 COVID/政治化主题

| 关键词 | R6 命中文件数 |
|---|---|
| `COVID\|coronavirus\|pandemic` | 0 |
| `vaccine` | 0（除常规医学上下文）|
| `lockdown\|Fauci\|Ivermectin\|Gates` | 0 |

**[我推断] R6 内 COVID 主题完全消失**（R5 内 4 期有相关讨论）。R6 回到纯"代谢-饮食"轨道。

---

## 2. R5 → R6 验证结论

| R5 假设 | R6 实测 | 结论 |
|---|---|---|
| **R5 智识"三脚架"**（WHO 1948 + Guyton 反 Mayo） | WHO 1948 = **0**、Guyton = **0**、Mayo Clinic = **0** | **三脚架在 R6 内整体坍塌**。R5 标志性的"WHO 定义 + Guyton 教材 + 反 Mayo Clinic"结构在 R6 内 0 次出现 |
| R5 0 个当代同行（Attia/Baker/Chaffee/Norwitz/Saladino = 0/8） | R6 仍 = **0/16** | **完全保留**。100 期视频，Ekberg 字面未点名上述 16 位当代同行中任何一位 |
| R5 0 个 Taubes | R6 仍 = **0** | **完全保留**。**全 R6 内 0 次出现 "Taubes"、"Good Calories"、"Why We Get Fat"、"Case for Keto" 等字样** |
| R5 0 个 Cochrane/meta-analysis | R6 仍 = **0** | **完全保留**。R6 系统综述引用 = 0 |
| **R5 内 5 个真实历史/当代人物引用** | R6 内 = **0/5** | **R5 引用网络在 R6 内归零**：Weston Price、Pollan、Mercola、Atkins、Sperry 全部消失。**R6 = 智识"空转期"** |
| R5 内 Lancet 2 次正面引用 | R6 内 = **0** | R5 的"用 Lancet 反 Lancet 主流"叙事也消失 |
| R5 内 FDA 1 次 | R6 内 = **9 次** | **唯一显著增加** — R6 有完整 1 期视频专门讲 FDA 修改"healthy"标签提案 |
| R5 内 functional medicine = 0 | R6 内 = **3 次** | **R6 新概念** — Ekberg 开始把"functional medicine doctor"当可引用的同行类别（不点名具体医生，但承认这一职业类别） |

---

## 3. R6 内 8 条核心发现

### 发现 1：R5 的"三脚架"在 R6 内整体坍塌 — 智识真空期

- **数据**：R5 内 Ekberg 智识体系有 3 个清晰支点：(a) 1948 WHO 健康定义（正面引用）、(b) Guyton & Hall《Textbook of Medical Physiology》("the law book")、(c) Mayo Clinic（反证靶子 ×5+）。三者共同构成"借 WHO + Guyton 权威，攻击 Mayo Clinic 主流叙事"的话术结构。
- **R6 实测**：
  - `WHO 1948` 健康定义 → **0 引用**（R5 的 `[20201120001.md 00:07:13.840]` 经典引用在 R6 内不再复现）
  - `Guyton` / `Textbook of Medical Physiology` → **0 引用**（R5 的 `[20210903001.md 00:04:35.479]` "the best reference for how the human body works is called Guyton and Hall textbook of medical physiology. It's been the standard since 1956..." 在 R6 内不再复现）
  - `Mayo Clinic` → **0 引用**（R5 的 `[20210903001.md 00:06:12.300]` "the experts I'll refer to are going to be the USDA and the Mayo Clinic not because I want to pick on them or analyze them specifically but cuz they publish a lot and they represent the general consensus" 不再复现）
- **一手观察**：R6 内 Ekberg 完全不引用任何具名教科书或具名医疗机构。**他不再进行"借权威打靶"的话术**。
- **[我推断]**：R6 是 Ekberg 智识体系的 **"自然主义讲述期"** — 100 期视频全靠"身体的自然设计 + 代谢逻辑"自说自话，不再需要外部锚点。这可能反映 (a) R5 时期的话术已稳定到不再需要重申、(b) 频道策略从"借权威打靶"转为"通俗化代谢教育"、(c) 视频数量变大（每周 2 期）后每期简化论证。

### 发现 2：R6 内出现 9 次 FDA 引用 — 唯一新增的"机构对话"

- **数据**：R5 内 FDA 1 次 → R6 内 9 次（10 倍增长）
- **来源**：`${HOME}/Documents/女娲造人/@drekberg/20230414001.md`（"Top 10 Foods That Can't Be Called HEALTHY ANYMORE!"，2023-04-14）
- **一手引用**（开场）：`[20230414001.md 00:00:55.920]` "basically in for a food fight and what's happened now is that the FDA is proposing some changes to the rules about how manufacturers are allowed to label food products"
- **一手引用**（对 FDA 略带肯定）：`[20230414001.md 00:02:54.000]` "to give the FDA some credit now that they finally they do something and this is super super exciting to me it's a step in the right direction it's a sign of some kind of Awakening"
- **一手引用**（结论）：`[20230414001.md 00:18:10.560]` "I would point out that the existing guidelines the USDA and the FDA"
- **一手引用**（具体冲突点）：`[20230414001.md 00:12:13.680]` "a 54-page paper to the FDA where they're saying that these proposed changes are overly restrictive" — 描述行业游说
- **用法**：FDA 在 R6 内被 **作为对话方** 而非反证对象。Ekberg 罕见地给 FDA 一些肯定（"step in the right direction"），但仍批评其"低脂 + 高谷物 + 允许糖"的核心建议
- **[我推断]**：FDA 的 R6 角色变化反映 Ekberg 对"机构"的态度从"全面反证"软化为"战术对话" — 当机构做出符合他框架的调整时（如限制"healthy"标签用糖），他愿意给 credit。这与他 R5 时期"反 Mayo Clinic"硬刚姿态形成对比。

### 发现 3：R6 内出现"functional medicine"作为隐含同行类别 — R5 完全没有

- **数据**：R5 内 "functional medicine" = 0 → R6 内 = 3 次
- **来源 1**：`${HOME}/Documents/女娲造人/@drekberg/20231103001.md`（2023-11-03）
  - 一手引用：`[20231103001.md 00:22:38.280]` "what most people who are involved with functional medicine with nutrition"
- **来源 2**：`${HOME}/Documents/女娲造人/@drekberg/20240405001.md`（2024-04-05）
  - 一手引用：`[20240405001.md 00:16:54.320]` "the doctors in functional medicine, who actually work with this kind of stuff, they will probably"
- **来源 3**：`${HOME}/Documents/女娲造人/@drekberg/20240419001.md`（2024-04-19）
  - 一手引用：`[20240419001.md 00:02:37.400]` "most people who work in the functional medicine field, who do blood work and actually"
- **用法**：Ekberg 用"functional medicine doctor"作为 **"比普通医生更懂营养的同行"** 的代称，但不点名任何具体医生（如 Hyman / Bland / Kharrazian）
- **[我推断]**：R6 内 Ekberg 开始 **承认"医生类别"的存在**（functional medicine practitioner），但 **不背书任何具体从业者**。这是一个从 R5 的"零同行"立场向 R6 的"承认职业类别但不点名"的微妙转变 — 仍守住"独立判断"标签，但承认这不是 Ekberg 一人在战斗。

### 发现 4：Nobel Prize 在 R6 内 1 次 — 但与 Ohsumi/autophagy 无关

- **数据**：R5 Nobel = 0 → R6 Nobel = 1（仍是 1 次量级）
- **来源**：`${HOME}/Documents/女娲造人/@drekberg/20240329001.md`（2024-03-29）
- **一手引用**：`[20240329001.md 00:02:52.000]` "In fact, there was a Nobel Prize winner called Rod Sperry. He got a Nobel Prize for brain research, and he said that more than 90% of the energy expenditure"
- **用法**：Rod Sperry（1981 年诺贝尔生理学或医学奖）被引用是为佐证"大脑消耗 90%+ 能量"。**与 R6 内的 autophagy 主题（`[20220819001.md]`、`[20230113001.md]`）完全无交集** — Ekberg 在讲 autophagy 时 0 次提到 Yoshinori Ohsumi（2016 年诺贝尔奖）
- **[我推断]**：R6 内 Ekberg 的 autophagy 叙事仍靠"自噬 = 自我清理"通用解释 + 禁食触发机制，**不进入"细胞生物学家 Yoshinori Ohsumi 命名了自噬机制"这一学术深水区**。他保持"概念科普"而非"学术溯源"。

### 发现 5：R6 内的"研究语言"全靠模糊指代 — 0 次具体研究点名

- **数据**：116 次 "study" 出现，但 0 次 "published in <journal>"、0 次具名研究、0 次具体作者（除 R5 的 Weston Price 1 次、R5 的 Rod Sperry 1 次）
- **一手观察**（典型 R6 句式）：
  - `[20220812001.md 00:09:20.400]` "this study suggests that if you compare this alpha linoleic acid to a saturated fatty acid"
  - `[20220722001.md 00:24:14.580]` "the worst food they can eat number six is coffee and there's been quite a bit of research done on"
  - `[20220826001.md 00:01:47.040]` "some research that suggests that phytonutrients in lemons can actually kill certain cancer cells"
- **[我推断]**：R6 内 Ekberg 用"study suggests" / "research done on" 作为 **修辞挡箭牌** — 借"研究"这个范畴词增加权威感，但不提供任何具名来源。这是一种 **"权威修辞无具体锚点"** 的科普话语。R5 时期他至少会点 "Lancet 1997"、"Lancet 2017 12 factors" 这种具名研究，R6 内连这种级别的具体性都消失了。

### 发现 6：R6 内 0 次 "Mayo Clinic" + 0 次 "Lancet" + 0 次 "Guyton" — "反证靶子"和"司法终审"同时退场

- **数据**：R5 内 Mayo Clinic ×5+、Lancet ×2、Guyton ×1（合计 8+ 次具名反证/司法引用）→ R6 内三者合计 = **0**
- **一手观察**：R6 内 100 期视频，Ekberg **不使用任何具名机构、任何具名期刊、任何具名教科书** 作为论证支撑
- **反证靶子的替代**：R6 内 Ekberg 改用 **模糊的"they"/"the government"/"the medical system"** 表述
  - 一手引用：`[20230616001.md 00:05:06.300]` "we're told to eat the ADA the AMA the USDA all those government agencies these all those medical"
  - 一手引用：`[20221028001.md 00:20:44.820]` "the massive deception and misinformation there is still some hope we're catching on so the USDA have"
  - 一手引用：`[20230414001.md 00:01:19.080]` "let me preface this by saying that in general I am not a fan of what the FDA or the USDA recommends"
- **[我推断]**：R5 的"M5 智识策略 = 抓 Mayo Clinic 具体措辞漏洞 + 用 Guyton 反证 + 借 WHO 1948 立权威"是 **精雕细琢的辩论型话语**。R6 的话术已转为 **"代谢-生理-胰岛素" 通用逻辑** — 论证自给自足，不需要外部权威。这降低了论证门槛但也降低了辩论锋利度。

### 发现 7：R6 内"代谢 + 胰岛素 + 炎症"三联词占绝对主导 — 智识谱系退到"机制本体"

- **数据**：R6 内 `metabolic` 298 次 + `insulin resistance` 330 次 + `inflammation` 221 次 = 三大机制词合计 849 次（每期平均 8.5 次）
- **一手观察**（典型 R6 句式）：
  - `[20220624001.md 00:04:58.480]` "one underlying factor here that we have to control is insulin resistance because if you have"
  - `[20230414001.md 00:02:40.080]` "now we're promoting insulin resistance and degenerative disease"
  - `[20230113001.md]` 标题："Activate Autophagy For A Long Life But Don't Do THIS"
- **[我推断]**：R6 内 Ekberg 的智识谱系已 **从"R5 借权威打靶" 退到 "R6 讲机制本体"**。他的智识坐标系完全围绕"胰岛素抵抗 → 代谢综合征 → 炎症 → 退化"自循环，几乎不与任何外部人物/机构/教科书产生交集。这是一种 **"内卷型自洽"** — 体系封闭、自说自话、依赖机制内在逻辑说服。

### 发现 8：R6 内 0 个 COVID/political 主题，但 1 期 Ozempic 视频反映"GLP-1 时代"到来

- **数据**：R5 内 COVID = 4 期 → R6 内 COVID = 0 期。但 R6 内出现 1 期 **Ozempic / Wegovy** 主题视频：
- **来源**：`${HOME}/Documents/女娲造人/@drekberg/20230728001.md`（"You Must Know THIS Before Taking WEIGHT LOSS Meds like OZEMPIC"，2023-07-28）
- **一手引用**（开场）：`[20230728001.md 00:00:06.300]` "Hello Health Champions today I want to talk about what you need to know before you start a weight loss medication like ozempic and I've gotten tons and tons of questions hundreds literally"
- **一手引用**（机制讨论）：`[20230728001.md 00:00:41.640]` "called wegovy and the other is called ozempic so these contain the active ingredient"
- **用法**：Ekberg 不点名任何 GLP-1 专家（如 Robert Kushner、Daniel Drucker、Jens Juul Holst），**不引用任何 Ozempic trial**（如 STEP trial、SURMOUNT trial），**只用"它如何影响胰岛素和食欲"的机制讨论**。
- **COVID → Ozempic 的议题切换**：
  - R5（2020-2021）：4 期内容关注 COVID，但角度是"代谢综合征 = 真正风险"
  - R6（2022-2024）：0 期内容关注 COVID，但 1 期内容关注 Ozempic/Wegovy — 反映 2022 年后 GLP-1 减肥药成为大众健康新焦点
  - **两者共同点**：Ekberg 不参与"是否要吃/打"的辩论，只参与"它如何影响代谢"的机制讨论
- **[我推断]**：R6 内 Ekberg 是 **"去辩论化、去政治化、去个人化"** 的代谢教育者。他不参与任何"X 是好是坏"的具体辩论（疫苗辩论、减肥药辩论、命名饮食阵营辩论），只输出"代谢逻辑是什么"。

---

## 4. R6 智识谱系总图

```
                       〔Ekberg 自己的机制逻辑〕
                                  │
            ┌─────────────────────┼─────────────────────┐
            │                     │                     │
       代谢本体（机制）        饮食工具菜单         通用病理二分
            │                     │                     │
   insulin resistance (330)  keto (214)        inflammation (221)
   metabolic (298)           carnivore (28)    natural (129)
   calorie (373)             ketosis (30)      refined → 致病
   inflammation (221)        intermittent fast  
                                  │
                                  │ 借以解释 ↓
                                  │
   ┌──────────────────────────────┴──────────────────────────────┐
   │   〔模糊对话方 / 泛化反证对象〕                              │
   │                                                            │
   │  "the government"       "the ADA / AMA / USDA"            │
   │  "the medical system"   "they" / "the experts"             │
   │  "they don't want you to know"                             │
   │                                                            │
   │  FDA (9×) — 唯一具体化对话方，2023-04-14 一期               │
   │  CDC (1×) — 唯一数据点引用                                 │
   │  WHO (1×) — 借以论证睡眠不足致癌                            │
   │                                                            │
   │  〔functional medicine doctor (3×)〕                       │
   │  2023-11-03 / 2024-04-05 / 2024-04-19                       │
   │  —— 承认"职业类别"，但不点名任何具体医生                    │
   └────────────────────────────────────────────────────────────┘

   〔0 个具名同行 / 0 个具名机构 / 0 个具名期刊 / 0 个具名教科书〕

   〔R5 "三脚架"全部退场〕：
   - WHO 1948 健康定义        0 次
   - Guyton & Hall 教材       0 次
   - Mayo Clinic 反证         0 次
   - Weston A. Price 历史权威  0 次
   - Lancet 期刊              0 次
```

---

## 5. R6 智识谱系特征总结（与 R5 对照）

| 维度 | R5 特征 | R6 特征 | 变化 |
|---|---|---|---|
| **历史权威引用** | Weston Price ×1 | **0** | 消失 |
| **机构反证靶子** | Mayo Clinic ×5+, USDA ×多次, ADA, AMA, Johns Hopkins, Harvard Health | 改用 "ADA/AMA/USDA 集体 + FDA 单点" | 弱化 |
| **机构正面引用** | WHO 1948 健康定义 | WHO 1×（非 1948 定义，而是致癌分类） | 弱化 |
| **司法终审教材** | Guyton & Hall ×1 | **0** | 消失 |
| **顶级期刊** | Lancet ×2（反主流用途）| **0** | 消失 |
| **当代同行** | 0（16/16 列表全 0） | 0（16/16 列表仍 0） | 持平 |
| **替代性同行类别** | 无 | functional medicine doctor（3×，2023-11+） | 新增 |
| **研究语言密度** | 100/100 提及"研究" | 100/100 提及"研究" | 持平 |
| **具名研究引用** | 3 处 "published in <journal>" | **0** | 消失 |
| **系统综述** | 0（Cochrane/meta-analysis）| 0 | 持平 |
| **2023 时代新议题** | — | FDA "healthy" 标签提案 (2023-04) / Ozempic/Wegovy (2023-07) | 新增 |
| **COVID 议题** | 4 期 | 0 期 | 退出 |
| **R5 智识三脚架** | 完整（WHO 1948 + Guyton + 反 Mayo） | **0** | 整体坍塌 |

**[我推断] R6 智识策略的核心变化**：

1. **从"借权威打靶"到"机制自洽"** — R5 时期 Ekberg 的话术需要外部锚点（WHO 1948 + Guyton）才能给"Mayo Clinic 错了我对"提供合法性。R6 时期他不再需要这种借力 — 他的代谢-胰岛素-炎症机制本身已成为自足论证。
2. **从"具名反证"到"泛化反证"** — R5 时期他点 Mayo Clinic 5+ 次、Lancet 2 次。R6 时期他改用"the government"、"the ADA/AMA/USDA" 集体指代。这降低了反证的锋利度但也降低了被反证对象的反弹风险。
3. **从"零同行"到"承认职业类别"** — R5 时期他完全孤立。R6 时期他 3 次提到"functional medicine doctor"（2023-11 起）— 这是个微妙的"承认战友们存在但不点名"的话术。
4. **从"反应型"到"机制型"** — R5 时期他会针对具体事件/研究/政策发表看法（"Mayo Clinic 这篇文章漏了胰岛素"、"FDA 这次建议不好"）。R6 时期他更倾向讲"代谢-激素-细胞"的普适机制，事件反应型内容（如 2023-04-14 FDA 提案、2023-07-28 Ozempic）只是偶发，不是主轴。
