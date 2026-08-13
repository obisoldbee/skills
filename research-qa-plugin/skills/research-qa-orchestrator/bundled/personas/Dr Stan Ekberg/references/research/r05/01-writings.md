# R05 著作维度（2020-07-24 → 2022-06-10，100 文件）

> Phase 1 Agent 1 — fuxi-skill Dr. Sten Ekberg distillation, writings slice
> 切片范围：`/tmp/r5_files.txt`（R5 第 401-500 个 YYYYMMDD 命名 .md 文件）
> 全部为 YouTube 视频自动字幕 VTT 转写，无外部著作/书籍/博客文章。100% 内容载体 = 100 期 YouTube 视频字幕。

---

## 0. 元数据

- **跨度**：2020-07-24 → 2022-06-10 = 23 个月（≈115 周）
- **100 个文件** = **100 期独立 YouTube 视频**
- **未发现任何博客文章、独立著作、长文 PDF、播客节目或小册子**。`book=37` 命中绝大多数是 `of course` 的英文误报，唯一真命中是 1 处在视频里"提到一本别人的书"，未见任何"我写了这本书/这本书马上出版"表述。
- **未发现：Survival Biology / Ulite / Uveia / Nexus / Wellness For Life / beef salt water / animal-based / extended fasting / multi-day fasting / prolonged fasting** 全部 0 命中。
- **唯一广告/CTA 类短视频**：2020-11-22 "Get Healthy Naturally" 纯频道宣传片 29 行（其余 99 期均为完整讲座视频）。

---

## 1. Grep 命令 + 命中数（核心查询）

```bash
cd ${HOME}/Documents/女娲造人/@drekberg/
# 命令模板
grep -c "<kw>" $(cat /tmp/r5_files.txt) 2>/dev/null | awk -F: '{s+=$2} END {print s}'
```

| 关键词 | 命中数（次） | 出现该词的文件数 |
|---|---|---|
| Health Champions | 85 | 85（几乎每期片头招呼语）|
| carnivore | 39 | 9 |
| autophagy | 91 | （未单独统计文件数，密度 Top5：20210723=15, 20200731=15, 20211015=10, 20220506=8, 20220311=8）|
| fasting | 324 | （最高频词）|
| intermittent | 99 | |
| keto | 227 | |
| insulin resistance | 266 | |
| blood sugar | 291 | |
| gut | 134 | |
| leaky | 35 | |
| autoimmune | 27 | |
| ketogenic | 32 | |
| resveratrol | 3 | 1（20201023）|
| sirtuin | 3 | 1（20201218）|
| NAD+ / NAD plus | 0（`NAD+` 字符串）/ `NAD plus`/`NAD` 多次 | 0/（深挖 20201218 Wim Hof 与 20210730 Aging）|
| NMN | 1 | 1（20210730 Aging）|
| longevity | 12 | |
| epigenetic | 10 | 1（20210528 Belly Fat Mistakes）|
| mitochondri(a) | 22 | |
| dopamine | 4 | |
| Olympic / decathlon | 35 | （开场招呼语"holistic doctor and a former Olympic decathlete"在 R5 中至少出现 24 次）|
| Sweden / Swedish | 10 / 0 | 散布（pizza salad, crayfish, krusbär 等饮食文化点缀，无 R4 那种反 lockdown 政治化论述）|
| COVID / coronavirus | 0 字符串 / 1+ | 1-2 期（20200724 标题明示；中后期未持续）|
| vaccine / vaccination | 1 / 0 | （R4 的 9+ 期 COVID 锋面在 R5 大幅消退）|
| lockdown | 2 | （零星提及，非主轴）|
| book | 37（几乎全为 "of course" 误报） | 0 自传/书出版 |
| podcast / new show / live stream / membership / course | 0 / 0 / 0 / 1 / 207（`course` 多为"of course"）| 0 |
| community | 7 | 零星 |
| Ulite / Uveia / Nexus | 0 | 0（R5 中这三个产品名完全缺席）|
| Survival Biology | 0（字符串）/ 1（语义相关：20211015 "Fasting For Survival"） | 0/1 |

