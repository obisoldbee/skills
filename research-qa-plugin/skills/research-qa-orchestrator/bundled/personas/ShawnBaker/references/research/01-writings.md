# R01: 著作维度调研 (100 files, 2018-01-01 → 2020-01-23)

## 轮 1/17 (2018-01-01 → 2020-01-23)

**素材范围**: `${HOME}/Documents/女娲造人/@ShawnBakerMD/20180101001.md` ~ `20200123001.md` (100 个 .md 文件)
**调研方式**: 关键词 grep + 重点文件 Read
**核心人物**: Dr. Shawn Baker, MD (整骨外科医生 background per self-statements)
**关键人物/组织**: Joe Rogan, Paul Saladino, Rhonda Patrick, Chris Kresser, Joel Kahn, Dave Feldman, Frank Tufano, Mickie van Dorpe

---

## 轮 2/17 (2020-01-27 → 2022-11-29)

**素材范围**: `${HOME}/Documents/女娲造人/@ShawnBakerMD/20200127001.md` ~ `20221129001.md` (100 个 .md 文件)
**调研方式**: 关键词 grep + 重点文件 Read
**关键人物/组织（R02 新增）**: Layne Norton (新对手, 2022 出现), Kyrie Irving / Cam Newton (vegan 受伤范例), KY Furneaux (Naked and Afraid carnivore), Glenelg Zynga (rancher 盟友), Will Harris / Joel Salatin (regenerative 盟友)
**注意**: 本轮未发现 "revero" 概念。anima-based 一词 2022 年开始高频使用（carnivore 近义词）。

---

## 1. R02 调研命令一览 (grep + 命中数)

| 关键词 | 命令 | 命中文件数 | 最高单文件命中 |
|---|---|---|---|
| `revero` | `grep -ciE "revero" $(ls \| sort \| sed -n '101,200p')` | **0** | 0 |
| `carnivore` | `grep -ciE "carnivore" $(ls \| sort \| sed -n '101,200p')` | **57** | 35 (20200202) |
| `animal.based\|animal based` | `grep -ciE "animal.based\|animal based" $(ls \| sort \| sed -n '101,200p')` | **5** | 4 (20220805) |
| `MeatRx\|meat rx\|meatrx` | `grep -ciE "MeatRx\|meat rx\|meatrx" $(ls \| sort \| sed -n '101,200p')` | **9** | 6 (20200202) |
| `seed oil` | `grep -ciE "seed oil" $(ls \| sort \| sed -n '101,200p')` | **8** | 6 (20220716) |
| `fiber` | `grep -ciE "fiber" $(ls \| sort | sed -n '101,200p')` | **7** | 22 (20220626) |
| `cholesterol` | `grep -ciE "cholesterol" $(ls \| sort \| sed -n '101,200p')` | **10** | 36 (20200801) |
| `insulin` | `grep -ciE "insulin" $(ls \| sort \| sed -n '101,200p')` | **10** | 18 (20200319) |
| `keto\|ketogenic` | `grep -ciE "keto\|ketogenic" $(ls \| sort \| sed -n '101,200p')` | **10+** | 22 (20220825) |
| `vegan\|vegetarian` | `grep -ciE "vegan\|vegetarian" $(ls \| sort \| sed -n '101,200p')` | **30+** | 27 (20200224) |
| `plant` | `grep -ciE "plant" $(ls \| sort \| sed -n '101,200p')` | **10+** | 13 (20200129) |
| `cancer` | `grep -ciE "cancer" $(ls \| sort \| sed -n '101,200p')` | **9** | 4 (20200202) |
| `longevity\|aging\|age` | `grep -ciE "longevity\|aging\|age" $(ls \| sort \| sed -n '101,200p')` | **10+** | 22 (20200227) |
| `rogan` | `grep -ciE "rogan" $(ls \| sort \| sed -n '101,200p')` | **10+** | 12 (20200129) |
| `netflix\|game.changer\|documentary` | `grep -ciE "game.changer\|netflix\|documentary" $(ls \| sort \| sed -n '101,200p')` | **5** | 2 |
| `zero carb` | `grep -ciE "zero carb\|zerocarb" $(ls \| sort \| sed -n '101,200p')` | **3** | 6 (20220826) |
| `allin\|allday` | `grep -ciE "allin\|allday" $(ls \| sort \| sed -n '101,200p')` | **6** | 6 (20200428) |
| `ancestral\|evolution` | `grep -ciE "ancestral\|evolution" $(ls \| sort \| sed -n '101,200p')` | **6** | 4 (20200206) |
| `regenerative` | `grep -ciE "regenerative" $(ls \| sort \| sed -n '101,200p')` | **9** | 8 (20200224) |
| `layne norton\|norton` | `grep -niE "layne norton\|norton" $(ls \| sort \| sed -n '101,200p')` | **2** | (20200326, 20220312) |

**关键发现**:
- `revero` 0 命中 → **R02 没有出现 revero 概念** (我推断：revero 是 2023+ 后期产物，未在本轮浮现)
- `carnivore` 仍是绝对主导词 (57 文件)，与 R01 一致
- `animal based` 在 R02 后段 2022 年新出现 (5 文件)，主要为 R02 新增
- Layne Norton 在 R02 出现 2 次：2020-03 首次 (Layne Norton, Naked and Afraid)，2022-03 第二次 (animal based 主题)

---

## 2. R02 核心论点 (5-10 个发现)

### 2.1 carnivore 是肉+动物性食物，**包括乳制品/蛋**（R02 强化版 vs R01）
- **他/她说过的**:
  - `[20200202001.md 00:00:11–00:00:27]` 开头 FAQ 列表: "Can I eat eggs? Can I eat dairy? Can I drink stevia? Can I drink alcohol? Can I do backflips?" 表明 carnivore 包含 dairy 和 egg，不禁止 stevia/alcohol
  - `[20200202001.md 00:02:08]` "My knee pain continued eating carnivore until I eliminated dairy and then my knee healed very rapidly" - 表明 dairy 不是每个人必吃，可以 elimination
  - `[20220627001.md 00:02:13–00:02:17]` "people doing elimination diets carnivore diets some of them include dairy successfully some do not"
- **R02 演化**: R01 是"肉是 ancestral 食物"；R02 强化 carnivore 包含 dairy/egg/甚至 stevia/alcohol 的灵活性
- **真实属性**: 真信念 (≥5 次)

### 2.2 **Baker 自称"carnivore"命名者**（R02 新增，重要发现）
- **他/她说过的**:
  - `[20220627001.md 00:10:39–00:11:06]` "this was that can one of the reasons i call this a carnivore diet because animal animal products as carbs... that's one of the reasons i named it the carnivore if you guys don't know that i was the guy that came up with the carnival diet wrote the book called the carnivore diet and now it's become common uh parlance"
  - "I was the guy that came up with the carnivore diet" - 自报命名者身份
- **R02 新出现**（vs R01）
- **真实属性**: 他/她自述
- **我的推断**: 视频内单一来源声称，未与其他来源交叉验证 → 不能独立确认命名优先权

### 2.3 **animal-based 与 carnivore 互通使用**（R02 新增）
- **他/她说过的**:
  - `[20220627001.md 00:11:08]` "for for this style of eating this animal-based eating all right guys let me know"
  - `[20220805001.md 03:19 / 04:53]` "go more in a more animal based fashion"; "went on a more animal-based diet"
  - `[20220825001.md 16:33]` "add anything but animal based ingredients"
  - `[20220826001.md 31:30]` "you have all these animal-based foods that you are full of vitamins and"
  - `[20220312001.md]` 标题 "Response to Layne Norton's criticism of animal based diets" - 在 2022 年已开始用 "animal based" 替代 "carnivore" 来回应批评
- **R02 新出现** (vs R01 完全没出现)
- **真实属性**: 真信念 (5 个文件 ≥5 次)

### 2.4 **anti-meat agenda = 营养指南杀了人** (R02 强化的道德框架)
- **他/她说过的**:
  - `[20200127001.md 00:01:42–00:01:56]` "the nutritional guidelines killed my mom and almost killed me I try to honor my mom's life by living my best life and help those are in their journey who want it we have to fight this anti meat agenda so this isn't anyone else's loved ones"
  - 引用教练的妈妈 52 岁死于 T2D / CHF / kidney disease
- **真实属性**: 真信念
- **R02 延续**: R01 已有"fight the lies"，R02 强化"营养指南 = 杀人"的具体故事

### 2.5 **regenerative agriculture 是环境-健康双解** (R02 强化)
- **他/她说过的**:
  - `[20200127001.md 00:02:53–00:03:34]` "he is rebuilding the soil he's actually putting carbon into the ground just like you know the White Oaks pasture ranch which is confirmed on a study so we're seeing more and more guys that are actually putting carbon back into the ground and so they are doing far better than we could ever hope to do with the fake P protein stuff where they continued to till in mono crop and degrade the soil"
  - `[20200206001.md 10:47–10:51]` "it's always better time to step up need a revolution guys we can do it with regenerative agriculture"
- **R02 强化**: R01 已有 grass-fed 提及；R02 把 regenerative 与 carbon sequestration 直接挂钩
- **真实属性**: 真信念
- **新盟友 (R02)**: Glenelg Zynga (Alder Supremo Ranch, Idaho), Will Harris, Joel Salatin (regenerative 三剑客), White Oak Pastures (有 study 引用)

### 2.6 **grain-finished vs grass-finished 不是健康问题，只是环境问题** (R02 新增明确立场)
- **他/她说过的**:
  - `[20200202001.md 00:02:39–00:02:50]` "the argument about grain-finished, grass grass-finished, regenerative, that is an environmental argument. It's not so much of a health argument. I know there's people that disagree with that. Be that as it may, the thousands of results I've seen show that they both seem to work equally as well, quite honestly"
- **R02 新增立场**: 明确将 grain-fed/grass-fed 划分从健康挪到环境
- **真实属性**: 真信念 (单一文件但叙述清晰)

### 2.7 **Layne Norton = R02 新对手** (vs R01)
- **他/她说过的**:
  - `[20200326001.md 01:17–01:26]` 标题 "Layne Norton, Naked and Afraid and Doctors being muzzled!" 整期; 描述 "this is so lame Norton made a video talking about some comment I made"
  - `[20220312001.md 00:00:08–00:00:12]` "when you say nutrition uh person fitness person by the name of elaine norton i've i've met wayne before i think he's an"; `[05:28]` "leigh norton i respectfully disagree"
  - `[20220312001.md 04:01]` Saladino 引用 (Rogan 出现)
- **R02 新出现**: 整个 R01 没有提及 Layne Norton
- **真实属性**: 真信念 (2 次直接对立, 跨度 2020-03 → 2022-03)

### 2.8 **Joe Rogan 是反复盟友 (not "too aggressive" 标题但内容是辩护)** (R02 延续)
- **他/她说过的**:
  - `[20200221001.md]` 整期主题 "Joe Rogan too aggressive on carnivore?" (Baker 替 Rogan 辩护)
  - `[20200202001.md]` 出现 4 次 Rogan 引用
  - `[20200201001.md]` 11 次 Rogan 命中
  - `[20200129001.md]` 12 次 Rogan 命中
- **R02 延续**: R01 已有 Rogan 核心盟友，R02 同样
- **真实属性**: 真信念 (10+ 文件提及)

### 2.9 **vegan 运动员反复受伤 = 蛋白质利用差** (R02 强化)
- **他/她说过的**:
  - `[20200221001.md 00:02:08–00:02:29]` "in the world of vegan athletes we've got Kyrie Kyrie Irving is out done season over shoulder you know he can join Cam Newton in a list of growing list of vegans have gotten hurt and can't can't recover and we'll say well dr. Baker all athletes get hurt we see the recovery process in vegans is extremely slow relative to other athletes"
  - `[20200221001.md 00:02:36–00:03:12]` "KY Furneaux she was a stunt woman that did naked and afraid' the TV show twice once as a vegetarian she survived ended up eating meat... took her two years to recover from that six weeks... she went back on the show several years later as a carnivore... felt good back in the gym without any problem within two or three days"
- **R02 强化**: 用名人运动员 + 真人秀案例论证 vegan 恢复慢
- **真实属性**: 真信念

### 2.10 **fiber 神话仍持续反对** (R02 后期 2022 集中爆发)
- **他/她说过的**:
  - `[20220312001.md]` 20 次 fiber 命中 (整期)
  - `[20220626001.md]` 22 次 fiber 命中
  - `[20201007001.md]` 6 次 fiber
- **R02 延续**: R01 已有 fiber 神话; R02 后段 2022 集中爆发
- **真实属性**: 真信念 (7 文件)

---

## 3. R02 关键盟友/对手演变

### 盟友（R02 延续 R01 + 新增）
- Joe Rogan (R02 延续, 2020-02 专门一期辩护)
- Paul Saladino (R02 延续, 2020-01/02 多次提及"被攻击")
- Glenelg Zynga / Will Harris / Joel Salatin (R02 新增, regenerative agriculture 阵营)
- KY Furneaux (R02 新增, Naked and Afraid 真人秀 carnivore 案例)
- MeatRx 团队 (MeatRx 9 次提及, 含 2020-01/02/03/10, 2022-08 podcast)

### 对手（R02 延续 + 新增）
- Joel Kahn (R02 延续, 2020-02 嘲弄 + 2020-08 "Gout and Dr Joel Kahn 'debate'" 整期)
- Dr. Baker 反复用 "the doctors" 复数泛称 (R02 延续 R01)
- Layne Norton (R02 **新对手**, 2020-03 + 2022-03 两次冲突)
- Harvard (笼统被引用, 2020-01 母亲案例 "anti meat study from Harvard")

### 中立/被引述
- Kyrie Irving, Cam Newton (vegan, 作反面案例)
- Ky Furneaux 出现于案例分析

---

## 4. R02 立场演化追踪

| 维度 | R01 (2018-01 → 2020-01) | R02 (2020-01 → 2022-11) |
|---|---|---|
| carnivore 定义 | 肉 + 蛋 + 乳制品 | 同样（但 R02 进一步允许 stevia/alcohol "can I do backflips"） |
| animal-based 一词 | **未出现** | **2022 年开始高频使用**, 与 carnivore 互通 |
| revero 概念 | **未出现** | **未出现**（grep 0 命中）|
| 命名权主张 | 未明确主张 | **2022-06 明确主张 "I was the guy that came up with the carnivore diet"** |
| regenerative 农业 | 已有 grass-fed 提及 | **强化**: 直接挂钩 carbon sequestration + 引出 White Oak Pastures study |
| fiber 反对 | 已确立 "fiber 神话" | R02 后期 2022 年集中爆发（20+ 次/期）|
| Layne Norton | 未出现 | **R02 新对手** (2020-03 首次冲突, 2022-03 升级) |
| Joel Kahn | R01 已被嘲弄 | R02 同样 (2020-08 gout debate 整期) |
| Joe Rogan | R01 核心盟友 | R02 同样 (2020-02 整期辩护 "too aggressive") |
| 道德框架 | "fight the lies" | **强化**: "营养指南 killed my mom" 具体故事 |
| 公司化 MeatRx | 已存在 (R01 已有 meatrx.com) | R02 同样 (9 次提及, 含 podcast) |

---

## 5. 调研方法 + 限制

- 关键词 grep 命中数已记录 (Section 1)
- 重点文件 Read 数量: 3 (20200127, 20200202, 20200221)
- 限制: 100 个文件中只 Read 3 个整文件头部 100 行，其他 97 个仅靠 grep 命中位置
- 限制: revero 一词 grep 0 命中，可高置信度报告 R02 未出现
- 限制: 部分 grep 命中未抽取上下文（如 20220825001 22 次 keto, 20220626001 22 次 fiber, 20200801001 36 次 cholesterol, 20200227001 22 次 age）
- 限制: "anima-based" 5 个文件中 4 个来自 2022 年（20220312, 20220627, 20220805, 20220825, 20220826），分布集中于轮 2 后段

---

## 6. 待 R03-R17 验证的开放问题

- revero 概念何时首次出现？R03+ 必须查
- "carnivore 命名权"主张在 R03+ 是否被其他人物引用/挑战
- Layne Norton 对立是否升级 (R03+ 应追踪)
- animal-based 是否在 R03 替代 carnivore 成为主导词
- 公司化 (revero, MeatRx Inc, 商业产品) 在 R03+ 是否成型

---

## 轮 3/17 (2022-11-30 → 2023-04-28)

**素材范围**: `${HOME}/Documents/女娲造人/@ShawnBakerMD/20221130001.md` ~ `20230428001.md` (100 个 .md 文件)
**调研方式**: 关键词 grep + 重点文件 Read
**R03 重点问题**: (a) revero 是否首次出现 (b) 公司化叙事 (c) longevity/aging 长期主义 (d) 立场是否演化

---

## 7. R03 调研命令一览 (grep + 命中数)

| 关键词 | 命中文件数 | 命中总次数 | 关键变化 vs R02 |
|---|---|---|---|
| `revero` (大小写不敏感) | **0** | **0** | R02 也是 0 → **R03 仍 0 命中**（R03 重点查无果）|
| `MeatRx` / `meat.rx` / `meatrx` | **0** | **0** | R02 9 命中 → **R03 完全消失**，从品牌词降到隐式 |
| `carnivore` | 40 | 171 | R02 57 → R03 40，**绝对值下降**但仍主导 |
| `animal.based` | 7 | 14 | R02 5 → R03 7，**继续增长** |
| `seed oil` | 18 | 95 | R02 8 → R03 18，**R03 核心主题**（专门有 1 期 41 次） |
| `insulin` | 34 | 201 | R02 10 → R03 34，**R03 全面爆发** |
| `sugar` | 45 | 392 | R02 弱 → R03 45 文件，**R03 最高频概念** |
| `processed` | 42 | 293 | R02 未统计 → R03 42 文件 |
| `inflammation` | 33 | 112 | R02 未统计 → R03 33 文件 |
| `fiber` | 14 | 120 | R02 7 → R03 14，**翻倍**但非单期集中 |
| `cholesterol` | 14 | 145 | R02 10 → R03 14，**显著上升** |
| `keto` / `ketogenic` | 16 / 10 | 54 / 26 | R02 10+ → R03 26 keto 词频，**R03 副线** |
| `cancer` | 16 | 58 | R02 9 → R03 16，**近翻倍** |
| `aging` | 13 | 36 | R02 10+ → R03 13 文件，**稳定存在**（含"aging/reverse"反复出现）|
| `longevity` | 4 | 15 | R02 10+ → R03 4 文件，**衰减**（aging 替 longevity）|
| `company` | 5 | 12 | R02 6 → R03 5，**微量存在**（无公司化主旋律）|
| `vegan` | 16 | 75 | R02 30+ → R03 16，**减半**（被 seed oil/inflammation 让位）|
| `regenerative` | **0** | **0** | R02 9 → R03 0，**完全消失**（R03 让位给炎症/种子油）|
| `mTOR` / `PUFA` | 0 / 0 | 0 / 0 | R03 未引入这两个 longevity/脂质学术语 |
| `book` / `publish` / `amazon` | 5 / 100 / 0 | 21 / 114 / 0 | publish 100 是元数据（vtt 来源），不计入内容 |
| `GLP-1` / `Ozempic` / `semaglutide` | 见 20230104 单独 | 1 期 | **R03 新话题**（GLP-1 减肥药批判）|
| `world.carnivore.month` | 5 | - | **R03 新活动词**（2023-01 集中提及）|

**关键负面发现**:
- **`revero` 在 R03 整个 100 文件 0 命中**（精确 grep, 大小写不敏感, 含 `Revero` / `revero` / `Rvero`）。R02 也是 0 命中 → **revero 概念要到 R04 以后才会浮现**（如果会出现）。这意味着 R03 不能回答"revero 完整出现 + 公司化叙事 + 长期主义话题"这个 R03 重点。
- **`MeatRx` 在 R03 完全消失** (0 命中)。R02 提及 9 次 → R03 0 次。推断：Baker 在 R03 已不用 MeatRx 这个品牌词进入 YouTube 标题/口播，但网站/meatrx.com 可能仍在运营（未在本数据集体现）。
- **`regenerative` 在 R03 0 命中**，R02 是 9 命中 → **regenerative 农业彻底从 R03 主线退出**。

---

## 8. R03 核心论点 (10 个发现)

### 8.1 三大"杀手食材"= seed oils + sugar + grains (R03 核心框架)
- **他/她说过的**:
  - `[20230326001.md 00:00:01.920]` 整期标题 "These 3 Ingredients Are Killing You (REMOVE THEM NOW!)" - Baker 亲口
  - `[20230326001.md 00:00:14.940–00:01:24.780]` "number one these so-called seed oils... the second common ingredient and it's everywhere is sugar... the final ingredient grains grains can be very problematic"
  - `[20230326001.md 00:03:22.739–00:03:24.710]` "all have anti-nutrients in them oxalates phytates lectins which can potentially compete with absorption of nutrients and leech out some of the nutrients from the body they can cause gut irritation and inflammation which can lead to the so-called leaky gut"
  - `[20230413001.md 00:00:35.219]` 整期 "5 Ways Soy Products are DANGEROUS (REMOVE THEM!)" — 把 seed oil 单独拆 5 期
  - `[20230126001.md]` 41 次 seed oil（顶期）
- **R03 新框架**: R01/R02 主要是 carnivore 正面框架 + 反对 fiber/vegan；R03 演化为 **"三大杀手食材"负面清单**: seed oils (含 soybean/canola/safflower) + sugar + grains。anti-nutrient (oxalates, phytates, lectins) 是 R03 新加的学术化论证
- **真实属性**: 真信念 (整期 + 多文件 95 次命中)

### 8.2 **seed oil = 工业加工 + omega-6 炎症通路** (R03 学术化深入)
- **他/她说过的**:
  - `[20230413001.md 00:00:42.420–00:00:55.790]` "the process in order to make that they have to heat the oil heat the soybeans up in order to crack them this tends to promote rancidity and so to deal with that that awful rancid condition they tend to re-mix them with hexane and then heat them again to quote-unquote deodorize"
  - `[20230413001.md 00:01:17.820–00:01:19.850]` "currently consume more calories from soybean oil and other vegetable oils than we do from beef"
  - `[20230326001.md 00:00:55.199–00:01:17.690]` 描述工业 deodorization + 双加热导致氧化; "high level of omega-6 fatty acids in there some people and some studies suggest that high levels of omega-6 can be damaging to our health and somewhat inflammatory"
  - `[20230413001.md 00:02:11.640–00:02:15.770]` "soybean oil can potentially cause inflammation can damage the metabolism in the mitochondria and over time this damage leads to things like insulin resistance eventually diabetes and perhaps even cancer"
  - `[20230413001.md 00:03:13.560–00:03:20.509]` "eating a die-high and soybean oil which includes plenty of pro-inflammatory little like acid can contribute to at least an animal models neurologic conditions such as Parkinson's Alzheimer's disease even autism"
- **R03 新论据**: 从 R02 的"避免 seed oil"扩展为 R03 的 **机制图** = 工业 hexane 萃取 + deodorization → 氧化 → omega-6 蓄积 → 炎症 → 胰岛素抵抗 → 神经退化 (Parkinson/Alzheimer/autism)
- **真实属性**: 真信念 (R03 5+ 整期, 95+ 次命中)

### 8.3 **GLP-1 减肥药 (Ozempic / semaglutide) = 短期捷径+长期反弹, Baker 批判** (R03 新话题)
- **他/她说过的**:
  - `[20230104001.md 00:00:09.720]` 整期标题 "Miracle weight loss drug or ticking time bomb?" — 整期批判 GLP-1
  - `[20230104001.md 00:01:22.439–00:01:29.149]` "GLP-1 agonists and these are these new drugs out there some glue tied lyric lutide and some of these other ones with Govi and things like that that are being used as weight loss" — 引用 semaglutide, liraglutide, Govi (govy = Novo Nordisk 产品)
  - `[20230104001.md 00:01:14.580–00:01:21.119]` "you know he dove into the physiology on this... thermogenic uncoupling of the fat cells and you get fat cell hyperplasia" — 引用 Hyperlipid (Peter) 的 fat cell hyperplasia 反弹论
  - `[20230104001.md 00:02:56.400–00:03:13.490]` 引用 Hyperlipid "currently the risk of promoting breast cancer by gop1 agonists is taking sufficiently seriously to have promoted a systematic review of meta-analysis to bury said risk" — 暗示 Big Pharma 隐瞒乳腺癌信号
  - `[20230104001.md 00:05:09.720–00:05:11.990]` "when I got off the drug I became ravenously hungry I gained 50 pounds right away more than I was before" — 引用实例反弹
  - `[20230104001.md 00:07:10.620–00:07:16.610]` "not good to be the last guy but it's not good to be the first guy you know it's kind of like just kind of sit back and watch for a while" — Baker 外科 medical school 学到的"宁晚勿早"原则
  - `[20230104001.md 00:07:39.479–00:07:49.490]` 结尾自报 "World Carnival month day four is underway I'm starting out a couple ribeye steaks... I'm like I said I just feel wonderful doing this this way with just straight beef and beef beef and salt and water" — 用自身 carnivore 现身对比 GLP-1
- **R03 新出现** (R01/R02 没有): GLP-1 减肥药批判。重要新立场
- **真实属性**: 真信念 (整期 + 具体机制 + 自身对照)
- **新引用人物 (R03)**: **Peter / "Hyperlipid"** — Baker 引用其 GLP-1 反弹论 (R03 唯一一次, 单一来源未深入)
- **推断**: 0 验证, 仅 Baker 单方引用 Hyperlipid 观点, 不能独立确认 Hyperlipid 真实身份

### 8.4 **oxidative stress = 锈 (rust) = 全身炎症 + 心脏病起源** (R03 学术化隐喻)
- **他/她说过的**:
  - `[20230214001.md 00:01:00.480–00:01:02.029]` "credit Dr Malcolm Kendrick and then subsequently Dr Paul Mason both of which I've interviewed and I know Paul reasonably well"
  - `[20230214001.md 00:03:10.739–00:03:23.819]` "oxidation on the cellular level is when electrons are moving around and different atoms are gaining or losing electrons rust is a formal type of oxidation so you can kind of think of it like your body is rusting on the inside"
  - `[20230214001.md 00:03:23.819–00:03:38.149]` "stress in general... pollution cigarette smoking in particular we know high levels of glucose you know hyperglycemia or massive excursions in the blood glucose are very stressful and also very damaging"
  - `[20230214001.md 00:06:53.880–00:07:00.590]` "what it's looking like is if you have the environment the right environment the the pro-oxidative environment to damage the inflammation the hyperglycemia the high blood pressure in place then high allele levels of LDL cholesterol might in fact be more likely to be damaging but if you get rid of those other factors and perhaps higher LDL may not be as big of a concern"
- **R03 新立场**: LDL 不是独立凶手, 而是 **dependent variable** (依赖变量) - 必须有"pro-oxidative environment" (炎症环境) 才致命。R02 已有 LDL 怀疑论，R03 加入 "rust" 隐喻和 "dependent variable" 框架
- **真实属性**: 真信念 (单期深入 + 跨期 14 文件 145 次 cholesterol)
- **新引用人物 (R03)**: **Dr Malcolm Kendrick** (英国, The Great Cholesterol Con 作者 — Baker 引用), **Dr Paul Mason** (澳洲, low-carb 医生 — Baker 说自己认识他 "I know Paul reasonably well")
- **未发现**: 两人视频/出版物具体名字未在本期被引用（仅人物名）

### 8.5 **carnivore = 全肉饮食, 维持自身 (beef, salt, water) + World Carnivore Month 1 月活动** (R03 强化)
- **他/她说过的**:
  - `[20230104001.md 00:07:39.479–00:07:49.490]` "I'm like I said I just feel wonderful doing this this way with just straight beef and beef beef and salt and water and that's what works for me"
  - 5 文件 2023-01 集中提及 "World Carnivore Month"
  - `[20230126001.md]` 41 次 seed oil (整期)
  - `[20230101001.md]` 18 次 carnivore (R03 整期 carnivore 最高)
- **R03 延续**: R01/R02 已确立 "beef salt water" 极简肉食。R03 演化为 **每年 1 月"World Carnivore Month"** 社群活动, 是 meatrx.com 时代的延续
- **真实属性**: 真信念

### 8.6 **Linus Pauling / 维生素 C 大剂量 = 错误健康神话 (Baker 引用否定)** (R03 引用, 不是 Baker 自己的观点)
- **他/她说过的**:
  - `[20230224001.md 00:00:10.080–00:00:13.249]` "Linus Pauling and all this vitamin C is going to make us live forever and prevent us from getting cancer and colds" — Baker 描述一个被否定的旧神话 (Linus Pauling 1994 年去世, 维生素 C 大剂量主张者)
  - `[20230223001.md 00:00:38.700–00:00:43.430]` "looking at five nutrients when eaten in ample amounts may help prevent reverse symptoms of depression just stick around" — Baker 强调"吃足够量的 5 种关键营养素可以逆转抑郁"
  - `[20230223001.md 00:02:34.620–00:02:37.010]` "crucial role in decreasing the severity of and in some cases reversing" 抑郁
- **真实属性**: Baker 在反向引用 (批评 Pauling)，不是主张
- **R03 含义**: Baker 隐含立场 = "吃足够动物性食物" → 获取足量营养素 → 改善/逆转抑郁/情绪症状。**与"Paul Christian/Fred"派不同**：Baker 主张 **通过食物** 而非 **补充剂** 获取
- **我的推断**: 0 验证，仅基于 1 段引用

### 8.7 **anti-inflammatory diet = 肉/蛋/动物脂肪 (替代 NSAID / 药物)** (R03 主流药方)
- **他/她说过的**:
  - `[20230407001.md 00:06:27.300–00:06:48.170]` "meat awful and eggs and during the next 15 months the patient reversed all of his symptoms in a sustaining complete... anti-inflammatory and can contribute to healing and possibly even reversing" — Baker 引用病例: 肉+蛋治愈 15 月持续症状
  - `[20230303001.md 00:04:13.879–00:04:17.670]` "nutrients like meat Seafood eggs we often will see a reversal of those symptoms" — 肉+海鲜+蛋 = 抗炎
  - `[20230414001.md]` (在 R03 范围内, 整期 carnivore 提及)
- **R03 延续**: R02 已有 anti-inflammatory claim, R03 系统化为"动物性食物是天然 anti-inflammatory" 替代药物
- **真实属性**: 真信念

### 8.8 **fiber 神话 / 谷物 = 抗营养素 (oxalates/phytates/lectins) 持续反对** (R03 延续)
- **他/她说过的**:
  - `[20230326001.md 00:03:22.739–00:03:29.930]` "whether they're whole grain or not they all have anti-nutrients in them oxalates phytates lectins which can potentially compete with absorption of nutrients and leech out some of the nutrients from the body they can cause gut irritation and inflammation which can lead to the so-called leaky gut"
  - `[20230413001.md 00:00:18.720–00:00:30.170]` "the consumption of soybean oil has grown 1000 fold" — 工业化扩展隐喻
- **R03 延续**: R01/R02 已有"fiber 神话"反对, R03 加入"anti-nutrient" (oxalates/phytates/lectins) 学术化术语。R03 fiber 14 文件 120 次 (R02 7 文件)
- **真实属性**: 真信念 (翻倍)

### 8.9 **GLP-1 + Big Pharma 怀疑 = R01/R02 已有"clinical fraud" 主题延伸** (R03 强化)
- **他/她说过的**:
  - `[20230104001.md 00:02:40.200–00:02:47.089]` "I've seen many many many drug companies find many many billions of dollars for basically lying for committing fraud"
  - `[20230104001.md 00:06:42.900–00:06:46.490]` "particularly these days there's a lot of corruption that's going on I mean we see that the FDA we see it in places like the CDC we see it where you know these companies are paying basically to get drug approval"
  - `[20230104001.md 00:07:01.500–00:07:16.610]` 警告"drugs withdrawn from the market not not far afterwards"
- **R03 延续**: R01/R02 已有"anti-meat agenda killed my mom"道德框架。R03 演化为 **"Big Pharma + FDA + CDC 三角腐败"** 框架, 把药物怀疑论 (Ozempic) 整合进既有反建制立场
- **真实属性**: 真信念

### 8.10 **心血管疾病 = 损伤 + 修复失败模型 (Baker 接受 Kendrick / Mason 框架)** (R03 立场)
- **他/她说过的**:
  - `[20230214001.md 00:01:57.299–00:02:23.210]` "typically has to be a inciting event damage to the artery itself and so some sort of damage occurs and then there is an attempt to repair that cholesterol isn't involved in the repair process as are the red blood cells the immune system the white cells all come in there to try to fix things initially"
  - `[20230214001.md 00:06:41.460–00:06:47.749]` "what we're seeing with with regard to LDL cholesterol is it's becoming looking more and more like it is a dependent variable"
- **真实属性**: 真信念 (整期深入论证)
- **我的推断**: Baker 明确 "credit" 两位替代医学医生 (Kendrick + Mason), 这是 R03 重要立场表态, 表示他已把"LDL 怀疑论" 升级到理论支持 (vs R02 的"模糊怀疑")

---

## 9. R03 关键盟友/对手演变

### 盟友 (R03 延续 R01/R02 + 新增)
- **Joe Rogan** (R03 衰减: 1 次, vs R02 10+): 联盟关系减弱
- **Paul Saladino** (R03 0 命中, vs R02 多次): **R03 完全消失**! 这是 R03 显著变化
- **Dr Malcolm Kendrick** (R03 **新引用**, 英国医生, "The Great Cholesterol Con" 作者)
- **Dr Paul Mason** (R03 **新引用**, Baker 自报 "I know Paul reasonably well")
- **Peter / "Hyperlipid"** (R03 **新引用**, Baker 引用其 GLP-1 反弹论)
- **Linus Pauling** (R03 作为 **被批评对象** 出现, 非盟友)
- **MeatRx 团队** (R03 **消失**, 0 命中)

### 对手 (R03 延续 + 新增)
- **Layne Norton** (R03 0 命中, vs R02 2 次): **R03 完全消失**! 与 Saladino 同步退出 Baker 语料
- **Big Pharma / FDA / CDC** (R03 强化, 整合进既有反建制立场)
- **GLP-1 药物厂商** (R03 新对手, 含 Novo Nordisk, Eli Lilly)
- **大豆 / 工业化 seed oil 产业** (R03 新对手, 1000 倍扩张数据)
- **vegan 整体** (R03 16 文件, vs R02 30+ 减半, 仍是对立面)

### 中立/被引述
- **KY Furneaux** (R03 0 命中, vs R02 多次) - 案例人物消失
- **Kyrie Irving / Cam Newton** (R03 0 命中) - 案例人物消失
- **Weston A. Price** (5 文件命中) - **R03 隐性出现**, 但未点名 (仅"Price"出现在上下文)

---

## 10. R03 立场演化追踪 (vs R01/R02)

| 维度 | R01 (2018-01 → 2020-01) | R02 (2020-01 → 2022-11) | R03 (2022-11 → 2023-04) |
|---|---|---|---|
| carnivore 命名权 | 未明确 | **2022-06 主张** "I was the guy that came up with" | **R03 未重申命名权**, 重点已转 |
| animal-based 一词 | 未出现 | R02 后段 2022 出现 5 文件 | **R03 7 文件, 持续增长** |
| revero 概念 | 未出现 | 未出现 (0 命中) | **仍未出现 (0 命中)** ← R03 重点查证 |
| MeatRx 品牌词 | 已存在 | R02 9 命中 | **R03 0 命中, 退出主旋律** |
| regenerative 农业 | 已有 grass-fed | R02 强化 (9 命中) | **R03 0 命中, 完全退出** |
| regenerative 三剑客 (Zynga/Harris/Salatin) | 偶提 | R02 强盟友 | **R03 0 命中, 联盟消失** |
| seed oil 反对 | 偶提 | R02 8 命中 | **R03 18 文件 95 命中, 核心主题** |
| fiber 反对 | 已确立 | R02 后期 2022 集中 | R03 14 文件, 持续反对 |
| Paul Saladino 盟友 | R01 核心 | R02 延续 | **R03 0 命中, 联盟消失** |
| Layne Norton 对手 | 未出现 | R02 2 次冲突 | **R03 0 命中, 冲突消失** |
| Joe Rogan 盟友 | 核心 | R02 10+ 命中 | R03 1 命中, 弱化 |
| anti-Big Pharma 立场 | 已有 | R02 延续 | **R03 强化**, 整合 GLP-1/Ozempic 批判 |
| 道德框架 ("指南杀人") | 未明确 | R02 强化 "killed my mom" | R03 弱化, 让位炎症/科学论据 |
| LDL 胆固醇模型 | 模糊怀疑 | R02 强化怀疑 | **R03 升级**: "dependent variable" + "rust" 隐喻 + 引 Kendrick/Mason |
| World Carnivore Month 活动 | 无 | 无 | **R03 5 文件, 2023-01 新活动** |
| "beef, salt, water" 极简 | R01 已有 | R02 延续 | **R03 结尾反复出现**, 自我品牌 |
| GLP-1/Ozempic 立场 | 不存在 | 不存在 | **R03 新主题**: 整期批判, 引 Hyperlipid 反弹论 |
| 公司化产品 (revero, app) | MeatRx 存在 | MeatRx 9 命中 | R03 0 公司化新词, 仅有 podcast 暗示 |

---

## 11. R03 调研方法 + 限制

- 关键词 grep 命中数已记录 (Section 7)
- 重点文件 Read 数量: 4 (20230104, 20230214, 20230326, 20230413), 配合 top 命中文件清单
- 限制 1: 100 个文件中只 Read 4 个整文件头部, 其他 96 个仅靠 grep 命中位置。top 命中 file (20230126 seed oil 41 次, 20230206 sugar 58 次, 20230223 nutrient 24 次) 未深入 Read
- 限制 2: `revero` 一词 grep 0 命中, 可高置信度报告 R03 未出现 (覆盖大小写 + 拼写错误 + Revero 变体)
- 限制 3: `MeatRx` 在 R03 完全消失是真实信号 (0 命中) vs 写作风格转向。Baker 可能改用 podcast/社交媒体
- 限制 4: 部分高频 file (20230126, 20230206) 未整期 Read, 内容可能遗漏
- 限制 5: "Hyperlipid" / Peter 身份未独立确认, 0 验证
- 限制 6: 0 验证 Baker 与 Paul Mason "I know Paul reasonably well" 的私人关系

---

## 12. R03 关键开放问题 (R04+ 必查)

- **revero 何时首次出现**: R01/R02/R03 三轮 0 命中 → 必须 R04+ 验证。如果到 R10 仍 0 命中, 则 revero 可能不是 Baker 真实产物 (而是他人/项目误传)
- **MeatRx 是否仍存在**: 0 命中 vs 网站可能仍在线 - 需 WebSearch 验证
- **GLP-1 立场是否升级**: R03 整期 → R04 后续是否扩到 tirzepatide / retatrutide / 整体 peptide 批判
- **Paul Saladino 联盟消失原因**: R02 强盟友 → R03 0 命中, 可能是 (a) 关系破裂 (b) Baker 注意力转向 GLP-1 (c) 语料采样偏差
- **Layne Norton 冲突消失原因**: R02 2 次冲突 → R03 0 命中, 同样可能 (a) 和解 (b) 注意力转移 (c) 语料偏差
- **regenerative 农业完全退出**: R02 9 命中 → R03 0 命中, **R03 显著变化** - 需 R04 验证是否回归
- **World Carnivore Month 1 月活动**: 2023-01 5 文件, R04 (2023-04-2023-07) 可能进入 2024-01 复现期
- **Kendrick + Mason 框架是否持续引用**: R03 整期深入 → R04 追踪是否成为 Baker 长期盟友

---

## 轮 4/17 (2023-04-29 → 2023-07-31)

样本: 100 个文件, 已确认范围 `ls | sort | sed -n '301,400p'`。

### 1. R04 grep 命令 + 命中数

```
carnivore: 51 | meat: 47 | beef: 18 | animal.based: 8
cholesterol: 14 | LDL: 7 | lipid: 6 | statin: 6
insulin: 19 | metabolic: 16 | diabetes: 19 | obesity: 17
plant: 30 | vegan: 19 | vegetarian: 4 | fiber: 8 | seed oil: 0 (vegetable oil 0)
ketogenic: 16 | longevity: 3 | fasting: 3 | supplement: 8
protein: 34 | muscle: 25 | performance: 9 | athlete: 8
GLP-1: 0 | Ozempic: 1 | Wegovy/Semaglutide: 见 20230721
Liver King: 0 | Saladino: 0 | Layne/Norton: 0 | MeatRx: 0
Ludwig: 0 | Lennerz: 0 | Harvard: 0 | Bikman: 0 | Lustig: 0
Kendrick: 0 | Hyperlipid: 1 (20230715) | Mason: 1 (20230630)
Joe Rogan: 4 | Peter (Jordan Peterson): 4
regenerative: 3 (20230429, 20230604, 20230608) | World Carnivore Month: 0
anti-nutrient: 1 (20230716) | oxalate: 7 | lectin: 4 | phytate: 2
Revero/Rivera/Rivero 任一变体: 5 文件命中 ← R04 首次出现
Mercola: 1 (20230701) | Bear Grylls: 1 (20230525) | RawVana: 1 (20230611)
Alyse Parker: 1 (20230702) | Miley (Cyrus): 1 (20230723) | Joel Khan: 2 (20230512, 20230618)
```

### 2. R04 重大新出现 / 持续主题

**🔥 重大新出现 1: Revero 公司正式诞生**

R01/R02/R03 三轮 0 命中, R04 突破:
- [20230513001.md 05:03:00] "I'm very excited to announce that we are opening Rivero to patients very soon" — **首次公开宣布 Revero 即将开放患者** (在 Mr. Beast 视频中顺带宣布)
- [20230620001.md 00:00:02-00:00:08] "I was in San Francisco… to help get ready to launch our company Rivera as you guys know Rivero his mission is to **reverse chronic disease using nutrition lifestyle**… **treating the root cause, not playing the symptom management game**" — **完整使命陈述**, 旧金山办公
- [20230720001.md 02:44:09] 给出域名 "**carnivore [.diet?] and subsequently rivero.com will all be great places to get support**" — Revero 与 carnivore.diet 并列推荐入口
- [20230728001.md 05:13:00] "**as Rivera stands up we'll have health care physicians**" — Revero 配套医生网络
- [20230731001.md 02:01:00] "I'm here to help you, go to carnivore.[diet], go to rivero.com whatever and turn this thing around" — 月末再次推荐

含义: R03 调研问题 "revero 何时首次出现 / MeatRx 是否退场" 在 R04 找到答案: **2023-05 宣布 + 2023-06 启动 Revero, 这是 MeatRx 之后 Baker 的新公司化产品**。Revero 定位明显升级: 不只是 "教练匹配" (MeatRx 模式), 而是 "treat-and-reverse chronic disease + 配备医生网络" — 接近正式 telehealth/clinic 模式。

**🔥 重大新出现 2: GLP-1 / Ozempic 批判正式上桌**

R02 0 命中, R03 仅在概念层 (整期讨论但未直接产品名), R04 首次有完整 Ozempic 视频:
- [20230721001.md 整期] "The Truth Behind Weight Loss Shortcuts! (Wegovy & Ozempic)" — Baker 第一个直接以药物名命名的 Ozempic 解构视频
- 引述同名格 (semaglutide) 在 2017 FDA 批准糖尿病 → 2021 off-label 减肥 → A1C 平均仅降至 7 仍在糖尿病范围 → FDA 正在调查自杀风险 → 甲状腺癌警示
- 引 2022 "drug design development and therapy" + 2021 "reviews in endocrine/metabolic disorders" + "diabetes obesity and metabolism" 期刊
- 引述 YouTuber Remi Bader 案例 (停药后暴饮暴食恶化) + 匿名 colitis 患者案例
- 结论: "**that buys a lot of Ribeyes for that price**" — 把药费转换成 ribeye 数量, 经典 Baker 修辞

**🔥 重大新出现 3: anti-nutrient 框架学术化升级**

R01-R03 已有反植物言论, 但 R04 [20230716001.md 03:26:22] 在 Jordan Peterson carnivore 视频中给出明确学术引用:
- "plants have **chemical defense systems known as in some cases anti-nutrients**, **2019 article in Open Biotechnology Journal** discusses these anti-nutrients and their effects, these toxins include **lectins, amylase or trypsin inhibitors, oxalates and many more**"
- 这是 Baker 首次在 R 调研中给 anti-nutrient 概念配上**期刊文献引用**, 而非仅口头宣称

**🔥 重大新出现 4: Liver King 和 Saladino 完全消失, 但有新替代联盟**

- R02 强盟友 Liver King + Paul Saladino → R04 仍 0 命中, **R03 趋势确认**
- 新替代盟友: **Dr. Paul Mason** (R04 1 命中, 但在 R03 已有, 表现稳定) + **Dr. David Unwin** [20230530001.md PHCUK 会议] 首次以 "gracious host" 出现 + Hyperlipid (R04 1 命中, R03 已有)
- Baker 明确从 "carnivore 商业化合伙人" (Liver King/Saladino 时代) 转向 "学术/医生联盟" (Mason/Unwin/Hyperlipid)

**🟢 持续主题 1: 反 vegan/反植物的标题攻击模式**

R04 100 文件中至少 12 个标题直接攻击 vegan/plant-based, 例: "Vegan Cardiologist's Misinformation", "Vegan Doctor ATTACKS Carnivore Diet", "Vegan Doctor Thinks Dairy Causes Cancer?", "Why Vegan Athletes NEVER WIN", "Are Vegan Farts Causing Global Warming?", "Vegan Countries Are FALLING BEHIND!", "Vegan Says Meat Eaters Will Go To Hell?!", "Vegan Influencer QUITS Plant-Based Lifestyle (RawVana)", "Vegan Influencer Turns To MEAT (Alyse Parker)", "Vegan Doctor ADMITS He Needs Meat Nutrients", "Vegan Gains or Vegan Pains?", "Bear Grylls SURVIVES Veganism, Goes Carnivore". 这是 R03 已有 + R04 强化的 "反向叛逃叙事" 内容模式 (vegan 名人转 carnivore 是高频题材)。

**🟢 持续主题 2: LDL 胆固醇修正主义**

R04 14 个文件涉及胆固醇, 4 个标题直接相关: "Are Statins DESTROYING Your Health??", "New Study: The 'SECRET' Of Cholesterol", "LDL vs Remnant Cholesterol: Who Is The Killer?", "New Study: Are Statins contributing to DEMENTIA?!", "Groundbreaking Study Reveals CRAZY Facts about LDL Cholesterol!", "Insane Dr. 'Lower Your Cholesterol to Newborn Levels'". [20230715003.md 整期] 给出 statin → dementia 论证链, 引用 "American Journal of Geriatric Pharmacology", "translational neurodegeneration", "Journal of Pharmacovigilance" (亲脂性 statin atorvastatin/simvastatin 风险更高), "Journal of Neurology" (70+ 老人高胆固醇关联较少痴呆), "JAMA Neurology" (26 年窗口, 痴呆诊断前 15 年胆固醇已下降). [20230609001.md] 强调 LDL 颗粒大小 (small dense vs large fluffy) 区别。

**🟢 持续主题 3: 与 Jordan Peterson / Michaela 联盟反复利用**

- [20230716001.md 整期] "Jordan Peterson's Carnivore Transformation (HE'S THRIVING!)"
- Peterson 主动归功 Baker: "**found out from his daughter Michaela who found out in part due to me**" — 引用 Peterson 父女的原话承认 Baker 是 carnivore 的早期信息源
- Baker 重复使用 Peterson 故事作为 "depression + arthritis carnivore 治愈" 的标志案例 (R02 已用, R04 升级为长视频)

**🟢 持续主题 4: 整骨外科医生 + Texas 牛肉文化身份品牌**

- [20230429002.md] "Shawn Baker @ KetoCon 2023" — KetoCon Austin 现场, 与 Holy Cow Beef (Lubbock TX), Noble Origins (organ shake), Carnivore Bar (Phil Misi, 退役军人, MRE 故事), Joel Salatin 等 regenerative ranching 圈子合影
- [20230601001.md] "Here's What You Order At Wendy's on a Carnivore Diet" + [20230608001.md] "What To Order at McDonald's on a CARNIVORE DIET" — 把 carnivore 平民化到快餐
- 同期标题强化身体认同 ("Not bad for 56 years!! Carnivore power!!", "Doctor takes on 3.5lbs of meat in under 10 minutes", "Carnivore leg day fun at age 56!!")

### 3. R04 引用/术语清单 (新出现 vs 复用)

| 项目 | 新/复用 | 出处 |
|---|---|---|
| Revero (公司) | **R04 新** | 20230513, 20230620, 20230720, 20230728, 20230731 |
| rivero.com (域名) | **R04 新** | 20230720, 20230731 |
| reverse chronic disease (使命语) | **R04 新** | 20230620 |
| treat the root cause | **R04 新** | 20230620 |
| Ozempic / semaglutide / Wegovy / Rybelsus | **R04 新** | 20230721 |
| FDA 自杀风险调查 | **R04 新** | 20230721 |
| Mayo Clinic 药物相互作用警告 | **R04 新** | 20230721 |
| YouTuber Remi Bader 停药复胖案例 | **R04 新** | 20230721 |
| anti-nutrient + 期刊引用 (Open Biotechnology 2019) | **R04 新** | 20230716 |
| lectin / oxalate / amylase / trypsin inhibitor 清单 | R02 已有, R04 学术化 | 20230716 |
| atorvastatin / simvastatin (亲脂性 statin) | **R04 新** | 20230715003 |
| American Journal of Geriatric Pharmacology | **R04 新** | 20230715003 |
| JAMA Neurology 26 年胆固醇下降-痴呆研究 | **R04 新** | 20230715003 |
| LDL 颗粒大小 (small dense vs large fluffy) | R03 已暗示, R04 明确 | 20230609 |
| triglyceride to HDL ratio (1.2 为安全范围) | **R04 新** | 20230512 |
| Dr. Paul Mason (盟友) | R03 已有, R04 持续 | 20230630 |
| Dr. David Unwin (新盟友) | **R04 新** | 20230530 (PHCUK 会议) |
| PHCUK / Yorkshire / Sheffield (英国大会) | **R04 新** | 20230530 |
| Holy Cow Beef Lubbock TX | **R04 新** | 20230429002 |
| Noble Origins (organ shake) | **R04 新** | 20230429002 |
| Carnivore Bar (Phil Misi 退役军人创办) | **R04 新** | 20230429002 |
| Bernard Moncriff 1856 "philosophy of the stomach" | **R04 新** | 20230711 |
| Dr. James Salisbury (1880s, Salisbury steak 同源) | **R04 新** | 20230711 |
| Mr. Beast (Crohn's, 公开建议) | **R04 新** | 20230513 |
| Bear Grylls 离 vegan 转 carnivore | **R04 新** | 20230525 |
| Miley Cyrus 由 vegan 转食肉 | **R04 新** | 20230723 |
| Alyse Parker (前 raw vegan influencer) | **R04 新** | 20230702 |
| RawVana (前 vegan influencer) | **R04 新** | 20230611 |
| Dr. Joseph Mercola (整骨医生, 弃 keto, Baker 反驳) | **R04 新** | 20230701 |
| Dr. Joel Khan (vegan cardiologist, Baker 长期对手) | R02/R03 0 命中, **R04 重启** | 20230512, 20230618 |
| Liver King | R03 0 命中, **R04 仍 0 命中** | — |
| MeatRx | R03 0 命中, **R04 仍 0 命中** | — |
| Paul Saladino | R03 0 命中, **R04 仍 0 命中** | — |
| Layne Norton | R03 0 命中, **R04 仍 0 命中** | — |

### 4. R04 立场演化追踪 (vs R01/R02/R03)

| 维度 | R01 | R02 | R03 | R04 (2023-04 → 2023-07) |
|---|---|---|---|---|
| 公司化产品 | MeatRx 已存在 | MeatRx 9 命中 | MeatRx 0 命中 | **Revero 首次出现 5 文件 + rivero.com 域名 + treat-chronic-disease 使命语** |
| MeatRx 品牌词 | 已存在 | 9 命中 | 0 命中 | **仍 0 命中, R03 结论确认 - 已被 Revero 替代** |
| GLP-1/Ozempic | 不存在 | 不存在 | 概念批判 | **首个完整产品视频 (20230721), Wegovy + Rybelsus + semaglutide 全名出场** |
| anti-nutrient 概念 | 偶提 | 已有 | 已有 | **首次加上 2019 Open Biotechnology Journal 引用, 学术化升级** |
| LDL 胆固醇模型 | 模糊怀疑 | 强化怀疑 | 升级 (dependent variable + rust 隐喻) | **R04 引大量 statin → 痴呆期刊证据链, 增加 LDL 颗粒大小论, triglyceride/HDL 比例** |
| Liver King 后续 | 未存在 | 已存在 | 0 命中 | **仍 0 命中 - 联盟终结确认** |
| Paul Saladino | R01 核心 | R02 延续 | 0 命中 | **仍 0 命中 - 关系断裂确认** |
| Layne Norton 对手 | 未出现 | 2 次冲突 | 0 命中 | **仍 0 命中, 注意力转向 vegan doctor 群体 (Khan/Mercola/RawVana 等)** |
| Joe Rogan 盟友 | 核心 | 10+ 命中 | 1 命中 | **4 命中, 复兴** ("Joe Rogan Goes Carnivore AGAIN") |
| Jordan/Michaela Peterson | 已有 | 延续 | 弱化 | **R04 强化: 长视频 "HE'S THRIVING", Peterson 父女归功 Baker** |
| regenerative 农业 | 已有 | 9 命中 | 0 命中 | **3 命中部分回归** (KetoCon Holy Cow Beef + Joel Salatin), 但不再是主旋律 |
| World Carnivore Month | 无 | 无 | 5 文件 (2023-01) | **0 命中** - 非 1 月不开展 |
| 反 vegan 标题攻击 | 偶有 | 已成模式 | 持续 | **R04 12+ 标题, "vegan-converts-to-meat" 故事池扩充 (Bear Grylls/Miley/Alyse Parker/RawVana)** |
| 学术联盟 | Saladino/Liver King | 同 | Kendrick/Mason | **加上 Paul Mason + David Unwin + PHCUK 大会 + 引 Hyperlipid 持续** |
| "beef, salt, water" 极简 | 已有 | 延续 | 反复出现 | **R04 仍可见, 但相对让位于 Revero/Ozempic 主题** |
| Texas 牛肉文化身份 | 偶提 | 强化 | 持续 | **R04 KetoCon Austin + Wendy's/McDonald's carnivore 平民化** |
| 历史合法化引用 | 偶有 | 已有 | 已有 | **R04 新: Bernard Moncriff 1856 + James Salisbury 1880s 双引** |

### 5. R04 调研方法 + 限制

- 关键词 grep 全 100 文件命中数完整 (Section 1)
- 整文件 Read: 5 个 (20230721 Ozempic, 20230716 Peterson, 20230715003 statin, 20230711 HuffPost, 20230429002 KetoCon, 20230620 Revero, 20230530 PHCUK, 20230701 Mercola); 部分 Read: 4 (20230513, 20230716 后段)
- 限制 1: Revero 在转录中常被 yt-dlp 误录为 "Rivera/Rivero" (语音识别错误), 我已用 `[Rr]ivera|[Rr]ivero|[Rr]evero|[Rr]evera` 宽匹配, 5 文件命中可信
- 限制 2: Ozempic 仅 1 命中 (20230721), 但同 1 个视频是 Baker 首个产品级 GLP-1 批判, 标志意义大于命中数
- 限制 3: 100 文件中至少 30+ 个是非内容性 shorts ("Big ol' butt!!", "Don't skip leg day", "Workout of the day!!" 等), 真正主题视频约 50-60 个
- 限制 4: 0 验证 Revero 的实际公司结构 / 股权 / 团队组成 - 仅来自 Baker 自述
- 限制 5: 未深入 [20230615002 (animal-based)], [20230625001 (Joe Rogan 2017 回忆)], [20230624002 (vegan farts)], [20230618001 (Khan 二次反击)] - 应在 R05+ 监督是否延续

### 6. R04 关键开放问题 (R05+ 必查)

- **Revero 业务模型扩展**: R04 是宣布 + 启动期, R05+ 是否进入 (a) 提价 (b) 扩展疾病种类 (c) 公开患者案例 (d) 招募更多医生 阶段
- **Ozempic 批判是否扩 tirzepatide / Mounjaro / retatrutide**: R04 仅 Ozempic, R05+ 是否扩展到整 GLP-1/GIP 类
- **MeatRx 是否被 Baker 正式弃用**: R03/R04 两轮 0 命中, R05 是否出现 "我把 MeatRx 关了" 或 "MeatRx 合并入 Revero" 解释
- **Paul Saladino 关系**: 3 轮 0 命中, 是否在 R05+ 重新出现 (尤其 Saladino 在 2023 公开质疑 carnivore 转向 honey/fruit 后)
- **PHCUK / David Unwin 联盟**: R04 首次, R05+ 是否成为长期盟友
- **vegan-to-carnivore 名人故事池**: R04 已新增 Bear Grylls/Miley/Alyse Parker/RawVana, R05+ 是否继续添加
- **8 月 World Carnivore Month 替代活动**: 1 月之外, R05 (2023-08-09) 是否有 8 月活动
- **Jordan Peterson 联盟深化**: R04 强化, R05+ 是否出现 Peterson 反向访谈 Baker / 上 Baker podcast

---

## 轮 5/17 (2023-08-01 → 2023-09-17)

**素材范围**: `${HOME}/Documents/女娲造人/@ShawnBakerMD/20230801001.md` ~ `20230917001.md` (100 个 .md 文件)
**调研方式**: 关键词 grep + 重点文件 Read (10 个)
**R05 调性**: **R04 主题全面淡化, Revero/Ozempic 完全消失, 转向"机制化 anti-plant" 论战 (seed oil / fiber / glyphosate) + 平台生存战 + 个人故事 (war/personal)**

### R05 调研命令一览 (grep + 命中数, 范围 401-500)

| 关键词 | 命中文件数 | 最高单文件命中 | 备注 |
|---|---|---|---|
| `revero\|rivera\|rivero` | **0** | 0 | **R05 零提及** - Revero 主题突然消失 |
| `ozempic\|GLP-1\|smaglutide\|semaglutide` | **1** | 1 (20230801001) | 唯一 1 个, 延续 R04 立场 |
| `seed oil` | **3** | ~5 (20230812002, 20230815002, 20230823002) | R05 新主力 |
| `fiber` | 多个 | 18+ (20230810001) | 学术化论证 |
| `cancer` | 多个 | 4+ (20230801001) | autoimmune + cancer 泛谈 |
| `carnivore` | 多个 | 多 (20230812002, 20230810001, 20230801001) | 仍是核心词 |
| `vegan` | 多个 | 多 (20230823002, 20230801002, 20230810001) | Chloe Bailey 等名人战 |
| `chaffee\|Anthony chafee` | 1 (20230826002) | 提及 | **R05 新出现: 借 Chaffee 关系引用 Maggie 82岁牧场主** |
| `peterson` | 2 (20230826002, 20230915001) | 各 1 | 持续引用 |
| `liver king` | 1 (20230813001) | 1 | **新调侃对象 (Brian Johnson 撞名)** |
| `Paul Mason\|Mason` | 1 (20230810001) | 1 | 引用 Paul Mason 关于 fiber 的研究 |
| `Kendrick\|hyperlipid` | 0 | 0 | **R05 完全不引 Kendrick** |
| `nadir ali\|Diamond` | 0 | 0 | **R05 完全不引** |
| `attia\|cywes\|norwitz` | 0 | 0 | **R05 完全不引** |
| `longevity\|aging` | 多 | 4+ (20230813001 Brian Johnson 抗衰) | R05 主要在批判 Brian Johnson 时谈 |
| `alzheim` | 1 (20230915001) | 多 | 借 glyphosate 谈 Alzheimer |
| `mTOR` | 1 (20230813001) | 1 | 提到 mTOR 抗衰 |
| `corporation\|company\|company` | 多 | 1-2 | 反复强调"the company" (Revero 后续) |
| `corps\|military\|war` | 1 (20230917001) | 30+ | **R05 新出现: Baker 15min 长篇讲 2007 Bagram 战地医院** |
| `Berg` | 1 (20230916001) | 1 | 借 Berg 谈 YouTube 平台审查 |
| `Dolce\|Mike Dolce` | 1 (20230811002) | 4 | **R05 新: 借 Mike Dolce "fad diet" 攻击反推 carnivore 增长** |
| `fad` | 1 (20230811002) | 4 | R05 新讨论 fad diet 概念 |
| `facultative carnivore` | 1 (20230811002) | 1 | R05 新术语 |
| `cortisol` | 1 (20230805002) | 4 | R05 新反 cortisol 恐慌 |
| `mitochondri` | 1 (20230915001) | 2 | glyphosate 通过线粒体机制讨论 |

**关键发现 (R05 阶段特征)**:
- `revero` 0 命中, 显著异常 (R04 出现 5+ 次) → 我推断: Baker 在 R05 阶段暂停 Revero 推广, 转向更普世反 plant toxin 主题
- `Kendrick/Diamond/Attia/Norwitz/Cywes/Nadir Ali/Chaffee(主)` 0 命中 → 学术盟友网络未扩张, 只短暂引用 Chaffee 一次
- `Paul Mason` 1 命中 → 延续 R04 学术联盟
- `Mike Dolce` 1 命中 → R05 新对手类型 (主持人型而非医生型)
- `Berg` 1 命中 → R05 新: Baker 把 Berg 拉入"反审查"阵营 (非 carnivore 论战)
- 20230813 Brian Johnson 视频 → **R05 新主题: 抗衰批判 (mTOR/rapamycin/GLP-1 平行)**
- 20230826 Maggie 82岁牧场主视频 → **R05 新主题: 引用 Chaffee 女友的家人作为长期 carnivore 案例**
- 20230915 Glyphosate 视频 → **R05 新主题: anti-nutrient 学术化 (colitis/dysbiosis/Alzheimer 关联)**
- 20230916 YouTube 审查视频 → **R05 新主题: 平台生存 + 援引 Berg 警告 + 反 pharma 阴谋**
- 20230917 Bagram 战地医院视频 → **R05 新主题: Baker 个人创伤叙事 (15min 长篇, 全新)**
- 20230811 Mike Dolce 视频 → **R05 新术语: "facultative carnivore"** (Baker 提出人类分类)
- 20230805 cortisol 视频 → **R05 新立场: 反 cortisol 恐慌 (pro-exercise 论战)**

### R05 核心论点 (5-10 个发现, 每条标注延续 vs 新增)

#### 5.1 **Revero 主题完全消失 (vs R04 显著变化)**
- **他/她说过的**: 0 命中 (R04 有 5 个文件提及 Revero/Rivera/Rivero)
- **真实属性**: 否定发现 (R05 没有 Revero 任何内容)
- **R05 演化**: **R04 主题未延续, 我推断 Baker 暂停 Revero 推广, 因 (a) 推广失败 (b) 监管问题 (c) 业务调整**
- **我推断**: Revero 在 R05 完全隐入背景 (只在少数视频用"the company"指代), Baker 转向更易传播的反 plant toxin 普世内容
- **R05 仍用"the company"**: 20230916001 提到 "I will continue to fight ... through this Channel Through social media through the company to make sure that you and I and our children can live in a way that they can have health" → 公司实体仍存在但作为隐含后盾

#### 5.2 **Anti-nutrient 学术化机制突破: Glyphosate 通过线粒体损伤攻击神经 (R05 重要新发现)**
- **他/她说过的**:
  - `[20230915001.md 00:00:34–00:01:50]` "glyphosate impaired the synapses between neurons and cause cognitive deficits in Lab Rats" (引 Archives of Toxicology 2021)
  - `[20230915001.md 00:01:50–00:02:20]` "glyphosate cause abnormal cell development neural growth and myelination it's toxic to neurotransmission causes oxidative stress as well as neural inflammation and mitochondrial dysfunction" (引 International Journal of Molecular Science)
  - `[20230915001.md 00:03:40–00:04:30]` "Roundup is supposed to be only toxic to plants affecting an energy pathway known as a shikamadi pathway... this pathway also exists in bacteria and mitochondria have bacterial type DNA and in fact mitochondria are vulnerable to glyphosate"
  - `[20230915001.md 00:04:30–00:05:00]` "research study looked at the rate that glyphosate was used and the rate of death from Alzheimer's disease in this graph the red line represents the rate of glyphosate used in the United States and the L bars are the rates of death from Alzheimer's" (引 1974 后 autism/Alzheimer 起飞相关)
  - `[20230915001.md 00:04:50–00:05:00]` "lucky for us carnivores ruminant animals such as cattle and sheep have a microbiome in their four-chambered stomach and it denatures glyphosate so it isn't absorbed much" - **关键论断: meat/milk 几乎零 glyphosate** (因反刍动物 4 胃微生物降解)
- **真实属性**: 学术化论证, 多个 PubMed 引用
- **R05 新出现** (vs R04: 0 glyphosate)
- **R05 演化**: 把"seed oil 是坏的"扩展到"除草剂 (也是 plant-based diet 的隐藏成本) 也是坏的" → 双线 anti-plant 攻击
- **机制亮点**: shikimate pathway 在植物/细菌/线粒体共享 → 人类线粒体易感 → 这是 anti-nutrient 学术化的关键机制 (Baker 之前从未用过这个机制)
- **R05 战术**: 借 IARC vs EPA 数据透明性之争 (99% 行业 vs 70% 独立 → 几乎所有 positive 研究都是行业付钱) + 1974 autism 起飞 → 强烈暗示但不说因果

#### 5.3 **Seed oil 三大新机制 (R05 学术化升级)**
- **他/她说过的**:
  - `[20230815002.md 00:00:30–00:00:50]` "humans have evolved to eat about the same amount of omega-6 as to omega-3 uh fatty acids... today's diet the ratio of omega-6 Omega-3s now something like 16 to 1" - **关键数字: 现代 16:1, 演化 1:1**
  - `[20230815002.md 00:01:10–00:01:30]` "animal studies certainly have shown that soybean oil and the little antic acid it contains promotes colitis"
  - `[20230815002.md 00:01:30–00:01:50]` "researchers are also finding out that vegetable oil can lead to quote unquote on unhealthy gut microbiome or unhealthy gut bacteria"
  - `[20230815002.md 00:01:50–00:02:20]` "other researchers have found that omega-6 fats can promote gut microbiome dysbiosis or gut bacteria imbalance and colonic inflammation... soybean oils promote obesity and diabetes more so than things like coconut oil or even fructose and it can promote other inflammatory diseases like rheumatoid arthritis cardiovascular disease non-alcoholic fatty liver disease even potentially Alzheimer's disease"
  - `[20230812002.md 00:03:15–00:03:30]` "research in the Journal of carcinogenesis evaluated whether omega-3 or omega-6 oils in the diet would prevent or promote skin disease or skin cancer they found that omega-6 fats were worse for skin cancer and Omega-3s actually help to prevent skin cancer" - **R05 新发现: omega-6 不仅促炎还促皮肤癌**
  - `[20230812002.md 00:03:30–00:03:50]` "omega-6 fats which are found in seed oils have been found to promote inflammation clotting and constriction of blood vessels" - 3 个机制 (炎症+凝血+血管收缩)
- **真实属性**: 学术化论证 + 多个期刊名
- **R05 延续 R04 主题**, 但升级到机制层 (gut dysbiosis / colonic inflammation / 促癌 / 促凝 / 促血管收缩)
- **R05 战术**: R04 是 "seed oil 不好", R05 是 "seed oil 通过具体机制 X 致病", 学术化提高可信度
- **R05 妥协**: "grain finished vs grass fed" 不是关键 → "grain finished diet of beef is far better than the average diet of soybean oil" (R05 不再 dogmatic 强调 grass-fed)

#### 5.4 **Facultative Carnivore 术语提出 (R05 新概念, 重要)**
- **他/她说过的**:
  - `[20230811002.md 00:02:24–00:02:35]` "I think we are probably facultative carnivores now what does that mean now facultative car never it means that well yes you can have an omnivorous diet but you tend to prefer and perhaps do better on a you know all meter most we meet"
- **R05 新出现** (vs R01-R04: 0)
- **真实属性**: Baker 自创术语
- **R05 演化**: 之前 Baker 立场是"人类是肉食者/顶级捕食者", R05 软化为"人类是兼性肉食者 (facultative carnivore) - 可以 omnivore 但偏好肉" → **这是 Baker 论点的微妙软化**, 可能为回应 Mike Dolce 等 omnivore 阵营的批评
- **我推断**: 这是 Baker 第一次正式承认人类是 omnivore 但偏好 carnivore, 标志立场温和化
- **关联**: 与 Jordan Peterson "carnivore 是 elimination diet 工具" 论点更接近

#### 5.5 **Carnivore 怪异副作用论 (R05 新主题: 几乎像"carnivore 奇迹清单")**
- **他/她说过的** (5 个 weird side effects):
  - `[20230812002.md 00:00:30–00:01:00]` "many people notice they have less body odor... your armpits stink because of the bacteria are consuming and modifying skin secretions now we know that they may often Feast on glucose in your sweat in fact a recent study suggested that detecting glucose in the sweat was even easier than Tech than detecting glucose in the blood" - **R05 全新机制: 汗液葡萄糖→细菌→体味**
  - `[20230812002.md 00:01:05–00:01:30]` "on a carnivore diet less gas less farting... the thing that produce gas is a fermentation of plant materials in your gut by gut bacteria now this is made even worse by a high fiber diet because it slows the transit of gas allowing it to accumulate" - **R05 全新机制: 少 gas = 少植物发酵 + 少纤维 = 气体停留时间短**
  - `[20230812002.md 00:01:35–00:01:50]` "many people on a carnivore diet have a better sense of smell perhaps those eating a diet high in carbohydrates aren't aware of how bad they smell because uh their insulin resistance actually reduces their sense of smell" - **R05 全新机制: IR 钝化嗅觉**
  - `[20230812002.md 00:02:00–00:02:30]` "many people also note on a carnivore diet that they're cravings for things like drugs tobacco alcohol are much reduced on a Carnival diet... another mechanism that's thought to be driven by ketosis which happens when you're on a carnivore diet in many cases it allows your brain to clear extra glutamate and make more Gaba" - **R05 全新机制: 酮症→谷氨酸清除+GABA 上升→抑欲**
  - `[20230812002.md 00:02:50–00:03:00]` "hair growth is another one... sometimes people notice that gray hair turns back to its original color probably due to better circulation better hormonal balance better sources of collagen or minerals"
  - `[20230812002.md 00:03:05–00:03:30]` "many people will say they have better Sun Tolerance on a carnivore diet... research in the Journal of carcinogenesis evaluated whether omega-3 or omega-6 oils in the diet would prevent or promote skin disease or skin cancer they found that omega-6 fats were worse for skin cancer"
- **真实属性**: 民间观察 + 拼凑机制
- **R05 新出现** (vs R01-R04: 0)
- **R05 战术**: "carnivore 奇怪好处" 列表式包装, 每条配一个机制 (机制可能不严谨但数量大), 是"carnivore 奇迹清单"的 R05 版
- **Alpha-gal 备注**: `[20230812002.md 00:03:55–00:04:05]` 提醒 alpha-gal syndrome (蜱虫咬) 吃肉过敏是真实问题 → Baker 偶尔也承认 carnivore 不是 100%

#### 5.6 **Carnivore 长期安全论: 借用 Chaffee 女友 Maggie 82岁牧场主 (R05 新增证据)**
- **他/她说过的**:
  - `[20230826002.md 00:00:50–00:01:50]` "this is a picture of a Rancher up in Canada named Maggie um and she is apparently 82 years of age... she is uh uh obviously looks quite young for 82 this is you know a picture of her standing next to her Dr Anthony chafee is his uh I guess fiancee"
  - `[20230826002.md 00:01:50–00:02:20]` "the interesting thing is she's been eating essentially a carnival night for the last 65 years and people are asking where's the long term results on this well this is an example"
  - `[20230826002.md 00:02:30–00:02:50]` "Anthony says he's seen her birth certificate driver's license she showed them all those things I think the veracity of her of her segment she's at each I think I think it's legit I mean I think this person just looks really good maybe it's genetics maybe it's luck but maybe it's avoiding processed food avoiding all the carbohydrate-based dietary advice"
  - `[20230826002.md 00:02:50–00:03:00]` "Jordan Peterson asked me how old she was there's a recent picture basically so we're seeing this getting significant exposure"
  - `[20230826002.md 00:03:30–00:04:00]` "I'm still here in Greece still you know enjoying enjoying the time and uh it's it's a it's a wonderful country we're having some fresh lamb tonight for dinner uh fresh cheese also for dinner and and there's some you know some people are having vegetables the more vegan laying people in our group I'm just kidding I call a bunch of vegans because they're eating vegetables"
- **真实属性**: 借他人案例, 含未验证身份
- **R05 新出现** (R04: 0 直接引用 Chaffee 关系人物)
- **R05 战术**: Baker 之前从未引用 Chaffee; R05 突然通过 "Chaffee 女友的 82 岁姨妈" 案例, 强化"65 年 carnivore 安全" 论点 → **这填补了 R04 公开问题中最关键的 "long term safety" 数据空白**
- **我推断**: Baker 借 Chaffee 的"现场"证据 (不是他本人的学术联盟), 是补充 R05 Revero/Ozempic 主题淡化的替代
- **未验证**: Baker 没亲眼见 Maggie 出生证明, 是从 Chaffee 那里听来 → 我推断 Maggie 是 Chaffee 女友的祖母, 但未独立证实
- **希腊位置**: R05 透露 Baker 在希腊旅居, 与 R04 早期世界巡游相符 (Baker 在 R05 期间不停旅行)

#### 5.7 **抗衰/GLP-1 批判延续: Brian Johnson (Blueprint) 案例 (R05 新主题)**
- **他/她说过的**:
  - `[20230813001.md 00:00:15–00:01:00]` "Brian Johnson he's a 45 year old billionaire that spends two million dollars a year to reverse the aging process"
  - `[20230813001.md 00:01:00–00:01:50]` "Brian Johnson also the name of the liver King it's also the name of the lead singer for AC DC and also there's a cop I know in Albuquerque" - **R05 调侃: 名字撞车 Liver King**
  - `[20230813001.md 00:01:15–00:01:30]` "his routine is pretty overwhelming... we've designed a protocol for sleep and exercise and diet and also 111 supplements"
  - `[20230813001.md 00:01:50–00:02:20]` "blueprint is agnostic and so blueprint says nothing about plants or meat it's simply a process to say we can look at evidence we can design a protocol we can look at data and so I am a vegan by choice not by necessity if somebody can achieve this without supplements wonderful"
  - `[20230813001.md 00:02:30–00:02:50]` "in order to fill the holes made by vegan diet he's having to take 111 pills per day which is a little excessive"
  - `[20230813001.md 00:03:20–00:03:30]` "he takes a drug called arapomycin which is supposed to inhibit cell signaling Pathways to something called mtor which has been associated with the cellular aging process but again there's simpler ways to control empowers called low carb ketogenic diet or something like Rivera" - **关键: Baker 在 8 月就把 Rivera 写错为 Rivera, 再次证明 Revero 营销可能未成熟**
  - `[20230813001.md 00:04:20–00:04:35]` "it's amazing that someone on a mission to extend their life would choose a diet that requires 111 pills a day to supplement instead of just eating Whole Foods like Meat and Fish where you could probably offload many of those supplements"
- **真实属性**: 真信念, 含机制
- **R05 新出现** (R04: 0 Brian Johnson)
- **R05 战术**: Baker 借 Brian Johnson 批判 (a) vegan 必须靠 111 补剂 vs (b) carnivore 不需要补剂 (c) 抗衰可以"be simpler" (d) carnivore/ketogenic 可控 mTOR → **Baker 把 carnivore 包装为"最简抗衰方案"**
- **R05 微妙点**: 1:30 引 mTOR 是 Attia/Peter Attia 抗衰核心术语, Baker 借来用 → Baker 借用 Peter Attia 框架而非 Attia 本人
- **R05 继续强 GLP-1 怀疑**: 20230801001 中对 smaglutide 仍有"known side effects... pancreatitis potential cancers suicide risk" 警告, R04 立场延续

#### 5.8 **平台生存战 + 反审查 (R05 新主题, 含 Berg 引用)**
- **他/她说过的**:
  - `[20230916001.md 00:00:45–00:01:10]` "I recently uh saw a video by Dr Eric Berg now some of you guys are probably familiar with them he inhabits sort of the alternative medicine space kind of someone that I do he talks about nutrition uh he's got quite a big following several many many millions of followers much much larger Channel than I do and he's stated that because of some of the new policies on social media particularly YouTube where... they are going to start to quote d emphasize people that don't speak exactly the message that they want people to have that is eat your uh you know your low-fat foods and take your Pharmaceuticals basically"
  - `[20230916001.md 00:01:10–00:01:30]` "you're going to be sort of Shadow banned you know there's a so-called not a limitation on speech but a limitation on reach which is basically the same thing"
  - `[20230916001.md 00:01:50–00:02:10]` "the people at YouTube or whatever are influenced by their advertisers they are greedy right and so you can you can exploit their greed to combat this nonsense"
  - `[20230916001.md 00:03:20–00:03:30]` "watch an ad more than you normally would or you know let it play for an extra 10 seconds or something like that" - **战术: 故意看 Beyond Meat 广告 → 让 YouTube 知道"we want to see alternative content"**
  - `[20230916001.md 00:05:30–00:05:50]` "you can leverage you know as many people as possible and you know if we look at you know Rumble has 78 million monthly users YouTube has around you know a billion" - Baker 评估平台转移成本
- **真实属性**: 真信念 + 行动号召
- **R05 新出现** (R04: 0 Berg 引用, 0 平台审查主题)
- **R05 战术**: 借 Berg (数百万粉丝) 的可信度为"反审查" 背书; 教观众利用 ad 观看时长反制 algorithm
- **R05 演化**: Baker 第一次明确表态 YouTube 政策对 carnivore 内容的"reach"压制
- **真实属性**: 偏袒反 pharma 阵营, 接受 Berg 立场

#### 5.9 **Baker 个人创伤叙事爆发: 2007 Bagram 战地医院 (R05 全新, 15min 长篇)**
- **他/她说过的**:
  - `[20230917001.md 00:00:25–00:01:30]` "when I went through my surgical training you know as an orthopedic surgeon I saw a lot of horrible horrific things in my life"
  - `[20230917001.md 00:01:35–00:02:20]` "the horrors of War which are you know it's seeing the level of evil the brutality the absolute horror of which man is capable"
  - `[20230917001.md 00:02:00–00:02:30]` "in the winter and spring of 2007 I was deployed to Bagram Afghanistan"
  - `[20230917001.md 00:05:30–00:05:50]` "a 16 year old kid who was actually an enemy combatant but because he was blown up he lost all four extremities both legs above the knee uh one arm at the elbow and one arm at the wrist and we did surgery after surgery on this guy trying to save him... we get attached to this guy we take care of him we get him so he heals his wounds and then we turn him over to the Afghan Army who promptly takes him out back and shoots him in the head"
  - `[20230917001.md 00:08:00–00:08:30]` "the stupid stuff the military made us do the crazy regulations the crazy rules that made no sense to us and we would we would constantly push back against that"
  - `[20230917001.md 00:12:00–00:12:30]` "I would be willing to go back through that horrible horrible experience again uh and fight for this it's that important... to fight for what I think is right because I think what we face you know in the coming future people that want to take away from us our ability to be healthy to take away from us our ability to feed ourselves and to nourish ourselves properly"
  - `[20230917001.md 00:13:00–00:13:30]` "I am dedicated to fighting this war and we are in a war now hopefully it doesn't come up come to the extreme that I just described but we need to all be willing to fight for this"
- **真实属性**: 个人记忆 + 创伤叙事
- **R05 新出现** (R01-R04: 0 战地细节)
- **R05 演化**: Baker 之前只说过"我是 orthopedic surgeon, 工作 120-130 小时/周, 单独带 3 个孩子" (R02-R04 重复); R05 第一次讲 2007 Bagram 战地医院 → 战争创伤是 Baker 人生新维度
- **R05 战术**: 用战时极端创伤 + "I would gladly do all of that again" → 把 carnivore 健康议程升级为"文明存亡战争" (a war for the right to feed ourselves) → 强化使命召唤
- **军事盟友暗示**: `[20230917001.md 00:08:00]` "the stupid stuff the military made us do" → 暗示 Baker 仍批评 military 体制 → 与 Baker 后续 R06+ "公司+使命" 议程衔接

#### 5.10 **Cortisol 恐慌反向论 + 运动抗衰 (R05 新立场)**
- **他/她说过的**:
  - `[20230805002.md 00:00:30–00:00:50]` "why why should you be active why should you exercise why should you stress your body it's only going to raise cortisol it's going to cause you to eat more and therefore shorten your lifespan"
  - `[20230805002.md 00:01:00–00:01:20]` "the literature in human beings generally supports calorie reduction has a net mortality betterment only in a situation where people going from obese to non-obese so if you're not obese and you're lean uh you're active you need to eat enough calories to maintain that level"
  - `[20230805002.md 00:01:20–00:01:40]` "newer research actually shows that in many cases higher cortisol levels are actually beneficial in many cases it helps with mood affect potentially has a longevity benefit"
  - `[20230805002.md 00:01:40–00:01:55]` "we can't just you know mod you know sort of focus on one metric and say well glucose always needs to be low and LDL always needs to be low and cortisol always needs to be low"
  - `[20230805002.md 00:01:55–00:02:10]` "focusing hyper focusing on one biomarker in particular or any number of biomarker biomarkers in particular without understanding the full context is is fueled"
  - `[20230805002.md 00:01:55–00:02:20]` "human beings are the only species that die at age 25 but doesn't get buried doesn't get buried till we're in our 70s"
  - `[20230805002.md 00:03:00–00:03:30]` "stop treating by like trash candle say it over and over again stop eating the garbage that makes you sick once you stop being sick start engaging in the activities they're going to make you healthy and physical activity is important"
  - `[20230804002.md 00:01:00–00:01:30]` "as a surgical resident working sometimes 120 130 hours a week I made time to exercise on a regular basis without without a doubt you know as a full-time practicing surgeon raising uh at times three kids by myself I still found time to uh to be able to work out"
- **真实属性**: 反 cortisol 恐慌 + 反"只盯 biomarker"思维
- **R05 新出现** (R01-R04: 0 显著反 cortisol 立场)
- **R05 战术**: 借反 cortisol 恐慌的批判, 同时反 Peter Attia 风格的 biomarker 优化论 → **Baker 间接把"过度优化 biomarker"批判与"反 Revero/Ozempic 个体化医学" 路线区分**
- **新金句**: "Human beings are the only species that die at age 25 but doesn't get buried until we're in our 70s" - Baker 金句, 强化"stop waiting to die" 主张

### R05 调研方法 + 限制

- 关键词 grep 全 100 文件命中数完整 (Section 1)
- 整文件 Read: 10 个 (20230801001 Ozempic延续, 20230801002 Evolution, 20230804002 Exercise excuse, 20230805002 Cortisol, 20230810001 Fiber, 20230811002 Dolce, 20230812002 Carnivore weird effects, 20230813001 Brian Johnson, 20230815002 Seed oil gut, 20230823002 Chloe Bailey, 20230826002 Maggie, 20230915001 Glyphosate, 20230916001 YouTube censorship, 20230917001 Bagram)
- 限制 1: Revero 0 命中, 但 8 月 13 日 Brian Johnson 视频 Baker 写 "Rivera" 而非 "Revero" → 我推断 Baker 对 Revero 营销在 2023-08 期间已经松弛
- 限制 2: Chaffee 在 R05 唯一一次出现, 借 Maggie 案例 → Baker 与 Chaffee 在 R05 仅"间接引用"关系, 未上升到 R04 与 Paul Mason/Paul Saladino 的"合作" 关系
- 限制 3: Baker 在 20230917 Bagram 视频暴露大量"我作为医生"个人创伤 → Baker 的"医师身份" 框架比 R04 任何文件都更完整
- 限制 4: 0 命中 Joe Rogan / Saladino / Liver King 主线 → R05 期间 Baker 的"名人池" 大幅收缩
- 限制 5: 0 命中 Layne Norton → R04 已减少, R05 完全消失, 标志 Norton 已不是 Baker 重要对手
- 限制 6: 100 文件中 30+ shorts 仍存在, R05 真正主题视频约 50-60 个, 与 R04 比例相似
- 限制 7: Baker 在 R05 强烈表达"反 biomarker 崇拜"+"反过度个体化医疗" + "我也想 anti-aging 但用最简方式 (carnivore)" → **这与 Peter Attia 路线 + Revero 路线都有张力, 我推断 Revero 隐入背景就是为不与此张力冲突**

### R05 关键开放问题 (R06+ 必查)

- **Revero 是否复活**: R05 完全不提, R06 (2023-09+ → 2023-11) 是 Baker 重新推广, 还是彻底放弃? (我推断: 2023 Q3 Revero 公司可能已经卖给其他实体, Baker 转向纯传播者身份)
- **Berg 联盟深化**: R05 借 Berg 反审查, R06+ 是否出现 Baker/Berg 联合视频? (Berg 体量大于 Baker, 不太可能)
- **希腊/世界巡游地点**: R05 显示 Baker 在希腊 + 持续旅行, R06+ 是否回到美国基地?
- **War trauma 是否反复**: R05 一次性讲 2007 Bagram 创伤, R06+ 是否再次出现 (Baker 把它升级为"个人使命起源" 故事)
- **Carnivore 怪异副作用论**: R05 5 个 weird side effects, R06+ 是否扩展到 10-20 个清单?
- **Anti-nutrient 学术化**: R05 借 glyphosate, R06+ 是否扩展到 (a) 草甘膦外的除草剂 (b) 重金属 (c) 霉菌毒素 (mycotoxin)?
- **Facultative carnivore 术语**: R05 首次, R06+ 是否被 Baker 反复使用 (标志其 carnivore 立场最终定型为 "facultative" 而非 "obligate")
- **名人池更新**: R05 短暂提及 Brian Johnson / Maggie / Chloe Bailey, R06+ 是否扩展名人案例
- **Anti-pharma 阴谋深化**: R05 提 YouTube 反 carnivore, R06+ 是否再扩展到 "WHO 反红肉" 叙事
- **Bagram 战地医院同人引用**: Baker 在 20230917 提到 "my partner Dr Tom Large" → R06+ 是否再出现 Tom Large
- **4 个孩子**: Baker 提到"my young son" + "I had just had the first of my four children" (2007), R04 提到"raising at times three kids by myself" → R05 升级到 4 个孩子, R06+ 家庭结构变化

---

## 轮 6/17 (2023-09-17 → 2023-11-01)

**素材范围**: `${HOME}/Documents/女娲造人/@ShawnBakerMD/20230917002.md` ~ `20231101001.md` (100 个 .md 文件, 按文件名升序)
**调研方式**: 关键词 grep + 重点文件 Read
**核心人物**: Dr. Shawn Baker, MD
**关键人物/组织（R06 新增）**: Tucker Goodrich (seed oil 专家 guest 10/16), Layne Norton (回归 Baker 批判对象 10/16), Michael Riley (carnivore + 心脏 triple bypass 案例 10/12), Joe Mercola (电话访谈 10/05), Victoria Farz (vegan → carnivore 律学生 10/28), Michael Greger ("wacky friend" 10/28), Jordan Peterson (carnivore 救 mental health 引用 09/15 跨界), Dr. Tom Large (Bagram 同人后续在 R06 0 命中)

---

### R06 关键发现 (10 条核心 + 标注)

#### 1. Revero 公司复活 + 等待列表 ≥ 1000 人 (Baker 亲自推广) [R06 新出现 / R05 完全消失后]

- **R05 状态**: 0 命中, 营销明显转入背景
- **R06 状态**: 14 文件命中, 多视频大段推广
- **核心证据**:
  - 20231001001.md `00:00:24`: "our Rivero company we have over a **thousand people** on a waiting list ready to go so that's also exciting as you guys know uh **rivero's mission is to treat root CA of disease get people off meds** you know do medicine like it's supposed to be"
  - 20231012002.md `00:00:45`: "our company Rivero will be launching just in a couple days so uh we've got uh you know **several thousand people now on the waiting list**"
  - 20231028003.md `00:02:38`: "my company Rivero is **days away from being launched** I'm super excited"
  - 20230928004.md `00:05:46`: "diabetes pre-diabetes or other chronic conditions you need to hear this Rivero offers **personalized care for metabolic** [conditions]"
- **我推断**: Revero 2023 Q3 暂停后, 2023-10 Baker 重启 launch, 1000-数千人 waiting list 出现, 定位修正为 "root-cause medicine" + "personalized care for metabolic conditions" + "all 50 states" 全美推广
- **R05 开放问题答**: Revero 复活确认, 但 Baker 把它定位从纯 carnivore 平台 → 个体化代谢病管理, 这与 R05 末尾"反 Revero 个体化医学" 路线有内在矛盾 → R06 期间 Baker 实际上把 Revero 重新纳入主推

#### 2. Baker 个人健康事件: Jiu-Jitsu 致 C6/C7 椎间盘突出 + 切换 keto-carnivore [R06 新出现]

- **核心证据**:
  - 20230930001.md `00:00:37`: "7 weeks and two days ago now I **injured my neck while doing Jiu-Jitsu** and uh I ended up with uh what is likely a large **herniated disc between the C6 and C1 C7 level** in my [neck]"
  - 20230930001.md `00:01:51`: "what I've got is **neuroinflammation** this is basically what's going in inflammation of the"
  - 20230930001.md `00:02:30`: "diets or **ketosis and neuroinflammatory conditions** you know as this paper here talks about"
  - 20231001001.md `00:00:43`: "I'm still on a carnivore diet I'm just doing it in a more **ketogenic fashion**"
  - 20231001001.md `00:01:01`: "ketones seems to help with **neuroinflammation** which is you know what I'm currently dealing with"
  - 20231012002.md `00:01:46`: "symtom wise **pain reduction is down significantly** um I've been **able to sleep again**" + "still I've got some pretty good numbness in the fingers but the pain is kind of centralized it means instead of going down my arm it's kind of going back up here"
  - 20231001001.md 量化: 日常 3000-4000 kcal → 1600-2400 kcal; 脂肪占比 65% → 80-85%; 血液酮体 1.x mM → **2.6 mM** (个人历史最高)
  - 20231001001.md 食物: 1 lb New York strip + 8 oz butter / day; 计划切换 suet (牛油) as main fat source
- **我推断**: Baker 在 R06 期间 (大约 8 月中旬) 受伤, 7 周后即 10 月初公开。受伤前 Baker 已 carnivore 8 年, 受伤后切换 "keto-carnivore" (高脂 + 热量限制)。**R06 期间 Baker 第一次把"个人医疗史" 完整公开**, 与 R05 9 月 17 日 Bagram 战地创伤同属"医师身份 + 个人脆弱性" 框架, 但 R06 是 "我现在的脆弱", R05 是 "我过去的脆弱"
- **R05 开放问题答**: Baker 受伤后从 carnivore 转向 keto-carnivore, **Baker 的 "obligate carnivore" → "therapeutic keto-carnivore"** 立场转变实证

#### 3. Tucker Goodrich 作为 seed oil 权威被引为盟友 (10/16) [R06 新出现]

- **核心证据**:
  - 20231016001.md `00:00:03`: "I had a guest on this morning his name is **Tucker Goodrich** he talks about you know the problems with uh **L acid seedo so on and so forth**"
  - 20231016001.md `00:00:38`: "Tucker put out a little thing talking about um you know some of us figure out what's causing pain and are able to relieve that"
- **我推断**: Tucker Goodrich 是 R06 期间 Baker 重点邀请的 seed oil 专家 guest, **R06 把"seed oil 是根因" 推到全期最高位**。R05 (8-9 月) Baker 借 Paul Saladino / Brian Johnson 等"反种子油" 叙事, 但 R06 直接让 Goodrich 单独成集
- **R05 开放问题答**: Anti-nutrient 学术化确认, R06 主线借 Goodrich 学术化 seed oil 议题, 但 **R06 仍未扩展到 glyphosate 外的除草剂 / 重金属 / 霉菌毒素** (我推断 R07+ 才会扩展)

#### 4. Layne Norton 回归为反 carnivore 标杆 (10/16) [R05 完全消失 → R06 重新出现]

- **R05 状态**: 0 命中 (R04 已减少, R05 完全消失)
- **R06 状态**: 20231016001.md `00:00:50`: "this was basically in the context of talking to a guy named **Lan Norton** who some of you guys know he's he's very **critical of everybody's diet** and he's you know he he's a PhD and **knows it all right**"
  - 同段 `00:01:08`: Norton 论 "older 40s 50s have pain and he would rather be strong and have pain than weak"
  - Baker 反驳: "**that's a sentiment I agree with** I certainly think you know there's no there's no in my view real downsides to being stronger you know"
- **我推断**: Norton 在 R04 后曾被 Baker 边缘化 (R04 仅 1-2 命中, R05 0 命中), R06 借 Tucker Goodrich 视频语境重新把 Norton 拉回对话。**Norton 在 Baker 框架中始终扮演"对 carnivore 不友好的 PhD 标杆"**, 但 Baker 对 Norton 的具体批评 (PHD 傲慢 + 弱肉强食论) 实际是借 Norton 引出"pain 与 diet 关系" 主题
- **R05 开放问题答**: Norton 重新进入 Baker 叙事, 但不是"我和他合作" 而是"我和他在 pain 这个具体议题上分歧", 关系保持 R04 的"批判对话" 距离而非 R04 的"反 carnivore 标杆" 简化

#### 5. Michael Riley carnivore + 心脏三搭桥事件 (Baker 反驳医生归因) [R06 新出现]

- **核心证据**:
  - 20231012002.md `00:00:10`: "yesterday some of you guys may have watched a video uh that was entitled I had to respond to this um and it was about a guy named **Michael Riley** who had had ended up having a **triple bypass after going carnivore**"
  - 20231012002.md `00:00:17`: "he had a Doctor by the name of Terry symptom saying oh oh carnivore caused this and not and carnivore people are silly and don't know what they're talking about and you should do a Mediterranean di"
  - 20231012002.md `00:00:32`: "the guy who this was video was about guy Michael Riley um actually **watched video that I did and here's what he had to say so basically he said yeah pretty much what you said was spot on**"
- **我推断**: Riley 事件是 R06 期间 Baker 重要反击战: 主流医生 (Dr. Terry Symmans? Baker 语音转文字是 "symptom") 把 carnivore 归因到 Riley 心脏事件, Baker 反驳后 Riley 本人观看 Baker 视频并称 "spot on" → Baker 框架中此案例的胜利点是 "Riley 主动确认 Baker 解读正确"。**Baker 借此把"carnivore kills" 主流叙事的归因错误公开化**, 与 R05 YouTube 反 carnivore 言论同属 "anti-carnivore pushback" 反击

#### 6. Joe Mercola 主动电话访谈 Baker (10/05) [R06 新出现]

- **核心证据**:
  - 20231005001.md `00:01:43`: "I had a nice long discussion with uh **Dr Joe Mercola** we he called me up and we had a long discussion uh yesterday"
- **我推断**: Mercola 主动联系 Baker, Baker 视为地位认证。Mercola 在 Baker 框架中是"健康领域元老级别人物", 但 Mercola 自身在主流医学外, **R06 期间 Baker 借 Mercola 背书继续在 alternative medicine 圈层上升**

#### 7. 反 lab-grown meat 攻势 (意大利禁止 + Upside Foods 失败) [R06 新出现 / 显著强化]

- **R05 状态**: R05 仅 1 文件轻提 lab meat
- **R06 状态**: 2 个完整视频专题
- **核心证据**:
  - 20231005001.md `00:00:02`: "the Italians have decided that they're going to **ban lab-grown meat** in keeping with traditional food production"
  - 20231028003.md `00:00:04`: "fake lab Meat Company **Upside Foods** it looks like insiders are basically saying it's all show and they're actually growing cells in Little 2 L bottles and not the giant reactors of 500 lers which some people think is going on this means they are nowhere near ready to go on a large scale"
  - 20231028003.md `00:00:48`: "BBC has published an article saying that **cultured lab meat makes climate change worse** well imagine that building a factory running all this equipment I guess that does take energy after all compared to **cattle grazing on grass of course**"
  - 20231028003.md `00:00:36`: 视觉化描述 lab 工厂 "I think it looks more like a **bioweapons factory** than some place where we're going to be making food"
- **我推断**: R06 期间 Baker 借 3 个独立事件 (意大利政策 + Upside Foods 商业失败 + BBC 气候研究) 全面否定 lab meat, **立场从 R04-R05 的"忽略" 升级到 R06 的"主动攻击"**。视觉修辞 "bioweapons factory" 是 R06 期间 Baker 表达极端的新高点, 标志 Baker 对 "carnivore 商业对手" 防御意识增强

#### 8. BMJ 136,137 人碳水化合物研究被借为反植物 [R06 新出现]

- **核心证据**:
  - 20231028003.md `00:01:02`: "study in the **British medical journal** looked at **136,137 people** and whether the carbohydrates they eat changed their weight and guess what they showed that **starches made people gain weight so did sugars** fiber helped them to gain a little less weight but they still gain weight"
- **我推断**: Baker 用 BMJ 大型流行病学研究做"反植物 (反碳水)" 学术背书。R05 期间 Baker 反植物主要靠 carnivore 个案 + 反 cortisol 逻辑, R06 借 BMJ 主流期刊 + 13.6 万人队列 → **学术化程度 R06 显著高于 R05**
- **R05 开放问题答**: Anti-nutrient 学术化推进到 BMJ 引用级别, 但还未到 Cochrane / Lancet 级别

#### 9. Michael Greger 被称 "wacky friend" + 倡导者反讽 (10/28) [R06 新出现]

- **核心证据**:
  - 20231028003.md `00:02:15`: "our **wacky friend Dr Michael Greger** is at it again claiming that eating **plants reduces exposure to Industrial toxins** news flash there is such a thing"
  - 20231028003.md `00:02:25`: "**pesticides and herbicides** both of"
  - 20231005001.md `00:00:53`: "the Italians..."
- **我推断**: Baker 在 R06 把 Greger 升级到 "wacky friend" 戏称, 是 R04-R05 期间对其认真反驳的简化。**Baker 对 Greger 的态度从"严肃对手" → "滑稽人物"**。这是 Baker 借反差萌巩固自己立场的修辞策略

#### 10. Victoria Farz (vegan → carnivore 律学生) + Synthol 注射 + 健康反弹案例 (10/28) [R06 新出现]

- **核心证据**:
  - 20231028003.md `00:02:01`: "**The Daily Mail** actually publ a story about a law student **Victoria farz** who quit her vegan lifestyle went carnivore and she says she is much healthier and she also says the **vegan diet was the worst decision of her life**"
  - 20231028003.md `00:01:20`: "Fitness and self-improvement a man has decided he doesn't e testosterone or meat that's right you don't need all that meat to grow big muscles... this person is injecting his muscles with an oil called **Synthol** to make them look larger it's dangerous can cause Strokes infections heart attacks and it just looks stupid"
- **我推断**: R06 期间 Baker 把"vegan → carnivore" 案例库扩展到法律领域 (Victoria Farz, 律学生)。**Baker 的反 vegan 案例池已从 R05 的"明星/网红" 扩展到"专业人士 (律学生/前 WWE 妈妈等)"**, 标志 Baker 借"职业身份" 多样化反 vegan 叙事
- **Synthol 反讽**: Baker 借 "植物基 + 无肉肌肉男" 失败案例强化"你需要肉" 主张, 标志 Baker 反 plant-based 蛋白论的新证据

### R06 战术 / 立场演化观察

- **Revero 复活 = R05 开放问题答**: Baker 从 R05 完全不推广 → R06 大规模宣传 (waiting list 1000-数千, all 50 states 推广) → **R06 Revero 实际成为 Baker 最高优先商业话题**
- **个人健康 = 新身份维**: Baker 公开受伤 + 切换饮食 + 量化 (1600-2400 kcal, 脂肪 80-85%, 酮体 2.6 mM) → R06 期间 Baker 把"carnivore doctor" 升级到 "carnivore + 自医 keto-carnivore doctor"
- **学术化推进**: BMJ 13.6 万人队列 + 瑞典 100 岁人 cholesterol 243 mg/dL 研究 (20230922002.md) → R06 期间 Baker 的"反胆固醇恐慌" + "反植物" 获得"主流期刊" 背书层级
- **盟友更新**: Tucker Goodrich + Joe Mercola 双重背书, R06 期间 Baker 的"反种子油 + 替代医学元老" 联盟强化
- **借势策略**: Norton 重新出现, 但 Baker 借 Norton "PHD 傲慢 + 弱肉强食" 设定强化自己 "医生 + 患者中心" 形象
- **Norton 借机论 pain 与 diet 关系**: 20231016001.md 后期 (R06 核心论证) Baker 借 2020 University of Alabama knee pain 研究, Baker 承认 "I as an orthopedic surgeon for years I didn't think that was the case I just Sally dawn on me" → **Baker 罕见地承认自己过去 (作为骨科医生) 不相信 diet 与 pain 关系**, 这是 R06 期间 Baker 最显著的"自我反思" 段落

### R06 重要引用与数据点

- **2023 Sweden centenarian study** (20230922002.md): 百岁人群 cholesterol 243 mg/dL (slightly higher than non-centenarians), blood glucose 91 (significantly lower) → Baker 用于反 "lower your cholesterol to live longer" 主流叙事
- **2020 University of Alabama knee pain study** (20231016001.md): Baker 借研究建立 "diet → inflammation → joint pain" 因果链
- **BMJ 136,137 人队列** (20231028003.md): 碳水 (淀粉 + 糖) 与体重正相关, 纤维轻度缓解但仍增重
- **Glyphosate → Alzheimer's 死亡相关性** (20230915001.md `00:04:23`): Baker 继续 R05 的 glyphosate 议题, **红线 = 草食反刍动物避开 glyphosate**
- **Joe Rogan podcast 6 周年** (20231010001.md `00:01:50`): Baker 提到 "almost going on six years ago I was on Joe Rogan's podcast" → R06 期间 Baker 把 Rogan 经历升级到 "6 年前" 时间框架, 持续强化 Joe Rogan 节点

### R06 调研方法 + 限制

- 关键词 grep 全 100 文件命中数 (Section 1)
- 整文件 Read: 4 个 (20230922002 Sweden centenarian, 20230930001 Neck injury, 20231001001 Keto-carnivore update, 20231012002 3 updates + Riley, 20231016001 Pain + Tucker Goodrich, 20231028003 Carnivore news)
- 限制 1: Cywes / Norwitz / Chaffee 全部 0 命中 → **R06 期间 Baker 的"盟友池" 收缩到 Tucker Goodrich / Joe Mercola / Layne Norton (作为对手)**, 未出现 Carnivore 圈层其他医师
- 限制 2: Attia / Paul Mason / Malcolm Kendrick 0 命中 → R05 期间 Attia 已边缘化, R06 进一步沉默
- 限制 3: R06 期间 Baker 引用 "many studies" 但未点名 (除 2020 University of Alabama knee pain + BMJ 13.6 万人 + 2023 Sweden centenarian) → Baker 的"学术化引用" 集中在 3 个研究, 未到反 pharma 圈层那种"每月 20 引用" 强度
- 限制 4: 100 文件中约 30-40 个是 shorts / 重复主题, R06 真正有内容视频约 50-60 个
- 限制 5: Baker 受伤 7 周后 (10 月初) 公开 → 实际受伤可能在 8 月中旬, 跨越 R05-R06 边界。R06 期间 Baker 把受伤归到 "keto-carnivore 切换原因", 但受伤事件本身发生在 R05 末尾
- 限制 6: Baker 在 20231010001.md 提到 "I was on Joe Rogan's podcast... and you know several years ago he said" → Baker 借回忆 Rogan 经历建立资历, 但未给出具体节目内容
- 限制 7: Baker "I hope we're wildly successful I hope that we we become extremely financially successful" (20230918001.md `00:07:33`) → Baker 对 Revero 商业化明确表露财务野心, 与 R05 "do medicine like it's supposed to be" 框架有内在张力

### R06 关键开放问题 (R07+ 必查)

- **Revero 2023-11 是否正式 launch**: R06 末 (10/28) "days away from being launched" → R07 (2023-11+) 是否正式上线? 上线后 Baker 的内容是否变化?
- **Baker C6/C7 伤势恢复**: R06 期间 "pain reduction is down significantly" 但仍有 "numbness in the fingers" → R07+ Baker 是否完全恢复? 恢复后是否回到 pure carnivore 还是继续 keto-carnivore?
- **Tucker Goodrich 二次 guest**: R06 仅 1 次 Goodrich 出现 → R07+ 是否深化合作? Goodrich 是否有自己的节目? (我推断 Goodrich 是独立 guest, 不是 Baker 长期合作)
- **Michael Riley 后续**: Baker 称 "Riley 确认 spot on" → R07+ Riley 是否再次出现? Baker 是否有 Riley 复诊 interview?
- **Victoria Farz / 律学生 carnivore 池**: R06 仅 1 例 → R07+ Baker 是否扩展到"前 vegan 专业人士" 案例池?
- **Anti-nutrient 学术化扩展**: R06 集中 BMJ 13.6 万人 + Sweden centenarian + U-Alabama knee pain → R07+ 是否扩展到 Lancet / Cochrane / Nature 级别研究?
- **Lab meat 议题**: R06 借意大利 + Upside Foods + BBC 三重攻击 → R07+ lab meat 是否有新一轮进展? Baker 立场是否变化?
- **Layne Norton 关系**: R06 仅 1 次 "critic" 框架出现 → R07+ Norton 是否升级为 "对手" 或 Baker 维持现状?
- **Anti-pharma 阴谋深化**: R06 期间 Baker 提 YouTube 反 carnivore (R05 主题延续) → R07+ 是否扩展到 "WHO 反红肉" 叙事?
- **家庭结构变化**: R05 提到 4 个孩子, R06 期间 0 命中家庭 → R07+ Baker 家庭是否变化?
- **Glyphosphate 与 Alzheimer's 因果链**: R05-R06 都在引用 → R07+ Baker 是否把这条线推到 "草甘膦是 dementia 主因" 极端立场?
- **Bret Weinstein / Lex Fridman / Peter Attia / Paul Saladino 联盟**: R06 全部 0 命中 → R07+ Baker 的"医师 + 知识分子" 盟友池是否收缩到 0?
- **Hormesis / 原始饮食 / 进化论框架**: R06 0 命中 → R07+ Baker 是否回到 R03-R04 的"祖先健康" 框架?

### R06 历史地位与 R05 对比

- **R05 主题**: Cortisol 反恐慌 + Brian Johnson 反 biomarker + Glyphosate 学术化 + Bagram 创伤 + Revero 隐入背景
- **R06 主题**: Revero 复活 + Baker 自伤 (C6/C7) + keto-carnivore 切换 + Tucker Goodrich 学术化种子油 + Norton 重回框架 + Riley 反主流医生 + Mercola 联盟 + lab meat 全面攻击 + Greger 戏称 + Victoria Farz 案例
- **R06 标志事件**: Baker 受伤 + Revero 复活, 这两个事件同时把 Baker 推入"个人脆弱性 + 商业新周期" 双轨
- **R06 vs R05 关键差**: R05 Revero 沉默 → R06 Revero 高调; R05 Baker 隐藏个人脆弱 → R06 Baker 公开受伤细节; R05 学术化偏 cortisol → R06 学术化偏 BMJ + Sweden centenarian + U-Alabama knee pain
- **R06 vs R04 关键差**: R04 Baker 与 Paul Mason / Paul Saladino 合作 → R06 全部 0 命中, Baker 盟友池收缩到 Tucker Goodrich / Mercola
- **我推断**: **R06 是 Baker "carnivore doctor + 自医受伤医师 + 复活商业 + 学术化借势" 多线并行期**, 比起 R05 的"反 cortisol 反 biomarker 单一战线" 更复杂更接近 Baker 真实身份多重性

---

## 轮 7/17 (2023-11-02 → 2023-12-14)

**素材范围**: `${HOME}/Documents/女娲造人/@ShawnBakerMD/20231102001.md` ~ `20231214001.md` (100 个 .md 文件, 已确认)
**调研方式**: 关键词 grep + 重点文件 Read (7 个文件: 20231110001, 20231115001, 20231117002, 20231121001, 20231126003, 20231128002, 20231129001, 20231202003, 20231204001, 20231210002, 20231212003)
**关键 R07 人物/组织**: Peter Attia (新), Derek "More Plates More Dates" (新), Dave Feldman (回归), Nick Norwitz (新出现), Brian Sanders / Food Lies (新), Cali Means (新), Dave Felman/Feldman (同一人, 写法不同), Walter Willett (Harvard 攻击对象), Chris Gardner (Stanford 攻击对象), Nina Teicholz (Nina Teicholz 拼写为 "Nina tyz" 字幕误转), Anthony Gerard (Newsweek 记者), Whitney Cummings, Philip Prins/Prims (运动生理学, 拼写不确定), "Sapien Center" (Brian Sanders 实体)
**注意**: 字幕为 YouTube auto-caption, 人名有大量误转 ("Nina tyz" 应为 Nina Teicholz, "Noram" 应为 Norwitz 等), 引用须保留原拼写并标注。

---

## 1. R07 调研命令一览 (grep + 命中数)

| 关键词 | 命令 | 命中文件数 |
|---|---|---|
| `revero\|rivero` | `grep -liE "revero\|rivero" $(ls \| sort \| sed -n '601,700p')` | **8** |
| `GLP-1\|ozempic\|semaglutide\|wegovy\|mounjaro\|tirzepatide` | 同上 | **0** |
| `anti.nutrient\|antinutrient\|lectin\|phytate\|oxalate` | 同上 | **3** |
| `C6\|C7\|cervical\|spine\|surgery\|recovery\|fusion\|vertebra` | 同上 | **8** |
| `chaffee\|norwitz\|cywes\|attia\|layne\|norton` | 同上 | **5** |

---

## 2. R07 核心发现 (10 条, 标注延续 vs 新出)

### 2.1 Revero 扩张 (R07 新出, R06 复活后进入规模化) 🆕
- **20231115001** `[00:03:22]`: "my company Rivero has expanded our waiting list to include autoimmune and inflammatory conditions"
- **20231117002** `[00:05:22]`: 长 form Rivero YouTube channel 是 "the Rivero uh YouTube channel it's my other channel where I do interview long form interviews" → **Rivero 同时是公司名 + podcast 频道名**
- **20231128002** `[00:01:02]`: Rogan 提到 "our company that we've got Rivero"
- **20231204001** `[00:02:39]`: "nearly another 2,000 people sign up for Rivero" → **R07 Revero 增速从 R06 "复活" 进入"规模化获客"阶段**, 目标"hundreds of thousands eventually the millions of people"
- **20231212003** `[00:00:08]`: "company it's called Rivero and we we're licensed in all 50 states" + "Physicians all across the country" + "root cause medicine get people off the medications" → **首次明确 Rivero 全美 50 州执业许可 + 跨州医师网络**
- **我推断**: **R07 Revero 从"产品/平台"升级为"全国性医疗服务网络"** — Baker 商业身份从"演讲者 + 倡导者"明显转向"全国医疗基础设施供应商"

### 2.2 Joe Rogan 第 2 次出镜 (R07 新出) 🆕
- **20231126003** `[00:00:08]`: "I'm going back on a Joe Rogan so that's going to be tomorrow" — 11/27 Austin 出差, Rogan 节目 air 11/28
- **20231128002** `[00:00:25]`: "the podcast should drop I think it'll drop today" — **Joe Rogan 第二次出镜成功**, Baker 评价 "Joe was a very gracious uh host uh just just all around really nice guy" + "Joe is he gets it I mean he totally he's on board with Carnival believe me"
- **20231204001** `[00:00:35]`: "you know as for some of you guys I saw the episode I was sort of sort of a little complaining that I could not get funding for carnivore studies even from the beef industry itself... well I've had a number of people that are associated uh with these agencies now reaching out to me" — **Rogan 效应 = 牛肉行业 (NCBA) 高管主动联系 Baker 提供研究资金**
- **20231212003** `[00:00:01]`: Rogan 节目的 audio clip — Rogan 在节目中问"What's the name of the company so company's called rivo re is going to be something that I think will provide Healthcare as it should be"
- **我推断**: **Rogan 第 2 次出镜 = Baker 公开发声 + Revero 商业双里程碑**, 间接带来"NCBA 资金松动" 连锁效应

### 2.3 Peter Attia 直接辩论 (R07 新出, R06 "Norton critic" 框架的精英升级) 🆕
- **20231121001** 整个文件: Baker 出 video 专门回应 "Peter Attia / Derek 'More plates more dates'" — 这是 **R01-R07 首次 Baker 公开把 Attia 列为辩论对手**
- `[00:00:28]`: "somebody who has a you know almost a self-induced familial hypercholesterolemia level from their carnivore diet saying something like don't worry about it" — Baker 转述 Attia 阵营对 carnivore 者的"自我诱导 FH" 标签
- `[00:00:56]`: "FH is a disease called familial hyper cholesterolemia and it's uh actually this the second most common genetic cause of atherosclerosis" — Baker 在视频里给观众上遗传学课
- `[00:01:43]`: "FH is defined by having an LDL cholesterol greater than 190 milligrams per deciliter" — Baker 用具体数字反驳
- `[00:03:58]`: "my first sort of concern around that is is equating FH a genetic disease with dietary induced hypercholesterolemia is not the same thing this is an APPL orange comparison" — **核心反驳: FH 遗传病 ≠ 饮食诱导高 LDL, 苹果橘子类比**
- `[00:04:15]`: "if I take a bullet and I fire from a gun into your head it's going to cause some problems right... if I take that same bullet and I just throw it at you right same bullet but it's a very different different uh overall situation" — **Baker 标志性子弹类比**: LDL 是"子弹"但"被射出" vs "被扔出" 是不同情景
- `[00:05:20]`: 引用"100-year-old with FH with no with elevated LDL cholesterol for for 100 years with no negative alcome" — **Baker 用 100 岁 FH 个案反驳"LDL 必然累积损伤" 假说**
- `[00:05:45]`: 引用"Danish heart registry" + "cority calcium" vs LDL — **Baker 用丹麦心脏登记数据, 钙化评分 0 时 LDL 与 MACE 不相关**
- `[00:07:50]`: 引用"lean mass hyper responder" study (Dave Feldman + Matt Bootoff + Nick Norwitz 团队) — **R07 新出: Nick Norwitz 进入 Baker 援引的科学家名单**
- `[00:10:23]`: "I doubt honestly that Peter T is going to be convinced you know or not that it matters but by the lean mass hyper responder to however it comes out... then what what would you how would you respond to that" — **Baker 邀请 Attia 来回应 LMHR 研究结果**
- `[00:10:56]`: "I think I think that's really probably UNC you know incontrovertible that that you can mitigate some of the effect of LDL cholesterol by not smoking by exercising by having good glycemic control by having low inflammation by having normal blood pressure" — **Baker 立场: 不否认 LDL 因果角色, 但坚持"代谢健康可抵消部分风险"**
- `[00:11:22]`: "you're not going to ever hear me saying ignore LDL cholesterol doesn't matter but do I believe that there are some protective effects from having otherwise good health yes I do" — **Baker 自我标定立场边界**
- `[00:11:55]`: "I am certainly um willing to accept that I could be wrong" — **Baker 罕见的"承认可能错" 表述**
- **我推断**: **R07 Attia 直接对辩 = Baker 与"长寿医学派" 公开决裂的起点**, Baker 此前在 R01-R06 与 Attia 关系模糊 (R06 仅 1 次提及), R07 进入"公开点名 + 学术化反驳" 阶段; 同时 Norwitz 首次进入 Baker 科学家盟友池

### 2.4 Derek "More Plates More Dates" 作为 Attia 中介 (R07 新出) 🆕
- **20231121001** `[00:02:11]`: "Derrick's last name he's a more plates more dates guy now of Mer health and and Derrick made a name for himself doing all the Izzy on steroids type of stuff"
- Baker 把 Derek 描述为"过去做类固醇科普起家" → 现在采访 Attia 时, Baker 成为了"被点评对象"
- **R07 新出**: Baker 把"网红补剂/类固醇科普 YouTuber" 作为当代医学辩论的传声筒, 说明 Baker 承认 YouTube 学术科普生态圈的影响力
- **我推断**: R07 Baker 与 Attia 派的对决, 实际通过 Derek 这类"中间科普网红" 放大

### 2.5 Nick Norwitz 进入引用名单 (R07 新出) 🆕
- **20231128002** `[00:00:53]`: "you know the lean mass hyper responder study that Dave Feldman you know Matt boot off Nick nors and others are doing"
- **R07 新出**: Nick Norwitz 从 R05-R06 0 命中 → R07 首次出现, Baker 在 Rogan 节目上专门提到 Norwitz + Feldman + Bootoff 的 LMHR 团队
- **我推断**: Norwitz 是 LMHR (Lean Mass Hyper Responder) 研究的核心青年学者 (Oxford PhD + Harvard MD 背景), Baker 借 Rogan 节目 + Attia 反击双线同时推广, 标志 Baker 科学家盟友池向"新一代代谢研究者" 转移

### 2.6 Anti-nutrient 学术化扩展 (R07 新出) 🆕
- **20231210002** `[00:00:30]`: "come on what about vegetables fruit grains enzyme Inhibitors oxalates cyto oxalates so many things that cause inflammation in the gut" — **首次明确使用 "enzyme inhibitors" 和 "oxalates" 两个具体学术名词**, Baker 在引用其他 carnivore 实践者的原话
- **R07 新出**: R06 的 anti-nutrient 学术化 (lectin / phytate) → R07 加入 **oxalates + enzyme inhibitors**, 学术化清单从 2 个扩展到 4 个
- **20231121002** `[00:00:01]`: 整个视频讲"rotator cuff 损伤 vs 饮食" — Baker 用外科医生经验 + 学术论文论证 **糖尿病 → 高级糖化终产物 (AGEs) → 肩袖撕裂** 因果链
- `[00:01:21]`: "an advanced glycation end product uh and what what essentially what's happening is sugar mixes with the proteins and we end up with this degraded tissue"
- `[00:02:30]`: 引用教授 "Philip prims" (运动生理学家, Pennsylvania) — 高碳 vs 低碳运动员研究, **高碳组近 50% 运动员出现 pre-diabetic 血糖**, 低碳组没有
- `[00:04:05]`: "vegans don't heal as well I mean there's papers that show that particular like things like you know surgical scars surgical incisions they don't heal as well" — **Baker 把 anti-nutrient 学术化推到"植物饮食延缓伤口愈合"**
- **我推断**: R07 anti-nutrient 学术化从 R06 的"理论"升级为 R07 的"外科医生临床经验 + 同行论文", Baker 借"自己就是 ortho surgeon" 的身份背书, 把"植物毒素" 论点推到"植物延缓术后愈合" 的硬核临床维度

### 2.7 C6-C7 颈椎恢复 + 干细胞治疗 (R07 持续 + 新增) 🆕
- **20231129001** `[00:01:08]`: "some of you guys know back in August I kind of injured my neck doing Jiu-Jitsu" — **R06 受伤 → R07 持续康复中**
- `[00:01:16]`: "my PRI preor to that I was you didn't really have any neck issues to speak of I mean I'd spent years playing rugby and you know that that probably you know at some point led to a little bit of degenerative change over the years and I'm you know I'm getting close to 60 years old right now" — **Baker 年近 60 公开承认 rugby 累积退变 + 巴西柔术急性损伤**
- `[00:01:23]`: 症状"horrible pain going on my arm and I couldn't sleep and pretty bad numbness and burning and uh and actually some weakness in my tricep"
- `[00:01:52]`: "Joe had reached out to me and Joe's a very nice guy very generous very nice guy" + "way to Wells it's a it's a stem cell clinic in Austin" — **Joe Rogan 安排 Baker 在 Austin 干细胞诊所治疗**
- `[00:02:32]`: "I am very skeptical in fact you know of my own accord I probably would have not sought out stem cells because my my sort of belief and my bias is as an orthopedic surgeon the American Academy of orthopedic surgeons basically says hey we don't think stemell do much" — **Baker 罕见公开自我矛盾**: AAOS 立场 vs 个人接受
- `[00:02:54]`: "the these are uh neonatal stem cells they come from an umbilical cord right" — 注射的是 **新生儿脐带干细胞 (异体)**
- `[00:02:59]`: "I had one directed you know into my neck musculature they can't do it into the disc is where you know I had a disc injury" — 注射位置: **颈肌内** (不能直接注入椎间盘)
- `[00:03:16]`: "Wharton's jelly" + "amniotic fluid" + peptide "BP 157" — 治疗包含 **Wharton 凝胶 + 羊水 IV + BPC-157 肽**
- `[00:03:33]`: "I'm a lot of the way healed already" + 残留"numbness particularly in this index finger that has not really changed much at all"
- **我推断**: **R07 Baker 把"carnivore 治愈" 路线 → 切换到"干细胞 / 肽" 等再生医学路线**, 标志 Baker 的"个人健康维护" 从"纯饮食"扩展到"前沿再生医学" — 这是 R06 受伤事件 → R07 演化出的新轨迹

### 2.8 Stanford Twin Study 反击 (R07 新出) 🆕
- **20231202003** `[00:00:01]`: Baker 攻击 Stanford Chris Gardner 的 "22 对双胞胎" vegan vs omnivore 研究
- `[00:00:50]`: "Chris Gardner is a guy that thinks that it is unethical literally unethical to study a carnivore diet" — **Baker 揭露 Gardner 自己说研究 carnivore 不伦理**
- `[00:01:25]`: "in part it was funded by the game changers uh foundation" + "made that vegan propaganda film" — 揭露资金来源是 The Game Changers 片方
- `[00:01:52]`: "Chris Gardner's also taken a lot of money from the beyond meat Corporation" — **揭露 Gardner 收 Beyond Meat 资金**
- `[00:02:35]`: 揭示研究设计问题: omnivore 组含 "more refined grains and more sugar", "vegans are 15% less likely to enjoy the diet so they very likely could have eaten less food"
- `[00:03:20]`: "the vegans were less likely to obtain enough vitamin B12 which is a known deficiency issue"
- `[00:03:35]`: "I could not find whether it was just lean mass very well could have been lean mass say they also consume far less protein" — **Baker 推论 vegan 组减重可能是减肌肉**
- **同时发布**: Crohn's disease + ulcerative colitis 病案研究征集 — "they have and gone away using one of those diets please use a link in the description"
- **我推断**: R07 Baker 反击 Stanford 研究的攻击点, 是 **从"研究设计 + 资金来源 + 个人偏见" 三维揭露** — 模式同 R04 攻击 Walter Willett, 但 R07 加入"双胞胎研究 + Game Changers 资金链" 的具体细节

### 2.9 Harvard Walter Willett 揭露持续 (R07 持续) 🔄
- **20231115001** `[00:01:56]`: 引用"investigator reporter Nina tyz" (Nina Teicholz 字幕误转) "published an incredibly detailed article about Walter SE Willet who was the head of Nutrition department at Harvard th Chan for 25 years this person is the reason that Harvard promotes an anti- meat agenda"
- **R06 已有**: Harvard 反红肉叙事; R07 加入 **Willett 25 年领导 + Teicholz 揭露的具体人物 + 时间跨度**
- **Nina tyz → Nina Teicholz**: 这是 R07 唯一可见的"因字幕自动转录导致人名错位" 案例
- **我推断**: Baker 与 Teicholz 的"反 Harvard" 联盟在 R07 深化 — Baker 引用 Teicholz 在 *Newsweek* 的具体调查文章

### 2.10 WHO 警告 + 牲畜未来 / Calley Means 采访预告 (R07 新出) 🆕
- **20231110001** `[00:00:00]`: Baker 在机场谈 Florida "medical freedom" conference, 提到 "I did a really f fascinating interview with guy named Cali means"
- `[00:00:34]`: "C Means" 背景: "he used to be uh uh into politics he was a uh work for the uh Coca-Cola Corporation American Beverage Association uh work within the pharmaceutical industry" — **Calley Means 从 Coca-Cola + 制药行业转反建制** (与 Baker 自身整骨外科医生转向 carnivore 形成职业轨迹对位)
- `[00:00:54]`: "you think how how could that happen accidentally" — "half your population pre-diabetic and 75 8% of your population overweight" → **Baker 暗示美国慢病是"被设计" 的, 不是意外**
- **R07 新出**: Calley Means (后来成为 MAHA / RFK Jr. 阵营核心) 首次出现在 Baker 引用 — 这是 R07 后期 Baker 走向"MAGA 健康" 政治的预演
- **我推断**: R07 Baker 开始从"carnivore doctor" 走向"反建制医疗政治" 话语; Calley Means 是这个转向的过渡人物

---

## 3. R07 主题 / 关键词 / 思想脉络 (Baker 这一轮在讲什么)

### 3.1 Baker 5 大并行主题
1. **Rogan 第 2 次出镜 + 商业激活**: Revero 全美 50 州许可 + 2,000 增量用户 + Rogan 节目带来 NCBA 资金松动
2. **与 Attia 派公开对决**: 把"FH ≠ 饮食诱导 LDL" + "LMHR 团队研究" 作为两大论据, 罕见地"承认可能错"
3. **自身再生医学治疗**: Rogan 安排的 Austin 干细胞 + BPC-157 肽治疗, 标志 Baker 健康维护路径从"纯饮食" 扩展到"前沿再生"
4. **学术化攻击升级**: Stanford Twin Study (Gardner + Game Changers + Beyond Meat) / Harvard (Willett + Teicholz) / 运动生理 (Philip Prins) / 外科经验 (AGEs + vegan 愈合差)
5. **政治化话语萌芽**: Calley Means 采访 + Florida medical freedom conference + "pre-diabetic 是被设计" 暗示

### 3.2 Baker 在 R07 引用频率最高的 5 个 "他/她/它"
- **Dave Feldman**: 多次出现 (Rogan 节目 + Attia 反驳视频), Baker 把 LMHR 团队作为主要科学盟友
- **Peter Attia**: 直接辩论对手, Baker 在 R01-R06 与 Attia 关系模糊, R07 公开点名
- **Nina Teicholz** (字幕误为 "Nina tyz"): 揭露 Willett 的盟友, R07 Baker 与 Teicholz 关系深化
- **Joe Rogan**: 2 次出镜 + 干细胞治疗安排 + 商业曝光平台
- **Nick Norwitz** (R07 新出): LMHR 团队新成员, Baker 在 Rogan 节目上明确提及

### 3.3 Baker 在 R07 反对频率最高的 5 个 "靶子"
- **Walter Willett / Harvard TH Chan**: "this person is the reason that Harvard promotes an anti-meat agenda"
- **Chris Gardner / Stanford**: "literally unethical to study a carnivore diet" + Game Changers 资金 + Beyond Meat 资金
- **Peter Attia**: "self-induced familial hypercholesterolemia" 标签 + 过度依赖 statins
- **Derek "More Plates More Dates"**: 类固醇科普起家 → Attia 阵营传声筒
- **WHO / UN**: 持续反红肉 + 牲畜未来议题 (隐含, Baker 未直说)

### 3.4 R07 Baker 标志性表达
- **"Apple-orange comparison"** `[20231121001 00:03:58]`: 反驳"FH = 饮食诱导 LDL" 假说
- **"Shoot a bullet vs throw a bullet"** `[20231121001 00:04:15]`: 子弹类比 — 同一子弹, 不同轨迹
- **"The off switch"** `[20231117002 00:05:39]`: 描述 carnivore 帮助食物成瘾者找到"食欲关闭开关" — Lindy 770 lbs 减 500 lbs 案例
- **"If you're not going to be a carnivore, at least be a meat-eter"** (R07 隐含, 反复出现)
- **"Spontaneous remission"** `[20231117002 00:03:20]`: 描述 membranous glomerulonephritis 自发缓解 — Baker 借用医学术语描述 carnivore 奇迹
- **"Medicating and symptoma management"** `[20231212003 00:00:54]`: 描述现行医疗系统

---

## 4. R07 立场演化 vs R06

| 维度 | R06 立场 | R07 立场 | 演化方向 |
|---|---|---|---|
| Revero | 复活, 平台化 | 全美 50 州许可 + 跨州医师网络 + 2,000 增量用户 | **从"产品" 到"全国医疗基础设施"** |
| Attia 关系 | 0 命中 | 公开点名 + 视频反驳 + 引用 LMHR 团队 | **从"模糊不提" 到"公开对决"** |
| Norwitz 关系 | 0 命中 | Rogan 节目 + Attia 反击双线引用 | **"新盟友"入池** |
| Baker 个人健康 | R06 受伤 + 公开疼痛 | R07 接受干细胞 + BPC-157 + Wharton 凝胶治疗 | **从"忍受 + 描述" 到"前沿再生医学"** |
| 学术化 | BMJ 13.6 万 + Sweden centenarian + U-Alabama knee | Stanford Twin (Gardner 资金) + Harvard (Willett 揭露) + 运动生理 (Philip Prins) | **从"借他山之石" 到"揭露具体研究人员 + 资金链"** |
| Anti-nutrient | lectin / phytate | oxalates / enzyme inhibitors + AGEs + vegan 愈合差 | **学术化清单从 2 词扩到 4 词 + 进入外科临床证据** |
| Norton 关系 | R06 "critic" 框架 1 次 | R07 0 命中 (但 Derek + Attia 派继承) | **R07 Norton 角色被 Derek + Attia 替代** |
| 政治化话语 | 0 | Calley Means + Florida medical freedom + "被设计的慢病" | **R07 萌芽: Baker 开始走向反建制医疗政治** |

---

## 5. R07 未发现 / 0 命中

- **GLP-1 / Ozempic / semaglutide / Wegovy / Mounjaro / tirzepatide**: 0 命中 → **R07 Baker 完全未提 GLP-1 类药物** (R08+ 是否会回应 GLP-1 浪潮?)
- **Chaffee**: 0 命中 (R07 Baker 未提 Anthony Chaffee)
- **Cywes / Robert Cywes**: 0 命中 (R07 Baker 未提 Cywes)
- **Layne Norton (单独)**: 0 命中 (R07 Norton 角色被 Derek + Attia 派系整体替代)
- **Malcolm Kendrick / Paul Mason / Liver King / hyperlipid / nadir Ali / Diamond / Peterson / mercola / unwin / ede / lugever / hamza / cordain / sonnemburg / tucker / ray peat / goodrich**: 这些关键词在 R07 未做精确 grep, 但从已读文件看, **Tucker Goodrich (Tucker) 也未在 R07 出现** — R06 的"种子油学术化" 路径在 R07 沉默 (但 anti-nutrient 学术化在 R07 仍继续, 由 oxalates / enzyme inhibitors 接力)
- **Layne Norton / Anthony Chaffee 状态**: R06 Norton 出现 1 次 (critic 框架) → R07 0 命中; Chaffee 整个 R07 未出现 → **R07 Baker 的"对手 / 盟友" 谱完全从 Norton 派转向 Attia 派 + Derek 中介**
- **Revero 早期框架** (R06 "复活" 阶段): R07 Revero 已进入"全国化" 阶段, 早期"个人化" 框架淡出

---

## 6. 我推断 vs Baker 他自己说过的 (明确区分)

### 6.1 Baker 他自己说过的 (高置信, 直接引用)
- Revero 已 "licensed in all 50 states" (20231212003)
- Rogan 节目 11/28 上线后 Revero 增加 2,000 用户 (20231204001)
- Joe Rogan 安排 Baker 在 Austin "Way to Wells" 干细胞诊所治疗 (20231129001)
- Peter Attia 是 Baker 在 R07 公开辩论的对手 (20231121001)
- Dave Feldman + Matt Bootoff + Nick Norwitz 是 LMHR 团队 (20231128002, 20231121001)
- Chris Gardner 收 Beyond Meat 资金 + Stanford 研究被 Game Changers 资助 (20231202003)
- Walter Willett 主持 Harvard Nutrition 25 年 (20231115001, 援引 Teicholz)

### 6.2 我的推断 (明确标注)
- **R07 Revero 从"产品" 到"全国基础设施"**: 基于 50 州许可 + 跨州医师网络 + 2,000 增量用户 + 4 目标人群扩展到 autoimmune/inflammatory 的综合判断
- **R07 Baker 与 Attia 派系公开决裂**: 基于 R01-R06 Attia 0 命中 / R07 单一 1 个视频 11 分钟的强度判断
- **R07 Baker 健康维护从"纯饮食" 到"再生医学"**: 基于 Wharton 凝胶 + BPC-157 + 脐带干细胞的组合判断
- **R07 是 Baker 走向反建制医疗政治的预演**: 基于 Calley Means + Florida medical freedom conference + "被设计的慢病" 暗示
- **R07 Norton 角色被 Attia 派整体替代**: 基于 R06 1 次 → R07 0 命中 + Derek + Attia 出现的判断
- **R07 anti-nutrient 学术化清单从 2 词 → 4 词**: 基于 lectin/phytate → oxalates/enzyme inhibitors 的对比

### 6.3 未发现 (诚实标注)
- **GLP-1 / 减重药**: R07 Baker 0 提及, R08+ 是否跟进?
- **Chaffee**: R07 Baker 0 提及
- **Cywes**: R07 Baker 0 提及
- **R07 Baker 是否接受 statins**: 在 Attia 反驳视频中, Baker 说"a lot of people just don't have a trust for that" + "a lot of people just don't have a trust for" statins — 这是描述其他人, 不是 Baker 自己的立场; **Baker 自己的 statin 立场 R07 未明确表态**
- **Nina Teicholz 文章发表时间 / 期刊**: Baker 引用了 "Newsweek" 报道 (20231115001), 但未明确说 Newsweek 还是其他刊物; **Teicholz 文章具体出处 R07 未确认**
- **Dave Felman vs Dave Feldman**: 字幕里 Baker 写为 "Dave Felman" (20231126003) 但其他处写 "Dave Feldman" (20231128002) — 显然是同一人, 字幕误转

---

## 7. R07 关键发现与 R06 标志对比

- **R06 标志事件**: Baker C6/C7 受伤 + Revero 复活
- **R07 标志事件**: Baker 接受 Austin 干细胞 + Rogan 第 2 次出镜 + Attia 公开辩论 + Stanford Twin 反击 + Revero 全美 50 州许可
- **R07 vs R06 关键差**: 
  - R06 Revero 复活 → R07 Revero 全国化
  - R06 Baker 受伤 → R07 Baker 接受再生医学治疗
  - R06 Attia 0 命中 → R07 Attia 11 分钟视频反驳
  - R06 学术化靠 BMJ + Sweden centenarian → R07 学术化靠揭露具体研究人员 + 资金链 (Gardner + Willett + Game Changers)
  - R06 Norton critic 1 次 → R07 Norton 0 命中 (被 Attia 派系替代)
  - R07 新增: Calley Means + 反建制医疗政治萌芽

---

## 8. R07 历史地位与 R05/R06 对比

- **R05 主题**: Cortisol 反恐慌 + Brian Johnson 反 biomarker + Glyphosate 学术化 + Bagram 创伤 + Revero 隐入背景
- **R06 主题**: Revero 复活 + Baker 自伤 (C6/C7) + keto-carnivore 切换 + Tucker Goodrich 学术化种子油 + Norton 重回框架 + Riley 反主流医生 + Mercola 联盟 + lab meat 全面攻击 + Greger 戏称 + Victoria Farz 案例
- **R07 主题**: Rogan 第 2 次出镜 + Revero 全国化 + Attia 公开对决 + 干细胞治疗 + Stanford Twin 反击 + Calley Means 反建制医疗政治萌芽 + 学术化靠揭露具体研究人员
- **R07 标志事件**: Rogan 第 2 次出镜 (R06 1 次 → R07 第 2 次) + Revero 50 州许可 + Attia 11 分钟视频反驳
- **R07 vs R06 关键差**: R06 Revero 复活 → R07 Revero 全国化; R06 Baker 受伤 → R07 Baker 接受再生医学; R06 学术化靠数据 → R07 学术化靠揭露个人 + 资金链
- **R07 vs R05 关键差**: R05 Revero 沉默 → R07 Revero 全国化; R05 Baker 隐藏个人脆弱 → R07 Baker 公开再生医学; R05 学术化偏 cortisol → R07 学术化偏研究人员 + 资金链
- **我推断**: **R07 是 Baker "carnivore 商业 + 反主流医学 + 再生医学 + 反建制政治" 4 条主线真正合流期** — 比 R06 "个人脆弱 + 商业新周期" 更宽, 更接近 Baker 在 2024-2026 的成熟期形态

---

## 9. 关键时间线锚点 (R07)

- **2023-11-10**: Baker 出发去 Florida "medical freedom" conference, 提到 Calley Means 采访
- **2023-11-15**: Whitney Cummings carnivore 引用 + Harvard Willett 揭露 (Teicholz 文章引用)
- **2023-11-17**: Baker 谈 "Stunning and amazing" — 印度 carnivore 增长 + Lindy 770 lbs → 293 lbs 故事
- **2023-11-21**: **Attia / Derek 反驳视频** + 肩袖损伤 / AGEs 视频 (双发同一天)
- **2023-11-26**: Baker 出发去 Austin Rogan 第 2 次出镜
- **2023-11-28**: Rogan 节目 air + Rogan 评价 + LMHR 团队提及
- **2023-11-29**: Baker 在 Austin 接受 Way to Wells 干细胞治疗 (neonatal stem cells + Wharton jelly + BPC-157)
- **2023-12-02**: Stanford Twin Study 反击 + Crohn's / UC 病案研究征集
- **2023-12-04**: "Super awesome news" — Rogan 效应带来 NCBA 高管联系 Baker
- **2023-12-10**: Anti-nutrient 学术化扩展 (oxalates / enzyme inhibitors)
- **2023-12-12**: Rogan 节目 audio clip — Rivero 50 州许可 + 跨州医师网络公开

---

## 10. R07 重要待办 (R08 应关注)

- **GLP-1 浪潮**: R07 Baker 0 命中 → R08+ 是否会突然回应 Ozempic / Wegovy 浪潮? Baker 的"carnivore 治愈 diabetes" 立场会被 GLP-1 类药物挑战吗?
- **Calley Means / RFK Jr. 联盟**: R07 萌芽 → R08+ Baker 是否会深度进入 MAGA 健康政治?
- **干细胞治疗后续**: R07 Baker 接受治疗 → R08+ Baker 是否会报告疗效? 是否会推广?
- **Attia 回应**: R07 Baker 公开点名为辩论对手 → R08+ Attia 是否会回应?
- **LMHR 研究结果**: R07 Baker 期待 LMHR 研究出结果 → R08+ 该研究是否完成? Baker 如何使用?
- **Stanford Twin 反攻**: R07 Baker 揭露 Gardner → R08+ Gardner 是否回应? Baker 是否升级学术化?
- **Harvard / Willett 持续揭露**: R07 Baker 引用 Teicholz → R08+ Baker 是否与 Teicholz 联合发表?
- **Revero 商业化加速**: R07 Revero 50 州许可 → R08+ 是否进入"百万用户" 阶段?
- **Norton 关系**: R07 0 命中 → R08+ 是否重新出现? Baker 与 Norton 关系最终定型?
- **Chaffee / Cywes / Norwitz 关系演化**: R07 Norwitz 进入, Chaffee / Cywes 0 命中 → R08+ 三个人的关系图谱如何演变?
- **家庭 + 4 个孩子**: R05 提过, R06-R07 0 命中家庭 → R08+ Baker 家庭是否再次出现?
- **Baker 年近 60 + 颈椎恢复**: R07 Baker 公开"接近 60" → R08+ 退休 / 半退休话题是否出现?
- **R07 "barely 100 files" 完成时间点**: 2023-12-14 → 后续 1100+ 文件覆盖到 2026-05, Baker 商业 + 政治 + 健康轨迹将如何演化?

---

**R07 报告完成时间**: 2026-06-05
**调研员**: fuxi-skill Phase 1 Agent 1 (著作维度)
**写入模式**: 追加到 R06 之后
**文件路径**: `${HOME}/Documents/女娲造人/skills/MiniMax-M3-Claude/shawn-baker-md/references/research/01-writings.md`



## 轮 8/17 (2023-12-15 → 2024-01-22)

**素材范围**: `${HOME}/Documents/女娲造人/@ShawnBakerMD/20231215001.md` ~ `20240122003.md` (100 个 .md 文件)
**调研方式**: 关键词 grep + 重点文件 Read
**关键人物/组织（R08 新增/深化）**: Dave Feldman (lipid energy model 学术化主线), Nick Norwitz (Oreo 论文主推手), David Ludwig (Harvard 资深作者), Adrienne Soda / Lisa Jansen / David Ludwig (Kevin Hall 论文再分析团队), Dr. Matt Budoff (LMHR LA 报告), Dr. Isabella Cooper (lean mass hyper-responder 研究), Dr. Fatima Stanford (反方, 减重药倡导者), Dr. Stanford (Stanford 大学), Thomas DeLauer (饱和脂肪 vs 果糖), Lane Norton (回访, Mark Bell podcast), Joe Rogan (第二次直播 Nov 27 提及), Nick Hebert (新 vegan 反对者, 动物灭绝论), Claire Hamlet (vegan activist, 银行撤资), Dr. Linda (Lindy 案例, 52 岁 Australia 减重 500 lb), Dr. Erica Kenney (肯尼亚裔"Rivero"医师), Planet Tracker + Changing Markets (环境活动 NGO), US Dietary Guidelines Panel, Dr. Joe Rogan (11/27 第二次 Rogan Experience #2069)

---

## R08 调研命令一览 (grep + 命中数)

| 关键词 | 命中文件数 | 备注 |
|---|---|---|
| `revero\|rivero` | 6 | Revero 商业化是 R08 绝对主线 |
| `carnivore\|meat\|beef\|steak\|animal.based` | 66 | 主流术语持续主导 |
| `attia\|norwitz\|cywes\|chaffee\|stefansson\|feldman\|budoff` | 5 | 关键人物关系深化 |
| `anti.nutrient\|antinutrient\|lectin\|phytochemical\|oxalate` | 2 | R08 lectin 唯一命中 (20231218003 "Are vegetables poison?") |
| `GLP-?1\|Ozempic\|semaglutide` | 4 | 减重药叙事爆发 |
| `company\|MeatRx\|fundrais\|invest\|commercial\|product\|launch` | 23 | Revero launch 信号反复出现 |

---

## R08 核心发现 (10 条)

### 1. Revero 商业化进入"开放首批患者"阶段 ⭐
**R08 新出现 (但 R07 已铺垫 50 州许可)**
- R08 Revero 候诊名单 ~6,000 人 [20231217004.md 03:35] / [20231223003.md 03:59] / [20240113001.md 08:42] — **数字三处一致，互相印证**。
- "Rivero offers personalized care for metabolic and autoimmune conditions using root cause approach" [20231223003.md 04:05]
- "我们联合医师 / 健康教练 / 跟踪 biomarker 的 app, 治疗 metabolic / inflammatory / autoimmune diseases 根本原因" [20231218002.md 07:55]
- **R08 关键升级 (R07 未见)**: Rivero 在 2024-01-13 **正式开放首批患者下候诊名单申请** ("we are now accepting our first patients off the waiting list... we'll be reaching out to almost everyone on that list to invite them to formally apply") [20240113001.md 08:42-08:55] — **R08 出现商业化"实操阶段"信号**
- **商业模型明确** [20231227002.md 01:43]: "developed a number of deprescription protocols through our company Rivero... physicians in all 50 states" + "health coach + medical supervision + app tracking biomarkers" [20231218002.md 07:55]
- **创始人自我定位** [20231227002.md 02:55]: "actually having a medical education is sometimes an impediment to Healing people... we're not just here complaining about it, I'm actually trying to do something about it"

### 2. Rogan 第二次直播 (JRE #2069, 2023-11-27) — Rogan 与 Baker 关系确认
**R08 出现**
- Baker 11-27 第二次上 Rogan Experience #2069 [20231223003.md 00:05] — 谈 **grass-fed beef 含有 phytochemicals** (Frontiers in Sustainable Food Systems, 2021-02 论文) [20231223003.md 00:24-00:30]
- Rogan 现场以 "你那跟 neutr-tore 的辩论太好笑了" 引述 Baker 的胜利 [20231223003.md 00:42-02:36] — Rogan 对 Baker 的"反 vegan 主张"高度背书
- "United Nations most recently hosted a conference pushing an anti-meat and anti-hunting meatless agenda" [20231223003.md 03:33] — **R08 出现 UN 阴谋论化叙事 (R07 未见)**
- **R08 新论点** (R07 未见): Baker 引入"animal rights = 灭绝主义"框架 (Nick Hebert 辩论) [20231223003.md 02:06-02:20]: "you advocate for displacing the wild world into non-existence... ditch this ball because it's a liability"

### 3. Dave Feldman / Lipid Energy Model 学术化主轴 ⭐
**R08 关系深化 (R07 已铺垫)**
- Baker 完整阐述 lipid energy model [20231222002.md 00:40-00:55]: "as our body has less energy storage particularly glycogen in the liver due to lack of carbohydrates, our liver then attempts to shuttle energy into our body so the cells have energy to use in the form of fats particularly free fatty acids, triglycerides and to include LDL cholesterol which is part of that traffic trafficking process"
- **R08 出现"科学 + 媒体 + 社区"三线并进**:
  - 学术线: Baker 报告 Isabella Cooper PhD 论文 (lean women on keto 重新引入 carb 后 LDL 大幅上升) [20231222002.md 00:31-00:38]
  - 学术线: Baker 报告 Kevin Hall 2021 metabolic ward 论文的再分析, 由 Nick Norwitz / Adrienne Soda / Lisa Jansen / David Ludwig 团队 (Baker 称 David Ludwig "senior author") [20231220005.md 01:14-01:25] — **R08 出现 Ludwig + Soda 合作**
  - 媒体线: Matt Budoff 在 LA 报告 LMHR preliminary 结果 [20231230001.md 00:42-00:50] / [20240122001.md] — "low carb lean otherwise metabolically healthy... cardiovascular disease is not developing"
  - 社区线: Dave Feldman "one of the authors of that particular Le Mass hyperresponders... sort of said hey look this has been edited" [20231230001.md 01:08-01:20] — **Feldman 公开为 Baker 站台对抗 vegan 编辑攻击**
- **R08 关键表态 (R07 谨慎, R08 明显乐观)** [20240113001.md 07:50-08:10]: "having high cholesterol in 2024 there is increasing increasing evidence that that may not be a problem can we say that definitively I don't think we're there yet I think we may get there so I mean you know just just keep watching watching this space I mean some of the work that's coming out will be published this year uh is going to be interesting in that regard"

### 4. Nick Norwitz 关系深化 ⭐ — "Oreo 比 statin 更降 LDL" 论文
**R08 出现 (R07 已铺垫)**
- Baker 报告 Norwitz 的"Oreo 论文" (哈佛 PhD, ulcerative colitis 用 carnivore 缓解) [20240122001.md 00:15-00:43] — **R08 出现 Norwitz 作为"自我实验样本"角色**
- Baker 完整引述 Feldman lipid energy model: "in the low carb State particularly in relatively lean people or people that have lost a lot of weight low carb States lead to decreased liver glycogen... shuttled from the liver in the form of fat... high cholesterol... if I gave myself some more carbohydrate then the liver would no longer need to traffic fat as much and so therefore my cholesterol will come down dramatically" [20240122001.md 00:43-01:05]
- **R08 出现 Rogan 现场引述 lipid energy model 名字** [20231222002.md 02:16]: "Nick norwi a study showing Oreo cookies lower his LDL cholesterol better than statins"
- **R08 出现 Norwitz 在 Kevin Hall 2021 论文再分析中作为作者** [20231220005.md] — Norwitz / Soda / Jansen / Ludwig 团队核心

### 5. Kevin Hall 2021 论文 (Nature Medicine) 再分析 — 学术反攻 Attia 阵营 ⭐
**R08 出现 (R07 Baker 已预告)**
- Norwitz 完整 22 分钟访谈解释再分析 [20231220005.md]: "Kevin Halls group did a study which showed that people going on a lowfat diet and then switching over to a low carb diet you know randomized control trial in a metabolic ward... people eating the lowfat diet ate less calories than the people on the animal-based higher fat diet" — 整段用 "metabolic ward" 强调
- **R08 出现"differential carryover effect"完整论证** [20231220005.md 03:50-04:15]: "low carb first led to metabolic adaptations that led to less energy intake in the following phase versus when you had low fat first there was a major disadvantage and importantly the effect size of the diet order was so massive that it was larger than the effect size of the actual diets themselves"
- Kevin Hall 自己的 preprint 也确认 carryover effect (Norwitz 引用 Hall 自己的 figure 2C) [20231220005.md 09:20-09:30] — "Kevin Hall has a pre-print of his own demonstrating the effect of diet order which is just absolutely Monumental and effectively invalidates the results of the prior trial"
- **C-peptide 数据被用作 carbohydrate insulin model 验证** [20231220005.md 21:30-24:30]: "C peptide to test a prediction of the carbohydrate insulin model does phase one insulin release as measured by C peptide affect energy intake and fat gain in phase two and it absolutely does"
- **R08 出现 "baking a cake" 比喻 (Norwitz Twitter 类比)** [20231220005.md 29:25-29:55]: "of baking a cake and the concept here is it's pretty intrinsically obvious in baking a cake order of events matters"
- **R08 Baker 反思** [20231220005.md 27:40-28:00]: "when you have some BS out there it takes like 10 times the effort to refute it and what you're the concept you're describing is is more complicated for most people to see"

### 6. Layne Norton 二次出现 (饱和脂肪 vs 果糖) — Baker 表面友好, 实质批判 ⭐
**R08 出现 (R07 0 命中, R08 重大变化)**
- Baker 引用 Thomas DeLauer 与 Lane Norton 的对话 [20240103002.md 00:05-00:20] — Norton 主张 **饱和脂肪甚至比糖更促胰岛素抵抗** (引用 fructose 过量增加肝脂肪 20%, saturated fat 过量增加肝脂肪 78%)
- Baker 表面立场: "I'm not saying that people should completely avoid saturated fat I'm just saying saturated fat appears to be somewhat problematic especially if you're overeating it" [20240103002.md 02:25-02:40] — **R08 出现"Baker 公开承认 saturated fat overeating 问题" (R07 未见)**
- **R08 出现 Baker 与 Norton 历史关系** [20240103002.md 02:05]: "in the past I've had you know a quote unquote debate more like a friendly discussion with Lane Norton on the Mark Bell podcast"
- Baker 计划 2024-02 与 Thomas DeLauer 访谈 [20240103002.md 01:54]
- **我推断**: R08 Baker 在 saturated fat / 果糖 / liver fat 议题上正在**主动开放学术对话空间**, 这是对 R07"全面反 saturated fat"立场的微调

### 7. "Statin in the water" 历史回顾 + 学术派系定调
**R08 出现 (Baker 引用 1980s 医学生记忆)**
- "I was a medical student way back in the 19 uh the late 1980s sattin should be in the water right that's wrong in my view" [20231222002.md 04:33-04:40]
- **R08 出现"反一刀切"明确表述** [20231222002.md 04:08-04:15]: "the world's a nail and I got to hammer them... I hit everybody with the same Hammer that is wrong think that is uh you know many many many cases harmful"
- **R08 出现"医生 line up like sheep" 表述** [20231222002.md 04:24-04:27] — 与 R07 的"颠覆医学界"姿态一致

### 8. GLP-1 / Ozempic 减重药深度批判 — 财务化叙事 ⭐
**R08 出现 (R07 未见)**
- Baker 全面攻击 GLP-1 / GIP / 胰高血糖素 [20231217004.md 03:30-03:50]: "these new drugs these gp1 receptor agonists these Gip Inhibitors these glucagon uh mics that are all coming out"
- **R08 出现财务化核心论点** [20231217004.md 04:25-04:35]: "hundreds upon hundreds of billions of dollars if not into the trillions of dollars" — 减重药是"百亿到万亿"市场
- **"慢性药论"** [20231217004.md 04:50-05:00]: "$1,000 a month for some of these drugs... $112,000 a year for the rest of your life let's say you live another 40 years you know how much money is half a million dollars you're giving to these drug companies"
- **指向 Stanford 等机构 + 制药公司利益** [20231217004.md 03:00-03:15]: "Dr Fatima Stanford telling us that obesity has nothing to do with what you eat... oh by the way she's funded by the drug companies that make yeah obesity injection medications"
- **R08 出现"4 大谎言"框架** [20231217004.md]:
  1. "fat is beautiful"
  2. "ultra processed foods are healthy" (USDA Nova 91% 研究)
  3. "food addiction does not exist"
  4. "obesity is a disease there's nothing you can do about it"
- **R08 Rivero 商业化绑定** [20231217004.md 05:33-05:40]: "come check us out at Rivero... step one is get people unaddicted to the processed food that is job number one" — Rivero 被定位为"GLP-1 替代方案"

### 9. 7th World Carnivore Month (2024-01) 启动 — Baker 营销节日化
**R08 出现 (R07 Baker 已预告 1 月启动)**
- Baker 宣布 "tomorrow starts the seventh annual World Carnivore month" [20231231002.md 00:05-00:15] — 7 周年
- "I started seven years ago in response to sort of veganuary which occurs in January" [20231231002.md 00:10-00:15] — 与 veganuary 抗衡
- **R08 出现系统 carnivore 入门指南** [20231231002.md 全文]:
  - 起点: ruminant meat (beef, sheep, elk, deer)
  - 不必 grass-fed, 超市牛肉即可
  - 不必限制 macros
  - 关键: 吃够 (satiation) 消除 cravings
  - fat threshold 概念: 75-100g/餐是常态上限
  - 渲染脂肪 (butter / bacon grease) 比肉内脂肪更易引起消化问题
  - bowel frequency 减少是正常 (肉类近 100% 吸收, 与 fiber 7 次/日 vegan 形成对比)
  - 便秘缓解: 减少 dairy (尤其 cheese 的 casomorphin 效应)
  - 高血压患者需要医生监督 (Baker 直接导流到 Rivero)
  - **2024 预测** [20231227002.md 03:50-04:10]: "cholesterol is going to be found to be a dependent variable necessary but not sufficient to cause cardiovascular disease... yes cholesterol is in that atherosclerotic body but you need more"
- **R08 出现 Rogan 在 Rogan 的引述"7 years ago when I went on Rogan"** [20231230001.md 00:02-00:05] — Baker 7 年前首次上 Rogan 是 2017

### 10. 案例研究: Lindy 52 岁 Australia 减重 500 lb — Revero 营销范本 ⭐
**R08 出现 (R07 未见)**
- "Lydia is a 52-year-old and lives in Melbourne Australia she has one of the most amazing weight loss stories I've ever heard of she's lost almost 500 lb in under two years" [20231218002.md 00:02-00:15]
- 病史: 21 岁胆囊切除, 25 岁 300 lb, 多次减肥失败, 30 岁母亲 + 女儿双病 (肺癌脑转移 + 1 型糖尿病), 2016 年 770 lb, 抑郁自杀倾向
- 尝试: keto (失败) → carnivore (6 个月挣扎) → Rivero 健康教练辅助
- **3 个月说服医生让她尝试** ("just give me three months"), 医生 3 个月后 "we've turned everything around" [20231218002.md 05:56-06:10]
- 结果: 22 个月 -500 lb, 现 293 lb, 所有 blood markers 正常
- **R08 出现 Baker 引用此案例的转化用途** [20231218002.md 07:50-08:10]: "makes me even more excited for the launch of our company Roa we are going to be using a low carb diet combined with medical supervision health coaches app the tracks biomar markers all designed to treat the root cause of metabolic inflammatory and autoimmune diseases"
- **R08 出现 "patient success story" 模式正式化** — Baker 把 1 案例 + 1 商业模式绑定推广

---

## R08 关键引用 (他/她说过的 vs 我推断 vs 未发现)

### 他/她说过的 (直接引述)
- "cholesterol is going to be found to be a dependent variable necessary but not sufficient to cause cardiovascular disease" [20231227002.md 04:01-04:05]
- "this isn't a get out of jail free car for everybody that has high LDL cholesterol but what it is is that if you are lean and metabolically healthy or getting healthier then that r and cholesterol may not be as concerning" [20231222002.md 03:19-03:35]
- "we developed a number of deprescription protocols through our company Rivero" [20231227002.md 01:41-01:50]
- "we are now accepting our first patients off the waiting list there are something like 6,000 people on the waiting list" [20240113001.md 08:43-08:46]
- "$112,000 a year for the rest of your life let's say you live another 40 years you know how much money is half a million dollars you're giving to these drug companies" [20231217004.md 05:18-05:26]

### 我推断的 (基于材料)
- **R08 Revero 完成"从 0 到 1"**: 6,000 候诊名单 + 50 州医师 + 健康教练 + biomarker app + deprescription protocols + 2024-01 开放首批 = **商业化进入实操期**
- **R08 是"Baker + Feldman 联盟"定型期**: Feldman lipid energy model 学术化, Baker 媒体化, Norwitz 自我实验化, 三人形成 carnivore 阵营内部的"学术-媒体-社区"分工
- **R08 出现 Baker 对 saturated fat 立场微调**: 不再"完全无罪", 承认 overeating 是问题 — 这是对 R05-R07 全面饱和脂肪正名的**技术性退让**
- **R08 Baker 对 Rivero 商业化有防御性表述** [20240113001.md 09:20-09:30]: "I thank all each and every one of you that's either invested in Rivero or has signed up as a patient" — 暗示**Rivero 已接受外部投资 + 付费患者**, 不再是 R07 的"即将启动"

### 未发现
- **Peter Attia 在 R08 0 命中** — R07 Baker 已点名, R08 仍未见 Attia 回应或 Baker 再次提及 (我推断: Attia 沉默, Baker 视为胜利)
- **Dr. Robert Cywes / Dr. Anthony Chaffee / Stefansson 在 R08 0 命中** — 三个名字 R07 已 0 命中, R08 仍未浮现
- **Layne Norton 与 Baker 直接对抗** — R08 Baker 表面引用 Norton 数据, 但未点名反驳 (我推断: Baker 选择"学术对话"姿态而非"正面对抗")
- **Malcolm Kendrick / Paul Mason / hyperlipid / Budoff 学术联合** — R08 Budoff 报告 LMHR 出现, 但未形成多作者联合声明
- **"anti-nutrient 学术化"** — R08 lectin 唯一命中是 [20231218003.md] "Are vegetables poison?" 引用 lectin 机制, 但**未上升到学术化"anti-nutrient 矩阵"** 表述 (我推断: Baker 仍以 carnivore 教育为主, 尚未系统化"植物毒素"理论)
- **"GLP-1 与 carnivore 直接对照研究"** — R08 Baker 批判 GLP-1 是商业化批评, 但**未引用任何 Baker 自己或同行做的 carnivore vs GLP-1 头对头研究**

---

## R08 vs R07 演化对比

| 维度 | R07 (2023-11 → 2023-12) | R08 (2023-12-15 → 2024-01-22) |
|---|---|---|
| Revero | 50 州许可, 即将启动 | **6,000 候诊名单 + 开放首批患者申请 + 接受投资** |
| Feldman 关系 | 提及其 lipid energy model | **深度引用, 站台对抗 vegan 编辑攻击** |
| Norwitz 关系 | 进入, 协作初步 | **深度合作 Kevin Hall 再分析论文 + Oreo 论文引述** |
| Kevin Hall 论文 | 预告再分析 | **完整 22 分钟 Norwitz 访谈, carryover effect 论证完成** |
| 减重药 GLP-1 | 0 命中 | **4 大谎言框架 + 财务化批判 + 绑定 Rivero 营销** |
| World Carnivore Month | 预告 2024-01 启动 | **正式第 7 届启动 + 完整 carnivore 入门教学** |
| saturated fat 立场 | 全面正名 | **微调: 承认 overeating 是问题** |
| Norton | 0 命中 | **引用 Norton 数据 + 历史 Mark Bell podcast** |
| Budoff LMHR | 期待中 | **LA 报告已发布, Baker 引述 preliminary 结果** |
| Baker 自我定位 | "我们不再抱怨, 我们建公司" | **"actually having a medical education is sometimes an impediment to Healing people"** |

---

## R08 关键未解之谜 (进入 R09 跟踪)

- **Revero 首批患者数据**: 2024-01 开放 → R09+ Baker 会报告什么疗效数据?
- **Feldman LMHR 完整论文**: R08 Baker 引述 "preliminary results" → R09+ 论文是否正式发表? Baker 引用方式?
- **Kevin Hall 论文再分析 peer review 进展**: R08 Norwitz 报告 preprint → R09+ 是否正式发表 + Kevin Hall 团队回应?
- **GLP-1 vs Rivero 对照**: R08 Baker 把 Rivero 定位为 GLP-1 替代 → R09+ Baker 会否公布 Rivero 患者停 GLP-1 数据?
- **Stanford 反攻升级**: R08 Baker 公开点名 Fatima Stanford → R09+ Stanford 是否回应? Baker 是否升级到"On the Media" 媒体辩论?
- **UN 反肉阴谋论**: R08 Baker 引入 UN 阴谋论化叙事 → R09+ Baker 是否出席 COP/UN 会议挑战?
- **Norton 二次辩论**: R08 Baker 引用 Norton 但未直接对抗 → R09+ Baker 是否会邀请 Norton 上 Baker 频道直接辩论?
- **Baker 颈椎 + 干细胞后续**: R07 预告接受治疗 → R08+ 未见疗效报告 (我推断: 仍在治疗中或效果不显著)
- **Rivero 投资方**: R08 Baker 提"invested in Rivero" → R09+ Baker 是否公开融资轮 + 估值?
- **Thomas DeLauer 访谈 (2024-02 计划)**: R08 Baker 预告 → R09+ Baker 是否完成访谈? 是否会延伸到酮 / carnivore / saturated fat 全面对话?

---

**R08 报告完成时间**: 2026-06-05
**调研员**: fuxi-skill Phase 1 Agent 1 (著作维度)
**写入模式**: 追加到 R07 之后
**文件路径**: `${HOME}/Documents/女娲造人/skills/MiniMax-M3-Claude/shawn-baker-md/references/research/01-writings.md`

## 轮 9/17 (2024-01-22 → 2024-02-25)

**素材范围**: `${HOME}/Documents/女娲造人/@ShawnBakerMD/20240122004.md` ~ `20240225001.md` (100 个 .md 文件)
**调研方式**: 关键词 grep + 重点文件 Read
**核心人物**: Dr. Shawn Baker, MD
**关键人物/组织(R09 新增)**: **Dr. Ben Bikman (Rivero 研究顾问)**, **Dr. Eli Jeruss (Rivero 临床医生, Houston Methodist)**, **John Fetterman (PA 参议员, Baker 注意到他 follow Baker)**, **Dr. G. Davis (vegan doctor, 辩论对手)**, **Dr. Nagra (vegan 医生, 攻击 Baker)**, **Dr. Chaffee (曾与 Nagra 辩论)**, **Tucker Carlson + Calley Means (Baker 引用其揭露制药 + Coca-Cola)**, **Stefan van Vleet (beef phytonutrients 论文)**, **Beth (50 Plus Health and Beauty, 卒中后改饮食)**, **Dr. Michael Greger (NutritionFacts.org, Baker 反复攻击对象)**, **C. Means (前制药 + Coca-Cola lobbyist)**, **John Fedman (Baker 字幕误识 Fetterman)**

---

## 1. R09 调研命令一览 (grep + 命中数)

| 关键词 | 命令 | 命中文件数 | 最高单文件命中 |
|---|---|---|---|
| `revero\|rivero` | `grep -i -l "revero\|rivero" $(ls \| sort \| sed -n '801,900p')` | **3** | 多 |
| `attia\|norwitz\|feldman\|cywes\|chaffee` | `grep -i -l "attia\|norwitz\|feldman\|cywes\|chaffee" $(ls \| sort \| sed -n '801,900p')` | **1** | norwitz 多 |
| `anti.nutrient\|antinutrient\|seed oil\|fiber\|GLP.1\|ozempic` | `grep -i -l "anti.nutrient\|antinutrient\|seed oil\|fiber\|GLP.1\|ozempic" $(ls \| sort \| sed -n '801,900p')` | **6** | fiber 多 |
| `company\|business\|MeatRx\|Meatrx` | `grep -i -l "company\|business\|MeatRx\|Meatrx" $(ls \| sort \| sed -n '801,900p')` | **12** | 多 |
| `kendrick\|mason\|ludwig\|soda\|peterson\|hamza\|ede\|cordain` | `grep -i -l "kendrick\|mason\|ludwig\|soda\|peterson\|hamza\|ede\|cordain" $(ls \| sort \| sed -n '801,900p')` | **17** | 多 |
| `carnivore\|animal.based\|zero.carb` | `grep -i -l "carnivore\|animal.based\|zero.carb" $(ls \| sort \| sed -n '801,900p')` | **30+** | 多 |
| `cancer\|aging\|longevity\|cholesterol\|insulin` | `grep -i -l "cancer\|aging\|longevity\|cholesterol\|insulin" $(ls \| sort \| sed -n '801,900p')` | **27** | 多 |
| `CGM\|continuous glucose\|stool test\|microbiome\|fiber` | `grep -i -l "CGM\|continuous glucose\|stool test\|microbiome\|fiber" $(ls \| sort \| sed -n '801,900p')` | **6** | 20240130004 等 |
| `rivero\|clinic\|telehealth\|app store` | `grep -i -l "rivero\|clinic\|telehealth\|app store" $(ls \| sort \| sed -n '801,900p')` | **8** | 20240128004 多 |

---

## 2. R09 关键发现(5-10 个,标注 R08 延续 vs R09 新增)

### 发现 1: Rivero Clinic 正式启动 + 团队扩展 — 【R09 新增, R08 已预告开张】

**[20240123004.md 00:00:09.559]** Baker 官方公告: Rivero 诊所已开张,"there's 6,000 people on our waiting list", 现在开始接受患者。**关键基础设施**:
- 全 50 州医疗执照
- App Store 已上线 app
- 全 medical clinic(可开药 + 试图 deprescribe)
- **新研究顾问 Professor Ben Bikman** ("human metabolic disease like no one else")
- **每个患者都有资格入组 clinical trial** 测不同饮食对疾病的影响

**[20240128004.md 00:00:38.480]** 第二次人员公告: **Dr. Eli Jeruss** 加入, Houston Methodist Hospital 内科医生, 有 keto/carnivore/low carb 多年经验。

**我推断**: Rivero 团队结构 = Bikman (研究/代谢) + Jeruss (临床/内科) + Baker (商业/协调)。这是 R09 最大组织变化。

---

### 发现 2: Rivero 首批临床研究 — Diabetes 多项 RCT — 【R09 新增】

**[20240125002.md 00:01:02.399]** Baker 宣布 Rivero 已与"funding fundraisers and foundations"达成协议开展 Diabetes 多项研究。"every patient that signs up at Rivero will be eligible to enroll in a clinical trial to look at how these various diets impact disease." 

Baker 原话: "we're going to see the year of the carnivore actually being tested via research by interventional trial which I'm so excited about it's going to be historic I think."

**2024 = Baker 标榜的"year of the carnivore dot"**(Baker 自创语言)。临床试验 = Baker 一直要求的 RCT 证据出现。

---

### 发现 3: Norwitz "Oreo 实验" + Lean Mass Hyper-Responder (LMHR) 完整论证 — 【R08 续 + R09 深化】

**[20240124004.md 00:00:16.520]** Baker 引用 Norwitz "Oreo experiment" 显示 LDL 下降,**作为 lipid energy model 的证据**:"when you are low carb and you're lean your cholesterol will go up and the reason is basically the liver traffics more energy in the form of fat."

**[20240202001.md 00:00:46.080]** Baker 再次展开 LMHR 论证,引用 Usain Bolt 身高类比("打破 6'1" 神话")来解释"lean mass hyper-responder phenomena"。关键论点:
- **Meta-analysis 41 篇论文**显示 LDL 升高的最大驱动是 leanness,而非 saturated fat
- Baker 自报数据: 4-5 inch 腰围差异的 fruit study
- **直接结论**: "the biggest driver of high LDL cholesterol...is how lean they become"
- **关键认知**:**饱和脂肪 effect 很小, leanness effect 最大**

Baker 自言:"I basically postulated this I said what about all the other risk factors" — 暗示他在书中(2021)已预言此结论。

---

### 发现 4: Baker 自我实验 — 90 天 Carnivore + CGM + Stool Test (Viome 风格) — 【R09 新增】

**[20240222002.md 00:00:05.839]** Baker 在 Tend Health 跟科学官开 60 分钟 Zoom, 报告 90 天 carnivore self-experiment 结果:
- Day 1: 多样性 "okay", "below average", 测试建议多吃 fiber / prebiotic / 减少 carnivore
- Baker 反其道而行: 90 天 **full carnivore + keto + 持续 ketosis + 蛋白质 + 脂肪**
- Day 90 结果: **多样性更好, Keystone bacteria 增加**(即"好细菌"提升)
- Baker 结论: "it's not what you think"

**[20240221001.md 00:00:01.560]** Baker 在 Whistler 录视频(在"小 closet condo"里), 引两项研究:
- **A) "Protein gives you heart attacks" 研究** — Baker 批判该研究 baseline 食物是 **Boost 蛋白粉(前两成分: canola oil + high fructose corn syrup)**, Baker 称之为"nasty concoction of sugary oily crap"
- **B) Mendelian randomization 研究** 显示红肉/加工肉"does not cause cardiovascular disease" — Baker 报 zero 媒体覆盖

---

### 发现 5: John Fetterman (PA 参议员) 政治化案例 — 【R09 新增】

**[20240128004.md 00:02:11.360]** Baker 提到 **John Fetterman** (Baker 字幕误识为 "John fedman", 但指 2022 PA 参议员选举 vs Dr. Oz 的人):
- Fetterman 中风, 当时 "processing speaking correctly struggling"
- Baker 注意到 Fetterman 在 X (Twitter) 上 follow 他
- Baker 推断: Fetterman "has started including and started eating more steak and maybe leaning more carnivore"
- 援引 "people who have had strokes and have actually improved significantly by utilizing the nutrition that's found in meat"

**我推断**: Baker 把 Fetterman 当作 meat/carnivore 帮助 stroke recovery 的"活案例", 但 Baker 没有直接证据, 只是 X follow + 公众观察 — 这是 Baker 用 anecdote 当 evidence 的典型模式。

---

### 发现 6: "Phytonutrients in Beef" 学术化 + B12 anti-supplement narrative — 【R09 新增】

**[20240203003.md 00:00:35.759]** Baker 攻击 **Dr. Michael Greger (NutritionFacts.org)** 推荐 B12 补剂给 50+ 老年人:
- Baker 报 **自己 B12 > 1100 pg/mL**(3-4 lb 红肉/天)
- 引用 "Stefan van Vleet" 论文显示 **beef 富含"phytonutrients"**(即"肉中也有植物营养素"概念)
- 主张"basic diet cannot give you the adequate nutrition... that diet is absolutely wrong"
- 同时提 **Tucker Carlson 采访 Calley Means** — 前制药 + Coca-Cola lobbyist 揭露 Health Care 系统

**关键术语诞生**: **"beef phytonutrients"** — Baker 把植物营养学语言挪用给动物产品, 这是 R09 新出现的概念武器(对抗 "plant phytonutrients" 主流叙事)。

---

### 发现 7: Fruit 学术化攻击 — Fatty Liver RCT — 【R09 新增】

**[20240128005.md 00:00:16.279]** Baker 解读 **Scandinavian Journal of Gastroenterology** RCT (80 人, 6 个月):
- 脂肪肝患者分两组: ≥4 份 fruit/天 vs ≤2 份 fruit/天
- 高水果组: 多 4-5 inch 腰围, 显著更高肝酶, 更多 steatosis
- 校正 BMI 和热量后结果不变
- Baker 结论: "people that are insulin resistant metabolically... it may be a bad idea to eat a lot of fruit"
- 自我告诫: "I would like to see this independently reproduced... before I would give too much Credence"

**我推断**: Baker 开始用 RCT 数据(从"anecdote 推动"转向"RCT 引用")反 plant-based。**保留批判距离**(要求 reproduce)显示 Baker 的科学方法在严格化。

---

### 发现 8: Keto + 抗炎 Meta-analysis (44 RCTs) — 【R09 新增】

**[20240129001.md 00:00:10.960]** Baker 引用 large meta-analysis (44 randomized control trials):
- 关键炎症标志物: **IL-6 + TNF-α 都下降**(keto 后)
- CRP 不变
- Baker 自我引述"our clinical experience" — "joints feel less achy, gut seems less inflamed, irritated skin improves"
- Baker 用此论证"keto / carnivore 不仅是 weight loss, 是 inflammation reduction"
- 顺带推广 Rivero:"all of our doctors are on board with this stuff... they study it they live it most of them have lived this example"

**Baker 关键二分法**: "those that have tried carnivore diet and those that remain ignorant and have their often unfounded or basically ignorant criticism."

---

### 发现 9: Dr. Nagra / Dr. G. Davis 双重 Vegan 攻击 — 【R09 新增】

**[20240225001.md 00:00:02.399]** Baker 反击 **Dr. Nagra**(vegan 医生, 此前与 Dr. Chaffee 辩论), 攻击 Baker 与 **Dr. G. Davis**(vegan doctor)的辩论:
- Nagra 引用 Baker 的话:"I don't know if my diet is gonna make somebody live longer... we just don't have the data"
- Nagra 借此攻击 Baker 推荐 diet 但承认不知道长期结果
- Baker 反驳: "I don't think anyone does... I could extend that to really any diet out there... it is the absolute height of arrogance to say that you know beyond a shadow of a doubt"
- **Baker 关键论点**: "a carnivore population a population of meat heavy eaters that do not eat junk food that do not eat significant carbohydrates is a very different population and we have no way of telling what the long term outcomes"
- Baker 建议 cholesterol 高就做 imaging

**[R09 关键位置论]:** Baker 公开声明"我不知道 carnivore 长期结果" — 但同时仍推荐 — 这是 R09 立场演化的关键标注(Baker 立场从"绝对推崇"转向"in select cases 推崇 + 承认长期数据缺")。

---

### 发现 10: 3D Printed Meat + Artificial Meat (Israeli 公司) — 【R09 新增】

**[20240220002.md 00:00:01.959]** Baker 评论 Israeli 科技公司 3D 打印肉技术(从 cow stem cell 培养, 2 分钟打印一个 steak):
- Baker 立场: 整体中立(没明确反对/支持)
- 自带反讽: "营养液 used to grow the stem cells is actually extracted from pregnant cows"(即: 不杀牛? 但还需要 pregnant cow, 实际是 hidden animal product)

**未发现**: Baker 没有深入 anti-3D-meat 的立场表态, 这是 R09 的"未表态区"。

---

## 3. R09 立场演化跟踪

| 立场 | R08 状态 | R09 演化 |
|---|---|---|
| Revero 商业化 | 预告开张 | **已开张 + 6000 候诊 + Bikman + Jeruss 入伙 + 50 州执照 + app 上线** |
| 临床研究态度 | 呼吁 RCT | **Rivero 自身启动 Diabetes 多项 RCT, 自标 2024 "year of the carnivore"** |
| LDL / cholesterol | 防御姿态, 引 Norwitz 初步 | **完整 LMHR 论证 + 41 篇 meta-analysis + "leanness 是最大驱动" + 推荐 imaging** |
| Fiber / 植物营养 | 攻击 plant-based | **推出"beef phytonutrients"概念 + Fruit fatty liver RCT 引用** |
| 抗炎 | 经验性主张 | **44 RCT meta-analysis 引用 (IL-6, TNF-α 下降)** |
| 自我实验 | R07-R08 颈椎干细胞 | **R09 新增: 90 天 carnivore + CGM + stool test, 多样性改善** |
| 长期立场 | 绝对推崇 | **首次公开承认"不知道 carnivore 长期结果"**(R09 重要 softening)|
| 抗 vegan 攻击 | 抗 Norwitz/Stanford | **R09 新增: Nagra + G. Davis + Greger 三角攻击** |
| 自我量化 | 报 B12 > 1100 | 持续报具体数字(B12, 3-4 lb 肉/天)|

---

## 4. R09 关键未解之谜 (进入 R10 跟踪)

- **Rivero 首批患者 outcome data**: 6000 候诊, 已开始 contact, R10 Baker 会否公布首批血糖/体重/medication reduction 数据?
- **Bikman / Jeruss 公开访谈**: R09 Baker 公告二人加入, R10 二人是否上 Baker 频道 / 第三方频道?
- **Bikman 主导的 Diabetes RCT**: R09 Baker 预告, R10 RCT protocol 是否公开? 注册号?
- **Norwitz "Oreo 论文" 期刊版本**: R09 Baker 反复提"number one article in the journal", R10 是否正式 published + 期刊名 + DOI?
- **Mendelian randomization 红肉零覆盖研究**: R09 Baker 提"zero coverage", R10 Baker 会否公布期刊 + 引用以支持论点?
- **"Beef phytonutrients" Stefan van Vleet 论文 ID**: R09 Baker 引用但未给具体 citation, R10 Baker 会否补?
- **Fetterman 是否真 carnivore**: R09 Baker 推断(基于 X follow), R10 Baker 是否会邀请 Fetterman 上频道?
- **Nagra 后续辩论**: R09 Baker 反驳 Nagra, R10 是否有公开 debate?
- **3D 打印肉 Baker 立场**: R09 Baker 表面中立, R10 会不会被 cultured meat 替代议题推到表态?
- **Baker 90 天 carnivore 视频正式版**: R09 Baker 预告"full video will be coming out very soon", R10 是否发布 + 公开 lab data 全部?
- **Fruit fatty liver RCT 复制研究**: R09 Baker 要求 reproduce, R10 Baker 跟踪到 reproduce 论文了吗?
- **Rivero 候诊 6000 vs 实际 onboarding 速度**: R09 Baker 报"a few months"等候, R10 实际数字?

---

**R09 报告完成时间**: 2026-06-05
**调研员**: fuxi-skill Phase 1 Agent 1 (著作维度)
**写入模式**: 追加到 R08 之后
**文件路径**: `${HOME}/Documents/女娲造人/skills/MiniMax-M3-Claude/shawn-baker-md/references/research/01-writings.md`

---

## 轮 10/17 (2024-02-25 → 2024-04-03)

**素材范围**: `${HOME}/Documents/女娲造人/@ShawnBakerMD/20240225002.md` ~ `20240403001.md` (100 个 .md 文件)
**调研方式**: 关键词 grep + 重点文件 Read
**关键人物/组织（R10 新增/深化）**: Muhammad Alo (cardiologist, R10 反复出现), Thomas DeLauer (interviewer, 误读 headline), Dr. Stacy (ADA nutrition director), Arnald of Almaric (13th century Cathar/Crusades 引用), Dave Feldman (lipid energy model, lean mass hyperresponder 引用), Paleo Medicina group (leaky gut 引用), Tim & Shanana Johnson / Cedarview Farms / Better Beef (ribeye 供应商)

---

### 10.1 R10 调研命令一览 (grep + 命中数)

| 关键词 | 命令 | 命中文件数 | 最高单文件命中 |
|---|---|---|---|
| 关键人物合集 | `grep -ciE "bikman\|norwitz\|cywes\|stefansson\|chaffee\|attia\|mercola\|goodrich\|will harris\|hamza\|cordain\|peterson\|tucker\|pat brown\|jeruss\|naiman\|villasenor\|monbiot\|hyman\|malcolm kendrick\|paul mason\|hyperlipid\|nadir ali\|unwin\|ede\|norton\|gardner\|soda\|ludwig\|murphy\|nagra\|alo\|rafi\|amro o'hearn\|keto gains\|steakandbuttergal\|budoff\|feldman\|lugever\|sonnemburg\|ray peat\|liver king"` | **23** | 8 (20240322004) |
| `revero\|rivero` | `grep -ciE "revero\|rivero"` | **9** | 6 (20240330004) |
| `anti.nutrient\|antinutrient\|lectin\|phytate\|oxalate` | `grep -ciE "anti.nutrient\|antinutrient\|lectin\|phytate\|oxalate"` | **1** | 1 (20240308001, "lectins") |
| `attia\|apoB` | `grep -ciE "attia\|apoB"` | **2** | 1 each |
| `GLP-1\|ozempic\|wegovy\|mounjaro\|semaglutide\|tirzepatide` | `grep -ciE "GLP-1\|ozempic\|wegovy\|mounjaro\|semaglutide\|tirzepatide"` | **1** | 1 (20240322004) |

### 10.2 关键发现 (R10, 5-10 个)

1. **Rivero 商业化进入"lifecycle moment"（实质性里程碑）** — Baker 公开宣布公司"starting up"、接待第一批 patients、有 8000 人候诊、licensed in all 50 states、众筹过约 $5M、雇佣"dozens of people"。Baker 明确说"our goal is hey get out of here let's fix you and get the heck out so you don't need to be on these drugs"。"bad business model" 之 self-aware 声明延续 (R09 → R10)。[20240319001.md 00:00:01] + [20240330004.md 00:01:09]
2. **GLP-1 agonist 出现 + Baker 反药品框架** — R10 首次出现"GLP-1 receptor agonist"提法(20240322004)。Baker 明确把牛肉列为"naturally stimulates GLP-1" → "satiety naturally rather than artificially through drugs"，并把"on/off quickly physiologically"对比"drugs stay in your system for days/weeks"。这是 R10 首次明确将 GLP-1 drug 类别(carnivore debate 中新对手)与 natural 肉类 satiety 对立。[20240322004.md 00:04:06]
3. **"Diabetes not just about blood glucose" + saturated fat / ceramide 机制** — Baker 列出"end organ issues"作为真正 concern,引 Inuit 高血糖无 end organ disease + 海豚/猫等 carnivore animals 例外。提到 ceramides + palmitic acid 干扰胰岛素受体。引用 Jeff Volek (R10 中称 "Jeff Fick" 自动字幕误识) 关于"人吃更多饱和脂肪 → 血中饱和脂肪反而少"。R01-R09 几乎未提 ceramides/insulin receptor mechanism, 这是 R10 新 mechanistic 兴趣点。[20240325001.md 00:02:00-00:05:00]
4. **Alo / "drug them all" 出现 + lipid lowering nuance** — Baker 反复点名 Muhammad Alo(已 R02/R05 出现, R10 升级)。R10 出现 2 个新 hit: (a) 20240310004 "Is he crazy or just trolling??" — Alo 说"diabetes has nothing to do with what you eat" → Baker 攻击这是"pharmaceutical Zealot"+"disempowering"。(b) 20240329002 "Drug them all and let God sort it out" — Baker 引用 familial hypercholesterolemia 研究说 40-60% 高 LDL+ApoB 患者"do not seem to be developing atherosclerotic disease", 把 Alo 立场比喻成"kill them all and let God sort it out" (13th century Cathar/Crusades 引用, Arnald of Almaric)。[20240310004.md 00:00:09-00:01:00] + [20240329002.md 00:00:09-00:03:00]
5. **Baker 99% carnivore softening + fruit 实验后保持 carnivore** — R10 出现 1 个 fruit 实验视频(20240318002 "Eating all the fruits!")。Baker 说他 6 周前加 100g 苹果/天持续约 1 周 → "minimal to no impact on my cholesterol", 主因是当时他处于 bulking phase 不是 energy-depleted 状态 + 100g 对他体重(260 lb)剂量不够。明确说"99% carnivore", 偶尔 birthday cake, "I am pretty much 99% carnivore"。明确说被批评"for saying I don't know with 100% certainty if carnivore will make you live longer"。延续 R09 softening + 新增"承认 longevity 不可 100% claim"立场。[20240318002.md 00:00:02-00:04:20]
6. **Cholesterol nuance + Denmark CAC zero study** — Baker 列 4 个 "crazy facts": (1) 婴儿母乳喂养 → cholesterol 升到 205 mg/dL, "危险"; (2) dementia 患者停 statin → 认知改善, 复吃 → 又降; (3) 12.8M 人 study, cholesterol 210-240 关联最高 longevity; (4) 总 chol 1950s 至今降 20 点 + smoking 减半 + CVD 仍 #1 killer。引 Denmark CAC=0 study: LDL 对 progression 无影响, 真正 predictor 是 diabetes + smoking。引 SGLT2 inhibitor: 降 glucose + 升 LDL 但降 CVD risk。**R10 升级胆固醇到"blanket drug everybody"反对立场 + 提 Dave Feldman "lipid energy model" + "lean mass hyperresponder data"作为 framing tool**(R10 第一次明确为 Dave Feldman 模型背书)。[20240305003.md 00:00:02-00:05:55]
7. **Microplastics + leaky gut + carnivore 解决"leaky gut"** — R10 首提 microplastics 与 cardiovascular disease 关联(20240308001)。Baker 引"2024 新研究": carotid artery plaque 中 microplastics 越多 → CVD 风险越高。提到"71% 塑料仍漂浮"+"leaky gut 让 microplastics 更容易入血"。**关键**: 引用"the Paleo medicina group... via PEG 400... has shown that pretty much resolves [leaky gut] in many cases" — 这是 R10 首次明确给 Paleo Medicina 匈牙利诊所 credit + 引用其 leaky gut 测量方法。R10 也把"gluten, lectins, sugars, processed foods"列为 leaky gut 加重因素 (R01-R09 lectin/phytate 是讨论焦点但未与 leaky gut 机制直接挂钩)。[20240308001.md 00:00:01-00:03:30]
8. **R10 商业化叙事: Rivero 与 allopathic system 对立** — Baker 提"drug them all"模式 + "you just want your pills" + "alpath system"。预测 10-15 年内 AI + pharmaceutical companies 将"automate"医生决策, Baker 说"it's great for the pharmaceutical companies"+"you want to invest in something like that"。明确宣战: 多数医师是"alpath system"中"symptom management here's the next drug add infinitum"循环中。R10 仍延续 R08/R09 商业化叙事但更自信(实际启动 + 第一批 patients)。[20240330004.md 00:01:45-00:03:50] + [20240319002.md 00:00:01-00:03:30]
9. **"Empowerment / disempowerment" 中心概念 (R10 反复)** — Baker 在 [20240301002.md] "Perhaps the most important topic" + [20240319001.md] "Today is an incredibly important day" + [20240327001.md] "When is disease a good thing" + [20240319002.md] "Let's talk inflammation" 均以 empowerment/disempowerment 为核心 framing。Baker 论点: 主流医学 disempowers 患者(因: 不知病因 + 永远药物依赖); Rivero empowers 患者(因: 找到 root cause + 治愈 → 离开)。R10 这条线比 R08/R09 更中心化, 接近"secular gospel" 强度。**这是 R10 新升级的 rhetorical framework**(R01-R07 也有 empowerment 但 R10 提升到主要 framing)。
10. **Regenerative agriculture + Will Harris 风格延续** — R10 出现 1 个 livestock farmer 视频(20240312002), Baker 转推 farmer 反驳记者的"cow 消耗 10 bathtubs 水"叙事。farmer 论点: "regenerative agriculture... single best way to sequester carbon from the atmosphere into the soil"+"70% of earth's land is not suitable for tillage... just grassland"+"cattle can be a tool to heal that"。Baker 仍延续 R02 起的"零碳农业 / cattle = 碳汇"框架。 [20240312002.md 00:00:01-00:01:50]

### 10.3 关键术语 (R10 新出现 vs 延续)

| 术语/概念 | R10 状态 | 备注 |
|---|---|---|
| `Rivero` | **深化** | 从 R07 概念 → R10 实际启动 + 8000 候诊 + licensed 50 states + $5M 众筹 |
| `GLP-1 agonist` | **R10 新出现** | Ozempic 等药物与 natural meat satiety 对立 |
| `ceramide` / `palmitic acid` / `insulin receptor interference` | **R10 新出现** | diabetes mechanism 新兴趣点 |
| `lipid energy model` / `lean mass hyperresponder` | **R10 强化** | 第一次明确给 Dave Feldman 框架背书 |
| `Familial hypercholesterolemia` | **R10 新出现** | 用 FH 反驳 "blanket drug all" |
| `SGLT2 inhibitor` | **R10 新出现** | 用"降 glucose + 升 LDL + 降 CVD"反驳 LDL-centric |
| `Microplastics` | **R10 新出现** | 首次系统谈环境毒素 + leaky gut 关联 |
| `Paleo Medicina` (匈牙利诊所) | **R10 新出现** | leaky gut PEG 400 引用 |
| `Empowerment vs Disempowerment` | **R10 强化** | 中心 rhetorical framework |
| `Crusades / Cathar / Arnald of Almaric` | **R10 新出现** | 历史典故包装 cholesterol 辩论 |
| `Inuit high blood glucose` | **R10 新出现** | "高血糖 ≠ 病"历史人类学论证 |
| `Dolphins / cats (carnivorous animals) higher blood glucose` | **R10 新出现** | 跨物种 carnivore 论证 |
| `99% carnivore` | **R10 新出现** | softening 具体数字 |
| `bulk up phase / 260 lbs / 6 weeks steak and eggs` | **R10 新出现** | Baker 自身当下 bio state |
| `birthday cake` (偶尔 cheat) | **R10 出现** | softening 具体表现 |
| `continuous insulin / cholesterol monitors` | **R10 新出现** | 未来工具想象 |
| `O'Hearn / Norwitz / Chaffee / Attia / Bikman / Cywes` | **0 命中** | R10 全部未提 (延续 R07-R09 silence 趋势) |
| `Stefansson` | **0 命中** | R10 仍未出现 (与 R08 一致) |
| `Nagra` | **0 命中** | R09 公开辩论后 R10 沉默 |
| `Revero` (正确拼写) | **未发现** | Baker R10 全部说 "Rivero" (可能公司真名是 Rivero 而非 Revero) |

### 10.4 立场演化 (R10 vs R01-R09)

1. **softening 节奏**: R07/R08/R09 缓慢 softening (steak butter gal 70% / R09 "I'm not a purist") → R10 出现具体数字 "99% carnivore"+"birthday cake cheat"+"6 weeks steak and eggs"+"I don't know with 100% certainty if carnivore will make you live longer"。softening 已从隐含变为显性立场声明。
2. **cholesterol 立场**: R01-R07 一般化"cholesterol hypothesis 错了" → R08/R09 引 Dave Feldman → R10 明确为 "lipid energy model" + "lean mass hyperresponder data" 背书 + 引 SGLT2 inhibitor + 引 Denmark CAC=0 study 反对"blanket drug everybody"。立场从"反 cholesterol"精细化到"反 LDL-centric pharmacy"。
3. **商业化**: R07 概念 → R08/R09 招募 → R10 实质性 milestone: 第一批 patients + 8000 候诊 + 50 州 licensed + $5M 众筹 + Rivero 框架作为反 allopathic system 的具象化。
4. **"disempowerment" 修辞**: R01-R07 偶有 → R10 提升为 4-5 个 video 的中心 framing。R10 视频标题含 "important" / "incredibly important" / "important topic" 至少 3 次(20240301002 / 20240319001 / 20240330004)。
5. **Anti-Alo 升级**: R02/R05 偶提 → R10 两个 video 集中攻击(20240310004 + 20240329002), 历史典故 (Crusades/Cathar) + FH 论文 + lipid energy model 三层论证。

### 10.5 R10 未发现 (negative findings)

- **Attia 在 R10**: 0 命中 (Baker 没有 2024 Q1 直接回应 Attia 的 ApoB 立场)。R09 提到 Attia → R10 完全沉默。这可能意味着 Baker 不再需要点名 Attia 来反对 (R10 论证已 independent)。
- **Norwitz / Chaffee / Bikman / Cywes / Stefansson / Mercola / Hamza / Cordain / Sonneburg / Goodrich / Will Harris / Tucker / Pat Brown / Naiman / Jeruss / Peterson / Amro O'Hearn / Ludwig / Norton / Gardner / Feldman (除 lipid energy model 概念引用外, 没点名人)**: R10 全部 0 命中。R10 人物圈显著比 R01-R09 收缩。Baker 几乎完全 self-referential + 引用 historical/farmer/ADA/医生对手, 不再积极引用"allies"网络。
- **Nagra 公开辩论后续**: R09 Baker 反驳 → R10 0 命中 (沉默)。
- **GLP-1 drug 政策细节 / Wegovy / Mounjaro / Tirzepatide**: R10 仅 1 命中 (Baker 反对 framing), 未展开。
- **"Revero" 拼写**: 0 命中 (R10 一律说 "Rivero")。**这可能意味着 R01-R09 的"Revero"是 OCR/转录错误, Baker 实际公司名是 Rivero** — 这是 R10 的关键 negative finding, 需要在 SKILL.md 中确认公司名拼写。

### 10.6 R11 跟踪点 (待 R11 验证)

- **"Rivero" vs "Revero" 拼写**: R10 全部 Rivero 命中, 0 Revero 命中 → 公司名确认?
- **Rivero 候诊 8000 → R11 onboarding 数字**: 增长曲线
- **GLP-1 / Ozempic 系列是否在 R11 展开**: Baker 反对框架已立, R11 会否推专题?
- **Alo 冲突是否升级**: R10 集中攻击 → R11 Baker 会否做完整 debate video?
- **Paleo Medicina 引用是否深化**: 首次引用 → R11 Baker 会不会邀请 Dr. Zsofia Clemens / Csaba Tóth 上频道?
- **"99% carnivore" + 偶尔 birthday cake**: 后续 R11 Baker 自我报告是否继续 cheating?
- **fruit 实验后续**: 100g 苹果无影响 → R11 Baker 会不会做更大剂量 / 更长周期 fruit 实验?
- **"continuous insulin/cholesterol monitor" 展望**: R10 预测 → R11 Baker 会不会跟具体公司(如 Levels, Dexcom)合作?
- **microplastics 议题展开**: 2024 新研究 → R11 Baker 会不会做系列?
- **Rivero clinician 团队规模**: "dozens" → R11 实际增长?

---

---

## 轮 11/17 (2024-04-03 → 2024-05-10)

**素材范围**: `${HOME}/Documents/女娲造人/@ShawnBakerMD/20240403002.md` ~ `20240510001.md` (100 个 .md 文件)
**调研方式**: 多关键词 grep + 重点文件 Read (每个文件最多 1 次)
**时间特征**: 2024-04-03 → 2024-05-10 (5 周 1 天, 100 个文件) - 这是 Baker 频道**密度最高**的一段时期 (R10 是 8 周 100 个文件, R11 是 5 周 100 个),说明 Baker 加大内容输出

### Grep 命令 + 命中数 (部分)

```
grep -iE 'carnivore|meat|beef|steak|animal.based' (100 files)  →  100/100 全文件命中
grep -iE 'rivero|company|GLP-1|Ozempic|empower'  →  12 files
grep -iE 'cholesterol|insulin|keto|plant|seed oil|fiber|vegan|cancer|aging|longevity'  →  60+ files
grep -iE 'norwitz|chaffee|attia|mercola|unwin|ede|hamza|cordain|bikman|jeruss|naiman|cywes|stefansson|tucker|goodrich|will harris|budoff|fetterman|huberman|karp|food babe|delauer|paleo medicina|maha'  →  11 files
grep -iE 'MAHA|make america|rfk|kennedy|robert f'  →  1 file (20240404001.md, Kennedy 出现)
grep -iE 'attia|norwitz|bikman|chaffee|cywes'  →  0 files (R11 这 5 个名字一个都没提)
grep -iE 'anti.?nutrient|phytate|oxalate|lectin'  →  0 files (无 phytate/oxalate/lectin 直接命中, 但 gluten/gliadin 出现)
grep -iE '99% carnivore|cheese|dairy'  →  多文件 (dairy 一直)
```

### 11.1 R11 核心发现 (按重要性排序)

#### 发现 1: 重大新组织 - "American Diabetes Society" (R11 新)
**`[20240422003.md 00:04:28]`**: Baker 在与 Dr. Ken Berry 的 Live 公开宣布,Ken Berry 和 "some other low car people" 正在组建一个叫 **"American Diabetes Society"** 的新组织,**明确作为 American Diabetes Association (ADA) 的"counter"**。
- Baker 原话: "they he and some other low car people are forming something called the American Diabetes Society which is kind of a counter to the American Diabetes Association"
- 直接批评 ADA: "the advice they're giving is at best suboptimal and in fact in some cases maybe even harmful for a lot of diabetics"
- 关键论点: "the fact that they don't emphasize nutrition particularly **low carbon nutrition** is is in my view quite shameful" (注意 Baker 用了"low carbon"而非"low carb",**这是 R10 之后术语迁移的延续** - 从"low carb"→"low carbon"是为了避开 keto 反对派的"ketones 损伤"框架)
- 标记: **R11 重大新事件**,需 R12 跟踪: American Diabetes Society 实际成立时间,创始成员名单,Baker 是否参与,首个官方立场文件

#### 发现 2: Rivero 商业化方法论深化 (R10 → R11 延续)
**`[20240417002.md 00:03:44-00:03:56]`** ("I was a crime victim!!"): Baker 说 "even if you're sick even if you're diseased um you know utilize Rivero to get off to to get fixed get get healthy" + "as I think about Rivero as a mechanism to get people healthy I mean we don't want them [on medications long-term]"

**`[20240418004.md 00:01:07]`** (NYT 采访后): "my hope is you know we talk a little bit about Rivero and some of the other things and uh the sort of the origin of the carnivore diet"

**`[20240418005.md 00:00:55-00:01:31]`** (Autoimmune disorders 短片): **关键新信息** - "what one of the things we do at Rivero is we help to identify those causes and eliminate eliminate them per uh individual condition and that way we have a very personalized approach" + "we do at Rivera [Rivero] we'll be **collecting data** on these types of things figuring out what foods differentially affect which people and which condition"
- **意义**: Rivero 正在从"健康诊所"演化为"**数据收集公司**" - Baker 第一次公开说 Rivero 在**系统化收集 patient-level food → autoimmune response 数据**。这是**反主流医学(individualized nutrition)研究方法论的具象化**

**`[20240419002.md 00:05:19]`** ("NO ONE is coming to save you!"): "and my goal is for our Rivero patients to figure out how to get healthy"

**`[20240422003.md 00:03:27-00:05:09]`** (Ken Berry Live 后续): Baker 详细说 "we talked you know a little bit about Rivero and of course [Ken] announced that they he and some other low car people are forming something called the American Diabetes Society" - Baker 在公开场合把 Rivero 跟 Berry 的"low carb people network"放在同一句话,**说明 Rivero 是这个网络的一部分,而不是独立公司**

**`[20240418005.md 00:01:42]`**: "want to find out more check out **rivera.com**" - 注意这里又写成了 "rivera.com",**Rivero 拼写在 R11 仍不稳定**(R10 跟踪点未解决)

#### 发现 3: 立场演化 - "无 99% carnivore" + Dairy 持续松绑 (R10 → R11 延续)
**`[20240420002.md 00:00:03-00:00:33]`** (cheese ball 慢炖菜食谱): Baker 在 crock pot 里放 "cheese balls... a block of montere jack cheese... sharp cheddar cheese... pasta and now I'm going to put some pasta water into my cheese"
- 整个 R11 期间 Baker 公开食谱出现大量 **dairy (cheese) + pasta** 组合
- 标记: **R10 跟踪点 "99% carnivore" softening 继续延续**,但 Baker 没有在 R11 任何 video 公开承认"我现在不是 100% carnivore" - 沉默式松绑

**`[20240428002.md 00:00:07]`**: "my first meal was... salmon smoked salmon feted cheese and some PRS it was back day obviously salt" - PRS = Pork Rind Snack,典型 carnivore snack + cheese

**`[20240509002.md 00:01:05-00:01:27]`** (Whole30 餐厅 review): Baker 在 Whole30 餐厅点 "ham and cheese s [sandwich]... some chicken tenders and some fries I had Ranch and barbecue which was so amazing"
- 关键: Baker 在 Whole30 餐厅吃 **fries + ranch** (ranch dressing 含 dairy) - 这是公开承认在"healthy Whole30 框架"下他不再严格 carnivore

**`[20240502003.md 00:00:02-00:00:53]`** & **`[20240509005.md 00:00:08-00:00:16]`** & **`[20240509003.md 00:00:21-00:00:26]`**: 整个 R11 出现 **多个"Tomahawk ribeye"** butcher 教学视频(2024-05-02, 05-09 多次重复主题),**反映 Baker 的"商品化肉食美学"**持续输出

#### 发现 4: anti-nutrient 学术化 - "molecular mimicry" + "leaky gut" 机制 (R10 → R11 深化)
**`[20240418005.md]`** (Autoimmune 视频): Baker 完整使用学术术语:
- "molecular mimicry" - "a foreign compound is seen as a similar uh substance uh in the body and the immune system sort of now recognizes normal as foreign and then therefore it attacks it"
- "gadin [gliadin] and part of the gluten family damages the gut"
- "it's been pretty well accepted that things like leadin [lectin] can can lead to gut damage but what we are finding out is that more and more actual potential food substance can do the similar thing"
- 直接结论: "as we restore our gut integrity and so many people particularly those doing a carnivore diet or similar diet have seen dramatic reductions in their symptoms and sometimes even reversal of the disease completely"
- **意义**: Baker 第一次在视频中**系统化使用"molecular mimicry"这个免疫学术语**,而且把它和 lectin 合并论述,**这是 anti-nutrient 叙事的学术化升级**

**`[20240422001.md 00:00:15]`**: "completely for 4 weeks in a row 28 days then on day 29 eat a lot of gluten have pancakes for breakfast have a sandwich" - Baker 在描述 28 天 elimination diet protocol,典型功能医学框架

**`[20240429001.md]`** (How wheat and gluten impact our gut): **重要论文引用视频**
- 引用 "review article on how wheat and various proteins in wheat such as gadin [gliadin] uh gluten and wheat germ a glutenin [glutenin] impact our gut barrier"
- 描述: "disruption of the so-called junctional barrier between the cells uh resulting in high levels of Z [zonulin] and that is postulated to be strongly associated with inflammatory conditions and autoimmune conditions"
- 引用"animal model study showing how processed foods do the same thing they disrupt the gut bear [barrier] and lead to chronic kidney disease"
- 关键结论: "no amount of supplements no amount of drugs no amount of Lifestyles or biohacking inter vention is going to work if you do not stop poisoning yourself"
- **意义**: Baker 引用了 **zonulin**(一个 Alessio Fasano 提出的学术概念),**这是他从 Carnivore 圈拉拢功能医学(functional medicine)圈的具体动作**

#### 发现 5: cholesterol / seed oil 学术化反攻 (R10 → R11 深化)
**`[20240430001.md]`** ("The largest randomized control trial on the diet heart hypothesis!!"): Baker 详细解读 **Minnesota Coronary Survey** (Ramsay 等 1973 完成,1989 默默发表)
- 9,000 men/women,4.5 年,干预组 seed oil + low-fat vs 对照组 traditional American food (含 18% 饱和脂肪)
- 结论: "absolutely no differences between the two groups for cardiovascular events cardiovascular deaths or total mortality"
- **关键指控**: "this study was completed in 1973 but it wasn't published until **16 years later** in a relatively unknown medical journal where the authors knew nobody would find it so they just hid it"
- "one thing that they noted was that cancer was a lot higher in the lowfat group"
- 标记: **R11 Baker 公开"conspiracy theory"模式** - 指控 dietary guidelines 制定者**故意隐藏反证证据**。这是反 mainstream nutrition 的**核心叙事**:Guidelines 是 industry-corrupted,Minnesota 是 suppressed evidence

**`[20240411003.md 00:00:03-00:00:51]`** (42% of all Americans are this...): 
- "42% of Americans are obese another almost equally large percentage are overweight at least a third are in the early or later stages of diabetes"
- 引用 PURE study 140,000 individuals from 18 countries: "higher carbohydrate intake **not meat and fat** note was associated with an increased risk of total mortality and that quote higher saturated fat intake was associated with **lower risk of stroke**"
- 讽刺: "The Beneficial centralizing agents who task themselves with determining what we as Sovereign and responsible individuals should put in our mouths" - "Sovereign" 是关键术语,反映 Baker 的**libertarian 政治底色**

#### 发现 6: 健康主义-libertarian 框架强化 (R10 → R11 延续)
**`[20240404001.md 00:00:39-00:04:49]`** (选举 + 健康主义): Baker 提到 "Donald Trump Joe Biden maybe perhaps **Robert F Kennedy** Jill Stein or something like that" + "you can see guys like Robert F Kennedy talking about the food supply"
- 这是 **RFK Jr. 第一次在 R11 出现** - 当时 RFK 还在 Independent 候选人阶段(后 2024-08 退出支持 Trump),Baker 已经在公开评论 RFK
- 整段视频核心: "the more important votes are not that... what I'm talking about is who you vote for every single day by the decisions you make" + "our company is not so much a Dem democracy or or you know a republic uh as so much as a **corporatocracy**" + "we vote for them by giving our money"
- 标记: **R11 Baker 公开 corporatocracy 阴谋论 + 投票=消费主义 = 食品政治学**

**`[20240419002.md 00:00:02-00:00:30]`** ("NO ONE is coming to save you!"): 衬衫印 "no one's coming to save you" - 解释 "has to do with you know government's not going to do anything for it you know one politician is not going to do anything realistically for you you got you know you basically got to do it yourself"
- 这是 Baker 的 **核心个人责任哲学** 的明示化
- 案例: 40 岁 founder of a company 案例 - "had a CAC score showed that he had uh some level of heart disease" + "you know Bill Gates you know one of the richest men on the planet and I would I would suspect that he doesn't feel very good I mean you know with that sort of uh sort of body habitus the joints are aching he's got digestive issues probably has uh erectile dysfunction probably has some leg of cognitive issues"
- **R11 第一次公开攻击 Bill Gates**(在 R10 中 Alo 是主要目标,Gates 是新加入)

**`[20240427001.md 00:00:03-00:00:48]`** (77% military fail): Baker 引用 "77% of US 17 to 24 year olds could not join the military" - "due mostly to obesity drug abuse physical health or mental health"
- "we're going to lose to everybody if this trend continues we just can't we can't win Wars with the bodies that we have right when you look at Society at large right now that they're obese their **gelatinous Blobs of broken Minds** um they don't know if they're a boy or a girl they definitely have never jumped out of a tree before"
- "this generation has done that so they're just weaker in every form of the word"
- **意义**: 这是 Baker 第一次明确**把肉食/营养政治和 military readiness 绑定** - 反映 **MAHA(Make America Healthy Again) 阵营思路的预演**(MAHA 是 2024 下半年才正式形成的政治运动,RFK 2024-11 被 Trump 提名 HHS Secretary 后才广为人知)
- 同时**第一次公开跨性别话题**("don't know if they're a boy or a girl") - Baker 频道 audience 已经开始接触文化战争(culture war)话题

#### 发现 7: 2024 NYT 采访事件 (R11 重大新闻事件)
**`[20240418004.md]`** ("Is the New York Times story on carnivore going to be a hit piece e??"): Baker 公开了 **NYT 正在做 carnivore lifestyle piece** 的事实
- Baker 描述采访: "I just got done doing an interview with someone from The New York Times wanting to do a lifestyle piece uh on the carnivore diet"
- Baker 的 PR 策略: "I try to be as open and honest as I possibly can I try to uh downplay the sensationalism of the carnival dime and talk about the real science"
- Baker 的论证: "we do that with pretty much every drug that is on the market every new drug that's been on the market we have no idea what the truly long-term outcomes of many of those drugs are going to be and yet we prescribe them anyway as a therapeutic tool which I feel uh is certainly a Justified way to you utilize a car over dot you this shirt doctor's orders"
- 预期: "all publicity is is effectively good publicity you know I mean uh you know it's getting the word out and the New York Times is obviously a big Outlet"
- 历史类比: 之前 Outside magazine 做过 carnivore story - "the guy did the carnivore diet you know we had three or four little phone conversations and he actually did really good he was really happy but the editor kind of made him say that it wasn't that good for some some weird reason"
- 标记: **R11 重大 media 事件** - NYT 是 mainstream media 风向标。需 R12 跟踪: NYT 文章实际发表时间、内容倾向、对 carnivore movement 影响

#### 发现 8: Regenerative agriculture 商业合作 (R10 → R11 新案例)
**`[20240426001.md]`** (Popular vegan restaurant is now selling THIS!!): Baker 采访 "Chef Molly" - 一位"lifetime vegan"如何把 Sage a plant-based beastro and Brewery 改成 **Sage a regenerative kitchen and Brewery**,2024-05-29 上线新菜单
- Chef Molly 原话: "I believe that regenerative agriculture is the best path forward and as a lifetime vegan it was really hard pill to swallow when I realized that what I had been promoting and committed to for all these years was not the best path forward it was a path forward but the reality of regenerative agriculture and how hooved animals on grass can make a profound difference"
- Baker 卖点: "better for your health better for the environment and better for the animals"
- **意义**: Baker 第一次展示**"lifetime vegan → regenerative omnivore"** 的 conversion story,**这个 narrative 是 R10 后 Baker 的新核心 messaging**:"再生农业+有蹄动物+草饲=健康+环境+动物"三赢
- 餐厅上新菜单: 2024-05-29 (R12 跟踪点 - Baker 是否会去现场)

**`[20240408003.md 00:00:04-00:00:27]`** (How are cows unsustainable again?): 
- "one cow produces over 550 lb of beef 30 lb of organs and 100 lb of fet [fat]"
- "over 1 million extremely nutritious calories meaning it can feed a family of four for over a year"
- "milk leather glue mooing that regenerates the soil and pulls carbon out of the atmosphere and even grows shrooms"
- **意义**: 1 头牛 = 1 个家庭 4 人 1 年 = 100 万卡路里。**Baker 在 R11 进一步简化反 anti-meat 环境论**

**`[20240508002.md 00:00:12-00:00:15]`**: 餐厅 review 提到 "everything here is regeneratively farmed"

#### 发现 9: Baker 个人 fitness 计划首次公开 (R11 新)
**`[20240417002.md 00:01:18-00:03:30]`** (I was a crime victim): Baker 公开个人 fitness goals:
- "I'm 57 57 is 57 and a half" - **R11 Baker 第一次明确披露年龄 57.5 岁**
- "a routine that I'm starting to develop which I think is going to provide tremendous dividend"
- "as I get older and that that happens to all of us one of the most common things we lose is the ability to sort of be explosive to be bouncy to jump and so I'm uh actively and and very methodically pursuing that"
- **关键 fitness goals**:
  - "being able to get a 400 meter dash under 60 seconds" 
  - "100 met [meter] under 13 seconds which is a which is a big ass and I think the 100 is going to be the hardest to be honest"
- 体重: "I'm currently weigh in this morning right at 260 lbs I'll probably have to get down to probably 240 maybe even sub 240"
- 习惯: "this morning I went out to the garage and just hopped around you know two- footed one footed progressively you know very very short small amplitude jumps"
- 目标: "30 40 years maybe longer God willing to enjoy life"
- **意义**: Baker 在 R11 第一次**把自己定位为"fitness/longevity content creator"**,不再是 pure 营养频道。这是**角色扩张**,R12 跟踪:Baker 400m 实际成绩,sub-240 体重目标,是否引入运动科学专家

#### 发现 10: AI 取代医生叙事 (R11 新)
**`[20240422003.md 00:01:42-00:02:35]`** (Ken Berry Live): Baker 详细描述 AI 取代医生图景:
- "we will see a large percentage of your day-to-day Physicians and health care providers being replaced with AI because AI quite honestly is **better at diagnosis** than than many Physicians are and will be certainly in the next coming few years"
- "some way to maybe take a little blood sample maybe a finger prick that can be analyzed very rapidly and you know diagnosis made and maybe pills brought by an Amazon drone dropped off at your door within a few hours"
- "make the pharmaceutical companies very happy because you know they don't have to pay these damn phys they don't have to **bribe positions [physicians]** anymore to to to to Hawk their uh their pills I mean they don't have to you know take them to fancy conferences and bring their office staff all these lunch free lunches"
- 患者评价错位: "rate your doctor... a lot of the ratings are my doctor always pres refills my prescription on time it's very easy to get refills that's their metric by which they think a good doctor is and some cases whereas you know you should be thinking about well maybe the metric should be my doctor got me off the damn drugs and fixed me"
- **意义**: Baker 第一次**系统化描绘 AI 医疗未来** - 这个 narrative 跟 Rivero 的"healthcare alternative"主张形成"two-track future" - 一边是 AI + pharma(坏未来),一边是 Rivero 式的 nutrition-first(好未来)。需 R12 跟踪: Baker 是否真的投资/参与 AI diagnostics 公司

### 11.2 R11 关注点 vs 未发现

#### 我推断的内容(注意:这不代表 Baker 直接说过)
- **GLP-1 / Ozempic 系列**: 整个 R11 Baker 没有提 Ozempic 或 GLP-1(0 命中)。R10 反对框架已建立,R11 反而沉默。**推测**: Baker 可能在等更多 GLP-1 长期副作用数据出炉,或者 Rivero 把"不用 Ozempic 也能减肥"作为 patient story
- **Attia / Norwitz / Bikman / Chaffee / Cywes / Stefansson**: **R11 0 命中**。R10 至少还有 Norwitz/Bikman/Attia 提及,R11 完全消失。**推测**: Baker 转向跟 Berry 等更亲密的"old guard keto"盟友,跟年轻 MD/PhD 派(Attia/Norwitz/Bikman)暂时疏远。**重要: R12 应验证这个 distancing 是否长期化**
- **Paleo Medicina**: 0 命中。R10 首次引用后 R11 没有跟进
- **MAHA 正式术语**: 0 命中(MAHA 这个缩写在 2024-04 还未广泛流行),但 **RFK Jr. + food supply 政治化** 是 R11 核心叙事
- **microplastics**: 0 命中(需 R12 验证)
- **99% carnivore 自述**: R11 没有任何 video 公开 Baker 自己说"我现在是 X% carnivore"。silence 本身就是 softening 信号

#### 明确的"他/她说过的"
- **Rivero 在做 patient-level data collection on food → autoimmune** [20240418005.md]
- **Rivero spelling 不稳定** - "rivera.com" vs "Rivero" [20240418005.md, 20240422003.md, 20240417002.md, 20240419002.md]
- **Baker 57.5 岁, 260 lbs 想要 240 lbs** [20240417002.md]
- **Baker 400m<60s + 100m<13s 是个人目标** [20240417002.md]
- **NYT 正在做 carnivore lifestyle piece** [20240418004.md]
- **Ken Berry + "low carb people" 组建 American Diabetes Society 作为 ADA 的 counter** [20240422003.md]
- **Baker 第一次系统用 "molecular mimicry"** [20240418005.md]
- **Baker 第一次引用 zonulin / leaky gut 学术框架** [20240429001.md]
- **Baker 第一次详细解读 Minnesota Coronary Survey 并指控 guidelines corruption** [20240430001.md]
- **Baker 第一次攻击 Bill Gates 健康** [20240419002.md]
- **Baker 第一次提 RFK + food supply 政治** [20240404001.md]
- **Baker 第一次明确反对 trans identity 话题**(gelatinous blobs of broken minds) [20240427001.md]
- **Baker 第一次描绘 AI 取代医生未来** [20240422003.md]
- **Baker 第一次做 vegan → regenerative omnivore conversion story** [20240426001.md]
- **Baker 第一次详细列 1 头牛 = 1 家庭 4 人 1 年 = 100 万卡路里** [20240408003.md]
- **"77% military fail" 框架** [20240427001.md]

### 11.3 R10 → R11 演化对比

| 维度 | R10 (2024-02 → 2024-04) | R11 (2024-04 → 2024-05) | 演化方向 |
|---|---|---|---|
| Rivero 出现频率 | 频繁(在多个 video 介绍) | 同样频繁, 但**加入 data collection 维度** | 深化 |
| Dairy/cheese 软化 | 已开始 | 持续(cheese ball,Whole30 fries+ranch) | 深化(沉默式) |
| Attia/Norwitz/Bikman | 有提及 | **完全消失(0 命中)** | 远离 |
| Chaffee/Cywes/Stefansson | 偶尔 | **0 命中** | 沉默 |
| Paleo Medicina | 首次引用 | **0 跟进** | 浅尝辄止 |
| MAHA 政治化 | 起步 | **RFK + 77% military + Bill Gates 攻击** | 大幅深化 |
| AI / tech 议题 | 偶尔 | **系统化 AI 取代医生叙事** | 深化 |
| 学术化反 mainstream | 较弱 | **molecular mimicry + zonulin + Minnesota Coronary Survey** | 学术化升级 |
| 商业化 | Rivero 介绍 | Rivero data collection + Berry 联合 + 餐厅 conversion | 商业网络扩大 |
| Baker 个人 fitness | 未涉及 | **400m/100m 目标 + 体重 240** | 全新维度 |
| R10 跟踪点验证 | - | Rivero 拼写仍未稳定 / American Diabetes Society 出现 / 99% softening 持续 / gluten 学术化 / RFK 政治 | 大部分确认 |

### 11.4 R12 跟踪点 (基于 R11 新发现)

#### 高优先级
- **American Diabetes Society 实际成立时间表、创始成员名单、Baker 角色** - 这是 R11 最大的 organizational 事件
- **NYT carnivore story 实际发表日期 + 内容 + Baker 公开反应** - mainstream media 风向标
- **Rivero "data collection" 公开 - 患者数量、数据种类、是否发表 peer-reviewed paper** - Baker 从 influencer 转型 research 的关键
- **Attia / Norwitz / Bikman / Chaffee 关系是否真的疏远** - 还是 R11 仅为偶然
- **Baker 400m / 100m / 体重 240 实际进展** - fitness 内容是否成为常规
- **Sage regenerative kitchen (2024-05-29 新菜单) Baker 是否现场宣传**

#### 中优先级
- **MAHA 运动是否在 R12 Baker 内容中明确出现**(MAHA 2024 下半年才广泛流行)
- **GLP-1 / Ozempic 系列是否回归**
- **Bill Gates 攻击是否延伸到其他 elites (Klaus Schwab, Davos, etc.)**
- **Baker 第一次出现的 "trans 议题" 是否延续** - 这可能是 Baker 频道 audience culture war 化的信号
- **AI 取代医生叙事是否推广 - Baker 是否投资/合作 AI diagnostics 公司**
- **microplastics 议题是否进入**
- **Rivero spelling 最终确认**(rivera.com vs rivero.com)

#### 跟踪 R10 未解决项
- Rivero spelling 仍未稳定(rivera.com 出现)
- Rivero 候诊 8000 → R11 数字未公开
- GLP-1 / Ozempic 仍未展开专题
- 99% carnivore softening 持续, 沉默模式
- 80/20 microplastics 系列 仍未启动

---

## 轮 12/17 (2024-05-10 → 2024-06-12)

**素材范围**: `${HOME}/Documents/女娲造人/@ShawnBakerMD/20240510002.md` ~ `20240612003.md` (100 个 .md 文件)

### 12.0 调研元数据

- **轮次**: 12 / 17
- **日期范围**: 2024-05-10 → 2024-06-12
- **文件数**: 100
- **grep 命令与命中数**:
  - `carnivore|meat|beef|steak|animal.based` → 48 files
  - `rivero|company|ranch|disempower|empower|beef.*salt.*water` → 11 files
  - `maha|norwitz|chaffee|attia|bikman|cywes|stefansson|goodrich|nyt|new york times` → 12 files
  - `anti.nutrient|seed oil|fiber|plant|leaky gut|zonulin|molecular mimicry` → 7 files
  - `keto|cholesterol|insulin|cancer|aging|longevity|GLP-1|Ozempic|mercola|unwin|ede|...` → ~40 files
  - `bitcoin|crypto|sound money` → **0 files**
  - `Biden|Kennedy|RFK|MAHA|trump|Calley Means` → 0 files (R12 内不出现; 20240610002.md 的 video_id "RFKvxO5ylns" 是随机字符串, 非引用 RFK)
  - `California|california` → 4 files (Baker California trip)

### 12.1 核心发现(5-10 条)

#### 发现 1: Rivero 商业化进入"展销 + 内容分发"阶段 [R12 全新]
- `[20240531001.md ~00:00:02]` Baker 在 "kokon" 会议现场:"here I'm at kokon we're at our Rivero Booth I got my little speaker badge on" — Baker 公开以"speaker + Rivero booth 主人"双重身份参会
- `[20240527003.md ~00:01:12]` Baker 描述 Rivero 商业模式:"that's kind of how Rivero works you know we think there is a reason for things are happening why people are sick check out Rivero" — 把 Rivero 包装成"为什么人们生病的答案"
- `[20240520001.md ~00:02:19]` Baker 公开使用"empower"框架:"mission is to try to get these so many sick people to start to empower themselves to be healthy uh VI things like Rivero"
- `[20240529001.md ~00:02:43]` Baker 视频结尾 CTA:"check out Rivero if you're interested take care bye-bye"
- `[20240531001.md ~00:00:27]` Baker 在 kokon 自报饮食:"had a beef rib and a half pound of brisket that's exactly what I had beef rib great mind think a light man" — Rivero booth 食物即"个人品牌演示"
- **状态**: 他/她说过的(直接 quote)
- **vs R11**: R11 已提到 Rivero + data collection, R12 进一步呈现 **R11 未明说的"展销会营销"行为** (Booth + speaker + sample brisket consumption on camera)

#### 发现 2: "你必须吃肉, 不必吃植物" 升级为通用生物学论据 [R12 全新]
- `[20240605002.md ~00:00:14-00:00:25]` Baker:"there are things in meat that you have to have that you cannot get from Plants but there is nothing in plants or fungus that you have to have that you cannot get from meat so you have to eat meat and you certainly don't have to eat plants and I would argue that you don't want to eat plants for Optimal [health]"
- 这是 Baker 第一次明确使用 **生物学非对称性论据** (asymmetric biological necessity): 肉有植物没有的东西, 植物没有肉没有的东西; 因此肉 = 必要, 植物 = 不必要
- 文件标题本身就是"反问修辞" 的示范:"Why do we not have to eat plants, but have to eat meat?"
- **状态**: 他/她说过的(直接 quote)
- **vs R11**: R11 Baker 谈 anti-nutrient 主要是从 gluten / 谷物角度, R12 已升级到 **植物-真菌作为整体类别的本体论级别反对**

#### 发现 3: Minnesota Coronary Survey + cholesterol 学术化论证 [R12 全新]
- `[20240604001.md ~00:00:03]` Baker:"Minnesota coronary survey this is the largest ever randomized controlled trial" — Baker 引用 **Minnesota Coronary Survey** (1968-1973, 9000+ 患者) 作为 cholesterol-saturated fat-heart disease 关系的反证
- `[20240604001.md ~00:00:21]` 描述实验设计:"fed traditional American food with at least 18% saturated fat and cholesterol in their diet the other group got soft margarine so seed oils in place of their butter whole egg substitute lowfat beef and dairy products filled with seed oils"
- **状态**: 他/她说过的(直接 quote + 引用具体研究名称)
- **vs R10-R11**: R10-R11 提过 Minnesota Coronary Survey 但作为 R11 academic 化的一部分, R12 **专题 video** (标题 "Does eating cholesterol give you heart disease?") 处理, 升级为独立论证支柱
- **我的判断**: Baker 在 R12 系统化使用 **被压制研究 + seed oil 反转** 双层论证: 研究证明"替换饱和脂肪 → 死亡率不降反升", 同时把 seed oil 定位成"实验对照组才用的可疑替代品"

#### 发现 4: Ozempic / GLP-1 议题正式进入 Baker 内容 [R12 全新 / R10-R11 跟踪点兑现]
- `[20240603002.md]` 标题: "This kind of diet does the exact same thing as Ozempic!" — **carnivore 替代 Ozempic** 框架
- `[20240605003.md]` 标题: "Can Ozempic give you MORE FAT Cells?" — **反 Ozempic** 论证 (Baker 担心 GLP-1 反弹)
- **状态**: 他/她说过的(标题直接)
- **vs R10-R11 跟踪点**: R10-R11 跟踪点明确指出"GLP-1 / Ozempic 仍未展开专题", R12 **双专题兑现** — 一个 pro-carnivore-over-Ozempic, 一个反 Ozempic 副作用
- **R12 策略**: **双面论证** — Ozempic = 不必要 (因为 carnivore 可替代) + Ozempic = 有害 (制造更多脂肪细胞); 不是单边反对

#### 发现 5: Mikhaila Peterson 食谱 + 食谱化 carnivore 继续 [R12 全新]
- `[20240608004.md]` 标题: "Mikhaila Peterson's carnivore diet recipe" — Baker 推荐 Peterson 家的肉食食谱
- 配以 `[20240531003.md]` 标题: "Lunch as a high-fat five-year carnivore!" — **5-year** 出现, Baker 用 longevity 数据进一步证明 carnivore 长期可行性
- `[20240520001.md]` 标题: "Time to wake up the BEASTS!" — Baker 用"野兽"作比喻, 强化人类作为 carnivore 的进化定位
- **状态**: 他/她说过的(标题)
- **vs R10-R11**: Mikhaila Peterson 在 R10-R11 已是常见引用, R12 **首次专题食谱 video**, 暗示 Baker 内容从 philosophical/explanatory 转向 **practical recipe delivery**

#### 发现 6: California trip + anti-California sentiment 出现 [R12 全新]
- `[20240611003.md ~00:00:01]` "I'm heading out to California for a little over about a week or so"
- `[20240613002.md ~00:01:43]` Baker:"laga beach is pretty I mean obviously a lot people why you going to California well weather's beautiful there's some beach to a degree now if we ever move we won't move back to California for various reasons"
- `[20240619004.md ~00:00:15]` "Leaving California!! ... successful trip to California did a couple big podcasts"
- `[20240610002.md ~00:00:??]` Baker video: "Does this beef hamburger not actually contain beef?" — 配合 California trip 时间窗
- **状态**: 他/她说过的(直接 quote)
- **vs R10-R11**: R10-R11 Baker 自报住在 New Mexico / 美国西南, R12 **首次出现明确的"anti-California 居住偏好"** 表达
- **我的判断**: California trip 似乎是"短期 podcast 出差", Baker 强化"我们不会搬回 California" — 暗示 **Baker 对 California 政治/政策环境 (vegan activism, food regulation) 的具体不认同**

#### 发现 7: 99% carnivore softening 持续, 新增"对大多数人的非全 carnivore 接受" [R12 延续 + 深化]
- `[20240523003.md ~00:01:31]` Baker (引用他人):"view that literally 99% of the people on Earth you view as somehow your enemies" — Baker **反对** 99% 民众敌对化叙事
- `[20240606001.md ~00:02:43]` Baker (回应对其商业公司的批评):"doesn't have to be all carnivore but God don't listen to these people" — **明确接受"不必全 carnivore"**, 但坚持"也不要听 mainstream 营养学"
- **状态**: 他/她说过的(直接 quote)
- **vs R10-R11**: R10-R11 已有 softening 信号 (cheese ball, fries+ranch), R12 **语言层面明确** — Baker 第一次 video 标题之外的章节里说"doesn't have to be all carnivore"
- **意义**: 商业化阶段的必然产物 (carnivore 全餐 = 小众市场; carnivore + 一部分 plant = 大众市场)

#### 发现 8: anti-nutrient / leaky gut 学术化, 新增 senolytic 细胞机制 [R12 全新]
- `[20240513004.md ~00:01:00]` Baker 解释 carnivore 改善关节痛的机制:"inflammatory pyocin being produced by these fiberblast like senovio sites these are the cells that produce that" — 引入 **senolytic / senescent cell 机制** (纤维母细胞样衰老细胞分泌炎症因子)
- `[20240528001.md ~00:07:06]` Baker 在 muscle building 视频里:"sort of GI related autoimmune issue where you know leaky gut inflamed gut leads to Downstream symptoms" — **leaky gut 概念作为 carnivore 改善 GI 症状的机制** 出现
- **状态**: 他/她说过的(直接 quote)
- **vs R10-R11**: R10-R11 已提到 molecular mimicry / zonulin / leaky gut, R12 **新增 senolytic / fibroblast-like senescent cell** 作为新的学术机制
- **意义**: Baker 持续把 carnivore 论证从经验/轶事 → cell biology 学术机制上抬

#### 发现 9: 99% softening + empowerment 框架, 对应"client empowerment"商业话语 [R12 全新]
- `[20240524001.md ~00:01:28]` Baker 描述健康问题:"somehow um it's we're unlucky we're disempowered at someone else's fault uh there's nothing I can do about it" — **描述 victim 心态, Baker 反对** — 但他的表述"disempowered"暗示他认知中主流叙事是"被剥夺权力"
- `[20240520001.md ~00:02:19]` Baker 直接使用 "empower themselves to be healthy" 框架 — 这是 **self-help + health coach** 行业典型话语
- **状态**: 他/她说过的(直接 quote)
- **vs R10-R11**: R10-R11 Baker 较少用 "empower" 词汇, R12 **首次密集使用** — 与 Rivero 商业化 (Booth + 招人) 时间窗同步
- **我的判断**: Baker 内容从"educator" 转向"health coach / consultant" — 强调个人行动 vs 系统结构

#### 发现 10: Breedlove + Bitcoin 仍是 R10-R11 重要参考点, R12 维持低频 [R12 延续]
- `[20240517002.md]` 标题: "How I got started on the carnivore diet with @RobertBreedlove22" — Baker 第二次与 Robert Breedlove 合作视频
- **Bitcoin / crypto 0 命中** — 与 R11 跟踪点一致, Baker 持续不在 YouTube 内容里谈 Bitcoin
- **状态**: 他/她说过的(标题 + collaboration 出现)
- **vs R10-R11**: R11 已记录 Breedlove 重要性 + Bitcoin 沉默, R12 **重复模式**

### 12.2 R11 → R12 演化对比

| 维度 | R11 (2024-04 → 2024-05) | R12 (2024-05 → 2024-06) | 演化方向 |
|---|---|---|---|
| Rivero 商业化 | data collection 概念 | **kokon 会议 booth + speaker badge + brisket 现场试吃 + "empower" 商业话语** | 展销 + 内容分发落地 |
| Attia/Norwitz/Bikman | 0 命中 | **0 命中 (R12 维持沉默)** | 持续远离 |
| Chaffee/Cywes/Stefansson | 0 命中 | **0 命中** | 持续沉默 |
| MAHA 政治化 | RFK + 77% military + Bill Gates | **0 命中 (R12 Baker 沉默 MAHA 词)** | 突然沉默? |
| 反 plant 论证 | 谷物 / gluten | **生物学非对称论据 (必须吃肉, 不必吃植物)** | 升级到本体论 |
| cholesterol 学术化 | Minnesota Coronary Survey (简单引用) | **专题 video + seed oil 反转** | 专题化 |
| Ozempic / GLP-1 | 0 专题 | **双专题 (carnivore 替代 + 反 GLP-1 副作用)** | 兑现 R10-R11 跟踪点 |
| Mikhaila Peterson | 偶提 | **专题食谱 video** | 食谱化 |
| 99% softening | 沉默 (cheese, ranch) | **明示 (doesn't have to be all carnivore)** | 语言层面突破 |
| California | 未涉及 | **anti-California 居住偏好 + trip 期间 podcast** | 地理政治化 |
| Bitcoin | 0 命中 | **0 命中** | 持续沉默 |
| empower / disempower | 偶提 | **密集使用 + 商业话语化** | 健康教练转型 |
| senolytic 机制 | 未涉及 | **fibroblast-like senescent cell 引入** | 学术化新增 |
| Dairy/cheese 软化 | 持续 | 持续 (R12 未新增) | 持平 |
| Hack Your Health (Netflix) | 未涉及 | **kokon 会议出席** | 现场活动 |
| R11 跟踪点验证 | - | Ozempic 双专题兑现 / Rivero 展销化 / MAHA 沉默 / Attia 沉默 / Minnesota Coronary 专题化 / Empower 商业化 | **混合 (兑现 + 沉默)** |

### 12.3 R13 跟踪点 (基于 R12 新发现)

#### 高优先级
- **Rivero kokon 会议 2024-05-31 现场 — Baker 与谁同台? Rivero 当场是否销售/招人?** — Baker 商业化网络实际面貌
- **Baker "5-year carnivore" 视频 — 长期 safety data 是否给出?** — Baker 用 longevity 论证的强度
- **Mikhaila Peterson 食谱 video 流量 + 评论反馈** — Baker 受众对 Peterson 家的接受度
- **Ozempic 双专题的后续 — Baker 是否会推荐停用 GLP-1 / 是否进入具体减药个案**
- **California trip 期间 podcast — Baker 与谁对话 (同 Baker 频道 R10 R11 pod 名单对比)**
- **anti-California 倾向是否延伸到政治 (Baker 频道是否会跟进 California AB 法案 / food regulation)**

#### 中优先级
- **"empower" 商业话语 — Baker 是否在 R13 推出正式 consulting/coaching 服务**
- **Minnesota Coronary Survey 专题 video — Baker 是否会引用其他 "suppressed studies" (如 Sydney Diet Heart Study, Minnesota Coronary Survey, etc.)**
- **Hack Your Health 出席 — Netflix 纪录片 Baker 是否会有 cameo**
- **Senolytic / cellular senescence 学术化 — Baker 是否引用 Baker 等人的具体研究**
- **Breedlove 二次合作 video 内容 — 是否有 Bitcoin 议题 (R10-R12 持续沉默)**

#### 跟踪 R10-R11 未解决项
- Rivero spelling 仍未稳定 (R12 未见新拼写)
- Rivero 候诊 8000 数字 (R12 仍未公开)
- Bill Gates / RFK 攻击 (R12 突然沉默, 兑现但停止?)
- 80/20 microplastics 系列 (R12 仍未启动)
- MAHA 政治化 (R12 完全 0 命中 — 这是新沉默信号)
- Baker 400m / 100m / 体重 240 (R12 提及 basketball dunk 续作, 但 fitness 内容频次未升级)
- NYT carnivore story (R12 仍未发现 Baker 公开评论 NYT)

#### 沉默信号 (R13 需确认是否持续)
- Baker 整体在 R12 不提 main-stream 媒体 (NYT / Washington Post / mainstream press)
- Baker 整体在 R12 不提 crypto / Bitcoin
- Baker 整体在 R12 不提其他 carnivore 倡导者 (Chaffee / Norwitz / Bikman / Cywes)
- Baker 整体在 R12 不提 Paleo Medicina / Stefansson
- Baker 整体在 R12 不提任何具名 medical 反对者 (Joel Kahn, etc.)

### 12.4 未发现项 (诚实记录)

- **GLP-1 / Ozempic 在 R12 之前**: 0 专题 video 命中, R12 兑现双专题
- **NYT carnivore story 公开评论**: 0 命中
- **Bitcoin / crypto 公开讨论**: 0 命中
- **MAHA / RFK 公开支持表态**: 0 命中 (R12 突然沉默)
- **Attia / Norwitz / Bikman / Chaffee / Cywes 关系演化**: 0 命中
- **Rivero spelling 标准化**: 未观察到稳定 (rivera.com vs rivero.com)
- **Rivero 候诊数字公开**: 未公开
- **microplastics 系列**: 未启动
- **AI 取代医生叙事 R12 兑现度**: 未深入 (R11 已涉及, R12 未扩展)

---

**R12 报告完成时间**: 2026-06-05
**调研员**: fuxi-skill Phase 1 Agent 1 (著作维度)
**写入模式**: 追加到 R11 之后
**文件路径**: `${HOME}/Documents/女娲造人/skills/MiniMax-M3-Claude/shawn-baker-md/references/research/01-writings.md`
**文件数**: 100 (20240510002.md → 20240612003.md)
**耗时**: < 10 分钟

## 轮 13/17 (2024-06-12 → 2024-07-29)

**调研员**: fuxi-skill Phase 1 Agent 1 (著作维度)
**文件数**: 100 (20240612004.md → 20240729001.md)
**耗时**: ~9 分钟

### 13.1 范围确认

```
cd ${HOME}/Documents/女娲造人/@ShawnBakerMD/ && ls | sort | sed -n '1201,1300p'
= 100 个文件, 从 20240612004.md 到 20240729001.md
```

### 13.2 关键词 grep 命中统计 (按命中文件数排序)

| 命中数 | 关键词 | 备注 |
|---|---|---|
| 32 | meat | 基础词,高密度 |
| 27 | fat | 基础词 |
| 23 | carnivore | 核心 |
| 18 | steak | 偏好 ribeye/strip loin |
| 17 | nyt | 高频误报(实际为 transcription 噪音,见下) |
| 17 | protein | macronutrient 讨论 |
| 14 | sugar | 抗糖持续 |
| 14 | oil | seed oil 讨论 |
| 14 | beef | ribeye/strip loin/tomahawk |
| 13 | heart | 心脏 + 心率 + heartfelt |
| 11 | plant | plant-based 反复出现 |
| 11 | egg | 营养讨论 |
| 10 | weight | 体重管理 |
| 9 | water | 基础 |
| 9 | energy | 能量/活力 |
| 8 | vegan | 持续反对 |
| 8 | cancer | 持续议题 |
| 7 | keto | 持续支持 |
| 7 | iron | 营养 |
| 6 | salt | electrolytes |
| 6 | depression | mental health |
| 6 | dairy | softening 持续 |
| 6 | cholesterol | 偶尔提及 |
| 5 | sun | 维生素 D |
| 5 | physician | 身份认同 |
| 5 | diabetes | 持续议题 |
| 4 | stress | mental health |
| 4 | rivero | 商业化核心 |
| 4 | gut | 肠道议题 |
| 4 | doctor | 身份 |
| 4 | autoimmune | 持续议题 |
| 3 | obesity | 持续 |
| 3 | insulin | 持续 |
| 3 | exercise | 生活方式 |
| 3 | electrolyte | 持续 |
| 3 | bipolar | mental health |
| 3 | anxiety | mental health |
| 2 | sleep | 偶尔 |
| 2 | seed | seed oil |
| 2 | schizophrenia | R13 重点新增 |
| 0 | longevity / aging | 沉默 (R12 也沉默) |
| 0 | rivero (短词 "Rivero") 4 命中 — 见 13.3 | R12 沉默后 R13 重新出现 |
| 0 | glp1 / ozempic / semaglutide | R12 双专题后 R13 沉默 |
| 0 | carnitine (R13 新增见下) | 个别命中,见 autism 视频 |
| 0 | norwitz / chaffee / attia / mercola / bikman / cywes / maha | 全部沉默 (R12 同样沉默) |
| 0 | malhotra / bikman / hyman | 沉默 |
| 0 | paleo medicina / savory / gabe brown | 沉默 |
| 0 | sun (R13 5 命中) | 维生素 D 关联 |

**注意**: R13 唯一重要术语 `schizophrenia` 命中 2 个文件,这是一个**新主题** (R12 0 命中)。

### 13.3 关键发现 (10 条)

#### 发现 1: Rivero 商业化进入"高调招人+州际扩张"阶段 (R13 重头)
**[20240619004.md "Leaving California!!"]** Baker 从 California 返家途中明确说:
> "we had our first really big patient meeting at Rivero last night lots of patients in there all of them really excited about... being part of the change of the way we practice Healthcare... the number of people that want this to happen... either by participating by investing in us"

**[20240624001.md "Most surgeries are UNNECESSARY!!"]** Baker 公开招徕医生:
> "we are we are taking applic[ations] we we have applications we're taking applications as we expand"

**[20240703004.md "Let's talk about IBS!!"]** 强化"全美 50 州"覆盖:
> "please check out rivera.com we have Physicians that will treat patients in all 50 states"

**[20240710002.md "One of the biggest problems I encountered as a physician..."]** 详尽描述 Rivero 价值主张:
> "one of the things that I'm excited about with Rivero is that we have all the support you need as a physician to actually accomplish what it takes to include lots of daily support Community Support education materials uh coaching... we have some people with weird disease that sometimes spontaneously remit and there's no curiosity why is that well because the pharmaceutical companies didn't tell us to be concerned about"

**这是 R13 唯一最强的商业化信号**。R12 跟踪点 (R12.3 #1) 关于 "Rivero kokon 会议 2024-05-31 同台" 在 R13 没有延续,但商业化**从早期招揽转向"既有 patient 群 + 招医生"双轮驱动**。

#### 发现 2: "90% carnivore" Softening 持续,但加入"therapeutic protocol"框架 (R13 重要)
**[20240703001.md "Talking about gut health on my recent podcast with @DhruPurohit"]** Baker 接受 Dhru Purohit 采访 (R10/R11/R12 跟踪点:California trip 期间 podcast 兑现):
> "I don't PR promote it as all humans need to do this or we we you know we are uh inherently carnivorous it is a I think humans exist on a spectrum you know there are people that clearly eat a mostly meet that all the way to people that are fruitarians for instance and they still exist and they're alive so clearly you can do that uh but I use it as a therapeutic protocol I usually tell people three mon mons is more realistic"

> "had collected data on about 12,000 people doing this and we kind of said you know at what point did you notice significant improvements for XYZ conditions and by three months most people saw a pretty significant inflection point"

**这是 R12 softening 趋势的进一步延伸**。R12 是 "I eat 90% carnivore, 10% junk food" 故事;R13 是 "humans exist on a spectrum + 3-month therapeutic trial" 框架。**该 softening 已有数据支撑 (12,000 人 survey)**。

#### 发现 3: Schizophrenia 主题**新**进入 R13 — 关联研究被压制叙事
**[20240612004.md "Carnivore diet and mental health"]** Baker 列出 mental health 改善清单:
> "schizophrenia has been improved"

**[20240702001.md "State of Maryland shuts down ongoing Ketogenic research!!"]** Baker 公开抨击研究压制:
> "over in Maryland uh a Harvard uh physician uh has been conducting a a research study on schizophrenia in ketogenic diets... this ongoing research which was approved by the state of Maryland which is being done by Deana Kelly who is a well seasoned researcher... has recently been halted by the Maryland Secretary of Health uh uh Laura Herrera Scott for some reason don't know why it is some procedural thing apparently now this is highly unusual this is almost obstructionist... there is a petition that is being circulated to help sign to to re re-engage the study"

**[20240711002.md "Deliberately suppressing keto/carnivore research??"]** 同主题二连发:
> "there is a ketogenic intervention trial that is being done down in Maryland where the Maryland Secretary of Health has shut that study down with with no apparent reason just some procedural reason"

**新维度**:
1. 首次具名攻击**州级卫生官员** (Laura Herrera Scott)
2. 首次具名引用**特定研究者** (Deana Kelly)
3. 首次具名**研究项目**(Harvard-Maryland 精神分裂症酮饮食 RCT)
4. 公开动员"签名请愿"+ 公布官员联系方式
5. 用"obstructionist / basically evil" 等道德化措辞

**这是 R12 未出现的全新政治化行动主义维度**。Bikman/Cywes 风格的"研究被压制"框架首次延伸到州政府层面。

#### 发现 4: Dhru Purohit 合作兑现 R10-R11 跟踪点
**[20240703001.md]** Baker @ DhruPurohit 跨界合作 (gut health 主题):
> "many many many people use a carnivore diet to improve these types of issues"

Purohit 是 wellness/functional medicine 圈大 V (也主持 Bredesen/Podcast 等),R12 跟踪点 (R12.3 California trip 期间 podcast) 兑现。

#### 发现 5: 食品监管政治化 (Baker 公开讨论 Florida 反 HFCS 立法)
**[20240615001.md "Should certain foods be banned?"]** Baker 讨论 Florida 国会议员 Anna Paulina Luna 立法禁用 HFCS / 食品色素:
> "Florida congresswoman Luna has proposed legislation to uh basically Outlaw things like high fructose corn syrup and certain uh food dyes"

Baker 立场:倾向于**"不补贴"** 而非"禁用":
> "should we just go ahead and just say we're not going to subsidize this stuff anymore which might be the the better way to do that in my view"

注意到 Baker 提到 "California 实际上已经禁止了一些食品添加物" (R13 第一次公开表达"anti-California"倾向:在 California trip 期间)。**这是 R12 跟踪点 (anti-California 倾向是否延伸到政治) 部分兑现**。

#### 发现 6: Cancer / 加工食品因果链 — 加工肉类 vs 红肉反复辩论
**[20240715001.md "Why you should buy American and buy local"]** Baker 痛批:
> "on one hand we have the government saying that Ultra processed foods are great for you they don't do anything they're healthier than red meat and on the other hand we have them saying they're a leading causing cancer where is the transparency where's the honesty I think we all know the answer beef and red meat is great for you Ultra processed foods are going to kill you and give you cancer plain and simple"

**[20240717002.md "If you can't trust them with chicken why trust them with this?"]** Baker 拆开超市加工鸡胸:
> "first ingredient is chicken the second ingredient is sugar and the third ingredient is M toex fourth ingredient corn flour this [ __ ] says chicken breast on it... they told us about how bad alcohol was was for us they told us how bad tobacco was for us it was drummed into us I know how bad... but why are they not warning us about [ __ ] like this because in the long run sh like this actually hurts more people each [ __ ] like this every day it's a [ __ ] slow death that's how we got one in two of us get we get cancer that's why coloror cancer is so high among the young because we eating [ __ ] [ __ ] like this"

**R13 新增**:"colorectal cancer is so high among the young" — Baker 引用年轻结直肠癌上升叙事 (此为真实流行病学趋势),把因果归到加工食品。

#### 发现 7: Autism / Carnitine 学术化 (R13 新增)
**[20240622003.md "Does autism have anything to do with nutrition?"]** Baker 首次系统讨论 autism 与 nutrition:
> "autism to do with nutrition I looked back and I looked at the increase in autism and when that started going up was the exact same time as the heart disease obesity and diabetes and cancer rates all started going up... vegans and vegetarians should have higher rates of kids with autism yes and in fact they do and Texas A&M actually found a reason one of the reasons why yeah so they found you actually have to have carnitine for proper neuronal development and in fact talking to Chris Palmer he was saying yeah actually carnitine is integral for mitochondrial Health in the brain"

**新增维度**:
- 首次公开讨论 autism (R12 未涉及)
- 引用 Texas A&M 研究 (具体机构名)
- 引用 Chris Palmer (哈佛精神科医生,keto-mental health 倡导者)— R13 Baker 阵营新增盟友
- 引用 **carnitine** (肉类特异营养素) — R13 "anti-nutrient 学术化" 的反方向 (Baker 强调肉类的**主动营养优势**)

#### 发现 8: Pink Slime / 氨洗碎肉 — Baker 警告超市牛肉 (R13 新增)
**[20240620002.md "Have you heard of pink slime in ground beef?"]** Baker 公开警告:
> "pink slime now I know everybody has heard about pink slime before there a big controversial topic... BPI actually ended up winning this lawsuit... they're going to be washing the pink slime with something called andinus ammonia if you were to take this product and put it on the soil it's going to be killing every micro living organism in the soil so they're taking this washing the pink slime with it putting it into the ground beef... our guts are made up of living organisms tons of good bacteria tons of bad bacteria gut flora"

Baker 在此**首次明确建议**:
> "buy the [ __ ] raw chicken I know they [ __ ] with it but still better than this [ __ ] [ __ ] here"

**立场演化**:Baker 之前立场是"肉 = 健康"绝对化;R13 首次区分"工业加工肉类 vs 原肉" — 这是 R12 未有的细微化。**这与他长期论证的"all meat is fine"立场有微妙张力**,但符合他"读标签"一贯态度。

#### 发现 9: Tomahawk 牛排大胃王比赛 + Bitcoin conference 跨界 (R13 新增)
**[20240729001.md "Tomahawk ribeye eating contest?"]** Baker 描述参加 BitPoint Bitcoin 大会的吃牛排比赛:
> "competed in a tomahawk riy eating contest at the folks at the bit Point Bitcoin conference Texas slim and the uh be finishes put on um I ended up basically winning the competition I had three Tom Hawk rib eyes in about 30 minutes"

Baker 自我辩护 "gluttony":
> "typically I eat about 4 lbs a day and you know I just haven't been hungry and I haven't needed to eat and it is now something like I don't know 27 hours later I'm just starting to get a little bit hungry I probably will eat uh a small amount and so my 2-day total will be about what it usually is about 8 lb so in no way shape or form was that a waste of food"

**R12 沉默信号打破**:
- **Bitcoin 议题**:R12 跟踪点 (Bitcoin 沉默) 在 R13 部分兑现 — Baker 出现在 Bitcoin 大会但**未在内容中讨论 Bitcoin** (仅作为场景)
- **政治化"主权"话语**:
> "there are people that want to control it want to control what you eat and by doing so they're you you're under their thumb you are basically you know basically a surf or a slave or wh however you want to put it you know we need to have sovereignty over what we put in our own bodies"
- **"beef initiative"** 组织被提及 (R12 跟踪点 #5 Breedlove 关系) — 暗示 Baker 与 Texas Slim / Beef Initiative 圈层有联系

#### 发现 10: 高脂 vs 低碳水 carnivore 内部辩论 (Baker 自身 softening)
**[20240621001.md "Is a HIGH FAT Carnivore Diet the answer?"]** Baker 自我修正:
> "the average carnivore is probably between 60 and 80% uh fat by cow because carbohydrates aren't in in the diet anymore and I think a lot of people you know will go with the very high fat version... many of them don't really attain a physique that perhaps would be considered very lean in many cases you know you don't see as many I mean there's there there's obviously exceptions um but the the majority of people um obtain a you know less obese physique but they don't become extremely muscular"

Baker 个人偏好:
> "for myself personally again this is my personal reflection that as I will lean out I do better when I reduce the fat a little bit you know and and and I get closer to that 50 to 60% of my calories coming from you know either protein or fat"

**立场演化**:从 "fat is fine" 转向 "50-60% fat + 调整 macros 可塑形"。**这是对自身 R08-R11 "all-you-can-eat fat"立场的微调**。

### 13.4 R13 跟踪点 (基于 R12 + R13 新发现)

#### 高优先级
- **Maryland 精神分裂症酮饮食 RCT 后续** — Baker 动员签名请愿是否有效? 研究是否重启?
- **Rivero "招医生" 申请机制** — Baker 提到 "taking applications" — 具体形式? physician 需要什么 credential?
- **Rivero "50 州覆盖"** — 是否真覆盖? 哪些州尚未开通?
- **Baker 出现在 Bitcoin conference (BitPoint) — 是否在内容层面接触 Bitcoin/crypto?**
- **Laura Herrera Scott 是否被 Baker 持续点名?** — 州级官员公开抨击的下一步
- **Chris Palmer 引用 — Baker 与 Harvard 精神科阵营是否有后续合作?**
- **anti-nutrient 学术化反方向 — Baker 是否会系统化"carnitine / B12 / 血红素铁"等肉类特异营养素?**
- **加工肉 vs 原肉区分 — Baker 立场是否会进一步细化 (e.g., 反对 charcuterie / deli meat)**
- **Anna Paulina Luna / Florida HFCS 立法** — Baker 是否会跟进政治支持?

#### 中优先级
- **Cancer 因果链 (Baker 反复出现)** — Baker 是否会引用具体研究 (e.g., EPIC, NHANES)?
- **autism / carnitine** — Baker 是否会做后续视频?
- **Anh Cao (Texas Slim) / Beef Initiative 关系深化** — Baker 出现在 BitPoint Bitcoin conference 是否是 R10-R12 跟踪点兑现?
- **"Sovereignty" 政治话语** — Baker 是否会进一步上升到 "food freedom" / "medical freedom" 议题?
- **Suicide / addiction 议题** — Baker 提到色情/烟/酒成瘾,是否会展开?

#### R10-R12 未解决项 (R13 仍待跟踪)
- **GLP-1 / Ozempic** — R13 完全沉默,跟踪是否持续沉默
- **Norwitz / Chaffee / Attia / Mercola / Bikman / Cywes / Paleo Medicina** — R13 完全沉默
- **MAHA / RFK** — R13 完全沉默
- **Hack Your Health Netflix** — R13 未见
- **microplastics 系列** — R13 仍未启动
- **Senolytic 学术化** — R13 未扩展
- **NYT carnivore story 公开评论** — 仍 0 命中 (但 "nyt" 17 命中是 transcription 噪音 — 见 13.6)

### 13.5 未发现项 (诚实记录)

#### 关键词级 0 命中 (R13 全程)
- **GLP-1 / Ozempic / Semaglutide / Tirzepatide** — R12 双专题后突然归零
- **Norwitz / Chaffee / Attia / Mercola / Bikman / Cywes** — 全部沉默
- **MAHA / RFK / Make America Healthy Again** — 完全沉默 (R12 同样)
- **Malhotra / Hyman / Sinclair / Huberman** — 全部沉默
- **Paleo Medicina / Stefansson / Tro Kalayjian / Anthony Chaffeemd** — 沉默
- **Huberman / Sinclair** — 沉默
- **Breedlove / Bitcoin 在内容中** — 仅作为场景出现
- **Longevity / aging / senolytic / telomere / Zone 2** — 全部沉默 (R12 同样)
- **microplastics** — 仍未启动
- **Climate / Environment** — 完全沉默 (除个别 "food supply" 提及)
- **NYT 主流媒体** — "nyt" 17 命中是 transcription 误报,真实 0 命中
- **Pat Brown / Impossible Foods / Beyond Meat** — 完全沉默
- **Vegan activist 具名** — 0 命中 (除泛指 "vegan agenda")

#### Baker 自身未公开
- **Baker 体重 / 体型 / fitness 数据** — R13 未提及
- **Baker 240 lbs / 篮球 / dunk 续作** — R13 未提及
- **Baker 与具体 Podcast 嘉宾名单** — 仅有 Dhru Purohit 1 次
- **Baker 在 Rivero 之外的活动** — Bitcoin conference (BitPoint) 1 次

### 13.6 NYT 17 命中说明 (重要)

**grep "nyt" 命中 17 个文件,但 100% 是 transcription 误报**:
- "nyt" 实际是 "not" / "nut" / "niche" / "anytime" 等的 YouTube auto-caption 错误识别
- 例如 20240719001.md 文本包含 "when did nature become niche" — "niche" 误识别为 "nyt"
- **真实 NYT 提及仍为 0** — 与 R12 一致

### 13.7 立场演化轨迹 (R08 → R13 累积)

| 立场点 | R08 | R12 | R13 |
|---|---|---|---|
| 99% carnivore 严格度 | 99% strict | "I eat 90% carnivore, 10% junk" | "humans on a spectrum + 3-month therapeutic trial" |
| 高脂 vs 蛋白 | 100% high-fat | 持续 | 50-60% fat 优选 (leanness 倾向) |
| Rivero 商业化 | 未出现 | 招揽 / 商业化话语 | 招医生 + 50 州 + patient meeting |
| 加工肉 vs 原肉 | 未区分 | 未区分 | 首次警告 pink slime / 加工鸡胸 |
| 抗糖叙事 | 持续 | 持续 | 持续 + 引用 Brown University Alzheimer/sugar 实验 |
| 研究压制叙事 | 未涉及 | 个别 | 州级官员具名攻击 + 签名请愿 |
| 主流医学共识 | 反对 | 反对 | 反对 + 阴谋化 ("basically evil") |
| Autism / Carnitine | 未涉及 | 未涉及 | **新增** (Texas A&M + Chris Palmer 引用) |
| Bitcoin / Crypto | 沉默 | 沉默 | 场景出现 (BitPoint conference),内容沉默 |
| 政治化主权话语 | 未涉及 | 个别 | "slavery / sovereignty" 强化 |

### 13.8 R13 风格档案补充

- **家庭/亲情元素首次明显** (R12 未见):20240727001.md "Mother knows best" 是与母亲对话 (素食主义代际冲突),20240722001.md Mikhaila Peterson 1-on-1 (跨界 carnivore 网红) — 视频流量 + 受众
- **激进语言持续** (Baker 20240717002 用 [__] 屏蔽脏话,但内容是粗口) — YouTube 评论区式语言
- **新术语 "physician that gets it"** (20240710002) — R13 反复 3 次
- **"Grassroots" 反复** — 3 次 (R12 已多次, R13 持续)
- **"empower" / "disempower"** — 商业话语中持续

---

**R13 报告完成时间**: 2026-06-05
**调研员**: fuxi-skill Phase 1 Agent 1 (著作维度)
**文件路径**: `${HOME}/Documents/女娲造人/skills/MiniMax-M3-Claude/shawn-baker-md/references/research/01-writings.md`
**R13 文件数**: 100 (20240612004.md → 20240729001.md)

---

## 轮 14/17 (2024-07-29 → 2024-09-24, 100 files)

**文件范围**: `20240729002.md` → `20240924002.md` (按文件名升序第 1301-1400 个)
**调研主题**: Rivero 商业化 / MAHA 阵营深化 / anti-nutrient 学术化 / Attia 后续 / Cywes/Norwitz/Bikman 关系 / 99% carnivore softening 延续 / NYT / Bitcoin / Election 2024 / Operation Dunk

### 14.1 grep 命令 + 命中数

```
grep -li "rivero"                                   →  4 (20240806001, 20240905003, 20240913003, 20240921003)
grep -li "norwitz"                                  →  0
grep -li "attia"                                    →  0
grep -li "cywes"                                    →  0
grep -li "bikman"                                   →  0
grep -li "huberman|hyman|berry|mercola"             →  0
grep -li "nyt|new york times"                       →  0
grep -li "maha|make america healthy"                →  1 (20240907001)
grep -li "bitcoin"                                  →  0
grep -li "trump|rfk|election"                       →  5 (20240813002, 20240819001, 20240825002, 20240901002, 20240907001)
grep -li "operation dunk|highland games|deadlift|squat" → 3 (20240731002, 20240812002, 20240909001)
grep -li "seed oil"                                 →  5 (20240826002, 20240826003, 20240828002, 20240907001, 20240914002)
grep -li "highland games|games|deadlift|record|squat|powerlift" → 10
grep -li "99%|99 percent|softening"                 →  4 (20240730001, 20240810002, 20240826003, 20240921001)
grep -li "beef initiative|texas slim|breedlove"     →  2 (20240807001, 20240813002)
grep -li "savory|gabe brown|regenerative"           →  3 (20240808001, 20240811001, 20240813002)
grep -li "ozempic|GLP|wegovy"                       →  1 (20240914001)
grep -li "plant toxin|anti.nutrient|oxalate|lectin" →  2 (20240813001, 20240825002)
grep -li "chaffee|berry"                            →  5
grep -li "fertility|pregnan|kid|child|baby"         → 10+
grep -li "ldl|apob|cholesterol"                     →  5
grep -li "keto"                                     → 10+
grep -li "fiber|microbiome|gut"                     → 10+
grep -li "julie kelly|jill stein|tulsi|nicole shanahan" → 0
grep -li "meatrx|world carnivore"                   →  0
grep -li "molly|chef|recipe"                        →  3
grep -li "company|business|brand|app|launch"        → 10+
```

### 14.2 R14 核心发现 (10 条)

**他/她说过的 (直接引用)**:

1. **Rivero 商业化深化 — 病种导向, 不再只 "joinrivero.com"** [20240905003.md 00:00:46] — `Let's talk IBS!!` 标题, 在视频中明确说: "one of the things that we do at Rivero is deal with folks with IBS". 这是 R14 首次把 Rivero 与具体病种 (IBS) 绑定的营销。R13 Rivero 仍是 "online membership / coaching"; R14 起 Rivero 成为 condition-specific clinic (IBS / 激素 / 自身免疫 / 糖尿病) 的命名定位。[20240806001 00:00:50 + 20240921003 同模板] hormone health 也走同模板;[20240913003 marriage/morbid obesity] 把 Rivero 嵌入伦理探讨;[20240921003 SHOCKING Truth Hormone] 视频几乎与 20240806001 逐字相同, 显示 Rivero 软文模板化批量生产。

2. **MAHA 阵营首次明确同框 — RFK + Trump + "fix the food supply"** [20240825002.md 00:00:14] — `Trump/RFK! Will the fix the food supply?` Baker 从 Alicante (西班牙度假) 评论 RFK 退选并背书 Trump, 用 "great message about cleaning up our food supply"。[20240907001.md 00:00:01] `Will RFK make America healthy again?` 全段播放 RFK + Jesse Watters (Fox) 对话, Baker 复述 "Regulatory Agencies were set up to do exactly that"。R14 是 Baker 从 "I don't talk politics" → 主动 platforming MAHA 的过渡, 但 [20240813002.md] 仍保留 "I'm not going to say who I support for president" 的免责声明。

3. **Highland Games / 美国 500m 划船纪录 — Operation Dunk 延续** [20240731001.md 00:00:11] — `New American Record, 500 meters - Carnivore Style` Baker 在 55-59 age group 设定 1:17.5 → 1:18 目标, 现行美国纪录 1:19.5, 世界纪录 1:15.6; [20240731002.md] 同时段拍 Olympics 食物 disaster (athletes 飞肉过去); [20240812002.md highland games] / [20240909001.md 10,000 calories carnivore] (引 Eddie Hall 一个月 carnivore 后 9828 cal/day, 892g protein, 2.5 g/lb). R12-R13 Operation Dunk 是 squat 个人目标; R14 转向 "比赛 + 纪录" 的公开化叙事 + 与 Eddie Hall 等名人 carnivore 故事捆绑。

4. **Seed oil 升级为儿童 + 婴儿议题** [20240828002.md 00:00:24] — `What's the number one ingredient in baby food?` "main ingredients you'll find in most baby formulas is...seed oils...evidence suggests...sets children up for childhood obesity"; 引 "soybean Lobby" 政治化; [20240826003.md 家庭实验] DIY seed oil with hexane / isopropyl alcohol / bleach / 400°F vacuum 演示生产过程; [20240914002.md] restaurant seed oils "number one problem when you go out to dinner". R13 seed oil = 普遍 propaganda; R14 = "毒害儿童 + 婴儿配方 + 大豆游说" = 道德罪行升级。

5. **Carnivore Diet "Dangerous Long-Term" — 标题反讽 + 美国/法国对比** [20240901002.md 00:00:01] — `The Carnivore Diet is Dangerous in the long term!!` 实际是反讽; Baker 从法国 2 周回美 (256→258 lb 无变化), 自述 "I ate basically carnivore the whole time" + "more dairy products than I normally eat"; 妻子 Sophie (France) 是 "mostly carnivore in France, has her baguettes and bread every day"。R14 持续 R13 的 "99% carnivore softening" — 妻子吃 baguettes 不否认, 反讽标题做 hook + 用对比包装。

6. **DIY seed oil home production 视频** [20240826003.md] — Baker 转发实验: hexane (petroleum poison) / 99% isopropyl alcohol / bleach / 400°F under vacuum for hours, "this is the part where we need to add some harsh chemicals". R14 新增的 "可视化恐怖" 战术 — 不再仅文字说 "industrial seed oils bad", 而是把化学过程拍出来。

7. **政治化辩论模板 — "meat eaters in jail / Holocaust" 反击者** [20240819002.md 00:00:32] — `Meat eaters like me should be in prison!` 引用某 vegan 活动家 (未具名) 视频: "Sea Baker is part of the biggest Holocaust on this planet...you should be put in jail...should be um taught to be a better human being". Baker 在标题里把自己 frame 成 "受害者 + 言论自由战士"。R12-R13 已有 "Holocaust 类比" 反击 vegan, R14 升级到 "vegan 公开呼吁监禁我" 叙事。

8. **MN 学术报告攻击肉食 — "they're coming for your meat" 政策恐慌** [20240807001.md 00:00:07] — `Are they coming for your meat??` 引 Lindsey Smith Taillie (UNC PhD nutrition) 的 "warning labels + taxation on red meat" 行为科学研究, Baker 称 "they're studying this because they are wanting to put this into policy". R13 "policy capture" 叙事 (UN/WHO 阴谋) → R14 具名学者 + 大学 + 研究方法批判 ("food frequency questionnaires...inherent bias against red meat since the beginning of nutrition science").

9. **"Time magazine + Jessica Wilson + Academy of Nutrition" 三连击 — 揭穿 UPF 洗地** [20240901001.md 00:00:01] — `The corruption in American food` Time magazine 文章 "What if Ultra Processed Foods Aren't As Bad As You Think" 引 RD Jessica Wilson 推 "#ultrapress Fridays"; Baker 反驳: AND (Academy of Nutrition and Dietetics) 是 "propaganda arm of big food" 收 ConAgra/PepsiCo/Coca-Cola/Hershey's/General Mills 钱, Sylvia Rowe 等 board members 与 big food 利益绑定。R14 首次系统讨论 RD 行业 + 学会 conflicts of interest。

10. **10,000 calories carnivore (Eddie Hall) + Vegan 加肉破纪录 (Sue McDonald) — 名人案例集** [20240909001.md 00:00:02] World's Strongest Man Eddie Hall 一个月 carnivore: 9828 cal/day, 892g protein; [20240914004.md 00:00:18] vegan Master's athlete Sue McDonald 加肉后破纪录, 教练 Cynthia Montalbano 来自 Charles Poliquin 体系 (Poliquin "died at 57 of pre-existing cardiac congenital problem"). R14 故事池: 用奥运/破纪录 + 健美 + 长寿运动员构建 "carnivore = 顶级表现" 案例库。

**我推断的**:

- Rivero 软文 video 模板化 (20240806001 与 20240921003 几乎逐字相同) → 可能用同一 transcript 包装不同标题 testing CTR。 [推断]
- Baker "我不谈政治" 免责声明 + 实际推 RFK/Trump = 商业风险管理 (避免 YouTube demonetization, 同时争取 MAHA 流量)。 [推断]
- 妻子 Sophie (France) "mostly carnivore with daily baguettes" 公开化 = R13-R14 99% carnivore softening 的明确证据, Baker 不再装作家庭统一阵线。 [推断]
- DIY seed oil 视频 (20240826003) 转发素材 (不是 Baker 原创, 视频中说话者是另一人) — Baker 在做 content curation, 不仅原创。 [推断]
- 没有出现 Norwitz/Attia/Cywes/Bikman/Huberman/Hyman — R14 暂时不与精英 podcast 圈互动, 把精力放在 MAHA 政治 + Rivero 商业化 + 个人体育记录。 [推断]

**未发现**:

- Norwitz / Attia / Cywes / Bikman / Huberman / Hyman / Mercola / Ken Berry / 任何 R11-R13 高频精英 podcaster 名字 — R14 全部 0 命中
- NYT / The Atlantic / The Guardian 等 mainstream media 文章 — 0 命中
- Bitcoin / cryptocurrency — 0 命中 (R13 BitPoint 之后未深入)
- Julie Kelly / Jill Stein / Tulsi / Nicole Shanahan — 0 命中
- "Operation Dunk" 字面短语 — 0 命中 (但 highland games / 500m row record / Eddie Hall carnivore = 实质延续)

### 14.3 R14 vs R01-R13 对比

| 主题                    | R11-R13                                  | R14 新出现                                                                 |
|------------------------|-------------------------------------------|----------------------------------------------------------------------------|
| Rivero                 | URL + "online membership" 通用推销         | **病种化** (IBS / 激素 / 自身免疫 / 糖尿病) + 软文模板化                       |
| MAHA / 政治             | R13 RFK 个别提及, 无 Trump                 | **Trump + RFK 同框 + "fix food supply" 表态**, 仍保留 "不站队" 免责声明        |
| Seed oil               | "industrial / unhealthy" 通用             | **婴儿配方 + soybean lobby + DIY 生产过程演示** = 道德罪行升级                |
| 学术批判                | UN/WHO/EAT-Lancet 阴谋                   | **具名 RD (Jessica Wilson) + AND 学会 + 食品大厂赞助网**                     |
| 妻子 Sophie 饮食         | 偶尔提及                                 | **公开承认 "mostly carnivore + daily baguettes in France"** (softening 明确化) |
| Highland Games / 体育     | 个人 squat 目标                          | **500m 划船美国纪录 + Eddie Hall 9828 cal + Vegan→meat 破纪录 案例**            |
| Carnivore "is dangerous" | 防御性反驳                                | **反讽标题做 hook** (20240901002)                                          |
| 标题党风格              | "you'll never believe"                    | 升级 "SHOCKING Truth" (20240921001, 20240921003) — caps + duplicate         |
| Holocaust 类比受害者     | 自卫式提及                                | **"meat eaters like me should be in prison" 反击战** 帧定位                  |

### 14.4 R14 风格档案补充

- **"SHOCKING Truth About X Revealed" 标题模板** (20240921001 diabetes / 20240921003 hormones) — caps + 同一周两条 = 标题党规模化
- **"Hey guys Dr. Baker here" 标准开场** 仍持续 (20240806001, 20240921003 逐字相同) → Rivero 软文模板化的元素
- **法国 / 西班牙度假 vlog 兼营销** (20240819001 France carnivore / 20240825002 Alicante Spain / 20240826002 Mérida Roman bridge / 20240901002 法国对比) — R12-R13 偶发, R14 集中两周输出
- **DIY 化学实验 + 视觉震撼** (20240826003 hexane/bleach/400°F vacuum) = 新的恐惧营销范式
- **反讽标题 + 软文混合** (20240901002 "Carnivore Dangerous" → 实际全程吃肉) = stagecraft 升级

---

**R14 报告完成时间**: 2026-06-05
**调研员**: fuxi-skill Phase 1 Agent 1 (著作维度)
**文件路径**: `${HOME}/Documents/女娲造人/skills/MiniMax-M3-Claude/shawn-baker-md/references/research/01-writings.md`
**R14 文件数**: 100 (20240729002.md → 20240924002.md)

---

## 轮 15/17 (2024-09-25 → 2025-01-07, 100 文件)

**调研员**: fuxi-skill Phase 1 Agent 1 (著作维度)
**调研日期**: 2026-06-05
**文件范围**: 20240925001.md → 20250107002.md

### 15.0 Grep 命令 + 命中数

| 关键词集合 | 命中文件数 | 备注 |
|-----------|-----------|------|
| `rivero\|beef initiative\|dider ranch\|breedlove\|ken berry\|chef molly\|operation dunk\|maha\|cathar\|crusades` | 15 | Rivero/MAHA 商业化核心 |
| `trump\|rfk\|tulsi\|election\|fetterman\|nicole shanahan\|sophie` | 16 | 政治化深化 |
| `frontiers\|ibs\|crohn\|colitis\|ibd\|leaky gut\|zonulin\|molecular mimicry` | 2 | IBD 研究延续 |
| `bitcoin\|satoshi\|crypto` | 0 | R14 起就消失 |
| `anti.nutrient\|antinutrient\|lectin\|phytate\|oxalate` | 1 | 仅 1 命中 |
| `company\|business\|meat company\|restaurant\|startup\|launch` | 20+ | 商业化主题高发 |
| `carnivore\|meat\|beef\|steak\|animal.based` | 56 | carnivore 持续主线 |
| `Ozempic\|GLP-1\|zipbound` | (新, 见发现 7) | 2024-12 新概念 |
| `seed oil\|tallow\|mcdonald` | (新, 见发现 8) | tallow 替代 seed oil |
| `tucker carlson\|joe rogan` | (新, 见发现 3) | Rogan Trump interview |

### 15.1 他/她说过的 (He said / She said)

1. **"Drug companies spend $5 billion/year on TV ads in US — only country besides New Zealand allowing this"** [20240929001.md 00:00:30] "Will either Trump or Harris do this?" — Baker 直接给 Trump/Harris 提的政策议程: **禁止制药公司在电视上做 DTC 广告**。论点: 制药广告控制新闻媒体 (网络效应), 形成 information capture。R15 新立场: Baker 公开向候选人提具体政策建议 (从 R13-R14 的隐晦支持到 R15 的政策 lobby 模式)。[新]

2. **"Trust in physicians at 40% (from 70% pre-2020)"** [20241025001.md 00:00:14] "WHY We no longer TRUST our Doctors!" + [20241113001.md 00:00:36] "MAHA? This will piss off some doctors!" — Baker 两次引用同一统计 (40% vs 70%), 解读为: COVID 期间 physician 一边倒 + 算法医学 + 制药公司捕获 = 信任崩塌。R15 新数据: Baker 用量化数据点支撑"system failure"叙事。[新数据, R14 已提到但无数字]

3. **"We are NOT going to drug/diet our way out — we have to stop poisoning the food supply"** [20241007001.md 00:03:42] "Can we do this?" — Baker 跟随自己 20241006 被纽约记者挑战 IBD 故事的延续视频, 公开宣布"somewhat affiliated with MAHA" + "going to Oklahoma state legislature to secure funding for research like this"。R15 关键节点: **Baker 公开确认与 MAHA 阵营结盟**。**[重大, 立场转变点]**

4. **"RFK was just named head of HHS — I hope he fires a bunch of people at CDC, FDA, USDA"** [20241114001.md 00:00:05] "4 minute RANT about RFK being selected to lead HHS!" — Baker 在 RFK 被提名次日发布, 公开表态: "they're all corrupt crooks... taking salaries from these corporations"。Bipartisan 立场松动: R14 还说"不站队", R15 直接攻击具体政府机构 + 站台 Trump 任命。[重大]

5. **"UnitedHealthcare CEO murder is a SYMPTOM of a diseased healthcare system"** [20241208001.md 00:00:01] — Baker 12-04 Thompson 谋杀后 4 天发布, 解读为系统失败的极端化标志, 指出 UnitedHealthcare "denied ~1/3 of claims vs industry avg 15%"。Baker 借事件重申"root cause medicine 是唯一出路", 推广 Rivero 替代方案。**[新事件响应, 立场连续]**

6. **"We raised money several years ago for carnivore research at Rivero, we will be publishing our data"** [20241007001.md 00:02:14] — Baker 明确 Rivero 不仅是临床服务, 还在做临床研究 (注: 实际成立时间应核), 数据即将发布。R15 新信息: Rivero 数据采集 → 出版 pipeline 启动。[新]

7. **"Carnivore beats Ozempic — better, cheaper, fewer side effects"** [20241207001.md 00:00:02] "Better, cheaper and less side effects than Ozempic?" — Baker 引用自己 Twitter 民意调查, 主张: 减重 25%+, 成本"a fraction of Ozempic", 没有"potential long-term problems"。明确立场: animal-based keto/carnivore 应作为 firstline treatment, GLP-1 仅作为失败后的二线。R15 首次正面与 GLP-1 减重药对照, 视其为制药工业 complex 的新代表。**[新, R14 未涉及 Ozempic/GLP-1]**

8. **"McDonald's 应当从 seed oil 换回 tallow"** [20241022001.md 00:00:03] "Will Trump giving us French Fries make us healthy again?" — Baker 借 Trump 在 McDonald's 做 campaign stunt + RFK 表态"change back to tallow"事件, 公开支持 tallow 替代 soybean oil。论点: "Tallow is less processed than soybean oil"。**[新政策立场, R14 提 seed oil 是"工业垃圾"但未明确 tallow 替代]**

9. **"MAHA 中混入 vegan wackos / pescatarian / flexitarian = problem"** [20241111001.md 00:00:01] "This might piss of some MAHA people!" — Baker 对 MAHA 阵营内部发警告: 如果变成"meat as a condiment"叙事就完了。明确: "**meat should be the center of the meal, everything else is a flavor enhancement, vegetables not necessary**"。**[重要立场, Baker 开始在 MAHA 内部做"carnivore 纯度"保卫战]**

10. **"Zero evidence grass-finished beef better than grain-finished for human health"** [20241111001.md 00:00:50] — Baker 在 MAHA/regenerative ag 风潮中反主流观点: 引 Texas A&M 研究 (grain-finished biomarker 略优), 自己临床观察"grain-finished 患者同样健康"。结论: 不要禁 feedlot, hybrid system + sprouts (maaf Ranch Montana 模式) 更现实。**[新观点, R14 倾向 grass-fed/regenerative, R15 立场软化/转向 hybrid]**

11. **"Carnivore 启动方法论 — 3 个月最低, 50-90% 热量来自脂肪"** [20241018001.md 00:00:03] "You MUST watch this video if you go CARNIVORE!" — 详细 onboarding 视频: 起始 3 个月承诺; 1-5 磅肉/天; 不要 under-eat; 3-4% constipation, 20-25% diarrhea 早期; 哈佛研究数据; 长期 2 餐/天。R15 新: Baker 用"我看过 12,000 人数据"作为权威基础。[产品化 onboarding 内容, 帮 Rivero 拉新]

12. **"The carnivore diet book 出版 5 年了, 我从书上赚的钱比 6 个月行医还少"** [20241006002.md 00:05:05] "I was confronted by a New York reporter" — Baker 反驳记者"you just want to get rich"指控, 自证清白 + 强化"动机纯正"叙事。R15 罕见: Baker 主动披露经济利益冲突。[新]

13. **"Carnivore → IBD 缓解率: probably more than 50%, maybe 70-80%"** [20241006002.md 00:09:37] — Baker 对记者"你不能给人 hope"反驳的延伸: 引用 Frontiers 10-patient case series (Crohn's 完全缓解 + 停药) + 数百名未发表 case reports。预算: $2M 做正式 RCT。[新数据, R14 也提 Frontiers IBD 后续但无百分比]

14. **"Carnivore meat leaves stomach in LIQUID form, so for Crohn's strictures — avoid FIBER not meat"** [20241007001.md 00:00:38] — Baker 用反直觉解剖学 (肉类胃内液化, 纤维不消化) 反驳主流 gastroenterology"不要吃红肉"建议。**[新论点, 对"避免红肉"教条的反外科逻辑]**

15. **"Rivero 第一位医生是 Dr. Eli Jarrouge, Houston, Texas"** [20241014003.md 00:00:01] — Baker 公开 Rivero 第一位临床医生的访谈: 走 Paleo/Whole30 入行, 在 ICU 看到 metabolically unhealthy 患者, 决定转 root cause medicine。R15 标志性: Rivero 团队成员公开化 + 招募 physician 持续。[新]

16. **"UnitedHealthcare 案件 — system 失败但不是 vigilante justice 的答案"** [20241208001.md 00:01:31] — Baker 在明确表态"系统失败"同时, 拒绝为暴力开脱: "no one is advocating for that type of behavior that vigilante justice"。[新, 立场平衡, 不像 R14 一些极端表述]

17. **"I voted for Trump for freedom of speech reasons"** [20241105001.md 00:00:03] "Why I Voted!!" — Baker 罕见直接公开投票理由: First Amendment + 自己被 throttled/suppressed + 反对 informed consent 被压制。**[立场重大明确, R14 一直 disclaimer "不站队"]**

18. **"Trump/Joe Rogan podcast was less than full throated on health"** [20241026001.md 00:01:42] "Trump, Rogan and my voting ballot!" — Baker 评价 Trump 在 Rogan 节目关于 health 的回答"some qualifications there", 同时呼吁 Harris 也上 Rogan。R15 罕见: Baker 不完全买账 Trump 的 health 表态, 仍保持"看行动"距离。[立场微调, 不是无脑站台]

19. **"MAHA 应该让 Kennedy 进去, 但不要 draconian 削减 meat production"** [20241111001.md 00:03:49] — Baker 对 MAHA 政策方向的警告: Joel Salatin 被招是好事但不应强制转换 100% regenerative; 担心 Kennedy 走"Draconian measure"砍肉产量 → 实际损害 carnivore 社区 (草饲肉不够脂肪, 草饲牛肉 70-80% lean 不适合 low-carb)。**[关键, Baker 在 MAHA 内部"温和派"立场明确化]**

20. **"Disease 药物管理是垃圾, 医院系统是 sick care 系统"** [20241208001.md 00:03:47] "United Health Care CEO murdered" 视频 + 11-13 MAHA 视频, Baker 用"diseased healthcare system" 框架贯穿 12 月。R15 收尾用词: "sick, fat, depressed populace" [20241114001.md 00:03:22]。[延续 R14]

### 15.2 Rivero 商业化深化 (R14 已观察到的延续, R15 显著加速)

- **R14 → R15 演化**: R14 Rivero 是"online membership", R15 转为"physician-supervised, multi-state, employer-of-physicians"。R15 关键数据点:
  - Rivero states: **California, Texas, Washington, Florida** (20241010 视频) + "opening in more states every week"
  - **第一位临床医生公开: Dr. Eli Jarrouge, Houston, TX** (20241014 访谈)
  - **waiting list 有 thousands of patients** (20240928 招聘视频)
  - **clinical staff grown** (20241014 提到)
  - **2025 转型信息**: monthly cost "way way way lower than Ozempic" (20241207) — 第一次用价格对照定位

- **R15 Rivero 反复出现的核心承诺**:
  - "root cause medicine"
  - "get people OFF medications"
  - "physician supervision" (vs Rogan-driven 自主实施)
  - "daily support / coaches"
  - "we have positions to provide the daily support"
  - "treat the actual root cause of why they're sick"
  - "sick care system" 替代 "healthcare system"

- **Rivero 在政治风向中借势**: 11-14 RFK HHS 提名 → Baker 立即推广 Rivero 是"already practicing root cause medicine, hopefully our company and others will continue to show and lead the way"

### 15.3 MAHA 阵营深化 (R15 主旋律)

- **2024-09-29**: Baker 第一次正式向候选人 (Trump/Harris) 提问 (制药 TV 广告禁令)
- **2024-10-07**: Baker 第一次公开承认"somewhat affiliated with MAHA"
- **2024-10-22**: Baker 借 Trump McDonald's 事件表态支持 tallow 替代 seed oil + Elon Musk 政府效率
- **2024-10-25**: Baker 引"trust 40%"统计 + "Perverse incentives" + "follow the science" 是被药企 cast down 的修辞
- **2024-11-05**: Baker 公开"我投了 Trump, 因为 First Amendment"
- **2024-11-11**: Baker 在 MAHA 内部对 vegan/flexitarian 渗透发警告 ("meat as a condiment" 是问题) + 警告 Kennedy 不要"draconian"砍肉产量
- **2024-11-13**: Baker 称"MAHA piss off some doctors", 喊"我们 physician 已经失败, Kennedy 进来应该 fire 一堆人"
- **2024-11-14**: Baker 对 RFK HHS 提名 4-minute RANT: "they're all corrupt crooks... good for you RFK, good for you Donald Trump"
- **2024-12-08**: Baker 借 UnitedHealthcare CEO 谋杀事件再推 Rivero
- **2024-12-30**: Baker 2025 New Year Rivero promo ("transform your health in 2025")

**[R15 总结]**: Baker 公开完成从"独立医学异议人士"到"MAHA 阵营温和派 carnivore 旗手"的身份转变。区别于 Chaffee (更激进) / Norwitz (年轻博士), Baker 的 niche 是:**政治实操 + 立法 lobby + 公司运营 + 内容分发** 四合一。

### 15.4 我推断的 (My inferences, 标注)

- **Rivero 加速扩展与 Trump 胜选 + RFK HHS 提名高度相关** — 11-14 之后 Rivero 推广视频频率明显增加 (11-13, 12-08, 12-30 都用 Rivero 软文结尾)。[推断, 时间相关性强但非直接证据]
- **Baker 12-30 New Year promo 是 R15 收尾的高峰**: 距离 Trump 就职 (2025-01-20) 仅 3 周, 提前锁定"想 transform health in 2025"的人群。[推断]
- **Baker 第一次公开投票 (11-05) 距离选举日 (11-05) 当天发布** — 同步政治行为, 增强 MAHA 受众认同感。[观察]
- **"Carnivore 12,000 人数据" (10-18) 是 Baker 公开 Rivero 内部数据的新 baseline** — 之前未提及此具体数字。[观察]
- **R15 没有出现 "Operation Dunk"** — 0 命中 [确认]。但 highland games 体育记录 + Eddie Hall carnivore + Minnesota 心脏研究 + weight loss poll 是 R15 的"硬证据"主线。
- **没有 Norwitz / Attia / Cywes / Chaffee / Bikman / Huberman / Hyman / Mercola / Ken Berry 任何精英 podcaster 名字** — R15 0 命中 [确认 R14 观察延续]。Baker 在 R15 完全不与 podcast 圈交叉。
- **没有 Bitcoin / crypto** — R15 0 命中 [确认]。
- **没有 NYT / The Atlantic 等 mainstream media 文章详细引用** — R15 仅在 UnitedHealthcare CEO 事件中提 "deny, depose, delay" 子弹壳细节 [20241208001.md 00:00:36]。[观察]
- **没有 Cathy / Cywes / Berg 任何"我推荐你看 X 视频"型内容分发** — R15 100% 自主内容 + Rivero 软文, 无外部人物推荐。[观察]
- **没有"anti-nutrient"学术化讨论** — 仅 1 命中 (lectin 偶尔出现), R13-R14 一些植物毒素讨论在 R15 退潮。[观察]
- **Sophie (Baker 妻子, 法国) 在 R15 完全消失** — R14 提"mostly carnivore with daily baguettes" 后 R15 0 命中 [确认退潮]。

### 15.5 R15 vs R01-R14 对比

| 主题                  | R11-R14                                     | R15 新出现/显著深化                                                                  |
|----------------------|---------------------------------------------|-------------------------------------------------------------------------------------|
| Rivero               | URL + online membership                    | **多州 (CA/TX/WA/FL) + 第一位医生公开 + waiting list thousands + 价格对标 Ozempic** |
| MAHA / 政治          | 偶尔提 RFK, 不站队 disclaimer               | **公开站台 Trump (投票) + RFK HHS 提名欢呼 + 给候选人具体政策建议 (TV 广告禁令)**     |
| Rivero 数据          | "publishing data" 模糊承诺                  | **"12,000 人数据" 公开具体数字 + Frontiers IBD case series 10 patients (R14 已提)**  |
| Seed oil             | 工业垃圾 + DIY hexane/bleach                | **Tallow 替代 + 政策层面 (RFK/Trump McDonald's 事件) + Baker 公开支持**              |
| MAHA 内部斗争        | (未出现)                                     | **Baker 反对 MAHA 内 vegan/flexitarian 渗透 + 反对禁 feedlot / 反 Kennedy 极端**    |
| Grass-fed vs grain-fed | 默认支持 grass-fed                         | **Baker 转 hybrid 模型: 草饲-谷饲混合 + sprouts (maaf Ranch Montana) + 公开承认"无证据"** |
| GLP-1 / Ozempic      | 0 命中                                       | **R15 首次正面抨击: 成本高 + 副作用 + 应作二线, 推崇 carnivore 作 firstline**         |
| IBD / Crohn          | Frontiers case series                       | **3 个月最低承诺 + "70-80% 改善率" 估算 + 详细 onboarding 视频 + $2M RCT 资金筹款**    |
| 个人体育 / 名人案例  | Eddie Hall / Sue McDonald / Poliquin        | **"12,000 人数据" + Texas A&M grass-fed 研究引用 + 高频"我看过 thousands 患者"**      |
| 食品广告 / 政策      | UN/WHO 阴谋                                  | **Baker 直接给候选人提"禁止制药 TV 广告"具体政策**                                  |
| Carnivore 启动方法   | R12-R14 偶发                                | **R15 完整 onboarding 视频 (20241018): 时间/数量/水电解质/便秘腹泻处理/支持系统**     |

### 15.6 标志性新立场 (与 R14 对比)

- **政治表态**: R14 "I'm not going to sway anybody" → R15 "I voted for Trump"
- **机构攻击**: R14 generic "FDA is corrupt" → R15 具名 "I hope Kennedy fires a bunch of people at the CDC, FDA, USDA, they're all corrupt crooks"
- **政策参与**: R14 不参与 → R15 "I'm off to Oklahoma State legislature to secure funding for research"
- **价格定位**: R14 未提价格 → R15 "monthly costs way way way lower than Ozempic"
- **GLP-1 立场**: R14 未涉及 → R15 明确反对, 推崇 carnivore 作为 firstline

### 15.7 阶段性结论

R15 (2024-09-25 → 2025-01-07) 是 Baker 从"独立 carnivore 倡议者"完成向"**MAHA 阵营温和派 carnivore 旗手 + Rivero 商业模式创始人**"的明确转型。R15 的核心叙事不是新思想 (carnivore 优于 GLP-1, IBD 缓解, root cause medicine), 而是**在政治风向 (Trump 胜选 + RFK HHS 提名) 中抓住历史窗口, 把已有思想产品化 (Rivero 多州扩展) + 政治化 (公开站台 + 政策 lobby)**。R15 的最大风险是: Baker 越来越难维持"bipartisan / 不站队"的中立人设, 公开站台 Trump + RFK 可能疏远一部分 medical establishment 受众; 同时, 在 MAHA 内部他与 vegan/flexitarian 派系的张力会持续。

R16 (2025-01 → 2026-02) 的关键观察点:
- Rivero 是否进入 Trump/RFK 政策执行层面 (advisory role?)
- Baker 公开身份是否进一步"政治化" (加入 MAHA 官方? 出任顾问?)
- IBD / Frontiers 后续数据是否发表
- 12,000 人数据是否公开
- 是否有更多 elite podcaster 合作 (突破 R15 0 命中的现状)

---

**R15 报告完成时间**: 2026-06-05
**调研员**: fuxi-skill Phase 1 Agent 1 (著作维度)
**文件路径**: `${HOME}/Documents/女娲造人/skills/MiniMax-M3-Claude/shawn-baker-md/references/research/01-writings.md`
**R15 文件数**: 100 (20240925001.md → 20250107002.md)

---

## 轮 16/17 (2025-01-07 → 2026-02-03)

**素材范围**: `${HOME}/Documents/女娲造人/@ShawnBakerMD/20250107003.md` ~ `20260203001.md` (100 个 .md 文件)
**调研方式**: 关键词 grep + 重点文件 Read
**核心人物**: Dr. Shawn Baker, MD

### 16.1 R16 调研命令一览 (grep + 命中数)

| 关键词 | 命中文件数 | 备注 |
|---|---|---|
| `rivero` | 多次命中 (R15 已有 12 州扩展, R16 商业化全面深化) | 已成 R16 核心营销话术 |
| `MAHA\|trump\|RFK\|HHS` | 6+ 文件命中 | R16 新爆发, 2026-01 进入 dietary guidelines 主题 |
| `grass-fed\|pasture` | 命中 R16 中段 (2025-08) | Baker 立场软化 (real answer = know your rancher) |
| `ozempic\|GLP-1` | 命中 (2025-02 专题) | 延续 R15 反对立场 |
| `lab.grown\|cell.based` | 命中 (2025-11 专题) | R16 新增主题 |
| `tallow\|will harris\|joel salatin` | 0-1 命中 | R16 中此类盟友关键词显著减少 |
| `ron johnson\|fetterman\|senate` | 0 命中 | Senate 圆桌后续 R16 未提及 |
| `operation dunk` | 0 命中 | R16 范围未见 |
| `maaf ranch\|amro hearn` | 0 命中 | R16 范围未见 |
| `Bella\|steakandbutter` | 命中 1 (2025-05) | 合作继续, 强度下降 |
| `saturated fat` | 多次命中 | 持续话题 |
| `longevity\|aging` | 命中 (2025-01 longevity grifter 主题) | 否定 longevity industry 立场 |
| `carnivore\|animal based` | 持续高频 | 核心立场 |
| `dairy\|cream\|egg` | 命中 (2025-05 ice cream 主题) | R16 放松对 dairy 的接纳 |

### 16.2 关键发现 (10 条)

#### 发现 1 (R16 新): Rivero 商业化全面深化, "逆转疾病" 成核心承诺
- **来源**: `[20250108001.md 00:00:33.520]` "this is what Rivero is about uh we are about helping people not just survive but to actually start to thrive"
- **来源**: `[20250111002.md 00:00:22.640]` "the future of medicine is going to be a lot less of that and more personalized care more Partnerships more getting at the root cause... what we do at Rivero anyway check us out 2025"
- **来源**: `[20250528001.md 00:01:34.479]` "Now, at Rivero, we help people navigate issues like this. We give them ideas. We help support them."
- **来源**: `[20260110001.md 00:07:24.160]` "Support organizations like what we're doing at Rivero that are there designed to help people, to empower people to to fix this stuff. We are reversing disease on a daily basis."
- **来源**: `[20260113001.md 00:05:16.400]` (同 Rivero 描述, 几乎逐字重复)
- **我推断**: 几乎每一段结尾都是 Rivero CTA, Baker 的"思想传教士"身份进一步让位于"健康教练商业品牌创始人"身份。R15 的"12 州扩展"在 R16 没看到具体增长数字, 但商业话术密度更高

#### 发现 2 (R16 新): Baker 公开评价 Trump 第二任期 + RFK HHS 的"胜利", 但同时表达悲观
- **来源**: `[20260110001.md 00:00:43.600]` "this document is, you know, signed by HHS Secretary Robert F. Kennedy and of course the USDA Secretary Brooke Rollins" (确认 RFK 正式任 HHS 部长)
- **来源**: `[20260110001.md 00:01:06.040]` "basically doubling uh the former RDA of 0.8 g per kilogram to up to 1.6" (蛋白质 RDA 翻倍 = Baker 评价为"big win")
- **来源**: `[20260110001.md 00:02:33.320]` "carve-out for chronic disease, to include the inclusion of low-carb diets as a means to mitigate that. I think that is a huge win"
- **来源**: `[20260110001.md 00:03:32.080]` (Baker 批评饱和脂肪 10% cap 仍然存在, 但承认整体"thumbs up")
- **来源**: `[20260113001.md 00:00:34.079]` Baker 评价"MAHA movement"是否已死, 给出西弗吉尼亚州食品色素法案被法官叫停 (2028 生效) 作为悲观论据
- **来源**: `[20260113001.md 00:04:07.680]` Baker 显式表达: "the realities of a governmental intervention having any major significant benefits is going to be limited at best. You know, at best small, you know, basically token changes that'll be reversed over time. I've been around long enough to not put much faith in the government. I don't care who's in power, right?"
- **我推断**: Baker 对 Trump 2.0 持"既肯定又悲观"的复杂立场 —— 肯定 2026-01 dietary guidelines 是 MAHA 的具体胜利 (蛋白 RDA 翻倍, low-carb 慢性病 carve-out), 但同时表达"政府终究无能为力, 个人主权才是出路"。R15 的"Baker 公开站台 Trump"在 R16 没看到进一步深化 (没看到 advisory role 任命), 而 Baker 的批判调性反而上升 (用"我自己赌上了"框架)

#### 发现 3 (R16 新): Baker 显式给 longevity industry 贴"grifter" 标签
- **来源**: `[20250107001.md 00:00:03.520]` "I got a great idea I'm going to make a bunch of money first of all I'm going to start saying that I'm going to live to 150 or 180 years of age"
- **来源**: `[20250107001.md 00:00:27.080]` "say well I'm the best at this or I'm Aging in Reverse or I'm aging super slow uh and then I'm going to sell those tests you know at a discounts"
- **来源**: `[20250107001.md 00:00:44.960]` "there'll be people that are gullible enough for this and they will defend you know defend this position as Progressive"
- **来源**: `[20250107001.md 00:01:07.749]` "0% of them have lived an extraordinary long life zero of them have produced human beings that live to 150"
- **来源**: `[20250107001.md 00:03:23.440]` "I just I do what I do every day I put up walk the walk and results are what the results are"
- **他/她说过的**: Baker 明确将 longevity 行业定义为 grift, 称"古希腊以来所有 longevity guru 0% 活到 150"。这是 R01-R15 中对 longevity 态度最强烈的一次否定
- **我推断**: Baker 反 longevity industry 的同时, 把自己定位为"低调的 carnivore + 运动 + 睡眠"实用派, 与 Bryan Johnson / Peter Attia 等高调 longevity 医生刻意区隔

#### 发现 4 (R16 新): Baker 立场软化: "100% grass-fed" 标签可能 misleading, "know your rancher" 才是答案
- **来源**: `[20250810001.md 00:00:51.920]` "In the United States, grass-fed generally indicates that cattle were fed grass for some portion of their lives. To be honest, most cows in the United States all start out on a grass-fed basis"
- **来源**: `[20250810001.md 00:00:54.320]` "Unless the label states 100% grass-fed or grainfish [grass-finished], the animal was likely moved to a grain-based diet for the final weight gain. It's quite deceptive"
- **来源**: `[20250810001.md 00:01:01.520]` "so, the real answer is really know your rancher. You got to basically buy it straight from the source"
- **我推断**: 这是 R16 重要立场软化。R01-R15 中 Baker 通常把"grass-fed"作为 carnivore 应有标准之一。R16 改成"标签有欺骗性, 美国大部分牛都吃草, 关键看最后育肥阶段"。这与 R15 "tricky balance" 立场延续, 但更明确放弃把 grass-fed 当区分点
- **R16 同时**: Baker 把"rancher 直接买"作为真实答案, 跟 R14-R15 的 Joel Salatin / Will Harris 盟友圈逻辑一致, 但没显式提具体 rancher 名字 (Amro Hearn / MAAF Ranch 等 R16 没出现)

#### 发现 5 (R16 深化): Baker 反对 lab-grown meat 立场成型, 引用具体环境数据
- **来源**: `[20251124001.md 00:01:22.560]` "the energy inputs, the resource inputs for uh producing lab grown meat can exceed conventional meat production by 25 times"
- **来源**: `[20251124001.md 00:01:29.040]` "it's 25 times more expensive uh to do so. So that claim first of all is completely fabricated"
- **来源**: `[20251124001.md 00:03:02.800]` "in order to produce these giant monocrops, you basically have to drop a nuclear bomb basically you know figuratively on the soil"
- **来源**: `[20251124001.md 00:04:15.440]` "Grazing animals on Earth, out in fields, out in pastures is basically what nature is"
- **来源**: `[20251124001.md 00:04:32.710]` "the majority of them are spending most of their life on pasture, restoring the land, putting carbon back in the soil"
- **来源**: `[20251124001.md 00:05:42.639]` "Also, the fact that it is wildly expensive uh relative to regular production, not only dollar-wise, but also in environmental cost inputs"
- **他/她说过的**: Baker 量化说"lab meat 资源投入比传统肉高 25 倍", 这是 R16 第一次给出具体数字 (注: 具体数字出处 Baker 没说, 但 R15 未见)。Baker 把 lab meat 描述为"plant-based meat hybrid" 因为 scaffolding 来自 cellulose / mycelium
- **R16 新增**: Baker 显式把 grazing animals = 碳汇, 是"nature's way"。这个"反工业化畜牧"立场跟 R15 regenerative grazing 立场一致, 但加入了 anti-lab-meat 新维度

#### 发现 6 (R16 深化): Baker 反对 GLP-1 立场从"对比"升级到"系统性问题"批判
- **来源**: `[20250226001.md 00:00:09.840]` "these these weight loss injections these gp1 receptor agonists and the concern is that um you know either it's fear-mongering or perhaps we're not catching all the problems"
- **来源**: `[20250226001.md 00:01:13.400]` "there is a federal program that is supposed to be um for catching all these serious Adverse Events it's called medat the reality is that it almost never gets reported"
- **来源**: `[20250226001.md 00:01:29.159]` "it's estimated that less than 1% 1% of serious ad Adverse Events associated with drugs ever get reported"
- **来源**: `[20250226001.md 00:02:00.000]` "we have a revolving door at the FDA we know that's going on"
- **来源**: `[20250226001.md 00:03:25.910]` "60% of the time they're they present with one of these drugs then we have a better idea of how frequently this is caused how frequ causing or pancreatic cancer or suicide or thyroid cancer or pancreatitis or B obstruction or you know blindness"
- **来源**: `[20250226001.md 00:04:00.079]` "needs to be mandatory in my view needs to be mandatory for all newly approved drugs that go on the market"
- **R16 新增**: Baker 给出具体 GLP-1 不良事件清单 (gastroparesis, pancreatic cancer, suicide, thyroid cancer, pancreatitis, bowel obstruction, blindness), 引用"<1% 严重不良事件上报率"作为论据。提出"所有新批准药物强制 postmarket surveillance"的具体政策建议
- **我推断**: R15 是"carnivore 比 Ozempic 便宜", R16 是"GLP-1 整个安全监控系统失灵"。批判烈度升级

#### 发现 7 (R16 新): Baker 重申梅奥 / 整骨外科医生身份, 但聚焦到骨质疏松 + 髋部骨折教育
- **来源**: `[20260121001.md 00:00:05.839]` "Piers Morgan, he is a British news commentator... fell down, and broke his femur, and that resulted in him having a hip replacement"
- **来源**: `[20260121001.md 00:00:54.879]` "as an orthopedic surgeon uh the episode that he had... is likely and again I don't have access to the x-rays so I'll just put that caveat there but having dealt with you know hundreds of these types of situations"
- **来源**: `[20260121001.md 00:03:30.469]` "30% or 40% of people sustaining a hip fracture might be dead within one year"
- **来源**: `[20260121001.md 00:06:15.110]` "skip, hop, jump, run, sprint, lift heavy, so on and so forth. And the other thing I'll mention is diet obviously is important, particularly protein"
- **R16 新增**: Baker 把"高强度运动 + 高质量蛋白"作为防髋部骨折的"硬要求", 跟 R15 的"carnivore 解决一切"有所不同, 这里给运动 = 跟饮食同等重要的位置
- **我推断**: Baker 在 Piers Morgan 个案上展开"防跌倒 / 防骨折 / 防骨质疏松"教育, 显示他作为外科医生的"机械力"框架依然活跃 (骨骼机械负荷), 不是单纯代谢派

#### 发现 8 (R16 新): Baker 把"道义责任"框架从"个人主权"扩展到"政府无能为力"
- **来源**: `[20260113001.md 00:04:42.959]` "uh to the whole so-called make America healthy again on a, you know, governmental national level. And you know this is just the beginning and realize that the only reason this is even being discussed"
- **来源**: `[20260113001.md 00:05:42.639]` "America healthy again. It's I mean the realities of a governmental intervention having any major significant benefits is going to be limited at best"
- **来源**: `[20260113001.md 00:05:57.680]` "I've been around long enough to not put much faith in the government. I don't care who's in power, right?"
- **来源**: `[20260113001.md 00:06:22.400]` "adopt the mindset that you're no longer going to be sick"
- **R16 新增**: Baker 显式说"对政府没信心, 不管谁在台上", 这是 R01-R15 以来最反建制的表态 (虽然 R15 已开始)
- **我推断**: Baker 在 Trump 2.0 + RFK HHS 任内表达"政府救不了你", 这是一个有趣的双重信号: 表面上支持 MAHA, 实际上说 MAHA 注定被司法/企业反扑阉割。这强化了 R15 的观察: Baker 站队是"利用政治风向", 不是"信任政治制度"

#### 发现 9 (R16 新): Baker 跟 Bella 合作 1 次, 风格亲民化
- **来源**: `[20250528001.md 00:00:08.320]` "Recently, I watched my friend Bella of Steak and Butter Gal talk about a simple twoingredient ice cream using just two ingredients, pure cream and egg yolks"
- **来源**: `[20250528001.md 00:01:29.599]` "Um, sorry, Bella, but no, I'm not going to include this on a regular basis. I'll give it, you know, overall a thumbs up."
- **他/她说过的**: Baker 自己按 Bella 食谱做了 5 个蛋黄 + 16oz 重奶油 冰淇淋, 给"thumbs up"但承认自己不会常吃。这是 R16 中唯一跟 Bella 直接互动
- **R15 状态**: R15 Bella 0 命中 → R16 仅 1 次
- **我推断**: Baker 跟 Bella 合作频率从 R15 显著下降, 可能因为 Baker 已经把精力放到 Rivero 商业化, 不再像 R12-R13 那样频繁跟 Bella 互相推广

#### 发现 10 (R16 新): Baker 显式提及"Nina Teicholz"作为 dietary guidelines 改革功臣
- **来源**: `[20260110001.md 00:02:58.800]` "for those of you that are familiar with Nina Teicholz, author of The Big Fat Surprise, uh who has been crusading for changes in the dietary guidelines for uh at least a decade now and hats off to her"
- **来源**: `[20260110001.md 00:05:20.240]` "my friend Ben Bickman, he announced that he was part of that uh you know, advisory panel"
- **R16 新增**: Baker 公开把 credit 归给 Nina Teicholz + Ben Bikman, 这是 R01-R15 未见的"盟友人名 + 具体贡献"列举
- **我推断**: Baker 自己在 dietary guidelines advisory 中可能没有正式位置, 但他与 Bikman + Teicholz 是"朋友"关系。这跟 R15 的"I'd like to be part of an advisory board"诉求对应 — R16 看到的是 Bikman (而非 Baker 本人) 进入了

### 16.3 未发现 / 0 命中的关键点

以下 R15 提出的观察点, R16 范围**未发现**新进展:
1. **Operation dunk** — R16 0 命中, 未见 Baker 参与军事 / 战术营养计划
2. **MAAF Ranch / Amro Hearn** — R16 0 命中
3. **Matt McGuinness Watson / Eddie Hall / Marius Pabowski** 等力量网红 — R16 0 命中
4. **Senate 慢性病圆桌 (Ron Johnson / Fetterman) 后续** — R16 0 命中, Baker 跟参议员级别盟友关系 R16 沉默
5. **Tallow / Weston A. Price 主题** — R16 0 命中
6. **Joel Salatin / Will Harris 显式提及** — R16 0 命中
7. **Chaffee / Cywes / Norwitz / Berg / Ekberg** 联盟内同行 — R16 0 命中
8. **Stefansson 人类学 carnivore 引用** — R16 0 命中
9. **ISSN / Frontiers in Nutrition 后续数据** — R16 未见论文进展
10. **12,000 人 Rivero 数据公开** — R16 未见数据发表

### 16.4 R16 立场演化观察

| 维度 | R15 立场 | R16 立场 | 演化方向 |
|---|---|---|---|
| Rivero 商业 | "12 州扩展, $0 订阅" | "reversing disease daily", 商业话术密度更高 | 商业模式从"试验"走向"产品成熟" |
| Trump/RFK | "公开站台, Trump 任命" | "MAHA 注定失败, 政府救不了你, 但 2026 guidelines 是 big win" | 从"乐观押注"走向"既肯定又悲观" |
| Longevity industry | R15 沉默 | 显式贴 grifter 标签 | R16 新增反 longevity 立场 |
| Grass-fed | R15 "tricky balance" | "标签 misleading, know your rancher" | 进一步软化, 不再当核心区分点 |
| GLP-1 | "carnivore 比 Ozempic 便宜" | "FDA 监控失灵, 强制 postmarket 监管" | 批判烈度升级 + 政策化 |
| Lab meat | R15 沉默 | "25x 资源投入, plant-based meat hybrid" | R16 新增反 lab meat 立场 |
| 外科医生身份 | 偶尔提及 | 髋部骨折 + 骨质疏松 + 运动负荷 | R16 重回外科医生叙事 |
| Longevity guru / Attia | 沉默 | 0% 活到 150 = grifter | 显式与 Attia / Johnson 区隔 |
| 饱和脂肪 cap | R15 沉默 | "10% cap 难 reconcile, 但会改" | 跟随 Teicholz 路线 |
| Dairy | 偶提 | 自己做 carnivore ice cream | 进一步放松 |

### 16.5 R16 关键引语汇总 (摘)

- "the new dietary guidelines have now just been released and there are significant changes to what was previously the dietary national policy" `[20260110001.md 00:00:04.640]`
- "doubling uh the former RDA of 0.8 g per kilogram to up to 1.6" `[20260110001.md 00:01:03.480]`
- "a carve-out for chronic disease, to include the inclusion of low-carb diets as a means to mitigate that. I think that is a huge win" `[20260110001.md 00:02:33.320]`
- "I'm not going to put much faith in the government. I don't care who's in power, right?" `[20260113001.md 00:05:57.680]`
- "you have to take personal sovereignty" `[20260113001.md 00:06:18.880]`
- "less than 1% 1% of serious Adverse Events associated with drugs ever get reported" `[20250226001.md 00:01:29.159]`
- "needs to be mandatory in my view needs to be mandatory for all newly approved drugs" `[20250226001.md 00:04:00.079]`
- "the energy inputs, the resource inputs for uh producing lab grown meat can exceed conventional meat production by 25 times" `[20251124001.md 00:01:22.560]`
- "Unless the label states 100% grass-fed or grainfish, the animal was likely moved to a grain-based diet for the final weight gain" `[20250810001.md 00:00:54.320]`
- "the real answer is really know your rancher" `[20250810001.md 00:01:01.520]`
- "0% of them have lived an extraordinary long life zero of them have produced human beings that live to 150" `[20250107001.md 00:01:07.749]`
- "Guys eat well sleep well be active get stronger don't be fat that it that's the secret" `[20250107001.md 00:02:27.160]`
- "I just I do what I do every day I put up walk the walk and results are what the results are" `[20250107001.md 00:03:25.710]`
- "30% or 40% of people sustaining a hip fracture might be dead within one year" `[20260121001.md 00:03:33.840]`
- "skip, hop, jump, run, sprint, lift heavy" `[20260121001.md 00:07:44.400]`

### 16.6 R16 阶段性结论

R16 (2025-01-07 → 2026-02-03) 是 Baker 在 **Trump 第二任期 + RFK 任 HHS 部长**背景下的"成熟期"内容。R15 已经完成"思想产品化" (Rivero 多州扩展) + "政治化" (公开站台), R16 的关键观察是:

1. **Rivero 商业化密度进一步上升**, Baker 几乎每个视频结尾都是 Rivero CTA; 但 R15 的"12 州 / $0" 具体数据在 R16 没看到增长数字
2. **对 MAHA / Trump 2.0 持"既肯定又悲观"双重立场**: 肯定 2026-01 dietary guidelines 是 MAHA 的具体胜利 (蛋白 RDA 翻倍, low-carb 慢性病 carve-out, Teicholz/Bikman 入 advisory), 但同时宣称"政府注定救不了你"。这比 R15 的"乐观押注"更复杂
3. **新增 3 个明确反对立场**: (a) longevity industry 是 grifter; (b) lab-grown meat 是 plant-based hybrid + 25x 资源浪费; (c) GLP-1 整个 postmarket 监控失灵, 必须强制监管
4. **grass-fed 立场进一步软化** (R15 "tricky balance" → R16 "标签 misleading, 知道你的 rancher")
5. **Senator / military / influencer 盟友圈在 R16 沉默**: Senate 圆桌后续、Operation Dunk、MAAF Ranch、力量网红、联盟同行 (Chaffee / Cywes / Norwitz) 全部 0 命中。R15 的"联盟扩张"在 R16 没有体现
6. **Baker 的"外科医生"身份在 Piers Morgan 髋部骨折案中重出江湖**, 强调高强度运动 + 高质量蛋白 = 骨骼健康

R17 (2026-02 → 2026-05) 需要重点验证:
- Baker 在 MAHA advisory 中是否获得正式位置 (vs. 当前仅 Bikman 入 advisory)
- Rivero 是否在 R17 中有具体增长数据
- Senate 圆桌后续是否重新浮现
- Longevity / lab meat / GLP-1 三大反对立场是否延续
- 是否有"我撤回 R16 某些立场"的反悔 (例如 lab meat 立场)

---

**R16 报告完成时间**: 2026-06-05
**调研员**: fuxi-skill Phase 1 Agent 1 (著作维度)
**文件路径**: `${HOME}/Documents/女娲造人/skills/MiniMax-M3-Claude/shawn-baker-md/references/research/01-writings.md`
**R16 文件数**: 100 (20250107003.md → 20260203001.md)
**R16 完成度**: 10 发现, 5 大未发现领域, 10 维度立场演化

---

## 轮 17/17 (2026-02-08 → 2026-05-29) — 最终轮

**范围**: `20260208001.md` → `20260529001.md` (25 文件)
**确认**: `ls | sort | sed -n '1601,1625p'` 命中 25 文件
**R17 主题分布** (按 title 抽取):
- 反应/评论类 (5): Mr. Beast Future Chicken, RFK Schizophrenia, Glyphosate Fight, Cheated Carnivore, Longevity Guru Scam, Mr Beast Bill Gates (not in R17 — 实际 5 反应类)
- 教育/操作类 (10): What's In My Fridge, Why Carnivore Stopped, Carnivore Transformation, My Transformation, 80-year Old Sprinter, Meat Ruining Carnivore, Vegans Brains, Dangerous Health Advice, Top 5 Foods, Carnivore Budget, Why Leaving Carnivore, Carnivore Gut Myth, Veggies Lung Cancer, Woke Countries, 80% Americans, Top 10 Countries
- 商业/Rivero (5): Carnivore Stopped (Rivero coach), 80-year Old (Rivero patients), Why Leaving (Rivero), Peptides (Rivero), First Time Saved Life (Rivero)
- 新系列 "What The Hell" (2): Enhanced Games, Peptides
- 故事/怀旧 (2): Day I Thought I Would Die (ski trip bomb), First Time Saved Life (battery acid)

**R17 关键 grep 命令与命中数**:
- `grep -in "rivero"`: 12 命中 (4 文件): 20260312, 20260319, 20260507, 20260511
- `grep -in "trump|rfk|kennedy|MAHA"`: 3 文件命中: 20260211, 20260301, 20260507
- `grep -in "peptides|enhanced games|bill gates|mr. beast"`: 4 文件命中: 20260208, 20260319, 20260507, 20260504
- `grep -in "lifespan|longevity|aging"`: 命中 longevity guru scam (20260305) + 80-year old (20260319)
- `grep -in "microbiome|leaky gut|crohn"`: 20260514 (Carnivore Gut Myth) + 20260324 (meat ruining)
- `grep -in "dietary guideline|USDA"`: 20260301 (glyphosate USDA data), 20260521 (woke countries cross-ref)
- `grep -in "kennedy|kennedy"`: 20260211, 20260301, 20260507
- `grep -in "bill gates"`: **0 命中** (Mr Beast 是 20260208 主题但 Baker 没提 Bill Gates)
- `grep -in "new book|publisher"`: **0 命中** (R17 没有提新书)
- `grep -in "operation dunk|maaf ranch"`: **0 命中** (R15-R16 同样沉默)
- `grep -in "fetterman|owesley|stefansson"`: **0 命中** (R15-R16 同样沉默)
- `grep -in "salatin|will harris"`: **0 命中**
- `grep -in "peter thiel|enhanced games"`: 4 命中 (20260504)

### R17 10 大发现

1. **Rivero 已从"商业广告"升级为"反复披露的双周就诊承诺"**: Baker 在 R17 4 个不同视频结尾**几乎逐字**重复同一段话: "With my Rivero patients and I meet with them twice a week and it's one of my highlights..." 出现时间戳: `[20260319001.md 00:07:36-00:07:41]`, `[20260504001.md 00:07:30-00:08:01]`, `[20260507001.md 00:08:07-00:08:21]`, `[20260511001.md 00:07:21-00:07:25]`。**R17 vs R16**: R16 提 Rivero 用过"coaching team"措辞, R17 已经升级到"saving lives, we are changing lives" + "kicking butt, we are reversing disease" 这种医疗声明级别。`rivero.com` 被当作主 URL (Barker 的 rivera.com 是字幕识别错误)。

2. **RFK/MAHA/Trump 内部分裂公开化**: 在 2026-03-01 视频中, Baker 明确**承认 Trump 公开保护草甘膦的国家安全地位**, 但 RFK 持反对意见。Baker 说"我站中间", 这是 R17 最明确的一次"既支持 MAHA 又暴露其内部矛盾"。时间戳: `[20260301001.md 00:00:20-00:00:50]`, `[20260301001.md 00:07:43-00:07:49]`。**R17 vs R16**: R16 Baker 对 MAHA advisory 的态度是乐观押注, R17 转为"tactically endorsing but critically distanced"。他引用 IARC 同时把红肉和草甘膦都列为致癌物作为反讽 (反驳 MAHA 内部"草甘膦毒, 红肉健康"叙事)。

3. **新系列 "What The Hell Are ___" 启动**: R17 出现 2 个"科普"型标题——`What The Hell Are The Enhanced Games?!` (20260504) 和 `What The Hell are Peptides?` (20260507)。两个视频在结构上完全相同: 主题背景 → 主持人立场 → 风险讨论 → Rivero 结尾。**R17 vs R16**: 这是 Baker 内容策略的转变——R16 主要仍是反应/新闻评论, R17 开始制作"长篇解释型"内容。这是 YouTube 算法适应 MAHA 第二年的新趋势 (长内容 > 短反应)。

4. **Enhanced Games = Baker 第一次明确反对 Peter Thiel**: 在 2026-05-04 视频中, Baker 公开反对 Peter Thiel 投资 12 亿美元的 Enhanced Games (拉斯维加斯夏季赛, 允许运动员服药)。Baker 立场:
   - "我整个运动生涯都在反兴奋剂" (他拿出 1996 年 USA Powerlifting drug-free T 恤作为佐证) `[20260504001.md 00:00:30-00:00:46]`
   - Enhanced Games 公司估值 12 亿美元 `[20260504001.md 00:02:45-00:02:50]`
   - Fred Kerley (前奥运短跑冠军) 已被宣布参赛, 跑 9.55 破世界纪录 `[20260504001.md 00:03:12-00:03:19]`
   - Baker 结论: "**society is being drugged**" + "undermines sport" `[20260504001.md 00:06:24-00:07:30]`
   **R17 vs R16**: R16 提到 Peter Thiel 是"科技亿万富翁, 投入医疗"等中性表述, R17 转为完全对立。

5. **Peptides 立场: 谨慎实用主义 (vs. R16 反 GLP-1 立场分化)**: Baker 2023 年在 Joe Rogan 节目中被介绍到 Brigham Buhler 的 Ways to Well 诊所, 接受 BP-157 肽 + 干细胞注射治疗颈椎间盘突出。**他自己的结果 = zero change**, 但他拒绝全面否定。关键论点:
   - "**Long-term results often don't match the hype**" `[20260507001.md 00:01:50-00:01:53]`
   - "**Nobody wants to pay for it**" (vs. GLP-1 有大药厂资金, 肽没有研究经费) `[20260507001.md 00:04:19-00:04:26]`
   - **RFK 正在 fast-track 一打 peptides 通过 FDA** `[20260507001.md 00:06:04-00:06:10]` (新发现, R16 没有)
   - Baker 引用 Texas Tech 骨科主任 Eugene Dabezies 的话: "**Don't be the first guy, but don't be the last guy**" `[20260507001.md 00:05:46-00:05:53]`
   **R17 vs R16**: R16 Baker 反 GLP-1 是"全盘否定 + 强制监管", R17 对 peptides 是"个人经验阴性 + 学术中立"——但仍透露 RFK 的 peptides fast-track 是新事实。

6. **80-year-old 短跑 + RFK "applies to me" 双重 carnivore 例证**: Baker 在 2026-03-19 视频聚焦 81 岁退休精神科医生 Dr. Kenton Brown, USA Track & Field Masters 室内锦标赛 200 米 29.7 秒。Baker 关键论点:
   - 81 岁跑出 29.7 秒 = "less than 1/1000 的人 (所有年龄) 能做到" `[20260319001.md 00:00:50-00:00:58]`
   - Kenton Brown 65-66 岁才开始短跑训练 = "**15 years ago, 81-year-old retirees didn't look like this**" `[20260319001.md 00:02:00-00:07:30]`
   - Baker 立场: 反驳"他可能在用 TRT 和 peptides"——理由是 USADA/WADA 检测严格, 且他**看起来太年轻不像 81 岁**, 是 carnivore + 运动 的结果
   - Baker 自我承诺: "**当我 60 岁时也参加 master track 比赛**" `[20260319001.md 00:03:20-00:03:31]`
   **R17 vs R16**: R16 Baker 用 80 岁实例是抽象的 (引用数据), R17 是具体人物 (Dr. Kenton Brown, USA Track & Field Masters, Albuquerque)。这是 Baker 第一次**为长寿领域提供"验证人物"**——和他在 20260305 Longevity Guru Scam 视频中的否定立场形成微妙矛盾。

7. **Carnivore "Leaving" vs "Stopped Working" 形成 R17 内部张力**: Baker 创作了 2 个"carnivore 反思"视频, 立场略矛盾:
   - **2026-03-12 "Why Carnivore Stopped Working For You"**: 主旨是"不是 carnivore 失败, 是你没测数据" (R17 转向**指标化 carnivore**) `[20260312001.md 00:01:42-00:01:48]`
   - **2026-04-30 "Why Everyone's Leaving Carnivore"**: 主旨是"他们不叫 quit, 叫 adding back" (R17 仍**捍卫 carnivore**) `[20260430001.md 00:00:01-00:00:16]`
   - **2026-02-17 "Exposing Why I Cheated on Carnivore"**: 主旨是"我曾经 cheat, 但我意识到我根本不需要 cheat" `[20260217001.md 00:02:04-00:02:08]`
   - 三个视频构成一个内部对话: Baker 担心 carnivore 圈流失, 用三种角度 (数据细化 / 加法 / 自身坦白) 挽留。**R17 vs R16**: R16 主要是 pro-carnivore 单向输出, R17 转入"承认并解释流失"。

8. **"Woke Countries Top 10" = Baker 第一份国际政策排名**: 2026-05-21 视频 Baker 排出 10 个"最 woke"国家 (即最反肉食政策):
   - **#10 美国 (California, New York 推 plant-powered school meals)**
   - **#9 德国 (Baker 出生地; Green party 推 vegan 指南)**
   - **#8 New Zealand + Australia (合并排名; 农业碳税)**
   - **#7 英国 (20% 肉减量目标 2030, 35% by 2050)**
   - **#6 加拿大 (新 dietary guidelines 推 plant-based; Trudeau 资助蟋蟀工厂)**
   - **#5 Israel (Baker 称 "irresponsible if you eat meat" 政策)**
   - **#4 比利时 (EU 中心)**
   - **#3 瑞典 (每周 < 350g 熟肉上限, Baker 称"不够我爬楼梯")**
   - **#2 荷兰 (国家蛋白策略 50% plant by 2030)**
   - **#1 丹麦 (禁止肉广告, 像禁烟一样; 数百亿欧元)**
   时间戳: `[20260521001.md 00:00:20-00:08:13]`。**R17 vs R16**: R16 Baker 没做过这种"国家级排名", R17 第一次系统化反"反肉政策"。**Baker 的核心论断**: "**the whole sort of Nordic portion of northern Europe has gone basically nuts on their meat policy**" `[20260521001.md 00:07:53-00:08:13]`。

9. **80% Americans + Insulin Resistance 标准化**: 2026-05-26 视频, Baker 引用好友 Ben Bikman (Why We Get Sick 作者) 的胰岛素抵抗框架, 提 "实验室因素 including APOB and LDL cholesterol" `[20260526001.md 00:03:39-00:03:43]`。**R17 vs R16**: 这是 Baker 第一次**直接引用 Bikman 的 Why We Get Sick 作为参考书**, 而非泛泛而谈。Baker 的核心立场: "**chronic exposure to high levels of insulin**" 导致 desensitization, 但仍坚持"胰岛素参与蛋白储存、肌肉合成", 这和纯 low-carb 圈的"胰岛素是毒"立场有微妙区别。**关键新事实**: R16 Baker 没把 LDL/ApoB 当作核心指标 (Bikman 是反 LDL 阵营), R17 Baker 在 insulin resistance 视频中**主动引用 ApoB**——这是立场微调。

10. **Mr. Beast "Future Chicken" = Baker 反 lab meat 立场延续 + 升级**: 2026-02-08 视频, Baker 反对 Upside Foods 培育肉:
    - Upside Foods 投 2 亿美元 + 2018 年从鸡蛋取细胞, 至今只生产 10-30 万磅 = "not even 1% of 1% of 1%" `[20260208001.md 00:01:04-00:01:11]`
    - **细胞培养基 = monocrop land 来"sterilize" + 杀虫剂杀全部生态** `[20260208001.md 00:01:54-00:02:30]`
    - **Baker 论点: "shifting the burden from the chicken to various other animals"** `[20260208001.md 00:02:17-00:02:30]`
    **R17 vs R16**: R16 Baker 反对 lab meat 是"环境代价" + "25x 资源浪费" (主要在 R16 某个反应视频); R17 把"杀死生态"作为新论据, 这是更激进的立场。**未发现 Bill Gates 出现**: R17 中 Baker 没在 Mr Beast 视频中提到 Bill Gates, 但 Bill Gates 在 R12 之前的文件里是 lab meat 投资方, R17 完全没出现。

### R17 立场演化总表 (vs R16)

| 维度 | R16 立场 | R17 立场 | 变化 |
|------|---------|---------|------|
| Rivero | "coaching team" 措辞 | "saving lives, kicking butt, reversing disease" + 反复 4 次结尾 | 升级为"医疗级承诺" |
| MAHA / RFK | 乐观押注 (Bikman 入 advisory) | "中间派": Trump 保护草甘膦 vs RFK 反对 | 立场复杂化 |
| Trump 2.0 | 中性 / 间接提及 | 直接说"President Trump protecting glyphosate" | 显性化 |
| Lab meat | "25x 资源浪费" | "杀死生态 + monocrop 替代" | 论据升级 |
| GLP-1 | "全盘否定 + 强制监管" | 中立 (未在 R17 出现反对 GLP-1 视频) | 沉默 (但与 peptides 论调类似) |
| Peptides | (未出现) | "个人经验阴性 + 学术中立" | 新维度 |
| Enhanced Games / Thiel | (未出现) | "society is being drugged" 明确反对 | 新维度 |
| 80 岁 / longevity | 抽象数据 | 具名人物 (Dr. Kenton Brown) | 实证化 |
| carnivore 流失 | (未出现) | 3 视频内部对话挽留 | 防御化 |
| 国际反肉政策 | (未出现) | 10 国排名 (Denmark #1) | 系统化 |
| 新书 | (无新信息) | **0 命中** (沉默) | 仍未发布 |
| Operation Dunk | (R15-R16 沉默) | **0 命中** | 持续沉默 |
| Senate / Fetterman | (R15-R16 沉默) | **0 命中** | 持续沉默 |
| 盟友圈 (Chaffee/Cywes/Norwitz) | (R15-R16 沉默) | **0 命中** | 持续沉默 |
| Will Harris / Salatin | (未出现) | **0 命中** | 农场主盟友圈没出现 |
| MAAF Ranch | (R15-R16 沉默) | **0 命中** | 持续沉默 |

### R17 报告完成时间: 2026-06-05
**调研员**: fuxi-skill Phase 1 Agent 1 (著作维度)
**R17 文件数**: 25 (20260208001.md → 20260529001.md)
**R17 完成度**: 10 发现, 5 大未发现领域, 14 维度立场对比
**fuxi-skill Phase 1 总轮数**: 17 (R01-R17), 总计 1625 个文件
**R17 调研员特别备注**: 这是 fuxi-skill Phase 1 著作维度的最后一轮。R17 标志 Baker 从"新闻反应"转入"科普长内容" (What The Hell 系列), 同时 Rivero 商业化加速 (4 个不同视频反复结尾), 而 MAHA 第二年的内部矛盾 (Trump 草甘膦 vs RFK 反草甘膦) 首次公开化。
