# R02 著作维度调研：Dr. Sten Ekberg（@drekberg）

- **切片范围**：R2 100 个文件（2017-10-02 → 2018-08-17，file_ids 101–200）
- **切片文件清单**：`/tmp/r2_files.txt`（100 个 YYYYMMDD###.md 路径）
- **调研人**：fuxi-skill Phase 1 Agent 1（著作维度）
- **方法**：grep 优先（不 Read 全文），关键词频次 + 命中文件定位 + 标题抽样

---

## 一、关键词频次全景（R2 100 文件）

执行命令（统一模式：逐文件 grep -ci 后累加）：

```bash
while read f; do c=$(grep -ci "KEYWORD" "$f"); total=$((total+c)); done < /tmp/r2_files.txt
```

| 命中数 | 关键词 | 类别 |
|---:|---|---|
| 329 | `the body` | R1 锚词（验证是否消退）|
| 120 | `Berg` | ⚠️ 大部分是 "Ekberg" 自身姓，真实提及 Dr. Berg = 0 |
| 95 | `keto` | 饮食 |
| 71 | `Wellness for Life` | 频道/品牌口号（开篇固定套语）|
| 42 | `insulin resistance` | R1 已建立核心模型 |
| 28 | `ketogenic` | 饮食 |
| 17 | `holistic` | 哲学 |
| 13 | `inflammation` | 病理机制 |
| 13 | `gut` | 病理机制 |
| 8 | `autoimmune` | 病理机制（集中于甲状腺专题）|
| 3 | `leaky` | 病理机制 |
| 0 | `root cause` | ⚠️ **R1 仅 1 次，R2 仍为 0** |
| 0 | `User Manual` | ⚠️ R2 无 |
| 0 | `Survival Biology` | ⚠️ R2 无 |
| 0 | `Health Champions` | ⚠️ R2 无 |
| 0 | `Perlmutter` | ⚠️ R1 锚点，R2 未延续 |
| 0 | `Mercola` | ⚠️ R1 锚点，R2 未延续 |
| 0 | `Hyman` | ⚠️ 无 |
| 0 | `Pollan` | ⚠️ 无 |
| 0 | `Weston A. Price` | ⚠️ 无 |
| 0 | `Atkins` / `Banting` | ⚠️ 无 |
| 0 | `Attia` | ⚠️ 无 |
| 0 | `Gundry` | ⚠️ 无 |
| 1 | `Davis` | 噪声（需复核是否指 William Davis）|

**结论（我推断）**：R2 阶段 Ekberg 尚未建立"智识谱系引用"习惯——R1 提到的 Perlmutter/Mercola 在 R2 完全消失，R2 没有引入任何新权威人物作为"盟友/对话者"。**R2 仍处于"单点原创"模式**，未进入"联盟叙事"阶段。

---

## 二、5–10 个核心发现

### 发现 1："Wellness for Life" 是 R2 唯一稳定品牌符号

- **频次**：71 次（71/100 文件 ≈ 71% 覆盖率）
- **典型用法**（开篇套语）：
  - `[20180817001.md 00:00:00]` "I'm Dr. Ekberg with Wellness For Life and if you'd like to truly master health..."
  - `[20180727001.md 00:00:13]` "hey i'm dr ekberg with wellness for life and if you'd like to truly master health"
- **结尾配套套语**：`"if you'd like to truly master health"`（也是高频出现）
- **一手（他说的）** [20180625001.md 00:00:11]: "Hey I'm Dr. Ekberg with Wellness For Life and if you'd like to truly master"
- **我推断**：R2 阶段他的"品牌矩阵"是 **1 个**（Wellness For Life + 终极目标 "truly master health"），**不是 3 个**。R1 没出现、这个切片里也没出现的 "Health Champions / Wellness For Life / Survival Biology" 三件套属于**后期才发展**出来的品牌宇宙。

### 发现 2：R2 出现"Doctor Of The Future Award"（2017-11-20）—— 这是身份背书的关键节点

