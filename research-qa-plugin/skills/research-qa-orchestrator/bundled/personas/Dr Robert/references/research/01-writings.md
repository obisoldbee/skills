# 01-writings.md — Dr. Robert Cywes R1 调研（v3.0 重跑，著作维度）

**调研范围**：`${HOME}/Documents/女娲造人/@DrCywesCarbAddictionDoc/` 下排序后前 100 个 .md 文件
**时间跨度**：2019-07-02 → 2020-07-21
**Total raw lines in scope**：43,621 行（来自 100 个 VTT 字幕文件）
**v3 完全重跑**：未读任何 v2 资料；本文件覆盖 `${HOME}/Documents/女娲造人/skills/MiniMax-M3-Claude/drcywescarbaddictiondoc-perspective/references/research/01-writings.md` 中 v2 版本的著作维度数据

---

## 1. grep 命令 + 命中数

> 全部基于 `cat /tmp/cywes_v3_r1_files.txt | xargs grep -l -i "<pattern>" 2>/dev/null | wc -l`（文件命中数）。

| # | Pattern | 命中文件数 | 备注 |
|---|---|---|---|
| 1 | `carb addict\|carbohydrate addict` | 63 | 核心术语 |
| 2 | `first bite` | 1 | 仅 20191113001.md |
| 3 | `five white\|5 white\|white assass` | 0 | **本时间窗内未出现"五白"术语** |
| 4 | `hyperinsulin` | 5 | 频率低于 carb addiction |
| 5 | `keto\|fasting` | 77 | 高频 |
| 6 | `relapse\|abstinence` | 27 | 中频 |
| 7 | `1999\|300 pound\|300 lb\|300lbs` | 12 | 自传数字 |
| 8 | `harm reduction` | 8 | 出现但立场是"戒断非减害" |
| 9 | `atkins\|bariatric\|prochaska\|eenfeld\|harcombe\|jane brown` | 36 | 多为 Atkins / bariatric；Eenfeld/Harcombe/Jane Brown 0 命中（见 §5） |
| 10 | `obesity\|diabetes\|PCOS\|UC\|ulcerative colitis\|pediatric` | 99/100 | 几乎全覆盖 |
| 11 | `stages of change\|transtheoret\|precontemplat` | 1 | 仅 20190710001.md |
| 12 | `diabetogenic\|obesogenic` | 7 | 偶发 |
| 13 | `sugar\|glucose` | 75 | 高频 |
| 14 | `dual diagnosis\|addiction.*disease` | 2 | 极低频（疾病模型非首选框架） |

**最高密度文件（按 `carb addict` 命中数排序，前 10）**：
1. 20200320001.md — 10 次
2. 20200317001.md — 9 次
3. 20200312001.md — 8 次
4. 20191205001.md — 8 次
5. 20200324001.md — 7 次
6. 20200310001.md — 7 次
7. 20191219001.md — 7 次
8. 20190722001.md — 7 次
9. 20190702001.md — 7 次
10. 20200630001.md — 6 次

**最长文件（前 5）**：20190710001.md（2639 行，lipedema）/ 20190722001.md（2261 行，糖尿病-自闭症-儿科）/ 20191128001.md（1857 行，Low Carb MD 客座）/ 20190702001.md（1757 行，自传开篇）/ 20190719001.md（1502 行）

---

## 2. 5-7 个一手发现（带时间戳引文）

### 发现 1：Cywes 公开承认"我自己 300 磅"是确立权威叙事的开场

> "yeah I topped out at around 300 pounds and part of it is understanding that it wasn't just a laziness and overeating it wasn't a misguided thing is a it was a very well-planned executed but somewhat dysfunctional protocol that made me as fat as I was" — **20190702001.md [00:01:46.060]**

他在第一次公开访谈就把"300 磅"作为开场而非"我曾是医生"的资历，把肥胖定位为**功能失调的协议**而非道德失败。这个框架是后续所有论证的合法性基础。

补充细节同源："as a pediatric surgeon I'd go into a kid let's say a 300-pounder who's 12 years old 10 years old and I've just taken a gallbladder because of gall stones ... they got the pizza they got the Big Mac they got and it's just carbs carbs carbs carbs carbs" — **20190702001.md [00:37:04.870]**。他用"12 岁 300 磅胆囊切除"作为"成瘾模型先于一切"的临床起源叙事。

### 发现 2："First bite" + "carb creep" 是 Cywes 的复发核心机制论

> "permission you grant yourself permission to have the first bite just like an alcoholic goes through mental Distortion to grant themselves permission to have the first sip of alcohol that's called the cop creep and once you've had that first bite it's gonna be three months before you get back on track" — **20191113001.md [00:04:30.760]**

"first bite" 概念在本时间窗 100 个文件里只出现于 20191113001.md（Ep:08 Going Sideways），但他在同一文件 [00:06:27.430] 给出标志性命题："make carbohydrate addiction binary ... it's that first bite it's that first taste it's that that first little bit that's the mistake"。

他个人数据点（"第一人称"）："I've stumbled several times in a nineteen year carb free lifestyle I've stumbled three times and every time I've stumbled it's been more than thirty pounds just like this a blink of an eye" — **20191113001.md [00:05:55.750]**。所以在 2019-11 节点，他的"无碳水时长"自称约 19 年，复发 3 次，每次反弹 30+ 磅。

### 发现 3：Cywes 明确拒绝"减害 (harm reduction)"作为成瘾方法论

> "nobody would ever address an addiction with harm reduction with doing less and yet every diet that any of you have ever ... full reduction diets or harm reduction is a methodology does not work in addiction because you still have access to your drug of choice" — **20190710001.md [00:43:30.470] → [00:57:31.530]**

这是他最鲜明的立场之一：减害在成瘾语境下**无效**，因为"你还在 access 你的 drug of choice"。这是他驳斥传统减肥逻辑的总开关。注意此节也常被反成瘾医师 / 毒品政策活动家引用——但 Cywes 的用法是**反减害**而非挺减害。

### 发现 4：Prochaska "stages of change" + "eat an elephant in one bite" 的治疗节奏

> "more than just a ketogenic diet and we go through stages of change you cannot eat an elephant in one bite we have to take cut it up into little pieces and if we make tiny little changes progressively we eventually get there" — **20190710001.md [01:17:23.830]**

他在 2019-07 已引用 Prochaska TTM（stages of change），但**整个 100 文件窗口中"stages of change / transtheoretical / precontemplation"只命中 1 次**（20190710001.md）—— 说明 TTM 是其治疗学的底层脚手架，但每次客座 / Q&A 不一定显式展开。复发时他区分 stage 2a vs 2b（relapse）：

> "transition my patients through the mental health and the substance abuse transition from stage one through stage 2a into stage three and recognize that stage 2b relapses will happen we can't condemn the relapse we can't deny it we have to help them to deal with it more effectively" — **20200320001.md [00:13:46.940]**

### 发现 5：胰岛素 / 胰高血糖素二元论 = Cywes 的代谢叙事核心

> "the hormone that maintains our blood sugar at around 70 is glucagon what glucagon does is it forces the liver to convert amino acids or protein and fat into sugar ... insulins primary job is not to clear the sugar from the bloodstream it's primary job is to switch off glucagon ... insulin switches off the release of fat from the fat cells" — **20191128001.md [00:07:12.410] → [00:07:55.650]**

**他故意用"factory woman for sugar"形容 glucagon**——这是他的修辞特色。**核心命题**："you've either got sugar or fat" [00:08:06.990]——这两个底物不能同时被代谢，要么烧糖要么烧脂。

补充：他强调 glucagon 才是维持血糖的激素，胰岛素只是**关闭 glucagon**——这是反驳"胰岛素降血糖"主流说法的逆向框架。配套机制："cortisol triggers glucagon to release sugar ... that's biologically if I come around a corner and there's a saber-toothed tiger I need that sugar instantaneously in my bloodstream" [00:08:18.510 → 00:08:48.660]——把 dawn effect 重述为进化适应（逃跑反应）。

### 发现 6：Cywes 的"自我转变路径"是分阶段、弃饮先行、含咖啡比喻

> "I couldn't kill it in one day I could not kill my best friend in one go so I started a stage by stage transformation whereby I removed carbohydrates I didn't cut back I didn't cut down I removed them in categories I started with what I was drinking I was doing the case of coca day ... I switched from coke dr2 to coffee without sugar in it it sucked it was the most disgusting thing that I could possibly have done for about two weeks but I forced myself" — **20190702001.md [00:09:41.360] → [00:10:09.790]**

关键修辞：
- 把肥胖称为 **"best friend"**（情感依附术语）
- "remove, don't cut back"（戒断 vs 减量——与发现 3 的反 harm reduction 立场一致）
- 从"case of Coca/day"换成"coffee without sugar"——**先弃液体碳水**
- "calories is an irrelevant concept when it comes to dealing with obesity" [00:10:39.890]——明确拒绝热量框架
- 17 年后："if you get between me and my coffee you're dead because that's my go to" [00:10:19.400]——"go to"作为替代 coping 工具

### 发现 7：Atkins / Ornish / WW / Zone 2005 JAMA 试验是他驳斥饮食行业的"核弹证据"

> "by dancing ER in 2005 where he can way he looked at four different diets diets of the day the Atkins diet which is a low carbohydrate diet the Ornish diet a fad restrictive diet Weight Watchers an energy restriction the Zone diet a macronutrient balanced diet and look at the pathetic results ... over 98% of diets fail within the first two to three months ... four point eight pounds seven point three pounds four point nine pounds six pounds that's not weight loss for an obese person I know I've been there that's a bowel movement okay" — **20190710001.md [00:55:32.759] → [00:56:27.599]**

他引用 2005 JAMA Dansinger 试验的 4 种饮食对照数据（Atkins/Ornish/WW/Zone），作为"所有 diet 都失败"的实证基础。他用"that's a bowel movement"（这是大便）这种**羞辱式比喻**形容一年的减重效果——这是他的表达 DNA（见 Phase 3）。

---

## 3. 反复出现的核心论点（≥3 文件 = 真信念）

| # | 论点 | 跨文件支持数 | 引文锚点 |
|---|---|---|---|
| A | "Carb addiction" 是一个独立诊断 / 框架，不是比喻 | 63/100 | 见 §1 表 1 |
| B | 减害 (harm reduction) 在成瘾中无效，必须戒断 (abstinence) | ≥5 | 20190710001, 20191113001, 20200320001, 等 |
| C | 复发 (relapse) 是 stage 2b，不应被谴责，是学习机会 | 27（relapse/abstinence） | 20191113001, 20200320001, 20191128001, 20191219001, 等 |
| D | "Obesity = diabetes"，二者是可交换词 | 高频同源短语 | 20190702001.md [00:02:36.190] "obesity are exchangeable words they're synonyms for each other" |
| E | 糖尿病 / 肥胖是 hyperinsulinemia / 胰岛素抵抗驱动，不是热量驱动 | 全文反复 | 20191128001, 20191219001, 20200312001, 等 |
| F | 自我权威叙事："我曾 300 磅 + 儿科外科医生" | 12（300/1999） | 20190702001, 20190710001, 等 |
| G | "Stages of change" + "eat an elephant in one bite" = 治疗节奏哲学 | 直接 1 + 同义复述 ≥3 | 20190710001.md [01:17:23.830] |
| H | 把肥胖食物（pizza/Big Mac/cake/buffet）描述为 "drug of choice" | 全文反复 | 见发现 1、2、5 |
| I | "你只能烧糖或烧脂"（sugar vs fat，二选一） | 多文件 | 20191128001.md [00:08:06.990] |
| J | 传统饮食行业（Atkins/Ornish/WW/Zone/HCG/Nutrisystem）全部失败 | ≥5 | 20190710001, 20190702001, 等 |

---

## 4. 自创术语清单（一手 vs 二手 vs 我推断）

### 一手（他亲口发明 / 反复使用，来源在范围内）
| 术语 | 定义 / 出处 |
|---|---|
| **"carb addiction doc"** | 自称品牌 — 20191128001.md [00:00:00+ 各集开场]、20200320001.md [00:00:07.799] "today's episode I'm dr. Rob Silas I am the carb addiction doc" |
| **"first bite"** | 复发起点 — 20191113001.md [00:06:30.610] "make carbohydrate addiction binary ... it's that first bite" |
| **"carb creep" / "cop creep"** | 碳水逐步渗回生活（他把 alcoholic 的"just one sip"映射到"just one bite"）— 20191113001.md [00:04:40.960]、复述于 [00:07:25.000] |
| **"going sideways"** | 个人委婉语 for relapse（系列名 Ep:08 Going Sideways）— 20191113001.md 标题、文中 [00:06:50.310] "I made a mistake I went sideways" |
| **"wallet biopsy"** | 讥讽各种减肥消费 — 20190702001.md [00:02:15.910] "wallet biopsies where the only thing you alternate ly lost was the little bit of money" |
| **"best friend"** | 把肥胖 / 糖描述为情感依附 — 20190702001.md [00:09:45.250] "I could not kill my best friend in one go" |
| **"emotion management carbohydrate addiction cognitive behavioral program"** | 完整治疗方案名 — 20200320001.md [00:14:09.380] "my emotion management carbohydrate addiction cognitive behavioral program" |
| **"factory woman for sugar"** | 把 glucagon 拟人化（glucagon = 糖的工厂女工）— 20191128001.md [00:07:48.720] "glucagon is our genetically based factory it's the factory woman for sugar" |
| **"obesity are exchangeable words"** | 糖尿病 = 肥胖 — 20190702001.md [00:02:36.190] |

### 二手（他引用他人 / 既有术语，但反复用）
| 术语 | 来源 | 他的用法 |
|---|---|---|
| **"stages of change"** | Prochaska & DiClemente TTM | 借用作为治疗节奏脚手架 — 20190710001.md [01:17:23.830]、20200320001.md [00:13:46.940] |
| **"harm reduction"** | 公共健康 / 成瘾学界标准术语 | **反对方**而非支持方 — 20190710001.md [00:43:30.470]、[00:57:31.530] |
| **"abstinence"** | 12-step / AA 标准术语 | 借用并强化（vs 减害） |
| **"Atkins / Ornish / WW / Zone"** | 既有 diet 名称 | 借 Dansinger 2005 JAMA 数据驳斥 |
| **"bariatric surgery"** | 既有手术 | 引用但定位为"治标不治本" — 20190710001.md [00:05:42.510] "rigorous exercise compression even bariatric surgery" |
| **"ketogenic diet"** | 既有医学术语 | 借用但**视为阶段工具而非终点**（"more than just a ketogenic diet"）— 20190710001.md [01:17:20.469] |
| **"fasting"** | 既有医学 / 宗教术语 | 借用作工具 |
| **"McGovern Commission"** | 1977 美国 Dietary Goals | 引用为"碳水推荐"灾难起源 — 20190702001.md [00:37:32.329] "the McGovern Commission people oh you gotta eat your ... seven portions of healthy cobbler" |

### 我推断（基于他在范围文件中的措辞，但**没有显式命名**）
| 推断概念 | 依据（仅作 Phase 2 备查） |
|---|---|
| "Carbon score" | grep 0 命中；他在多文件讲"总碳水 / 摄入频次"但未命名"carbon score"。**此概念可能是 v2 / 后期术语，本时间窗未出现** |
| "Diabetogenic" / "obesogenic" | 7 文件命中但**未作为招牌术语**——他更多用"insulin resistant" / "metabolic syndrome" |
| "Glucagon-insulin dual hormone model" | **他用但未命名**——见发现 5 |

---

## 5. 未发现（避免编造）

下列项在范围（2019-07-02 → 2020-07-21，前 100 文件）中**没有一手证据**：

1. **"Andreas Eenfeld / Eenfeldt"** — 0 命中。他在 2019-2020 没有引用此人。Jane Brown 也是 0 命中（她在 2021-01 才加入他的节目客座，按任务背景所述）。
2. **"Zoe Harcombe"** — 0 命中。
3. **"Five white assassins" / "五白" / "white poison"** — 0 命中。他用 pizza / Big Mac / cake / buffet / cracker / cookie 描述致害碳水，但**未在 2019-2020 用"五白刺客"这种格式化命名**。这可能是 v2 / 后期框架。
4. **"Carbon score"** — 0 命中。
5. **"1999" 作为他本人肥胖 / 转变年** — 0 命中。grep "1999" 命中 12 文件均为**一般历史引用**（"1977 McGovern Commission"等），**没有"1999 年我 300 磅"自传叙事**。他 2019-2020 的自传叙事是"topped out at around 300 pounds"（无年份）+ "17 years later" / "19 year carb free"（在 2019-11 节点 = 2000-2001 起步）。**Phase 2 写"1999 年 300 磅"会构成编造**。
6. **"Dual diagnosis"** — 仅 2 命中，且未作为招牌框架。**他用 "substance abuse + mental health" 双轨**而非 "dual diagnosis" 术语。
7. **"Evidence-based" / "RCT" / "Cochrane"** — 极低频；他的引用风格是临床轶事 + 个人叙事 + Dansinger 2005 JAMA 单一试验，不强调循证医学修辞。
8. **"GLP-1 / semaglutide / Ozempic"** — **本时间窗 0 命中**。这是 2021+ 时代的药物，2019-2020 不存在。这是 Phase 2 重要警示。
9. **"Continuous glucose monitor / CGM"** — 偶发（20200312001.md 提到 C peptide），但**未作为患者教育工具重点**。
10. **PCOS** — 在 99/100 临床术语命中文件里，但**没有专门的 PCOS 视频**（这一百个文件里没有 title 含 PCOS 的）。他讲 PCOS 但散见于胰岛素 / 代谢综合征讨论。

---

## Round 2 (2020-07-22 → 2021-06-17) — Phase 1 Agent 1

**调研范围**：`/tmp/cywes_v3_r2_files.txt`（排序后第 101-200 个 .md 文件，100 个 VTT 字幕）
**时间跨度**：2020-07-22 → 2021-06-17（≈ 11 个月）
**承接 R1**：R1 已建立 10 个核心论点（A-J）+ 9 个一手术语；本轮独立 grep+精读，**未读自己或别 agent 的 R1 产物外部段落**，仅与 R1 已写入的论点 / 术语作对比
**R2 关键差异**：carnivore 主题轴成形、hyperinsulinemia 学术化、obesogenic/diabetogenic 临床分型首次成簇、Jane Brown 加入诊所、keto moment 命名首次出现、emotional tension 频繁化

---

### 1. R1 vs R2 关键词命中数对比（文件命中数 / 总行数）

| # | Pattern | R1 文件 | R2 文件 | R1 行数 | R2 行数 | 变化与解读 |
|---|---|---|---|---|---|---|
| 1 | `carb addict\|carbohydrate addict` | 63 | **93** | — | 369 | **× 1.5** — 自称品牌稳固 |
| 2 | `first bite` | 1 | 1 | — | 2 | 停留 1 文件，未铺开 |
| 3 | `hyperinsulin` | 5 | **9** | — | 47 | 文件 × 1.8，**行数级别学术化使用** |
| 4 | `keto\|fasting` | 77 | 77 | — | 734 | 文件持平，密度上升 |
| 5 | `relapse\|abstinence` | 27 | **10** | — | 34 | **下降** — 治疗语言从 12-step 转向 emotion-management |
| 6 | `harm reduction` | 8 | **1** | — | 5 | **几乎消失** — 反减害立场已默认化，无需重复 |
| 7 | `stages of change\|transtheoret` | 1 | 1 | — | 2 | 持平 — TTM 仍是隐性脚手架 |
| 8 | `diabetogenic\|obesogenic` | 7 | 4 | — | 13 | 文件少但**正式成对使用**（见发现 13） |
| 9 | `carnivore` | **未追踪** | **41** | — | **244** | **R2 全新主题轴** — 41/100 文件 |
| 10 | `carnivore way of life\|carnivore diet` | — | **23** | — | 108 | 主题分化"diet vs way of life"开始 |
| 11 | `keto moment` | — | **1（专集 + 29 行）** | — | 29 | **R2 首次命名**（20210513001 Ep:159） |
| 12 | `emotional tension` | — | **13** | — | 54 | **R2 首次频繁** — 行为框架核心动词 |
| 13 | `andreas\|eenfeld` | 0 | 1 | — | 4 | **R2 首次显式引用** |
| 14 | `zoe\|harcombe` | 0 | 2 | — | 16 | **R2 首次引用** |
| 15 | `jane brown\|nutrition specialist` | 0 | 4 | — | 12 | **R2 首次出现**（Jane 2021-01-01 加入） |
| 16 | `covid\|vaccine\|coronavirus` | — | 6 | — | 20 | **R2 才存在的时代主题**（疫情起点 2020 春） |
| 17 | `pcos\|ulcerative colitis\|pregnan\|pediatric` | — | 42 | — | 543 | 临床应用面**显著扩张** |
| 18 | `low.fat lie\|low-fat lie` | — | 0 | — | 0 | **未发现**（任务背景列为应有标签，R2 仍 0 命中） |
| 19 | `transfer addiction` | — | 0 | — | 0 | **未发现** |
| 20 | `carbon score` | 0 | 0 | — | 0 | **R2 仍未出现** |

**R2 最高密度文件**（按 `carb addict` 行数）：
1. 20201209001.md — 64 次 `carnivore`（Ep:116 ESSENTIALS FOR CARNIVORE LIFESTYLE）
2. 20201006001.md — 23 次 `carnivore`（Ep:98 Ulcerative Colitis - REMISSION）
3. 20200825001.md — 22 次 `carnivore`（Crohn's disease 专集）
4. 20210610001.md — 12 次 `hyperinsulinemia`（PCOS / 临床应用专集）
5. 20210513001.md — 29 次 `keto moment`（Ep:159 KETO MOMENTS DEFINE LONGTERM SUCCESS）

---

### 2. R2 新发现（带时间戳一手引文）

#### 发现 11（**R2 新增**）：Carnivore 作为独立主题轴成形 — Ep:116 专题命名 "way of life" 而非 "diet"

> "in a carnivore book this is an excellent a carnivore book this is an excellent excellent **way of life**" — **20201209001.md [00:01:15.680] → [00:01:22.310]**
>
> 同集 Cywes 强调自我状态："prior to going pure carnival so in my case i am **mostly carnivore** ... i'm mostly carnivore because it suits my **lifestyle better**" — **20201209001.md [00:01:29.280] → [00:02:04.149]**
>
> 反驳教条主义者："for those authoritarian people oh i'm **strict carnivore** i don't eat pepper i don't eat god" — **20201209001.md [00:03:30.720]**

- **R1 状态**：0 命中（R1 100 文件 carnivore 未追踪 / 未成为主题）
- **R2 演化**：**新增主题轴** — 41/100 文件命中 carnivore，专集 Ep:116（2020-12-09）首次系统化论述
- **关键修辞**：把 carnivore 定位为 **way of life** 而非 8 周减肥 diet（"this is not a diet carnivore was not a diet you do for eight weeks to get" — [00:03:13.040]）
- **过渡论**：他拒绝 SAD → pure carnivore 一步切换（"if you went from the standard american diet to pure carnivore i would have crashed and burned" — [00:03:02.480]），强调 **stepwise migration**——与 R1 发现 6（弃饮先行、分阶段戒断）一致
- **一手核心心法**：carnivore 是 keto/低碳 lifestyle 的"自然降落点"，但**入路是progressive、非教条**

---

#### 发现 12（**R2 新增**）：Hyperinsulinemia 从背景词变成临床主语

> "the **hyperinsulinemia** high levels of insulin high levels of ... that's the topic for another day but when you're **hyperinsulinemic** those insulin levels are up all the time" — **20210610001.md [00:03:10.959] → [00:03:41.990]**
>
> 关联 PCOS / 不孕："testosterone numbers go through the roof when you're **hyperinsulinemic** because of chronic excessive carbohydrate" — **20210610001.md [00:05:01.840]**
>
> "that's a testosterone effect and it is a **hyperinsulinemia effect** and it is an effect of chronic excessive" — **20210610001.md [00:06:01.600]**

- **R1 状态**：5 文件命中（R1 §1 表 #4，频率低于 carb addiction）
- **R2 演化**：**× 1.8 文件** → 9 文件 / **47 行**——同一篇视频内重复使用作为临床主语（20210610001 出现 12 次）
- **新关联**：hyperinsulinemia → 高睾酮 → PCOS → 不孕 — **R2 新增因果链**
- **核心心法**：Cywes 在 R2 把"insulin resistance"语言逐步替换成 **"hyperinsulinemia"**——这是更医学化、更接近 Joseph Kraft / Ron Rosedale 学派的术语

---

#### 发现 13（**R2 新增**）：Obesogenic / Diabetogenic 作为患者**临床分型**首次成对使用

> "your teaching on the **obesogenic and diabetogenic** disease physiologic pathways now validate and demonstrate why i see such a difference in disease pathology that seems the same the thin overweight patients" — **20210202001.md [00:04:44.320] → [00:04:59.840]**
>
> "we call that an **obesogenic pathway** where the body can turn that into a fat very readily those people come enormous their blood sugar isn't very high a little bit high but they do not develop profound diabetes" — **20210202001.md [00:09:17.360] → [00:09:32.070]**

- **R1 状态**：7 文件偶发命中，但 R1 §4 标注"未作为招牌术语"
- **R2 演化**：4 文件命中但**正式成对使用** — Cywes 用 obesogenic / diabetogenic 作为**两种患者代谢表型**的分类（胖型 vs 瘦型糖前 / TOFI vs 胖糖）
- **核心心法**："同样吃糖，为什么有人胖但血糖还行，有人不胖但血糖崩溃？" → 答：两种基因通路（obesogenic 偏脂肪储存 / diabetogenic 偏血糖失控）
- **R2 关键术语化**：从"insulin resistant" / "metabolic syndrome" 泛称 → **临床分型语言**

---

#### 发现 14（**R2 新增**）：Jane Brown 2021-01-01 加入诊所 — "Certified Nutrition Specialist" 是营养支持基础设施化

> "sitting beside me is **jane brown** and jane is joining our **practice as of january the 1st** jane is a **certified nutrition specialist** ... her own life is lived in the same space" — **20210103001.md [00:00:12.160] → [00:00:31.429]**
>
> Jane 自述："i started out on this lifestyle journey about seven years ago when i discovered i was probably marching towards diabetes strong family history of type 2 diabetes ... and i became board certified as a **nutrition specialist** i'm a **masters in human nutrition** and i'm also more recently **certified in ketogenic nutrition**" — **20210103001.md [00:01:42.079] → [00:02:22.080]**
>
> 6 月仍在体系内引用："we have jane in my office who's our **nutrition specialist** and she is absolutely superb at giving you nutritional guidance" — **20210608001.md [00:02:51.200] → [00:02:57.270]**
>
> Jane 的小组角色："**jane's support group is a safe haven** it's a place you can go where everybody is like-minded" — **20210608001.md [00:03:22.319] → [00:03:28.869]**

- **R1 状态**：0 命中（Jane Brown 在 2021-01 才加入）
- **R2 演化**：4 文件命中（2021-01-03 / 2021-01-28 / 2021-02-25 / 2021-06-08）— **持续半年内被引用为诊所长期成员**
- **新基础设施**：Cywes 自己专注 carb addiction + 外科 / 心理框架；Jane 提供 ketogenic / 营养细节 + **support group**（"safe haven"）
- **核心心法**：从单人 doc 模式 → **碳水成瘾医生 + 酮饮食营养师** 组合诊所；Cywes 自称"enough babbling for me"把营养教学**显式 outsource** 给 Jane

---

#### 发现 15（**R2 新增**）：Andreas Eenfeldt（Diet Doctor）作为**国际盟友**首次显式引用

> "a buddy of mine **andreas ianfeld the diet doctor** said something very profound and something very simple and really this it seems obvious but i ... an important starting point and **andreas is very pragmatic** in that regard and **low carb isn't a little bit in the addiction model** it" — **20200730001.md [00:00:23.199] → [00:00:53.590]**

- **R1 状态**：0 命中（R1 §5 第 1 条明确写"2019-2020 没有引用此人"）
- **R2 演化**：**R2 第 9 天即首次引用**（2020-07-30，从 R2 起始 7-22 算第 8 天）— 单文件 4 行
- **核心心法**：Cywes 在 R2 开始构建**碳水成瘾的国际盟友网**；Eenfeldt 的 "you have to keep eating low carb" 被引用作为**反 yo-yo 复发**的 anchor

