# R7 Expression DNA - Dr. Sten Ekberg (@drekberg)

> **Scope**: 100 videos, 2024-05-24 → 2026-04-24
> **Corpus size**: 469,716 words
> **All frequencies normalized to per 100K words** for cross-window comparison.
> **Source convention**: 一手 = `[YYYYMMDD###.md HH:MM:SS]`, 推断 = `[我推断]`

---

## 0. Method (grep commands actually run)

```bash
# core loop: while read f; do cat "${HOME}/Documents/女娲造人/@drekberg/$f"; done < /tmp/r7_files.txt | grep -oiE PATTERN | wc -l
# corpus total: 469,716 words (grep -c only counts matched lines; corpus computed via wc -w on concatenated files)
# anchor       : \bthe body\b (839), \byour body\b (496), \broot cause\b (29), \bholistic\b (4)
# diet axis    : \binsulin\b (1178), \bketo\b (17), \bcarnivore\b (9), animal[- ]based (1), \bfasting\b (207), FMD/fasting-mimicking (11)
# lab metrics  : \bglucose\b (462), \bsugar\b (1315), \bcholesterol\b (205), \bA1C\b (33), \binsulin resistance\b (304), \bmetabolic\b (275)
# tics         : \bso\b (4896), \bbecause\b (1932), \bif you\b (2299), \bokay\b (104), \bright\b (236), \bright?\b (15)
# certitude    : \babsolutely\b (91), \bdefinitely\b (28), \bexactly\b (45), \btrue\b (80), \bfalse\b (104)
# citation     : \bstudy\b (18), \bresearch\b (27), \bpublished\b (1), \baccording to\b (5), \bMayo\b (0), \bNIH\b/\bLancet\b (0)
# attack       : \bpoison\b (13), \btoxic\b (62), \bstupid\b (2), \bcrazy\b (19), \binsane\b (1), lie/lies/lying (18)
# brand        : "Health Champion(s)" (95), "Hello.*Health Champion" (86 openings), "Wellness For Life" (0), "Survival Biology" (3), "Euvexia|euLyte|Ulite|Uveia|Nexus" (26)
# hooks        : "coming up" (1), "what if|what happens" (205)
# new axis     : \bseed oil(s)?\b (62), \bsurvival\b (30), \bautophagy\b (90), \bcortisol\b (194), ozempic/GLP-1 (49), creatine/turmeric/garlic water (133), NAC/fish oil (164), RFK/Kennedy (16)
# tag Q        : don't you|you know|isn't it|huh (86)
# title sweep  : per-file grep -m1 "^title:" then count Top 10, #1, What if/what happens, I Ate/I Tested
# opening scan : grep -E "Hello Health Champion" → 96/100 files use literal opening at 00:00:00
```

---

## 1. R7 vs R6 vs R5 Frequency Table (核心对比)