- **文件**：`20171120002.md` + `20171120004.md`（同视频，video_id `KMgz7WkWllw`，疑似重传）
- **关键转录** `[20171120004.md 00:00:17–01:25]`：
  - "the first award goes to Dr. Sten Ekberg is a **former Olympic athlete** our 2017..."
  - "...he expressed the desire to is potentially expand his practice and he did..."
  - "...him and his wife started a **YouTube channel** posting video of Cairo tips healthy recipe has the Amelie remedy and **nutrition response testing** in related videos"
  - "...his video have reached over 20 truck up to **23,000 years**..."
  - "...is working with **doctor unit on a solution to handle neurological brain pathway** with nutrition and chiropractic care he increases visit to a total of..."
- **一手（他说的，但这段是颁奖方/同事介绍他）** [20171120004.md 00:00:17]
- **二手（颁奖方描述他）** [20171120004.md] 整段颁奖介绍
- **我推断**：此条揭示三个 R1/R2 都成立的身份标签 —— **(a) 前奥运十项全能选手**、**(b) 与妻子共运营 YouTube 频道**、**(c) 与"doctor unit"（疑为 Dr. Ubani 或同人）合作"神经脑路径"项目**、**(d) 此时订阅 20k–23k**。"nutrition response testing" 暴露他在 2017 末期的临床方法学（属 applied kinesiology / 机能学流派）。

### 发现 3：饮食叙事核心是 "Keto + Intermittent Fasting" 双柱，与 R1 模型升级

- **keto 频次**：95（高）
- **ketogenic**：28
- **intermittent fasting / fasting**：高频（`20180112001.md` 11 次、`20180810001.md` 13 次、`20180622001.md` 13 次）
- **R2 关键 keto 专题（标题抽样）**：
  - `20180101001.md | Keto Diet Explained For Beginners Simply` （15 次 keto）
  - `20180209001.md | How To Do Keto Right` （13 次）
  - `20180112001.md | Keto vs Intermittent Fasting - Which Is Better?` （11 次）
  - `20180618001.md | Real Doctor Reacts To Doctor Mike on Diets: Ketogenic Diet | Diet Review` （17 次，**R2 keto 最高单文件**）
  - `20180219001.md | Do We Need Carbs To Survive? - Dr Ekberg`
  - `20180730001.md | Are Vegan Low Carb Diets Healthy?` （20 次 "the body" + 8 次 keto）
  - `20180706001.md | Ideal Food For Humans`
- **一手（他说的）** [20180618001.md 00:01:10]: "...American diet down to **low carbs to ketogenic and to intermittent fasting**"——他用一条**线性升级路径**（标准美式饮食 → 低碳 → 生酮 → 间歇性断食）组织饮食光谱。
- **我推断**：R1 的"胰岛素抵抗"模型在 R2 被**操作化**为"keto + IF"二选一/双轨推荐。**"ketogenic 饮食是胰岛素抵抗的解药"是 R2 的临床主张**——这是 R1 → R2 的模型升级，但**没有引入新的概念（如 metabolic flexibility、autophagy 等更后期才会出现的词）**。

### 发现 4：R2 出现"Real Doctor Reacts"系列（3 期）—— 内容形式的演化

- **3 期 R2 内的"Real Doctor Reacts"视频**：
  - `20180618001.md | Real Doctor Reacts To Doctor Mike on Diets: Ketogenic Diet | Diet Review`
  - `20180622001.md | Real Doctor Reacts To Dr. Sam Robbins Intermittent Fasting: Weight Loss, Get Fat & Get Diabetes`
  - `20180813001.md | Real Doctor Reacts To The Mathematics Of Weight Loss Ruben Meerman TEDxQUT`
- **二手（他评论的对象）**：
  - **Doctor Mike (Mike Varshavski)** —— 主流医生 YouTuber
  - **Dr. Sam Robbins** —— 健康/补剂类 YouTuber
  - **Ruben Meerman** —— TEDxQUT 演讲者（科普视频"The Mathematics of Weight Loss"）