---

## 2. 关键发现（10 条，按权重排序）

### 发现 1（**【一手】**）：R5 的核心主轴是 **fasting（断食）+ insulin resistance（胰岛素抵抗）**，不是 longevity / carnivore

- **fasting=324、insulin resistance=266、keto=227、blood sugar=291、autophagy=91、intermittent=99**
- 单期视频平均 3-5 个核心词同时出现。
- **R4 预告的"抗衰老第二阶段"并未在 R5 成为主轴**。longevity 仅 12 命中、epigenetic 10 命中、NAD+/sirtuin 仅各 1 期。Sirtuin/NAD/resveratrol 的"集中科普"集中在两期：
  - **20201218 "What Happens During Wim Hof Breathing?"**（`[20201218001.md 00:17:17] you activate survival circuits you have sirtuins to have survival genes`，`[00:17:25] sirtuins to have survival genes and if you expose your body to something harsh`）【一手】
  - **20210730 "Your Doctor Is Wrong About Aging"**（`[00:26:10] up regulates these genes is something called NAD, nicotinamide adenine dinucleotide`，`[00:26:18] supplements called NR and NMN`）【一手】
  - **20201023 "Top 10 Worst Foods Doctors Tell You To Eat"**（resveratrol 3 命中；`[00:21:13] resveratrol and this has been linked to various different health benefits`）【一手】
- **[我推断]**：R4 把 longevity 抬到"第二阶段"开题后，R5 **没有扩成连续系列**。抗衰老话题被打散成两期 "Wim Hof"（2020-12）与 "Your Doctor Is Wrong About Aging"（2021-07），中间被 fasting / keto / insulin resistance 主轴完全压过。可能的解释：R5 跨越的 23 个月里，Ekberg 的算法/观众反馈表明 fasting+keto+IR 流量优于 longevity 深度长文，所以他没把 longevity 做成"主菜单"。

### 发现 2（**【一手】**）：R5 出现一个 **"What If You Stop X For 30 Days?" 极限实验系列** —— 这是 R4 没有的节目格式

R5 中明确以 "What If You X For 30 Days" 为标题的视频至少 6 期：
- 20211008 "What If You Stop Eating **Sugar** For 30 Days?"
- 20211119 "What If You Stop Eating **Breakfast** For 30 Days?"
- 20211224 "What If You Stop Eating **Bread** For 30 Days?"
- 20220114 "What If You Only **Ate Once A Day** For 30 Days?"
- 20220211 "What If You Only Eat **Fruit** For 30 Days?"
- 20220325 "What If You Ate **Only Meat** For 30 Days?"（**carnivore 主轴唯一专题**）
- 20220506 "What Happens If You Don't Eat For 3 Days?"（30 天系列的延伸变体：3 天 / 5 天）
- 20210723 "What Happens If You Don't Eat For 5 Days?"
- 20220610 "What If You Eat **BACON** Every Day For 30 Days?"

**[我推断]**：这是 R4 → R5 之间 Ekberg **节目格式的一次升级**。R4 几乎全是 "Top 10..."、"What Happens When You..."、"Your Doctor Is Wrong About..." 三种模板。R5 引入 "What If You X 30 Days" 极限实验模板，**作为"carnivore 是否值得做"的实操钩子**——把抽象的宏量营养争论转译成"我陪你 30 天"的承诺。20220325 carnivore 30 天 + 20220610 bacon 30 天 = 这个节目公式在 R5 末尾的两次高密度收尾。

### 发现 3（**【一手】**）：R5 出现 **"Your Doctor Is Wrong About X" 系列**——R4 模板的延续与扩展

- 20210312 "Your Doctor Is Wrong About **Blood Sugar & Fasting**"
- 20210507 "Your Doctor Is Wrong About **Cholesterol**"
- 20210618 "Your Doctor Is Wrong About **Insulin Resistance**"
- 20210903 "Your Doctor Is Wrong About **Weight Loss**"
- 20210730 "Your Doctor Is Wrong About **Aging**"（含 NAD/NMN/NR/resveratrol/sirtuin 集中阐述）
- 20210312 也有 1 命中 NMN 上下文（[00:26:18]）

