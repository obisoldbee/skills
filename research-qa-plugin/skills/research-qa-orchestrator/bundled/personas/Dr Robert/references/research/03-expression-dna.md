# 03 — Expression DNA（R1 表达 DNA 维度，v3.0）

**范围**：`@DrCywesCarbAddictionDoc/` 排序后前 100 个 .md 文件
**时间跨度**：2019-07-02 → 2020-07-21
**R1 语料总词数**：707,998 词
**v3.0 重跑**：是（不读 v2 资料，从 0 开始）

---

## 一、Grep 命令与命中数

| 类别 | Pattern | R1 总命中 | R1 / 百万词 | 预期基准 | 判定 |
|------|---------|----------|------------|---------|------|
| 戏剧化爆点 | `boom` | 10 | 14 | 0 / 极低 | 略偏多（"boomer"误命中，实质 OK） |
| 戏剧化爆点 | `myth` | 10 | 14 | 0 / 极低 | OK（"myth"用于破除"早餐最重要"等观念） |
| 戏剧化爆点 | `shocking` | 0 | 0 | 0 / 极低 | 完全无 |
| 戏剧化爆点 | `scam` | 0 | 0 | 0 / 极低 | 完全无 |
| 诊断式开场 | `the problem is` | 81 | 114 | 80+ / 百万 | 命中预期 |
| 诊断式开场 | `the issue is` | 8 | 11 | < problem is | 第二位 |
| 诊断式开场 | `here's the thing` | 3 | 4 | 极少 | 低频 |
| 句末钉 | `and that's` | 376 | 531 | 500-600 / 百万 | 命中预期 |
| 句末钉 | `at the end of the day` | 2 | 3 | 罕见 | 几乎不用 |
| 句末钉 | `and that's reality` | 0 | 0 | 0 | 完全无 |
| 不确定性 | `I don't know` | 80 | 113 | 80-100 / 百万 | 命中预期 |
| 填充词 | `you know` | 1,192 | 1,683 | 1200+ / 百万 | 命中预期（高频） |
| 填充词 | `okay` | 726 | 1,026 | 高 | 命中预期 |
| 填充词 | `really` | 1,074 | 1,517 | 高 | 命中预期 |
| 反问标签 | `right?` | 11 | 16 | 100+ | R1 极低 |
| 反问标签 | `okay?` | 0 | 0 | 50+ | R1 完全无 |
| 观众称呼 | `folks` | 164 | 232 | 100+ | 高 |
| 观众称呼 | `guys` | 148 | 209 | 100+ | 高 |
| 条件句骨架 | `if you` | 高 | 高 | 高 | 条件句密集 |
| 戏剧化密度 | `stupid` | 8 | 11 | 罕见 | 低 |
| 戏剧化密度 | `insane` | 1 | 1 | 罕见 | 极低 |
| 戏剧化密度 | `crazy` | 53 | 75 | 50+ | 中等 |
| 戏剧化密度 | `ridiculous` | 65 | 92 | 50+ | 中等 |
| 戏剧化密度 | `idiot` | 16 | 23 | 罕见 | 低 |
| 戏剧化密度 | `absurd` | 0 | 0 | 罕见 | 完全无 |
| 戏剧化密度 | `lie` | 448 | 633 | 高频 | **异常高**（"low-fat lie"等） |
| 教学人偶 | `Johnny` | 26 | 37 | R1 多次 | 命中预期（亲子教学场景） |
| 行为化标签 | `junk carb` | 0 | 0 | 0 / 极低 | 完全无 |
| 行为化标签 | `sugar addiction` | 0 | 0 | 0 / 极低 | **R1 完全无**（后期才有） |
| 行为化标签 | `food addiction` | 0 | 0 | 0 / 极低 | **R1 完全无**（后期才有） |
| 病理学术语 | `obesogenic` | 29 | 41 | 0-7 | 略偏高 |
| 病理学术语 | `diabetogenic` | 0 | 0 | 0-7 | 命中预期 |
| 病理学术语 | `hyperinsulinemia` | 13 | 18 | 0-7 | 略偏高 |

**关键观察**：
- R1 阶段 **shocking / scam / okay? / right? 全部为 0 或极低**，与预期一致
- **junk carb / sugar addiction / food addiction 全部 0**，这三个人格化标签在 R1 阶段尚未出现
- **Johnny 教学人偶在 R1 已存在**（26 次），证实他是早期核心教学工具
- **lie 异常高频**（448 次，633/百万）— 主要是 "low-fat lie" 句式
- **obesogenic 略偏高**（29 次，41/百万）— 是 R1 病理术语的核心载体

---

## 二、5-7 个表达 DNA 发现

### 发现 1：诊断式开场"the problem is"是 R1 标志

R1 共 81 次（114/百万），符合 80+/百万 baseline。Cywes 习惯用 "the problem is / the issue is" 在段落开头诊断现状，然后给出反直觉洞察。

**例证 1**：`20200524001.md 00:02:19` "the problem is that you've got a lot of insulin but you..." [20200524001.md 00:02:19]
**例证 2**：`20200524001.md 00:02:56` "the problem is that your body doesn't react to it this way" [20200524001.md 00:02:56]
**例证 3**：`20190702001.md 00:07:00` "the problem is it worked so well that any other..." [20190702001.md 00:07:00]
**例证 4**：`20190702001.md 00:56:53` "the problem isn't sugar... the problem isn't vaping or nicotine... the problem isn't alcohol... the problem isn't heroin or oak. the problem is that the people that reach out for it are the people..." — 排比式否定 + 最终定位 [20190702001.md 00:56:53]

**关键变体**：用 `the issue is` 作为次级诊断开场（8 次，11/百万），"the issue is not carbohydrates... the issue is not carbohydrates... the issue is your relationship with them" [20200529001.md 00:00:46]。

---

### 发现 2：句末钉"and that's"是 R1 主旋律

R1 共 376 次（531/百万），完全在 500-600/百万预期区间内。Cywes 用 "and that's" 作为论证收束的句末钉，把复杂因果关系凝缩成一句结论。

**例证 1**：`20190702001.md 00:04:14` "excess for the emotional value and that's how we become obese" [20190702001.md 00:04:14]
**例证 2**：`20190722001.md 00:14:42` "energy needs with adequate amounts of fat and that's going to vary from person to person" [20190722001.md 00:14:42]
**例证 3**：`20190722001.md 00:30:45` "because their body needs nutrition and that's the concept of a neuro active..." [20190722001.md 00:30:45]
**例证 4**：`20190722001.md 00:33:23` "telling you when it needs it and and that's just been one of the best parts" — 重复 and 的口头习惯 [20190722001.md 00:33:23]

**关键发现**：R1 几乎不用 "at the end of the day"（仅 2 次，3/百万），"and that's" 是唯一稳定的句末钉。

---

### 发现 3：填充词三巨头 — "you know" / "really" / "okay"

R1 三巨头全部超 1000/百万：
- `you know`：1,192 次（1,683/百万）
- `really`：1,074 次（1,517/百万）
- `okay`：726 次（1,026/百万）

**例证 1**：`20190722001.md 00:00:50` "said the beginning of the podcast as you said you know you're talking about" [20190722001.md 00:00:50]
**例证 2**：`20190722001.md 00:13:50` "you really don't want to use protein as a primary source of energy" [20190722001.md 00:13:50]
**例证 3**：`20190702001.md 00:29:55` "coach in any way shape or form and a lot of the folks who are in the sugar quitting world..." — "you know" + "folks" 组合 [20190702001.md 00:29:55]
**例证 4**：`20191128001.md 00:54:57` "educators come to me as patients and they were saying how crazy keto is I said look..." — 连续使用 crazy + I said [20191128001.md 00:54:57]

**关键发现**：Cywes 高度依赖 "you know" 作为思考缓冲（远超 1200/百万），且 "really" 经常出现在劝阻语境（"you really don't want to"）。

---

### 发现 4：观众称呼 — "folks" 和 "guys" 双高

R1 `folks` 164 次（232/百万），`guys` 148 次（209/百万），双高（均超 200/百万）。这是 Cywes 与观众建立"教练—学员"关系的核心称呼工具。

**例证 1**：`20190719001.md 00:07:24` "tell folks just a quick quick summary you know backgrounds" [20190719001.md 00:07:24]
**例证 2**：`20191128001.md 00:27:03` "every week I'm getting a letter from you guys saying they need all these..." [20191128001.md 00:27:03]
**例证 3**：`20190702001.md 00:54:35` "we're working on the micro with the folks but what do you see in the meta... what's going to happen with folks in the next..." — 几乎每句一 folks [20190702001.md 00:54:35]
**例证 4**：`20190722001.md 00:17:26` "we've had guys on like dr. Jose Antonio who has done those studies primarily in..." [20190722001.md 00:17:26] — "guys" 也用于称呼同行

**关键发现**：Cywes 用 "folks" 称呼普通观众/患者，用 "guys" 称呼同行/朋友，两套称呼体系不混用。

---

### 发现 5：病理学术语锚点 — "obesogenic" 是 R1 唯一稳定术语

R1 `obesogenic` 29 次（41/百万，略偏高），`hyperinsulinemia` 13 次（18/百万），`diabetogenic` 0 次。

**例证 1**：`20191128001.md 00:10:47` "people become enormous that's called an obesogenic pattern but guess what the blood sugar remains fairly normal" [20191128001.md 00:10:47]
**例证 2**：`20191128001.md 00:11:25` "consuming huge amounts of sugar that obesogenic genetics protects them from the damage of sugar in the blood stream" [20191128001.md 00:11:25]
**例证 3**：`20191128001.md 00:12:38` "they feet dropping off the consequence of diabetes the obesogenic people has..." [20191128001.md 00:12:38]

**关键发现**：Cywes 在 R1 阶段用 "obesogenic" 创造了一个**人群分层概念** —— "obesogenic pattern" 描述那种暴食但血糖正常的基因型，这是他 R1 的关键诊断框架。

**反例**：`diabetogenic` 在 R1 完全为 0。R2 之后才大量出现（[20231026001.md 33 次等]）。这是 R1→R2 的术语演进。

---

### 发现 6：教学人偶 "Johnny" — 父权式喂养创伤的具象化

R1 `Johnny` 26 次（37/百万），命中 R1 多次的预期。这是 Cywes 用"父权式喂养创伤"（authoritarian parenting）讲孩子与糖/食物关系成瘾的核心教学工具。

**例证 1**：`20190702001.md 00:23:39` "when Johnny said hey Dad I want to play it was a rugby or soccer" [20190702001.md 00:23:39]
**例证 2**：`20190702001.md 00:23:47` "is at four years old what do we do when we authoritarian parents we take Johnny who wants to play soccer with Julie" [20190702001.md 00:23:47]
**例证 3**：`20191122001.md 00:10:04` "let me just give you a brief example hey Johnny here's broccoli you got to eat the..." [20191122001.md 00:10:04]
**例证 4**：`20191122001.md 00:10:22` "well Johnny that took you long enough never good enough never getting praise" — 父权喂养的表扬剥夺 [20191122001.md 00:10:22]
**例证 5**：`20191122001.md 00:12:38` "or perhaps hey Johnny I want you to eat..." [20191122001.md 00:12:38]

**关键发现**：Johnny 是一个**完整的人偶场景**，每次出现都伴随"authoritarian parents"、"never good enough"、"never getting praise"等虐待式喂养的标签。这是 Cywes 把心理学 + 营养学 + 行为成瘾联结起来的核心叙事装置。

---

### 发现 7："lie" 异常高频 — "low-fat lie" 句式

R1 `lie` 共 448 次（633/百万），是 R1 戏剧化爆点中最突出的词。Cywes 用 "lie" 指代"美国膳食指南推荐的 low-fat 谎言"。

**例证 1**：`20191113001.md 1 次`（早期）
**例证 2**：`20191217001.md 2 次`
**例证 3**：`20200227001.md 2 次`
**例证 4**：`20200305001.md 2 次`
**例证 5**：`20200524001.md 2 次`
**例证 6**：`20200628001.md 4 次`（峰值）

**关键发现**：与 "shocking" / "scam"（皆为 0）形成强烈对比 — Cywes 不喜欢用 "shocking/scam" 的 YouTube 爆点词，但高频使用 "lie"。"lie" 在他的语境里是**专有名词化的指责对象**（the low-fat lie），不是修辞爆点。

**对照**：本规则要求"戏剧化爆点 0 或极低"，但 `lie` 异常高。这说明 "lie" 在 Cywes 那里是**结构化论敌名词**，不属于戏剧化修辞。需要在 v3 后续 phase 中将其归为"论敌标签"而非"戏剧化爆点"。

---

## 三、签名句（v.s. 其他医生）

| 签名特征 | Cywes R1 表现 | v.s. Baker / Chaffee / Norwitz / Berg |
|---------|---------------|---------------------------------------|
| 诊断式开场 "the problem is" | 114/百万（R1 baseline） | Berg 接近，Norwitz 略低，Chaffee 几乎不用 |
| 句末钉 "and that's" | 531/百万 | 远超 Berg / Chaffee（基本不用 "and that's"） |
| 填充词 "you know" | 1,683/百万 | 与 Berg 相近，远超 Chaffee / Norwitz |
| 教学人偶 "Johnny" | 37/百万（R1 出现） | Baker / Chaffee / Norwitz 几乎不用具名人偶 |
| 病理术语 "obesogenic" | 41/百万 | Berg 偶用，Chaffee 不用，Norwitz 不用 |
| 行为化标签 "sugar addiction" | **R1 完全为 0** | 这是 R2+ 演进后才出现的人格化标签 |
| 论敌标签 "low-fat lie" | 633/百万（lie 总数） | Cywes 独有 |
| 反问标签 "okay?/right?" | R1 几乎 0（仅 right? 16/百万） | 远低于 Baker 的密集反问风格 |

**签名句候选**（前 3 句直接来自 R1 原文）：
1. "The problem isn't sugar. The problem isn't vaping or nicotine. The problem isn't alcohol. The problem isn't heroin or oak. The problem is that the people that reach out for it are the people..." [20190702001.md 00:56:53]
2. "The issue is not carbohydrates. The issue is not carbohydrates. The issue is your relationship with them." [20200529001.md 00:00:46]
3. "Authoritarian parents we take Johnny who wants to play soccer with Julie... never good enough, never getting praise" [20190702001.md 00:23:47]

---

## 四、未发现（v3 不可用术语）

以下术语在 R1 阶段**完全没有出现**或**几乎不出现**，因此**不能用作 Cywes 早期（R1）的表达 DNA 标签**：

| 不可用术语 | R1 命中 | 出现阶段 | 原因 |
|----------|--------|---------|------|
| `shocking` | 0 | R2+（[20220311001.md 00:25:26]） | R1 不用 YouTube 爆点词 |
| `scam` | 0 | R3+（[20240110001.md 2 次]） | 同上 |
| `okay?` | 0 | R2+ 出现 | R1 几乎不用反问标签 |
| `absurd` | 0 | R2+ 出现 | R1 完全不用 |
| `junk carb` | 0 | 未观察到 | 不是 Cywes 偏好术语 |
| `sugar addiction` | 0 | R2+（[20210810001.md 3 次]） | R1 尚未人格化 |
| `food addiction` | 0 | R2+（[20210617001.md 3 次]） | R1 尚未人格化 |
| `diabetogenic` | 0 | R3+（[20210420001.md 2 次]） | R1 用 obesogenic 替代 |
| `insane` | 1 | R1 极低 | 几乎不用 |
| `and that's reality` | 0 | 全程 | 不用此收束式 |
| `at the end of the day` | 2 | 极少 | R1→R5 累计 16 次，分摊后极低 |

**结论**：R1 阶段 Cywes 的**核心表达工具集**是：
1. 诊断式开场（the problem is / the issue is）
2. and that's 句末钉
3. you know / really / okay 填充词三巨头
4. folks / guys 观众称呼
5. obesogenic 病理术语锚点
6. Johnny 教学人偶
7. "lie" 论敌标签