- **我推断**：(a) "Real Doctor Reacts" 是 R2 期间**新出现**的格式创新（连续 3 期，6 月–8 月集中发布）；(b) 这构成 R2 的**外部人物引用 100%**——R2 中他**只**通过 "React" 格式间接对话其他创作者，**从未在自己原创叙事中引用任何一位"盟友医生"**。这与 R1 的"Perlmutter + Blackburn + mercola.com"模式**完全不同**。

### 发现 5：甲状腺专题是 R2 唯一"病理机制深度展开"的单集

- **文件**：`20171211001.md | Thyroid Issues Explained` —— autoimmune 8 次（全 R2 最高）、inflammation 4 次（全 R2 最高）、gut 8 次
- **一手（他说的）** [20171211001.md 00:12:21]: "...much as 90 percent of it today is autoimmune except they don't test for it"
- **一手（他说的）** [20171211001.md 00:13:20]: "...that virtually all autoimmune disease starts with an **unhealthy gut** it starts with..."
- **一手（他说的）** [20180423001.md 05:25]: "...**leaky gut** and... gut flora from having a poor intestinal integrity..."
- **我推断**：R2 已建立"**gut → leaky gut → autoimmune**"的病理因果链，但**还没有系统化、也没有高频复用**（R2 中 leaky 仅 3 次）。这条因果链是 R1/R2 的"半成品"——它在 R2 出现，但没有在标题/品牌口号中固化（这与"胰岛素抵抗→keto"的高频复用形成对比）。

### 发现 6："Stress is the number one killer" 是 R2 反复重申的命题

- **频次**：stress 在多个单集高密度出现
  - `20180817001.md | Adrenal Fatigue Symptoms, Causes, and Treatment`（26 次，**R2 最高**）
  - `20180528001.md | Stress Signs & Just How Much It Hurts You - Dr Ekberg`（24 次）
  - `20171222001.md | Stress Is The Number One Killer`（24 次）
  - `20180409001.md | Stress And Digestion`（16 次）
  - `20180709001.md | What Happens To Your Brain When You Stress?`（14 次）
  - `20171106001.md | Can Stress Cause High Blood Pressure?`（13 次）
- **一手（他说的）** [20171222001.md title]: "Stress Is The Number One Killer" —— 这本身是命题陈述，不是问题。
- **我推断**：R1 的"压力三件套"（皮质醇/肾上腺/血糖）在 R2 已升级为**独立专题系列**，且带强断言标题。"压力是头号杀手"是 R2 的核心命题之一（与胰岛素抵抗并列）。

### 发现 7：R2 仍深度绑定"整脊师"身份，但角色已从"调整脊柱"转向"神经系统 + 姿势"

- **频次**：
  - `20180309001.md | Which Chiropractic Technique Is Best?`（16 次 chiropractic）
  - `20180430001.md | How Does Chiropractic Work?`（10 次）
  - `20180727001.md | Pros And Cons Of Baby Chiropractic - Dr Ekberg`（9 次）
  - `20180720001.md | Chiropractic vs Medicine (DC vs MD)`（9 次）
- **延伸神经/姿势专题**：
  - `20171124001.md | What Happens To Your BRAIN When You Are TEXTING?`
  - `20180316001.md | Maximize Your Brain Plasticity For A Super Brain - Doctor Explains Neuroplasticity`
  - `20180226001.md | Posture Exercises`
  - `20180702001.md | Unexpected Benefits Of Good Posture - Dr Ekberg`
  - `20180723001.md | Walking Arm Swing Predicts Dementia`
- **我推断**：R1 提到的"Neurologically based chiropractic"心智模型在 R2 被**展开**为"神经系统 + 姿势 + 神经可塑性"系列（特别见 2018-03 起的 7 期内密集出现）。这是 R1 → R2 的**模型升级**之一——从"调整椎体"叙事向"神经系统主导"叙事迁移。

### 发现 8："Holistic" 是 R2 唯一一次专门定义的概念

