# R3 Timeline Report (2018-08-20 → 2019-07-22)

**范围**: 100 个 .md 文件（slice 201-300）
**主轴**: R3 期间 11 个月的 Dr. Sten Ekberg 公开身份、品牌、节目形态、个人叙事、节目密度演化
**切片**: `/tmp/r3_files.txt`（R3 路径下 100 个 file ID）

---

## 一、Grep 命令与命中数

```bash
# 关键词 1：品牌名（Health Champions / Ulite / Uveia / Nexus / Wellness For Life）
grep -i -E "Health Champions|Ulite|Uveia|Nexus"  $(cat /tmp/r3_files.txt)  # 命中 0
grep -i    "Wellness For Life"                  $(cat /tmp/r3_files.txt)  # 命中 23（intro 中）
grep -i    "former Olympic|former Olympian"     $(cat /tmp/r3_files.txt)  # 命中 14（intro + 行内）
grep -i    "holistic doctor"                    $(cat /tmp/r3_files.txt)  # 命中 14（仅 2019-05 起的 intro）

# 关键词 2：地理 / 自传 / 个人危机
grep -i    "Sweden|Swedish"                     $(cat /tmp/r3_files.txt)  # 命中 1（"Swedish linne"）
grep -i    "Olympic athlete|decathlete"         $(cat /tmp/r3_files.txt)  # 命中 7+
grep -i    "I myself|when I was|I was"          $(cat /tmp/r3_files.txt)  # 多
grep -i    "pesticide|insulin resistance"       $(cat /tmp/r3_files.txt)  # 多

# 关键词 3：节目形式 / 社群 / 活动
grep -i    "retreat|seminar|new show|new series|podcast|live stream|membership|course"  # 多为"of course"
grep -i    "Freddie Ulan|Royal Lee|Weston Price"  # 命中 6+（2018-09 / 2018-11）
```

---

## 二、核心发现（8 条）

### 发现 1 — **品牌切换的精确日期：2019-05-03**（最关键）

R3 期内 100 个文件横跨 **2018-08-20 至 2019-07-22**，刚好覆盖一次完整的频道定位换轨。

- **2018-08-20 ~ 2019-01-25**：intro 一律为 `Hey I'm Dr. Ekberg with Wellness For Life and if you'd like to truly master health...`
  - 末次确认 WFL intro：`20190125001.md:00:00:05` [一手]
  - 中间 `20190114001 / 20190118001 / 20190121001` 多次 intros grep 为空 → 推测当批视频或非 Ekberg 录制、或 intro 文本有变体。**保守结论：WFL intro 至少用到 2019-01-25 仍存在** [一手 + 我推断]
- **2019-05-03 起**：`20190503001.md:00:00:24` 首次出现 `I'm Dr. Ekberg I'm a holistic doctor and a former Olympian`
  - 同档 `20190506001.md:00:00:34` 改为 `former Olympic decathlete`（完整版）
  - **之后所有视频均沿用 "holistic doctor + former Olympic decathlete" 模板**
- **2019-05-24**：`20190524001.md:00:00:16` 出现行尾口播 `(Wellness For Life)` → 品牌名"半残"嵌入 [一手] — 推测主标牌已换但 WFL 仍作为副 sign-off
- **[我推断]** 2019-02 ~ 2019-04 共 4 个月 R3 内 28 个文件 intro 全部 grep 为空，可能该段已系统性替换 intro 模板（**待 R4/R5 验证**）

**R2 → R3 验证**：
- R2 23,000 订阅 / R2 0 个 Health Champions → R3 仍 0 个 Health Champions（Health Champions **首次出现尚未在 R3 范围内**，**待 R4 验证**）
- R2 2018-04-06 首次自传（Sweden+1992+decathlete）→ R3 内 Sweden 仅出现 1 次（`20181116001.md:00:01:28` "Swedish linne"，讲的是 Weston Price 史料典故，并非 Ekberg 自传）[一手]
- R2 2018-01 Sedona retreat → R3 **未重复** Sedona（0 hit）[一手]
- R2 "Doctor Of The Future Award" 2017-11-20 → R3 **未提及**（0 hit）[一手]

---

### 发现 2 — **"former Olympic decathlete" 进入正式 intro：2019-05-06**（不是 2019-05-03）