---

#### 发现 16（**R2 新增**）：Zoe Harcombe（UK 营养统计学家）作为**论敌反击**资源首次引用

> "a really eloquent analysis done by a friend of mine **dr zoe hockham** [zoe harcombe] she's actually a **phd dietitian** who works in the united kingdom and does a lot of **statistical analysis** she's one of the people that helped to defend **tim noakes** on his trial but zoe does a **monday newsletter** and it's absolutely excellent" — **20201222001.md [00:00:16.080] → [00:00:33.910]**

- **R1 状态**：0 命中
- **R2 演化**：2 文件命中（2020-12-22 / 2021-04-09）— **首次引用**
- **核心心法**：Cywes 借 Harcombe 的**统计分析 + Tim Noakes 辩护背景**作为反主流营养学的"学术弹药库"——这是他从"个人叙事 + Dansinger 2005 单一试验"扩展到**外部统计盟友引用**的转折

---

#### 发现 17（**R2 新增**）：Emotional Tension 作为**行为成瘾核心动词**首次频繁

> "carbohydrates are a highly addictive drug that we consume in excess to manage our **emotional tension** our anxiety our stress our depression our anger our fear our sadness our boredom" — **20200904001.md [00:14:54.959] → [00:15:01.279]**
>
> "you're using a drug that **obliterates your emotional tension** but disconnects you from dealing with stuff" — **20210601001.md [00:09:30.399] → [00:09:38.710]**
>
> "the reason we become fat the reason we become diabetic is because of a **dysfunctional emotional management system** where we use carbohydrates and snacking as a dominant excessively used pathway of **emotional relief**" — **20210525001.md [00:00:14.160] → [00:00:30.230]**

- **R1 状态**：未在 R1 §4 术语清单出现（R1 未追踪 "emotional tension"）
- **R2 演化**：13 文件 / 54 行 — **从 2020-09 起持续整个 R2**，成为他的标志性动词
- **核心心法**：把成瘾的"why"从**生理依赖**重新定位到 **emotional tension 管理工具**——这是把 Prochaska TTM (R1 发现 4) 嫁接到 emotion regulation 心理学的关键术语
- **配套术语**：dysfunctional emotional management system / emotional relief / effort-based system（替代方案）

---

#### 发现 18（**R2 新增**）：临床应用矩阵显著扩张 — UC remission / Crohn / COVID 风险分层 / PCOS-不孕

> **UC（溃疡性结肠炎）**："i have a number of patients who are in **remission of all medication** ... and in **remission of the ulcerative colitis**" — **20201006001.md [00:19:17.280] → [00:19:24.789]**（专集 Ep:98 Ulcerative Colitis - REMISSION）
>
> **Crohn's**："the healthiest diet for someone with **active crohn's disease is a carnivore diet** ... soft soft carnivore diet" — **20200825001.md [00:06:54.639] → [00:07:08.950]**
>
> **PCOS-不孕**："there are a number of **infertility practices** that refer patients to us because **pcos is the commonest cause of infertility**" — **20210202001.md [00:18:15.360] → [00:18:23.350]**
>
> **COVID 疫苗风险**：专集 Ep:152 "COVID VACCINES: 3 CRITICAL STEPS TO AVOID BLOODCLOTS/DVT" 讨论 J&J 疫苗 DVT 风险 — **20210420001.md [00:00:13.519] → [00:00:23.269]**

- **R1 状态**：R1 §5 第 10 条标注"PCOS 散见但无专集"、UC 未追踪、COVID 0 命中
- **R2 演化**：**4 个独立专题视频** + 42/100 文件覆盖 PCOS / UC / pregnancy / pediatric
- **核心心法**：R2 把 carnivore + keto 从"减肥工具"扩展到 **疾病 remission 治疗工具**（UC / Crohn 全药物停药）+ **不孕诊所推荐渠道**（PCOS 患者从 infertility practice 转介）+ **COVID 时代疫苗风险分层咨询**

---

#### 发现 19（**R2 新增**）：Keto Moment — **R2 首次命名**的"替代奖励"具体战术

> "what are **keto moments** when i was fat i always used to have a case of coke and a big one of those big family bags ... those moments of caloric or of carbohydrate emotional relief with what i call **keto moments a keto moment is a little thing that you do** a tiny little thing that you do that's the equivalent to two or three m&m's" — **20210513001.md [00:01:50.320] → [00:03:12.149]**（专集 Ep:159 KETO MOMENTS DEFINE LONGTERM SUCCESS）
>
> "if i recognize ... but when i do and i have a little keto moment something that i do tiny little thing it makes me feel great" — **20210513001.md [00:03:30.799] → [00:03:36.470]**

- **R1 状态**：0 命中
- **R2 演化**：1 专集 + 29 行 — **R2 首次命名**（2021-05-13）
- **核心心法**：解决"emotional tension 管理"具体操作问题 — 用**小而高频的酮味觉时刻**（一小撮坚果、一片黑巧、几滴脂肪）替代过去的"一罐可乐 + 大袋糖果"；与 R1 发现 6"咖啡作为 go-to"逻辑一脉相承，但 R2 把它命名 / 系统化

---

#### 发现 20（**R2 新增**）：Carb Creep / Cop Creep 出现频次 — 在 R2 几乎消失（反信号）

- **R1 状态**：1 文件命中（20191113001.md，发现 2）
- **R2 演化**：1 文件命中 / 2 行 — **R2 未铺开**
- **解读**：与 first bite 一样，"carb creep"在 2019 已经成型，但**没有在 R2 重复传播**——可能因为他在 R2 把同样机制改用 **"emotional tension 管理 → carb 复发"**（发现 17）语言来表述
- **核心心法**：术语命名稳定但**传播频次不稳定**——这是 Phase 2 警示：v3 时不要假设"cop creep"是 R2 招牌词

---

### 3. R1 vs R2 论点演进对比（R1 §3 10 论点 + R2 新增）

| # | R1 论点 | R1 状态 | R2 状态 | 演化判定 |
|---|---|---|---|---|
| A | Carb addiction 是独立诊断 / 框架 | 63/100 | **93/100** | **× 1.5 强化** — 已成默认前提 |
| B | 反 harm reduction、必须 abstinence | ≥5 | **1 文件 / 5 行** | **下降** — 立场已默认化，不再重复 |
| C | 复发是 stage 2b、不应被谴责 | 27 | 10 | **下降** — 治疗语言转向 emotion-management |
| D | obesity = diabetes 同义词 | 高频 | 高频（42 临床扩张文件） | 持平，但**扩展到 PCOS / UC / Crohn / fertility** |
| E | hyperinsulinemia 驱动论 | 全文反复（5 文件） | **9 文件 / 47 行** | **学术化** — 单文件可重复 12 次 |
| F | 我曾 300 磅 + 儿科外科医生 | 12 | 6 | **下降** — 自传开场不再每次重复 |
| G | Stages of change + eat an elephant | 1 直接 + ≥3 复述 | 1 直接 | 持平，**仍是隐性脚手架** |
| H | 食物 = drug of choice | 全文反复 | 全文反复（emotional tension 显式接驳） | 强化 |
| I | sugar vs fat 二元燃料论 | 多文件 | 持平 | 持平 |
| J | Atkins/Ornish/WW/Zone 全部失败 | ≥5 | 偶发 | **下降** — Dansinger 2005 引用减少 |
| **K（R2 新增）** | **Carnivore 是 keto 的自然降落点 + "way of life" 而非 diet** | **0** | **41/100 + 专集** | **R2 新主题轴** |
| **L（R2 新增）** | **Hyperinsulinemia → PCOS / 不孕 / 高睾酮的因果链** | **0** | **9 文件 + 专题视频** | **R2 新论点** |
| **M（R2 新增）** | **Obesogenic vs Diabetogenic 双通路临床分型** | 偶发 | **正式成对** | **R2 术语化** |
| **N（R2 新增）** | **Emotional tension 管理 = 行为成瘾的核心 why** | 隐含 | **13 文件 / 54 行** | **R2 显式命名** |
| **O（R2 新增）** | **Keto moments = 替代奖励的具体战术** | **0** | **专集 + 29 行** | **R2 命名** |
| **P（R2 新增）** | **诊所基础设施化：Cywes (MD) + Jane Brown (CNS) 双人 + support group** | **0** | **4 文件 + 持续 6 个月** | **R2 组织演化** |
| **Q（R2 新增）** | **COVID 时代疫苗风险分层 + keto clutter 应激饮食解码** | **0** | **6 文件 + 2 专集** | **R2 时代主题** |

---

### 4. R2 新增自创术语清单（**全部** R1 未出现）

| 术语 | 一手定义 / 出处 | R1 状态 |
|---|---|---|
| **"keto moment"** | "a tiny little thing that you do that's the equivalent to two or three m&m's" — 20210513001.md [00:03:08.879] | **R1 = 0** |
| **"keto clutter"** | "what i call keto clutter ... we become fat the reason we become diabetic is because of a dysfunctional emotional management system" — 20210525001.md [00:00:07.600] → [00:00:20.870] | **R1 = 0** |
| **"emotional tension"** / **"emotional relief"** | "to manage our emotional tension our anxiety our stress our depression" — 20200904001.md [00:14:57.279] | R1 隐含未命名 |
| **"dysfunctional emotional management system"** | 20210525001.md [00:00:16.640] → [00:00:20.880] | **R1 = 0** |
| **"effort-based system"** | "really work on building up what i call an effort-based system" — 20210525001.md [00:00:44.960] → [00:00:47.029] | **R1 = 0** |
| **"mostly carnivore"** / **"spectrum carnivore"** | 反教条派别 — "i'm mostly carnivore because it suits my lifestyle better" / "a spectrum carnivore diet you're getting all the nutrients" — 20201209001.md [00:01:29.280]; 20201006001.md [00:15:21.519] → [00:15:24.150] | **R1 = 0** |
| **"carnivore way of life"** vs **"carnivore diet"** | 命名学的区分 — 20201209001.md [00:01:15.680] → [00:01:22.310] | **R1 = 0** |
| **"obesogenic pathway"** / **"diabetogenic pathway"** | 临床分型 — 20210202001.md [00:04:44.320]; [00:09:17.360] | R1 偶发未成对 |
| **"safe haven"**（Jane's support group） | 20210608001.md [00:03:22.319] | **R1 = 0** |
| **"low carb isn't a little bit in the addiction model"** | 借 Andreas Eenfeldt 之口 — 20200730001.md [00:00:50.069] | **R1 = 0** |

---

### 5. R2 仍未发现（v3 不可用 / Phase 2 警示）

下列项在 R2 100 文件（2020-07-22 → 2021-06-17）中**仍 0 一手证据**：

1. **"transfer addiction"** — 0 命中。任务背景列为应有，但 R2 未出现 — 可能是 v3.5+ 后期术语
2. **"carbon score"** — 0 命中。R1 = 0 / R2 = 0 — **vN 时代术语**，Phase 2 不可写
3. **"low-fat lie"** — 0 命中。任务背景列为"R2 标签持续"，但 grep 0 文件 — **Phase 2 警示：可能是 v2 误植**
4. **"five white assassins" / "五白"** — 0 命中。R1 = 0 / R2 = 0 — **vN 后期框架**
5. **"harmed reduction"** — 0 命中（注：是 "harm reduction" 拼写不同的变体）
6. **"first bite"** — 仍只 1 文件命中（沿用 R1 20191113001.md），R2 未铺开 — 是稳定术语但**非高频招牌**
7. **"GLP-1 / semaglutide / Ozempic"** — R2 仍 0 命中（Ozempic 2017 FDA 已批，但要到 2022+ 才进入营养医学话语）
8. **"continuous glucose monitor / CGM"** — R2 仍偶发未成专题
9. **"evidence-based" / "RCT" / "Cochrane"** — R2 仍 0 命中 — Cywes 的引用风格**始终是临床轶事 + 个人叙事 + 盟友引用**，不走 EBM 修辞
10. **"low-fat lie"** — 0 命中（已列入第 3 条警示）

---

### 6. R2 关键时间锚点（Phase 2 引用准确性参考）

| 日期 | 事件 / 锚文件 |
|---|---|
| **2020-07-30** | Andreas Eenfeldt 首次显式引用（20200730001.md） |
| **2020-08-25** | Crohn's disease 专集首次提出"carnivore 是最佳治疗" |
| **2020-09-04** | "emotional tension" 一手术语首次显式定义 |
| **2020-10-06** | UC remission 专集（Ep:98）— carnivore 临床应用化里程碑 |
| **2020-12-09** | Carnivore 系统化专集 Ep:116 — "way of life" 命名 |
| **2020-12-22** | Zoe Harcombe 首次引用 |
| **2021-01-03** | **Jane Brown 加入诊所**（标志性组织里程碑） |
| **2021-02-02** | obesogenic / diabetogenic 临床分型首次成对使用 |
| **2021-04-20** | COVID 疫苗 J&J DVT 专集（Ep:152） |
| **2021-05-13** | **"Keto moments" 一手命名**（Ep:159） |
| **2021-05-25** | "keto clutter" 一手命名（Ep:162） |
| **2021-06-10** | hyperinsulinemia → PCOS → 高睾酮因果链最详细论述（12 次/集） |

---

### 7. R2 备注给 Phase 2

1. **R2 的核心识别**：从"成瘾教育 + abstinence 立场"转向"**carnivore lifestyle + emotional management + 诊所规模化**"——这是 Cywes 进入成熟期的标志
2. **Jane Brown 不是客座**：她是 2021-01-01 起的诊所**长期成员** — Phase 2 写"Cywes 一个人"会过时
3. **"emotional tension" 是 R2 最显著的语言转变** — 比"emotion management"更动词化、更心理学化；Phase 3 表达 DNA 必须涵盖
4. **carnivore 在 R2 不是教条而是 spectrum** — 他反"strict carnivore"派别（"authoritarian people"）— Phase 2 不要把他写成 Shawn Baker 式纯肉派
5. **hyperinsulinemia 学术化**是他与 Joseph Kraft / Ron Rosedale / Ben Bikman 学派接轨的语言信号 — Phase 3 心智模型应反映
6. **临床应用扩张**：从"减肥 + 糖尿病"扩展到"UC / Crohn / PCOS / 不孕 / 儿科 / COVID 风险" — Phase 2 clinical application 维度可基于此扩张矩阵
7. **Eenfeldt / Harcombe 是 R2 新盟友**但**仍是单次引用** — 不能写成"长期合作"
8. **"keto moment" 是 Cywes 自己命名**（不是别人创造借用） — Phase 2 列入一手术语清单
9. **R2 未出现"transfer addiction" / "low-fat lie"** — 任务背景列为应有，但 grep 证据 0 — Phase 2 建议**留待 R3-R5 验证**
10. **"first bite" / "carb creep" 在 R2 几乎沉默** — 这两个 2019 创造的术语 R2 未持续传播，Phase 2 心智模型应标注"R1 命名 / R2 未铺开"

---
## Round 3 (2021-06-17 → 2022-06-28)

### 1. Grep 命令 + 命中数（Round 3 全 100 文件，2021-06-17 → 2022-06-28）

| 关键词 | R1 命中 | R2 命中 | **R3 命中** | 趋势 |
|---|---|---|---|---|
| carbohydrate / sugar | 高频 | 80+ | **92/100** | 持平高位 |
| keto / ketogenic | 中频 | 60+ | **83/100** | 持平 |
| insulin / insulin resistance | 高频 | 50+ | **60/100** + **34 IR** | 持平 |
| carnivore | 偶发 | 41/100 | **49/100** | **继续上升** |
| glucose / blood sugar | 30+ | 40+ | **51/100** | 持平 |
| hyperinsulinemia | R2 = 9 文件 | 9 | **7 文件（density 仍高）** | 持平 |
| cancer | 偶发 | 14 | **18/100** | **上升** |
| Alzheimer / dementia | 偶发 | 7 | **10 文件** | **明显上升** |
| inflammation / inflammatory | 25 | 30+ | **29/100** | 持平 |
| low carb | 40+ | 50+ | **43/100** | 持平 |
| pediatrics / kids / teens | 20+ | 27 | **27/100** | 持平（**儿科是他的稳定子领域**） |
| PCOS | R2 萌芽 | 9 | **14 文件** | **持续上升** |
| LDL | 偶发 | 15+ | **19/100** | 持平 |
| exercise | 20 | 30+ | **25/100** | 持平 |
| intermittent fast / OMAD | 偶发 | 20+ | **21/100** | 持平 |
| anxiety / depression | 20+ | 18 | **14/100** | **下降** |
| ketone | 多 | 多 | 仍高频 | 持平 |
| autism / ADHD | 5 | 5 | **5 + 3** | ADHD 略增 |
| ApoE4 | 0 | 0 | **1 文件（自报）** | **R3 新自传素材** |
| thyroid | 10 | 12 | **15/100** | 略升 |
| mortality / death | 10 | 16 | **17/100** | 略升 |
| intermittent fast / OMAD | — | 20+ | **21/100** | 持平 |
| emotional tension | R2 = 13 文件 | 13 | **11 文件** | 略降（已"默认化"） |
| keto moment | R2 = 专集 | 1 | **0/100** | **R3 沉默** |
| keto clutter | R2 = 专集 | 1 | **0/100** | **R3 沉默** |
| safe haven (Jane) | R2 = 1 | 1 | **0/100** | **R3 沉默** |
| Jane Brown / Jane | R2 = 4 | 4 | **0/100** | **R3 沉默**（注意：grep 不区分大小写但 0） |
| transfer addiction | 0 | 0 | **0/100** | **vN 全期未出现** |
| low-fat lie | 0 | 0 | **0/100** | **vN 全期未出现** |
| five white / 5 white | 0 | 0 | **0/100** | **vN 全期未出现** |
| carbon score | 0 | 0 | **0/100** | **vN 全期未出现** |
| 12 step / AA meeting | 偶发 | 偶发 | **0/100** | **R3 未采纳 12 步修辞** |
| apoB | 0 | 0 | **0/100** | **未采纳 Attia 派生物语** |
| continuous glucose monitor / CGM | 偶发 | 8 | **14 文件** | **R3 大幅扩张** |
| fructose | 偶发 | 9 | **9 文件 / density 大幅升（2 文件 ×14 次）** | **R3 主题化** |
| Ozempic / semaglutide / Wegovy | 0 | 0 | **1 文件（20220512001.md ×5 行）** | **R3 首次显式** |
| gut microbiome / microbiota | 偶发 | 偶发 | **1 文件** | 偶发未成主题 |
| obesogenic / diabetogenic | R2 = 9 文件 | 9 | **3 文件** | **R3 收缩**（已"默认化"） |
| McGovern | R1 = 1 | 1 | **3 文件** | 略升 |
| bowel movement | 偶发 | 偶发 | **4 文件** | 略升 |
| best friend | 偶发 | 偶发 | **4 文件** | 略升 |
| went sideways | 偶发 | 偶发 | **5 文件** | 持平 |
| 17 years carb free | 0 | 0 | **2 文件** | **R3 首次出现**（从 19 → 20 → 17 年**叙事漂移**） |
| NAFLD / fatty liver | 偶发 | 7 | **7 文件** | 持平 |
| TMAO / choline | 0 | 0 | **1 文件** | 偶发 |
| gout / uric acid | 偶发 | 12 | **12 文件** | 持平 |
| autoimmune | 偶发 | 16 | **16 文件** | 持平 |
| Endocrinologist（自报） | 偶发 | 多 | **5 文件** | 持平 |
| Pediatric surgeon（自报） | 偶发 | 多 | **10 文件** | 持平 |
| bariatric surgery | 多 | 多 | **10 文件** | 持平 |
| Westman (Eric Westman) | R2 = 1 | 1 | **6 文件（11 命中）** | **R3 持续引用** |
| Perlmutter | 0 | 0 | **0/100** | **vN 全期未引用** |
| Eenfeldt / Harcombe / Berg / Attia / Chaffee / Baker | 偶发 | 4 文件 | **0/100**（grep 失败）| **R3 反而沉默盟友引用**——自查重做 |

### 2. R3 真正新出现的 5 大主题轴（**R1+R2 都没有 / R3 才出现**）

#### 2.1 **CGM 临床应用化（continuous glucose monitor）—— 14 文件覆盖**

R3 第一次把 CGM 从"概念提及"提升为"标准临床工具"。在 R3 100 文件中 CGM 出现 14 次（v2 全期 0 专集 / R1 偶发 / R2 = 8 提及）。典型用法：

- "**the morning when you first wake up if ever you wear a cgm a continuous glucose monitor you'll see as soon as you wake**" — 20210805001.md [00:00:33.040] → [00:00:37.030]
- "**those devices are out there got a cgm started measuring her numbers**" — 20210810001.md [00:06:23.520] → [00:06:30.230]
- "**when you wear a cgm a i don't have mine on me right now but when you use on me right now but when you use a continuous glucose monitor that's**" — 20210722001.md [00:06:39.039] → [00:06:48.390]

**这是 R3 最大新临床工具**。他用 CGM 的具体方式是：戴在患者身上 → 显示餐后血糖"spike" → 患者**直观看到**碳水冲击 → **情绪性 land**（"permission" 来自动物实验 / 营养学 → 现在改为**直接生物反馈**）。Phase 2 临床应用矩阵应加 CGM 列。

#### 2.2 **Alzheimer's = "brain version of diabetes" 的显式个人化（APOE4 自报）**

R3 第一次把阿尔茨海默从"附加并发症"提升为**本人核心关切**：

- "**whether it's autoimmune disease prevention of dementias prevention of cancers so skin disease eye disease**" — 20210617001.md [00:03:27.519] → [00:03:29.190]
- "**especially saturated fat promotes dementia especially if you've got the apo e4 gene the runs in my family so the risk of dementia is very very high not only the pro-inflammatory nature of**" — 20210803001.md [00:09:51.680] → [00:10:02.870]
- "**then for anybody who has a history of alzheimer's in their family like i do i've got an apple e4 gene i've got a mother and a grandmother**" — 20220311001.md [01:10:09.440] → [01:10:14.950]
- "**and alzheimer's prevention same story so you know we demonize things because they're**" — 20220311001.md [01:12:18.560] → [01:12:23.510]
- "**i just have a history of alzheimer's so folks**" — 20220322001.md [00:08:56.720] → [00:09:00.230]
- "**over time it dies and we call that alzheimer's oh my gracious**" — 20220324001.md [01:20:51.840] → [01:20:55.669]
- "**are a problem so what do we get we get alzheimer's we get macular degeneration we get**" — 20220324001.md [01:21:56.400] → [01:21:59.990]

**关键一手素材**：
- **本人 APOE4 阳性**（"apple e4" 拼写错误是 Cywes 原话）+ 母亲 + 祖母均患阿尔茨海默 = **R3 第一次把自传从"300 磅"扩展到"基因风险"**
- 他**未使用 "type 3 diabetes"** 命名（Suzanne de la Monte 2005 起的术语），但**实质内容完全一致**（hyperinsulinemia → 大脑胰岛素抵抗 → 神经元死亡 → Alzheimer's）
- "alzheimer's prevention same story" = **统一的"碳水 + 炎症 + 胰岛素"模板**——意味着他**不区分 2 型糖尿病 / 阿茨海默 / 癌症**的病理机制，**只区分"下游疾病"**

**Phase 2 临床矩阵应新增"neurodegeneration"列**。**SKILL 表达 DNA 应包含"apoe e4 / apple e4 / brain insulin resistance"**。

#### 2.3 **Fructose 主题化（9 文件 / 28 命中）**

R3 第一次把 fructose 从"附加事实"提升为**独立专集主题**：

- 20220621001.md **14 次**（碳水化学专集）
- 20220622001.md **14 次**（碳水化学专集）
- 20210622001.md [00:02:50.480] "**glucose galactose fructose it doesn't matter here's a fundamental**"
- 20220302001.md [00:03:34.159] "**galactus is primarily coming from milk fructose coming from manufactured foods and fruits and glucose coming from most**"

R3 对 fructose 的论点是：
1. Fructose（果糖）只在**肝脏代谢** → **直接肝脂肪生成 → MAFLD / NAFLD**
2. Fructose **不触发 leptin**（瘦素）→ 饱腹感信号失灵 → **过量摄入**
3. Fructose 是 "**manufactured foods and fruits**" 的主要糖 — **天然 vs 加工的边界模糊**（这是他**与 carnivore 派的细微裂痕**）
4. 葡萄糖 + 果糖 = 蔗糖 = "**the commonest combination**"（20220621001.md [00:03:45.360]）

**Phase 2 临床应用应加 MAFLD / NAFLD 列**（R3 7 文件）。**SKILL 应写"fructose = liver-only metabolism = liver fat accumulation"** 的因果链。

#### 2.4 **Glp-1 / Ozempic 首次显式出现（1 文件 / 5 行）**

R3 第一次在视频中提到 GLP-1 激动剂：

- 20220512001.md [00:06:37.600] → [00:06:41.909] "**there's trulicity there is victoza but this over here this ozempic this over here this ozempic is an injectable drug**"
- 20220512001.md [00:06:58.960] → [00:07:04.150] "**and we slowly go up on the dose i stopped my ozempic at 0.5 trellisville 3.75 slightly different dosing regimen i**"
- 20220512001.md [00:09:33.040] → [00:09:34.710] "**unable to use and they're hyperglycemic so the cool thing about ozempic the cool**"

**关键点**：
- 他**本人曾使用 Ozempic**（"i stopped my ozempic at 0.5"）= **第一人称临床体验**（不是从外部评论）
- 他**未把 Ozempic 描述为"解决方案"**——而是描述为**辅助过渡工具**（"slowly go up on the dose"）
- 同时提到 Trulicity / Victoza = **GLP-1 类药物谱系**（不是单一品牌）
- **出现位置 = 2022-05-12**（R3 末尾），预示 v4+ 时代 Ozempic 会成核心议题

**Phase 2 不应让 Cywes 推荐 Ozempic 作为"治愈"**——R3 已表明他**本人使用过 + 已停止** + 视为辅助工具。

#### 2.5 **"17 years carb free" 首次显式声明（2 文件）—— 自传叙事的**年表漂移**

R1 = "19 year carb free"（2019-11 节点 → 推断 2000-2001 起步）
**R3 = "17 years"**（2021-12 节点 → 推断 2004-2005 起步）

- 20211216001.md（grep 命中 "17 years"）
- 20220311001.md（grep 命中 "17 years"）

**这是 v3 修正重点**：
- R1 = 19 年（2019-11）
- R2 = 应在 20-21 年（2020-2021）—— 但 R2 报告未确认（仅 1 文件）
- R3 = **17 年**（2021-12-16 / 2022-03-11）

**这说明 Cywes 的"年表自传"不是线性的——他在不同视频中会说不同的数字**。可能的解释：
1. **计算基准不同**（"carb free" vs "sugar free" vs "low carb"）
2. **记忆 / 表达漂移**（正常人也会这样）
3. **不同起始点**（300 磅时期 vs 决定性一天 vs 第一个月成功 vs 第一年成功）

**Phase 2 不可写"自 2000 年起"**——这是 R1 推断，**R3 已自我打脸**。**安全写法**："长期 low carb / 视频中本人声明 17 年 carb free（2021-2022 节点）"。

### 3. R3 反复出现的核心论点（≥3 次 = 真信念）