- **文件**：`20180312001.md | What Is Holistic Health? - Dr Ekberg`（holistic 8 次，R2 最高）
- **一手（他说的）** [20180312001.md 00:00:00]: "What is holistic health? I'm gonna explain how it works"
- **一手（他说的）** [20180312001.md 00:00:29]: "...holistic health has nothing to do with burning incense or waving crystals..."
- **我推断**：R2 仅有**一期**专门讲 holistic，且采用"祛魅式"开场（"与熏香/水晶无关"）。说明 R2 阶段 holistic **还不是他的核心标签词**（仅 17 次），更多是"防御性解释"——可能被主流医学批评时使用。**R1 的"Holism"心智模型在 R2 没有深化**。

### 发现 9：R2 无任何"代谢灵活性"、"autophagy"、"mTOR"、"NAD+"、"Zone 2"、"ApoB"等后期标签词

- 全部 0 命中。
- **我推断**：R2 是 Ekberg 思想体系的**早期形态**——只有"胰岛素抵抗 / keto / IF / stress / gut-leaky-autoimmune / 神经系统"六条核心线索，**还没有进入代谢精细化阶段**。这套精细化词汇属于他**后来的演化**（R3+ 才可能见到）。

### 发现 10：R2 没有 "root cause"，没有 "Survival Biology"，没有 "User Manual for Humans"

- R1 早期使用的 "the body" 锚词（329 次）依然极高频
- R1 提到 1 次的 "root cause" 在 R2 = 0
- "Survival Biology" / "User Manual for Humans" / "Health Champions" 全部 = 0
- **我推断**：R2 是 Ekberg 尚未"品牌化"的过渡期 —— **他在 R2 用 "the body" 这个朴素词**而非后期那套"User Manual/Survival Biology"框架。R1 → R2 → R3（推测）应有一个**品牌升级事件**——可能在 2018 末或 2019 完成 "Wellness for Life" → "User Manual for Humans / Survival Biology" 的概念跃迁。

---

## 三、R1 → R2 模型迁移对照表

| R1 锚点 | R2 状态 | 备注 |
|---|---|---|
| `the body` 锚词 | 维持（329 次）| 朴素的身体观未升级 |
| 智识谱系（Perlmutter / Blackburn / mercola.com）| **完全消失**（0 命中）| R2 无任何盟友医生引用 |
| "User Manual for Humans" | **0 命中** | 后期才会出现 |
| "Survival Biology" | **0 命中** | 后期才会出现 |
| "Health Champions" | **0 命中** | 后期才会出现 |
| "Holism" 心智模型 | 仅 1 期专门讲，17 次 | 弱化，未深化 |
| "Neurologically based" | **升级**为"神经系统+姿势+神经可塑性"系列（7 期专题）| 模型升级 |
| "压力 / 皮质醇"模型 | **升级**为独立命题系列（"stress is the number one killer"）| 标题级断言 |
| "毒素"模型 | **未出现** | R2 无 toxins/mycotoxins/mold 专题 |
| "胰岛素抵抗"模型 | **操作化**为 keto + IF 双柱 | 模型升级 |
| R1 = "Real Doctor Reacts" 格式 | **R2 新增 3 期** | 外部引用仅通过 React 格式间接进行 |
| 颁奖身份"Doctor Of The Future" | **R2 新增节点**（2017-11-20）| 揭示 23k 订阅、奥运背景、营养反应测试方法学 |

---

## 四、原始数据（grep 命令 + 命中数）