**[我推断]**：这条线显示 Ekberg 在 R5 把"反驳医生"系列扩展到 **aging** 维度（R4 主轴在 blood sugar / diabetes / insulin），但仅 1 期，未做成 longevity 主线。

### 发现 4（**【一手】**）：**R5 验证：Health Champions 品牌定型 100% 锁定**

- 85 / 100 文件片头招呼语 = "Hello Health Champions" 或 "Hello health champions."
- 开场签名 24/100 期包含"holistic doctor and a former Olympic decathlete"双标签。
- **唯一例外**：2020-11-22 的 29 行短片 "Get Healthy Naturally" 用 "Hello I'm Dr Ekberg" 而非 "Hello Health Champions"——这是频道宣传片而非内容视频，确认品牌定型。
- 健身自传身份（Olympic decathlete）的可见度：35 次 "Olympic" 命中、10 次 "Sweden"（多为饮食文化点缀，如"pizza salad"、crayfish、gooseberry/krusbär）。

**[我推断]**：R4 (2019-12-27) 定型后，**R5 23 个月内 85% 视频保持品牌一致**，开场脚本的稳定性 = Ekberg 团队已有"模板化生产"流程。

### 发现 5（**【一手】**）：**carnivore 从 R4 的"次要"升至 R5 的"边缘实验主题"，但未进入主菜单**

- **9 / 100 文件出现 carnivore 关键词**（vs R4 的 8 文件，R5 几乎持平）
- carnivore 关键词首次出现：**2020-09-11、2020-09-18**（R4 末期，R5 起点）
- carnivore 关键词出现密度 Top 3：
  - 20220325 "What If You Ate Only Meat For 30 Days?"= **23 命中**（R5 单期最高）
  - 20210709 "Top 10 Foods High In Protein" = 5 命中（protein/carnivore 上下文）
  - 20210820 "Fake Burger: Better Than Meat & Saves The Planet?" = 2 命中
- **carnivore 命中 23 次的 20220325 是 R5 carnivore 内容的总集**：`[00:00:00] What would happen if you only ate meat for 30 days? Well there is this thing called a carnivore diet`，并系统化回答"营养是否够（thiamin 60%、Mg 75%、Fe 200%、Vit C 30%）"+"为什么够（葡萄糖减少→营养吸收效率提升）"+"RDA 是基于小鼠合成物"+"临时 vs 长期"四问。
- **R4 2020-07-03 抗衰老开题 + R4 8 期 carnivore 抬升**的预期，**R5 没有兑现为"carnivore 主轴化"**。Carnivore 始终是"30 天实验"框架下的一个应用题，不构成 R5 的核心叙事。

### 发现 6（**【一手】**）：**R5 personal experience 维度停留在 R4 三段弧（athlete → sugar → recovery），未展开"健康危机"**

R5 中个人史片段（皆在视频中口述，**不是自传文章**）：
- 2020-07-24 COVID 片：开篇延续"holistic doctor + Olympic decathlete"标签
- 2020-11-22 频道宣传片："once you understand how much power you have over your health you will become excited about the possibilities and then when you make a decision to do something about it you become a health champion" — **未给具体病史，仅给身份转化叙事**
- 2021-08-20 Fake Burger：`[00:05:27] a lot of garbage when I was an athlete and it came back to bite me I ate pizza and ice`（R4 三段弧的复读：运动员期垃圾饮食→3% 体脂率）
- 2021-02-26 Mexicans Were Skinny：未涉个人史
- 2021-11-19 No Breakfast for 30 Days：`[00:12:16] I first came to the US I was surprised to find that potato chips was promoted as food`（R4 移民美国饮食震惊点）
- 2020-08-21 Apple Cider Vinegar：`[00:10:42] oh I was baking but it didn't have any sugar because I only used dates and raisins`（健康期替代糖）
- 2021-10-08 No Sugar 30 Days：`[00:21:58] stuff if I can help it I had a diet soda about 40 years ago and I've never had one since because`（R4 时代已定型）