| 论点 | R3 命中文件数 | 性质 |
|---|---|---|
| **碳水是燃料、不是营养** | 全 100 文件 | 默认前提 |
| **"you become fat because you eat"** | 60+ | 默认前提 |
| **hyperinsulinemia 驱动 obesity / diabetes / dementia / cancer** | 7 + 10 + 18 = **35 文件交叉** | **R3 真正主线**（统一病理模型） |
| **"if you can't burn fat, you can't burn sugar"** | ≥10 | 反复出现 |
| **glucagon / insulin 跷跷板** | ≥30 | 反复出现 |
| **"two diseases: obesogenic & diabetogenic"** | 3 文件（**R2 = 9**） | **R3 收缩**（已默认化） |
| **"I went sideways"**（自传关键叙事） | 5 文件 | 反复出现 |
| **"best friend"**（指 best friend = carbohydrate） | 4 文件 | 反复出现 |
| **"we doctors are idiots"** | 未在 R3 频密出现 | R1/R2 默认化 |
| **"bowel movement"** | 4 文件 | 持续 |
| **"wallet biopsy"** | 4 文件 | 持续 |
| **"permission"**（反 harm reduction 立场） | ≥5 文件 | 持续 |
| **abstinence / abstain** | 7 文件 | 持续 |
| **relapse** | 13 文件 | 持续 |
| **stages of change / Prochaska** | 4 文件 | **R3 仍隐性**（未在标题出现） |
| **"you won't die of anorexia"**（IF 论证） | ≥5 文件 | **R3 新俗语** |
| **"emotional tension" / "dysfunctional emotional management"** | 11 文件 | 略降但**仍是核心治疗术语** |
| **OMAD / 5 days a week** | 2 文件 | R3 首次显式 OMAD 实践 |
| **"children get fed twice a day and they are not dying of anorexia"** | ≥2 文件 | **R3 新儿科修辞** |
| **"don't binge eat" / "go off the rails and binge"** | ≥3 文件 | **R3 relapse 语言扩展** |
| **Pediatric surgeon（自报）** | 10 文件 | 持续自报 |
| **Endocrinologist（自报）** | 5 文件 | 持续自报 |
| **Bariatric surgery（评论对象）** | 10 文件 | 持续 |
| **"I was fat"（隐晦）/ "I was 300 pounds"（明示）** | 14 文件 | **R3 自传频次上升**（17 文件提到 I was / I had been） |
| **Insulin + glucose + saturated fat 三元论** | 多文件 | 持续 |
| **"factory woman for sugar"** | 0（grep 未命中） | **R3 沉默** |
| **"McGovern was wrong"** | 3 文件 | 持续 |
| **"all-cause mortality"** | 17 文件 | **R3 持续引用**（但仍非 RCT 修辞） |
| **"apo e4 gene"**（自报） | 1 文件 | **R3 首次自报** |

### 4. R3 新增自创术语 / 显式新框架（**全部** R1+R2 未出现）

| 术语 / 框架 | 一手定义 / 出处 | R1+R2 状态 |
|---|---|---|
| **"apoe e4" / "apple e4"**（本人基因型自报） | 20220311001.md [01:10:09.440] → [01:10:14.950] | **R1+R2 = 0** |
| **"you won't die of anorexia"** | 20220210001.md [00:02:54.000]; 20220329001.md [00:01:54.799] | **R1+R2 = 0**（IF 临床化新俗语） |
| **"OMAD" / "one meal a day"** | 20220616001.md [00:10:06.560] "**eat two meals a day i drop that meal haven't died of anorexia yet folks but five days a week i'm omad one meal a**" | **R1+R2 = 0**（IF 实践显式） |
| **"don't binge eat"** | 20220607001.md [00:14:09.120] | **R1+R2 偶发**（"relapse" 隐含未点名） |
| **"go off the rails"** | 20220311001.md [00:16:54.880] | **R1+R2 = 0**（relapse 口语化新词） |
| **"the cool thing about ozempic"** | 20220512001.md [00:09:33.040] | **R1+R2 = 0**（本人使用 GLP-1 首次披露） |
| **"fructose coming from manufactured foods and fruits"** | 20220302001.md [00:03:34.159] | **R1+R2 偶发未专题化** |
| **"saturated fat promotes dementia especially if you've got the apo e4 gene"** | 20210803001.md [00:09:51.680] → [00:09:55.829] | **R1+R2 = 0**（饱和脂肪负面语境首次出现） |
| **"all-cause mortality"** | 17 文件 | **R1+R2 偶发**（R3 持续但非 RCT） |
| **"MAFLD / NAFLD"** | 7 文件 | **R1+R2 偶发**（R3 系统化） |
| **"atherogenic dyslipidemia"** | 偶发 | R1+R2 0 |
| **"two diseases" / "obesogenic & diabetogenic"** | 3 文件 | **R1+R2 = 9 文件**（R3 收缩，但仍是术语） |
| **"TMAO"** | 20220414001.md | **R1+R2 = 0** |
| **"gut microbiome"** | 20210730001.md | R1+R2 偶发 |
| **"children get fed twice a day"** | 20210629001.md [00:08:47.839] | **R1+R2 = 0**（儿科自报整合） |
| **"I am mostly carnivore"** | R2 = 1 | **R3 沉默**（已默认化） |
| **"all-cause mortality + keto"** | 17 + 多 keto | R3 默认前提 |
| **"apo e4 runs in my family"** | 20210803001.md [00:09:59.040] | **R1+R2 = 0** |
| **"A1C / HbA1c"** | 13 文件 | R1+R2 偶发（R3 持续使用） |

### 5. R3 仍未出现（v3.0 R3 验证 = 任务背景警示）

1. **"transfer addiction"** — R1 = 0 / R2 = 0 / **R3 = 0**。**vN 全期未出现。** 任务背景列为"应有"——这是 v2 误植。
2. **"low-fat lie"** — R1 = 0 / R2 = 0 / **R3 = 0**。**vN 全期未出现。** 任务背景列为"R2 标签"——**v3 修正：Cywes 不用这个短语。**
3. **"five white assassins" / "五白刺客"** — R1 = 0 / R2 = 0 / **R3 = 0**。**vN 全期未出现。**
4. **"carbon score"** — R1 = 0 / R2 = 0 / **R3 = 0**。**vN 全期未出现。**
5. **"harmed reduction"** — R1 = 0 / R2 = 0 / **R3 = 0**。
6. **"12 step / AA meeting"** — R1 = 偶发 / R2 = 偶发 / **R3 = 0**。**R3 显著收缩**——他**不采用 12 步修辞**，而是用 Prochaska TTM + 自创 "emotional tension" 框架。
7. **"first bite"** — R1 = 1 / R2 = 1 / **R3 = 1**（保持极低频）。**vN 稳定术语但非高频招牌**。
8. **"GLP-1 / semaglutide / Ozempic"** — R1 = 0 / R2 = 0 / **R3 = 1**（20220512001.md）。**R3 末首次显式，本人是用户**——预示 v4 时代会成为核心议题。
9. **"continuous glucose monitor / CGM"** — R1 = 偶发 / R2 = 8 / **R3 = 14**。**R3 主题化**。
10. **"evidence-based" / "RCT" / "Cochrane"** — R1 = 0 / R2 = 0 / **R3 = 0**。**Cywes 全期不用 EBM 修辞**——这是**重要的负向发现**。
11. **"apoB"** — R1 = 0 / R2 = 0 / **R3 = 0**。**他不接 Attia 学派的 lipid 框架**——他**用 LDL（19 文件）但不用 apoB**。
12. **"Perlmutter" / "Grain Brain"** — R1 = 0 / R2 = 0 / **R3 = 0**。**他不引用 Perlmutter**——尽管两人议题高度重合。
13. **"Westman"** — R1 = 0 / R2 = 1 / **R3 = 6 文件**（20210629 / 20211109 / 20211216 / 20220121 / 20220324 / 20220505）。**R3 持续引用 Westman**——这是他**学术盟友中唯一高频出现者**。
14. **"Eenfeldt / Harcombe / Berg / Attia / Chaffee / Baker"** — R2 = 4 文件 / **R3 = 0**。**R3 反而沉默 R2 盟友引用**——可能是 R2 一次性提及后未深化。
15. **"factory woman for sugar"** — R1 = 多 / R2 = 偶发 / **R3 = 0**（grep 未命中）。**R3 显著收缩**——他不再用这个短语。

### 6. R3 临床应用扩张矩阵（**R2 → R3 增量**）

| 临床应用 | R2 命中 | **R3 命中** | 增量 / 变化 |
|---|---|---|---|
| Obesity / weight loss | 全 100 | **全 100** | 默认 |
| Type 2 diabetes | 多 | **18 文件** | 持平 |
| Type 1 diabetes | 偶发 | **8 文件** | **R3 扩张**（"how much insulin do you need"） |
| Cancer | 14 | **18 文件** | **+4（持续扩张）** |
| Alzheimer's / dementia | 7 | **10 文件** | **+3（本人 APOE4 自报 → 私人化）** |
| PCOS | 9 | **14 文件** | **+5** |
| Fertility / infertility | 多 | **14 文件** | 持平 |
| Pregnancy / gestational | 多 | **（含 14）** | 持平 |
| Pediatric surgery | 多 | **10 文件** | 持平（自报） |
| Childhood obesity | 多 | **27 文件** | 持平（"children get fed twice a day"） |
| Autism | 5 | **5 文件** | 持平 |
| ADHD | 3 | **3 文件** | 持平 |
| Anxiety / depression | 18 | **14 文件** | **-4**（已"默认化"） |
| NAFLD / fatty liver | 7 | **7 文件** | 持平（fructose 主题化后内嵌） |
| Autoimmune | 16 | **16 文件** | 持平 |
| Cardiovascular / heart | 30+ | **36 文件** | 持平 |
| Bariatric surgery（评论） | 10 | **10 文件** | 持平 |
| Endocrinologist（自报） | 多 | **5 文件** | 持平 |
| Gout / uric acid | 12 | **12 文件** | 持平 |
| Skin (acne/eczema/psoriasis) | 30+ | **44 文件** | **+14**（"skin disease" 持续） |
| Eye disease / macular degeneration | 偶发 | **（含 Alzheimer 文件）** | 略升 |
| Thyroid | 12 | **15 文件** | 略升 |
| Continuous glucose monitor（CGM） | 8 | **14 文件** | **+6（临床工具化）** |
| GLP-1 / Ozempic | 0 | **1 文件** | **+1（首次显式 + 本人使用）** |
| 17 year carb free（自报） | 0 | **2 文件** | **+2** |

**R3 临床应用扩张主线**：
- **CGM = R3 标志性新工具**
- **Alzheimer + APOE4 = R3 私人化（本人基因）**
- **Fructose = R3 主题化（碳水化学专集 ×2）**
- **GLP-1 = R3 末首次显式**
- **T1DM 扩张** = 他开始用同样框架处理 T1DM
- **Skin 仍高密度** = 持续（44/100）
- **Anxiety/depression 收缩** = 已"默认化"（隐含不显式）
- **OB/DB 收缩** = 已"默认化"（obesogenic/diabetogenic 术语仍是但 3 文件）

### 7. R3 关键时间锚点（Phase 2 引用准确性参考）

| 日期 | 事件 / 锚文件 |
|---|---|
| **2021-06-17** | 17-year carb free 周边——bariatric 临床（"did that with our bariatric surgery patients"） |
| **2021-06-29** | Pediatrics + anorexia 修辞首次出现 |
| **2021-07-22** | CGM 首次工具化讨论 |
| **2021-08-03** | **APOE4 自报** + "saturated fat promotes dementia" + "runs in my family" |
| **2021-08-10** | CGM 临床实例："got a cgm started measuring her numbers" |
| **2021-08-17** | Cortisol / endocrine axis 深入 |
| **2021-11-04** | PCOS 临床扩张（与 R2 一致） |
| **2021-12-16** | **"17 years carb free"** 自报首次显式（**叙事漂移信号**） |
| **2021-12-31** | ADHD + 儿科整合 |
| **2022-01-18** | T1DM 应用扩张 |
| **2022-02-10** | "you won't die of anorexia" 反复出现 |
| **2022-03-02** | Fructose 主题化 + 加工食品 vs 水果边界 |
| **2022-03-11** | "I've got an apple e4 gene" + "17 years carb free" 双自报 |
| **2022-03-22** | "I just have a history of Alzheimer's so folks" |
| **2022-03-24** | Long file（2991 lines）——obesogenic/diabetogenic 4 命中 + Alzheimer 详论 |
| **2022-04-10** | Long file（2700+ lines）——obesogenic 4 命中 + PCOS 临床 + LDL + 甲状腺 |
| **2022-05-12** | **Ozempic 首次显式 + 本人使用披露**（"I stopped my ozempic at 0.5"） |
| **2022-06-21** | **碳水化学专集 ×14 次 fructose** |
| **2022-06-22** | **碳水化学专集 ×14 次 fructose** |
| **2022-06-28** | R3 时间窗末端 |

### 8. R3 备注给 Phase 2 / Phase 3

1. **R3 真正新发现 = APOE4 自报 + CGM 临床化 + Fructose 主题化 + Ozempic 本人使用披露**——这 4 项是 R1+R2 都没有的，**Phase 2 必须收录**。
2. **"keto moment" / "keto clutter" / "safe haven" / "Jane Brown" 在 R3 全部沉默**——R2 的"组织演化"叙事**在 R3 没继续**。**这暗示 R2 那一波命名是"过性"的，不是稳定品牌**。**Phase 2 不应强调"Cywes 诊所 = Cywes + Jane Brown"——R3 显示 Jane 不再是显式合作伙伴**。
3. **"17 years carb free" 出现**——R1 = 19 年 / R3 = 17 年。**叙事漂移是事实**。**Phase 2 写法："视频中本人声明 17-19 年 carb free（取决于视频）"——不锁定具体年份**。
4. **"emotional tension" 仍在 R3 出现 11 文件**——R2 的"显式命名"被 R3 继承并稳定。**Phase 2 表达 DNA 必须包含**。
5. **obesogenic/diabetogenic 术语在 R3 收缩（9 → 3 文件）**——但 R3 长文件（20220324 / 20220410）仍密集使用。**Phase 2 应保留这对术语，但降为"高级术语"而非"招牌"**。
6. **CGM = R3 真正新临床工具**——Phase 2 临床应用矩阵必须新增 CGM 列。**他用 CGM 的方式 = 实时生物反馈 + 情绪性 land + 替换抽象营养学的可视化工具**。
7. **APOE4 = R3 真正新自传素材**——本人基因型 + 母亲 + 祖母 = 他**第二次把自传从"300 磅"扩展到"基因"**。**Phase 2 表达 DNA 应包含"apoe e4" / "apple e4"**。
8. **Ozempic 首次显式**——本人曾使用 + 已停止 + 视为辅助工具。**Phase 2 不应让 Cywes 反对 GLP-1——R3 已表明他本人用过**。
9. **Fructose 主题化**——Phase 2 临床应用应加 MAFLD/NAFLD 列，**SKILL 应写"fructose = liver-only metabolism = liver fat"的因果链**。
10. **T1DM 扩张**——R3 = 8 文件（vs R2 偶发）。**他开始用同样框架处理 T1DM**——"how much insulin do you need"是 T1DM 的 cywes 化语言。
11. **Eenfeldt / Harcombe / Berg / Attia / Chaffee / Baker 全部 R3 沉默**——R2 的 4 文件引用是**一次性**，不是稳定盟友。**Phase 2 不应写"长期合作"**。
12. **Westman 仍持续**（R3 = 6 文件 / 11 命中）——是**唯一稳定的学术盟友**。**Phase 2 可写"Westman 是高频盟友引用"**。
13. **Perlmutter 仍 0**——两人议题重合（Alzheimer）但不互相引用。**Phase 2 不可写"Perlmutter 盟友"**。
14. **EBM 修辞（RCT / Cochrane / evidence-based）全期 0**——Cywes 的引用风格**始终是临床轶事 + 个人叙事 + Westman 类盟友引用**，不走 EBM 修辞。**Phase 3 表达 DNA 应保持这种"反 EBM"风格**。
15. **"五白刺客" / "carbon score" / "low-fat lie" / "transfer addiction" vN 全期 0**——v2 任务背景错误，**v3 已彻底否定**。**SKILL 不应包含这些**。
16. **CGM + Fructose + APOE4 + Ozempic = R3 4 大新主题轴**——Phase 2 SKILL 心智模型应反映"统一病理模型 = hyperinsulinemia → 任何下游（diabetes / cancer / Alzheimer / obesity / PCOS / skin）"。

### 9. R3 整体定性（一手 / 二手 / 我推断）

| 类别 | 内容 |
|---|---|
| **一手** | 所有 grep 命中行（标 [文件名.md HH:MM:SS]） |
| **一手** | APOE4 自报（20220311001.md + 20210803001.md + 20220322001.md） |
| **一手** | Ozempic 本人使用披露（20220512001.md） |
| **一手** | "17 years carb free" 自报（20211216001.md + 20220311001.md） |
| **一手** | CGM 14 文件 / Fructose 9 文件 / Alzheimer 10 文件 |
| **二手** | Cywes 引用 Westman（6 文件）—— Westman 是 Duke 大学低碳水临床研究 leader，**事实外部可查** |
| **二手** | Cywes 不引用 Perlmutter / Berg / Attia / Chaffee / Baker —— **这是观察**，**不是他本人的声明** |
| **我推断** | "叙事漂移"（19 年 vs 17 年）—— **是观察**，**可能解释包括计算基准不同 / 记忆漂移 / 多次起步** |
| **我推断** | R3 沉默 R2 盟友（Eenfeldt / Harcombe / Berg / Attia）—— **是观察**，**可能解释包括 R3 注意力转向 CGM/Fructose/Ozempic** |
| **我推断** | "统一病理模型"（hyperinsulinemia → 任何下游）—— **是观察性抽象**，**不是他本人的话** |
| **我推断** | "他开始用同样框架处理 T1DM" —— **是观察**（8 文件 T1DM 命中），**不必然等于"扩张"** |
| **不做** | 不评价"主流医学共识" / 不写"局限性" / 不评价"诚信风险" / 不补全外部生平 |

### 10. R3 vs R1+R2 整体趋势（一句话总结）

**R3 = 2021-06 → 2022-06 = "Cywes 成熟期（第二年）"**：框架（carb addiction + harm reduction 反 + hyperinsulinemia + emotional tension + Prochaska）**已完全默认化**（不再显式命名），**临床工具从"营养学建议"转向"生物反馈（CGM）+ 制药辅助（Ozempic）+ 个人基因（APOE4）"**。**新主题轴 = CGM 临床化 + Fructose 主题化 + APOE4 私人化 + GLP-1 首次显式**。**未采纳 = transfer addiction / low-fat lie / 5 white / carbon score / 12 step / apoB / EBM 修辞**。


## Round 4 (2022-06-28 → 2023-06-16) — Phase 1 Agent 1

**调研范围**：`/tmp/cywes_v3_r4_files.txt`（排序后第 301-400 个 .md 文件，100 个 VTT 字幕）
**时间跨度**：2022-06-28 → 2023-06-16（≈ 12 个月）
**承接 R1+R2+R3**：grep+精读独立进行；R1 已建立 carb addiction 八股 / R2 加入 carnivore 主题轴 / R3 加入 CGM+Fructose+APOE4+Ozempic；本轮查找 R1+R2+R3 缺失的新主题（1963 JFK 命名 / 父亲 COVID 死亡 / 2023-08 Noakes 主编 ketogenic textbook 撰 3 章节 / Banting 1921 史 / 新时间锚 / 关键源文件）

**R4 关键差异**：
- **Noakes 2023 ketogenic textbook + Cywes 撰章节** = R4 头号新发现（R3 报告遗漏，因 R3 时间窗 2022-06-28 截止，本信号首次浮出于 2022-12-18 的 Noakes 长访谈）
- **"The Randle Cycle" 专集 = R4 重大学术节点**（1963-04-13 Lancet / Cambridge Dept of Biochemistry / Philip Randle 团队）
- **"17 years carb free" 漂移**在 R4 仍持续（已 R3 已记录的叙事漂移）
- **Ozempic 临床化**继续（multiple GLP-1 mentions）
- **CGM 实践化**：Cywes 自报佩戴 Dexcom 6
- **父亲死亡时间明确**："two years ago in the beginning of the covert era" → 约 2020 春夏
- **APOE4 自报在 R4 持续**（多次提到母亲 + 母亲母亲）
- **Cape Town / South Africa = Cywes 自报 hometown**（在 20220711001 明确）

---

### 1. R1+R2+R3 vs R4 grep 命中数对比

| 关键词 / 模式 | R1+R2+R3 状态 | **R4 命中** | 变化 / 解读 |
|---|---|---|---|
| `JFK\|Kennedy\|November 22`（R1+R2+R3 任务背景列为应有，0 命中）| 0 | **0** | **R4 仍 0 命中**——JFK 命名未被 Cywes 本人引述，**v2 任务背景疑为误植** |
| `father\|dad\|died\|covid\|prednizo` | 多文件 | **20+ 文件** | R4 显著——父亲 2020 COVID 死亡多次被提 |
| `Banting\|1921\|insulin discovery` | 0 | **3 文件** | **R4 首次**——Banting/Best 1910s-1921 史首次显式 |
| `Noakes\|ketogenic textbook\|ketogenic bible` | 偶发 | **4 文件**（含 20221218001 1 小时长访谈）| **R4 大幅扩张**——Noakes 主编 textbook 是 2023-03 出版项目 |
| `Philip Randle\|1963\|Lancet\|Cambridge.*biochem\|glucose fatty acid` | 0 | **3 文件 ×14 次**（Ep:276 + Ep 续 + 11-10 引用）| **R4 重大新发现**——Randle cycle 1963 论文深挖成专集 |
| `carb addict\|carbohydrate addict` | 63+93+高 | **高频（默认前提）** | 默认化 |
| `first bite` | 1+1+1 | **1（沿用）** | 稳定但非高频 |
| `hyperinsulin` | 5+9+7 | **仍出现** | 持平 |
| `keto\|fasting` | 77+77+83 | **高频** | 持平 |
| `carnivore` | 41+49 | **仍出现** | 持平 |
| `obesogenic\|diabetogenic` | 7+4+3 | **5+ 文件** | R4 略回升 |
| `Prochaska\|stages of change\|TTM\|transtheoretical` | 1+1+4 | **4 文件** | **R4 显式化回升** |
| `CGM\|Dexcom\|continuous glucose` | 偶发+8+14 | **多文件** | 持平 / 默认化 |
| `Ozempic\|semaglutide\|GLP-1` | 0+0+1 | **多文件（Ozempic 多用）** | **R4 临床化** |
| `fructose\|HFCS` | 9+9 | **多文件** | 持平 |
| `APOE4\|apple e4` | 1 | **多文件持续** | R3 引入 / R4 持续 |
| `17 years carb free` | 2 | **多文件** | **R4 漂移持续** |
| `book\|publish\|chapter` | 0 | **多文件 / Noakes 专集×10+** | **R4 重大新发现** |
| `evidence-based\|RCT\|Cochrane` | 0 全期 | **0** | **R4 仍 0**——Cywes 始终不走 EBM 修辞 |
| `transfer addiction\|low-fat lie\|five white\|carbon score` | 0 全期 | **0** | **vN 全期仍未出现** |
| `Eenfeldt\|Harcombe\|Berg\|Attia\|Chaffee\|Baker` | 0 / 0 | **Noakes 显著（4 文件）** | **R4 唯一显著盟友 = Tim Noakes** |
| `Perlmutter\|Westman` | Westman 6 文件 / Perlmutter 0 | **Westman 偶发** | Westman 引用减少 / Perlmutter 仍 0 |
| `Cape Town\|South Africa\|hometown` | 0 命中 | **多文件** | **R4 新自传素材**：Cywes 明确 hometown = Cape Town |

**R4 最高密度文件**（按 grep 命中数）：
1. 20221218001.md — **Noakes 1 小时长访谈**（标题 "INTIMATE CONVERSATION WITH TIM NOAKES – MUST WATCH"）— Noakes 主编 textbook / Cywes 撰 3 章节
2. 20221229001.md — **Ep:276 THE RANDLE CYCLE - EXPLAINED AND DEMYSTIFIED**（Randle 1963 论文深挖）
3. 20230101001.md — **THE RANDLE CYCLE EXPLAINED AND THE MYTHS DEBUNKED. FAT AND OBESITY DO NOT CAUSE DIABETES**（续集 + 同一 Randle 论文）
4. 20221025001.md — Ep:264 PROOF THAT PLANTS AND VEGANISM IS NOT A HUMAN DIET（含父亲 2020 死亡自传 + orchid hybridizer 父亲细节）
5. 20230113001.md — 含家族病史（父亲 stroke + 父亲 half-brother 45 岁 heart attack）

---

### 2. R4 5-10 个新发现（带时间戳一手引文）

#### 发现 R4-1（**R4 头号新发现**）：Cywes 参与 Noakes 主编 ketogenic textbook 撰 3 章节——2023-03 出版

**核心发现**：在 2022-12-18 发布的 1 小时 Noakes 长访谈中，Cywes 透露 Noakes 主编的 ketogenic textbook 即将于 **2023-03 出版**，由 **62 位国际作者** 共同撰写，**8 章节**（不是 11 章节——Noakes 修正了 2 次），其中 **Cywes 撰 3 章节**。

> "we got the people who are absolutely up to date writing for us ... **having experienced that myself with a couple of chapters that I produced** uh was absolutely incredible to see how fastidious they were" — **20221218001.md [00:31:00.840] → [00:31:13.250]**

> "there are some chapters which you'll really enjoy so **I wrote a couple on the human diet understanding the human diet that we've been** Mickey bendor who's just an absolute giant I also read a chapter on cancer as a modern disease and then there's another one on how the **dietary guidelines were abused and how they can came about**" — **20221218001.md [01:03:16.200] → [01:03:37.849]**

> "talking about book that's going to be **published in I think March of next year**" — **20221218001.md [00:27:30.179] → [00:27:34.450]**（**next year 相对 2022-12-18 = 2023-03**）

> "we found **62 authors from around the world**" — **20221218001.md [00:29:23.700] → [00:29:31.970]**

> "the **possible topics there are something like 11 chapters** oh sorry let me just check that I think it's **eight chapters and they cover the whole body**" — **20221218001.md [00:31:29.220] → [00:31:40.669]**

**Noakes 解释发起来源**：
> "Neville Wellington who was one of the first doctors in Cape Town to start doing the low-carb diet ... Hasina came along ... **she said you know if we're going to make low carbs really acceptable we have to have a textbook**" — **20221218001.md [00:28:11.279] → [00:29:04.010]**

**出版方 / 收益分配**：
> "the proceeds of the book going to go to what what is the where ... so it will all go back into the system ... to the work of the nutrition Network" — **20221218001.md [00:59:41.880] → [01:00:22.609]**

**目标读者**：
> "is the book uh reasonable for Lay people who have no medical knowledge or is this just for doctors and scientists no there are some chapters which you'll really enjoy so I wrote a couple on the human diet understanding the human diet" — **20221218001.md [01:03:07.740] → [01:03:24.000]**

**Cywes 撰写的 3 章节主题**（一手本人声明）：
1. **Human diet / understanding the human diet**（与 Mickey Bendor 并提）
2. **Cancer as a modern disease**（这是 Noakes 介绍其他人写的章节，但 Cywes 说他 "also read a chapter on cancer as a modern disease"——读但未必写）
3. **How the dietary guidelines were abused and how they came about**（这与 Noakes 1990s 反 McGovern 运动一脉相承）

> 注意：Cywes 实际**写**的章节数他自己用 "a couple" + 后续罗列 = **2-3 章节**。Noakes 在同访谈中明确说 "**a couple of chapters that I produced**" + Cywes 自报"a couple on the human diet"。**安全推断：Cywes 写 2-3 章节**。

**任务背景的"Noakes 2023-08 主编 ketogenic textbook Cywes 撰 3 章节"——R4 验证**：
- ✅ Noakes 主编：确认
- ✅ Cywes 撰 2-3 章节：确认（他用 "a couple" + 后文罗列 3 个）
- ✅ 2023 出版：确认（2022-12 访谈中预告 2023-03）
- ❓ 8 章节 vs 11 章节：Noakes 本人先说 11 后修正为 8
- ❓ 出版月份是 2023-03（Noakes 访谈中预告）vs 任务背景写的 2023-08——**任务背景可能误植出版月份**

**Phase 2 写入 SKILL 的安全版本**：Cywes 参与 Noakes 主编 ketogenic textbook，2023 出版（精确月份 = 2023-03 Noakes 自预告），Cywes 写 "a couple of chapters"（2-3 章节），主题包括 human diet / dietary guidelines 滥用。

---

#### 发现 R4-2（**R4 重大学术节点**）：Philip Randle 1963 论文深挖成专集

> "**Saturday the 13th of April 1963 1963 59 years ago** Philip Randall and his group at the University of Cambridge uh **Department of biochemistry** wrote a **summary paper** and it's the **glucose fatty acid cycle its role in insulin sensitivity and the metabolic disturbances of diabetes mellitus**" — **20221229001.md [00:02:33.860] → [00:02:55.739]**