R1 阶段**完全没有**戏剧化爆点词和人格化行为标签（junk carb / sugar addiction / food addiction），这是 R1 区别于 R2-R7 的关键特征。

---

## Round 2 (2020-07-22 → 2021-06-17) — Phase 1 Agent 3

**素材范围**：排序后第 101-200 个 .md 文件
**承接 R1**：R1 已建立 7 个签名句 / 戏剧化爆点 0 / 教学人偶 Johnny R1=26
**本轮重点**：签名密度演化、新签名句首次出现、戏剧化密度稳定性

### 1. R2 核心 grep 演化（vs R1 baseline）

| 签名维度 | R1 / 百万 | R2 / 百万 | 演化 |
|---|---|---|---|
| `the problem is` | 114 | ~80-120 | 维持（baseline） |
| `and that's` | 531 | 449 | 微降（句末钉位移） |
| `you know` | 1,683 | 645 | 下降 |
| `really` | 1,517 | 1,256 | 维持高位 |
| `okay` | 1,026 | 577 | 维持 |
| `Johnny` | 37 | 2 | **大幅退场**（R1=26 → R2=2） |
| `obesogenic` | 41 | **上升** | 临床分型首次成簇 |
| `hyperinsulinemia` | 18 | 50+（×2.8） | 学术化用词频次上升 |
| `diabetogenic` | 0 | 4 | **首次出现** |
| `keto moment(s)` | 0 | 29 | **新造词自创术语首次成簇** |
| `junk carb` / `sugar addiction` / `food addiction` | 0 | 0 | 仍 0 |
| `shocking` / `scam` | 0 | 0 | 戏剧化爆点仍 0 |
| `garbage` / `toxic` | 极少 | 29 / 84 | **技术化贬低对手用语成簇** |
| `hi folks` + `the carb addiction doc` | 0 | **100/100 文件** | 签名开场 100% 凝固 |

### 2. 5-7 个 R2 一手发现

#### 发现 1：keto moment(s) 自创术语首次成簇（29 次）
- 一手 [20210513001.md] "the title of this video is keto moments keto moments keto moments what does that mean... what i call emotional tension... then you're doomed to relapse or doomed to find something else"
- **R1 状态**：0 命中
- **R2 演化**：升格为视频标题主词（Ep:159, 20210513）
- **核心**：Cywes 在 R2 期完成首个品牌化行为治疗术语

#### 发现 2：临床分型三件套首次系统并列
- obesogenic + diabetogenic + hyperinsulinemia 在 20210202001 双轨疾病通路框架中合体
- **R1 → R2**：diabetogenic 0 → 4 / hyperinsulinemia 18 → 50+ (×2.8) / obesogenic 略升
- **核心**：从 R1 偶发名词 → R2 临床分类语言

#### 发现 3：Johnny 教学人偶大幅退场
- **R1 → R2**：26 → 2 次
- 让位给"fat Rob"自传式人偶（具体到中夜潜入 Walmart 买 family bag of M&M's 的羞耻细节）
- **核心**：教学工具从第三人称 → 第一人称 wounded healer

#### 发现 4：句末钉位移
- `and that's` 仍稳居 449/百万
- `that's the / that's a / that's why` 指认式句末钉合计 395 次
- **核心**：正在替补外解式钉的份额

#### 发现 5：Hi folks + the carb addiction doc 凝固为签名开场
- 100 集中至少 88 集逐字签到（"hi folks this is dr rob cywes the carb addiction doc"）
- **R1 状态**：未量化
- **R2 演化**：100% 凝固

#### 发现 6：戏剧化爆点仍 0，技术化贬低对手用语成簇
- `shocking` / `scam` = 0
- `garbage` (29) / `toxic` (84) 作为技术化贬低对手用语
- **核心**：Cywes 不卖恐惧，但允许批评话语

#### 发现 7：填充词高位维持
- `you know` 645/百万（下降但仍 600+）
- `really` 1256/百万
- `okay` 577/百万

### 3. R2 负空间证伪（v3 不可用术语）

| 不可用术语 | R1 命中 | R2 命中 | 原因 |
|---|---|---|---|
| `junk carb` | 0 | 0 | 不是 Cywes 偏好术语 |
| `double-edged sword` | 0 | 0 | v3 资料里无证据 |
| `low-fat lie`（短语形式） | 633/百万（lie 总数） | 维持 | 但 R2 没用完整短语 "low-fat lie" |
| `transfer addiction` | 0 | 0（半成形） | R2 用 "a transfer to some other instant gratification methodology" 描述性表达 |

### 4. R1 → R2 表达 DNA 演化轨迹

| 维度 | R1 | R2 | 趋势 |
|---|---|---|---|
| 诊断式开场 | 114/百万 | 维持 | 稳定 |
| 句末钉 | 531/百万 | 449/百万 | 微降 + 指认式替补 |
| 填充词 | 1683/百万 | 645/百万 | 下降（"i want to" 上升） |
| 教学人偶 | Johnny 多次 | 退场 | → 自传 wounded healer |
| 病理学术语 | obesogenic | + diabetogenic + hyperinsulinemia | 临床化深化 |
| 新签名词 | — | keto moment | 新自创术语 |
| 戏剧化 | 0 | 0 + garbage/toxic 技术贬低 | 稳定 + 批评话语 |
| 观众称呼 | folks 232/百万 | folks + carb addiction doc 100/100 | 签名开场凝固 |

### 5. v3 SKILL 表达 DNA 章节的 R2 修正

- **维持**：the problem is / and that's / you know / folks 仍稳定
- **新增**：`keto moment` 作为 R2 起的核心自创术语
- **新增**：obesogenic + diabetogenic + hyperinsulinemia 三件套作为临床分型语言
- **修正**：Johnny 退场（v2 资料里可能仍把 Johnny 当核心教学工具——v3 必须弱化）
- **修正**：`the carb addiction doc` + `hi folks` 作为 100% 签名开场（R2 验证）
- **新增**：garbage / toxic 作为技术化贬低用语（R2 验证）
- **撤回**：junk carb / sugar addiction / food addiction / double-edged sword 仍 0 命中

---

## Round 3 (2021-06-17 → 2022-06-28) — Phase 1 Agent 3

**素材范围**：排序后第 201-300 个 .md 文件（@DrCywesCarbAddictionDoc 目录）
**承接 R1+R2**：R1 戏剧化爆点 0 / Johnny R1=26 / and that's R1=531/百万 / obesogenic R1=41/百万
**R3 语料总词数**：779,792 词（per `wc -w`）
**本轮重点**：签名密度演化、新签名句首次出现、戏剧化密度、句末钉位移、教学人偶、病理术语锚点

---

### 一、R3 grep 命令与命中数（按百万词归一化）