**【我推断】**：R5 期间 Ekberg **没有把"健康危机"展开成新章节**。他的个人故事仍是 R4 的三段弧：运动员期垃圾饮食 → 觉醒 → 推荐 keto+fasting。R4 末期 2019-12-27 Health Champions 品牌定型后，R5 23 个月他没添新章节（无新"我得了 X 病"叙事，无新"我父亲/母亲的故事"展开）。

### 发现 7（**【一手】**）：**COVID 锋面在 R5 急剧消退——从 R4 的 9+ 期到 R5 的 1-2 期**

- 2020-07-24 "Coronavirus Is Getting Worse - Here Is What You MUST Do!"（R5 起点唯一明确 COVID 视频）
- 中后期零星"COVID" "lockdown" "vaccine" 命中，**不构成节目格式**
- Sweden 反 lockdown 政治化叙述在 R5 **几乎完全消失**（Sweden=10 命中全为饮食文化点缀：pizza salad、crayfish、gooseberry）

**[我推断]**：Ekberg 在 R5 期间选择**不把 COVID/vaccine/Sweden 当作主菜单**。这与 R4（2019-12 → 2020-07）的 9+ 期 COVID 锋面形成鲜明对比。可能原因：R5 跨越 Delta + Omicron 全程，他选择"退后一步"做 fasting+keto 长尾内容，避免频道定位被 pandemic 政治化裹挟。

### 发现 8（**【一手】**）：**"Sugar addiction" 在 R5 成为"机制层"科普——从 R4 框架到 R5 机制深挖**

- 关键命中：
  - 2020-10-30 "What Happens When You Eat Sugar?"（sugar 主轴首期）
  - 2021-10-08 "What If You Stop Eating Sugar For 30 Days?"
  - 2021-11-19 "What If You Stop Eating Breakfast For 30 Days?"
  - 2021-12-24 "What If You Stop Eating Bread For 30 Days?"
- "addiction" 关键词：~10+ 命中贯穿全期，集中在 sugar / bread / breakfast 主题
- "dopamine" 仅 4 命中（说明 Ekberg 不滥用 neurochemistry 术语，但会用"junkies getting our fix"等通俗化框架）

**[我推断]**：R4 sugar addiction 框架在 R5 演化为"30 天戒断挑战"的实操公式——把"为什么会成瘾"机制科普（dopamine/reward pathway）拆到几期独立视频里。这是 R4 → R5 节目格式的二次升级（从"What is X" 框架 → "30 days without X" 框架）。

### 发现 9（**【一手】**）：**R5 出现一个重要"被边缘化"主题：Wim Hof / 冷暴露 / 呼吸法**

- 2020-12-18 "What Happens During Wim Hof Breathing?"（sirtuin 唯一深度出现期）
- 2021-11-26 "Cold Hands And Feet - Should You Worry?"（非 Wim Hof 但冷相关）
- "Wim Hof" 字符串 0 命中（除该期标题外几乎不引用 Wim Hof 本人）

**[我推断]**：Ekberg 在 R4 末-R5 初有把 Wim Hof / 冷暴露纳入主菜单的迹象（sirtuin + survival genes 的引入），但 2020-12 之后**没有继续扩展**为"cold exposure 系列"。这与 carnivore 一样，是 R4 末"开题但未深挖"的子主题之一。

### 发现 10（**【一手】+ 【我推断】**）：**R5 中段（2021 末-2022 初）未见"extended fasting / multi-day fasting"专题化**

- 关键词精确字符串 `extended fasting` 仅 1 命中（2020-08-07 "What Happens When You Fast?"），`multi-day fasting` 0 命中，`prolonged fasting` 0 命中
- 但 30 天 / 5 天 / 3 天断食的"极限实验"系列（发现 2）在 R5 末尾 2021-07-23 (5 天)、2022-05-06 (3 天) 有两期集中
- **[我推断]**：R5 **没有出现"multi-day extended fasting"专题系列**，但通过 5 天 / 3 天 / 30 天不同 duration 的极限实验视频，**隐性打开了 multi-day 断食的入口**。R6-R8 阶段这个主题可能升格为新主菜单（待后续 R 阶段验证）。