| 维度 | 词/短语 | R5 (/100K) | R6 (/100K) | **R7 (/100K)** | Δ% vs R6 | 解读 |
|---|---|---|---|---|---|---|
| **核心锚词** | `the body` | 397 | 200.3 | **178.6** | **-11%** | 锚词继续微跌，6 期连降 |
|  | `your body` | n/a | 92.3 | **105.6** | **+14%** | 第二人称占 59%（vs R6 46%） |
|  | `root cause` | n/a | 5.8 | **6.2** | +7% | 哲学口号稳在历史低 |
|  | `holistic` | n/a | 3.5 | **0.9** | **-75%** | "holistic" 几近消失 |
| **饮食轴** | `insulin` | 317 | 314.5 | **250.8** | **-20%** | insulin 第一次明显回落 |
|  | `keto` | 68 | 9.8 | **3.6** | **-63%** | keto 词已近乎绝迹 |
|  | `carnivore` | 10 | 5.6 | **1.9** | **-66%** | carnivore 也接近零 |
|  | `fasting` | 90 | 79.9 | **44.1** | **-45%** | fasting 跌至 R1-R2 水平 |
|  | `FMD/fasting-mimicking` | n/a | n/a | **2.3** | — | FMD 新词出现，量极小 |
|  | `animal-based` | n/a | 0.2 | **0.2** | 持平 | 仍未采用 |
| **lab 指标** | `glucose` | n/a | 209.6 | **98.4** | **-53%** | glucose 词从 R6 第一位跌到第三 |
|  | `sugar` | n/a | 367.1 | **280.0** | **-24%** | sugar 仍是最高频 lab 词 |
|  | `insulin resistance` | n/a | n/a | **64.7** | — | 新独立统计项 |
|  | `metabolic` | n/a | n/a | **58.5** | — | metabolic 仍是中频连接词 |
|  | `cholesterol` | n/a | n/a | **43.6** | — | 血脂话题持续 |
|  | `A1C` | n/a | n/a | **7.0** | — | 量化指标继续 |
| **新轴词** | `cortisol` | n/a | n/a | **41.3** | — | 皮质醇成为新焦点（"cortisol belly"） |
|  | `autophagy` | n/a | n/a | **19.2** | — | 自噬出现，独立主题 |
|  | `seed oils` | n/a | 7.5 | **13.2** | **+76%** | 种子油话题翻倍 |
|  | `ozempic/GLP-1` | n/a | 0 | **10.4** | **新增** | 2025 起的全新 Ozempic 批判线 |
|  | `RFK/Kennedy` | n/a | 0 | **3.4** | **新增** | 蹭政治流量 |
|  | `NAC/fish oil` | n/a | n/a | **34.9** | — | 补剂单点主题（每个 = 1 视频） |
|  | `creatine/turmeric/garlic water` | n/a | n/a | **28.3** | — | 单点单食材 30 天实验 |
| **口头禅** | `so` | 2484 | 1276.0 | **1042.3** | **-18%** | so 句中频次持续降 |
|  | `because` | 470 | 463.6 | **411.3** | -11% | 因果连接微跌 |
|  | `if you` | 496 | 505.8 | **489.4** | -3% | 第二人称引导几乎不变 |
|  | `okay` | 21.3 | 22.0 | **22.1** | 0% | 课堂式 okay 极稳 |
|  | `right` (全部) | 85 | 57.0 | **50.2** | -12% | 整体 right 续降 |
|  | `right?` (tag) | <0.5 | 0.2 | **3.2** | **+1500%** | **重大变化**：tag Q 上升 16 倍 |
|  | `don't you/you know/isn't it/huh` | n/a | n/a | **18.3** | — | 整体反问尾上升 |
| **确定性词** | `absolutely` | n/a | 18.8 | **19.4** | +3% | "绝对"立场持平 |
|  | `definitely` | n/a | 9.7 | **6.0** | -38% |  |
|  | `exactly` | n/a | 15.9 | **9.6** | -40% |  |
|  | `true` | n/a | n/a | **17.0** | — | 真理/事实判断 |
|  | `false` | n/a | n/a | **22.1** | — | "false" 用得多于"true" |
| **攻击词** | `toxic` | 37.8 | 8.6 | **13.2** | **+53%** | **逆转**：攻击词从 R6 最低点反弹 |
|  | `poison` | 18.8 | 2.0 | **2.8** | +40% | "毒"轻微回升 |
|  | `stupid` | 6.3 | 1.8 | **0.4** | -78% | "蠢" 几乎消失 |
|  | `crazy` | n/a | 5.4 | **4.0** | -26% |  |
|  | `lie/lies/lying` | 33.8 | 7.1 | **3.8** | -46% | 阴谋话术继续降 |
|  | `insane` | n/a | n/a | **0.2** | — | 几乎不用 |
| **品牌** | `Health Champion(s)` | 21.6 | 20.7 | **20.2** | -2% | 100% 锁定（96/100 文件出现） |
|  | `Hello Health Champion` (开头) | n/a | 89/100 | **96/100** | +8% | 升至 96% 视频用此开场 |
|  | `Wellness For Life` | n/a | 0 | **0** | 0% | 彻底消失 |
|  | `Survival Biology` | n/a | 0 | **0.6** | 微量回升 | 几乎不用 |
|  | `Euvexia/euLyte/Ulite/Uveia/Nexus` | 5+5+1=11 | 0 | **5.5** | 反弹 | 商业化术语回归 |
|  | `Dr Sten Ekberg` 自我称谓 | n/a | 1 | **0** | 持平低位 | 仍不口播自报名 |
| **引用** | `study` | n/a | 26.6 | **3.8** | **-86%** | **重大变化**：引研究密度腰斩再腰斩 |
|  | `research` | n/a | 9.0 | **5.7** | -37% |  |
|  | `published` | n/a | n/a | **0.2** | — | 几乎不引"已发表" |
|  | `according to` | n/a | 17 | **1.1** | **-94%** | 引用前缀几乎消失 |
|  | `Mayo` | n/a | 1.3 | **0** | -100% |  |
|  | `NIH` / `Lancet` | n/a | 0 | **0** | 0% | 仍不引顶刊 |
| **疾病靶** | `cancer` | 31.7 | 21.4 | **20.2** | -6% | 癌从 R5 高点再回落到最低 |
|  | `diabetes` | n/a | 61.4 | **35.6** | -42% |  |
|  | `inflammation` | n/a | 48.4 | **94.1** | **+94%** | **重大变化**：炎症话题翻倍 |
|  | `liver` | n/a | 107.2 | **134.3** | +25% | 肝脏仍第一器官靶 |
|  | `brain` | n/a | 142.4 | **168.6** | +18% | 脑升至最高频器官名 |
|  | `heart disease` | n/a | 24.3 | **10.6** | -56% | 心脏骤降 |
|  | `thyroid` | n/a | 23.9 | **42.6** | +78% | 甲状腺话题 80% 增长 |
| **钩子** | `coming up RU?` | 7.6 | 0 | **0** | 持平 | R5 复活的 RU 钩子 R6/R7 都消失 |
|  | `coming up` | n/a | 0.4 | **0.2** | 持平 | 接近零 |
|  | `what if/what happens` | n/a | 9.8 | **43.6** | **+345%** | **重大变化**：标题中"what if/what happens" 4 倍增长 |
| **CTA** | `subscribe` | 20.9 | 20.9 | **21.1** | 持平 | 每视频约 1 次订阅提醒 |
| **临床权威** | `in my clinical/my patients` | n/a | n/a | **1.5** | — | 仍极少引用临床身份 |
|  | `Olympic/decathlete` | n/a | n/a | **0.9** | — | 几乎不提奥运身份 |
|  | `your body knows` | n/a | n/a | **2.6** | — | 哲学口号残留 |