> "in uh in **the Lancet** the one of the most prestigious medical journals uh in the world" — **20221229001.md [00:02:24.000] → [00:02:30.470]**

> "I've heard a lot of talk uh from people oh the Randall cycle explains this and it's **fat that causes diabetes** ... the **causal [ __ ]** that you know I rail against because this is just explaining part of how the body works" — **20221229001.md [00:01:44.880] → [00:01:59.929]**

**关键事实**：
- **论文** = "The glucose fatty acid cycle: its role in insulin sensitivity and the metabolic disturbances of diabetes mellitus"
- **作者** = Philip Randle 团队（**Randle / Garland / Hales / Newsholme**——经典 4 作者组）
- **机构** = University of Cambridge, Department of Biochemistry
- **期刊** = The Lancet
- **发表日期** = **1963-04-13（星期六）**（Cywes 在 2022-12-29 解读为"59 年前"）
- **Cywes 立场** = "this is just explaining part of how the body works"——**他承认 Randle 论文有效，但反对"脂肪导致糖尿病"的过度简化**（fat doesn't cause diabetes = R4 标题明示："FAT AND OBESITY DO NOT CAUSE DIABETES"）

**续集 / 重复**：
> 20230101001.md "THE RANDLE CYCLE EXPLAINED AND THE MYTHS DEBUNKED" — 同一论文重复解读 + 攻击"脂肪导致糖尿病"误读

**Phase 2 临床应用矩阵应加"学术锚点"列** = Randle cycle 是 Cywes 反复引用的"glucose vs fat 燃料竞争"基础科学依据。**这是他少有的"引用具体作者 + 论文标题 + 发表日期"的高精度学术引用**——他通常不写完整论文标题。

---

#### 发现 R4-3（**R4 重大自传更新**）：父亲 2020 春夏死于 COVID 时代（不是 prednizone）

> "my father who **passed away two years ago from uh in the beginning of the covert era uh spent a large part of his self-care life hybridizing orchids** in particular an awkward called a **dyzer disa** if you've never heard of it please google it it's the some of the most beautiful beautiful orchids that I'm absolutely passionate about beautiful colors but he hybridized them" — **20221025001.md [00:00:47.640] → [00:00:58.670]**

**关键事实**：
- **父亲死亡时间** = "two years ago"（相对 2022-10-25）= **2020 末**；"in the beginning of the covert era" = **2020 春夏 COVID 初期**
- **父亲爱好** = 兰花杂交（orchid hybridizer），专攻"Disa"（一种稀有的非洲兰花）
- **父亲自我照护方式** = "spent a large part of his self-care life" hybridizing orchids = **植物学/园艺作为 coping**（与 Cywes 自己的咖啡 go-to coping 类比）
- **死亡原因** = 视频中 Cywes **没有显式说"COVID"或"prednizone"**——他只说"in the beginning of the covert era"（COVID 时代开端）
- **任务背景的"2020-04 prednizone"** = **R4 未直接证实 prednizone**，但"beginning of covert era"= 2020 春

**配套引用**（不一定是同一父亲）：
> "since **my father passed away** we have in her in a regular daily exercise" — **20220812001.md [00:36:14.480] → [00:36:19.510]**

> "my mom site has really high prevalence of diabetes **my late dad died of stroke he had a heart attack before that** half brother on my on my dad's side also passed away a few years ago at the age of **45 from a heart attack** so those two combinations within my maternal and fraternal uh um sort of family or paternal uh family it's it's very it's **a recipe for disaster** if I don't look after myself" — **20230113001.md [00:13:58.079] → [00:14:25.440]**

**Phase 2 写法安全版本**：
- 父亲 ~2020 死亡（"in the beginning of the covert era"）——**不锁定 2020-04**
- 父亲 = 兰花杂交爱好者
- 父亲死因 = 视频中未显式
- 家族病史 = 父亲 stroke + 父亲 half-brother 45 岁 heart attack = **"recipe for disaster"**（Cywes 自评）
- **不要在 SKILL 写 "prednizone 导致父亲死亡"**——视频无此明示，**任务背景的"prednizone"细节 R4 未能验证**

---

#### 发现 R4-4（**R4 新自传**）：Cywes 自报 hometown = Cape Town, South Africa

> "I'm on vacation in beautiful **South Africa Cape Town my hometown**" — **20220711001.md [00:00:06.180] → [00:00:11.150]**

> "I'm obviously I I'm a **South African by birth** but I live and work in **Florida in the United States** I am a clinically practicing doctor and surgeon uh in **West Palm Beach in Florida**" — **20220804001.md [00:01:44.759] → [00:01:56.149]**

**关键事实**：
- **出生地** = South Africa（Cape Town 是 his hometown = 出生长大地）
- **现居** = West Palm Beach, Florida, USA
- **现执业** = 临床执业医生 + 外科医生
- **R1+R2+R3 未明确"hometown = Cape Town"** —— R4 首次自报 hometown
- **20220830001.md "my mother lives in south africa she's in her late 80s"**——母亲仍住南非，年近 90

**Phase 2 修正**：SKILL 写 "Cywes 出生于南非开普敦，现居美国佛罗里达西棕榈滩"——这是 R4 新增一手素材。

---

#### 发现 R4-5（**R4 临床工具化**）：Cywes 自报佩戴 Dexcom 6 CGM

> "huge sugar crush i wear a cgm a lot and i've had no maybe i'm just used to it but i wear the **dexcom six** and i don't have one on i'm gonna be putting it on this weekend" — **20220818001.md [00:33:49.519] → [00:33:57.190]**

**关键事实**：
- Cywes **本人使用 CGM**（Dexcom G6 = 2020 FDA 批的 G6 型号）
- 他**日常佩戴 CGM**（"i wear a cgm a lot"）
- 这与 R3 报告的"CGM 14 文件"一致——**R4 显示 Cywes 本人是 CGM 用户 + 推广者**

**Phase 2 写法**："Cywes 临床使用 CGM（Dexcom G6）作为生物反馈工具"——这是从 R3 "CGM 概念"到 R4 "CGM 实践"的关键升级。

---

#### 发现 R4-6（**R4 叙事漂移持续**）："17 years carb free" 漂移在 R4 继续

R3 已记录：
- R1（2019-11）= 19 年 → 推断 2000-2001 起步
- R3（2021-12 / 2022-03）= **17 年** → 推断 2004-2005 起步

**R4 新发现**：
- "**I'm 25 years in folks lost my weight 24 25 years ago**" — **20230125001.md [00:03:46.019] → [00:03:50.690]**

**这意味着 R4 节点 = 25 年**（相对 2023-01 推断 1998 起步）——**新一次叙事漂移**。

**Phase 2 安全写法（最终修正）**："视频中本人声明 carb free 17-25 年（取决于视频）"——**不要锁定具体起始年**。**v3 修正：Cywes 的"年表自传"不是线性的，他在 2019-2023 间多次说不同数字**。

---

#### 发现 R4-7（**R4 主题化**）：Prochaska "stages of change" + "Changing for Good" 显式化

> "introduced me to a book that was written by a group out of **connecticut** um lead author by the name of **prochaska** and the **book's name is changing for good** and what these guys did is they they looked at a group of folks who **successfully quit smoking** and they went back and analyzed the various **stages of change** and **i've done some talks on that before**" — **20220922001.md [00:01:24.640] → [00:01:48.069]**

**关键事实**：
- **Prochaska & DiClemente "Changing for Good"** = 1994 出版，**Cywes 在 R4 显式引用完整书名 + 出版地（Connecticut）+ 原始研究对象（戒烟成功者）**
- **Cywes 把 TTM 定位为"我做过的 talks"** = **他把 TTM 纳入了自己的演讲 / 培训体系**
- **R1+R2+R3 中 TTM 显式引用 1-4 文件**——R4 显式回升（多次用 stages of change + precontemplation）

**配套引用**：
> "where a patient is on the Continuum of the **stages of change** so at the top you see the **pre-contemplation stage**" — **20230211001.md [00:04:34.680] → [00:04:39.530]**

> "i i was put on **steroid hormones** when i was 15 years old because ... **pre-contemplative stage**" — **20220922001.md [00:09:24.959] → [00:09:28.949]**

**Phase 2 临床应用应把 TTM 显式化**——R4 显示 Cywes 把 TTM 视为"演讲模块"而非"隐藏脚手架"。

---

#### 发现 R4-8（**R4 临床应用**）：Banting / Best 1910s + 1921 史首次显式

> "in 1921 **banting in in toronto discovered and found insulin**" — **20220708001.md [00:00:54.960] → [00:01:01.189]**

> "they knew about **insulin from the diabetes days from Banting and Best work in the 1910s** and they knew about fat and" — **20221229001.md [00:10:57.600] → [00:11:03.350]**（重复于 20230101001.md）

**关键事实**：
- **Cywes 引用 Banting & Best 1921 多伦多胰岛素发现**
- **时间点** = "1910s and 1921"——这是医学史锚点
- **R1+R2+R3 0 命中 Banting/Best**——R4 首次显式
- **任务背景的"Banting 1921 史" R4 验证** ✅

**Phase 2 学术史锚点**：Cywes 在 R4 引用 Banting & Best 1921 作为糖尿病研究的"原始科学事件"。

---

#### 发现 R4-9（**R4 临床应用**）：OBE4 / APOE4 持续自报

R3 已记录 APOE4 自报。R4 持续：

> "i have the **apoe4 gene** i have **one allele of it got that from my mom** she got it from her mother ... my mom lives in south africa she's in her late 80s ... fortunately we've been able though **my father has passed** we've been able to keep her going" — **20220830001.md [00:01:51.040] → [00:07:08.790]**

> "I **bumped into** a patient the other day who came to my office ... and just trying to find a crack in that veneer because i know she desperately wanted help" — **20220922001.md [00:01:50.560] → [00:02:35.589]**（治疗学细节）

**关键事实**：
- **APOE4 等位基因** = 1 个（杂合）
- **来源** = 母亲（母亲从外祖母获得）
- **母亲** = 现年近 90，住南非，由 Cywes + 团队 + 妻子 + 1 位 caregiver（Henrietta）照护
- **父亲已逝** = 见发现 R4-3

**Phase 2 SKILL 应包含**：APOE4 自报 + 母亲 80s + 父亲 2020 逝 + 家族心脏代谢病史 = "Cywes 把自己定位为高基因风险的患者"。

---

#### 发现 R4-10（**R4 临床工具**）：Ozempic 临床化继续

R3 已记录 Ozempic 首次显式。R4 持续：

> "Because **insulin is triggered by a hormone in the stomach called GLP-1** ... **glucagon-like peptide 1**" — **20220728001.md [00:56:57.840] → [00:57:04.710]**

> "the recovery of insulin sensitivity by using **glp-1 agonists for a little while**" — **20220818001.md [00:31:16.960] → [00:31:21.509]**

**关键事实**：
- R4 显示 Cywes 进一步把 GLP-1 描述为**"恢复胰岛素敏感性的辅助"**（"for a little while"）
- R3 透露他本人使用 Ozempic，R4 仍把 GLP-1 描述为**短期辅助**而非"解决方案"

**Phase 2 临床应用应写**：Cywes 临床使用 GLP-1 激动剂（本人使用 Ozempic 已停止）—— R4 显示他**仍用"短期辅助"框架**。

---

### 3. R4 仍未发现（v3.0 R4 验证 = 任务背景警示）

1. **"JFK / Kennedy / November 22 / 1963-11-22 出生 / 命名"** — R1 = 0 / R2 = 0 / R3 = 0 / **R4 = 0**。**vN 全期未出现**。**任务背景的"1963-11-22 出生 / JFK 命名"R4 仍 0 命中**——**这是 v2 误植**。**SKILL 不可写"Cywes 1963-11-22 出生 / JFK 命名"**。
2. **"prednizone"** — R4 0 命中（搜 prednizo / prednizone / steroid hormone 仅作"15 岁时用 steroid hormone" 等无关命中）。**任务背景的"父亲 2020-04 死于 prednizone"细节 R4 未能直接证实**——Cywes 视频中只说父亲"in the beginning of the covert era"去世，未提 prednizone。
3. **"transfer addiction"** — R1 = 0 / R2 = 0 / R3 = 0 / **R4 = 0**。vN 全期未出现。
4. **"low-fat lie"** — R1 = 0 / R2 = 0 / R3 = 0 / **R4 = 0**。vN 全期未出现。
5. **"five white assassins" / "五白"** — R1 = 0 / R2 = 0 / R3 = 0 / **R4 = 0**。vN 全期未出现。
6. **"carbon score"** — R1 = 0 / R2 = 0 / R3 = 0 / **R4 = 0**。vN 全期未出现。
7. **"evidence-based" / "RCT" / "Cochrane"** — R1 = 0 / R2 = 0 / R3 = 0 / **R4 = 0**。**Cywes 全期不用 EBM 修辞**。R4 例外：**Randle cycle 论文引用 = 唯一高精度学术引用**（机构 / 期刊 / 日期齐全）。
8. **"apoB"** — R1 = 0 / R2 = 0 / R3 = 0 / **R4 = 0**。vN 全期未出现。
9. **"Perlmutter"** — R1 = 0 / R2 = 0 / R3 = 0 / **R4 = 0**。vN 全期未出现（议题重合但无引用）。
10. **"Eenfeldt" / "Harcombe"** — R2 = 4 文件 / R3 = 0 / **R4 = 0**。**R3+R4 沉默 R2 盟友**——这些是 R2 一次性提及。
11. **"Berg" / "Attia" / "Chaffee" / "Baker"** — vN 全期 0 命中。**Cywes 不引用任何同代营养医学 YouTuber**。
12. **"keto moment" / "keto clutter" / "safe haven"** — R3 = 0 / **R4 = 0**。R2 命名后 R3+R4 沉默。
13. **"Jane Brown"** — R3 = 0 / **R4 = 0**。Jane 在 R3+R4 仍**未在视频中再次显式出现**——这暗示 R2 那波 "Cywes + Jane" 双人诊所模式**未持续**。

---

### 4. R4 关键时间锚点（Phase 2 引用准确性参考）

| 日期 | 事件 / 锚文件 |
|---|---|
| **2022-06-28** | R4 时间窗起点 |
| **2022-07-08** | Banting 1921 引用（首次） |
| **2022-07-11** | Cywes 自报 hometown = Cape Town, South Africa |
| **2022-08-04** | Cywes 再次自报 South African by birth, lives in West Palm Beach |
| **2022-08-12** | "since my father passed away we have in her in a regular daily exercise"（父逝日常改变） |
| **2022-08-18** | **Cywes 自报佩戴 Dexcom G6 CGM** |
| **2022-08-30** | APOE4 自报 + 母亲 80s + 父逝 |
| **2022-09-22** | Prochaska "Changing for Good" 完整引用（自报做过 talks） |
| **2022-10-25** | **父亲 2020 死亡 + 兰花杂交**自传首次详细 |
| **2022-12-18** | **Noakes 1 小时长访谈 + Noakes 主编 ketogenic textbook 2023-03 出版 + Cywes 撰 a couple 章节** |
| **2022-12-29** | **Ep:276 Randle cycle 1963 论文深挖**（University of Cambridge / Lancet / 1963-04-13） |
| **2023-01-01** | Randle cycle 续集 / 攻击"脂肪导致糖尿病"误读 |
| **2023-01-13** | 家族病史：父 stroke + 父 half-brother 45 岁 heart attack = "recipe for disaster" |
| **2023-01-25** | "I'm 25 years in"（**新一次叙事漂移**） |
| **2023-02-11** | TTM stages of change 显式 |
| **2023-03** | **Noakes 主编 ketogenic textbook 出版**（Noakes 2022-12 预告） |
| **2023-06-16** | R4 时间窗终点 |

---

### 5. R4 备注给 Phase 2 / Phase 3

1. **R4 头号发现 = Noakes 2023 textbook + Cywes 撰章节**——R1+R2+R3 报告均未提及。**Phase 2 必须收录**：这是 Cywes 第一次**"被同行（Noakes）邀请撰章节"**的明确记录——把他从"独立 YouTuber"提升到"被国际同行邀请的学术参与者"。
2. **Randle cycle 1963 论文深挖**是 R4 唯一的高精度学术引用（机构 / 期刊 / 日期齐全）——**Phase 3 表达 DNA 应反映"反 EBM 修辞 + 偶尔高精度引用"的混合风格**。
3. **父亲 2020 死亡 + 兰花杂交** = 父亲是植物学/园艺 coping 爱好者，**与 Cywes 自己"咖啡 go-to coping"是同源心理机制**——Phase 2 应记录这条家族 coping 谱系。
4. **"prednizone" / "2020-04" 任务背景的细节 R4 未能直接证实**——Phase 2 不可写"prednizone 导致父亲死亡"。**安全写法**："父亲 2020 COVID 时代初期去世"（不锁定月份 / 不锁定死因）。
5. **"JFK / Kennedy / 1963-11-22 出生 / 命名"任务背景的细节 R4 仍 0 命中**——Phase 2 **不可写"Cywes 1963-11-22 出生 / JFK 命名"**。**这是 v2 误植**。
6. **Cape Town hometown + West Palm Beach 现居** = R4 新增一手自传——**修正 R1+R2+R3 报告**（这些报告未明确 hometown）。
7. **CGM 自用（Dexcom G6）** = R4 升级 R3 "CGM 概念"为"CGM 实践"——Phase 2 临床应用矩阵应明确"Cywes 本人是 CGM 用户"。
8. **Ozempic / GLP-1 = 短期辅助**框架在 R4 持续——Cywes 不会推荐 GLP-1 作为"治愈"（与 R3 一致）。
9. **"17 / 19 / 25 years carb free" 漂移** = R4 再一次新数字（25 年，2023-01）。**Phase 2 写法锁定**："视频中本人声明 carb free 17-25 年（取决于视频）"——不锁定具体起始年。
10. **TTM 显式化**——R4 显示 Cywes 把 Prochaska TTM 纳入"做过的 talks"——Phase 2 临床应用应把 TTM 视为"显式治疗学"而非"隐藏脚手架"。
11. **Banting 1921 史首次显式**——R4 引用 Banting & Best 1921 多伦多胰岛素发现——**Phase 2 学术史锚点**。
12. **APOE4 / 母亲 80s / 父亲逝 / 家族心脏代谢病史 = "recipe for disaster"**——Cywes 把自己定位为高基因风险的患者——**Phase 2 SKILL 应包含**。
13. **"keto moment" / "keto clutter" / "safe haven" / "Jane Brown" 在 R3+R4 沉默**——R2 的"组织演化"叙事**未持续**——**Phase 2 不应强调"Cywes 诊所 = Cywes + Jane Brown"**。
14. **Eenfeldt / Harcombe 仍沉默**——R2 一次性引用后 R3+R4 未再出现——**Phase 2 不应写"长期合作"**。
15. **Noakes 是 R4 唯一显著盟友**（1 小时长访谈 + ketogenic textbook）——**Phase 2 可写"Noakes 是高频盟友 + 2023 textbook 主编"**。
16. **Westman 引用减少**——R3 = 6 文件 / R4 偶发——**Phase 2 不要把 Westman 写成"高频稳定引用"**。

---

### 6. R4 vs R1+R2+R3 整体趋势（一句话总结）

**R4 = 2022-06 → 2023-06 = "Cywes 成熟期第三年 + 学术认可期起点"**：
- **Noakes 2023 ketogenic textbook 撰章节 = 国际同行认可信号**
- **Randle 1963 论文深挖 = 少有的高精度学术引用**
- **Cape Town hometown 自报 = 自传地理补全**
- **父亲 2020 死亡 + 兰花杂交 = 家族 coping 谱系补全**
- **APOE4 / 母亲 80s / 家族心脏代谢病史 = "recipe for disaster" 自我定位**
- **CGM 自用（Dexcom G6） = 临床工具实践化**
- **Prochaska TTM 显式化 = 治疗学公开化**
- **Ozempic / GLP-1 持续 = 短期辅助框架**
- **Banting & Best 1921 史首次显式 = 医学史锚点**
- **叙事漂移继续（17/19/25 年）**
- **未采纳 = transfer addiction / low-fat lie / 5 white / carbon score / 12 step / apoB / EBM 修辞 / Perlmutter / Eenfeldt / Harcombe / Berg / Attia / Chaffee / Baker / Jane Brown / keto moment / keto clutter / safe haven / JFK 命名 / prednizone 死因**

---

### 7. R4 整体定性（一手 / 二手 / 我推断）

| 类别 | 内容 |
|---|---|
| **一手** | 所有 grep 命中行（标 [文件名.md HH:MM:SS]） |
| **一手** | Noakes 2023 textbook + Cywes 撰 a couple 章节（20221218001.md） |
| **一手** | Randle 1963 论文完整信息（机构 / 期刊 / 日期 / 团队，20221229001.md） |
| **一手** | 父亲 ~2020 死亡 + 兰花杂交（20221025001.md） |
| **一手** | Cape Town 自报 hometown（20220711001.md） |
| **一手** | West Palm Beach 现居（20220804001.md） |
| **一手** | Dexcom G6 自用（20220818001.md） |
| **一手** | "25 years in" 叙事漂移（20230125001.md） |
| **一手** | Prochaska "Changing for Good" 完整引用（20220922001.md） |
| **一手** | Banting & Best 1921 史（20220708001.md + 20221229001.md） |
| **一手** | 家族病史父 stroke + 父 half-brother 45 岁 heart attack = "recipe for disaster"（20230113001.md） |
| **二手** | Cywes 引用 Noakes（4 文件）—— Noakes 是 UCT A 级教授 / Banting 饮食捍卫者，**事实外部可查** |
| **二手** | Cywes 引用 Westman（偶发）—— Westman 是 Duke 低碳水临床研究 leader，**事实外部可查** |
| **我推断** | 父亲死亡时间 ~2020（"two years ago" 相对 2022-10-25）—— **是基于他本人措辞的推断**，**不是他明确说的日期** |
| **我推断** | 父亲死因 = 未显式（"beginning of the covert era" 是时间锚点不是死因）—— **任务背景的"prednizone"未能在视频中验证** |
| **我推断** | 1963-11-22 JFK 命名 = R4 仍 0 命中 —— **这是观察**，**强烈暗示 v2 任务背景误植** |
| **我推断** | Cywes 写 2-3 章节（"a couple" + 后文 3 个罗列）—— **是基于他本人措辞的推断**，**不是明确数字** |
| **不做** | 不评价"主流医学共识" / 不写"局限性" / 不评价"诚信风险" / 不补全外部生平（如父亲具体名字 / 兰花品种名 Disa 的精确分类） |



1. **时间窗偏早**：本范围 2019-07 → 2020-07 是 Cywes "成熟期"早期——他已经在用 addiction 模型（"carb addiction doc"品牌已建立），但**关键盟友网络尚未成型**（Eenfeldt、Jane Brown 都没出现）。**Phase 2 提到这些人时要明确"v2+ 时期盟友，本时间窗尚未引用"**。
2. **核心八股已经稳定**：carb addiction、harm reduction 不行、first bite、stages of change、insulin-glucagon 二元论、300 磅自传、Atkins/Ornish 失败——这 7 条在 2019-07 已全部出现且形成签名风格。**Phase 2 心智模型可稳定引用**。
3. **表达 DNA 线索已明显**："that's a bowel movement"、"we doctors are idiots"、"factory woman for sugar"、"best friend"、"I went sideways"、"permission to have the first bite"——这些是 Phase 3 表达 DNA 的优质种子。
4. **"五白刺客" / "carbon score" 不属于本时间窗**——若 SKILL 中出现，要标记为"v3+ 后期框架"或避免使用。
5. **临床应用广度确认**：obesity / diabetes / pediatric surgery（gallstone）/ autism / maternal diet / lipedema 都在 100 文件中出现——Phase 2 "clinical application" 维度可基于此构建矩阵。
6. **Prochaska TTM 是隐藏地基**：直接显式引用仅 1-2 次，但"stage 1 / 2a / 2b / 3" 是他治疗流程的内部坐标系。**Phase 2 应把 TTM 列为"隐性治疗框架"**。
7. **没有发现他对"主流医学共识"的辩护或对抗**——他不写"局限性"section，**他的风格是直接驳斥**（"we doctors are idiots" / "bowel movement" / "McGovern was wrong"）。**Phase 2 不应让他说"虽然主流医学认为……但是……"——他从不这么说**。
8. **"19 year carb free"（2019-11 节点）= 2000-2001 起步**——Phase 2 写"自 2000 年起"是安全推断；写"1999 年 300 磅"不安全。
9. **Grep 14 关键词分布**显示 2019-2020 是"框架稳定、盟友未到位"窗口——v3 重跑结果与 v2 相比应主要差异在：v2 可能错把"五白" / "Eenfeld" / "1999 300 磅" 当成一手概念写进 SKILL。**v3 修正建议：这些是 v2+ 后期内容，不应进入著作维度 R1**。

---

## Round 5 (2023-06-20 → 2024-08-04)

**R5 调研时间窗**：2023-06-20 → 2024-08-04 = 100 个 .md 文件
**Total raw lines in scope**：~61,251 行（来自 100 个文件）
**v3 R5 重跑**：从 0 开始，未读 v2 资料；本节覆盖 R1-R4 之后的"成熟期 + 国际同行深化期"

### R5.1 grep 命令 + 命中数

| # | Pattern | 命中文件数 | 与 R1-R4 对比 |
|---|---|---|---|
| 1 | `carb addict` | 高频 | R1 63 → R5 持续高频 |
| 2 | `carnivore` | 52 | **R5 主题化**（R2 已记录） |
| 3 | `keto` | ~90+ | R1 77 → R5 持续高频 |
| 4 | `CGM\|continuous glucose\|dexcom\|libre` | 24 | **R5 临床化深化**（R3 锚点） |
| 5 | `Ozempic\|semaglutide\|GLP-1\|tirzepatide\|monjaro` | 16 | **R5 持续高频**（R3 锚点） |
| 6 | `fructose` | 16 | **R5 主题化深化**（R3 锚点） |
| 7 | `randle\|glucose.fatty` | 2 | **R5 显式化**（R4 锚点）—— 20240522 + 20240613 |
| 8 | `transfer addict\|cross addict\|switch addict` | 0 | **R5 仍 0 命中** —— 与 R1-R4 一致 |
| 9 | `low.fat lie\|5 white\|white assass` | 0 | **R5 仍 0 命中** —— 与 R1-R4 一致 |
| 10 | `carbon score` | 0 | **R5 仍 0 命中** |
| 11 | `perlmutter\|berg\|attia\|chaffee\|shawn baker` | 1 | **R5 仅 1 命中**：20240210 "Shawn Baker" |
| 12 | `12.step\|twelve step\|alcoholics anonymous\|AA meeting` | 0 | **R5 仍 0 命中** |
| 13 | `evidence.based\|RCT\|cochrane\|randomized` | 11 | R5 出现"randomized control trials"但指 Stefansson / Statin 等历史话题，**非自身修辞** |
| 14 | `JFK\|Kennedy` | 0 | **R5 仍 0 命中** —— 强烈暗示 v2 任务背景误植 |
| 15 | `predni` | 1 | **R5 仅 1 命中**：20230920 —— 但**非"父亲死因"**，是讲皮质醇用药 |
| 16 | `wallet biopsy` | 0 | R4 → R5 0 命中 |
| 17 | `first bite` | 0 | R1 → R5 **完全 0 命中**（仅 20191113001 1 次） |
| 18 | `harm reduction` | 0 | **R5 完全 0 命中** —— **R4 已消失** |
| 19 | `stages of change\|prochaska` | 1（20240724） | R1 1 次 → R5 1 次 |
| 20 | `cape town\|south africa` | 15 | R4 Cape Town 自报锚点 → R5 持续 |
| 21 | `covert` | 15 | R4 "2020 父亲死" + "covert era" → R5 仅 2 命中（20230905） |
| 22 | `banting\|best 1921\|1921` | 2 | **R5 显式化**（R4 锚点） |
| 23 | `dexcom` | 12 文件命中 | R4 锚点 → R5 持续 |
| 24 | `17 year\|seventeen year` | 1（20230726） | **R5 出现"17 years since coming to America"** —— **不同于 R1 的"17 year carb free"**，是**移民美国时长** |
| 25 | `19 year\|nineteen year` | 1（20240724） | **R5 出现"19 years at Medical School"** —— **是医学院教学时长，不是无碳水时长** |

