# 03 - Expression DNA (R4: 2019-07-26 → 2020-07-17)

> 范围：`${HOME}/Documents/女娲造人/@drekberg/` 第 301-400 个 .md 文件（100 个文件）
> 时段：2019-07-26 → 2020-07-17（R4 时段，约 12 个月）
> 对比基线：R1（2010-07 → 2017-05）/ R2（2017-10 → 2018-08）/ R3（2018-08-20 → 2019-07-22）
> **R4 语料：398,940 词 / 100 文件**（R4 比 R3 大 +50%，R4 视频产出继续加速——是 R1 的 1.78×）

---

## 1. 方法论

所有频次由 `grep -ic PATTERN $(cat /tmp/r4_files.txt)` 聚合得到（line 计数，与 R1/R2/R3 方法一致）。
R4 语料明显大于 R3（399K vs 266K，约 1.50×），所以**绝对频次**会自然偏高；
**归一化率（每 10 万词）** 才是真正的表达 DNA 信号——下文所有比较都按归一化率解读。

R3 已确认 `false` 频次被 `contains_ai_summary: "false"` 元数据污染约 100 次。
R4 同理：grep `false` 总命中 104 次，其中 `contains_ai_summary: "false"` 占 100 次，**真实 R4 `false` 仅 4 次**。
下文 `false` 已剔除元数据。

R3 已确认 `true` 不受元数据污染（R3 真实 55 次，R4 真实 82 次）。

---

## 2. 高频词频次表（R4 vs R3 vs R2 vs R1，归一化到 /100K 词）