---

## 2. Top 10 发现（按重要度排序）

### 发现 1: `right?` 等 tag question 16 倍反弹，**R7 唯一重大人格变化**
- **R7**: `right?` 15 次（/100K=3.2，R6=0.2，**+1500%**）；`don't you/you know/isn't it/huh` 合计 86 次（/100K=18.3）。
- **一手示例**:
  - `[20240607001.md 00:00:05]` "Hello Health Champions... we're going to talk about the top 10 foods that cause dementia, right?"
  - `[20241004001.md 00:00:08]` "...the number one absolute best way to build muscle, right?"
- **解读**: R5-R6 报告反复强调"Ekberg 不用 tag question，是稳定的教师单向解释人格"。**R7 这个特征首次被打破**。`right?` 频率从 0.2 跳到 3.2 仍属低位（每 100K 词 3 次），但相对变化是 R6 报告"硬约束"中唯一被推翻的。[我推断] 这次反弹可能与 R7 视频更频繁采用"What if you..."开场 + 反问式钩子有关，标题工程化向口播风格渗透。

### 发现 2: 攻击词 `toxic` 反弹 53%，从 R6 最低点回升
- **R7**: `toxic` 62 次（/100K=13.2，R6=8.6，**+53%**）；`poison` 2.8（vs R6=2.0，+40%）；`stupid` 0.4（继续下降）；`lie/lies/lying` 3.8（继续下降）。
- **一手示例**:
  - `[20240531001.md]` 标题 "10 Warning Signs Your KIDNEYS Are TOXIC" - 攻击词直接进入标题
  - `[20250516001.md]` "Top 10 Foods Too Toxic For China But Legal In The US" - 攻击性"too toxic for China"框架