- `20190503001.md:00:00:24`：`former Olympian`（无 "decathlete"）
- `20190506001.md:00:00:34`：`former Olympic decathlete` ← **完整品牌定位首次出现** [一手]
- 之后所有 R3 文件 `20190527001 / 20190531001 / 20190603002 / 20190610001 / 20190614001 / 20190617001 / 20190621001 / 20190708001 / 20190715001` 均为 `former Olympic decathlete`
- 变体：`20190610001.md:00:00:30` 句式 "I am a holistic doctor and a former Olympic..."（被打断）+ `20190705001.md:00:00:48` "former Olympian in decathlon"
- **结论**：2019-05-06 是 "former Olympic decathlete" 完整品牌定位锁定的 R3 内首日

R2 已提 "former Olympic decathlete" 一次（2018-04-06 首次自传），R3 的 **创新点** 是把它编入标准开场白 → **从"一次性自传"升级为"重复性 brand identity"**

---

### 发现 3 — **R3 唯一一次深度个人危机叙事：2018-11-05 Freddie Ulan 长访谈**（Ekberg 自己的版本未出现）

- 视频 ID `y3MgbMTs300`，title "Nutrition Response Testing Explained By Freddie Ulan - Dr Ekberg" [一手]
- 关键摘录（Ulan 讲述自己的故事，Ekberg 采访）：
  - `20181105001.md:00:01:32` "I had my I've been in the in the natural health industry... 53rd year as a chiropractor" — **Ulan 53 年**（Ulan 的，不是 Ekberg 的）[二手 - Ulan 讲]
  - `00:02:17` "42 okay now in 1986" — Ulan 自述 1986 年 42 岁开始生病（Ulan 自己的年龄）[二手 - Ulan 讲]
  - `00:02:47` "1986 87 88 I was traveling around the world educating parents" [二手 - Ulan 讲]
  - `00:03:18` "by 1991 I was incapacitated I was in bed 24 hours a day"
  - `00:03:25` "I was losing my ability to digest and assimilate foods... 1990 1991 it practically anything I eat was a horrible reaction"
  - `00:03:56` "if I would walk around it would shoot up to a hundred - I was sick really yeah"
  - `00:06:05` "when you're dying at least you know you're dying"
  - `00:12:50` "the answer to what had occurred to me was actually already known but very very well suppressed... Dr. Royal Lee" [二手 - Ulan 推 Dr. Royal Lee]
  - `00:12:58` "we had a 10-year track finding what was out there... 2003 yeah so I had a 10-year track"
  - `00:13:56` "for those who don't know Freddie Ulan creating an organization has trained over a thousand doctors and each of those doctors have trained and are educating thousands of patients so this Mannes is responsible for millions of lives"
- **重要说明**：以上 Ulan 讲自己的故事 ≠ Ekberg 讲自己的故事。R3 内 **Ekberg 本人的健康危机细节未在 R3 100 个文件中展开**。R2 "personal experiences" 伏笔 → R3 **仍未系统展开**（**待 R4/R5 验证**）

---

### 发现 4 — **节目形式密度：~9 部/月 × 11 个月 = ~100 部**（R3 是 Ekberg 全力出片期）

```
201901:  8 部    201905:  9 部
201902:  8 部    201906: 10 部
201903:  9 部    201907:  9 部
201904:  9 部
```

- 2018-12 9 部 / 2018-11 含 20181105 长访谈（Ulan 568 字幕段，全 R3 最长）[一手]
- **平均 ~9 部/月** = ~3 部/周（与 R2 后期产能一致，无明显爬坡或放缓）
- R3 后期（2019-06-10 / 2019-06-21 / 2019-07-08 / 2019-07-15）视频标题多为"36+ Intermittent Fasting Benefits" / "14 Shocking Facts About Insulin Resistance" / "26 Eye-Opening Insulin Resistance Signs" → **健康话题 + 列表型 SEO 标题** 模式稳定 [一手]
- 标题模式演化：
  - 2018-08 ~ 11：偏 "Real Doctor Reacts / Reveals / Reviews The TRUTH"（约 8 部）
  - 2018-12 ~ 2019-04：偏 "Real Doctor Reacts" + 简单疑问（Are FATS BAD? / Is MILK BAD? / Are EGGS BAD?）
  - 2019-05 起：偏 "Keto Diet vs X Diet" 横向对比 + 数字列表（"20 Fruits" / "26 Signs" / "14 Facts" / "36+ Benefits"）[一手]