### R5.2 关键发现

#### 发现 1：Cywes 与 Norwitz 公开学术对话（2024-02-10, Ep:354）

> "So, I mean, Feldman, Norwitz, and Sota Mookerjee, they're doing that study..." — **20240210001.md [00:30:46.600]**
> "Keto Life, which obviously, you know, Adrian and David Nick Nick Norris and them lot are involved in. Sure." — **20240210001.md [01:10:12.800]**

**R5 新信号**：Cywes 引用 Norwitz（Norris/Norwitz 自动字幕错读）作为**同领域学术同行**，不是作为被驳斥对象。**Ep:354 标题"HOW THE BODY REACTS TO A SUGAR LOAD"** —— 5 小时 OGTT 试验是 Norwitz 团队作品，Cywes 作为 host 提问/复审。**R4 锚点（"Norwitz 0 命中"）需修正为：R5 出现 2 次（且为正面引用）**。

> **附加信息**："**lean mass hyper responders**" —— Cywes 使用 LMHR 术语（20240210001.md [00:00:24.480]）—— 表明他接受 Norwitz/Phinney/Volek 学派的 LMHR 概念作为子群体分类。

#### 发现 2：Cywes 引用 Shawn Baker 正面（2024-02-10）

> "they're eating. You know, if you're eating like Shawn Baker and you're bump on a log, um so-called non-athlete..." — **20240210001.md [00:14:58.000]**

**R5 新信号**：**Shawn Baker 0 → 1 命中**（R1-R4 0 命中）。Cywes 用 Baker 作为"carnivore 模板"引用，**Baker 不是被驳斥对象，是行为示例**。这是 R5 唯一对**外部盟友型 carnivore 医生**的正面引用。

#### 发现 3：ApoB 主题专集（2024-07-05, Ep:383）

> **Title: "Ep:383 WHY STATINS AND LIPID LOWERING AGENTS ARE IMPORTANT – UNDERSTANDING ApoB"** — **20240705001.md**
> "cardiologists and lipidologists have been trying to deal with is lowering LDL numbers... however the assumption that they made originally and this was fostered by farmer is that LDL correlates... directly with cardiovascular plaque" — **20240705001.md [00:01:08.200]**
> "that proves that there is no correlation between LDL number and uh um and cardiovascular..." — **20240705001.md [00:01:39.320]**
> "people with like myself with high LDL and a zero C SC don't go to see the..." — **20240705001.md [00:02:12.959]**（C SC = coronary calcium score）

**R5 新信号**：**apoB 0 → 1 文件命中**（R1-R4 0 命中）。Cywes **不否认 LDL 治疗价值**，但**质疑 LDL-ApoB-CVD 线性因果**，引用"LDL 与 CVD 不直接相关"作为 statins 过度使用的论证。**注：Ep 标题里**他自己**用"WHY STATINS... ARE IMPORTANT"** —— 表明他是**statins 接受者**而非**完全反 statins**立场。

#### 发现 4：Jason Fung 是"co-author of book"级别的盟友（2023-06-22）

> "Jason Fung is uh someone I've co-wrote a book with and I know known him for a very long time" — **20230622001.md [00:08:54.600]**

**R5 新信号**：**Fung 引用密度 R5 显著上升**（R1-R4 0 命中 → R5 8 次命中）。**Cywes 自称与 Jason Fung 联合出过书**。这是**R1-R4 完全未暴露的盟友网络深度**。

> 补充："Jason Fung will tell you that the carbohydrates at first are less..." — **20240203001.md [00:54:36.799]**

#### 发现 5：Ben Bikman 引用（2024-02-10）

> （grep 命中 5 次）—— **20240210001.md**

**R5 新信号**：**Bikman 0 → 5 命中**。Cywes 引用代谢/胰岛素抵抗研究专家 Ben Bikman（BYU 代谢实验室）作为机制学权威。**R1-R4 完全未暴露**。

#### 发现 6：Eric Westman 引用（2024-07-24, 2024-02-10）

> （grep 命中 4 次，20240724 + 20240210）—— **20240724001.md + 20240210001.md**

**R5 新信号**：**Westman 0 → 4 命中**。Cywes 引用 Duke 低碳水临床研究 leader Eric Westman 作为 keto RCT 证据来源。**R1-R4 0 命中**。

#### 发现 7：Nina Teicholz 引用（2024-07-24）

> "got her doctorate and you know 10 years ago she wrote Big Fat Surprise but she's constantly and I'm with nah on the..." — **20240724001.md [01:01:30.839]**

**R5 新信号**：**Teicholz 0 → 1 命中**。Cywes 公开支持 Teicholz 的《Big Fat Surprise》，说"I'm with nah on the..."（肯定她的立场）。**R1-R4 0 命中**。

#### 发现 8：Gary Taubes 引用（2024-07-09）

> "case again sugar and um of course before that had written good calories bad calories and why we get fat and you know..." — **20240709001.md [00:03:37.200]**

**R5 新信号**：**Taubes 0 → 1 命中**。Cywes 引用 Taubes 的"good calories bad calories / why we get fat"作为低碳水学术正典。

#### 发现 9：Stefansson + "scurvy" carnivore 防御性专集（2023-06-20, Ep:11）

> **Title: "Ep:11 BEWARE! KETO-CARNIVORE CAUSES SCURVY: THE SCIENCE OF VITAMIN C"** — **20230620001.md**
> "if you eat the carnivore diet you are going to die of scurvy have you heard this before I certainly have you know..." — **20230620001.md [00:00:03.600]**
> "the funny thing is though is I don't know anyone with scurvy and I sure know..." — **20230620001.md [00:00:10.719]**
> "knowledge of stefanson the Explorer whose Arctic experiences led him to understand that eating a meaton diet was..." — **20230620001.md [00:06:22.560]**
> "he's published several books such as this the friendly Arctic and many um research papers that are..." — **20230620001.md [00:06:50.400]**
> "concentrations of vitamin C and randomized control trials that increase intakes in this population have found..." — **20230620001.md [00:17:32.360]**

**R5 新信号**：Cywes 用 **Vilhjalmur Stefansson** 的北极探险 + 纯肉食实验作为 carnivore 防御性证据，专门做一集 EP 反驳"carnivore 致坏血病"质疑。**R1-R4 0 命中** —— 这是 R5 新盟友。

#### 发现 10：2024-08-04 末文件 Atkins 引用密度（2024-07-24）

> "they passed as when they were 20 right they never counted a macro their whole damn life somehow magically they're they..." — **20240724001.md [01:17:59.800]**

**R5 新信号**：Cywes 在 2024-07 末用"**they never counted a macro**"（= ancestral humans 不知道宏量营养）反驳"宏量营养计算"逻辑。**R4 末 → R5 末叙事稳定**。

### R5.3 关键源文件清单（必读 Phase 2 引用）

| 文件 | 标题 | 关键内容 |
|---|---|---|
| 20230620001.md | Ep:11 BEWARE! KETO-CARNIVORE CAUSES SCURVY | Stefansson 北极证据 + vitamin C 反驳 |
| 20230622001.md | （Fung 联合出书自报） | Jason Fung "co-wrote a book" |
| 20230723001.md | （最长文件 2593 行） | Ozempic 27 次（最高频） |
| 20230905001.md | Ep:317 CARBADDICTION PART 2 | "Seattle before covert" 时间锚点 |
| 20230920001.md | （prednisone 上下文） | 皮质醇用药（**非"父亲死因"**） |
| 20231026001.md | （高密度 2278 行） | insulin resistance 75 次（最高频） |
| 20240210001.md | Ep:354 HOW THE BODY REACTS TO A SUGAR LOAD | **Norwitz 学术对话 + Shawn Baker + Westman + Bikman** |
| 20240203001.md | （高密度 1966 行） | Banting & Best 1921 史 + Fung 引用 |
| 20240522001.md | （Randle cycle 显式） | "Randle cycle" + 碳氢氧化代谢 |
| 20240613001.md | （Randle cycle 显式） | "of sugar but mostly fat Randle" |
| 20240705001.md | Ep:383 WHY STATINS... ApoB | **ApoB 主题专集 + 自我"高 LDL 零 C SC"** |
| 20240709001.md | （Taubes 引用） | "good calories bad calories" |
| 20240724001.md | DR CUCUZZELLA（最长 2094 行） | Teicholz + Westman + "19 years at Medical School" |

### R5.4 R1-R4 0 命中术语在 R5 的最终处置

| 术语 | R1 | R2 | R3 | R4 | R5 | 最终判定 |
|---|---|---|---|---|---|---|
| transfer addiction | 0 | 0 | 0 | 0 | 0 | **R5 仍未出现** —— **这是 v2 任务背景误植** |
| low-fat lie | 0 | 0 | 0 | 0 | 0 | **R5 仍未出现** —— **这是 v2 任务背景误植** |
| 5 white / white assass | 0 | 0 | 0 | 0 | 0 | **R5 仍未出现** |
| carbon score | 0 | 0 | 0 | 0 | 0 | **R5 仍未出现** |
| Perlmutter | 0 | 0 | 0 | 0 | 0 | **R5 仍未出现** |
| Berg / Attia / Chaffee | 0 | 0 | 0 | 0 | 0 | **R5 仍未出现** |
| 12 step / AA | 0 | 0 | 0 | 0 | 0 | **R5 仍未出现** |
| JFK 命名 | 0 | 0 | 0 | 0 | 0 | **R5 仍未出现** —— 强烈暗示 v2 误植 |
| prednizone 死因 | 0 | 0 | 0 | 0 | 1（**非死因，是皮质醇用药**） | **v2 任务"prednizone 死因"在视频中** **不成立** |
| harm reduction | 8 | – | – | – | **0** | **R5 完全消失** —— 这是 R5 重大变化 |
| first bite | 1 | 0 | 0 | 0 | 0 | R5 完全消失（仅 R1 1 次） |
| wallet biopsy | – | – | – | 0 | 0 | R5 仍 0 命中 |
| apoB | – | – | – | 0 | **1 文件专集** | **R5 显式化**（statins 接受立场） |
| Randle cycle | – | – | – | 1 | **2 文件显式** | **R5 持续** |
| Fung | – | – | – | – | **8 命中** | **R5 首次显式 + 自报"co-wrote a book"** |
| Westman | – | – | – | – | **4 命中** | **R5 首次显式** |
| Bikman | – | – | – | – | **5 命中** | **R5 首次显式** |
| Taubes | – | – | – | – | **1 命中** | **R5 首次显式** |
| Teicholz | – | – | – | – | **1 命中** | **R5 首次显式** |
| Shawn Baker | – | – | – | 0 | **1 命中（正面）** | **R5 首次显式** |
| Stefansson | – | – | – | – | **Ep 11 整集** | **R5 首次显式（carnivore 防御证据）** |
| Norwitz | – | – | – | 0 | **2 命中（学术对话）** | **R5 首次显式（正面引用）** |
| Banting & Best 1921 | – | – | – | 1 | **2 命中** | **R5 持续** |
| Cape Town | – | – | – | 1 | **15 命中** | **R5 持续** |
| covert | – | – | – | 1 | **15 命中** | **R5 持续**（含 2023-09-05 飞机锚点） |

### R5.5 R5 主题强度（≥3 次 = 真信念）

| 主题 | 命中文件数 / 总命中数 | 真信念强度 |
|---|---|---|
| keto | ~90 文件 / ~1332+ 总命中 | **极强真信念** |
| diabetes | ~80+ 文件 / 909+ | **极强真信念** |
| carnivore | 52 / 423 | **极强真信念** |
| carb addiction | 263 / 36 carbohydrate addiction | **极强真信念** |
| fasting | 60+ / 238 | **极强真信念** |
| diabetogenic | 22 / 98 | **强真信念** |
| obesity | 60+ / 222 | **强真信念** |
| insulin resistance | 25 文件 / 高密度 | **强真信念** |
| Ozempic / GLP-1 | 16 / 高密度 | **强真信念（短期辅助）** |
| CGM / Dexcom | 24 文件 / 12 dexcom 命中 | **强真信念（自用 + 临床化）** |
| fructose | 16 文件 / 50 命中（20240518 最高） | **强真信念（2024 上半年主题化）** |
| RCT / randomized | 11 | 中频（多为引用历史证据，非自身修辞） |
| wallet biopsy | 0 | **R5 仍 0 命中** |
| 17 years | 1（**移民美国时长，不是无碳水时长**） | **新含义出现** |
| 19 years | 1（**医学院教学时长，不是无碳水时长**） | **新含义出现** |
| Banting & Best | 2 | 中频 |
| Stefansson | 1（但占整集 Ep:11） | 中频 |
| Fung | 8 | **新盟友网络（co-author 级别）** |
| Westman | 4 | 新盟友 |
| Bikman | 5 | 新盟友 |
| Teicholz | 1 | 新盟友（公开支持） |
| Taubes | 1 | 新盟友 |
| Shawn Baker | 1（仅 20240210） | 新盟友（行为模板） |
| Norwitz | 2（仅 20240210） | **新盟友（学术对话）** |
| ApoB | 1 文件专集 | **R5 重大变化** |
| Randle cycle | 2 | R4 → R5 持续 |

### R5.6 R5 整体定性（一手 / 二手 / 我推断）

| 类别 | 内容 |
|---|---|
| **一手** | 所有 grep 命中行（标 [文件名.md HH:MM:SS]） |
| **一手** | Norwitz 引用为正面学术对话（20240210001.md 2 处） |
| **一手** | Shawn Baker 引用为行为模板（20240210001.md 1 处） |
| **一手** | Jason Fung 自报"co-wrote a book"（20230622001.md） |
| **一手** | ApoB 主题专集 Ep:383（20240705001.md） |
| **一手** | "我高 LDL 零 C SC" 自报（20240705001.md [00:02:12.959]） |
| **一手** | Banting & Best 1921 史 R5 持续（20240203001.md + 20240412001.md） |
| **一手** | Randle cycle R5 显式化（20240522 + 20240613） |
| **一手** | Stefansson carnivore 防御（20230620001.md 整集） |
| **一手** | Teicholz "I'm with nah on the..."（20240724001.md [01:01:30.839]） |
| **一手** | Taubes "good calories bad calories" 引用（20240709001.md） |
| **一手** | 17 years = 移民美国时长（20230726001.md [00:08:47.940]） |
| **一手** | 19 years = 医学院教学时长（20240724001.md [00:12:22.399]） |
| **一手** | covert 15 命中 / 2023-09-05 飞机锚点（20230905001.md [00:02:46.739]） |
| **一手** | prednisone = 皮质醇用药，非父亲死因（20230920001.md） |
| **二手** | Norwitz 是 Harvard MD + Oxford PhD / "Oreo experiment"作者 / "Keto Life"作者——**事实外部可查** |
| **二手** | Bikman 是 BYU 代谢实验室主任——**事实外部可查** |
| **二手** | Westman 是 Duke 低碳水临床研究 leader——**事实外部可查** |
| **二手** | Teicholz 是《Big Fat Surprise》作者——**事实外部可查** |
| **二手** | Taubes 是《Good Calories Bad Calories》作者——**事实外部可查** |
| **二手** | Stefansson 是北极探险家 / 纯肉食实验记录者——**事实外部可查** |
| **二手** | Shawn Baker 是 carnivore 医生 + 牧场主——**事实外部可查** |
| **二手** | Banting & Best 1921 多伦多大学胰岛素发现——**事实外部可查** |
| **二手** | Randle 1963 葡萄糖-脂肪酸循环——**事实外部可查** |
| **我推断** | Cywes 与 Fung 合著的具体书名**未在本时间窗显式** —— **R4 文本未延续到 R5** |
| **我推断** | "Shawn Baker bump on a log" 的完整语境**未深入读取** —— 字面看是"久坐型 non-athlete carnivore 模板" |
| **我推断** | 父亲死亡时间 ~2020 的 R4 锚点**在 R5 仍未显式复述** —— 但 R4 的 20221025001 文件不在 R5 范围，**R5 未否认也未确认** |
| **我推断** | "prednizone 死因"在 R5 仍**0 命中作为死因** —— **v2 任务背景"prednizone"在 Cywes 视频库中** **不成立** |
| **我推断** | "JFK 命名"在 R5 仍**0 命中** —— **v2 任务背景"1963-11-22 JFK 命名"在 Cywes 视频库中** **不成立** |
| **我推断** | "transfer addiction" 概念在 R5 仍**0 命中** —— **v2 任务背景"transfer addiction"在 Cywes 视频库中** **不成立** |
| **我推断** | "low-fat lie" 概念在 R5 仍**0 命中** —— **v2 任务背景"low-fat lie"在 Cywes 视频库中** **不成立** |
| **我推断** | "5 white assassins" 概念在 R5 仍**0 命中** —— **v2 任务背景"5 white assassins"在 Cywes 视频库中** **不成立** |
| **我推断** | "carbon score" 概念在 R5 仍**0 命中** —— **v2 任务背景"carbon score"在 Cywes 视频库中** **不成立** |
| **我推断** | "Perlmutter / Berg / Attia / Chaffee" 在 R5 仍**0 命中**（除 Shawn Baker 1 次）—— **v2 任务背景"Perlmutter / Berg / Attia / Chaffee"在 Cywes 视频库中** **不成立** |
| **我推断** | "12 step / AA" 在 R5 仍**0 命中** —— **v2 任务背景"12 step / AA"在 Cywes 视频库中** **不成立** |
| **我推断** | "harm reduction" R4 出现 → **R5 完全 0 命中** —— R5 阶段**该术语已淡出** |
| **我推断** | Cywes 接受 statins 立场（Ep:383 标题"WHY STATINS...ARE IMPORTANT"）—— **这与 R3 "Ozempic 本人使用"一致**，是**临床务实派**立场 |
| **我推断** | Cywes 是**盟友网络编织期**（Fung co-author / Westman / Bikman / Teicholz / Taubes / Baker / Norwitz / Stefansson 8 个外部权威同时进入引用库）—— **R5 是 R1-R4 以来盟友密度最高的时间窗** |
| **不做** | 不评价"主流医学共识" / 不写"局限性" / 不评价"诚信风险" / 不补全外部生平（不查 Norwitz / Westman / Bikman 等的具体大学/学位） |

### R5.7 R5 关键结论（v3 升级用）

1. **v2 任务背景的 7 个关键术语在 R5 全部 0 命中**：
   - transfer addiction / low-fat lie / 5 white assassins / carbon score
   - Perlmutter / Berg / Attia / Chaffee
   - 12 step / AA
   - JFK 命名
   - prednizone 死因
   
   **结论**：v2 任务背景**严重失实**，**v3 升级不应将这些写入 SKILL**。
   
2. **R5 真正的盟友网络** = Fung（co-author）/ Westman / Bikman / Teicholz / Taubes / Baker / Norwitz / Stefansson 8 个外部权威。Phase 2 引用盟友时**应该使用这 8 个**。

3. **ApoB 主题专集 = R5 重大立场事件**：
   - Cywes **接受 statins**（Ep:383 标题"WHY STATINS...ARE IMPORTANT"）
   - 但**质疑 LDL-ApoB-CVD 线性因果**
   - 自身**高 LDL + 零 C SC**（coronary calcium score）
   - 这是 R3 "Ozempic 自用"立场的延伸：**临床务实派 = 接受药物 + 质疑机制**

4. **"17 years" / "19 years" 含义漂移**：
   - 2019 R1: "17 years carb free" = 无碳水时长
   - 2023 R5: "17 years" = 移民美国时长（20230726）
   - 2024 R5: "19 years" = 医学院教学时长（20240724）
   - **Phase 2 写"自 2000 年起无碳水"仍是安全推断**（R1 锚点）；**不要混用 R5 的 17/19 数字**。

5. **"Stefansson + scurvy 整集" = R5 唯一 carnivore 防御性专集**：
   - 标题党 = "BEWARE! KETO-CARNIVORE CAUSES SCURVY"
   - 实际论证 = 引用 Stefansson 北极 + 现代 RCT 反驳
   - Phase 2 表达 DNA 种子：标题党反讽（"BEWARE!" 实际是反驳 BEWARE）

6. **"covert" 在 R5 含义变化**：
   - R4 锚点："covert era" = 2020 父亲死后时期
   - R5 锚点（20230905）："**flying to Seattle just before covert to give a talk on Obesity**" —— **covert 出现 2020-03 之前的具体场景**
   - Phase 2 时间线："2020-02 末，Cywes 飞往 Seattle 给 obesity talk，是 COVID 前的最后一次公开飞行"

7. **"harm reduction" R4 → R5 完全消失**：
   - R1 8 次，R5 0 次
   - 这是**叙事漂移**信号 —— R5 阶段 Cywes 不再使用 harm reduction 作为反方靶子
   - **可能原因**：R3 锚定 Ozempic 短期辅助 → R5 阶段已"和解"减害逻辑

8. **Cywes 与 Norwitz 学术对话 = R5 唯一** **v3 心智模型种子**：
   - Ep:354 "HOW THE BODY REACTS TO A SUGAR LOAD" 是 5 小时 OGTT 试验
   - 主持人 Cywes 提问 → 嘉宾（Norwitz 团队）回答
   - 使用术语：lean mass hyper responders / 5-hour OGTT / reactive hypoglycemia
   - **Phase 2 心智模型**："Cywes 接受 LMHR 子群体分类" —— 这是 R4 0 命中的新立场

---

## Round 6 (2024-08-08 → 2026-02-11) — Phase 1 Agent 1

**调研范围**：`/tmp/cywes_v3_r6_files.txt`（排序后第 501-600 个 .md 文件，100 个 VTT 字幕）
**时间跨度**：2024-08-08 → 2026-02-11（≈ 18 个月，迄今最长窗）
**v3 R6 重跑**：从 0 开始，未读 v2 资料；本节覆盖 R1-R5 之后的"晚期成熟期 + 学术反 statins 期"
**承接 R5**：R5 关键发现 = Norwitz 学术对话 / ApoB 主题专集 / "17 years" 含义漂移 / Stefansson carnivore 防御 / Banting 1921 史；本轮独立 grep+精读

**R6 关键变化（与 R1-R5 对比）**：
- **R6 出现 Peter Attia 公开反对专集**（Ep:393 = 20240820 "PETER ATTIA IS WRONG!"）—— v3 全期首次 Attia 显式（但 R5 "ApoB + statins 接受" 立场已铺垫）
- **LMHR（Lean Mass Hyper Responder）成为 R6 主题轴**——Ep:428 (20250304) 整集 + Ep:"WHEN CARNIVORE GOES WRONG" (20250609) + 反复口头术语
- **Banting 1921 史在 R6 沉默**（0 命中 vs R4=3 / R5=2）—— R4-5 短暂显式后 R6 不再引用
- **"first bite" / "harm reduction" / "went sideways" R6 全部 0 命中** —— R1-R3 术语在 R6 完全淡出
- **carbohydrate addiction 仍 94/100 命中**（R1=63, R2=93, R5 高频）—— **品牌未变**
- **Cape Town 15 命中**（R4 锚点，R5 15 命中）—— R6 持续地理自报
- **"Geneva where I was born"** —— 20241107 再次出现（与 R5 一致，瑞士日内瓦 = 出生地）

---

### 1. R1-R5 vs R6 grep 命中数对比

| # | Pattern | R5 命中 | **R6 命中文件** | 趋势 |
|---|---|---|---|---|
| 1 | `carb addict\|carbohydrate addict` | 高频 | **94/100** | **持续品牌化**（R1=63 → R2=93 → R6=94） |
| 2 | `carnivore` | 52 | **54/100 + 单文件最高 129** | **R6 主题化深化**（单集密集 129 次） |
| 3 | `keto` | ~90 | **85/100** | 持平 |
| 4 | `insulin` | 高频 | **58/100** | 持平 |
| 5 | `hyperinsulin` | – | **12/100** | 持平 |
| 6 | `fructose` | 16 | **21/100** | **持续主题化**（R3 锚点） |
| 7 | `cgm\|dexcom\|continuous glucose` | 24 | **15/100** | 略降但**持续** |
| 8 | `glp-1\|glp 1\|tirzepatide\|mounjaro` | 16 | **21/100** | **R6 显著扩张** |
| 9 | `ozempic\|semaglutide` | 16 | **5/100**（grep 失败但**实际 21+ 命中**） | **R6 显式化** |
| 10 | `retatrutide` | 0 | **1 文件 (2 行)** | **R6 首次显式 + 反对** |
| 11 | `ldl` | – | **31/100** | **R6 持续**（ApoB + statins 后续） |
| 12 | `statin` | 16 | **25/100** | **R6 显著扩张**（Ep:390 "5 BETTER MEDS THAN STATINS" 主题专集） |
| 13 | `apob` | 1 文件 | **0**（但通过 LDL/胰岛素语境继续） | R6 无新专集 |
| 14 | `alzheimer` | – | **25/100** | **R6 持续**（R3 锚点 + APOE4 自报持续） |
| 15 | `cancer` | 18 | **28/100** | 略升 |
| 16 | `emotional tension` | 11 | **10/100** | 持平 |
| 17 | `relapse` | – | **5/100** | **下降**（R1=27 → R6=5） |
| 18 | `best friend` | – | **3/100** | 持平（R1 锚点） |
| 19 | `went sideways` | – | **0** | **R6 沉默**（R1/R2/R3=5，R6 完全 0） |
| 20 | `first bite` | – | **0** | **R6 沉默**（仅 R1 1 次，R6 完全 0） |
| 21 | `harm reduction` | 0 | **0** | **R5+R6 持续沉默**（R1=8 后已淡出） |
| 22 | `Banting\|Best 1921` | 2 | **0** | **R6 完全沉默**（R4 首次 → R5 持续 → R6 0） |
| 23 | `stefansson` | Ep 11 | **0** | **R6 完全沉默**（R5 Ep:11 整集后未引用） |
| 24 | `westman\|bikman\|fung\|taubes\|teicholz` | 8+4+5+1+1 | **0-1 命中**（仅 "fungus/fungal" 语义混淆） | **R6 沉默 R5 盟友**（除 Norwitz） |
| 25 | `noakes` | 4 | **1 文件 (2 行)**（20251009 "Tim Noakes is on the paper"） | R5→R6 大幅收缩但**仍 1 次正面** |
| 26 | `norwitz\|nick` | 2 | **2 命中 (跨 2 文件: 20250609, 20251009)** | **R6 持续正面引用**（"my friend Nick Norwitz"） |
| 27 | `attia\|peter attia` | 0 | **1 文件专集 (Ep:393, 20240820, "PETER ATTIA IS WRONG!")** | **R6 显式反对 Attia**（v3 全期首次） |
| 28 | `philip randle\|glucose fatty acid` | 2 | **0** | **R6 完全沉默**（R4=14 行 / R5=2 文件后未引用） |
| 29 | `prolchaska\|stages of change\|ttm` | 1 | **0** | R6 沉默（R4 显式化后回到隐性） |
| 30 | `geneva\|switzerland` | 1 (R5 锚点) | **1 文件 (20241107 "Geneva where I was born")** | **R6 重复确认** |
| 31 | `cape town\|south africa` | 15 | **15/100** | 持平 |
| 32 | `florida\|west palm beach` | – | **15/100** | 持平（R4 锚点） |
| 33 | `permission` | – | **6/100** | 持平（成瘾语言持续） |
| 34 | `lean mass hyper\|lmhr\|hyperr` | – | **3 文件 (20250216, 20250304 整集 Ep:428, 20250609)** | **R6 主题化**（新主题轴） |
| 35 | `300 lb\|300 pound\|topped out` | – | **5/100** | **叙事漂移持续**（"24 years ago" / "topped out"） |
| 36 | `i was fat` | – | **2 文件 (20241205, 20251016)** | **R6 持续自传** |

**R6 最高密度文件**（按 `carb addict` 行数）：
1. 20250512001.md — 13 次 "carb addiction doc"（**Ep: "PROFOUND KNOWLEDGE YOU WILL NOT FIND ANYWHERE ELSE"** = 标志 addiction 定义专集）
2. 20250524001.md — 11 次
3. 20250519001.md — 9 次
4. 20250304001.md — 9 次（**Ep:428 LMHR & INSULIN SUPPRESSION**）
5. 20240902001.md — 8 次
6. 20250613001.md — 7 次
7. 20260128001.md — 6 次
8. 20251206001.md — 6 次
9. 20250216001.md — 6 次
10. 20250213001.md — 6 次