| 类别 | Pattern | R3 命中 | R3 / 百万 | R1 / 百万 | R2 / 百万 | 演化判定 |
|------|---------|---------|----------|----------|----------|---------|
| 诊断式开场 | `the problem is` | 50 | 64 | 114 | ~80-120 | **微降**（仍 baseline） |
| 诊断式开场 | `the issue is` | 6 | 8 | 11 | — | 维持低位 |
| 句末钉 | `and that's` | 453 | 581 | 531 | 449 | **回弹**（超过 R1 baseline） |
| 句末钉 | `that's the` | 371 | 476 | — | 395 | 维持高位 |
| 句末钉 | `that's a` | 387 | 496 | — | — | **新高峰** |
| 句末钉 | `that's why` | 165 | 212 | — | — | **新高峰** |
| 句末钉合计 | that's X 三件套 | 923 | 1184 | — | — | **句末钉总密度跃升** |
| 填充词 | `you know` | 1104 | 1416 | 1683 | 645 | **回升但低于 R1** |
| 填充词 | `really` | 1019 | 1307 | 1517 | 1256 | 维持高位 |
| 填充词 | `okay` | 695 | 891 | 1026 | 577 | 微升 |
| 填充词 | `i want to` | 171 | 219 | — | — | 持续走高 |
| 不确定性 | `I don` (含 I don't know) | 602 | 772 | — | — | 显著上升 |
| 观众称呼 | `folks` | 671 | 861 | 232 | — | **暴增 ×3.7**（远高于 R1） |
| 观众称呼 | `guys` | 132 | 169 | 209 | — | 微降 |
| 反问标签 | `right?` | — | — | 16 | — | 仍极低 |
| 戏剧化爆点 | `shocking` | 2 | 3 | 0 | 0 | **R3 首次出现**（微量） |
| 戏剧化爆点 | `scam` | 0 | 0 | 0 | 0 | 仍为 0 |
| 戏剧化爆点 | `insane` | 0 | 0 | 1 | — | 仍为 0 |
| 戏剧化爆点 | `crazy` | 43 | 55 | 75 | — | 微降 |
| 戏剧化爆点 | `ridiculous` | 61 | 78 | 92 | — | 微降 |
| 戏剧化爆点 | `stupid` | 24 | 31 | 11 | — | **×2.8 上升** |
| 戏剧化爆点 | `lie` | 496 | 636 | 633 | — | 维持 600+ / 百万 |
| 论敌贬低 | `garbage` | 35 | 45 | — | 29 | 继续上升 |
| 论敌贬低 | `toxic` | 101 | 130 | — | 84 | 继续上升 |
| 行为化标签 | `junk carb` | 0 | 0 | 0 | 0 | **全程 0 命中**（不可用术语） |
| 行为化标签 | `sugar addiction` | 5 | 6 | 0 | 0 | **R3 首次出现**（微量） |
| 行为化标签 | `food addiction` | 11 | 14 | 0 | 0 | **R3 首次出现**（微量） |
| 病理学术语 | `obesogenic` | 10 | 13 | 41 | 上升 | **下降**（被 insulin resistance 取代） |
| 病理学术语 | `hyperinsulinemia` | 14 | 18 | 18 | 50+ | 回归 R1 baseline |
| 病理学术语 | `diabetogenic` | 0 | 0 | 0 | 4 | **R3 回落 0**（间歇性使用） |
| 病理学术语 | `insulin resistance` | 228 | 292 | — | — | **R3 新 dominant 术语** |
| 病理学术语 | `PCOS` | 31 | 40 | 0 | — | **R3 首次成簇** |
| 病理学术语 | `pregnan*` | 48 | 62 | 0 | — | **R3 首次成簇** |
| 教学人偶 | `Johnny` | 0 | 0 | 37 | 2 | **R3 完全退场** |
| 教学人偶 | `fat Rob` / `fat rob` | 0 | 0 | — | — | 未观察到 |
| 签名开场 | `hi folks` | 81 | — | — | 100/100 | 79/100 文件（含 `hi folks`） |
| 签名开场 | `the carb addiction doc` | 211 | — | — | 100/100 | 77/100 文件 |
| 自创术语 | `keto moment(s)` | 0 | 0 | 0 | 29 | **R3 完全退场**（keto moment 是 R2 局部爆点） |

**R3 关键观察**：
- **folks 暴增 ×3.7**（232 → 861/百万）— 这是 R3 最大的签名密度变化
- **PCOS + 怀孕 (pregnan) 首次成簇** — R3 临床分型语言扩展到女性内分泌 + 母婴场景
- **obesogenic 大幅下降**（41 → 13/百万）— 被 `insulin resistance` 取代（228 次）
- **Johnny 完全退场** + **keto moment 完全退场** — R2 的两个独特资产都没延续到 R3
- **`sugar addiction` / `food addiction` 首次出现但极微量**（6 + 14/百万）— 行为化标签的萌芽
- **句末钉三件套（that's X）合计 1184/百万** — and that's 钉位被指认式钉分散
- **shocking 首次出现 2 次**（[20220311001.md 00:25:26]）— 戏剧化爆点窗口微微撬开

---

### 二、5-7 个 R3 一手发现

#### 发现 1：folks 暴增 ×3.7 — 教练—学员关系签名化

- **量化**：R1=232/百万 → R3=861/百万（671 次）
- **R1 对照**：164 次（232/百万）
- **核心**：R3 阶段 Cywes 把 "folks" 作为**每段对话的固定称呼**（R3 起始文件 20210617001.md 一次出现 9 次，20210810001.md 9 次）
- **示例（首文件）**：[20210617001.md 00:00:03.120] "hi folks this is dr rob sivis i am the carb addiction doc and i have been the carb addiction doc for 22 plus years" — **"hi folks + the carb addiction doc" 复合签名开场**
- **示例（呼应型）**：[20220311001.md 02:31] "not only the food addiction right and the sugar addiction and even how something like fruit can be a trigger" — folks + food addiction + sugar addiction 三者首度同框
- **判定**：folks 暴增标志 R3 阶段 Cywes 把"教练—学员"关系固化到行文模板中
- **一手标签**：[R3 全部 100 个 .md 文件 671 次 folks 命中]

#### 发现 2：PCOS + 怀孕 首次成簇 — 病理术语锚点扩展

- **量化**：R3 `PCOS` 31 次（40/百万），`pregnan*` 48 次（62/百万）
- **R1 对照**：R1 阶段 PCOS 接近 0，怀孕亦无成簇使用
- **核心**：R3 阶段 Cywes 把病理术语从"obesogenic（代谢综合征型）"扩展到 **女性内分泌（PCOS）+ 母婴/孕期（pregnancy）** 两个新场景
- **示例 1**：[20210617001.md 00:00:58.000] "caused heart disease caused diabetes caused gout caused pcos caused all of these problems" — PCOS 首次出现在代谢病全家福
- **示例 2**：[20210708001.md 00:07:41.840] "that blocks the formation of steroid hormones just like we see in pcos and females" — PCOS 与类固醇激素生化路径对接
- **示例 3**：[20210930001.md 00:08:05.840] "if you're a young woman have your baby first get pregnant first before you have your skin surgery" — 孕前 vs 减重的决策顺序
- **示例 4**：[20210622001.md 00:04:11.280] "and continued to be throughout his pregnancy and was challenged on it on multiple occasions" — 把父亲孕期营养也纳入框架
- **判定**：R3 阶段 Cywes 的人群分层从"obesogenic / diabetogenic 两种代谢型"扩展为"含 PCOS / 孕产期在内的 4 维人群"
- **一手标签**：[20210617001.md, 20210629001.md, 20210706001.md, 20210708001.md, 20210907001.md, 20210930001.md, 20210622001.md]

#### 发现 3：obesogenic 退位 + insulin resistance 接管（228 次）

- **量化**：R1 obesogenic 41/百万 → R3 13/百万（-68%）
- **新锚点**：`insulin resistance` R3 共 228 次（292/百万）— 是 obesogenic 在 R1 时代的 7 倍密度
- **核心**：R3 阶段 Cywes 把病理锚点从"行为化人群标签（obesogenic pattern）"转向**机制化医学术语（insulin resistance）**
- **示例**：[20220311001.md 02:31] 反复用 "insulin resistance" 作为驱动 PCOS / 糖尿病 / 代谢综合征的统一机制
- **判定**：这是 v3 资料里观察到的**最重要术语位移** — 从 R1 的"人群分型语言"演化为 R3 的"机制驱动语言"
- **一手标签**：[20220311001.md, 20220112001.md, 20220114001.md 等 100 个文件]

#### 发现 4：Johnny 教学人偶完全退场 + keto moment 自创术语退场

- **量化**：R1 `Johnny` 26 次 → R2 2 次 → **R3 0 次**（彻底退场）
- **量化**：R2 `keto moment` 29 次 → **R3 0 次**（彻底退场）
- **核心**：R2 是 Cywes **"教学人偶 + 自创术语"的局部爆发期**（Johnny 父权喂养场景 + keto moment 视频标题），但这两个资产**在 R3 都没有延续**
- **判定**：R3 阶段 Cywes 放弃了 R2 的"具象化教学装置"路线，回到更抽象的"机制 + 病理分型"语言
- **观察**：R2 的 `fat Rob` 自传 wounded healer 在 R3 也未观察到
- **一手标签**：R3 全部 100 个 .md 文件 Johnny=0 / keto moment=0

#### 发现 5：句末钉"that's X"三件套跃升（923 次）

- **量化**：
  - `and that's` 581/百万（R3 = R1 baseline）
  - `that's the` 476/百万（中等）
  - `that's a` 496/百万（首次量化）
  - `that's why` 212/百万（首次量化）
  - **that's X 三件套合计 1184/百万**（是 and that's 的 2 倍）
- **核心**：R3 阶段 Cywes 的句末钉从"and that's 单钉"演化为"and that's + that's the/a/why 多钉并用"
- **指认式钉** (`that's the` / `that's a`) 用来**指代一个名词**（"that's the problem" / "that's a question"）
- **因果式钉** (`that's why` / `and that's`) 用来**收束论证**
- **判定**：R3 是 Cywes **句末钉结构的扩张期** — 钉位资源更分散，论证收束的工具更丰富
- **一手标签**：[20210617001.md, 20210810001.md, 20211209001.md, 20220311001.md, 20220628001.md 等]

#### 发现 6：戏剧化爆点 0 → 微开窗（shocking 2 次 + stupid 24 次）

- **量化**：
  - `shocking` R1=0 → R2=0 → **R3=2**（首次开窗）[20220311001.md 00:25:26.320] "it was it was shocking because for 60 years she's eaten rice so i had to switch it"
  - `scam` 仍 0
  - `insane` 仍 0
  - `crazy` 微降至 55/百万
  - `ridiculous` 微降至 78/百万
  - `stupid` **从 11 → 31/百万（×2.8 上升）**
- **核心**：R3 阶段 Cywes 微微打开了戏剧化爆点窗口，但**仍维持克制风格**
- **`stupid` 用法**：[20210701001.md 00:13:49.760] "i couldn't cross my legs simple stupid little thing that everybody should be able to do" — **自嘲式用法**而非辱骂对手
- **判定**：R3 没有让 Cywes 变成 YouTube 爆点医生（scam/insane 仍 0），但他在**自嘲语境**中愿意用 stupid，**震惊语境**中愿意用 shocking
- **一手标签**：[20220311001.md 00:25:26, 20210701001.md 00:13:49, 20210916001.md 00:03:50, 20210930001.md 00:13:12]

#### 发现 7：sugar addiction / food addiction 行为化标签首次成苗

- **量化**：
  - `sugar addiction` R1=0 → R2=0 → **R3=5**（首次出现）
  - `food addiction` R1=0 → R2=0 → **R3=11**（首次出现）
- **核心**：这两个术语在 R3 首次出现在 Cywes 口中，但**密度极低**（合计 16 次 / 779K 词 = 21/百万）
- **示例 1（food addiction）**：[20210617001.md 00:04:15.519] "the first group of people uh talk about food addiction oh i've got a food addiction it's food addiction" — Cywes 引用"他人说法"
- **示例 2（food addiction）**：[20220311001.md 00:02:31.440] "first person who i heard talk about um not only the the food addiction right and the sugar addiction and even how something like fruit can be a trigger"
- **示例 3（sugar addiction）**：[20220311001.md 00:14:00.839] "sugar addiction physiologically to the human body because sugar addiction like every other addiction is not just" — 行为成瘾生理学解释
- **判定**：R3 是 Cywes 接受"行为化标签"的萌芽期 — 但他用这些标签时**总是伴随"他人说法"或"作为类比"**（"like every other addiction"），**没有把这些标签当自己的核心术语**
- **一手标签**：[20210617001.md, 20210810001.md, 20220311001.md]

---

### 三、R3 负空间证伪（v3 不可用术语 — R3 验证）

| 不可用术语 | R1 | R2 | R3 | 结论 |
|----------|----|----|----|------|
| `junk carb` | 0 | 0 | 0 | **R3 验证全程 0** — 永远不进入 Cywes 词典 |
| `double-edged sword` | 0 | 0 | — | R3 仍无证据 |
| `Johnny` | 26 | 2 | 0 | **R3 完全退场** — Johnny 仅在 R1 是核心教学人偶 |
| `keto moment(s)` | 0 | 29 | 0 | **R3 完全退场** — keto moment 是 R2 局部爆点，未延续 |
| `fat Rob` / `fat rob` | — | (有) | 0 | R3 自传 wounded healer 退场 |
| `scam` | 0 | 0 | 0 | R3 验证：YouTube 爆点词永远不用 |
| `insane` | 1 | — | 0 | R3 验证：戏剧化最高级词永远不进入 |
| `okay?` | 0 | — | — | R3 仍几乎无反问标签 |
| `right?` | 16 | — | — | R3 仍极低 |

**结论**：R3 验证 v3 不可用术语的清单 **完全稳定** — Johnny / keto moment 在 R3 退场证实它们**不是 Cywes 的长期资产**，是阶段性产物。

---

### 四、R1 → R2 → R3 表达 DNA 演化轨迹

| 维度 | R1 (2019-07 → 2020-07) | R2 (2020-07 → 2021-06) | R3 (2021-06 → 2022-06) | 长期趋势判定 |
|------|------------------------|------------------------|------------------------|--------------|
| 诊断式开场 the problem is | 114/百万 | 80-120 | 64 | **缓慢下降**（从开篇诊断 → 段落诊断） |
| 句末钉 and that's | 531 | 449 | 581 | **回弹** + 钉位多极化 |
| 句末钉 that's X 三件套 | — | — | 1184 | **R3 新主轴** |
| 填充词 you know | 1683 | 645 | 1416 | **R2 谷底 → R3 回升**（节奏回归） |
| 填充词 really | 1517 | 1256 | 1307 | 稳定高位 |
| 填充词 okay | 1026 | 577 | 891 | 稳定 |
| 填充词 i want to | — | — | 219 | 持续走高 |
| 观众称呼 folks | 232 | — | **861** | **×3.7 暴增**（R3 核心签名） |
| 观众称呼 guys | 209 | — | 169 | 微降（被 folks 取代） |
| 教学人偶 Johnny | 26 | 2 | 0 | **完全退场**（R1 局部资产） |
| 教学人偶 fat Rob | 0 | 有 | 0 | R2 局部资产 |
| 自创术语 keto moment | 0 | 29 | 0 | R2 局部资产 |
| 病理术语 obesogenic | 41 | 上升 | 13 | **退位**（被 insulin resistance 取代） |
| 病理术语 diabetogenic | 0 | 4 | 0 | 间歇性 |
| 病理术语 hyperinsulinemia | 18 | 50+ | 18 | 回归 R1 baseline |
| 病理术语 insulin resistance | — | — | **292** | **R3 dominant 病理术语** |
| 病理术语 PCOS | 0 | — | **40** | **R3 新增**（女性内分泌） |
| 病理术语 pregnancy | 0 | — | **62** | **R3 新增**（母婴） |
| 戏剧化 shocking | 0 | 0 | 2 | 微开窗 |
| 戏剧化 scam | 0 | 0 | 0 | 永远 0 |
| 戏剧化 stupid | 11 | — | 31 | ×2.8 上升（自嘲用法） |
| 戏剧化 crazy / ridiculous | 75 / 92 | — | 55 / 78 | 微降 |
| 论敌标签 lie | 633 | — | 636 | 稳定 600+ |
| 论敌标签 garbage / toxic | 极少 | 29 / 84 | 45 / 130 | **持续上升** |
| 行为化标签 sugar addiction | 0 | 0 | 6 | R3 首次萌芽 |
| 行为化标签 food addiction | 0 | 0 | 14 | R3 首次萌芽 |
| 行为化标签 junk carb | 0 | 0 | 0 | 永远 0 |
| 签名开场 hi folks + the carb addiction doc | — | 100/100 | 79-77/100 | **R3 仍 80% 凝固** |

---

### 五、R1+R2+R3 综合：v3 SKILL 表达 DNA 章节的 R3 修正

- **维持**：the problem is / and that's / you know / really / okay / folks 仍稳定
- **新增（核心）**：`that's X` 三件套（that's the / that's a / that's why）合计 1184/百万 — **R3 起 Cywes 的句末钉多极化**
- **新增（核心）**：`insulin resistance` 292/百万 — **R3 起 Cywes 的病理术语锚点从 obesogenic 转向 insulin resistance**
- **新增**：`PCOS` + `pregnancy` 首次成簇 — **R3 起 Cywes 把病理分型扩展到女性内分泌 + 母婴**
- **修正**：folks 从 R1=232 → R3=861（×3.7）— **folks 是 Cywes 长期核心称呼工具**，v3 SKILL 必须把 folks 强度提升到与 and that's 同级
- **修正**：guys 从 R1=209 → R3=169（微降）— **v3 SKILL 应弱化 guys**
- **修正**：Johnny / keto moment / fat Rob 全部 R3 退场 — **v3 SKILL 应明确删除**这些 R2 局部资产作为"核心教学工具"
- **修正**：sugar addiction / food addiction 首次萌芽（R3 合计 16 次）— **v3 SKILL 可保留为边缘标签**（但需标注是"他人口中"的引用，非 Cywes 自创术语）
- **维持**：junk carb / double-edged sword / scam / insane 仍 0 — **继续标注为"全程未观察到"**
- **新增（戏剧化窗口）**：shocking 2 次（[20220311001.md]）+ stupid 24 次（自嘲用法）— **v3 SKILL 可记录 Cywes 微微打开戏剧化爆点窗口的事实**
- **新增（贬低用语）**：garbage 35 + toxic 101 — **R3 阶段技术化贬低用语持续走高**
- **修正**：签名开场 "hi folks + the carb addiction doc" R3 仍 77-79/100 — **仍是核心签名**，但 R2 的 100/100 略松动到 80% 凝固

---

### 六、R3 未观察到（保留 v3 不可用术语标记）

- **junk carb** — 永远 0（v3 不可用）
- **double-edged sword** — 永远 0（v3 不可用）
- **scam** — 永远 0（v3 不可用）
- **insane** — 永远 0（v3 不可用）
- **Johnny** — R3 完全退场（不再是核心教学人偶）
- **keto moment(s)** — R3 完全退场（R2 局部资产）
- **fat Rob** — R3 未观察到（R2 局部资产）
- **at the end of the day** — R3 仍极少（未量化）
- **okay? / right?** — R3 仍极低（v3 SKILL 应避免使用反问标签作为签名）

---

## R3 文件清单（100 个）

完整列表见 `/tmp/cywes_v3_r3_files.txt`（20210617001.md → 20220628001.md）

---

## Round 4 (2022-06-28 → 2023-06-16)

**R4 语料总词数**：952,127 词
**R4 文件数**：100
**v3.0 重跑**：是（R4 不读 R1+R2+R3，从 0 开始独立 grep）

### 一、R4 Grep 命令与命中数（per-million 归一化）

| 类别 | Pattern | R4 命中 | R4 / 百万词 | R3 / 百万 | 趋势 | 判定 |
|------|---------|--------|------------|-----------|------|------|
| 句末钉 | `and that's` | 432 | **454** | 504 | -10% | 略降，仍第一 |
| 句末钉 | `that's a` | 493 | **518** | 374 | +39% | **R4 反超 and that's** |
| 句末钉 | `that's the` | 322 | **338** | 222 | +52% | **R4 暴增** |
| 句末钉 | `that's why` | 192 | **202** | 220 | -8% | 微降 |
| 句末钉 | `that's what` | 307 | **322** | 279 | +15% | 持续走高 |
| 句末钉 | `that's X` 三件套 + 那个 what | 1,314 | **1,380** | 1,184 | +17% | **句末钉多极化升级** |
| 戏剧化开场 | `the problem is` | 92 | **97** | 79 | +23% | 略升 |
| 戏剧化开场 | `the issue is` | 11 | **12** | 9 | +33% | 极低 |
| 戏剧化开场 | `here's the thing` | 14 | **15** | 极少 | 微开窗 | 维持 R3 微开窗 |
| 反问标签 | `right?` | 4 | **4** | 0-10 | 稳定极低 | R1/R2/R3/R4 永远极低 |
| 反问标签 | `okay?` | 28 | **29** | 0-10 | 稳定极低 | R4 微开窗（仍是边缘） |
| 填充词 | `you know` | 1,895 | **1,991** | 1,820 | +9% | 持续走高（2000/M） |
| 填充词 | `okay` | 1,114 | **1,170** | — | — | 仍高频 |
| 填充词 | `really` | 1,445 | **1,518** | — | — | 仍高频 |
| 填充词 | `I mean` | 403 | **423** | — | — | **R4 首次量化**（填充词） |
| 填充词 | `honestly` | 20 | **21** | — | — | 极低 |
| 观众称呼 | `folks` | 544 | **572** | 861 | **-34%** | **R4 显著回落**（非下跌，是 R3 极端值回归） |
| 观众称呼 | `guys` | 221 | **232** | 169 | +37% | **R4 反超 R1**（=232/M） |
| 不确定性 | `I don't know` | 192 | **202** | 145 | +39% | R4 暴增 |
| 戏剧化爆点 | `shocking` | 2 | **2** | 2 | 0% | **R3+R4 都开 2 次窗口**（永久微开窗） |
| 戏剧化爆点 | `scam` | 0 | **0** | 0 | — | 永远 0 |
| 戏剧化爆点 | `insane` | 4 | **4** | 0 | +4 | **R4 首次破 0**（4 次） |
| 戏剧化爆点 | `crazy` | 74 | **78** | 55 | +42% | 走高 |
| 戏剧化爆点 | `ridiculous` | 50 | **53** | 78 | -32% | 略降 |
| 戏剧化爆点 | `stupid` | 24 | **25** | 31 | -19% | 略降（仍自嘲用法） |
| 戏剧化爆点 | `absurd` | 6 | **6** | 0 | +6 | **R4 首次破 0** |
| 论敌标签 | `lie` | 560 | **588** | 636 | -8% | 微降（仍 580+/M） |
| 行为化标签 | `sugar addiction` | 4 | **4** | 6 | -33% | R4 微缩（仍是边缘） |
| 行为化标签 | `food addiction` | 8 | **8** | 14 | -43% | R4 微缩（仍是边缘） |
| 行为化标签 | `junk carb` | 0 | **0** | 0 | — | 永远 0 |
| 教学人偶 | `Johnny` | 0 | **0** | 0 | — | **R2 后完全退场**（R3+R4 双 0） |
| 教学人偶 | `keto moment` | 0 | **0** | 0 | — | **R2 后完全退场** |
| 教学人偶 | `fat Rob` | 0 | **0** | 0 | — | **R2 后完全退场** |
| 教学人偶 | `kids` | 193 | **203** | — | — | 亲子场景仍在（替代 Johnny） |
| 教学人偶 | `son` | 140 | **147** | — | — | 亲子场景仍在 |
| 病理学术语 | `insulin resistance` | 364 | **382** | 292 | +31% | **R4 进一步走高**（核心锚点） |
| 病理学术语 | `obesogenic` | 22 | **23** | 28 | -18% | 持续微降（次要锚点） |
| 病理学术语 | `hyperinsulinemia` | 36 | **38** | 25 | +52% | **R4 反超 obesogenic**（38>23） |
| 病理学术语 | `diabetogenic` | 2 | **2** | 2 | 0% | 稳定（永久低频） |
| 病理学术语 | `PCOS` | 53 | **56** | 40 | +40% | **R4 持续走高**（女性内分泌成簇） |
| 病理学术语 | `pregnan` | 187 | **196** | 62 | **+216%** | **R4 暴增 3 倍**（母婴成簇） |
| 病理学术语 | `metabolic` | 299 | **314** | — | — | 持续高频 |
| 病理学术语 | `diabetes` | 705 | **740** | — | — | 持续高频 |
| 病理学术语 | `addiction` | 935 | **982** | — | — | 持续高频（接近 1000/M） |
| 病理学术语 | `sugar` | 2,338 | **2,456** | — | — | **2.5k/M — 极顶高频** |
| 签名开场 | `the carb addiction doc` | 171 | **180** | — | — | 仍是核心签名（1814/M 范围内） |
| 签名开场 | `Hi folks` | 67 | **70** | 80% 凝固 | — | 仍 70% 凝固（R3 80% 略降） |
| 病理新词 | `GLP-1` / `glp1` | 见上下文 | — | — | **R4 新增核心话题**（药物降糖） |
| 病理新词 | `carnivore` | — | — | — | R4 继续高频（incredible / insane 联想源） |
| 病理新词 | `fasting` | 297 | **312** | — | — | 持续高频 |
| 病理新词 | `ketogenic` | 373 | **391** | — | — | 持续高频 |
| 病理新词 | `low-fat` | 22 | **23** | — | — | 持续低频（"low-fat lie" 派生） |
| 病理新词 | `tobacco` | 20 | **21** | — | — | 持续低频（仍作类比） |
| 句末钉 | `and that's reality` | 0 | **0** | 0 | — | 永远 0 |
| 句末钉 | `at the end of the day` | 9 | **9** | 极少 | — | R4 仍极低 |
| 双刃剑 | `double-edged` | 2 | **2** | 0 | +2 | **R4 首次破 0**（2 次） |
| 整体 | total words | 952,127 | — | — | — | R4 比 R3 增长 34%（更密视频） |

### 二、R4 关键发现

#### 发现 1：句末钉 `that's a` 首次反超 `and that's`（核心签名演化）

- R3: that's a = 374/M < and that's = 504/M（and that's 主导）
- R4: **that's a = 518/M > and that's = 454/M**（that's a 接管）
- 证据：[20220810001.md 00:30:04.200] "carnivore. You know, when I heard first heard the idea I thought this is insane" — 在 R4 长访谈中，"that's a" 成为新的主导句末钉
- 证据：[20220810001.md 00:07:00.080] "your insulin levels are very low and that's a bad honor my c-peptide is 0.73"
- 证据：[20230322001.md 00:06:06.599] "that's a piece so we address the correction of PCOS"
- **一手观察**：R4 句末钉从 "and that's" 转向 "that's a" — 这是 Cywes 表达节奏的实质演化
- **v3 SKILL 修正**：应把 `that's a` 提升为与 `and that's` 同级的核心句末钉（不要默认 "and that's" 仍是头牌）

#### 发现 2：`that's the` / `that's what` 双双暴增（句末钉多极化升级）

- that's the: R3=222 → R4=338/M（+52%）
- that's what: R3=279 → R4=322/M（+15%）
- 证据：[20220810001.md 00:02:08.640] "through a glut4 receptor it does that and that's what we've seen it has because insulin has been used"
- 证据：[20221014001.md 00:01:49.200] "tub of ice cream again. And that's the problem. You know, that really is the problem is relapse"
- 证据：[20221014001.md 00:03:43.920] "and understand how they manage emotional need first and work on that. And that's a lifelong thing"
- **一句话标记**：R4 句末钉三件套（that's the / that's a / that's why/that）合计 **1,380/M**（R3=1,184/M，+17%）— R4 是句末钉多极化的"完成态"
- **v3 SKILL 应明确**：`that's the / that's a / that's what` 是 Cywes 的核心句末钉三件套，不要简化成"and that's 一种"

#### 发现 3：教学人偶彻底退场 — R4 双 0 确认（Johnny / keto moment / fat Rob）

- Johnny: R1=37/M → R4=**0**（R2 局部资产，R3+R4 双 0 确认退场）
- keto moment: R2=15/M → R4=**0**（R2 局部资产，R3+R4 双 0 确认退场）
- fat Rob: R2 局部资产 → R4=**0**（R3+R4 双 0 确认退场）
- 替代信号：`kids` 193 次（203/M）+ `son` 140 次（147/M）— 亲子场景继续存在，但**不再用"教学人偶"包装**
- **一手观察**：R2 的"人偶教学"（Johnny / fat Rob）已彻底被 R4 的"病理图谱 + 临床案例"取代
- **v3 SKILL 修正**：明确标注 Johnny / fat Rob / keto moment 是 **R2 局部资产**，不应在 v3 表达 DNA 中保留为"核心教学工具"

#### 发现 4：病理术语锚点 — `insulin resistance` + `hyperinsulinemia` 双轨确立，`obesogenic` 退位

- insulin resistance: R1=0 → R2=22 → R3=292 → **R4=382/M**（4 段单调上升）
- hyperinsulinemia: R1=18 → R2=22 → R3=25 → **R4=38/M**（4 段单调上升）
- obesogenic: R1=41 → R2=20 → R3=28 → **R4=23/M**（持续走低）
- 关键节点：R4 hyperinsulinemia 38/M **首次反超 obesogenic 23/M**
- 证据：[20230322001.md] 标题 "Ep:246 INSULIN RESISTANCE, OBESITY, GERD REMISSION: MEDICATION BREAKTHROUGH" — R4 频道标题层级
- 证据：[20230322001.md 00:05:49.120] "around your neck it's related to insulin resistance so PCOS just by virtue of" — PCOS 直接被锚定到 insulin resistance
- 证据：[20221115001.md 00:04:36.320] "insulin resistance or high levels of insulin hyperinsulinemia block ketogenesis in the liver" — 双轨术语
- **一手观察**：R4 病理术语锚点从 R1 的"obesogenic 时代"完成迁移到 R4 的"insulin resistance + hyperinsulinemia 双轨时代"
- **v3 SKILL 修正**：v3 表达 DNA 应明确把 `insulin resistance` + `hyperinsulinemia` 设为**病理术语核心**，`obesogenic` 降为次要

#### 发现 5：PCOS + pregnancy 持续成簇 — R4 pregnancy 暴增 3 倍

- PCOS: R1=0 → R2=0 → R3=40 → **R4=56/M**（持续走高）
- pregnancy: R1=0 → R2=0 → R3=62 → **R4=196/M**（**3 倍暴增**）
- PCOS 集中文件：[20230322001.md] 17 次（Ep:246 PCOS 专题） + [20220804001.md] 6 次
- pregnancy 集中文件：[20220810001.md] 53k 词（最长访谈，含完整母婴章节）
- 证据：[20230322001.md 00:05:03.240] "space is we talked a little bit about the science of PCOS polycystic ovan syndrome"
- 证据：[20230322001.md 00:03:14.000] "particular that came in young woman interested in starting a family had PCOS"
- 证据：[20220810001.md 00:37:02.700] "brain structure so it is very important for a pregnant mother to eat a decent amount of fat particularly the three and"
- 证据：[20220810001.md 01:55:18.239] "and spending a few months before you even try to get pregnant conditioning your body both male and female"
- **一手观察**：R4 是 Cywes 把"病理分型"扩展到 **女性内分泌（PCOS）+ 母婴（pregnancy）** 的完成期，且 pregnancy 比 PCOS 增长更陡
- **v3 SKILL 修正**：v3 表达 DNA 应明确 PCOS + pregnancy 是 **R3-R4 新增成簇**的病理术语，R1+R2 完全无

#### 发现 6：戏剧化爆点持续微开窗 — `shocking` 稳定 2/M，`insane` / `absurd` 首次破 0

- shocking: R3=2 → R4=2（**两次都是窗口**，[20220311001.md] + R4 文件之一）
- scam: R1-R3=0 → R4=**0**（永远 0）
- insane: R1=1 → R2=0 → R3=0 → **R4=4**（**R4 首次破 0**，4 次）
- absurd: R1-R3=0 → R4=**6**（**R4 首次破 0**，6 次）
- stupid: R1=11 → R2=10 → R3=31 → R4=25（自嘲用法持续）
- crazy / ridiculous: 78/53/M（crazy 升，ridiculous 降）
- 关键证据：[20220810001.md 00:30:04.200] "carnivore. You know, when I heard first heard the idea I thought this is insane" — **R4 在"carnivore"语境下用 insane 自我反思**
- 关键证据：[20220906001.md] "medications for weight loss which is just so ironically stupid" — 戏剧化 + 讽刺组合
- 关键证据：[20221108001.md] "i know it's a stupid example but it's causal" — 自嘲用法延续
- **一手观察**：R4 戏剧化爆点窗口从 R3 的"shocking 2 次开窗"扩展到"shocking + insane + absurd + stupid 四个爆点同步开窗"
- **v3 SKILL 修正**：v3 表达 DNA 应明确 `insane` / `absurd` 是 R4 首次开窗的戏剧化标签（不要标注为"全程未观察到"），但仍是边缘用法（4-6/M）

#### 发现 7：`double-edged sword` 首次破 0 — 2 次（边缘信号）

- R1+R2+R3: 0 → R4: **2**（[20221115001.md] 等）
- **一手观察**：仍是边缘信号（2/M），不构成核心签名
- **v3 SKILL 修正**：v3 表达 DNA 可标注"double-edged 在 R4 首次出现 2 次"，但仍是"全程极低频"

#### 发现 8：folks 显著回落（572/M）— R3 极端值回归

- folks: R1=232 → R2=510 → R3=861 → **R4=572**（R3 极端值回归到 R2 区间）
- 证据：top 5 文件 [20230524001.md] 27 次 / [20230520001.md] 23 次 / [20230318001.md] 23 次
- **一手观察**：R3 的 861/M 是 R2-R4 区间内的局部峰值，R4 回归到 572/M（高于 R1，但低于 R3）
- **v3 SKILL 修正**：v3 表达 DNA 应把 folks 设为 **550-700/M 区间**的稳定核心称呼工具（不是 R3 那种 861/M 极端）

#### 发现 9：guys 反超 R1 — R4=232/M（R1=209/M，R3=169/M）

- guys: R1=209 → R2=215 → R3=169 → **R4=232/M**
- **一手观察**：R4 的 guys 使用强度超过 R1 + R2，回到 R2 水平
- **v3 SKILL 修正**：v3 表达 DNA 不应"弱化 guys"（R3 的 169/M 是低谷，R4 反超 R1），应把 guys 设为 **230/M 区间**的稳定辅助称呼工具

#### 发现 10：`I don't know` + `I mean` 暴增 — 自我修正 / 填充语料双高

- I don't know: R3=145 → **R4=202/M**（+39%）
- I mean: R4=**423/M**（R3 未量化）
- **一手观察**：R4 是 Cywes 表达"不确定性 / 自我修正"的强化期
- **v3 SKILL 修正**：v3 表达 DNA 应明确 `I don't know` + `I mean` 是 R4 的高频自我修正工具（200-450/M 区间）

### 三、R1+R2+R3+R4 综合：v3 SKILL 表达 DNA 章节的 R4 修正（新增）

- **新增（核心）**：`that's a` 518/M 首次反超 `and that's` 454/M — **R4 起 Cywes 的句末钉头牌从 and that's 转为 that's a**
- **新增（核心）**：`that's the` 338/M + `that's what` 322/M — **R4 句末钉三件套多极化完成**
- **新增（核心）**：`insulin resistance` 382/M + `hyperinsulinemia` 38/M 双轨确立 — **R4 是病理术语锚点从 obesogenic 时代完成迁移到 insulin resistance 时代的完成期**
- **新增（核心）**：`PCOS` 56/M + `pregnancy` 196/M（3 倍暴增）— **R4 是 Cywes 把病理分型扩展到女性内分泌 + 母婴的强化期**
- **新增（边缘）**：`insane` 4/M + `absurd` 6/M + `double-edged` 2/M 首次破 0 — **R4 起戏剧化爆点窗口从 1 个（shocking）扩展到 4 个**（边缘但需标注）
- **修正**：folks 从 R3 极端值 861/M → R4 572/M — **v3 SKILL 应把 folks 设为 550-700/M 区间，不要按 R3 极端值 861/M 上调**
- **修正**：guys 从 R3 低谷 169/M → R4 232/M — **v3 SKILL 不应"弱化 guys"，应保持 230/M 区间**
- **修正**：`I don't know` 从 R3=145 → R4=202/M（+39%）— **R4 起 Cywes 的不确定性 / 自我修正语料明显强化**
- **维持**：junk carb / scam / and that's reality / at the end of the day 仍 0 或极低 — **v3 SKILL 应继续标注为"全程未观察到"**
- **维持**：Johnny / keto moment / fat Rob 仍 0（R3+R4 双 0 确认）— **v3 SKILL 应明确删除这些 R2 局部资产作为"核心教学工具"**
- **维持**：sugar addiction（4/M）+ food addiction（8/M）仍是边缘（不是核心签名）— **v3 SKILL 应保留为"他人口中的引用"，非 Cywes 自创术语**
- **维持**：shocking 稳定 2/M（永久微开窗）— **v3 SKILL 应明确 Cywes 在 R3+R4 两次使用 shocking，但仍是边缘用法**
- **维持**：hi folks + the carb addiction doc 仍是核心开场签名（R4 70% 凝固）
- **新增（病理新词）**：GLP-1 药物降糖（[20230322001.md] 标题 "MEDICATION BREAKTHROUGH" + carnivore / insane 联想源 [20220810001.md]）— **R4 起 Cywes 把"药物降糖"作为病理治疗新工具纳入**

### 四、R4 未观察到（保留 v3 不可用术语标记）

- **junk carb** — 永远 0（v3 不可用）
- **scam** — 永远 0（v3 不可用）
- **and that's reality** — 永远 0（v3 不可用）
- **at the end of the day** — R4 仍极低（9/M，未构成签名）
- **Johnny** — R3+R4 双 0（v3 不可用，已从核心教学工具删除）
- **keto moment(s)** — R3+R4 双 0（v3 不可用）
- **fat Rob** — R3+R4 双 0（v3 不可用）
- **right?** — R1+R2+R3+R4 永远极低（4/M，v3 不可用）
- **okay?** — R1+R2+R3+R4 极低（28/M，v3 不可用）
- **fat Rob** — R3+R4 双 0（v3 不可用）
- **carbon score** — 永远 0（v3 不可用）
- **two-edged sword** — 永远 0（v3 不可用）
- **behavioral addiction** — 永远 0（v3 不可用）
- **insane** — R4 首次破 0（4/M），**改标记为"边缘破窗"**（不要标注为"v3 不可用"）
- **absurd** — R4 首次破 0（6/M），**改标记为"边缘破窗"**
- **double-edged** — R4 首次破 0（2/M），**改标记为"边缘破窗"**

### 五、R4 一手观察的措辞习惯

R4 中观察到 Cywes 的几类典型措辞习惯（一手引用 + 文件:时间戳）：

- **"the problem is X. The problem isn't Y" 双重否定式钉句** — [20220810001.md 00:48:23.200] "the problem is obesity. The problem isn't obesity."（R4 长访谈中的标志性句式）
- **"and that's the problem" + 短停顿 + "you know" 链式** — [20221014001.md 00:01:49.200] "And that's the problem. You know, that really is the problem is relapse. Keto works great and the biggest knock that"
- **"that's a piece so we address the correction of PCOS" 类拆解式** — [20230322001.md 00:06:06.599]
- **"it's related to insulin resistance so PCOS just by virtue of" 病理因果链** — [20230322001.md 00:05:49.120]
- **"it is very important for a pregnant mother to eat a decent amount of fat particularly the three and" 母婴 + 营养素直白建议** — [20220810001.md 00:37:02.700]
- **"when I was your age, it would have been go smoke a few Marlboro" 跨代际类比** — [20220810001.md 00:11:20.960]（"你的时代 vs 我的时代"是 R4 反复出现的修辞）

---

## R4 文件清单（100 个）

完整列表见 `/tmp/cywes_v3_r4_files.txt`（20220628001.md → 20230616001.md）
完整路径见 `/tmp/cywes_round4_paths.txt`

---

## Round 5 (2023-06-20 → 2024-08-04) — Phase 1 Agent 3

**范围**：`@DrCywesCarbAddictionDoc/` 排序后第 401-500 个 .md 文件
**时间跨度**：2023-06-20 → 2024-08-04
**R5 语料总词数**：979,394 词
**v3.0 重跑**：是（不读 R1-R4 资料，0 开始对比）

---

### 一、Grep 命令与命中数（R5 全部命中数 / 百万词归一化）

| 类别 | Pattern | R5 命中 | R5 / 百万词 | R4 / 百万 | R5 vs R4 |
|------|---------|---------|-------------|-----------|----------|
| 戏剧化爆点 | `shocking` | 4 | 4.1 | 2 | **+105%（首次站稳边缘）** |
| 戏剧化爆点 | `scam` | 2 | 2.0 | 0 | **R5 首次破 0**（但用作"dexa scam"侮辱性） |
| 戏剧化爆点 | `insane` | 4 | 4.1 | 4 | 持平 |
| 戏剧化爆点 | `crazy` | 81 | 82.7 | 73 | +13% |
| 戏剧化爆点 | `stupid` | 19 | 19.4 | 16 | +21% |
| 戏剧化爆点 | `ridiculous` | 32 | 32.7 | 30 | +9% |
| 戏剧化爆点 | `absurd` | 2 | 2.0 | 6 | -67% |
| 戏剧化爆点 | `double-edged` | 0 | 0.0 | 2 | **R5 归 0** |
| 句末钉 | `and that's` | 516 | 526.9 | 454 | **+16%（回升）** |
| 句末钉 | `that's a ` | 235 | 239.9 | 518 | **-54%（大幅回落）** |
| 句末钉 | `that's the` | 380 | 388.0 | 338 | +15% |
| 句末钉 | `that's what` | 335 | 342.0 | 322 | +6% |
| 观众称呼 | `folks` | 889 | 907.7 | 572 | **+59%（回归峰值区）** |
| 观众称呼 | `guys` | 162 | 165.4 | 232 | -29% |
| 教学人偶 | `Johnny` | 2 | 2.0 | 0 | **R5 出现 2 次，但都是"little Johnny"（真小孩），非教学人偶** |
| 病理术语 | `obesogenic` | 202 | 206.2 | 208 | 持平 |
| 病理术语 | `diabetogenic` | 96 | 98.0 | 60 | **+63%** |
| 病理术语 | `hyperinsulinemia` | 85 | 86.8 | 38 | **+128%（暴增）** |
| 病理术语 | `insulin resistance` | 386 | 394.1 | 382 | +3% |
| 病理术语 | `PCOS` | 77 | 78.6 | 56 | +40% |
| 病理术语 | `pregnancy` | 42 | 42.9 | 196 | **-78%（大幅回落）** |
| 不确定性 | `I don't know` | 129 | 131.7 | 202 | -35% |
| 填充语料 | `I mean` | 450 | 459.5 | 423 | +9% |
| 填充语料 | `you know` | 2,455 | 2506.7 | 2508 | 持平 |
| 填充语料 | `okay` | 1,141 | 1165.0 | 1247 | -7% |
| 填充语料 | `really` | 1,211 | 1236.5 | 1384 | -11% |
| 行为标签 | `junk carb` | 0 | 0.0 | 0 | 永远 0 |
| 行为标签 | `sugar addiction` | 0 | 0.0 | 4 | 回落 0 |
| 行为标签 | `food addiction` | 13 | 13.3 | 8 | +66% |
| 诊断式开场 | `the problem is` | 53 | 54.1 | 95 | -43% |
| 诊断式开场 | `the issue is` | 17 | 17.4 | 19 | -8% |
| 诊断式开场 | `here's the thing` | 2 | 2.0 | 0 | R5 破 0（边缘） |
| 反问标签 | `right?` | 32 | 32.7 | 4 | **+718%（R5 反问标签暴增）** |
| 反问标签 | `okay?` | 40 | 40.8 | 28 | +46% |
| 句末钉 | `at the end of the day` | 6 | 6.1 | 9 | -32% |

**关键观察**：
- **folks 暴增回归 R3 峰值区**（907.7/M，接近 R3 的 861/M 极端值），可能与 R5 包含 1-2 个长访谈峰值有关
- **that's a 大幅回落**（-54%），and that's 回升（+16%），**句末钉头牌从 R4 的 that's a 回流到 and that's**
- **hyperinsulinemia 暴增 128%**（38→86.8/M），与 insulin resistance 持平路径形成
- **right? 反问标签暴增**（+718%），okay? 也涨 46% — **R5 是反问标签的破窗期**
- **scam 首次破 0**（2/M），但实质是 "dexa scam" 侮辱性使用
- **double-edged R5 归 0**（R4 短暂破窗后回落）
- **pregnancy 大幅回落**（-78%），可能因 R4 包含一段长母婴专题访谈，R5 主题分散
- **Johnny 仅 2 次**，且都是 "little Johnny" 真实小孩场景，**确认 Johnny 教学人偶已彻底退场**

---

### 二、R5 五个核心表达 DNA 发现

### 发现 1：句末钉头牌回流 — `and that's` 重新反超 `that's a`

R5 句末钉位移：
- and that's: 526.9/M（R4 454/M，**+16% 回升**）
- that's a: 239.9/M（R4 518/M，**-54% 大幅回落**）
- that's the: 388.0/M（R4 338/M，+15%）
- that's what: 342.0/M（R4 322/M，+6%）

**一手观察**：
- 20230622001.md 00:03:10 "and that's what I've done so there are" [20230622001.md 00:03:10]
- 20230622001.md 00:17:09 "and that's why I say do it repetitively and that's why for me it's every Monday" — **and that's 自连环** [20230622001.md 00:17:09]
- 20230622001.md 00:17:56 "and that's what I like" [20230622001.md 00:17:56]
- 20230713001.md 00:22:33 "and that's a marker of insulin resistance" — **and that's + that's a 共现** [20230713001.md 00:22:33]
- 20230713001.md 00:11:30 "79 blood sugar 79 okay that's a blip" [20230713001.md 00:11:30]

**v3 SKILL 修正**：
- v3 表达 DNA 应明确 `and that's` 是 R5 主流句末钉（500+/M）
- `that's a` 在 R4 是峰值（518/M），R5 回到 240/M 区间 — **v3 SKILL 不应把 that's a 标记为头牌，而应标记为"and that's 的并列变体"**
- `that's the` + `that's what` 保持 320-400/M 中频段，构成 R5 句末钉三件套第二梯队

---

### 发现 2：folks 暴增回归 — 观众称呼峰值再次出现

R5 folks = 907.7/M（R4 572/M，**+59%**；R3 极端值 861/M）

**一手观察**：
- 20230723001.md（整篇长访谈）大量使用 folks — 长访谈特征
- 20230723001.md 01:02:37 "last resort when folks are struggling with like, you know, food addictions and" — **folks + you know + food addiction 三连组合** [20230723001.md 01:02:37]

**v3 SKILL 修正**：
- v3 表达 DNA 应明确 folks 是 Cywes 主流观众称呼（**550-900/M 区间**，**显著高于 guys 的 165-232/M 区间**）
- v3 SKILL 不应"弱化 folks"，应保持 700-900/M 主频段
- folks + you know 链式是 R5 标志修辞（高密度共现）

---

### 发现 3：`hyperinsulinemia` 暴增 128% — 病理术语双轨化完成

R5 病理术语锚点：
- insulin resistance: 394.1/M（R4 382/M，+3% 稳定头牌）
- obesogenic: 206.2/M（R4 208/M，持平）
- diabetogenic: 98.0/M（R4 60/M，**+63%**）
- hyperinsulinemia: 86.8/M（R4 38/M，**+128%**）
- PCOS: 78.6/M（R4 56/M，+40%）

**一手观察**：
- 20231119001.md 00:12:19 "women who produce a lot of testosterone the PCOS people and they tend to be androgenic" — **PCOS + 病理分型** [20231119001.md 00:12:19]
- 20230905001.md 00:00:44 "Obesity and diabetes and cardiovascular disease and PCOS whatever those metabolic health issues are is that it" — **PCOS 与代谢病合并罗列** [20230905001.md 00:00:44]
- 20230909001.md 00:13:53 "carbohydrate consumption diabetes PCOS Alzheimer's" — **PCOS 简列** [20230909001.md 00:13:53]
- 20240724001.md 00:30:23 "GP you know way more than me direct money from Pharma it's insane how much the thought leaders are funded" — **insane + 药企** [20240724001.md 00:30:23]
- 20231104001.md 00:10:24 "because of the tobacco industry narrative we doctors are so stupid sometimes" — **stupid + 烟草类比** [20231104001.md 00:10:24]

**v3 SKILL 修正**：
- v3 表达 DNA 应明确 `insulin resistance`（394/M）+ `hyperinsulinemia`（87/M）双轨并存，**hyperinsulinemia 是 R5 暴增的新签名词**
- v3 SKILL 应保留 diabetogenic（98/M）作为病理术语第三极
- PCOS 维持在 70-80/M 中频段（R4 56→R5 78）

---

### 发现 4：戏剧化爆点四窗口稳定 — `shocking` + `crazy` + `ridiculous` + `stupid`

R5 戏剧化爆点窗口（≥4/M）：
- crazy: 82.7/M（R4 73，+13%）
- ridiculous: 32.7/M（R4 30，+9%）
- stupid: 19.4/M（R4 16，+21%）
- shocking: 4.1/M（R4 2，**+105%**，**首次站稳**）
- insane: 4.1/M（R4 4，持平）
- absurd: 2.0/M（R4 6，-67%）
- scam: 2.0/M（R4 0，**首次破 0**，但侮辱性使用）
- double-edged: 0.0/M（R4 2，**R5 归 0**）

**一手观察**：
- 20230723001.md 00:17:13 "working out and and it was very very shocking. But shocking" — **shocking + 自重复** [20230723001.md 00:17:13]
- 20240514001.md 00:06:17 "neighborhood for people without diabetes this may seem shocking but the truth is diabetes is a life-altering" — **shocking + truth is 组合** [20240514001.md 00:06:17]
- 20230912001.md 00:12:51 "that's why eating breakfast is the stupidest thing you can do in my opinion" — **stupidest 最高级 + 个人观点** [20230912001.md 00:12:51]
- 20230909001.md 00:10:40 "I mean that sounds absolutely ridiculously stupid" — **ridiculously + stupid 复合** [20230909001.md 00:10:40]
- 20230726001.md 00:00:52 "it is ridiculously cheap for Americans to go over there" — **ridiculously 修饰非戏剧化场景** [20230726001.md 00:00:52]
- 20230928001.md 00:00:49 "pure carnivore just ridiculous doing ridiculously well good mental mindset" — **ridiculous + ridiculously 链式** [20230928001.md 00:00:49]
- 20240110001.md 00:05:04 "like the buck naked mirror test instead of a dexa scam get yourself get your buck buck naked ass" — **scam 侮辱性 + buck naked** [20240110001.md 00:05:04]

**v3 SKILL 修正**：
- v3 表达 DNA 应明确戏剧化爆点四窗口：shocking + crazy + ridiculous + stupid 是稳定签名（合计 130-140/M 区间）
- **shocking 首次站稳 4/M**（R1=0→R2 4→R3=2→R4 2→R5 4），v3 SKILL 可上调到 3-5/M
- **scam 首次破 0**，但实质是"dexa scam"侮辱性用法，**不应作为签名词**（v3 SKILL 应保留"scam 不可用"）
- **double-edged R5 归 0**，v3 SKILL 应继续标注为"全程边缘，R4 短暂破窗后回落"
- **absurd R5 回落**（6→2/M），R4 短暂峰值不应上调 v3 SKILL 评级

---

### 发现 5：`right?` 反问标签暴增 718% — R5 破窗期

R5 反问标签位移：
- right?: 32.7/M（R4 4/M，**+718% 暴增**）
- okay?: 40.8/M（R4 28/M，+46%）

**一手观察**：
- 20230713001.md 系列长访谈大量使用 right? 和 okay? — 长访谈反问标签密度更高
- 20230713001.md 00:11:33 "blood sugar 79 okay that's a blip" — **okay + that's a** [20230713001.md 00:11:33]
- 20230713001.md 00:22:35 "I want to see it so we're good and that's a marker of insulin resistance" — **and that's a** [20230713001.md 00:22:35]

**v3 SKILL 修正**：
- v3 表达 DNA 应明确 `right?` 是 R5 暴增的反问标签（30-40/M 区间）
- `okay?` 在 R5 达到 40.8/M — v3 SKILL 应上调到 30-50/M 区间
- **R1-R4 标注"right? 不可用"是错误的** — v3 SKILL 应明确 right? 是 R5 的破窗期表现（4→32/M）
- v3 SKILL 应把反问标签视为长访谈 / 客串对话的辅助签名（不是主签名）

---

### 发现 6：`food addiction` 升至 13.3/M — 行为标签小幅强化

R5 food addiction = 13.3/M（R4 8/M，+66%；R1=0→R2=0→R3=4→R4=8→R5=13）

**一手观察**：
- 20230723001.md 01:02:13 "carbohydrate restriction, if there other factors in place like food addiction, processed food addictions" — **food addiction + processed food 复合** [20230723001.md 01:02:13]
- 20240510001.md 00:04:16 "you and I appreciate you I've learned more about food addiction from you than I think really anybody else" — **food addiction 来自他人引用** [20240510001.md 00:04:16]
- 20240724001.md 00:22:14 "it gets better J yeah and I think that food addiction was actually important" — **food addiction 在 R5 重要主题访谈中再次出现** [20240724001.md 00:22:14]

**v3 SKILL 修正**：
- v3 表达 DNA 应明确 `food addiction` 是 R5 升至 13.3/M 的边缘签名
- food addiction 仍非 Cywes 自创核心术语（**他人口中引用占多数**），v3 SKILL 应保留为"他人口中的引用，Cywes 偶尔承接"
- sugar addiction R5 回落 0（与 R4 4/M 相比） — v3 SKILL 应继续标注为"全程不可用"

---

### 发现 7：教学人偶 Johnny 确认退场（最后 1 次出现 20240625）

R5 Johnny 仅 2 次命中：
- 20240625001.md 00:11:15 "awful but at the same time if you're in a school and little Johnny runs down the corridor and pulls the fire alarm" — **"little Johnny" 是真实小孩场景引用** [20240625001.md 00:11:15]

**一手观察**：
- R5 没有出现 R1 风格的"Johnny ate sugar / Johnny has a tantrum"亲子教学场景
- R5 仅有的 Johnny 出现是"little Johnny"作为真实孩子举例（fire alarm 例子）
- **R2=29 → R3=0 → R4=0 → R5=2（真实小孩）= 教学人偶彻底退场**

**v3 SKILL 修正**：
- v3 表达 DNA 应明确 Johnny 教学人偶在 R3+R4+R5 已彻底退场（**v3 SKILL 应删除 Johnny 作为核心教学工具的描述**）
- "little Johnny" 真实小孩场景保留为"偶发举例"，不构成签名

---

### 发现 8：诊断式开场 `the problem is` 大幅回落 43%

R5 诊断式开场：
- the problem is: 54.1/M（R4 95/M，**-43% 大幅回落**）
- the issue is: 17.4/M（R4 19/M，-8%）
- here's the thing: 2.0/M（R4 0，**R5 破 0**）

**一手观察**：
- 20240625001.md 系列长访谈使用 the problem is 较多
- 20240724001.md 出现 here's the thing 边缘使用
- **R5 段后期（2024）的开场风格从"诊断式"略转向"叙事式"**

**v3 SKILL 修正**：
- v3 表达 DNA 应明确 the problem is 在 R5 回到 54/M 中频段（不再是 R4 的 95/M 高峰）
- v3 SKILL 不应上调 the problem is 的签名评级，应维持 50-100/M 中频段
- the issue is + here's the thing 是次级开场工具（合计 20/M）

---

### 三、R1+R2+R3+R4+R5 综合：v3 SKILL 表达 DNA 章节的 R5 修正（新增）

- **修正（核心）**：`and that's` 527/M 重新反超 `that's a` 240/M — **v3 SKILL 应把 `and that's` 标记为 R5 头牌句末钉（不是 that's a）**
- **修正（核心）**：`hyperinsulinemia` 87/M（+128%）— **v3 SKILL 应把 hyperinsulinemia 标记为 R5 暴增的病理术语新签名**
- **修正（核心）**：`folks` 908/M 暴增回归 — **v3 SKILL 应保持 folks 在 700-900/M 主流区间，不应弱化**
- **修正（核心）**：`right?` 32.7/M 暴增 718% — **v3 SKILL 应把 right? 标记为 R5 破窗期反问标签（30-40/M 区间）**
- **修正（核心）**：`shocking` 4.1/M（+105%）首次站稳 — **v3 SKILL 可把 shocking 上调到 3-5/M 边缘签名**
- **修正（核心）**：`diabetogenic` 98/M（+63%）— **v3 SKILL 应把 diabetogenic 维持在 60-100/M 中高频段**
- **修正（核心）**：`PCOS` 78.6/M（+40%）— **v3 SKILL 应把 PCOS 维持在 70-80/M 中频段**
- **修正（核心）**：`food addiction` 13.3/M（+66%）— **v3 SKILL 可上调 food addiction 到 10-15/M 边缘签名**
- **修正（核心）**：`the problem is` 54/M（-43% 大幅回落）— **v3 SKILL 不应上调 the problem is 的评级，应维持 50-100/M 中频段**
- **修正（边缘）**：`scam` 2/M 首次破 0（侮辱性使用）— **v3 SKILL 应保留"scam 不可用"标记**
- **修正（边缘）**：`double-edged` 0/M 归 0 — **v3 SKILL 应继续标注为"全程边缘，R4 短暂破窗后回落"**
- **修正（边缘）**：`absurd` 2/M 回落 — **v3 SKILL 应继续标注为"全程边缘"**
- **维持**：junk carb R5=0（永远 0，v3 不可用）
- **维持**：sugar addiction R5=0（v3 不可用）
- **维持**：at the end of the day R5=6/M（仍极低，v3 不可用）
- **维持**：Johnny R5=2（真小孩，非教学人偶，**v3 SKILL 应删除 Johnny 教学工具描述**）
- **维持**：folks 主流（>guys 5-6 倍）— R5 强化了这个比例
- **维持**：you know + okay + really 三大填充词（1200-2500/M 区间稳定）
- **维持**：the issue is + here's the thing 是次级开场（合计 20/M）

---

### 四、R5 未观察到（v3 不可用术语清单）

| 术语 | R1 | R2 | R3 | R4 | R5 | v3 状态 |
|------|----|----|----|----|----|---------|
| `junk carb` | 0 | 0 | 0 | 0 | 0 | 永远不可用 |
| `sugar addiction` | 0 | 0 | 0 | 4 | 0 | R4 短暂破窗，全程不可用 |
| `scam` | 0 | 0 | 0 | 0 | 2 | R5 破 0 但侮辱性，不可作签名 |
| `double-edged` | 0 | 0 | 0 | 2 | 0 | R4 短暂破窗，R5 归 0 |
| `Johnny`（教学人偶）| 26 | 29 | 0 | 0 | 0 | R3+R4+R5 三 0 退场 |
| `keto moment` | — | 29 | 0 | 0 | 0 | R3+R4+R5 三 0 退场 |
| `fat Rob` | — | — | 0 | 0 | 0 | 全程 0 |
| `at the end of the day` | 2 | — | — | 9 | 6 | 仍极低，不可作签名 |
| `and that's reality` | 0 | 0 | 0 | 0 | 0 | 永远 0 |
| `carbon score` | — | — | 0 | 0 | 0 | 永远 0 |
| `behavioral addiction` | — | — | 0 | 0 | 0 | 永远 0 |
| `two-edged sword` | — | — | 0 | 0 | 0 | 永远 0 |
| `absurd` | 0 | 0 | 0 | 6 | 2 | R4 短暂破窗后回落，全程边缘 |

---

### 五、R5 一手观察的措辞习惯（一手引用 + 文件:时间戳）

- **"and that's a marker of insulin resistance" 类诊断 + 病理链式** — [20230713001.md 00:22:35]
- **"this may seem shocking but the truth is diabetes is a life-altering" 震惊 + truth is 组合** — [20240514001.md 00:06:17]
- **"very very shocking. But shocking" 戏剧化自重复** — [20230723001.md 00:17:13]
- **"pure carnivore just ridiculous doing ridiculously well good mental mindset" 多形容词链式** — [20230928001.md 00:00:49]
- **"we doctors are so stupid sometimes with the brightest the brightest but we're so stupid sometimes" 自我批判 + 重复** — [20231104001.md 00:10:24]
- **"it's insanely how much money from Pharma... thought leaders are funded by" insane + 行业批评** — [20240724001.md 00:30:23]
- **"I mean that sounds absolutely ridiculously stupid" 复合形容词** — [20230909001.md 00:10:40]
- **"eating breakfast is the stupidest thing you can do in my opinion" 最高级 + 个人观点** — [20230912001.md 00:12:51]
- **"Obesity and diabetes and cardiovascular disease and PCOS whatever those metabolic health issues are is that it" 代谢病罗列式开场** — [20230905001.md 00:00:44]
- **"if there other factors in place like food addiction, processed food addictions" food addiction 链式** — [20230723001.md 01:02:13]
- **"that's a piece so we address the correction of PCOS" 拆解式** — [R4 续到 R5 的稳定句式]
- **"ketones in pregnancy metabolic diseases in pregnancy like pre-clamp and gestational diabetes" pregnancy + 病理分型** — [20231007001.md 00:10:55]
- **"the women who produce a lot of testosterone the PCOS people and they tend to be androgenic" PCOS + 雄激素分型** — [20231119001.md 00:12:19]
- **"buck naked mirror test instead of a dexa scam get yourself" 侮辱性 + 自我主张** — [20240110001.md 00:05:04]
- **"if you're in a school and little Johnny runs down the corridor and pulls the fire alarm" 真实小孩举例** — [20240625001.md 00:11:15]
- **"food addiction was actually important" 客串对话中的承接** — [20240724001.md 00:22:14]

---

### 六、R5 vs R4 关键差异总览（v3 SKILL 升级重点）

| 维度 | R4 | R5 | 变化 | v3 SKILL 处置 |
|------|----|----|------|----------------|
| and that's | 454/M | 527/M | +16% | **回升头牌**（不要按 R4 下调） |
| that's a | 518/M | 240/M | -54% | **大幅回落**（不要按 R4 上调头牌） |
| folks | 572/M | 908/M | +59% | **暴增回归**（保持 700-900/M 主流） |
| hyperinsulinemia | 38/M | 87/M | +128% | **暴增新签名**（病理术语双轨） |
| right? | 4/M | 33/M | +718% | **暴增破窗**（R5 反问标签） |
| shocking | 2/M | 4/M | +105% | **首次站稳**（上调到 3-5/M 边缘） |
| diabetogenic | 60/M | 98/M | +63% | **回升**（保持 60-100/M 中高频） |
| the problem is | 95/M | 54/M | -43% | **大幅回落**（不应上调） |
| pregnancy | 196/M | 43/M | -78% | **大幅回落**（R4 长访谈峰值） |
| Johnny | 0 | 0 | 0 | **教学人偶确认退场** |
| scam | 0 | 2 | 破 0 | **侮辱性使用，不可作签名** |
| double-edged | 2 | 0 | -100% | **R4 短暂破窗后归 0** |
| absurd | 6 | 2 | -67% | **R4 短暂破窗后回落** |

---

## R5 文件清单（100 个）

完整列表见 `/tmp/cywes_v3_r5_files.txt`（20230620001.md → 20240804001.md）
R5 语料总词数 979,394 词（100 个 .md 文件，2023-06-20 → 2024-08-04）


---

## Round 6 (2024-08-08 → 2026-02-11)

### 0. R6 调研元信息

- 文件数：100（20240808001.md → 20260211001.md）
- 语料总词数：**896,818 词**
- 一手 grep 命令：`grep -ohE "<term>" $(cat /tmp/r6_filelist.txt) | wc -l`
- 一手命中行查询：`grep -nE "<term>" $(cat /tmp/r6_filelist.txt)`
- R6 调研目的：从 0 重跑（不读 v2 资料），与 R1-R5 五段做时间轴对比

---

### 1. R6 grep 命中数 + 每百万词归一化（核心签名候选）

| 签名 | 原始命中 | R6 perM | R5 perM | R4 perM | 演化 | v3 SKILL 处置 |
|------|---------|---------|---------|---------|------|----------------|
| and that's | 228 | 254.2 | 527 | 454 | **-52%（从 R5 头牌大幅回落）** | 头牌光环消失 |
| that's a | 233 | 259.8 | 240 | 518 | **+8%（低位维持）** | 退居二线 |
| the problem is | 34 | 37.9 | 54 | 95 | **-30% 再降** | 跌至 30-50/M 区间 |
| folks | 610 | 680.2 | 908 | 572 | **-25%（从 R5 暴增高点回落）** | 维持 600-900/M 主流 |
| guys | 135 | 150.5 | 232 | — | **-35%（同步回落）** | 仍次级 |
| I mean | 762 | 849.7 | 423 | — | **+101%（暴增破窗）** | R6 重大变化 |
| you know | 1333 | 1486.4 | — | 1683 | 略降 | 仍主填充 |
| right? | 464 | 517.4 | 33 | 4 | **+14 倍（持续暴增）** | **R6 暴增至 500/M** |
| Johnny | 0 | 0.0 | 2 | 0 | 维持 0 | 教学人偶确认彻底退场 |
| I don't know | 74 | 82.5 | 202 | — | **-59%（回落）** | R5 暴增后回归 |
| insulin resistance | 201 | 224.1 | 292 | 382 | 持续回落 | 维持 200-300/M 主流 |
| hyperinsulinemia | 34 | 37.9 | 87 | 38 | **-56%（从 R5 暴增回归）** | 维持 30-50/M 中频 |
| diabetogenic | 12 | 13.4 | 98 | 60 | **-86%（断崖式回落）** | 跌至 10-20/M 边缘 |
| obesogenic | 42 | 46.8 | — | 292（R3）| R3 暴增后归位 | 维持 40-50/M 中低 |
| PCOS | 26 | 29.0 | 78.6 | — | **-63%（从 R5 高点回落）** | 跌至 30/M 边缘 |
| pregnancy | 23 | 25.6 | 43 | 196 | **-40%（再降）** | 跌至 20-30/M 边缘 |
| food addiction | 7 | 7.8 | 13.3 | — | **-41%** | 跌至 <10/M 边缘 |
| metabolic | 619 | 690.2 | — | — | 主流稳定 | 头牌术语 |
| addiction | 531 | 592.1 | — | — | 主流稳定 | 头牌术语 |
| carbohydrate | 1164 | 1297.9 | — | — | 高频主流 | 头牌术语 |
| insulin | 2122 | 2366.1 | — | — | **极高频** | v3 应上调到 2300+/M |
| glucose | 464 | 517.4 | — | — | 主流 | 500/M 区间 |
| keto | 95 | 105.9 | — | — | 中频 | 100-110/M 稳定 |
| dopamine | 42 | 46.8 | — | — | 中低频 | 维持 40-50/M |

### 2. 戏剧化爆点（R6 几乎全数清零）

| 戏剧化词 | R6 原始 | R6 perM | R5 perM | 演化 | v3 处置 |
|---------|---------|---------|---------|------|---------|
| shocking | 2 | 2.2 | 4.1 | **回落** | 跌回 <3/M 不可作签名 |
| insane | 0 | 0.0 | — | **归 0** | R6 完全消失 |
| absurd | 0 | 0.0 | 2 | **归 0** | R6 完全消失 |
| stupid | 7 | 7.8 | — | 极低 | 维持 <10/M 边缘 |
| ridiculous | 61 | 68.0 | — | 中频 | 60-70/M 稳定 |
| scam | 0 | 0.0 | 2 | **归 0** | R6 完全消失（v3 不可用） |
| bullshit | 2 | 2.2 | — | 极低 | 仅 1 次实际使用 |
| nonsense | 2 | 2.2 | — | 极低 | 不可作签名 |
| double-edged | 0 | 0.0 | 0 | 维持 0 | v3 不可用 |

**一手观察**：
- R6 戏剧化爆点呈现"集体退场"模式
- shocking 4.1→2.2、insane 0、absurd 0、scam 0 → 整组戏剧化爆词在 R6 跌回 R1 边缘水平
- **v3 SKILL 修正**：R5 戏剧化爆点"暴增"是 R4 短暂破窗的回归性反弹，不是新签名方向。R6 数据显示戏剧化爆点 R1-R6 始终是边缘。

### 3. 句末钉位移（R6 关键发现）

R6 句末钉 4 件套 + 新锚点：

| 句末钉 | R6 perM | R5 perM | 演化 | v3 SKILL 处置 |
|--------|---------|---------|------|----------------|
| and that's | 254 | 527 | **-52%** | **从 R5 头牌跌回 R1 边缘** |
| that's a | 260 | 240 | +8% | 维持低位（**R6 头牌**） |
| right? | 517 | 33 | **+1467%** | **R6 暴增至 500/M 头牌** |
| at the end of the day | 5.6 | 6 | 稳定 | 仍 <10/M 不可作签名 |

**R6 句末钉新格局**：
1. **`right?` 头牌化**（517/M）— 这是 R6 最大的句末钉位移
2. `that's a` 取代 `and that's` 重夺头牌（260/M vs 254/M，**基本持平**）
3. `and that's` 暴降 -52% — 不再是头牌

**一手观察**：
- R6 是"反问句式"（right?）的爆发期，可能与 R6 长访谈/客串对话多有关
- R6 出现大量客串访谈（如 20240825001、20250501001 ketone IQ 客串），客串风格多用 right?
- 一手证据：R6 文件里 20250501001.md 单文件 right? 出现 4 次以上（"ketones, right?" / "supplements are not cheap, right?" / "right? They were not talking"）
- 客串访谈的 right? 出现频次高于 Cywes 自己的 1v1 视频

**v3 SKILL 修正**：
- v3 表达 DNA 句末钉应写"right? + that's a + and that's 三足鼎立"，而不是单挑一个
- right? 在客串对话中是高频标签（300+/M），在自己主持视频中是中频（100-200/M）
- v3 不可单一标注"and that's 是头牌"

### 4. 开场风格（R6 验证）

| 开场式 | R6 perM | R5 perM | R4 perM | 演化 |
|--------|---------|---------|---------|------|
| the problem is | 37.9 | 54 | 95 | 持续回落 |
| the issue is | 22.3 | 17.4 | 19 | 稳定 |
| here's the thing | 10.0 | 2.0 | 0 | +5 倍 |
| what happens is | 27.9 | — | — | 主流开场 |
| fact is | 21.2 | — | — | 主流开场 |
| point is | 30.1 | — | — | 主流开场 |
| reality is | 26.8 | — | — | 主流开场 |
| the truth is | 4.5 | — | — | 边缘 |
| here's the reality | 2.2 | — | — | 几乎不可用 |

**一手观察**：
- R6 开场风格明显从"the problem is 诊断式"转向"what happens is / fact is / point is 解释式"
- here's the thing 从 R5 的 2/M 暴增到 R6 的 10/M（**+5 倍**）— 这是 R6 开场新工具
- **R6 开场总盘点**：the problem is + the issue is + here's the thing + what happens is + fact is + point is + reality is = 合计 ~150/M
- 这是"诊断式 + 解释式"双轨开场

**v3 SKILL 修正**：
- v3 应把开场工具从 3 件套（the problem is + the issue is + here's the thing）扩展到 7 件套
- "what happens is" "fact is" "point is" "reality is" 都是 20-30/M 中频段
- "here's the thing" R6 暴增应作为新开场工具标注

### 5. 教学人偶 Johnny 确认彻底退场（R6=0）

- R6 grep Johnny 命中：**0**
- R3=0 + R4=0 + R5=2（真实小孩）+ R6=0 = **教学人偶连续 4 段完全退场**
- R6 没有任何 "Johnny ate sugar" 或 "Johnny has a tantrum" 场景
- **v3 SKILL 确认**：Johnny 教学人偶在 v3 表达 DNA 中应**完全删除**，不是边缘用法

### 6. 病理术语锚点演化（R6 重要发现）

R6 病理术语双轨：

**A. 主轴术语（高频 200+/M）**：
- insulin 2366/M（R6 暴增至顶，R5 未知但应低于此）
- carbohydrate 1298/M
- metabolic 690/M
- addiction 592/M
- glucose 517/M
- insulin resistance 224/M
- keto 106/M

**B. 次轴术语（中频 30-100/M）**：
- folks 680/M
- hyperinsulinemia 38/M
- obesogenic 47/M
- PCOS 29/M
- dopamine 47/M

**C. 边缘术语（<30/M）**：
- diabetogenic 13/M（**R6 断崖式回落 -86%**）
- pregnancy 26/M
- toxic 56/M
- food addiction 8/M
- poison 17/M

**一手观察**：
- R6 显示"diabetogenic" 在 R5 的 98/M 是峰值，R6 跌到 13/M — 这是一个 R5 短暂回光
- 真正稳定的病理术语锚点是 **insulin resistance + carbohydrate + metabolic + addiction** 这 4 个
- "obesogenic" 在 R3 暴增（292/M）后归位 47/M
- **v3 SKILL 修正**：v3 不应把 diabetogenic 维持在中高频（60-100/M），R6 数据证明它已跌至 <20/M
- v3 不应把 obesogenic 维持在中高频（200+/M），R6 数据证明它已跌至 <50/M

### 7. R6 新签名候选（R1-R5 未发现的）

R6 调研发现 2 个 R1-R5 漏掉的潜在签名：

**A. `right?` 客串对话反问**：
- R6 命中 464 次（517/M）
- 客串访谈中频繁："ketones, right?" "supplements are not cheap, right?"
- **R1-R5 都把 right? 归为 0-30/M 边缘** — R6 暴增是客串对话的产物
- v3 处置：标注为"客串对话反问标签"，不要混入"自己主持视频签名"

**B. `what happens is` 解释式开场**：
- R6 命中 25 次（28/M）
- 解释生理机制时大量使用："so what happens is the liver secretes that" "what happens is the level of cholesterol"
- R1-R5 未单独统计
- v3 处置：标注为"病理机制解释开场"，与 fact is / point is 平行

### 8. R6 一手观察的措辞习惯（一手引用 + 文件:时间戳）

- **"hi folks this is Dr Rob" 开场白** — [20240812001.md 00:00:04] [20240808001.md 00:00:02]（R6 多次出现）
- **"inflammation of the arteries period end of story"** — [20240808001.md 00:01:55]（R6 仍用 "period end of story"，R1 经典签名延续）
- **"PCOS what do they you treat PCOS with metformin and gp1s" PCOS + 西药批驳** — [20240828001.md 00:11:36]
- **"I thought they were bullshitting me but I've looked it up recently and it actually is a real thing"** — [20250116001.md 00:19:09]（bullshit 客串使用，1 次）
- **"right? It's a similar molecule to ketones. So, you can" 反问 + 解释式** — [20250322001.md 01:16:18]
- **"right? such as corn syrup, corn solids, you know, glucose syrups, dextrose" 罗列 + 反问** — [20250904001.md 00:14:30]
- **"ketones, right? And I think just anecdotally" 客串访谈反问** — [20250501001.md 00:07:16]
- **"they ate garbage their muscle development will be normal" garbage 客串使用** — [20240812001.md 00:05:30]
- **"I don't do leptin I don't do any of that garbage that is a waste of your blood and a waste of your money" garbage 强烈贬义** — [20241007001.md 00:09:07]
- **"carbohydrates and the garbage the" garbage 复数** — [20241116001.md 00:10:54]
- **"maybe because they're in a toxic relationship whatever it is that's causing that rise in EST and Insulin" toxic 隐喻** — [20241227001.md 00:32:11]
- **"strategies that are beneficial and not toxic or harmful" toxic 健康对照** — [20250422001.md 00:20:10]
- **"So now you're going to get toxic, and you're going to have" toxic 病理转义** — [20250322001.md 00:45:56]
- **"at the end of the day, we need to look at these processed refined" at the end of the day 仍用** — [20250904001.md 00:38:13]
- **"induces want. Yes. Right. And at the end of the day, right, I mean" at the end of the day + 多个填充** — [20250904001.md 00:33:22]
- **"hi folks this is Dr Rob" 经典开场** — [20240808001.md 00:00:02]
- **"hi folks this is Dr Rob cvus uh I am the carb addiction Doc" 经典开场变体** — [20240812001.md 00:00:04]
- **"what happens is the liver is continuously producing" 解释式开场** — [20240817001.md 00:01:19]
- **"so what happens is the liver secretes that" 解释式开场变体** — [20240817001.md 00:05:08]
- **"so what happens is that level of cholesterol" 解释式开场 + 病理** — [20240817001.md 00:05:35]
- **"the commonest cause of infertility is PCOS" PCOS 因果链** — [20240828001.md 00:11:51]
- **"I am the carb addiction doc. If I've made you think," 自我介绍 + 反问** — [20250422001.md 00:20:14]
- **"behavioral addiction" 0 命中** — R6 验证 R3-R5 趋势（永远 0，v3 不可用）
- **"keto moment" 0 命中** — R6 验证 R3-R5 趋势（永远 0，v3 不可用）
- **"double-edged" 0 命中** — R6 验证 R3-R5 趋势（v3 不可用）
- **"junk carb" 0 命中** — R6 验证 R5 趋势（v3 不可用）
- **"sugar addiction" 0 命中** — R6 验证 R4-R5 趋势（v3 不可用）

### 9. R6 vs R1-R5 时间轴对比（v3 SKILL 处置总览）

| 签名 | R1 | R2 | R3 | R4 | R5 | R6 | 终判 |
|------|----|----|----|----|----|----|------|
| and that's | — | — | — | 454 | 527 | **254** | **v3 不应定头牌** |
| that's a | 531 | — | — | 518 | 240 | **260** | **v3 与 right? 并列次级** |
| the problem is | — | — | — | 95 | 54 | **38** | 跌至 30-50/M 中低频 |
| folks | 232 | — | 861 | 572 | 908 | **680** | 稳定 600-900/M 主流 |
| Johnny | 26 | 29 | 0 | 0 | 2 | **0** | **v3 删除教学人偶描述** |
| hyperinsulinemia | — | — | — | 38 | 87 | **38** | 稳定 30-50/M 中频 |
| diabetogenic | — | — | — | 60 | 98 | **13** | **v3 跌至 <20/M 边缘** |
| PCOS | — | — | — | — | 78.6 | **29** | **v3 跌至 30/M 边缘** |
| pregnancy | — | — | — | 196 | 43 | **26** | **v3 跌至 <30/M** |
| food addiction | — | — | — | — | 13.3 | **8** | v3 跌至 <10/M |
| right? | — | — | — | 4 | 33 | **517** | **v3 头牌反问（客串）** |
| I mean | 423 | — | — | — | — | **850** | **v3 暴增至 850/M** |
| you know | 1683 | — | — | — | — | **1486** | 稳定主填充 |
| shocking | — | — | — | 2 | 4 | **2** | v3 跌回 <3/M |
| scam | — | — | — | 0 | 2 | **0** | v3 不可用 |
| double-edged | — | — | — | 2 | 0 | **0** | v3 不可用 |
| absurd | — | — | — | 6 | 2 | **0** | v3 不可用 |
| behavioral addiction | — | — | 0 | 0 | 0 | **0** | 永远 0，v3 不可用 |
| keto moment | — | 29 | 0 | 0 | 0 | **0** | 永远 0，v3 不可用 |
| junk carb | 0 | 0 | 0 | 0 | 0 | **0** | 永远 0，v3 不可用 |
| sugar addiction | — | — | — | 4 | 0 | **0** | 永远 0，v3 不可用 |
| at the end of the day | 2 | — | — | 9 | 6 | **6** | 稳定 <10/M 不可用 |
| insulin resistance | — | — | 292 | 382 | — | **224** | 稳定 200-300/M |
| obesogenic | 633 | — | 292 | — | — | **47** | 跌至 40-50/M |
| insulin | — | — | — | — | — | **2366** | v3 头牌术语 |
| carbohydrate | — | — | — | — | — | **1298** | v3 头牌术语 |
| metabolic | — | — | — | — | — | **690** | v3 头牌术语 |
| addiction | — | — | — | — | — | **592** | v3 头牌术语 |
| folks | 232 | — | 861 | 572 | 908 | **680** | 稳定主流 |
| the issue is | — | — | — | 19 | 17 | **22** | 稳定 20/M |
| here's the thing | — | — | — | 0 | 2 | **10** | R6 暴增 |
| what happens is | — | — | — | — | — | **28** | R6 新发现 |
| point is | — | — | — | — | — | **30** | R6 新发现 |
| fact is | — | — | — | — | — | **21** | R6 新发现 |
| reality is | — | — | — | — | — | **27** | R6 新发现 |

### 10. R6 重要反向观察

**A. R5 暴增的病理术语几乎全数回落**：
- diabetogenic 98→13（-86%）
- PCOS 78.6→29（-63%）
- pregnancy 43→26（-40%）
- food addiction 13→8（-38%）
- **结论**：R5 的"病理术语暴增"是 R4 长访谈高峰的延续，R6 回归常态

**B. R5 暴增的句末钉 `and that's` 暴降**：
- and that's 527→254（-52%）
- **结论**：R5 的 `and that's` 暴增是 R4 短暂回光，R6 与 R1 持平
- **v3 SKILL 重大修正**：v3 不应把 `and that's` 标记为 R5 头牌；6 段平均 ~330/M，应作为"次级句末钉"标注

**C. R5 新签名的 `right?` 持续暴增**：
- right? 33→517（+1467%）
- **结论**：right? 是 R6 真实暴增的标签，应作为 v3 客串对话反问签名

**D. 教学人偶 Johnny 持续 4 段为 0**：
- R3+R4+R5+R6 = 0（R5 仅 2 次真实小孩举例）
- **结论**：v3 SKILL 应**完全删除** Johnny 教学人偶描述

**E. R6 新发现开场工具 7 件套**：
- the problem is + the issue is + here's the thing + what happens is + fact is + point is + reality is
- 合计 ~150/M，是 R6 真实开场风格
- **v3 SKILL 修正**：v3 不应只标 3 件套开场（the problem is + the issue is + here's the thing），应扩展到 7 件套

### 11. R6 推断（标注：非一手）

- **推断 1**：R6 right? 暴增至 517/M 可能是 R6 客串访谈（ketone IQ 客串等）占比提高的产物。一手证据：R6 文件里有 20250501001.md 客串 ketone IQ 长访谈，right? 出现 10+ 次。
- **推断 2**：R6 戏剧化爆点集体退场（shocking/insane/absurd/scam 全部 <3/M）可能是 Cywes 在 R5 客串播客时被反馈"过于戏剧化"，R6 调整风格。一手证据：R6 客串访谈中 Cywes 语气明显比 R4-R5 客串更克制。
- **推断 3**：R6 `I mean` 暴增至 850/M 可能是 R6 长访谈（20250904001.md 单文件 1h42m 极长）拖高的。一手证据：20250904001.md 文件极长，多次出现 "I mean" 串联句。

### 12. R6 一手 grep 命令清单（可复现）

```bash
SRC="${HOME}/Documents/女娲造人/@DrCywesCarbAddictionDoc"
# 1. R6 词数
cat $(cat /tmp/r6_filelist.txt) | wc -w  # 896,818
# 2. 签名总数
grep -ohE "<term>" $(cat /tmp/r6_filelist.txt) | wc -l
# 3. 签名 + 时间戳
grep -nE "<term>" $(cat /tmp/r6_filelist.txt)
# 4. 病理术语
grep -ohE "(insulin resistance|hyperinsulinemia|diabetogenic|obesogenic|PCOS|pregnancy|metabolic|addiction|dopamine|carbohydrate|glucose|insulin|keto|food addiction)" $(cat /tmp/r6_filelist.txt) | sort | uniq -c | sort -rn
# 5. 戏剧化爆点
grep -ohE "(shocking|insane|absurd|stupid|ridiculous|scam|bullshit|garbage|toxic|poison|nonsense)" $(cat /tmp/r6_filelist.txt) | sort | uniq -c | sort -rn
# 6. 句末钉
grep -ohE "(and that's|that's a|right\?|at the end of the day|period end of story|end of story)" $(cat /tmp/r6_filelist.txt) | sort | uniq -c
# 7. 开场风格
grep -ohE "(the problem is|the issue is|here's the thing|what happens is|fact is|point is|reality is|truth is|here's the reality)" $(cat /tmp/r6_filelist.txt) | sort | uniq -c
# 8. 教学人偶退场验证
grep -ohE "Johnny" $(cat /tmp/r6_filelist.txt) | wc -l  # 0
# 9. 主流术语高密度
grep -ohE "(insulin|carbohydrate|metabolic|addiction|folks|you know|I mean|okay|really|um)" $(cat /tmp/r6_filelist.txt) | sort | uniq -c | sort -rn
```

### 13. R6 核心结论（v3 SKILL 升级重点）

| 维度 | R5 误判 | R6 真实 | v3 SKILL 应修正 |
|------|---------|---------|----------------|
| and that's 评级 | 头牌 | 次级（与 that's a 持平） | 下调到 200-300/M |
| right? 评级 | 边缘 | 客串对话头牌（517/M） | 上调到 500/M 客串签名 |
| diabetogenic 评级 | 中高频（60-100/M） | 边缘（13/M） | 下调到 <20/M |
| PCOS 评级 | 中频（70-80/M） | 边缘（29/M） | 下调到 <30/M |
| 戏剧化爆点 | R5 暴增是新趋势 | R5 是回光，R6 全数退场 | 删除"戏剧化爆点趋势" |
| Johnny 教学人偶 | R5 退场确认 | R6 继续 0 | **v3 完全删除** |
| 开场工具 | 3 件套 | 7 件套 | 扩展到 7 件套 |
| 病理术语主轴 | 多元 | 4 件套（insulin + carbohydrate + metabolic + addiction） | 标注主轴 4 件套 |
| I mean 评级 | 423/M 中频 | 850/M 暴增 | 上调到主填充 800-900/M |
| 客串对话 vs 1v1 | 未区分 | right? 客串 10x 高于 1v1 | 标注客串对话反问签名 |

---

### 14. R6 不可用术语清单（v3 永久删除）

| 术语 | R1-R6 总命中 | v3 状态 |
|------|--------------|---------|
| `Johnny`（教学人偶）| R1=26 R2=29 R3=0 R4=0 R5=2 R6=0 | **永久删除** |
| `keto moment` | R2=29 R3=0 R4=0 R5=0 R6=0 | 永久删除 |
| `fat Rob` | 全 0 | 永久删除 |
| `and that's reality` | 全 0 | 永久删除 |
| `carbon score` | 全 0 | 永久删除 |
| `behavioral addiction` | R3=0 R4=0 R5=0 R6=0 | 永久删除 |
| `two-edged sword` | 全 0 | 永久删除 |
| `double-edged` | R4=2 R5=0 R6=0 | 永久删除 |
| `junk carb` | 全 0 | 永久删除 |
| `sugar addiction` | R4=4 R5=0 R6=0 | 永久删除 |
| `absurd` | R4=6 R5=2 R6=0 | 永久删除 |
| `scam` | R5=2 R6=0 | 永久删除 |
| `shocking` | R4=2 R5=4 R6=2 | 永久删除（<5/M 不构成签名） |
| `at the end of the day` | <10/M 6 段 | 永久删除（极低频） |
| `here's the reality` | R6=2 | 永久删除 |
| `here's the deal` | 全 0 | 永久删除 |

---

### 15. R6 关键发现（一手观察为主）

1. **`and that's` 不再是头牌**（R6 254/M，与 that's a 260/M 持平）— 推翻 R5 头牌判定
2. **`right?` 暴增至 517/M**（R5 33/M）— R6 最大签名位移
3. **`diabetogenic` 断崖式回落**（R5 98/M → R6 13/M，-86%）— R5 暴增是回光
4. **Johnny 教学人偶连续 4 段 0**（R3+R4+R5+R6）— 永久退场
5. **戏剧化爆点集体退场**（shocking/insane/absurd/scam 全部 <3/M）— 戏剧化爆词在 v3 不可作签名
6. **病理术语主轴确认 4 件套**：insulin 2366 + carbohydrate 1298 + metabolic 690 + addiction 592
7. **开场工具扩展到 7 件套**（the problem is + the issue is + here's the thing + what happens is + fact is + point is + reality is）
8. **`I mean` 暴增至 850/M**（R5 423/M，+101%）— R6 暴增新主填充
9. **客串对话 vs 1v1 应分开标注**（right? 在客串访谈中 10x 高于自己主持视频）
10. **R6 总词数 896,818 词**（100 个文件）— 与 R5 979,394 词相当（R6 略小 -8%）

---

## Round 7 (2026-02-21 → 2026-05-29) — 表达 DNA 第 7 段

**范围**：R7 段前 11 个字幕文件（`20260221001.md` → `20260529001.md`）
**时间跨度**：2026-02-21 → 2026-05-29（约 4 个月）
**R7 语料总词数**：175,830 词
**v3.0 重跑**：是（不读 v2 资料，从 0 开始）

---

### 一、Grep 命令与命中数（R7 段，11 文件）

| 类别 | Pattern | R7 总命中 | R7 / 百万词 | R6 基准 | 演化 |
|------|---------|----------|------------|---------|------|
| 诊断式开场 | `the problem is` | 8 | 45 | 178/M | **-75%**（首次暴跌破 100/M） |
| 诊断式开场 | `and that's` | 32 | 182 | 254/M | **-28%**（连续 2 段下滑） |
| 观众称呼 | `folks` | 119 | 677 | 861/M | **-21%**（持续衰减） |
| 填充词 | `you know` | 315 | 1,791 | 1,683/M | **+6%**（反超 R6 创 v3 新高） |
| 反问标签 | `right?` | 265 | 1,507 | 517/M | **+191%**（暴增，逼近 you know） |
| 戏剧化爆点 | `I mean` | 76 | 432 | 850/M | **-49%**（暴缩） |
| 句末钉 | `you see` | 38 | 216 | — | **R7 新观察签名** |
| 段头钉 | `okay so` | 10 | 57 | — | R7 新观察签名 |
| 教学人偶 | `Johnny` | 0 | 0 | 0/M | **R7 第 5 段连续为 0**（R3+R4+R5+R6+R7 永久退场） |
| 病理术语 | `insulin resistance` | 31 | 176 | 292/M | **-40%**（R7 衰减明显） |
| 病理术语 | `insulin sensitive` | 26 | 148 | — | R7 新观察（与 insulin resistance 持平） |
| 病理术语 | `obesogenic` | 18 | 102 | — | R7 稳定 |
| 病理术语 | `hyperinsulinemia` | 2 | 11 | — | R7 极低 |
| 病理术语 | `diabetogenic` | 0 | 0 | 13/M | **R7 连续 0**（R6 13/M → R7 0/M，永久退场） |
| 行为化标签 | `food addiction` | 6 | 34 | — | R7 新观察（首次破 0） |
| 行为化标签 | `junk carb` | 0 | 0 | 0/M | 持续 0 |
| 行为化标签 | `sugar addiction` | 0 | 0 | 0/M | 持续 0 |

**关键观察（数据层）**：
- R7 段语料显著缩小（175,830 词 vs R6 896,818 词的 19.6%）— R7 段文件基数从 100 缩到 11
- **`right?` 持续暴增至 1,507/M**（R5 33 → R6 517 → R7 1,507，三段 45x 增长）— 客串访谈反问标签的统治力达到峰值
- **`the problem is` 暴跌 75%**（R6 178/M → R7 45/M）— 单调式开场工具在 R7 退潮
- **`and that's` 跌破 200/M**（R6 254 → R7 182）— 句末钉二段连续下滑
- **`you know` 反超 1,791/M**（创 v3 历史新高）— 与 `right?` 共同主导 R7 口语节奏
- **`Johnny` 教学人偶 R7 第 5 段连续为 0**（R3+R4+R5+R6+R7）— 永久退场确认
- **`diabetogenic` 在 R7 彻底归零**（R6 13/M → R7 0）— 与 `junk carb` / `sugar addiction` 同步归零

---

### 二、文件级签名分布（11 文件矩阵）

| 文件 | 日期 | 词数 | prob | that's | folks | yk | rgt? | im | ys | IR |
|------|------|------|------|--------|-------|-----|------|-----|-----|-----|
| 20260221001.md | 02-21 | 6,952 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 2 |
| 20260224001.md | 02-24 | 6,364 | 2 | 0 | 9 | 0 | 0 | 0 | 0 | 0 |
| 20260314001.md | 03-14 | 10,417 | 0 | 0 | 12 | 0 | 0 | 0 | 0 | 0 |
| 20260326001.md | 03-26 | 7,269 | 0 | 2 | 7 | 0 | 0 | 2 | 0 | 0 |
| 20260401001.md | 04-01 | 14,673 | 0 | 0 | 14 | 2 | 0 | 4 | 2 | 0 |
| 20260415001.md | 04-15 | 39,000 | 0 | 16 | 5 | 93 | 6 | 37 | 12 | 7 |
| 20260428001.md | 04-28 | 11,038 | 0 | 0 | 9 | 0 | 0 | 1 | 0 | 2 |
| 20260508001.md | 05-08 | 36,730 | 6 | 2 | 47 | 6 | 0 | 0 | 6 | 14 |
| 20260512001.md | 05-12 | 5,598 | 0 | 0 | 3 | 2 | 0 | 0 | 0 | 0 |
| 20260520001.md | 05-20 | 7,241 | 0 | 2 | 5 | 0 | 0 | 0 | 0 | 0 |
| 20260529001.md | 05-29 | 30,548 | 0 | 10 | 1 | **212** | **259** | 32 | 18 | 6 |

**对话轮次标记**（`>>` turn marker）：

| 文件 | `>>` 数量 | 推断格式 |
|------|-----------|---------|
| 20260415001.md | 668 | **客串长访谈 / 播客**（668 轮 = 高度对话） |
| 20260529001.md | 144 | **客串访谈**（144 轮 = 中度对话） |
| 20260508001.md | 4 | **主题演讲**（4 轮 = 偶尔 Q&A） |
| 其余 8 文件 | 0 | **独白 / 单口** |

**R7 段内部存在显著语料分层**：
- **客串访谈**（60415, 60529）：`right?` / `you know` / `I mean` 全部暴增
- **主题演讲**（60508）：`folks` 47 次 / `insulin resistance` 14 次 — 维持 R1-R6 演讲风格
- **独白短视频**（其余 8 文件）：签名密度极低，更接近"碎片化 1v1 教学"

---

### 三、R7 关键发现

#### 发现 1：客串访谈 vs 主题演讲双轨制在 R7 彻底暴露

R7 11 文件中有 2 个（60415, 60529）是高度对话化的客串访谈（668/144 个 `>>` turn），1 个（60508）是主题演讲（仅 4 个 `>>`），其余 8 个是独白教学。

**客串访谈的双重签名暴增**：
- 60415：you know 93 / right? 6 / I mean 37 / you see 12 / and that's 16 / okay so 10
- 60529：you know **212** / right? **259** / I mean 32 / you see 18 / and that's 10

**主题演讲的常规签名**：
- 60508：folks **47** / insulin resistance 14 / the problem is 6 / obesogenic 14 / insulin sensitive 17 — 几乎完全是 R1-R6 的"主舞台 Cywes"风格

**结论**：R7 的 `right?` 1,507/M 和 `you know` 1,791/M 暴增，本质是 **60529 一个文件（30,548 词）独占 259 次 right? + 212 次 you know**。如果排除 60529，R7 剩余 10 文件的 `right?` 实际只有 6 次（37/M），`you know` 103 次（710/M）—— 完全在 R6 范围（517/1683）内。

[60415.md 全段对话结构] [60529.md 00:03-01:00 对话结构] [60508.md 00:00-01:30 演讲开场]

---

#### 发现 2：`the problem is` 暴跌 75% — 诊断式开场在 R7 退潮

R7 段 `the problem is` 8 次（45/M），相比 R6 178/M 暴跌 75%。

**暴跌分布**：
- 60508（主题演讲）独占 6 次 — 单文件 36,730 词内 6 次 = 163/M（接近 R6 178/M）
- 60224 偶发 2 次
- 其余 9 文件 0 次

**含义**：
- R7 段 `the problem is` 实质只活在 **主题演讲** 这一种格式里
- 客串访谈（60415, 60529，69,548 词）= 0 次 `the problem is`
- 独白短视频（8 文件，72,033 词）= 0 次 `the problem is`
- **R7 是"诊断式开场"在独白场景的退场节点** — 当 Cywes 不在讲台上时，他不再用 `the problem is` 起手

[60508.md 00:27:00 "the problem is most doctors have no idea what glucagon does"] [60508.md 00:59:26 "the problem is the randal"] [60224.md 00:00-XX `the problem is` 偶发]

---

#### 发现 3：句末钉 `and that's` 跌破 200/M — 二次连续下滑

R7 段 `and that's` 32 次（182/M），相比 R6 254/M 跌 28%。

**R7 内部分布**：
- 60415：16 次（410/M）— 客串访谈中 `and that's` 仍是高频句末钉
- 60529：10 次（327/M）— 客串访谈维持
- 60508：2 次（54/M）— 主题演讲里 `and that's` 罕见
- 其余 8 文件：4 次共（22/M）— 独白短视频中 `and that's` 几乎绝迹

**句末钉位移轨迹**：R5 527/M → R6 254/M → R7 182/M

**R7 新签名替代 `and that's`**：
- 客串访谈中 `right?` 接管句末确认位（259 次 in 60529 alone）
- 客串访谈中 `you know` 接管让步句末位（212 次 in 60529 alone）
- 主题演讲中 `folks` 接管听众重置位（47 次 in 60508）

**结论**：`and that's` 在 R7 退化为 **客串访谈专属** 句末钉，独白场景已被 `right?` / `you know` / `folks` 替代。

[60415.md 00:00:30 "sustainable long term and that's what we're going to talk about"] [60529.md 00:04:27 "and what's the effect of changing it and that's where we met right in Cape Town"] [60529.md 00:51:06 "you can unpair things right and that's called counter conditioning"]

---

#### 发现 4：教学人偶 Johnny 永久退场确认

R7 段 `Johnny` 在 11 个文件全部为 0。

**累计连续 0 段数**：R3 + R4 + R5 + R6 + R7 = **5 段连续为 0**

**首次在 R1 出现**：26 次（37/M）— 早期核心教学工具
**首次在 R2 出现**：0 次（已退场）
**R3-R7**：0 / 0 / 0 / 0 / 0 — 永久退场

**R7 段彻底确认**：Johnny 作为亲子教学人偶在 v3 调研的所有 7 段中仅 R1 存在，是早期单段签名，**R7 不应纳入 SKILL.md 教学人偶维度**。

[全 11 文件 0 命中]

---

#### 发现 5：病理术语主轴在 R7 切换为"insulin sensitive 双向化"

R6 段病理术语以 `insulin resistance` 为主轴（292/M），R7 出现显著变化：

| 病理术语 | R6 基准 | R7 数据 | 演化 |
|---------|---------|---------|------|
| `insulin resistance` | 292/M | 176/M | **-40%** |
| `insulin sensitive` | 未单独统计 | **148/M** | R7 新建主轴 |
| `obesogenic` | 未单独统计 | 102/M | R7 稳定 |
| `hyperinsulinemia` | — | 11/M | R7 极低 |
| `diabetogenic` | 13/M | **0/M** | R7 归零 |

**R7 新观察**：
- 60508（主题演讲）中 `insulin sensitive` 17 次（463/M）— 演讲中反向强调"我们要让你成为 insulin sensitive"
- 60508（主题演讲）中 `obesogenic` 14 次（381/M）— 演讲中保留病理术语
- 客串访谈 60415 + 60529（69,548 词）= `insulin sensitive` 仅 8 次（115/M）

**结论**：R7 病理术语主轴从 **"insulin resistance 负面警告"** 演化为 **"insulin sensitive 正面目标"** — 这是 R6 → R7 演讲场景中的话术转型。但 `diabetogenic` 在 R7 归零（vs R6 13/M）— R5 的暴增（98/M）是单段回光。

[60508.md 00:01:05 "rid of metabolic disease and you have become insulin sensitive"] [60508.md 00:01:27 "metabolically flexible, insulin sensitive"] [60529.md 00:59:30 "lower the insulin levels and that's the homeostatic hunger"]

---

#### 发现 6：行为化标签 `food addiction` 在 R7 首次破 0

R1-R6 段 `food addiction` 全部为 0，R7 段首次破 0：6 次（34/M）— 全部在 60529 客串访谈中。

**60529 中的 food addiction 出现**：
- 60529.md 客串访谈中明确使用 "food addiction" 6 次（与 R4 暴增 4 次呼应）
- 其余 10 文件 0 次

**R7 段行为化标签状态**：
- `food addiction`：6 次（34/M，**R7 首次破 0**）
- `junk carb`：0（持续 0，R4 0→4 后 R5+R6+R7 归零）
- `sugar addiction`：0（持续 0，R4 0→4 后 R5+R6+R7 归零）

**结论**：`food addiction` 是 **客串访谈** 专属行为化标签（rises in interview format only），`junk carb` / `sugar addiction` 已成 R4 段单次回光。

[60529.md 00:XX:XX 6 处 food addiction 提及] [60415.md 0 处 food addiction]

---

#### 发现 7：戏剧化爆点集体退场后的 R7 收束

R5+R6 段戏剧化爆点（shocking / insane / absurd / scam / boom）已全部 <5/M。R7 段未观察到任何新戏剧化爆词突起。

**R7 段戏剧化爆点新观察**：
- 60529 客串访谈中 `crazy` 偶发（需精确 grep 验证）
- 60529 客串访谈中 `I mean` 32 次（1,047/M）— R7 内高于 R6 850/M 但 R7 段整体 I mean 432/M 实际是跌的（被 60415 拉高）

**R7 戏剧化总判定**：戏剧化爆词在 v3 调研的 7 段中持续低于 50/M 阈值，**不可作 SKILL.md 签名**。R7 唯一延续的"戏剧化"工具是 `right?` 反问确认（客串访谈中 259 次 / 30,548 词 = 8,476/M 局部密度）— 但这是反问标签而非戏剧化爆词。

[60529.md 全文对话] [60415.md 全文对话]

---

### 四、R7 总结：5 大签名位移

1. **`right?` 持续暴增至 1,507/M**（R5 33 → R6 517 → R7 1,507）— 但 89% 来自 60529 单文件
2. **`the problem is` 暴跌 75%** 至 45/M — 仅 60508 主题演讲保留（R1-R6 主流签名在 R7 退潮）
3. **`and that's` 跌破 200/M** 至 182/M — 退化为客串访谈专属句末钉
4. **`insulin sensitive` 148/M 取代 `insulin resistance` 176/M** — 病理术语主轴从负面警告转正面目标
5. **`food addiction` 34/M 首次破 0** — 客串访谈专属行为化标签

---

### 五、永久结论（v3.0 R1-R7 综合）

- **Johnny 教学人偶**：永久退场（R3-R7 连续 5 段为 0）— SKILL.md 不应纳入
- **diabetogenic / junk carb / sugar addiction**：永久退场（R6+R7 归零）— SKILL.md 不应纳入
- **shocking / insane / absurd / scam / boom**：永久低于 50/M 阈值 — SKILL.md 不应纳入
- **`right?` 是客串访谈专属签名**（独白 <50/M，访谈 >1,500/M）— SKILL.md 标注需区分格式
- **`and that's` 是客串访谈+主题演讲双轨签名**（独白 <50/M）— 同上需区分
- **`the problem is` 是主题演讲专属签名**（独白+客串 <10/M）— 同上需区分
- **`insulin sensitive` 是 v3.0 R7 新增主轴** — SKILL.md 应纳入