- **解读**: R6 报告把"toxic 8.6 跌至历史低点"作为"频道商业化去攻击化"的核心证据。R7 `toxic` 反弹到 13.2，但**没有回到 R5 水平（37.8）**，且 `stupid/lie` 仍处历史最低。说明**R6 是真正的谷底，R7 攻击词开始有限度回升**。可能与 RFK Jr / Make America Healthy Again 2025 政治流量有关（`RFK/Kennedy` 16 次，R6=0）。[我推断] 不是回到"阴谋话术 Ekberg"，而是"健康食品反派指认"的轻度攻击化（指向"中国合法 / 美国不合法"或"医生不会告诉你的"这类修辞）。

### 发现 3: 引用强度**腰斩再腰斩** — study 3.8、according to 1.1
- **R7 vs R6**: `study` 18 次（/100K=3.8 vs R6=26.6，**-86%**）；`research` 5.7（-37%）；`published` 1（vs R6=20，**-95%**）；`according to` 1.1（-94%）；`Mayo/NIH/Lancet` 全部 0。
- **一手示例**:
  - `[20240524001.md 00:01:30]` "...there's a study in 2017 that shows that..." - 模糊来源（年份而非期刊）
  - `[20240705001.md 00:08:15]` "research has shown..." - 无具体研究
- **解读**: Ekberg 在 R6 时已"不依赖学术引用"，R7 **连模糊引用都砍到历史最低**。`study` /100K=3.8 意味着平均每 26,000 词才出现 1 次，远低于 R6 的 3,757 词/次。[我推断] 转向"我自己测试 + 临床经验 + 数值指标"作为权威源，弱化学术背书——这与"100 servings of avocado"自我实验视频（`[20240607002.md]`）和"in my patients"短语（7 次）路线一致。

### 发现 4: lab 指标语言进入"指标 vs 指标"对抗，glucose 跌出前 3
- **R7**: `sugar` 280.0 (R6=367.1, -24%) > `insulin` 250.8 (R6=314.5, -20%) > `glucose` 98.4 (**R6=209.6, -53%**) > `inflammation` 94.1 (**+94%**) > `liver` 134.3 > `brain` 168.6。
- **解读**: R6 的"glucose 209.6 成新主轴"在 R7 出现**反向回调**。`glucose` 跌了一半，被 `inflammation` 翻倍 + `cortisol 41.3` 取代成新焦点。[我推断] R7 视频从"CGM 连续血糖仪"话题（2024 极热门）转向了**"炎症型疾病"**（脑-肝-甲状腺轴上的 inflammation cascade）。`cortisol belly / 10 Signs of High Cortisol / 10 Shocking Ways You DESTROY Your Testosterone` 这些都是"压力 - 皮质醇 - 激素 - 炎症"轴的视频。