| 维度 | 词 / 短语 | R1/100K | R2/100K | R3/100K | **R4/100K** | R3→R4% | R1→R4% | 信号 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 核心锚词 | `the body` | 227.2 | 255.2 | 233.2 | **216.0** | -7% | -5% | [一手] 4 期稳态，R4 微降但仍是 #1 主题 |
| 核心锚词 | `your body` | — | 146.6 | 138.9 | **142.6** | +3% | — | [一手] 持续高频，与 `the body` 合并 ≈ 359/100K |
| 核心锚词 | `root cause` | 0.4 | 0.0 | 2.6 | **10.0** | +285% | +2400% | [一手] **R4 全面复活，3.8× 增长** |
| 核心锚词 | `holistic` | 4.9 | 13.2 | 10.1 | **28.0** | +177% | +471% | [一手] **R4 大幅跃升（28/100K 接近 R1 的 5.7×）** |
| 主题 | `insulin` | — | 103.2 | 453.2 | **355.6** | -22% | — | [一手] R4 略降，但仍 ≈ R3 巅峰的 78% |
| 主题 | `keto` | — | 73.7 | 214.0 | **133.6** | -38% | — | [一手] R4 下降，但仍高密度（≈ R2 的 1.8×） |
| 主题 | `carnivore` | — | — | 1.5 | **3.2** | +113% | — | [一手] **R4 翻倍（13 次），carnivore 进入 R4 话语** |
| 主题 | `sugar` | — | 198.5 | 343.2 | **261.9** | -24% | — | [一手] R4 略降 |
| 主题 | `carbs` | — | 155.9 | 313.9 | **97.0** | -69% | — | [一手] R4 大降 |
| 主题 | `blood sugar` | — | 89.2 | 154.7 | **96.0** | -38% | — | [一手] R4 下降 |
| 主题 | `glucose` | — | 29.5 | 107.0 | **94.7** | -12% | — | [一手] R4 略降，仍高密度 |
| 主题 | `fasting` | — | — | 110.7 | **117.0** | +6% | — | [一手] **R4 持续高频（已超过 R3）** |
| 主题 | `hormone` | — | 92.3 | 58.6 | **101.0** | +72% | — | [一手] R4 反弹 |
| 主题 | `cancer` | — | 11.6 | 18.4 | **11.7** | -36% | — | [一手] R4 略降 |
| 主题 | `calorie` | — | 46.5 | 101.4 | **119.5** | +18% | — | [一手] R4 持续上升 |
| 口头禅 | `so` | 1,229.3 | 1,428.0 | 1,409.1 | **1,187.6** | -16% | -3% | [一手] R4 略降（每 84 词 1 次），仍占统治 |
| 口头禅 | `okay` | 114.5 | 20.2 | 63.1 | **65.1** | +3% | -43% | [一手] R4 稳住反弹水平 |
| 口头禅 | `right` | 119.8 | 79.9 | 87.1 | **141.3** | +62% | +18% | [一手] **R4 暴增 62%，"right" 用作确认填充词** |
| 口头禅 | `okay so` 过渡 | — | — | 7.9 | **7.0** | -11% | — | [一手] 稳定 |
| 真/假二元 | `true` | 43.4 | 48.1 | 20.7 | **20.5** | -1% | -53% | [一手] 稳定在 20/100K（绝对数 82） |
| 真/假二元 | `false`（去元数据） | — | ≈ 3 | 1.1 | **1.0** | -9% | — | [一手] **4 期真实 false 极低且稳定**（104 总命中 - 100 元数据 = 4 真实） |
| 强调词 | `absolutely` | — | 20.2 | 13.1 | **16.2** | +24% | — | [一手] 略升 |
| 强调词 | `definitely` | — | 3.9 | 4.5 | **7.5** | +67% | — | [一手] R4 翻倍 |
| 强调词 | `exactly` | — | 10.9 | 10.5 | **14.0** | +33% | — | [一手] 略升 |
| 攻击词汇 | `poison` | 13.0 | 3.9 | 19.1 | **11.5** | -40% | -12% | [一手] R4 回到 R1 水平，攻击密度缓和 |
| 攻击词汇 | `toxic` | 13.9 | 10.9 | 30.0 | **14.7** | -51% | +6% | [一手] R4 回到 R1 水平 |
| 攻击词汇 | `crazy` | — | 4.7 | 6.4 | **5.0** | -22% | — | [一手] 稳定 |
| 攻击词汇 | `stupid` | — | 2.3 | 7.5 | **4.0** | -47% | — | [一手] R4 略降 |
| 攻击词汇 | `insane` | — | 0.8 | 0.0 | **0.0** | 0% | — | [一手] 完全消失（R3、R4 连续归零） |
| 攻击词汇 | `nonsense` | — | — | 1.1 | **0.2** | -82% | — | [一手] 几近归零（仅 1 次） |
| 引用权威 | `study` / `studies` | — | 14.7 | 22.5 | **28.3** | +26% | — | [一手] R4 继续上升 |
| 引用权威 | `research` | — | 30.2 | 19.9 | **25.8** | +30% | — | [一手] R4 反弹 |
| 引用权威 | `published` | — | 5.4 | 39.0 | **31.0** | -21% | — | [一手] R4 略降，但仍 ≈ R3 水平（5.7× R2） |
| 引用权威 | `Mayo` (Clinic) | 8.5 | 0.0 | 5.6 | **4.0** | -29% | -53% | [一手] 略降 |
| 引用权威 | `Lancet` | — | — | 0.4 | **0.0** | -100% | — | [一手] R4 完全不提 |
| 引用权威 | `NIH` | — | 0.0 | 0.0 | **0.0** | 0% | — | [一手] 4 期归零 |
| 引用权威 | `according to` | — | 2.3 | 3.0 | **4.2** | +40% | — | [一手] R4 略升（"according to the CDC/guidelines"） |
| 品牌 | `Wellness For Life` | — | 55.0 | 14.6 | **0.0** | -100% | — | [一手] **R4 完全弃用 WFL 主品牌** |
| 品牌 | `Health Champions` | — | — | 0.0 | **13.7** | +∞ | — | [一手] **R4 启用新主品牌（55 次）**——品牌完全切换 |
| 品牌 | `Ulite` | — | — | — | **0.0** | — | — | [一手] R4 完全不提 |
| 品牌 | `Uveia` | — | — | — | **0.0** | — | — | [一手] R4 完全不提 |
| 签名开场 | `Hey I'm Dr. Ekberg` | — | 23.3 | 10.9 | **5.0** | -54% | — | [一手] R4 继续下降（20 次） |
| 签名开场 | `Hello Health Champions` | — | — | 0.0 | **13.7** | +∞ | — | [一手] **R4 启用新开场范式**（绝对 55 次） |
| 签名开场 | `Hey I'm Dr. Ekberg...holistic doctor and a former Olympic decathlete` | — | — | — | **18.8** | — | — | [一手] **75 次完整签名——R4 主开场句** |
| CTA | `Coming right up` | — | 18.6 | 21.0 | **22.5** | +7% | — | [一手] 微升（绝对 90 次），**核心签名 CTA R4 加强** |
| CTA | `? Coming right up` | — | — | 3.8 | **0.2** | -95% | — | [一手] **"X? Coming right up" R4 几近消失** |
| CTA | `truly master` | — | 38.7 | 18.8 | **22.3** | +19% | — | [一手] R4 反弹，绝对 82 次（`truly master health`） |
| CTA | `the body really works` | — | — | 18.0 | **24.3** | +35% | — | [一手] **R4 持续加密**（绝对 97 次） |
| CTA | `subscribe and hit that notification bell` | — | — | 29.7 | **20.0** | -33% | — | [一手] R4 略降 |
| CTA | `share this video` | — | — | 13.9 | **0.0** | -100% | — | [一手] **R4 完全弃用 "share this video"** |
| CTA | `you don't miss anything` | — | — | 15.8 | **10.7** | -32% | — | [一手] R4 略降 |
| 句法 | `first of all` | — | — | 11.6 | **9.2** | -21% | — | [一手] 略降 |
| 句法 | `if you` (条件句) | — | — | 380.9 | **429.8** | +13% | — | [一手] **R4 继续加密条件句** |
| 句法 | `because` | — | 339.7 | 481.4 | **459.9** | -4% | — | [一手] R4 稳住高位（绝对 1835 次） |
| 句法 | `that's why` | — | — | 30.8 | **32.3** | +5% | — | [一手] 略升 |
| 人称 | `I-contracts` (I'm/I've/I'll) | — | 170.7 | 123.5 | **145.3** | +18% | — | [一手] R4 反弹 |
| 人称 | `I-statements` (I think/I have/I know) | — | 76.8 | 54.1 | **63.6** | +18% | — | [一手] R4 反弹 |
| 人称 | `tag questions` (don't you/isn't it) | — | 98.6 | 9.4 | **1.0** | -89% | — | [一手] **4 期暴跌 99%——R4 几乎无反问句**（绝对 4 次） |

---

## 3. 关键发现（10 条）

### 发现 1：主品牌完全切换 — `Wellness For Life` 100% 弃用 → `Health Champions` 启用（55 次）
R2 baseline: WFL = 55/100K（高峰）
R3: WFL = 14.6/100K（弱化 -73%）
**R4: WFL = 0/100K（完全弃用 100% 下降），Health Champions = 13.7/100K（新启用 0 → 55 次）**

R4 是 Ekberg 视频品牌身份从 "Wellness For Life" 切换到 "Health Champions" 的完整过渡期。
开场句范式也跟着切换：
- R2: `"Hey I'm Dr. Ekberg with Wellness For Life and if you'd like to truly master"`
- R3: `"Hey I'm Dr. Ekberg I'm here at VidSummit"`（开场杂化）
- **R4: `"Hello Health Champions today I'm going to talk about..."`（绝对新开场）—— 51 次**

- [一手] 例：`[20200103001.md 00:00:00.000] "Hello Health Champions. Today I'm gonna talk about the five secrets to losing"`
- [一手] 例：`[20191227001.md 00:00:00.030] "hello health champions today I want to talk to you about how to get through the"`
- [一手] 例：`[20191118001.md 00:00:49.399] "Hey I'm Dr. Ekberg I'm a holistic doctor and a former Olympic decathlete and if"`
- [我推断] "Health Champions" 是 R4+ 主品牌（COVID 时期崛起？2019-12 启用），R3 是 0% → R4 是 100% 取代

### 发现 2：`holistic` 暴增 177%（10 → 28/100K），"holistic doctor" 升级为核心身份
R3 holistic 10.1 → R4 28.0（+177%）。R1 以来 4 期最高。
更关键：**"holistic doctor and a former Olympic decathlete" 完整签名 75 次**（R3 几乎不用）。
- [一手] 例：`[20191118001.md 00:00:49.399] "Hey I'm Dr. Ekberg I'm a holistic doctor and a former Olympic decathlete and if"`
- [一手] 例：`[20191115001.md 00:00:45.050] "Hey I'm Dr. Ekberg. I'm a holistic doctor and a former Olympic decathlete and if you"`
- [一手] 例：`[20191202001.md 00:01:12.250] "Hey I'm Dr. Ekberg I'm a holistic doctor and a former Olympic decathlete and if"`
- [我推断] R4 视频明确用"整脊师 + 奥运十项全能"双重身份定位，holistic 标识从 R3 偶用 → R4 系统化签名

### 发现 3：`root cause` 全面复活（2.6 → 10.0/100K，+285%）
R1: 0.4 / R2: 0.0 / R3: 2.6 / **R4: 10.0**（绝对 40 次，是 R3 的 5.7×）。
**R4 是 Ekberg 把 "root cause" 修辞完全激活的阶段**——holistic + root cause 同时上涨，说明他明确转向"功能医学/holistic 路线"叙事。
- [一手] 例：`[20190802001.md 00:07:26.950] "anymore does it address the root cause what is the root cause of obesity and"`
- [一手] 例：`[20190802001.md 00:07:33.340] "weight gain the root cause is called insulin insulin is a storage hormone"`
- [一手] 例：`[20190802001.md 00:08:02.380] "you hungry so does it address the root cause which is insulin resistance and"`
- [我推断] "root cause = insulin resistance" 在 R4 已是公式化叙事（root cause → 胰岛素抵抗 → 代谢综合征）

### 发现 4：代谢主题密度从 R3 巅峰略降但 `fasting` 超越 R3
R3 是 metabolic 框架最高峰（insulin 453/keto 214/glucose 107），R4 略降（insulin 356/keto 134/glucose 95）——但 `fasting` 117/100K（+6%）**反超 R3**，且 `calorie` 119/100K（+18% 持续上升）。
- [一手] 例：`[20190726001.md 00:10:55.300] "the tools of low carb high fat keto intermittent fasting to lower your"`
- [一手] 例：`[20190726001.md 00:11:22.120] "because low carb high fat keto intermittent fasting they're all tools"`
- [我推断] R4 视频从单一"keto" 框架转向"keto + fasting + calorie awareness" 的三合一饮食工具箱

### 发现 5：`carnivore` 翻倍（1.5 → 3.2/100K，+113%）
R3 carnivore 4 次，R4 13 次（绝对数）。虽仍属小众词，但 R4 是首次稳定出现的阶段。
- [一手] 例：`[20190726001.md 00:14:28.900] "eating too much protein some people can go carnivore and reduce reduce their"`
- [一手] 例：`[20190809001.md 00:03:35.400] "protein a lot of people again are having success with carnivore diets and a lot"`
- [一手] 例：`[20191104001.md 00:19:43.800] "longer digestive tracts then do carnivores and this allows humans to"`
- [我推断] R4 后期可能开始酝酿 carnivore 主题（呼应 R5/R6 大量推 carnivore 阶段）

### 发现 6：攻击词全面缓和 — `poison` -40% / `toxic` -51% / `stupid` -47% / `nonsense` -82% / `insane` 0%
R3 攻击词回弹期（R3 poison 19/toxic 30/stupid 7.5）结束。
R4: poison 11.5 / toxic 14.7 / stupid 4.0 / nonsense 0.2 / **insane 0.0**（R3 已是 0）。
**R4 攻击词水平全面回到 R1 baseline**。
- [一手] 例：`[20190823001.md 00:06:45.110] "infection it could be toxicity could be long-term low-grade toxicity or it could"`
- [一手] 例：`[20190826001.md 00:03:38.600] "because blood sugar is toxic to the brain that's why diabetics get these"`
- [一手] 例：`[20190920001.md 00:01:29.810] "the body is never stupid it never does anything random or unintelligent it's like gravity"`
- [一手] 例：`[20190920001.md 00:02:20.640] "stupid behavior of the cell is cause whatever the body does something it's adapting to something"`
- [我推断] R4 攻击词缓和 = 品牌升级期话术软化（"Health Champions" 是更温和的社群感品牌，相对 WFL 时代更少对抗）

### 发现 7：反问句彻底消失 — 4 期 99% 暴跌（98.6 → 1.0/100K）
R1: 未测 / R2: 98.6 / R3: 9.4（-90%） / **R4: 1.0（-89% 续降，绝对仅 4 次）**
**R4 是 Ekberg 完全转向"我说你听"独白式讲座的稳态期**——他基本不再用反问句。
- [我推断] 这与视频长度/结构有关：R3 起他开始用长讲座型内容，R4 完全定型——从 "isn't it?" / "don't you?" 转为 "because..."（详见发现 8）
- [一手] 例（仅存的 1 次 `right?`）：`[20200316001.md 00:04:51.310] "What would fasting be without bulletproof coffee right?"`
- [一手] 例（仅存的 1 次 `aren't you`）：`[20200515001.md 00:17:23.459] "12 and as far as energy drinks go I've never actually had even one aren't you supposed"`

### 发现 8：因果链 `because` 仍加密 459.9/100K（绝对 1835 次），条件句 `if you` 持续上升至 429.8
R2: because 339.7 / R3: 481.4 / **R4: 459.9**（稳住，绝对数远超 R3 1835 vs 1282）
R3: if you 380.9 / **R4: if you 429.8（+13%）**
**R4 论证模式 = "if you (条件)... because (原因)... that's why (结论)" 三段式因果链**——这是 R3 模式的延续和强化。
- [一手] 例：`[20190729001.md 00:02:16.410] "60s or even upper 50s without being a problem because you have ketones as an"`
- [一手] 例：`[20190729001.md 00:02:48.510] "A1c is A1c is a better measurement than simply fasting glucose because it"`
- [一手] 例：`[20190729001.md 00:05:07.080] "because you fell down the stairs then you're hurting because you fell down the"`
- [一手] 例：`[20190809001.md 00:07:00.190] "if you eat a lot of carbs but even if you don't you're still giving the body"`
- [我推断] R4 视频是高度结构化的"假设—因果—结论"科普讲座——条件句 + because 同时加密 = 论证链加密

### 发现 9：`right` 暴增 62% (87 → 141/100K)，`okay` 稳定 65
R3: right 87.1 / R4: **right 141.3（+62%，绝对 564 次）**。`right?` 标签问句仅 1 次，所以 `right` 几乎全是确认/填充词（"right?" 或 "that's right"），不是反问。
- [一手] 例：`[20190829001.md 00:09:07.820] "healthy lifestyle right a1c has come up one point but hey what's what's a point"`
- [一手] 例：`[20190729001.md 00:17:35.640] "have certain hormones in your body that peak right before you get up in the"`
- [我推断] R4 的 `right` 暴增不是反问化，而是 "right?" 用作停顿确认符（YouTube 视频中常见的口头填充）

### 发现 10：核心 CTA `X? Coming right up` 范式 95% 消失，但 `Coming right up` 绝对数 +61% (56→90)
R2: 18.6 / R3: 21.0 / **R4: 22.5（`Coming right up` 总数）**
R2: ?CRU 3.8 / R3: ?CRU 3.8 / **R4: ?CRU 0.2（-95%，仅 1 次）**
**R4 仍用 "Coming right up" 预告，但 "X? Coming right up" 双句范式基本消失**——预告更碎片化、不再用"X? Coming right up"做结构化预告。
- [一手] 例：`[20191101001.md 00:00:18.539] "Coming right up."`
- [一手] 例：`[20191115001.md 00:00:39.960] "people. Coming right up!"`
- [一手] 例：`[20191129001.md 00:00:22.140] "findings. Coming right up"`
- [我推断] R4 视频结构改变——从 R2/R3 的"开场提问 → Coming right up" 双段式 → R4 的"主题陈述 → Coming right up" 单段式

### 发现 11（补充）：R4 后期出现 `share ten principles` / `top 10 foods` 等清单式开场
R4 开始用"top 10 / five secrets / ten principles / 5 signs"清单式标题结构（与 R3 的提问式"X? Coming right up"不同）。
- [一手] 例：`[20200306001.md 00:00:39.660] "anything in this video I will share ten principles with you about how fat works"`
- [一手] 例：`[20200124001.md 00:00:00.000] "hello health champions today I want to share with you the top 10 foods to avoid"`
- [一手] 例：`[20200103001.md 00:00:00.000] "Hello Health Champions. Today I'm gonna talk about the five secrets to losing"`
- [我推断] 这是 YouTube SEO 优化策略——R4 起 Ekberg 转向"listicle"清单式标题（受疫情居家观众激增影响）

---

## 4. R4 表达 DNA 速记（One-paragraph profile）

**Sten Ekberg R4 表达 DNA** = 稳态身体锚点（`the body` 216/100K + `your body` 143/100K）+ 代谢框架绝对主导（`insulin` 356/100K + `fasting` 117/100K + `keto` 134/100K + `carnivore` 3.2/100K 萌芽）+ 全面复活 holistic/root cause 叙事（`holistic` 28/100K + `root cause` 10/100K，均为 R1 以来最高）+ 品牌完全切换（`Wellness For Life` 0/100K → `Health Champions` 13.7/100K）+ 完整签名 `holistic doctor and a former Olympic decathlete` 18.8/100K（75 次）+ 攻击词缓和回 R1 水平（`poison` 11.5 / `toxic` 14.7 / `stupid` 4.0 / `insane` 0.0）+ 持续独白化（`tag questions` 1.0/100K 99% 暴跌 + `because` 460/100K + `if you` 430/100K）+ 启用 `Hello Health Champions` 新开场范式（13.7/100K，51 次）+ 弃用 `share this video`（100% 归零）+ 保留 `Coming right up` 22.5/100K（绝对 90 次）但失去 `X?` 提问范式（0.2/100K 暴跌 95%）。

---

## 5. 与 R1+R2+R3 baseline 的关键差异表

| 信号 | R3 判断 / R3 数据 | R4 实证数据 | R4 真实状态 |
|---|---|---|---|
| `Wellness For Life` 主导 | R3 = 14.6/100K | R4 = 0/100K | **R4 完全弃用 WFL——品牌身份完全切换** |
| `Health Champions` 取代 | R3 = 0 | R4 = 13.7/100K | **R4 启用 HC 为新主品牌（55 次）** |
| `holistic` 偶用 | R3 = 10.1/100K | R4 = 28.0/100K | **R4 大幅上升（+177%）——"holistic doctor" 进入核心签名** |
| `root cause` 复活 | R3 = 2.6 | R4 = 10.0 | **R4 全面复活（+285%）——"root cause = insulin" 公式化** |
| 攻击词回弹 | R3 poison 19 / toxic 30 / stupid 7.5 | R4 poison 11.5 / toxic 14.7 / stupid 4.0 | **R4 攻击词全面缓和回 R1 水平** |
| 独白化 | R3 tag questions 9.4/100K | R4 tag questions 1.0/100K | **R4 反问句 4 期暴跌 99%** |
| `X? Coming right up` 预告 | R3 = 3.8 | R4 = 0.2 | **R4 双句预告范式 95% 消失** |
| `carnivore` 预热 | R3 = 1.5（4 次） | R4 = 3.2（13 次） | **R4 翻倍——carnivore 话题进入 R4 话语** |
| `Wellness For Life` 主导判断 | R2 baseline "R2 反复使用" | R4 100% 归零 | **R4 彻底退出——品牌完成切换** |
| `false` 否定式建构 | R3 真实 false = 1.1 | R4 真实 false = 1.0 | **4 期真实 false 极低且稳定（R4 总命中 104 - 元数据 100 = 真实 4）** |
| `if you` 条件句 | R3 = 380.9 | R4 = 429.8 | **R4 条件句持续加密（+13%）** |
| `because` 因果链 | R3 = 481.4 | R4 = 459.9 | **R4 稳住 R3 巅峰水平** |
| `published` 权威信号 | R3 = 39.0 | R4 = 31.0 | **R4 略降（-21%），但仍 ≈ R2 的 5.7×** |
| `Wellness For Life` → `Health Champions` | R3 锐降 73% | R4 = 0/100K vs 13.7/100K | **R4 品牌完成"硬切换"——不是渐变，是替代** |

---

## 6. R4 vs R3 关键变化汇总（按幅度排序）

| 排名 | 指标 | R3→R4% | 解读 |
|---|---|---:|---|
| 1 | `Wellness For Life` | -100% | 主品牌完全弃用 |
| 2 | `share this video` CTA | -100% | 该 CTA 消失 |
| 3 | `? Coming right up` 范式 | -95% | 双句预告范式消失 |
| 4 | `tag questions` 反问句 | -89% | 4 期暴跌 99% |
| 5 | `nonsense` | -82% | 几近归零 |
| 6 | `carbs` | -69% | 主题词密度大降 |
| 7 | `toxic` | -51% | 攻击词缓和回 R1 |
| 8 | `Hey I'm Dr. Ekberg` 开场 | -54% | 开场更分散 |
| 9 | `poison` | -40% | 攻击词缓和 |
| 10 | `insulin` | -22% | 代谢主题微降 |
| 11 | `keto` | -38% | 主题密度下降 |
| 12 | `Health Champions` 品牌 | +∞ (0→55) | 新主品牌启用 |
| 13 | `holistic` | +177% | holistic 身份升级 |
| 14 | `root cause` | +285% | 全面复活 |
| 15 | `carnivore` | +113% | carnivore 萌芽 |
| 16 | `right` 填充词 | +62% | 用作 "right?" 停顿 |
| 17 | `the body really works` CTA | +35% | 加密 |
| 18 | `because` 稳住 | 459.9 | 高密度论证链维持 |
| 19 | `if you` 条件句 | +13% | 持续加密 |
| 20 | `Coming right up` 绝对数 | +61% (56→90) | CTA 绝对频次上升 |

---

## 7. 验证命令（可复现）

```bash
# R4 核心 grep 命令（R4 100 文件合并 = 398,940 词）
grep -ric "the body" $(cat /tmp/r4_files.txt)        # 862
grep -ric "your body" $(cat /tmp/r4_files.txt)       # 569
grep -ric "root cause" $(cat /tmp/r4_files.txt)      # 40
grep -ric "insulin" $(cat /tmp/r4_files.txt)         # 1419
grep -ric "keto" $(cat /tmp/r4_files.txt)            # 533
grep -ric "fasting" $(cat /tmp/r4_files.txt)         # 467
grep -ric "carnivore" $(cat /tmp/r4_files.txt)       # 13
grep -ric "\\bokay\\b" $(cat /tmp/r4_files.txt)      # 260
grep -ric "\\bright\\b" $(cat /tmp/r4_files.txt)     # 564
grep -ric "poison" $(cat /tmp/r4_files.txt)          # 46
grep -ric "toxic" $(cat /tmp/r4_files.txt)           # 59
grep -ric "stupid" $(cat /tmp/r4_files.txt)          # 16
grep -ric "Coming right up" $(cat /tmp/r4_files.txt) # 90
grep -ric "? Coming right up" $(cat /tmp/r4_files.txt) # 1
grep -ric "truly master" $(cat /tmp/r4_files.txt)    # 82
grep -ric "Wellness For Life" $(cat /tmp/r4_files.txt) # 0
grep -ric "Health Champions" $(cat /tmp/r4_files.txt) # 55
grep -ric "Hello Health Champions" $(cat /tmp/r4_files.txt) # 51
grep -ric "Hey I'm Dr. Ekberg" $(cat /tmp/r4_files.txt) # 20
grep -ric "holistic doctor and a former Olympic" $(cat /tmp/r4_files.txt) # 75
grep -ric "share this video" $(cat /tmp/r4_files.txt) # 0
grep -ric "because" $(cat /tmp/r4_files.txt)         # 1835
grep -ric "if you" $(cat /tmp/r4_files.txt)          # 1715

# 关键元数据污染验证
grep -c 'contains_ai_summary: "false"' $(cat /tmp/r4_files.txt)  # 100（剔除后真实 false = 4）

# 归一化：count / 398940 × 100000
```

---

## 8. 未发现 / 缺失数据

- `Ulite` / `Uveia` 品牌：R4 完全未启用（0/0），推测 R4+ 仍未启动这两个品牌（可能 R5+ 才出现）
- `Lancet` / `NIH` / `WHO` 等权威机构引用：R4 仍极少（0 次），R3 baseline 0 命中保持——**Ekberg 4 期不依赖机构名引用**
- `Mayo Clinic` 引用：R4 略降（5.6 → 4.0/100K），仍偶尔引用
- R4 视频的"直播/访谈"成分：R4 仍以单人讲座为主（`Hey I'm Dr. Ekberg` 仅 20 次 = 仅 20% 视频有此签名），但 `Hello Health Champions` 开场 51 次说明 R4 大部分视频是标准化讲座
- COVID-19 影响：R4 跨越 2019-07 → 2020-07，恰是 COVID 爆发期。R4 末段（2020-03~2020-07）是否主题转向免疫/维生素 D？需后续 R5 研究
- `Ulite` / `Uveia`：仍是 0，未见品牌曝光

---

## 9. 10 条发现索引（按重要性）

1. **品牌完全切换**：`Wellness For Life` 100% 弃用 → `Health Champions` 启用（55 次）—— R4 是品牌身份硬切换期
2. **`holistic` 暴增 177%**（10 → 28/100K），"holistic doctor + Olympic decathlete" 完整签名 75 次
3. **`root cause` 全面复活 285%**（2.6 → 10/100K）—— holistic + root cause 同时上涨
4. **攻击词全面缓和回 R1 水平**：`poison` -40% / `toxic` -51% / `stupid` -47% / `insane` 0%
5. **反问句 4 期暴跌 99%**（98.6 → 1.0/100K）—— 独白化稳态期
6. **`X? Coming right up` 双句范式 95% 消失**（3.8 → 0.2/100K）—— 预告结构改变
7. **`carnivore` 翻倍**（1.5 → 3.2/100K，+113%）—— R4 是 carnivore 萌芽期
8. **`because` 稳住 459.9 + `if you` 加密 429.8**——"条件→因果→结论"三段式论证链定型
9. **`Hello Health Champions` 新开场范式 13.7/100K**（51 次）—— R4 启用新开场
10. **`share this video` CTA 100% 归零**——R4 弃用该 CTA，与新开场范式不匹配