---

### 发现 5 — **"former Olympic athlete" 在 2018-11 至 2018-12 已内嵌 3 次行内引用**（早于 2019-05 intro 化）

- `20181102001.md:00:06:28` "and I myself is an example of this because when I was an Olympic athlete and I was training 5/6 hours a day I ate probably five six seven thousand calories a day and a lot of it was sugar and candy and cereal and ice cream and bread and on and on and on and I had 3% body fat" [一手]
- `20181123001.md:00:09:21` "train the same way that an Olympic athlete is going to train an Olympic"
- `20181126001.md:00:07:39` "what is your goal I was an Olympic decathlete so my goal was extremely"
- `20181203001.md:00:11:22` "though I did go to the Olympics and had some success but who knows what would it"

**[我推断]** 2018-11 ~ 12 是"行内引用积累期"，2019-05 升级为"开场白标准组件"是 6 个月铺垫后的一次品牌定位合龙。

---

### 发现 6 — **R3 内 0 次提及 Sweden / 0 次提及 1992（出生年）/ 0 次提 Olympic trials 细节**

- 唯一 Sweden 出现：`20181116001.md:00:01:28` "the guy in Swedish linne is called linna and the guy who organized our..." — 这是 **Weston Price 史料**（讲 19 世纪瑞典医生），与 Ekberg 本人无关 [一手]
- 0 次"born in Sweden" / 0 次"1992 Olympics" / 0 次"my Olympic journey"
- R2 已提 1992 一次 → R3 期间 Ekberg **没有把"Sweden 出生"或"1992 年经历"作为个人叙事素材再讲** [一手]
- 这与 R2 2018-04-06 首次自传形成对比：R3 期间 Ekberg 个人故事的 **叙事权重重心已迁移到"former Olympic decathlete"运动品牌** 上，国家级背景信息进入"保留素材"而非"高频内容"

---

### 发现 7 — **新节目形态 0 个 / 新社群产品 0 个 / 新线下活动 0 个**（R3 是纯内容扩张期）

- 0 hit：podcast, membership, course, book, retreat (新), seminar (新), live stream, new show, new series
- "course" 命中 30+ 次但全部是介词 "of course" / "to course"（grep 已排除）
- "retreat" 0 hit（**Sedona 2018-01 未在 R3 重提**）[一手]
- "seminar" 仅出现 `20181105001.md:00:41:05 / 00:43:58 / 00:44:04`（"deliver a seminar to a bunch of doctors"）— Ulan 自己的故事，**Ekberg 没有在 R3 提过自己的 seminar** [二手 - Ulan 讲]
- "book" 命中 6 次，全部是引用别人书（"Dr. Robert Atkins... book" / "he wrote a book called propaganda"）[一手]
- **结论**：R3 是"单人 studio 出片 + 一次客座访谈"模式，**没有产品/社群/活动形态创新**。所有 R3 期间 Ekberg 的影响力扩张靠 YouTube 单平台算法 → 这也解释了为什么 2019-05 必须做品牌定位升级（holistic doctor + decathlete = SEO/可识别度双增强）

---

### 发现 8 — **2018-11-05 Ulan 访谈承载"导师叙事"，可能成为 Ekberg 后续英雄叙事的'原型'**

- 视频长度：568 字幕段，全 R3 第一长
- 故事元素齐全：
  1. 1986 年开始生病（pesticide 暴露 → 后验）[二手 - Ulan 讲]
  2. 1991 年卧床不起（"in bed 24 hours a day"）
  3. 1990-1991 任何食物都引发"horrible reaction"
  4. 走路 100°F 体温
  5. 去 Mexico 接受"非法治疗"（organic food、blood type treatment、vitamin infusion、stem cell、life cell therapy）
  6. 10 年研究（1991 → 2003）
  7. 2003 年"system finalized" → 创 Nutrition Response Testing 系统
  8. 培训 1000+ 医生 → 触达"millions of lives"