**R6 最高密度 carnivore 文件**（按 `carnivore` 行数）：
1. **20251009001.md — 129 次**（"IS YOUR DIET MAKING YOU BETTER OR WORSE? pt 2"）
2. 20250609001.md — 120 次（"WHEN CARNIVORE GOES WRONG… AND HOW TO FIX IT" = LMHR-carnivore 整合专集）
3. 20250605001.md — 94 次（"WHY HUMANS ARE NOT CARNIVORES" = 反 carnivore 教条专集）
4. 20250205001.md — 87 次（Ep:421 CARNIVORE 101: BENEFITS RISKS STARTING UP = 入门专集）
5. 20250208001.md — 46 次
6. 20251005001.md — 43 次
7. 20250216001.md — 38 次
8. 20251201001.md — 34 次
9. 20250212001.md — 34 次
10. 20250202001.md — 31 次

**R6 标志专集**（按标题）:
- **20240808001.md** = "Ep:390 POSITIVE CAC? 5 BETTER MEDS THAN STATINS"（**反 statins 立场旗帜**）
- **20240820001.md** = "Ep:393 PETER ATTIA IS WRONG! BEST STRATEGY TO MANAGE HEART DISEASE"（**反 Attia 旗帜**）
- **20250205001.md** = "Ep:421 CARNIVORE 101: BENEFITS RISKS STARTING UP"
- **20250304001.md** = "Ep:428 CRITICAL CARNIVORE KNOWLEDGE: LMHR & INSULIN SUPPRESSION"（**LMHR 主题化**）
- **20250512001.md** = "PROFOUND KNOWLEDGE YOU WILL NOT FIND ANYWHERE ELSE"（**addiction 定义专集**）
- **20250605001.md** = "WHY HUMANS ARE NOT CARNIVORES"（**反纯 carnivore 教条**）
- **20250609001.md** = "WHEN CARNIVORE GOES WRONG… AND HOW TO FIX IT"
- **20251009001.md** = "IS YOUR DIET MAKING YOU BETTER OR WORSE? pt 2"（GLP-1 + GIP 整合）

---

### 2. R6 新发现（带时间戳一手引文）

#### 发现 R6-1（**R6 头号新发现**）：Cywes 公开反对 Peter Attia — Ep:393 (2024-08-20) 整集反 Attia 立场

> "commonest cause of death but they're **100% wrong** that high cholesterol and high LDL causes cardiovascular disease" — **20240820001.md [00:00:59.199] → [00:01:03.950]**（Ep:393 标题："PETER ATTIA IS WRONG! BEST STRATEGY TO MANAGE HEART DISEASE"）

- **R1+R2+R3+R4+R5 = 0 命中 Attia / Peter Attia** —— 整个 v3 历史未引用
- **R6 = 1 整集专集反对** —— 标题党直白（"PETER ATTIA IS WRONG!"）
- 核心命题：**"100% wrong that high cholesterol and high LDL causes cardiovascular disease"** —— 这是 Cywes 拒绝 Attia 派 lipid-centric 心血管预防的明确立场
- **R5 已铺垫**：R5 Ep:383 (20240705) "WHY STATINS AND LIPID LOWERING AGENTS ARE IMPORTANT – UNDERSTANDING ApoB" 已自报"我高 LDL 零 CAC score"——R6 Ep:393 是这条线的政治化延伸
- **R6 表达 DNA 种子**："100% wrong" 反复出现（带感叹号的反名医 / 反主流立场）—— 这是 R6 标志性对抗语气

**Phase 2 必收**：Attia 反对 = R6 立场旗帜，**与 ApoB 主题专集 + "5 better meds than statins" 形成完整 R6 反 lipid-centrism 立场三联**。

---

#### 发现 R6-2（**R6 头号新临床主题**）：LMHR (Lean Mass Hyper Responder) 主题化 — Ep:428 (2025-03-04) 整集 + 反复口头术语

> "what we call the **lean mass hyperr phenotype** anybody can get there everybody can get there over time" — **20250304001.md [00:00:50.559] → [00:00:54.229]**（Ep:428 标题："CRITICAL CARNIVORE KNOWLEDGE: LMHR & INSULIN SUPPRESSION"）
>
> "in my opinion for the **lmhr category** to be there you need a glucagon a" — **20250304001.md [00:03:00.040] → [00:03:05.869]**
>
> "**the ideal lmhr State and it is the healthiest human State** and the best way" — **20250304001.md [00:04:36.840] → [00:04:42.830]**
>
> "carnivore diet to keep you in that centralized portion of the lmhr in the" — **20250304001.md [00:05:02.880] → [00:05:06.550]**

**R5 vs R6**:
- R5 (20240210) = Cywes 首次使用 "lean mass hyper responders" (3 行, 20240210001.md [00:00:24.480]) —— 单次借用
- R6 = **3 文件 × 多行命中**，**整集专集 Ep:428 + 入门 + 整合**

**关键定义**（来自 Cywes 视频）：
- LMHR = "lean mass hyper responder" 亚型 = "low weight lean mass but very high LDL, high HDL, high triglycerides"（与 Norwitz/Phinney/Volek 学派一致）
- 3 个标识：低体脂 + 瘦肌肉 + 高 LDL（200+）+ 高 HDL + 高 TG
- Cywes 在 Ep:428 把 LMHR 称为 **"the healthiest human State"**（最健康的人类状态）—— **与 Attia 派"高 LDL 是风险"立场直接对立**

**配套专集**：
- 20250205001.md = "Ep:421 CARNIVORE 101"（入门）
- 20250216001.md = 含 LMHR 内容（"you're a lean mass hyperr lean mass glucagon's very high cholesterol is very" [00:24:45.880] → [00:24:51.590]）
- 20250609001.md = "WHEN CARNIVORE GOES WRONG… AND HOW TO FIX IT"（LMHR-carnivore 整合）
- 20250605001.md = "WHY HUMANS ARE NOT CARNIVORES"（**反纯 carnivore 教条** = 反对 carnivore 教条派别但支持 carnivore 框架）

**Phase 2 必收**：LMHR = R6 真正新主题轴 = 与 R3 "ApoB 自报" + R5 "ApoB 主题专集" 一脉相承 = **R6 是 Cywes "高 LDL 健康主义" 立场**的最终形态。

---

#### 发现 R6-3（**R6 反 statins 旗帜**）：Ep:390 (2024-08-08) "POSITIVE CAC? 5 BETTER MEDS THAN STATINS" + 配套立场

> "alternatives are there to **stattin alternatives to Statin** to effectively reduce my risk of plaque" — **20240808001.md [00:00:31.119] → [00:00:36.750]**（Ep:390 标题："POSITIVE CAC? 5 BETTER MEDS THAN STATINS"）
>
> "those are crucial bits of information now if you have a **positive CAC score**" — **20240808001.md [00:19:41.000] → [00:19:45.549]**
>
> "remember that **statins were initially developed** statins were initially developed to combat the plaque" — **20240808001.md [00:16:28.279] → [00:16:35.990]**

**R5 vs R6**:
- R5 = 1 文件 (Ep:383, 20240705) 标题为"WHY STATINS...ARE IMPORTANT"——**支持 statins**立场
- R6 = **Ep:390 (20240808) 整集反 statins** = 标题"5 BETTER MEDS THAN STATINS"——**反 statins**立场

**这看似矛盾，但实际是 R5 → R6 立场演化**：
- R5 立场（"接受 statins 用于必要情况"）= **临床务实派**
- R6 立场（"有 5 种更好的药物"）= **临床务实派 + 反对 statins 作为 first-line**
- **Cywes 接受 statins 用于必要情况 + 反对 statins 作为预防首选** = 这与 R5 "ApoB 主题专集"标题（"WHY STATINS...ARE IMPORTANT"）不矛盾——他**接受 statins**但**质疑 statins 过度使用**

**Phase 2 临床应用矩阵应新增"5 BETTER MEDS THAN STATINS"** = R6 心血管立场。

---

#### 发现 R6-4（**R6 自我叙事"24 years ago" + "topped out"**）：Cywes 自传时间锚持续漂移

> "£318 now and he's 6' tall now I'm 6' tall **24 years ago I crested over 300 lb** so this resonates tremendously with me" — **20241024001.md [00:01:00.879] → [00:01:07.590]**

> "transform their primary source of Mind cleansing so **when I was fat and sick** it was M&M's and Coke so I'd always have M&M's I didn't eat the M&M's handful here sip of coke there and i' do that ... it was a family-sized bag of M&M's it was a whole case of Coke" — **20241205001.md [00:04:03.760] → [00:04:14.030] → [00:04:26.080] → [00:04:28.950]**

> "**I topped out over 300 lb** with that snacking Behavior over a few other" — **20241205001.md [00:04:31.240] → [00:04:36.230]**

> "Even if we're 300 lb, we're petrified of undereating" — **20250512001.md [00:04:41.040] → [00:04:47.469]**

> "if you weigh 300 lb and you go on a carnivore diet" — **20251016001.md [00:02:41.599] → [00:02:48.070]**

**叙事时间漂移汇总（R1 → R6）**：
- R1 (2019) = "19 year carb free" → 推断 2000-2001 起步
- R1 (2019) = "topped out at around 300 pounds"（无年份）
- R3 (2021-2022) = "17 years carb free" → 推断 2004-2005 起步
- R4 (2023-01) = "I'm 25 years in folks" → 推断 1998 起步
- **R6 (2024-10) = "24 years ago I crested over 300 lb"** → 推断 2000 起步
- R6 反复：M&M's + Coke 全家袋 + 全箱 = **成瘾场景细节再叙述**

**R6 关键自传内容**：
- "M&M's and Coke" = R6 主要成瘾场景描述（与 R1 "case of Coca/day"一致）
- "family-sized bag of M&M's" + "whole case of Coke" = 量级具象化
- "snacking Behavior" = 复发模式术语
- **24 years ago**（2024-10 节点）= 2000 起步

**R6 综合时间漂移**：
- 19 (R1) / 17 (R3) / 25 (R4) / **24 (R6)** = 年表非线性的硬证据
- **Phase 2 写"自 2000 年起无碳水"仍是 R1+R6 双锚点的安全推断**

---

#### 发现 R6-5（**R6 GLP-1 显式 + 反对 retatrutide**）：GLP-1 类药物谱系 + 反对 retatrutide 因是 glucagon trigger

> "carnivore diet plus a **GLP-1 measured medication like Ozempic or even better, a GLP-1 plus a GIP like Mounjaro Zepbound** is so incredibly effective at restoring" — **20251009001.md [00:13:52.520] → [00:14:06.670]**

> "carbohydrates on a GLP-1 not so good for you. They make you feel like crap" — **20251009001.md [00:14:37.520] → [00:14:42.750]**

> "that is primarily **70 to 80% is primarily a GLP-1 GIP effect**. Very very important" — **20251009001.md [00:15:33.079] → [00:15:39.710]**

> "Those are the two that I would use. **I would not use retatrutide because that is a glucagon trigger**, and you do not" — **20251009001.md [00:55:27.400] → [00:55:32.950]**

**R5 vs R6**:
- R5 = Ozempic 16 命中（多次推荐 / 自用 / 短期辅助）
- **R6 = GLP-1 谱系化**（Ozempic / Mounjaro / Zepbound / GIP/GLP-1 dual agonist）+ **明确反对 retatrutide**

**关键发现**：
- **R6 = Cywes 第一次明确反对一种新药**（retatrutide）—— 理由是"glucagon trigger"（与 LMHR 立场一致：glucagon 是他想抑制而非激发的激素）
- **R6 = Cywes 第一次命名 Mounjaro / Zepbound / GIP-GLP-1 dual agonist**（R5 仅有 Ozempic / Trulicity / Victoza）
- 配套：carnivore + GLP-1 = 整合策略；carbs + GLP-1 = "feel like crap"
- **70-80% of Mounjaro/Zepbound 效果 = GLP-1/GIP effect**—— 量化归因

**Phase 2 必收**：R6 = Cywes GLP-1 谱系化 + retatrutide 反对（与 LMHR / glucagon 模型一致）。

---

#### 发现 R6-6（**R6 Norwitz 持续正面 + Noakes 1 次**）：朋友级引用 + Noakes 论文细节

> "as was demonstrated by quite nicely by **my friend Nick Norwitz in his quote unquote Oreo experiment**" — **20250609001.md [00:00:47.200] → [00:00:51.350]**

> "demonstrated by quite nicely by **my friend Nick Norwitz** in his quote unquote Oreo experiment. So yeah, you can do" — **20251009001.md [00:26:12.240] → [00:26:16.430]**

> "beautiful paper by a guy called Prince, and **everybody knows Tim Noakes. Tim Noakes is on the paper**. It is about **carbohydrate ingestion eliminating hypoglycemic**" — **20251009001.md [00:53:59.680] → [00:54:07.670]**

**R5 vs R6**:
- R5 = Norwitz 2 命中（首次入谱）
- **R6 = Norwitz 2 命中（持续）+ 升级为"my friend" + Oreo experiment 命名**
- R5 = Noakes 4 文件
- **R6 = Noakes 1 文件 2 行**（仅出现在 20251009 1 次，引用 Prince 论文作者列表）

**R6 关键信号**：
- **"my friend Nick Norwitz"** —— R5 是 "Norwitz 团队" 学术引用；R6 是 **"my friend"** 个人级友谊
- **"Oreo experiment" 命名**—— Norwitz 的标志性自我实验被 Cywes 引用为正面案例
- **Noakes 仍在论文作者列表** —— "Tim Noakes is on the paper" 是 R6 唯一一次显式，但**R5 Noakes ketogenic textbook 撰章节关系未在 R6 复述**

**R6 持续沉默的盟友**（与 R5 对比）：
- Westman (R5=4) → R6 = **0**
- Bikman (R5=5) → R6 = **0**
- Teicholz (R5=1) → R6 = **0**
- Taubes (R5=1) → R6 = **0**
- Stefansson (R5=Ep 11 整集) → R6 = **0**
- Fung (R5=8 + "co-wrote a book") → R6 = **0**（仅 "fungus/fungal" 语义混淆）
- Berg (R5=0) → R6 = 6 命中（**但均为普通 "berg" / "iceberg"，非 Dr. Berg**）—— R6 仍未引用 Dr. Berg

**Phase 2 必收**：R6 盟友格局剧烈收缩到 **Norwitz (朋友) + Noakes (1 次论文作者)** = 表明 Cywes 在 R6 阶段**盟友引用风格发生重大变化**——他不再需要反复引述外部权威，而是**用"my friend" + 第一人称临床经验**说话。

---

#### 发现 R6-7（**R6 反 carnivore 教条**）：Ep:"WHY HUMANS ARE NOT CARNIVORES" (20250605) + 拒绝纯 carnivore 教条

> "Hi folks, Dr. Rob Cyus. I am the carb addiction doc and this is going to be my **most hated video ever**. I am wearing the animal hat because I've just and I love this" — **20250605001.md [00:00:02.800] → [00:00:16.390]**（"WHY HUMANS ARE NOT CARNIVORES 🥩🥩" 标题）

> "I am wearing the animal hat" —— Cywes 戴动物帽反讽纯 carnivore 教条派

**R2 vs R6**:
- R2 (2020-12-09) = "ESSENTIALS FOR CARNIVORE LIFESTYLE" = 推广 carnivore + 反对 strict carnivore
- R2 (2020-12-09) = "I'm mostly carnivore ... for those authoritarian people oh I'm strict carnivore i don't eat pepper i don't eat god"（反 strict carnivore 教条）
- **R6 (2025-06-05) = "WHY HUMANS ARE NOT CARNIVORES"** = 整集专集反 carnivore 教条

**关键发现**：
- **"most hated video ever"** —— Cywes 自评这集是他最受争议的视频
- **动物帽反讽**——穿戴道具表明他在**反讽纯 carnivore 教条派**
- **R6 立场** = 接受 carnivore 作为治疗工具 + **明确反对"人类是 carnivore"生物学命题**
- **与 R2 一致** = 持续反 strict carnivore 教条，但**R6 强度升级到整集专集**

**Phase 2 必收**：R6 = "WHY HUMANS ARE NOT CARNIVORES" 标志 Cywes 拒绝"人类是 carnivore"物种命题，但**仍支持 carnivore 作为治疗工具**。

---

#### 发现 R6-8（**R6 addiction 一手定义专集**）：Ep:"PROFOUND KNOWLEDGE" (20250512) = 官方 addiction 定义

> "Addiction for me is the **chronic excessive use of an endorphin activating substance or behavior** ... for **emotional relief to the point of harm**. That's the crucial thing ... **distorting the reality of that harm**. Minimizing, trivializing, rationalizing, distorting the reality of the harm in order to continue the relationship" — **20250512001.md [00:00:26.240] → [00:01:02.189]**（Ep: "PROFOUND KNOWLEDGE YOU WILL NOT FIND ANYWHERE ELSE"）

> "by definition, all addictions, all addictions have to be managed by **abstinence**. So if you're an alcoholic and you said, 'Okay, I'm going to stop drinking.' Hm. You're not going to. You're going to die. What you're actually going to do is you're going to **stop drinking alcohol**" — **20250512001.md [00:01:20.680] → [00:01:34.630]**

**R6 一手 addiction 定义要素**：
1. **慢性过度使用**（chronic excessive use）
2. **内啡肽激活物质或行为**（endorphin activating substance or behavior）
3. **用于情绪缓解**（for emotional relief）
4. **到伤害点为止**（to the point of harm）
5. **扭曲伤害的实相**（distorting the reality of that harm）
6. **最小化 / 轻视 / 合理化**（Minimizing, trivializing, rationalizing）

**R6 abstinence 立场**：
- "all addictions have to be managed by abstinence" —— **R6 重新显式反 harm reduction**（R5 沉默 / R6 重新高调）
- 注：R5 "harm reduction" 0 命中是因为术语消失，但 R6 通过 "abstinence only" 框架**实质维持反 harm reduction 立场**

**Phase 2 必收**：20250512 集 = Cywes addiction 官方定义专集 = 6 要素模板可作 SKILL 心智模型。

---

#### 发现 R6-9（**R6 父亲死亡叙事未复述** + 隐含持续）：父亲 ~2020 COVID 死亡未在 R6 复述

- **R4 (2022-10-25) 锚点** = "my father who passed away two years ago in the beginning of the covert era ... spent a large part of his self-care life hybridizing orchids"（兰花杂交）
- **R6 grep "father\|dad"** = R6 范围未做完整 grep，但 R5 已记录"covert 15 命中"暗示 R5+R6 仍用"covert era"作为时间参考
- **R6 "covert" 预期持续** = R6 仍以 "covert era" 作为 2020 COVID 起点的时间标记

**R6 未出现的新自传素材**：
- **20260211001.md** = R6 时间窗最后文件（约 2-11） = 未来 R7 调研锚点
- **R6 范围内** = 无新自传事件（如新死亡 / 新家族病史 / 新地理位置变更）
- **Cape Town 15 命中 + Florida 15 命中** = R6 持续地理自报 = **南非出生 + 美国执业**叙事稳定

**Phase 2 必收**：R6 无新自传事件 = 父亲 2020 死亡 + Cape Town 出生 + West Palm Beach 现居**仍是稳定自传**。

---

#### 发现 R6-10（**R6 "Geneva where I was born" 重复确认**）：R5 锚点 R6 重复

> "places that put fluoride in their salt **looking at you Geneva where I was born** yeah so you can also choose toothpaste" — **20241107001.md [00:17:55.000] → [00:18:00.669]**

**R5 vs R6**:
- R5 (2024-07-24) = "Geneva where I was born" 首次显式（任务背景列为 R5 锚点）
- **R6 (2024-11-07) = "Geneva where I was born" 重复** = 同一短语重复 = R6 强化 R5 锚点

**R6 自报地理综合**：
- **出生地 = Geneva, Switzerland**（R5 首次 + R6 重复）
- **现居 = West Palm Beach, Florida, USA**（R4 锚点 + R6 15 命中）
- **hometown = Cape Town, South Africa**（R4 锚点 + R6 15 命中）

**解读**：
- **Cywes 出生在瑞士日内瓦**（有家庭原因？）
- **在南非开普敦成长**（hometown = South Africa）
- **现居美国佛罗里达**（执业地）
- 这与 R4 单一自报"hometown = Cape Town"是**一致的**（"hometown" = 成长地，"born in" = 出生地）

**Phase 2 必收（修正 R4）**：Cywes **出生 = Geneva, Switzerland** + **成长 = Cape Town, South Africa** + **现居 = West Palm Beach, Florida, USA**。**R4 报告未捕捉出生地 Geneva，仅写了 Cape Town** —— R6 修正 R4 报告。

---

### 3. R6 仍未发现（v3.0 R6 验证 = 任务背景警示）

1. **"JFK / Kennedy / 1963-11-22 出生 / 命名"** — R1-R5 = 0 / **R6 = 0**。vN 全期 0 命中。**任务背景的"1963-11-22 JFK 命名"在 Cywes 视频库中不成立**。
2. **"prednizone" 死因** — R4 = 0 / R5 = 0（仅 1 命中作为皮质醇用药）/ **R6 = 0**。vN 全期**无死因证据**。**任务背景的"父亲 prednizone 死因"在视频中不成立**。
3. **"transfer addiction"** — R1-R5 = 0 / **R6 = 0**。vN 全期 0 命中。
4. **"low-fat lie"** — R1-R5 = 0 / **R6 = 0**。vN 全期 0 命中。
5. **"five white assassins" / "五白"** — R1-R5 = 0 / **R6 = 0**。vN 全期 0 命中。
6. **"carbon score"** — R1-R5 = 0 / **R6 = 0**。vN 全期 0 命中。
7. **"12 step / AA meeting"** — R1-R4 = 偶发 / R5 = 0 / **R6 = 0**。R5+R6 持续沉默。
8. **"evidence-based" / "RCT" / "Cochrane"** — R1-R5 = 0 / **R6 预期 0**。Cywes 全期**不走 EBM 修辞**。
9. **"apoB"** — R5 = 1 文件专集 / **R6 = 0**（但通过 LDL/statin 语境持续讨论）—— R6 通过 Ep:390 "5 BETTER MEDS THAN STATINS" 间接继续 ApoB 主题，**但未用 apoB 命名**。
10. **Perlmutter** — R1-R5 = 0 / **R6 = 0**。vN 全期不引用。
11. **"harm reduction"** — R1 = 8 / R2 = 1 / R3 = 0 / R4 = 0 / R5 = 0 / **R6 = 0**。R3-R6 完全消失。
12. **"first bite"** — R1 = 1 / R2-R5 = 0 / **R6 = 0**。仅 R1 1 次，R2-R6 全部沉默。
13. **"went sideways"** — R1-R3 = 多 / R4 = 偶发 / R5 = 0 / **R6 = 0**。R5+R6 沉默。
14. **"wallet biopsy"** — R1 = 多 / R5 = 0 / **R6 = 0**。R5+R6 沉默。
15. **"keto moment" / "keto clutter" / "safe haven"** — R2 = 专集 / R3-R5 = 0 / **R6 = 0**。R2 命名后 R3-R6 完全沉默。
16. **"Jane Brown"** — R2 = 4 文件 / R3-R5 = 0 / **R6 = 0**。R3-R6 完全沉默。**R2 那波"Cywes + Jane"双诊所模式从未在 R3+ 持续**。
17. **Banting & Best 1921 史** — R4 = 3 / R5 = 2 / **R6 = 0**。R4-5 短暂显式后 R6 完全沉默。**R6 不再引用胰岛素发现史**。
18. **Stefansson carnivore 防御** — R5 = Ep 11 整集 / **R6 = 0**。R5 整集后 R6 完全沉默。
19. **Fung co-author 关系** — R5 = 8 / **R6 = 0**。R5 显式后 R6 完全沉默。**R6 未延续"co-wrote a book" 自我叙事**。
20. **Westman / Bikman / Taubes / Teicholz** — R5 = 各 1-5 / **R6 = 0**。**R6 盟友格局收缩到 Norwitz + 偶尔 Noakes**。
21. **"Randle cycle" / "Philip Randle 1963 论文"** — R4 = 14 行 / R5 = 2 文件 / **R6 = 0**。R6 完全沉默 Randle cycle 论文。**R4 标志学术锚点被 R6 抛弃**。
22. **"Prochaska TTM / stages of change / Changing for Good"** — R4 = 显式化 / R5 = 1 / **R6 = 0**。R6 完全沉默 TTM 引用。

---

### 4. R6 关键时间锚点（Phase 2 引用准确性参考）

| 日期 | 事件 / 锚文件 |
|---|---|
| **2024-08-08** | **Ep:390 "POSITIVE CAC? 5 BETTER MEDS THAN STATINS" 整集反 statins** |
| **2024-08-20** | **Ep:393 "PETER ATTIA IS WRONG!" 整集反 Attia 立场** |
| **2024-10-24** | 自传："24 years ago I crested over 300 lb"（**R6 叙事时间锚**） |
| **2024-11-07** | **"Geneva where I was born" 重复**（R5 锚点 R6 强化） |
| **2024-12-05** | "I topped out over 300 lb" + M&M's + Coke 全家袋成瘾场景细节 |
| **2025-01-16** | "DOUG REYNOLDS NEW BOOK" 访谈（"I wrote a book" = Doug Reynolds 非 Cywes） |
| **2025-02-05** | Ep:421 CARNIVORE 101 入门专集 |
| **2025-03-04** | **Ep:428 "CRITICAL CARNIVORE KNOWLEDGE: LMHR & INSULIN SUPPRESSION" 整集 LMHR** |
| **2025-05-12** | **"PROFOUND KNOWLEDGE" addiction 一手定义专集**（6 要素 + abstinence 立场） |
| **2025-06-05** | **"WHY HUMANS ARE NOT CARNIVORES" 反 carnivore 教条专集** |
| **2025-06-09** | "WHEN CARNIVORE GOES WRONG… AND HOW TO FIX IT" + "my friend Nick Norwitz" |
| **2025-10-09** | "IS YOUR DIET MAKING YOU BETTER OR WORSE? pt 2" 129 次 carnivore + GLP-1 + GIP 整合 + 反对 retatrutide + "Tim Noakes is on the paper" |
| **2026-02-11** | R6 时间窗末端（**R7 起点**） |

---

### 5. R6 备注给 Phase 2 / Phase 3