---

## 3. R4 → R5 验证表（10 项 R4 假设）

| R4 假设 | R5 验证结果 | 证据 |
|---|---|---|
| Health Champions 品牌定型 | **完全锁定（85/100 期统一招呼）** | 命中 85 次 |
| 抗衰老第二阶段深挖 NAD+/NMN/resveratrol/雷帕霉素 | **未深挖，零散在 2 期** | sirtuin 仅 20201218, NAD+/NMN 仅 20210730, resveratrol 仅 20201023, 雷帕霉素 0 命中 |
| R4 8 期 carnivore 抬升 → R5 进主轴 | **未进主轴，仅 1 期专题**（20220325, 23 命中）| 9/100 文件出现 |
| R4 4 期 sugar addiction → R5 高频化 | **机制化 + 30 天挑战化** | 20211008 戒糖 + 20211119 戒早餐 + 20211224 戒面包 |
| R4 9+ 期 COVID → R5 持续 | **急剧消退（仅 1-2 期零星）** | 20200724 唯一标题明示 |
| R4 Sweden 反 lockdown → R5 政治化 | **完全退出政治面，Sweden 仅作饮食文化** | Sweden=10 全为饮食 |
| R4 personal experience 三段弧 → R5 展开健康危机 | **未展开，仍停留三段弧** | personal 12 命中 |
| R5 中段可能出现 extended fasting | **未专题化** | 关键词 0 命中 |
| R5 23 个月跨度核心节点 | **三个节目格式拐点**：20210312 ("Your Doctor is Wrong" 系列化) + 20210723 (5 天断食) + 20211008 ("What If You X 30 Days" 系列化) | |
| R5 可能新主轴 | **"What If You X 30 Days" 极限实验系列** | 6+ 期同名模板 |

---

## 4. R5 内容主题全图（100 期标题，顺序呈现 23 个月的演化）

### 2020 H2（7-12 月，20 期）：**fasting / keto / IR 主菜单奠基 + COVID 收尾 + 频道宣传**

```
20200724 COVID
20200731-20201016 集中: intermittent fasting / keto / fasting vs eating less / ketosis / ACV
20201030 What Happens When You Eat Sugar?
20201106-20201120 减脂方法论（calorie density diet vs keto）
20201122 频道宣传 29 行
20201127 Santa Is Fasting
20201204 Most Dangerous Foods For Immune System
20201211 Toxic Liver
20201218 Wim Hof Breathing  ← sirtuin 唯一深挖
20201225 ACV for Acid Reflux
```

### 2021 H1（1-6 月，26 期）：**keto / IF / Doctor Is Wrong 系列化 + 新主题爆发**

```
20210101 Lose Belly Fat: Complete Guide
20210108 MCT Oil
20210115 Toxic Kidneys
20210122 IF: When To Eat
20210129 Detox Liver
20210205 BRAIN If You NEVER Exercise
20210212 SECRET To Burning BODY FAT
20210219 How To Count Carbs On Keto
20210226 Mexicans Were Skinny On Corn ← Weston Price 系
20210305 Hidden Signs You Are Depressed
20210312 Your Doctor Is Wrong About Blood Sugar & Fasting  ← 系列拐点
20210319 Cooking Oils
20210326 What REALLY Happens When You Take Medicine
20210402 Toxic Gallbladder
20210409 IF For MASSIVE Weight Loss
20210416 Best & Worst Sweeteners
20210423 No Carb Foods Can Still Spike Blood Sugar
20210430 10 Warning Signs You Have Anxiety
20210507 Your Doctor Is Wrong About Cholesterol
20210514 Eat This For Massive Fasting Benefits
20210521 Doctor Reacts: Clogged Arteries Juice
20210528 Lose Belly Fat Mistakes  ← epigenetic 唯一深挖
20210604 Top 10 Most HARMFUL Foods
20210611 10 Signs You Have A Leaky Gut
20210618 Your Doctor Is Wrong About Insulin Resistance
20210625 Best Time To Fast (autophagy)
```