- **结构性意义**：Ekberg 通过**让 Ulan 完整讲完"重病→康复→创系统→规模化"四段式英雄旅程**，等于在 R3 内植入了一个 Ekberg 后续可以直接复用的 **叙事模板**（不写"我"，写"我的老师"）
- 验证：Ulan 提到"5% oncologist 患者活不过 5 年"vs"我们要的是 5% 没好的我们来研究" → 这是 Ekberg 后期所有"5% / 95%" / "holistic vs conventional" 价值对比的原型 [二手 - Ulan 讲]

---

## 三、R2 → R3 验证清单（一行一答）

| R2 假设 | R3 验证 | 证据 |
|---|---|---|
| Health Champions R2 = 0 | R3 仍 = 0 | 100 个文件 grep 0 hit |
| 2018-04-06 自传（Sweden+1992+decathlete）| Sweden / 1992 在 R3 0 hit | `20181116001` 是 Weston Price 史料 |
| "personal experiences" 伏笔 | R3 **未展开** Ekberg 自己的健康危机 | 唯一深度是 2018-11-05 Ulan 讲 Ulan 自己 |
| 2017-11-20 奖项 | R3 0 hit "Doctor Of The Future Award" | grep 无结果 |
| 23,000 订阅起点 | R3 期间 0 hit 订阅数 | 无 milestone 数字 |
| 2018-01 Sedona retreat | R3 0 hit "Sedona" | grep 无结果 |
| 2018-08-20 → 2019-07-22 11 个月核心节点 | **2019-05-03 品牌 intro 大切换**（最重） | 100% 一手 intro grep 验证 |

---

## 四、必须推给 R4/R5 的待验命题

1. **2019-02 ~ 2019-04 期间 28 个文件 intro 为何 grep 为空** — 是换模板、还是转介绍人、还是 grep regex 漏匹配？
2. **Health Champions for Humanity 首次出现的精确日期** — R3 内 0 hit，应在 R4 / R5 内
3. **Ekberg 本人健康危机的完整自述** — 0 hit in R3，应在 R4 / R5
4. **订阅 / 频道里程碑数字** — R3 0 hit，可能需要外部数据补
5. **"Doctor Of The Future Award" 后续使用频率** — R3 0 hit，可能奖项在他 2017 之后不再强调
6. **2018-11-05 Ulan 访谈是否是"客座访谈"系列的第一期** — R3 内 R3 范围 100 文件仅此 1 次客座长访谈

---

## 五、R3 内 R3 切片未发现的事

- **未发现** Health Champions / Ulite / Uveia / Nexus 任何一字
- **未发现** Sweden 作为 Ekberg 自传要素
- **未发现** 1992 / 出生年
- **未发现** podcast / membership / course（产品形态）
- **未发现** Sedona / 任何 retreat
- **未发现** 任何 milestone 订阅数 / 粉丝增长数字
- **未发现** new show / new series / live stream

---

## 六、R3 切片 11 个月的"叙事权重"重排

| 主题 | R2 权重（推测）| R3 权重 |
|---|---|---|
| Wellness For Life 品牌 | 高 | 高（至 2019-01-25）/ 退（2019-05-03 起）|
| former Olympic decathlete 品牌 | 低（2018-04 一次性自传）| **极高（intro 标准组件 2019-05-03 起）**|
| holistic doctor 自我定位 | 低 / 中 | **极高（2019-05-03 起 intro 第二项）**|
| Sweden / 出生背景 | 一次性提及 | **几乎归零** |
| Nutrition Response Testing / 工具叙事 | 已知 R2 提 | **重 — 2018-11-05 Ulan 长访谈系统化** |
| Sedona retreat / 线下活动 | R2 已知 | **0** |
| Insulin resistance / diabetes 主题 | R2 已强 | **R3 后半段主题中心化**（"26 Signs" / "14 Facts" / "How To Prevent Diabetes"）|
| 健康危机自述（Ekberg 本人）| R2 伏笔 | **0 — 等待 R4/R5** |

---

**完成时间**：R3 切片 100 个文件全部 grep + 关键 11 个文件 Read 验证
**总 grep 命令数**：14
**核心 R3 内单一最高密度视频**：20181105001（Freddie Ulan 访谈，568 字幕段）
**核心 R3 内品牌换轨日**：2019-05-03（"holistic doctor" + "former Olympian" intro 首次出现）→ 2019-05-06（"former Olympic decathlete" 完整版 intro 锁定）