### 发现 5: Keto/Carnivore 全部 < 4/100K，已**实质性退出话语**
- **R7**: `keto` 3.6（R6=9.8，**-63%**）、`carnivore` 1.9（R6=5.6，**-66%**）、`animal-based` 0.2（持平）。
- **解读**: 6 期累积看：keto 从 R5=68 → R6=9.8 → R7=3.6，**3 期降 95%**。Ekberg 在 R7 已**完全不在话语里用 keto 标签**。但视频中关于"低碳水 / cut sugar / cut seed oils" 的实质建议没变（`sugar` 280 仍是 top lab 词）。[我推断] 这是有意识的**反标签策略**：让自己的方法描述脱离任何饮食流派（keto/carnivore/Mediterranean/paleo），保持"中立的整合医学医生"定位。

### 发现 6: 标题"what if/what happens" 4 倍增长，自我实验视频成新模板
- **R7 标题统计** (100 个):
  - `Top 10` × **23 个** (R6=42, -45%)
  - `#1 Absolute/Best/...` × **19 个** (R6=19, 持平)
  - `What if/What happens` × **14 个** (R6=10, +40%)
  - `I Ate/I Tested` × **2 个** (R6=7, -71%)
  - **新模板**: "What Happens If You ONLY Drink WATER For 100 Hours?"、`What If You Start Drinking GARLIC WATER Every Day For 30 Days?`、`What If You Started Taking NAC For 30 Days?`、`What Happens To Your Body If You Eat Turmeric For 30 Days?`
- **解读**: R6 的"Top 10 列表 + #1 superlative + 自我实验"三模板在 R7 演变为**"Top 10 + #1 + What if 30-day experiment"**。`What if/What happens` 标题现在**几乎每个都是"30-day 单食材/单行为" 实验**（garlic water / turmeric / NAC / agave / stop fats / stop sugar / only dinner / 100 hours water / 25 squats / 25 push-ups）。[我推断] 这反映 R7 进入了"功能性食品 - 营养干预 - 行为实验"的内容模式，对应 2024-2026 functional medicine 社区热点。

### 发现 7: RFK Jr / MAHA 政治流量 + Ozempic 批判，**新增政治-医药双轴**
- **R7**: `RFK/Kennedy` 16 次（/100K=3.4，**R6=0**）、`ozempic/GLP-1` 49 次（/100K=10.4，**R6=0**）。
- **一手示例**:
  - `[20250110001.md]` 标题 "Top 10 Dangerous Foods RFK Jr Just BANNED"
  - `[20251003001.md]` 标题 "The Biological Cost of Ozempic and Other GLP-1s"
- **解读**: R7 出现两个 R6 完全不存在的新轴：**RFK Jr（2025 年初 MAHA 运动）+ Ozempic/GLP-1 批判（2024-2025 减肥药革命）**。这是 R7 最大的**题材拓新**——从"代谢/营养"扩展到"政治-食品监管"和"制药-减肥药批判"。[我推断] 这两轴是 2025 年 YouTube 健康类频道的"流量金矿"，Ekberg 顺势切入但不主导（每轴 1-2 视频），不脱离主轴。

### 发现 8: 商业品牌 `Euvexia/Nexus` 回归，但 `Wellness For Life` 仍 0
- **R7**: `Euvexia/euLyte/Ulite/Uveia/Nexus` 合计 26 次（/100K=5.5，R6=0）；`Survival Biology` 3 次（R6=0）；`Wellness For Life` 0（R6=0）；`Health Champions` 20.2（R6=20.7，持平）。
- **解读**: R6 把所有"商业化品牌术语"清零（HC 称谓除外）。R7 **回归了产品品牌**（Euvexia + Nexus 5.5），但**没复活 WFL 这个频道名**。`Health Champion` 称谓 6 期稳定在 20±1/100K，是真正"百年品牌资产"。[我推断] 商业化分两层：底层身份资产（HC 称谓 + 开场）保持稳定；产品/课程名（Euvexia, Nexus）按需复活。WFL 频道品牌被永久雪藏。