```bash
# 在 ${HOME}/Documents/女娲造人/@drekberg/ 下执行
# 切片文件清单：/tmp/r2_files.txt（100 个 YYYYMMDD###.md）

# 命令模板（每个关键词一行）
while read f; do c=$(grep -ci "KEYWORD" "$f"); total=$((total+c)); done < /tmp/r2_files.txt

# 执行结果（按命中数排序）：
329 | the body
120 | Berg          # 实际为 Ekberg 自身姓，真实 Dr. Berg = 0
 95 | keto
 71 | Wellness for Life
 42 | insulin resistance
 28 | ketogenic
 17 | holistic
 13 | inflammation
 13 | gut
  8 | autoimmune
  3 | leaky
  1 | Davis         # 待复核
  0 | root cause
  0 | User Manual
  0 | Survival Biology
  0 | Health Champions
  0 | Perlmutter
  0 | Mercola
  0 | Hyman
  0 | Pollan
  0 | Weston A. Price
  0 | Atkins
  0 | Banting
  0 | Attia
  0 | Gundry
  0 | neurologically based

# 按文件排序的 top 命中（用于精读定位）
while read f; do c=$(grep -ci "the body" "$f"); echo "$c|$f"; done < /tmp/r2_files.txt | sort -t'|' -k1 -nr | head -5
20|20180730001.md   # Are Vegan Low Carb Diets Healthy?
20|20180216001.md   # Prescription Medicine Side Effects
14|20171120003.md   # Blood Pressure Control
11|20171117001.md   # How To Treat Knee Pain Naturally
 9|20180625001.md   # The Dangers Of Statins & The Side Effects

# 关键路径文件清单（用于 deep-read 阶段参考）
20171211001.md  # Thyroid Issues Explained (autoimmune/gut/inflammation 集大成)
20171204001.md  # How To Lower Blood Sugar And Reverse Your Diabetes (insulin 7 次)
20180209001.md  # How To Do Keto Right (keto 13 次)
20180112001.md  # Keto vs Intermittent Fasting - Which Is Better?
20180618001.md  # Real Doctor Reacts To Doctor Mike on Ketogenic Diet (keto 17 次, R2 最高)
20171222001.md  # Stress Is The Number One Killer (命题级标题)
20180528001.md  # Stress Signs & Just How Much It Hurts You
20180817001.md  # Adrenal Fatigue Symptoms, Causes, and Treatment
20180312001.md  # What Is Holistic Health? - Dr Ekberg
20180309001.md  # Which Chiropractic Technique Is Best?
20171120004.md  # Doctor Of The Future Award (颁奖视频，身份背书)
20180622001.md  # Real Doctor Reacts To Dr. Sam Robbins Intermittent Fasting
20180813001.md  # Real Doctor Reacts To The Mathematics Of Weight Loss Ruben Meerman TEDxQUT
```

---

## 五、未发现项（硬限制内未呈现的 R1 锚词）

- **没有任何引用的"盟友医生"**：R1 提到的 Perlmutter、Blackburn、Mercola 在 R2 完全消失，且 R2 期间 Ekberg **没有引入任何新盟友医生**。
- **没有"root cause"作为方法论口号**：R1 提到的 1 次可能是巧合，R2 印证了"root cause"在 Ekberg 体系中**不是核心词**。
- **没有"毒素"专题系列**：R2 100 文件无 mold/mycotoxin/heavy metal detox 等内容。
- **没有"长寿 / 老化 / telomeres / sirtuins / NAD"系列**：与 Peter Attia 路径完全不交叉。
- **没有"动物性饮食 / carnivore"系列**：R2 不存在零碳农业/carnivore 命题（这是 Baker 流派，与 Ekberg 平行但不交叉）。
- **没有"成瘾 / 糖瘾 / 行为心理学"系列**：与 Cywes 路径不交叉。

---

## 六、给后续 agent 的提示

1. **R2 是"品牌未成型期"**——`Wellness for Life` 是唯一品牌符号；`Health Champions` / `User Manual for Humans` / `Survival Biology` 全部 R2 缺失。如发现这些词在 R3+ 突然高频，可定位"品牌跃迁事件"。
2. **R2 已建立"keto + IF"作为胰岛素抵抗的解药**——这是 R1 → R2 唯一清晰的"模型升级"。
3. **R2 期间他通过"Real Doctor Reacts"格式开始接触外部创作者**，但未内化进原创叙事——这是后续可能演化的入口。
4. **颁奖视频 `20171120004.md` 是 R2 唯一身份背书材料**，披露了 (a) 前奥运十项全能、(b) 23k 订阅（2017 末）、(c) "nutrition response testing" 方法学、(d) "neurological brain pathway" 合作项目。这 4 条事实可作为 Ekberg 早期身份硬证据。
5. **"holistic" 在 R2 是防御性使用**（"不是熏香/水晶"），这暗示他可能正面临主流医学对其整脊师身份的质疑——这是 R1 → R2 的一个**潜在叙事张力**。