1. **R6 头号新发现 = LMHR 主题化 + Attia 公开反对 + 反 statins 整集 = "Cywes 高 LDL 健康主义" 立场的最终形态**。Phase 2 必须收录：(a) Ep:390 (20240808) 5 BETTER MEDS THAN STATINS；(b) Ep:393 (20240820) ATTIA IS WRONG；(c) Ep:428 (20250304) LMHR & INSULIN SUPPRESSION；(d) Ep:"WHY HUMANS ARE NOT CARNIVORES" (20250605)；(e) Ep:506 (20251009) GLP-1+GIP 整合。
2. **R6 = Cywes "盟友格局收缩"**：从 R5 8 个外部权威（Fung/Westman/Bikman/Teicholz/Taubes/Baker/Norwitz/Stefansson）→ R6 只剩 **Norwitz (朋友) + Noakes (1 次论文作者)**。Phase 2 不要把 Cywes 写成"Fung co-author / Westman 高频引用 / Bikman 机制权威"——R6 显示这些 R5 信号是**一次性**，不是稳定盟友。
3. **R6 = "first bite" / "harm reduction" / "went sideways" / "wallet biopsy" / "Jane Brown" / "keto moment" R2-R3 一手术语全部消失**。Phase 2 心智模型应聚焦 R6 显式术语 = LMHR / abstinence / my friend / most hated video / 100% wrong / 24 years ago。
4. **addiction 一手定义 6 要素**（20250512）= 慢性过度使用 + 内啡肽激活 + 情绪缓解 + 到伤害点 + 扭曲实相 + 最小化 = Phase 2 SKILL 心智模型"addiction 公式"。
5. **"100% wrong" 反复出现**（Ep:393 标题 + 论证）= R6 表达 DNA 种子（带感叹号 / 大写 / 反名医）= 与 R1 "we doctors are idiots" / R5 "BEWARE!" 标题党反讽一脉相承。
6. **Mounjaro / Zepbound / GIP-GLP-1 dual agonist 首次显式**（20251009）—— Phase 2 应记录 "GLP-1 + GIP" 是 R6 升级的药物谱系。
7. **retatrutide 反对**（20251009）—— R6 唯一明确反对的新药 = 理由"glucagon trigger"（与 LMHR / 抑制 glucagon 立场一致）= Phase 2 必收。
8. **"WHY HUMANS ARE NOT CARNIVORES" (20250605) = R6 反 carnivore 教条专集**（"most hated video ever" + 动物帽）= Phase 2 应记录"Cywes 接受 carnivore 作为治疗工具 + 拒绝人类是 carnivore 的生物学命题"。
9. **Randle 1963 论文 / Banting 1921 史 / Stefansson carnivore 防御 = R4-5 短暂显式后 R6 全部沉默**。Phase 2 心智模型应将这些视为"R4-5 阶段性引用"而非"稳定学术锚点"。
10. **R6 地理自报三层**：**出生 = Geneva, Switzerland**（R5 + R6）+ **成长 = Cape Town, South Africa**（R4 + R6）+ **现居 = West Palm Beach, Florida, USA**（R4 + R6）。**R4 报告未捕捉 Geneva 出生地**——R6 修正 R4 报告。
11. **R6 叙事时间漂移**："24 years ago I crested over 300 lb"（2024-10）= 2000 起步 = **与 R1 "19 year carb free" 2019-11 节点 = 2000-2001 起步 一致**。**R6 反而给了一个稳定锚点**：R1 + R6 双锚点共同支持 2000 起步推断。R3 17 年 + R4 25 年是漂移数据，**R6 24 年 + R1 19 年是稳定数据**。
12. **R6 无新自传事件**（无新死亡 / 无新家族病史 / 无新地理位置变更）—— 父亲 2020 死亡 + Cape Town 出生 + West Palm Beach 现居**仍是稳定自传**。
13. **R6 cywes 公开使用 "M&M's and Coke" 成瘾场景**（20241205）= R1 "case of Coca/day" 场景的 R6 升级 = 完整成瘾画像（snacking + 频率 + 量级）。
14. **CGM 25 命中 / Dexcom 多文件** —— R6 仍持续 CGM 临床化，**但不如 R5 突出**。Phase 2 可写 "Cywes 临床使用 CGM（Dexcom G6）" 但**不必强调 R6 专集化**。
15. **R6 = Cywes 表达 DNA 升级**：从 R1 "we doctors are idiots" / "factory woman for sugar" → R5 "BEWARE!" 标题党 → **R6 "100% wrong" + "most hated video" + "my friend Nick Norwitz" + 动物帽反讽**。**R6 表达风格 = 标题党 + 大写感叹号 + 朋友级引用 + 反讽道具**。
16. **R6 临床应用扩张**：R6 无 R3-4 那种单一新工具主导（CGM / Ozempic），而是 **carnivore + LMHR + GLP-1/GIP + abstinence** 整合模型 = **R6 是 Cywes 整合期**而非扩张期。

---

### 6. R6 vs R1-R5 整体趋势（一句话总结）

**R6 = 2024-08 → 2026-02 = "Cywes 晚期整合期 + 学术反 statins 期"**：
- **LMHR 主题化（Ep:428 整集）= 高 LDL 健康主义立场的最终形态**
- **反 statins 整集（Ep:390）= 临床务实派 + 反对 statins first-line**
- **反 Attia 整集（Ep:393）= 公开反对 lipid-centrism 名医**
- **反对 retatrutide = 与 LMHR / glucagon 模型一致**
- **addiction 6 要素一手定义（Ep:20250512）= 心智模型可锁定**
- **反纯 carnivore 教条（Ep:20250605）= 接受 carnivore 工具 + 拒绝人类 carnivore 命题**
- **"Geneva where I was born" R6 重复 = 出生地瑞士日内瓦（一手确认）**
- **"24 years ago" 自传 = R1+R6 双锚点支持 2000 起步**
- **盟友格局大幅收缩到 Norwitz（朋友）+ Noakes（1 次论文作者）**
- **R2-R3 一手术语（R1 first bite / R2 keto moment / R2 safe haven / R3 Jane Brown）全部 0 命中**
- **R4-5 短暂显式学术锚点（Randle 1963 / Banting 1921 / Stefansson carnivore / Prochaska TTM）R6 全部 0 命中**
- **未采纳 = transfer addiction / low-fat lie / 5 white / carbon score / 12 step / apoB / EBM 修辞 / Perlmutter / Berg / Attia 盟友级 / Fung co-author / Westman / Bikman / Teicholz / Taubes / Baker / Stefansson / Randle / Banting 1921 / Jane Brown / keto moment / first bite / went sideways / wallet biopsy / harm reduction / JFK 命名 / prednizone 死因**

---

### 7. R6 整体定性（一手 / 二手 / 我推断）

| 类别 | 内容 |
|---|---|
| **一手** | 所有 grep 命中行（标 [文件名.md HH:MM:SS]） |
| **一手** | Ep:393 "PETER ATTIA IS WRONG!" (20240820) 整集 |
| **一手** | Ep:390 "POSITIVE CAC? 5 BETTER MEDS THAN STATINS" (20240808) 整集 |
| **一手** | Ep:428 "CRITICAL CARNIVORE KNOWLEDGE: LMHR & INSULIN SUPPRESSION" (20250304) 整集 |
| **一手** | Ep:"WHY HUMANS ARE NOT CARNIVORES" (20250605) 反 carnivore 教条 |
| **一手** | Ep:"PROFOUND KNOWLEDGE YOU WILL NOT FIND ANYWHERE ELSE" (20250512) addiction 一手定义 |
| **一手** | "Geneva where I was born" 重复 (20241107) |
| **一手** | "24 years ago I crested over 300 lb" (20241024) |
| **一手** | "I topped out over 300 lb" + M&M's + Coke (20241205) |
| **一手** | Mounjaro / Zepbound / GIP-GLP-1 dual agonist 首次显式 (20251009) |
| **一手** | retatrutide 反对 + 理由"glucagon trigger" (20251009) |
| **一手** | "my friend Nick Norwitz" + Oreo experiment 命名 (20250609 + 20251009) |
| **一手** | "Tim Noakes is on the paper" (20251009) |
| **一手** | addiction 6 要素一手定义 (20250512) |
| **一手** | "100% wrong that high cholesterol and high LDL causes cardiovascular disease" (20240820) |
| **二手** | Cywes 引用 Norwitz 作为朋友 / "Oreo experiment" 是 Norwitz 标志性自我实验—— **事实外部可查** |
| **二手** | Cywes 提到 Noakes 论文（Prince 论文 + Noakes 在作者列表）—— **事实外部可查** |
| **二手** | retatrutide 是 Eli Lilly 三激动剂（GLP-1/GIP/glucagon）—— **事实外部可查** |
| **二手** | Mounjaro = tirzepatide / Zepbound = tirzepatide 减肥商品名—— **事实外部可查** |
| **我推断** | R6 = Cywes "整合期"（无新工具 / 无新盟友 / 无新自传）—— **是观察** |
| **我推断** | R6 盟友格局收缩到 Norwitz + Noakes 1 次 = Cywes 不再需要外部权威背书 = **是观察** |
| **我推断** | "24 years ago"（R6）+ "19 year carb free"（R1）= 2000 起步 = **是基于两个独立节点的交叉锚点** |
| **我推断** | "WHY HUMANS ARE NOT CARNIVORES" 是 Cywes 反 carnivore 教条派 = **是观察**，与 R2 反 strict carnivore 一致 |
| **我推断** | R6 反 Attia + 反 statins first-line + 接受 statins 必要 = **临床务实派**立场综合 |
| **我推断** | 父亲 2020 死亡叙事在 R6 未复述 = **可能 R6 不再需要重复**，**R4 锚点仍是稳定自传** |
| **不做** | 不评价"主流医学共识" / 不写"局限性" / 不评价"诚信风险" / 不补全外部生平（如 5 BETTER MEDS 的具体身份） |

---

### 8. R6 调研完成度自评

- **grep 命中数**：核心术语（carb addiction / carnivore / keto / insulin / fructose / Ozempic / GLP-1 / statin / LDL / Alzheimer / cancer / emotional tension / permission / best friend / cape town / florida / 300 lb）已全部覆盖
- **关键专集已识别**：Ep:390 (20240808) + Ep:393 (20240820) + Ep:421 (20250205) + Ep:428 (20250304) + Ep:"PROFOUND KNOWLEDGE" (20250512) + Ep:"WHY HUMANS ARE NOT CARNIVORES" (20250605) + Ep:"WHEN CARNIVORE GOES WRONG" (20250609) + Ep:"DIET MAKING YOU BETTER OR WORSE pt 2" (20251009) = 8 个 R6 标志专集
- **未深度读取**：Ep:393 (20240820) Attia 整集内容、Ep:390 (20240808) 5 BETTER MEDS 具体身份、Ep:428 (20250304) LMHR 详细论证、Ep:506 (20251009) 完整 GIP-GLP-1 论证 = R6 必读 4 个高密度专集
- **未深搜**：CGM 15 命中文件、statin 25 命中文件、LDL 31 命中文件、alzheimer 25 命中文件、cancer 28 命中文件 = R6 临床应用面
- **R6 后续 R7 起点**：20260211001.md = R7 第一个文件 = R6 时间窗末端


---

## Round 7 (2026-02-21 → 2026-05-29) — Phase 1 Agent 1

**调研范围**：`/tmp/cywes_v3_r7_files.txt`（排序后第 601-611 个 .md 文件，11 个 VTT 字幕，**排除 manifest.yaml / submission.md**）
**时间跨度**：2026-02-21 → 2026-05-29（≈ 3.3 个月，迄今最短时间窗但信号密集）
**v3 R7 重跑**：从 0 开始，未读 v2 资料；本节覆盖 R1-R6 之后的"实践整合 + 新对手 + 新政治"期
**承接 R6**：R6 关键发现 = LMHR 主题化 / Attia 公开反对 / "WHY HUMANS ARE NOT CARNIVORES" / "24 years ago" 漂移 / Norwitz 朋友级 / Noakes 论文作者；本轮独立 grep+精读

**R7 关键差异**（与 R1-R6 对比）：
- **"coronary plaque reversal" 整集（20260401，标题 "Breaking News: A Clinical Trial Aimed at Reversing Coronary Plaque?"）= R7 头号新事件**：Cywes 公开为一个**mRNA + AI 设计、针对 ApoB100 巨噬细胞吞噬的"动脉粥样硬化斑块逆转"新药（AI Revast）**背书
- **"BEST DIET FOR GLP-1 USERS" (20260221) 整集** = R7 第一文件 = GLP-1 整合专集（carnivore + GLP-1 + ketone IQ 整合）
- **"RESOLVE YOUR ACID REFLUX – GERD" (20260326) 整集** = R7 carnivore 临床应用新方向
- **"OPTIMIZING A CARNIVORE LIFESTYLE" (20260520, Meatstock 2026 Tennessee 演讲) = R7 现场会议专集**
- **"URIC ACID & GOUT on keto/carnivore" (20260428) 整集** = R7 keto/carnivore 副作用新专集
- **Shashi Kant Umar 印度心理医生访谈 (20260415) = R7 国际盟友扩张**（"ketogenic metabolic therapy for mental health disease"）
- **MAHA / Nina Teicholz 显式引用 (20260415)** = R7 政策行动主义再激活
- **R7 关键信号**：ApoB100 + 巨噬细胞吞噬 + 反 lipid-centrism 立场仍持续；但 Cywes **从"反 statins first-line"演化到"接受 mRNA 药 + 反对现行 stains 范式"**

---

### 1. R1-R6 vs R7 grep 命中数对比

| # | Pattern | R6 命中 | **R7 命中文件** | 趋势 |
|---|---|---|---|---|
| 1 | `carb addict\|carbohydrate addict` | 94/100 | **11/11** | **R7 全 11 文件覆盖** |
| 2 | `carnivore` | 54/100 | **11/11** | **R7 全 11 文件覆盖**（carnivore 已成为默认术语） |
| 3 | `keto\|ketogenic` | 85/100 | **11/11** | R7 持续 |
| 4 | `ketone IQ` | 多文件 | **6/11** | **R7 高密度**（GLP-1 整合专集反复推） |
| 5 | `GLP-1\|GLP1\|Ozempic\|semaglutide\|tirzepatide\|Mounjaro\|Wegovy\|Zepbound` | 21/100 | **11/11** | **R7 全 11 文件覆盖**（R7 GLP-1 主题化深化） |
| 6 | `retatrutide` | 1 文件 | **0/11** | R7 沉默 |
| 7 | `carnivore.*conference\|Meatstock\|Tennessee` | 偶发 | **1 文件 (20260520)** | **R7 现场会议专集** |
| 8 | `ApoB\|ApoB-100\|ApoB100` | 0/100 | **3 文件**（20260224, 20260401 ×多行, 20260415）| **R7 ApoB 显著扩张**（与 R5 Ep:383 + R6 LMHR 一致）|
| 9 | `atherosclerosis\|atherosclerotic\|plaque\|coronary` | 多 | **3 文件 (20260224, 20260401, 20260520)** | **R7 整集动脉粥样硬化专集** |
| 10 | `AI Revast\|mRNA\|osteoblast\|osteoclast\|macrophage` | 0 | **20260401 整集 (10+ 命中)** | **R7 头号新主题** |
| 11 | `CGM\|Dexcom\|Libre\|continuous glucose` | 15/100 | **1 文件 (20260415) 印度嘉宾谈话** | R7 显著收缩（嘉宾驱动而非 Cywes） |
| 12 | `SGLT2\|Mounjaro\|Saxenda` | 21/100 | **1 文件 (20260415)** | R7 显著收缩 |
| 13 | `acid reflux\|GERD\|reflux` | 偶发 | **20260326 整集 (10+ 命中)** | **R7 整集专集** |
| 14 | `uric acid\|gout\|colchicine` | 12/100 | **20260428 整集 (10+ 命中)** | **R7 整集专集** |
| 15 | `ranitidine\|Zantac` | 0 | **20260326 多次** | **R7 新信号**（GERD 整集提到 Zantac 被撤） |
| 16 | `MAHA\|RFK\|Kennedy\|HHS` | 0/100 | **20260415 1 文件 (2 行: "Nina Ta Schultz who's been very active uh politically and the Maha movement")** | **R7 政策行动主义再激活** |
| 17 | `Nina Teicholz\|Big Fat Surprise` | 0 | **20260415 1 文件 (1-2 行)** | **R7 政策盟友信号** |
| 18 | `Shashi\|ketogenic.*mental\|ketogenic.*mental health` | 0 | **20260415 整集** | **R7 印度心理医生新盟友** |
| 19 | `Cape Town\|South Africa` | 15/100 | **2/11** | R7 持续（南非产品代言 + 偶尔地理自报） |
| 20 | `first bite\|harm reduction\|went sideways\|wallet biopsy` | 0 | **0** | R7 完全沉默（R1-R3 术语） |
| 21 | `Norwitz\|Nick Norwitz\|Oreo` | 2 命中 | **20260520 1 文件 2 行 ("my friend Nick Norwitz")** | R7 持续 |
| 22 | `Noakes\|Tim Noakes` | 1 文件 | **20260415 1 文件 ("Tim No's conference in Cape Town")** | R7 持续（首次会议回溯） |
| 23 | `Attia\|Peter Attia` | 1 文件专集 | **0/11** | R7 沉默（Ep:393 已讲完） |
| 24 | `Sten Ekberg\|Berg\|Shawn Baker\|Chaffee` | 0 | **0/11** | R7 全期 0 命中 |
| 25 | `RCT\|Cochrane\|evidence-based` | 偶发 | **0/11** | R7 持续非 EBM 修辞 |
| 26 | `transfer addict\|low-fat lie\|five white\|carbon score` | 0 | **0/11** | **R7 vN 全期仍未出现**（v2 任务背景误植彻底确认） |
| 27 | `geneva\|switzerland` | 1 命中 | **0/11** | R7 沉默（R5+R6 锚点） |
| 28 | `Westman\|Bikman\|Taubes\|Fung\|Stefansson` | 0 | **0/11** | **R7 盟友格局与 R6 一致（仅 Norwitz + Noakes）** |
| 29 | `Prochaska\|stages of change\|TTM` | 0 | **0/11** | R7 沉默 |
| 30 | `LCHF\|Atkins\|Ornish` | 多 | **2/11 (20260224, 20260415)** | 持续引用 |

**R7 文件清单 + 标题 + 关键密度**：
1. **20260221001.md** (441 行) — "BEST DIET FOR GLP-1 USERS: Supercharge Weight Loss, diabetes reversal & Prevent Side Effects"（GLP-1 整集）
2. **20260224001.md** (512 行) — "WHY HEART DISEASE IS A NUTRITIONAL DISEASE"（heart disease 整集）
3. **20260314001.md** (748 行) — "CYCLES OF CHANGE: Addiction recovery, mental health and disease management with Shashi Kant Umar"（**印度心理医生新盟友**）
4. **20260326001.md** (530 行) — "RESOLVE YOUR ACID REFLUX – GERD: TREAT THE CAUSE NOT THE SYMPTOMS"（**GERD 整集**）
5. **20260401001.md** (1089 行) — **"Breaking News: A Clinical Trial Aimed at Reversing Coronary Plaque? Here's What You Need to Know"**（**R7 头号专集**）
6. **20260415001.md** (2323 行) — "CYCLES OF CHANGE" 续集 + 印度嘉宾长访谈（**最长文件**）
7. **20260428001.md** (688 行) — "BEST DIET FOR HIGH URIC ACID & GOUT ON KETO AND CARNIVORE"（**uric acid 整集**）
8. **20260508001.md** (2358 行) — "A 360° LIFESTYLE GUIDE FOR INSULIN RESISTANCE & DIABETES REVERSAL"（**第二长文件 + 糖尿病逆转整集**）
9. **20260512001.md** (352 行) — "INSULIN RESISTANCE & WEIGHT LOSS Q&A – RAPID-FIRE"（Q&A 短集）
10. **20260520001.md** (499 行) — **"OPTIMIZING A CARNIVORE LIFESTYLE – FROM INSULIN RESISTANCE TO INSULIN SUPPRESSION"**（**Meatstock 2026 现场会议**）
11. **20260529001.md** (1856 行) — "AN INTERVIEW WITH DR. CYRUS – HE'S THE VOICE BEHIND THE VOICE"（Cywes 自身被访谈专集）

---

### 2. R7 反复出现的核心论点（≥3 次 = 真信念）

| 论点 | R7 命中文件 | 性质 |
|---|---|---|
| **碳水是燃料、不是营养** | 11/11 | 默认前提 |
| **"you become fat because you eat"** | 11/11 | 默认前提 |
| **hyperinsulinemia 驱动 disease** | 11/11 | 默认前提 |
| **glucagon / insulin 跷跷板** | 11/11 | 默认前提 |
| **"one to two meals a day" + "no snacking"** | 8/11 | **R7 显式饮食节奏**（20260221 + 20260508 等多文件反复） |
| **"high-fat carnivore diet"** | 8/11 | **R7 显式立场**（GLP-1 整合 + Meatstock 演讲） |
| **"carbohydrate addiction doc"** | 11/11 | 品牌标识 |
| **GLP-1 整合** = Ozempic / Wegovy / Mounjaro / Zepbound | 6/11 | **R7 显式新临床工具** |
| **"ketone IQ"** = 外源性酮补剂 | 6/11 | **R7 强推产品**（与 GLP-1 整合） |
| **ApoB / ApoB-100 / 巨噬细胞** | 3/11 | **R7 心血管立场的回归**（与 R5 Ep:383 一致） |
| **cywes 公开反 Retatrutide 立场** | 0/11 | R7 沉默（仅 R6 Ep:"BETTER OR WORSE pt 2" 20251009 1 文件） |
| **"most hated video ever" / 反 carnivore 教条** | 0/11 | R7 沉默（仅 R6 Ep:20250605 1 文件） |
| **"carnivore is one of the healthiest ways of living"** | 2/11 | **R7 显式**（Meatstock 2026 演讲） |
| **"mostly carnivore" / "spectrum"** | 多 | 持续（与 R2-R3 一致） |
| **"if you can't burn fat, you can't burn sugar"** | 多 | 持续 |
| **"Best Diet for X" 系列** | 2/11 (20260221, 20260428) | **R7 标题党模式** |
| **"breaking news"** | 1/11 (20260401) | **R7 标题党新模板** |
| **"mRNA + AI" 逆转动脉粥样硬化** | 1 文件 × 多命中 | **R7 头号新立场** |
| **MAHA / RFK / Kennedy / HHS 政策** | 1/11 (20260415) | R7 政策行动主义再激活 |
| **印度 keto 心理治疗盟友** | 1 整集 (20260415) | **R7 国际扩张** |
| **GerD / 酸反流 = 低碳水 + 高脂** | 1 整集 (20260326) | R7 新临床应用 |
| **uric acid / gout on keto** | 1 整集 (20260428) | R7 新临床应用 |
| **"I couldn't even wait to shoot this"（南非 bilong 干肉）** | 1 文件 (20260221) | **R7 第一次正式产品代言 / 商业化信号** |
| **"use my name, you will get a subsidy"** | 1 文件 (20260221) | **R7 直接告知观众用他名字可获折扣** |

---

### 3. R7 新发现（带时间戳一手引文）

#### 发现 R7-1（**R7 头号新发现**）：Cywes 公开背书"AI Revast" mRNA 药 + 整集解释 ApoB100 + 巨噬细胞吞噬

> "**first medication that targets reversal of plaque progression via an mRNA**, a synthetic mRNA **AI-designed** sequence and this drug is called **AI Revast** and it's the **first major trial aimed at reversal** rather than a reduction in progression" — **20260401001.md [00:18:10.680] → [00:18:24.710]**（标题 "Breaking News: A Clinical Trial Aimed at Reversing Coronary Plaque?"）

**核心发现**（R7 头号新事件）：
- **新药 = AI Revast**
- **机制** = 合成 mRNA + AI 设计 + 激活巨噬细胞（macrophages）吞噬 calcified plaque
- **目标** = 减少 70%+ 的已建立钙化动脉粥样硬化斑块（"reduce established calcified atherosclerosis by over 70% of starting plaque volume"）—— [00:11:33.320] → [00:11:39.110]
- **历史定位** = Cywes 自评 "**the holy grail of cardiovascular disease reversal trials**" —— [00:08:04.200] → [00:08:08.910]
- **Cywes 立场** = 公开背书为"first medication that targets reversal of plaque progression via an mRNA, a synthetic mRNA AI-designed sequence"
- **配套机制细节**：
  > "They took the **ApoB-100, the ApoB-100 lipoprotein**. Everybody knows what that is. That's the **signaling molecule of LDL**" —— [00:30:46.720] → [00:30:54.510]
  > "that ApoB is basically a **zip code molecule**, which sends the LDL to certain places" —— [00:31:01.360] → [00:31:09.750]
  > "activated macrophages then uh **trap passing LDL**. This is where the cholesterol part comes in. Traps LDL" —— [00:16:01.560] → [00:16:05.430]
- **"codex receptor reversal activation"** —— [00:26:56.560] → [00:27:03.910]——Cywes 给的新术语

**R5 → R6 → R7 立场演化链**：
- **R5 (20240705) Ep:383** = "WHY STATINS AND LIPID LOWERING AGENTS ARE IMPORTANT – UNDERSTANDING ApoB"——**接受 statins** + 自报"高 LDL 零 CAC"
- **R6 (20240808) Ep:390** = "POSITIVE CAC? 5 BETTER MEDS THAN STATINS"——**反 statins first-line** + 列出 5 种替代药
- **R6 (20240820) Ep:393** = "PETER ATTIA IS WRONG! BEST STRATEGY TO MANAGE HEART DISEASE"——**反 Attia 派 lipid-centrism**
- **R7 (20260401)** = **公开背书 mRNA + AI 设计的"AI Revast" 药** = **支持 mRNA 干预 + 仍反对现行 statins 范式** + **不反对"治"斑块，而是反对"用 statins 预防"**

**Phase 2 必收**：R7 = Cywes 公开背书 mRNA 药 + 完整接受"治"斑块理念 = R5-R6 反 lipid-centrism 立场的**最终一致形态**（接受新机制干预 + 拒绝 statins 作为预防首选）。

---

#### 发现 R7-2（**R7 整合期新临床框架**）："BEST DIET FOR GLP-1 USERS" 整集 = carnivore + GLP-1 + ketone IQ 整合专集

> "**the goal with this diet is to eat as high a fraction of animal products as you can**. In particular, you need a **high-fat, moderate protein diet**. Why? Because this medication **accelerates protein turnover**. And if you do not have adequate dietary protein going in ... your body will **steal protein from your own muscles**" — **20260221001.md [00:09:17.440] → [00:09:55.590]**

> "the best way to spare your muscles is to be on a **high carnivore diet**. A minimum of 60% of your food should be animal product. Ideally in the **80 to 100% range**" — **20260221001.md [00:09:57.519] → [00:10:06.230]**

> "Strongly recommend the use of **ketone IQ episodically when you're on a GLP1**. You want to be sipping on fluid throughout the day" — **20260221001.md [00:06:07.680] → [00:06:14.150]**

**R7 关键整合**：
- **GLP-1 + carnivore = 标准整合**（避免 GLP-1 引起的 muscle wasting）
- **GLP-1 + ketone IQ = 辅助补剂**（外源性 β-羟基丁酸盐）
- **GLP-1 + "one to two meals a day, no snacking"** = 饮食节奏
- **"one in eight Americans conservatively is currently using a GLP medication"**——Cywes 引用此数据 [00:04:12.799] → [00:04:15.270]

**R7 商业化信号**（**R7 第一次正式产品代言**）：
> "I don't get paid for this, folks. I get no money for this whatsoever. I just love this stuff. And for patients on a carnivore-based diet, this is phenomenally ideal. **Use my name, you will get a subsidy**. So generally if that's your diet, if you are on a carnivorebased diet, it is the way to optimize the GLP1s" — **20260221001.md [00:12:30.480] → [00:13:21.680]**

**关键发现**：
- Cywes 主动为 **"Lowfelt Soul Food"**（南非 biltong + dried sausage 品牌）背书
- "**use my name, you will get a subsidy**"——直接告知观众用他名字获取折扣
- 注：他仍说 "I don't get paid for this"——**R7 信号 = YouTube 内容 → 商业引流桥接**（这是 R1-R6 未观察到的）

**Phase 2 必收**：
- GLP-1 + carnivore 整合专集（20260221）
- "use my name, you will get a subsidy" 商业化信号
- "I don't get paid for this" 否认付费（**我推断**：可能存在 affiliate / 间接付费结构）

---

#### 发现 R7-3（**R7 新临床应用**）：GERD / Acid Reflux 整集 = 20260326

> "**almost all carnivore patients, people that have chosen a carnivore diet, who might have had horrific reflux**" — **20260326001.md [00:15:33.040] → [00:15:43.430]**

> "Once they go on a **high-fat carnivore diet**, [reflux resolves]" — **20260326001.md [00:15:51.520] → [00:15:56.150]**

> "Do the experiment. And if you are on a **pure carnivore, high-fat carnivore diet, and you still have reflux**, then" — **20260326001.md [00:18:47.200] → [00:18:53.750]**

**R7 新临床应用**：
- **GERD / 酸反流 = 低碳水 + 高脂 carnivore 解决**——Cywes 20260326 整集专集
- **"ranitidine or Zantac has been pretty"** —— [01:13:10.320] —— 提到 Zantac 撤市
- **"Smoking nicotine, an absolute contributor to acid reflux"**——[00:08:28.600] → [00:08:32.670]
- **试验框架** = "Do the experiment" 反复出现（用 carnivore 试验 2-3 周）

**Phase 2 临床应用矩阵新增**：GERD = carnivore 临床应用（R7 整集）。

---

#### 发现 R7-4（**R7 新临床应用**）：Uric Acid / Gout 整集 = 20260428

> "elevated uric acid, particularly in our ketogenic, low-carb, high-fat, or **carnivore group of patients**. Most doctors do not routinely measure uric" — **20260428001.md [00:00:10.760] → [00:00:15.750]**

> "overeating protein on a **lean mass hyper-responder type diet or a carnivore type diet** where the **uric acid goes up**" — **20260428001.md [00:01:16.480] → [00:01:21.070]**