### 2021 H2（7-12 月，27 期）：**"Your Doctor Is Wrong" 持续 + 5 天断食 + Aging + 30 天实验系列起手**

```
20210702 #1 Best Diet To Lose Belly Fat
20210709 Top 10 Protein Foods  ← 蛋白 / 兔子饥荒
20210716 10 Signs Not Drinking Enough Water
20210723 What Happens If You Don't Eat For 5 Days?  ← 30 天系列前奏
20210730 Your Doctor Is Wrong About Aging  ← NAD/NMN/NR 集中阐述
20210806 Lose Belly Fat But Don't Eat These Common Foods
20210813 Detox Kidneys
20210820 Fake Burger: Better Than Meat?  ← carnivore 反面
20210827 10 Signs Your Body Is Crying Out
20210903 Your Doctor Is Wrong About Weight Loss
20210910 Top 10 Best Foods To Break A Fast
20210917 Top 10 To Lose Belly Fat
20210924 10 Warning Signs Dementia
20211001 Top 10 Most Dangerous Foods
20211008 What If You Stop Eating Sugar For 30 Days?  ← 30 天系列开题
20211015 Fasting For Survival  ← 生存生物学 (20211015 00:00:00)
20211022 10 Prediabetes Signs
20211029 MicroPlastics In Bottled Water
20211105 5 Minutes Of This Burns Belly Fat
20211112 Worst Foods For Diabetics
20211119 What If You Stop Eating Breakfast For 30 Days?
20211126 Cold Hands And Feet
20211203 10 Signs Vitamin D Deficiency
20211210 10 Rules Of IF
20211217 Won't Lose Belly Fat Until You Do This
20211224 What If You Stop Eating Bread For 30 Days?
20211231 Top 10 Foods That Should Be Banned
```

### 2022 H1（1-6 月，21 期）：**30 天实验系列化 + New Topics（cancer / dementia / HIIT）**

```
20220107 10 Warning Signs Cancer
20220114 What If You Only Ate Once A Day For 30 Days?
20220121 10 IF Mistakes
20220211 What If You Only Eat Fruit For 30 Days?
20220218 Do THIS Every Day To Lose Belly Fat
20220225 You'll Never Worry About Cholesterol After This
20220304 How Your Cell Phone Destroys Your Brain  ← 全新主题：电磁波/脑
20220311 Best Type Of FAST For YOU
20220318 Top 10 Healthiest Vegetables
20220325 What If You Ate Only Meat For 30 Days?  ← carnivore 唯一专题
20220401 10 HIIT Exercises
20220408 10 Early Diabetes Signs
20220415 #1 Absolute Best Way To Reverse Dementia
20220422 What To Eat On One Meal A Day
20220429 Top 10 Foods That Cause Inflammation
20220506 What Happens If You Don't Eat For 3 Days?
20220513 #1 Best FATTY LIVER DETOX
20220520 Apple Cider Vinegar & Kombucha
20220527 Top 10 Foods To Lower Blood Sugar
20220603 10 Signs You Are Stressed
20220610 What If You Eat BACON Every Day For 30 Days?  ← R5 终点
```

---

## 5. 关键心智模型密度对比（R4 → R5）

| 心智模型 | R4 命中数 | R5 命中数 | R5 演化 |
|---|---|---|---|
| fasting | (R4 基础) | 324 | R5 上升为最核心词 |
| blood sugar | — | 291 | 与 fasting 几乎共现 |
| insulin resistance | 434 | 266 | R5 略降（但仍 Top 3）|
| keto | 533 | 227 | R5 略降（被 fasting 抢戏）|
| gut | 85 | 134 | R5 上升（leaky gut 科普线起）|
| leaky | 25 | 35 | R5 上升（10611 "10 Signs You Have A Leaky Gut" 专题）|
| autoimmune | 19 | 27 | R5 略升（20220325 提到 autoimmune 改善）|
| autophagy | — | 91 | R5 集中爆发（20210723、20200731 各 15 命中）|
| sirtuin | — | 3 | R5 仅 1 期（20201218 Wim Hof）|
| NAD+ | — | 0（字符串）/ 多次（"NAD plus"） | R5 仅 1 期（20210730 Aging）|
| NMN | — | 1 | R5 仅 1 期（20210730 Aging）|
| resveratrol | — | 3 | R5 仅 1 期（20201023 Worst Foods）|
| longevity | — | 12 | R5 散布 |
| epigenetic | — | 10 | R5 仅 1 期（20210528）|
| rapamycin / mTOR | — | 0 / 多次 | mTOR 在 20210528 出现 |