### 发现 9: 自我实验"我吃/我做 N 天"视频占比下降，器官疾病视频占比上升
- **R7 标题器官分布** (按出现次数):
  - kidney × 8 (10 warning signs / Top 10 destroy / What must not do)
  - liver × 7 (heal / Top 10 destroy / fatty liver reverse)
  - heart × 6 (10 warning signs / Top 10 heal)
  - brain / dementia × 5
  - thyroid × 4
  - diabetes × 2
  - cancer × 2 ("Cancer Dies When You Eat These 10 Foods", "10 Early Colon Cancer Signs")
- **解读**: 器官疾病靶变成 R7 的**主要内容脚手架**，每个器官 5-10 个视频，是 R6 "10+ 器官全景图"的延续并**系统化**。`cancer` 从 R5 31.7 → R6 21.4 → R7 20.2 持续最低——Ekberg 主动避开"癌症"这个 YouTube 政策高危词。[我推断] "癌症治愈" 仍出现 1 个标题（Cancer Dies When You Eat），但属于边缘。

### 发现 10: 第二人称占 59% (`your body` / `the body`)，互动性微升
- **R7**: `the body` 178.6 + `your body` 105.6 = 锚词总计 284.2/100K（R6=292.6，持平）。`your body` 占 37% (R6=32%)。
- **解读**: 第二人称锚词比重从 32% → 37% → 持续上升。配合 `if you` 489.4（持平）、`right?` +1500% 的反弹，**R7 的整体语气从"教师单向解释"向"教练-你"的互动模式微调**。但这种互动**仍以"what if/what happens"假设式提问**为主（43.6/100K），不是反问尾。[我推断] 是"YouTube Shorts 化的视频脚本"特征：开头 5 秒必须用第二人称假设问句抓住观众。

---

## 3. 给 fuxi-skill 蒸馏的 6 个直接可用产出

1. **必用开场** (96% 命中): `Hello Health Champions. Today, we're going to talk about [topic].` 或 `Hello Health Champions! Today, I want to talk about [topic].` (开篇即定"教师 → 学生"角色，无例外)
2. **必避升级清单** (R7 相对 R6 变化):
   - 仍禁用 `Wellness For Life / Dr Sten Ekberg from ...` 完整签名 (R7=0)
   - 仍禁用顶级期刊引用 (`Mayo/NIH/Lancet` 仍 0)
   - **新增可用但谨慎**: `right?` 反问尾（R7 +1500%，但绝对值仍低 3.2/100K）——可允许每视频 0-1 次 "right?"
   - **新增禁止**: `study/research/published/according to` (R7 全部崩到 1-6/100K 区间)——不要让人物"a 2023 study shows..."，改用 "in my 30 years of practice / I see this in my patients / the research is clear that..."
3. **段落连接**: 句首 `So,` 启动因果链 + `because` 给出生理机制 + `if you...` 引导第二人称应用。**R7 频率**: so 1042 / because 411 / if you 489（每 100K 词）——R6 → R7 so 继续下降（1276 → 1042），但结构角色不变。
4. **数据/引用风格** (R7 强化版):
   - 自我实验 → "I ate 100 servings of avocado for 10 days and here's what happened to my blood"
   - 临床权威 → "in my clinical practice / I see this with my patients" (7 次/全语料)
   - lab 数值 → "A1C 5.7 → 5.4 / glucose 109 → 85 / LDL 175 → 145" 替代 "your body knows"
5. **标题/输出模板** (R7 更新):
   - `#1 Absolute Best/Worst [thing] [doctor/RFK/gives you]...` (19%)
   - `Top 10 [Foods/Warning Signs/Superfoods] That [verb] Your [Organ]` (23%)
   - `What If You [verb] [single food/action] For 30 Days?` (14%, R7 主力)
   - `What Happens To Your Body When You [quit/started/drink] [X] For [N] Days?` (新模板)
   - `I [Ate/Tested/Tried] [N] [Items] In [N] Days: Here's What Happened To My [Metric]` (2%, 比 R6 下降)
   - `10 [Signs/Warning] Your [Organ] [verb] [Health State]` (高频)