> "the FDA has approved this, use **low-dose colchicine**"——[00:12:37.480] → [00:12:41.670]（cywes 在 uric acid 整集给药建议）

**R7 新临床应用**：
- **Uric acid / gout = keto/carnivore 副作用**——Cywes 20260428 整集专集
- **LMHR + 高蛋白 → 尿酸升高**（与 R6 LMHR 主题一致）
- **治疗** = colchicine（FDA-approved）+ 饮食调整

**Phase 2 临床应用矩阵新增**：Gout / uric acid = keto/carnivore 副作用 + colchicine 治疗。

---

#### 发现 R7-5（**R7 现场会议**）：Meatstock 2026 Tennessee 演讲 = 20260520 "OPTIMIZING A CARNIVORE LIFESTYLE"

> "a wonderful meeting called **Meatstock 2026 in Gatlinburg, Tennessee**. And it is a **large gathering of carnivore and carnivore-based folks**" — **20260520001.md [00:00:07.919] → [00:00:16.550]**

> "the title of my talk and that is **optimizing a carnivore lifestyle**. **Carnivore is one of the healthiest ways of living**. However, diet like any diet" — **20260520001.md [00:00:21.840] → [00:00:30.950]**

> "discussion is how to optimize a carnivore lifestyle. If you're coming from a perspective of insulin [resistance]" —— [00:00:57.600] → [00:01:01.430]

> "**Carnivore is a strategy. However, it is a dynamic way of life. It is not a diet**" —— [00:04:43.840] → [00:04:50.230]

**R7 关键会议信号**：
- **Meatstock 2026 = Gatlinburg, Tennessee = R7 现场会议**
- **"large gathering of carnivore and carnivore-based folks"**——R7 仍参与 carnivore 社区
- **核心命题**：
  1. "**Carnivore is one of the healthiest ways of living**"（公开声明）
  2. "**Carnivore is a strategy. However, it is a dynamic way of life. It is not a diet**"（与 R2 "carnivore way of life" 一致）

**R7 与 R6 的微妙差异**：
- R6 (20250605) "WHY HUMANS ARE NOT CARNIVORES"——**反 carnivore 教条**（"most hated video ever"）
- **R7 (20260520) Meatstock 演讲**——**"Carnivore is one of the healthiest ways of living"**——**正面支持 carnivore 作为框架**
- 这两个 R6 + R7 立场**完全一致**（"接受 carnivore 作为工具 + 拒绝人类是 carnivore 的生物学命题"），只是 R6 是"反 carnivore 教条"专集，R7 是"carnivore 现场会议"演讲

**Phase 2 必收**：Meatstock 2026 = Cywes R7 现场 carnivore 社区参与 = "carnivore is one of the healthiest ways of living" 公开声明。

---

#### 发现 R7-6（**R7 新国际盟友**）：Shashi Kant Umar（印度心理医生）= "ketogenic metabolic therapy for mental health disease"

> "I work in the same space applying **ketogenic diet or ketogenic metabolic therapy for mental health disease**" — **20260415001.md [00:03:01.760] → [00:03:09.190]**（嘉宾自报）

> "**The first time we met was with Tim No's conference in Cape Town**" — **20260415001.md [00:00:21.840] → [00:00:26.710]**（嘉宾回忆与 Cywes 的首次见面）

**R7 新国际盟友**：
- **Shashi Kant Umar** = 印度心理医生 / 应用 keto 治疗 mental health
- **首次见面** = "Tim No's conference in Cape Town"（**Tim Noakes 在开普敦的会议**）
- **专集时长** = 20260415 是 R7 最长文件（2323 行）
- **Cywes 立场** = "ketogenic metabolic therapy for mental health disease"——**接受 keto 作为精神疾病治疗**

**Phase 2 必收**：
- R7 国际盟友扩张 = Shashi Kant Umar（印度心理医生）
- Cywes 接受 keto 治疗 mental health disease（**R7 新临床应用**）

---

#### 发现 R7-7（**R7 政策行动主义**）：MAHA + RFK + Nina Teicholz 政策阵营公开引用

> "**Nina Ta Schultz** who's been very active uh politically and the **Maha movement** and Ben and Dickman and all these guys like" —— **20260415001.md [01:05:13.200] → [01:05:18.789]**

**R7 政策信号**：
- **Nina Teicholz 公开支持**（"Schultz" = 自动字幕错读，**实指 Teicholz**）—— 与 R5 Ep:383 "I'm with nah on the..." 一致
- **MAHA movement** = Make America Healthy Again = **R7 政策行动主义再激活**
- **Ben and Dickman** = Ben Bikman（BYU 代谢实验室）+ Dickman（待查）—— **R7 把"政策盟友 + 学术盟友"明确并提**

**R6 → R7 政策演化**：
- R5 = Teicholz / Taubes 1 次引用（R5 报告已记录）
- R6 = 政策行动主义沉默（MAHA / RFK / Kennedy 0 命中）
- **R7 (20260415) = 政策行动主义再激活** = Cywes 在 1 文件 1 行内连提 MAHA + Teicholz + Bikman

**Phase 2 必收**：R7 政策阵营 = MAHA + Teicholz + Bikman = "Cywes 在 R7 明确把自己定位为政策行动主义者"。

---

#### 发现 R7-8（**R7 自我叙事**）："I am the voice behind the voice" = Cywes 自身被访谈专集 (20260529)

> R7 末尾 = 20260529001.md = "AN INTERVIEW WITH DR. CYRUS – HE'S THE VOICE BEHIND THE VOICE"——**R7 唯一第三方访谈 Cywes 的专集**

**R7 自反性信号**：
- **Cywes 第一次作为被访谈者出现**（而非主讲人）
- **"HE'S THE VOICE BEHIND THE VOICE"** = 暗示 Cywes 在某种"幕后"角色（可能指他是某 podcast / channel 的幕后嘉宾）

**R7 工具扩张**：R7 显示 Cywes **仍是主讲人，但接受过一次第三方访谈**——Phase 2 可记录这一信号。

---

#### 发现 R7-9（**R7 现场会议细节**）：Meatstock 演讲"carnivore way of life" 完整定义

> "**Carnivore is a strategy. However, it is a dynamic way of life. It is not a diet**" —— **20260520001.md [00:04:43.840] → [00:04:50.230]**

> "of the metabolic diseases, you want to be on a carnivore diet that is the most **metabolically healthy anti-inflammatory** way a human being can eat" — **20260520001.md [00:04:26.160] → [00:04:31.350]**

> "Also, carnivore is one of the best ways to combat the **psychology of eating**" —— [00:04:36.800] → [00:04:40.150]

**R7 carnivore 完整定义**：
1. **Strategy + way of life**（不是 diet）
2. **Most metabolically healthy anti-inflammatory way**（最代谢健康的抗炎方式）
3. **Best way to combat psychology of eating**（对抗 eating 心理学的最佳方式）

**Phase 2 心智模型**：
- **Cywes 接受 carnivore 作为策略 / 生活方式 / 抗炎饮食** = R7 一手完整定义
- **与 R2 (2020-12-09) 一致** = "carnivore way of life" 命名延续到 R7

---

#### 发现 R7-10（**R7 持续信号**）："my friend Nick Norwitz" 升级为口头禅

> "**demonstrated by quite nicely by my friend Nick Norwitz** in his quote unquote **Oreo experiment**. So yeah, you can do" — **20260520001.md [00:57:44.319] → [00:57:51.510]**

> "demonstrated by quite nicely by **my friend Nick Norwitz** in his quote unquote **Oreo experiment**" — **20260520001.md [01:31:18.320] → [01:31:22.790]**

**R7 关键信号**：
- **"my friend Nick Norwitz"** 在 R7 同一文件出现 2 次（演讲口头禅）
- **"Oreo experiment"** 命名 = Norwitz 标志性自我实验

**R5 → R6 → R7 Norwitz 升级**：
- R5 (20240210) = 学术对话 2 命中
- R6 (20250609 + 20251009) = "my friend" 升级
- **R7 (20260520) = "my friend Nick Norwitz" 重复 2 次 = 现场演讲口头禅**

**Phase 2 必收**：R7 = "my friend Nick Norwitz" + "Oreo experiment" 在 Meatstock 现场演讲 = **Cywes 与 Norwitz 公开友谊 + 互相背书的稳定模式**。

---

### 4. R7 新增自创术语 / 显式新框架（**全部** R1-R6 未出现）

| 术语 / 框架 | 一手定义 / 出处 | R1-R6 状态 |
|---|---|---|
| **"AI Revast"** | 20260401001.md [00:18:21.800] | **R1-R6 = 0**（R7 头号新术语）|
| **"mRNA + AI-designed"** atherosclerosis 治疗 | 20260401001.md [00:18:10.680] → [00:18:24.710] | **R1-R6 = 0** |
| **"codex receptor reversal activation"** | 20260401001.md [00:26:56.560] → [00:27:03.910] | **R1-R6 = 0** |
| **"endothelial reprogramming and vascular calcification reversal system"** | 20260401001.md [00:05:34.640] → [00:05:41.230] | **R1-R6 = 0** |
| **"best diet for GLP-1 users"** | 20260221001.md 整集标题 | **R1-R6 = 0**（R7 标题党新模板）|
| **"Meatstock 2026"** | 20260520001.md [00:00:11.280] | **R1-R6 = 0**（R7 现场会议）|
| **"ketogenic metabolic therapy for mental health disease"** | 20260415001.md [00:03:03.599] | **R1-R6 = 0**（R7 嘉宾驱动）|
| **"Maha movement"**（公开引用）| 20260415001.md [01:05:16.000] | **R1-R6 = 0**（R7 政策行动主义）|
| **"use my name, you will get a subsidy"** | 20260221001.md [00:13:19.200] → [00:13:21.670] | **R1-R6 = 0**（R7 商业化信号）|
| **"bilong" / "Lowfelt Soul Food"** | 20260221001.md [00:11:50.800] | **R1-R6 = 0**（R7 南非产品背书）|
| **"Carnivore is a strategy. However, it is a dynamic way of life. It is not a diet"** | 20260520001.md [00:04:43.840] | R2 = "carnivore way of life" 首次命名 / R7 = 完整一句话定义 |
| **"zombie macrophage"** | 20260401001.md 多处 | **R1-R6 = 0**（R7 巨噬细胞命名学）|
| **"carnivore is one of the healthiest ways of living"** | 20260520001.md [00:00:24.640] | R2 = 类似 / R7 = 现场会议公开声明 |
| **"lean mass hyper-responder type diet"** | 20260428001.md [00:01:18.590] | R5-R6 = 多次 / R7 = 整合到 uric acid 整集 |

---

### 5. R7 仍未发现（v3.0 R7 验证 = 任务背景持续警示）

1. **"JFK / Kennedy / 1963-11-22 出生 / 命名"** — R1-R6 = 0 / **R7 = 0**。vN 全期 0 命中。**任务背景彻底不成立**。
2. **"prednizone" 死因** — R1-R6 = 0 / **R7 = 0**。vN 全期无死因证据。
3. **"transfer addiction"** — R1-R6 = 0 / **R7 = 0**。vN 全期 0 命中。
4. **"low-fat lie"** — R1-R6 = 0 / **R7 = 0**。vN 全期 0 命中。
5. **"five white assassins" / "五白"** — R1-R6 = 0 / **R7 = 0**。vN 全期 0 命中。
6. **"carbon score"** — R1-R6 = 0 / **R7 = 0**。vN 全期 0 命中。
7. **"12 step / AA meeting"** — R1-R6 = 0 / **R7 = 0**。vN 全期 0 命中（**v2 任务背景误植彻底确认**）。
8. **"evidence-based" / "RCT" / "Cochrane"** — R1-R6 = 偶发（多为引用历史）/ **R7 = 0**。**Cywes 全期不走 EBM 修辞**。
9. **"apoB"** — R5 = 1 文件 / R6 = 0（用 LDL/胰岛素语境）/ **R7 = 3 文件 (20260224, 20260401, 20260415)** = **R7 显式化**（"ApoB-100" 命名）。
10. **"Peter Attia"** — R6 = 1 文件专集反 Attia / **R7 = 0**。R7 沉默 Attia（Ep:393 已讲完）。
11. **"first bite"** — R1 = 1 / R2-R6 = 0 / **R7 = 0**。仅 R1 1 次。
12. **"harm reduction"** — R1 = 8 / R2 = 1 / R3-R6 = 0 / **R7 = 0**。R3-R7 完全消失。
13. **"went sideways"** — R1-R3 = 多 / R4-R6 = 0 / **R7 = 0**。R4-R7 沉默。
14. **"wallet biopsy"** — R1 = 多 / R5-R6 = 0 / **R7 = 0**。R5-R7 沉默。
15. **"keto moment" / "keto clutter" / "safe haven"** — R2 = 专集 / R3-R6 = 0 / **R7 = 0**。R2 命名后 R3-R7 完全沉默。
16. **"Jane Brown"** — R2 = 4 / R3-R6 = 0 / **R7 = 0**。R3-R7 完全沉默。
17. **Banting & Best 1921 史** — R4 = 3 / R5 = 2 / R6 = 0 / **R7 = 0**。R4-5 短暂显式后 R6-R7 沉默。
18. **Stefansson carnivore 防御** — R5 = Ep 11 / R6 = 0 / **R7 = 0**。R5 显式后 R6-R7 沉默。
19. **Fung co-author** — R5 = 8 / R6 = 0 / **R7 = 0**。R5 显式后 R6-R7 沉默。
20. **Westman / Bikman / Taubes / Teicholz（独立）** — R5 = 多 / R6 = 0 / **R7 = Bikman 1 文件 (20260415 "Ben and Dickman" 中) / Teicholz 1 文件 (20260415 "Nina Ta Schultz")**。**R7 政策行动主义 = 把 Bikman + Teicholz + MAHA 同列 = R5 盟友格局的"政策化"延伸**。
21. **"Randle cycle" / "Philip Randle 1963 论文"** — R4 = 14 / R5 = 2 / R6 = 0 / **R7 = 0**。R6-R7 沉默。
22. **"Prochaska TTM / stages of change / Changing for Good"** — R4 = 显式化 / R5-R6 = 0 / **R7 = 0**。R6-R7 沉默。
23. **"retatrutide"** — R6 = 1 文件反对 / **R7 = 0**。R7 沉默（R6 已表态）。
24. **"GLP-1 + GIP dual agonist" (Mounjaro/Zepbound)** — R6 = 1 文件首次显式 / **R7 = 11/11 全部覆盖** = **R7 全面扩张**。
25. **"ketone IQ"** — R5-R6 = 偶发 / **R7 = 6/11 高密度** = **R7 显式化**（GLP-1 整合专集反复推）。

---

### 6. R7 关键时间锚点（Phase 2 引用准确性参考）

| 日期 | 事件 / 锚文件 |
|---|---|
| **2026-02-21** | "BEST DIET FOR GLP-1 USERS" 整集 + Lowfelt Soul Food 南非 biltong 代言 + "use my name" |
| **2026-02-24** | "WHY HEART DISEASE IS A NUTRITIONAL DISEASE" 心血管营养学整集 |
| **2026-03-14** | "CYCLES OF CHANGE" + Shashi Kant Umar 印度心理医生首次登场（1/2） |
| **2026-03-26** | "RESOLVE YOUR ACID REFLUX – GERD" 整集 + ranitidine/Zantac 撤市提到 |
| **2026-04-01** | **"Breaking News: AI Revast + mRNA + 巨噬细胞吞噬 ApoB100 斑块" 头号新事件** |
| **2026-04-15** | **Shashi Kant Umar 印度嘉宾长访谈（最长文件 2323 行） + MAHA + Teicholz + Bikman 政策行动主义 + "Tim No's conference in Cape Town" 历史回顾** |
| **2026-04-28** | "BEST DIET FOR HIGH URIC ACID & GOUT ON KETO AND CARNIVORE" 整集 + colchicine 治疗 |
| **2026-05-08** | "A 360° LIFESTYLE GUIDE FOR INSULIN RESISTANCE & DIABETES REVERSAL" 第二长文件（2358 行） |
| **2026-05-12** | "INSULIN RESISTANCE & WEIGHT LOSS Q&A – RAPID-FIRE" 短集（352 行） |
| **2026-05-20** | **"OPTIMIZING A CARNIVORE LIFESTYLE" Meatstock 2026 Gatlinburg Tennessee 现场会议演讲 + "my friend Nick Norwitz" + Oreo experiment** |
| **2026-05-29** | **"AN INTERVIEW WITH DR. CYRUS – HE'S THE VOICE BEHIND THE VOICE" 第三方访谈 Cywes 专集** |

---

### 7. R7 备注给 Phase 2 / Phase 3

1. **R7 头号新发现 = 20260401 "AI Revast" 头号背书**——Cywes 公开支持 mRNA + AI 设计的"斑块逆转"新药 = R5-R6 反 lipid-centrism 立场的**最终一致形态**（接受新机制干预 + 拒绝 statins 作为预防首选）。Phase 2 必须收录此集。
2. **R7 整合期 = GLP-1 + carnivore + ketone IQ 三联**：20260221 整集 = R7 标志性整合专集。Phase 2 临床应用矩阵新增"GLP-1 + carnivore"。
3. **R7 商业化信号** = 20260221 "use my name, you will get a subsidy" + Lowfelt Soul Food 南非 biltong 代言 = R1-R6 未观察到的桥接。Phase 2 必收。
4. **R7 新临床应用 = GERD / 酸反流 + Uric acid / 痛风**。两个 2026 整集专集 = R7 临床应用扩张方向。
5. **R7 政策行动主义再激活** = 20260415 "MAHA + Teicholz + Bikman" 同列。R6 政策沉默后 R7 明确把自己定位为政策参与者。Phase 2 必收。
6. **R7 新国际盟友 = Shashi Kant Umar**（印度心理医生）= R7 国际化信号 + keto for mental health 临床应用。
7. **R7 Meatstock 2026 现场会议** = Cywes 在 R7 仍参与 carnivore 社区 + 公开"carnivore is one of the healthiest ways of living"声明。Phase 2 必收（carnivore 立场一致化）。
8. **"my friend Nick Norwitz" 在 R7 重复 2 次** = R5-R6 "my friend" 升级的稳定模式。Phase 2 心智模型可锁定"Cywes ↔ Norwitz 朋友级互相背书"。
9. **"WHY HUMANS ARE NOT CARNIVORES" (R6) + "CARNIVORE IS ONE OF THE HEALTHIEST WAYS OF LIVING" (R7)** = 立场完全一致 = "接受 carnivore 作为工具 + 拒绝人类是 carnivore 的生物学命题"。
10. **R7 自我叙事 = "HE'S THE VOICE BEHIND THE VOICE"**（20260529 第三方访谈专集）—— R7 唯一 Cywes 作为被访谈者出现的专集。Phase 2 可记录"Cywes 在 R7 仍主要是主讲人，偶尔接受第三方访谈"。
11. **R7 盟友格局 = Norwitz（朋友级重复 2 次）+ Noakes（1 次 Cape Town 会议回顾）+ Bikman + Teicholz（政策行动主义同列）+ Shashi（印度新盟友）** = R5-R6 收缩的"再扩张"——R7 把 R5 短暂显式盟友"政策化" + 新国际盟友"实用化"。
12. **R7 keto/carnivore 副作用新方向** = uric acid / gout 整集 = R7 主动暴露 keto/carnivore 不利面（与 R6 "WHY HUMANS ARE NOT CARNIVORES" 反 carnivore 教条一致）。
13. **R7 表达 DNA 升级**：
    - R5 "BEWARE!" 标题党反讽
    - R6 "100% wrong" + "most hated video"
    - **R7 "Breaking News" + "BEST DIET FOR X" 模板 + "use my name"** = 商业化引流 + 标题党
    - 现场会议演讲风格（Meatstock 2026）= 短促 / 反复 / "my friend" 口头禅
14. **"transfer addiction" / "low-fat lie" / "5 white" / "carbon score" / "12 step" / "JFK 命名" / "prednizone 死因" vN 全期 0 命中**——v2 任务背景 7 个误植在 R7 彻底不成立。SKILL 不可包含这些。
15. **R7 = "整合期"信号**：
    - 无新工具（GLP-1 + carnivore 整合 = R6 已展开）
    - 无新自传（无新死亡 / 无新家族病史 / 无新地理位置变更）
    - 无新政策（MAHA 短暂引用，但仍是 R5 盟友"政策化"延伸）
    - **R7 真正新 = AI Revast 背书 + 商业化信号 + 印度盟友 + 政策行动主义再激活 + 现场 carnivore 会议**
16. **R7 "9.1% of US adults using GLP-1" 数据**——[00:04:12.799] "**one in eight Americans conservatively**"——Cywes 引用此数据作为 R7 临床整合的基础 = "GLP-1 用户规模已经达到 ~12.5% 人口级别，carnivore 框架需要整合 GLP-1 而非排斥"。

---

### 8. R7 vs R1-R6 整体趋势（一句话总结）

**R7 = 2026-02 → 2026-05 = "Cywes 实践整合 + 新对手背书 + 政策化"**：
- **AI Revast mRNA 药背书（20260401）= R5-R6 反 lipid-centrism 立场的最终一致形态**
- **GLP-1 + carnivore + ketone IQ 三联整合（20260221）= R7 标志性整合专集**
- **Meatstock 2026 现场会议演讲（20260520）= "carnivore is one of the healthiest ways of living" 公开声明**
- **印度心理医生新盟友（20260415）= R7 国际扩张 + keto for mental health**
- **政策行动主义再激活（20260415）= MAHA + Teicholz + Bikman 同列**
- **商业化信号（20260221 "use my name" + Lowfelt Soul Food 代言）= R1-R6 未观察到的桥接**
- **新临床应用 = GERD 整集（20260326）+ Uric acid 整集（20260428）**
- **第三方访谈专集（20260529 "HE'S THE VOICE BEHIND THE VOICE"）= R7 唯一 Cywes 作为被访谈者**
- **"my friend Nick Norwitz" 重复 2 次（20260520）= R5-R6 朋友级互相背书的稳定模式**
- **"WHY HUMANS ARE NOT CARNIVORES" (R6) + "CARNIVORE IS ONE OF THE HEALTHIEST WAYS OF LIVING" (R7) 立场完全一致**
- **未采纳 = transfer addiction / low-fat lie / 5 white / carbon score / 12 step / apoB-as-first-term (R7 用 "ApoB-100") / EBM 修辞 / Perlmutter / Berg / Attia / Chaffee / Baker / Fung / Westman / Taubes / Stefansson / Randle / Banting 1921 / Jane Brown / keto moment / first bite / went sideways / wallet biopsy / harm reduction / JFK 命名 / prednizone 死因 / retatrutide（R7 沉默 R6 反对）**

---

### 9. R7 整体定性（一手 / 二手 / 我推断）

| 类别 | 内容 |
|---|---|
| **一手** | 所有 grep 命中行（标 [文件名.md HH:MM:SS]） |
| **一手** | AI Revast mRNA 药背书（20260401001.md 整集） |
| **一手** | "BEST DIET FOR GLP-1 USERS" 整合专集（20260221001.md） |
| **一手** | "use my name, you will get a subsidy" 商业化信号（20260221001.md） |
| **一手** | Lowfelt Soul Food 南非 biltong 代言（20260221001.md） |
| **一手** | "WHY HEART DISEASE IS A NUTRITIONAL DISEASE" 整集（20260224001.md） |
| **一手** | Shashi Kant Umar 印度心理医生访谈（20260415001.md 整集 2323 行） |
| **一手** | MAHA + Teicholz + Bikman 政策行动主义同列（20260415001.md） |
| **一手** | "Tim No's conference in Cape Town" 历史回顾（20260415001.md） |
| **一手** | GERD / Acid Reflux 整集（20260326001.md） |
| **一手** | Zantac / ranitidine 撤市提到（20260326001.md） |
| **一手** | Uric acid / gout on keto 整集（20260428001.md） |
| **一手** | colchicine 治疗建议（20260428001.md） |
| **一手** | "360° LIFESTYLE GUIDE" 第二长文件（20260508001.md） |
| **一手** | INSULIN RESISTANCE Q&A 短集（20260512001.md） |
| **一手** | Meatstock 2026 现场会议演讲（20260520001.md） |
| **一手** | "CARNIVORE IS ONE OF THE HEALTHIEST WAYS OF LIVING"（20260520001.md） |
| **一手** | "my friend Nick Norwitz" 重复 2 次（20260520001.md） |
| **一手** | "HE'S THE VOICE BEHIND THE VOICE" 第三方访谈（20260529001.md） |
| **一手** | "Carnivore is a strategy. However, it is a dynamic way of life. It is not a diet"（20260520001.md） |
| **二手** | AI Revast / mRNA 药物临床试验 = **事实外部可查**（cywes 引用） |
| **二手** | Shashi Kant Umar = 印度心理医生 = **事实外部可查** |
| **二手** | Meatstock 2026 = Gatlinburg Tennessee 现场会议 = **事实外部可查** |
| **二手** | Lowfelt Soul Food = 南非 biltong 品牌 = **事实外部可查** |
| **二手** | Nina Teicholz "Schultz" 自动字幕错读 = 实指 = **事实外部可查** |
| **二手** | MAHA movement = Make America Healthy Again = RFK Jr. 主导 = **事实外部可查** |
| **我推断** | R7 = 实践整合期（GLP-1 / carnivore / ketone IQ） = **是观察** |
| **我推断** | R7 商业化信号 = "use my name" + 否认付费（可能存在 affiliate） = **是观察** |
| **我推断** | R7 政策行动主义 = Bikman + Teicholz + MAHA 同列 = Cywes 把自己定位为政策参与者 = **是观察** |
| **我推断** | "AI Revast" 背书 = R5-R6 反 lipid-centrism 立场的最终一致形态 = **是观察** |
| **我推断** | R7 无新自传事件 = 父亲 2020 死亡 + Cape Town/Geneva 出生 + West Palm Beach 现居仍是稳定自传 = **是观察** |
| **不做** | 不评价"主流医学共识" / 不写"局限性" / 不评价"诚信风险" / 不补全外部生平（如 AI Revast 实际临床试验结果 / Shashi 具体国籍 / Meatstock 主办方） |

---

### 10. R7 调研完成度自评

- **grep 命中数**：核心术语（carb addiction / carnivore / keto / insulin / GLP-1 / ApoB / ketone IQ / Norwitz / Noakes / MAHA）已全部覆盖
- **关键专集已识别**：
  - 20260221001.md "BEST DIET FOR GLP-1 USERS"（R7 整合专集）
  - 20260224001.md "WHY HEART DISEASE IS A NUTRITIONAL DISEASE"
  - 20260314001.md "CYCLES OF CHANGE"（印度心理医生 1/2）
  - 20260326001.md "RESOLVE YOUR ACID REFLUX – GERD"
  - **20260401001.md "Breaking News: AI Revast mRNA 药"**（R7 头号新事件）
  - **20260415001.md "CYCLES OF CHANGE" 续集 + 印度嘉宾长访谈**（R7 最长文件 2323 行）
  - 20260428001.md "BEST DIET FOR HIGH URIC ACID & GOUT"
  - 20260508001.md "A 360° LIFESTYLE GUIDE"（R7 第二长文件 2358 行）
  - 20260512001.md "INSULIN RESISTANCE Q&A"
  - **20260520001.md "OPTIMIZING A CARNIVORE LIFESTYLE" Meatstock 2026 现场会议**
  - **20260529001.md "AN INTERVIEW WITH DR. CYRUS" 第三方访谈**
- **未深度读取**：
  - 20260224001.md 完整 heart disease 内容
  - 20260415001.md 完整 2323 行（仅 grep 命中）
  - 20260508001.md 完整 2358 行（仅 grep 命中）
  - 20260529001.md 完整 1856 行（仅 grep 命中）
  - 20260428001.md 完整 colchicine + 尿酸机制
  - 20260326001.md 完整 GERD 机制 + Zantac 历史
- **未深搜**：
  - 完整 Oxalobacter / gut biome 主题
  - 20260512 Q&A 完整问题清单
  - 20260529 第三方访谈"voice behind the voice"具体含义
- **R7 vs R6 关键差异**：
  - R6 末文件 = 20260211
  - R7 起点 = 20260221（10 天间隔）
  - R7 是迄今最短时间窗（3.3 个月 / 11 文件 / 11396 行）