**[我推断]**：R4 → R5 期间 **fasting + autophagy 上升为新王**，**keto 略降但未失势**，**longevity 始终未成主菜单**。Ekberg 的"R4 抗衰老第二阶段"被 R5 的"断食 30 天实验"内容抢走了流量。

---

## 6. R5 未发现（gap list）

1. **未发现**：任何独立著作（书、电子书、PDF 长文）。R5 唯一外部著作是"在视频里提到 Weston Price / Shawn Stevenson / Lewis Howes 等人"，不是 Ekberg 自己出版。
2. **未发现**：Survival Biology（书名或框架名 0 命中）。**20211015 标题"Fasting For Survival"** 是唯一相关，但内容仍是断食科普，**不是"Survival Biology"作为一套独立知识体系被提出**。
3. **未发现**：Ulite / Uveia / Nexus / Wellness For Life 四个产品/品牌名（R4 末期定型，但 R5 23 个月 0 命中——**[我推断]**Ekberg 在 R5 期间未公开推广这些产品，或这些产品名称与 R4 阶段有别）。
4. **未发现**：animal-based / beef salt water（Shawn Baker 系关键词 0 命中）。R5 期间 carnivore 主轴化未发生。
5. **未发现**：podcast / new show / live stream / membership（0 命中除 1 次"gym membership"短语）。**[我推断]** R5 期间 Ekberg **未启动播客/会员制/直播**，纯靠 YouTube 单频道。
6. **未发现**：extended fasting / multi-day fasting / prolonged fasting 任何形式的专题系列（关键词 0 命中）。**[我推断]** 3 天 / 5 天断食是 R5 的"过渡形态"，**真正的 extended / multi-day 专题化尚未发生**——这可能是 R6-R8 的主菜单候选。
7. **未发现**：COVID / vaccine 持续锋面（R4 的 9+ 期 → R5 的 1-2 期急退）。
8. **未发现**：Sweden 政治化反 lockdown 框架（Sweden 在 R5 仅作饮食文化点缀）。

---

## 7. R5 节目格式演化（vs R4）

R4 三种模板：
- "Top 10 X" 
- "What Happens When You X"
- "Your Doctor Is Wrong About X"

R5 新增两种模板：
- **"What If You X For 30 Days"** 极限实验系列（6+ 期）
- **"Doctor Reacts"** 反应类（20210521 Clogged Arteries Juice 1 期，新但未扩张）

R5 弱化模板：
- 早期 Top 10 系列密度下降，被 30 天实验取代

**[我推断]**：R5 23 个月里 Ekberg 完成了**节目格式从"科普讲堂"向"实操挑战"的部分迁移**。30 天实验模板把"信不信"的认知战转为"试 30 天"的行为战，是 YouTube 健康垂类的高 CTR 钩子。R6-R8 这个模板可能继续扩张。

---

## 8. 一句话总结

**R5（2020-07 → 2022-06）的 23 个月里，Ekberg 把"Health Champions"品牌锁死，把 fasting + insulin resistance 升格为绝对主菜单，但"longevity/sirtuin/NAD+/NMN/carnivore/extended fasting/Survival Biology"全部 R4 末预告的"第二阶段"主题**——**没有一个兑现为 R5 主菜单**。R5 真正的节目格式升级是"What If You X 30 Days"极限实验系列（6+ 期），把 R4 的"科普讲堂"转为"实操挑战"，并为 R6+ 的 extended fasting / carnivore / animal-based 留好了入口。R5 期间 100% 内容载体仍是 YouTube 视频字幕——未见任何博客、独立著作或播客形式的著作维度延展。