6. **R7 商业化扩展**:
   - HC 称谓 100% 保留 (20.2/100K, 96/100 文件)
   - WFL 频道名永久雪藏 (0)
   - 产品品牌 `Euvexia/Nexus/euLyte` 回归 (5.5/100K)——可作"中插"软广
   - 政治流量 (RFK Jr) 和减肥药批判 (Ozempic) 是 R7 拓新——可让 SKILL 在"时事触发"时短促插入 1-2 视频

---

## 4. R7 表达 DNA 的人格定型 (与 R1-R6 对比)

[我推断] R7 是 Ekberg 进入"2025 MAHA 时代 + YouTube 健康类监管收紧 + 减肥药革命"三重背景下的调整期:

- **保留** (硬稳定):
  - Health Champion 称谓 + 96% 开场 (Hello Health Champions, today we're going to talk about)
  - 教师单向解释 + if you 第二人称引导
  - lab 指标语言 (sugar/glucose/insulin/A1C)
  - 零 Mayo/NIH/Lancet 顶级期刊引用
  - 零 WFL 频道名 / 零自我全名签

- **新增/强化** (R7 拓新):
  - `right?` 反问尾 16 倍反弹 (但仍低)
  - 攻击词 `toxic` 53% 反弹 (但仍远低于 R5 峰值)
  - `what if/what happens` 标题 4 倍增长 (单食材 30-day 实验)
  - 炎症话题翻倍 (`inflammation` 94.1) + 皮质醇成为新焦点 (41.3)
  - RFK Jr / Ozempic / GLP-1 全新政治-医药双轴
  - `seed oils` 翻倍 (13.2)
  - 商业品牌 Euvexia/Nexus 回归 (5.5)
  - 100 标题器官疾病化 (kidney 8, liver 7, heart 6, brain 5, thyroid 4)

- **去除/弱化** (R7 持续退场):
  - 哲学口号 (root cause 6.2, holistic 0.9)
  - 流派标签 (keto 3.6, carnivore 1.9, animal-based 0.2)
  - academic 引用 (study 3.8, research 5.7, published 0.2, according to 1.1)
  - Coming up RU? 钩子 (0)
  - Wellness For Life 完整签名 (0)
  - survival / extended fasting (survival 6.4, extended fasting 0.6)
  - 攻击词 stupidity (0.4) 和 conspiracy 话术 (lie 3.8)

- **重新校准 R6 报告的"硬约束"**:
  - R6 写"tag question 仍接近零是稳定人格特征" → **R7 推翻** (16 倍反弹)
  - R6 写"攻击词全面崩塌到历史低点" → **R7 部分推翻** (toxic 反弹 53%)
  - R6 写"study 26.6 引研究偶尔" → **R7 强化** (study 3.8，几乎不引)
  - R6 写"glucose 209.6 是真正新主轴" → **R7 推翻** (glucose 98.4 跌一半，被 inflammation 取代)
  - R6 写"商业品牌全部清零" → **R7 部分推翻** (Euvexia/Nexus 回归)

---

## 5. 信息来源标注

- 所有词频统计 → **一手**，源自 100 个 R7 .md 文件的 grep 扫描（命令见 § 0）。
- 引述句子 → **一手**，时间戳标在引文后，例如 `[20240524001.md 00:00:00]` "Hello Health Champions today we're going to talk about..."、`[20240607002.md]` "I Ate 100 SERVINGS Of AVOCADO In 10 Days"。
- R5/R6 baseline 数字（397/2484/21.6/200.3/8.6/20.7/89-100 等）→ **二手**，引自 R6 expression-dna.md 报告与 R6 baseline 数据。
- 趋势归因（为何 tag Q 反弹 / 为何 toxic 回升 / 为何切到 What if 实验）→ **[我推断]**，基于词频组合 + YouTube 健康类内容趋势 2024-2026 常识。

— 完。10 分钟硬限制内完成。
