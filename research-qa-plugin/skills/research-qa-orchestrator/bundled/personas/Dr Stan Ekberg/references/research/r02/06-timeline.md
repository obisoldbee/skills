# 06-timeline.md — R2 时间线维度调研（@drekberg, 2017-10-02 → 2018-08-17）

> 范围：R2 第 101-200 个 .md 文件，共 100 个。
> 任务：R1 → R2 重点验证 + 2018 年关键节点识别。
> 来源标注：**[一手]** = 字幕原话（文件 + 时间戳）；**[二手]** = 第三方/字幕旁白；**[我推断]**。

---

## 一、Grep 命令记录

```bash
# 必查关键词
grep -l -i -E "Sweden|Swedish|Scandinavia|Europe" [R2 files]       → 1 hit (20180406001)
grep -l -i -E "Olympic|Olympics|decathlon|Barcelona" [R2 files]    → 3 hits (20171120002, 20171120004, 20180406001)
grep -l -i -E "I was born|grew up|born in" [R2 files]              → 1 hit (patient 20171124, 非自述)
grep -i -E "I was" [R2 files]                                      → 多 hits（关键：20180406001 自述 Olympic + fit vs healthy）
grep -l -i -E "Health Champions|Wellness for Life|WFL|HCL" [R2]    → 71 hits (全部 "Wellness for Life" 0 处 "Health Champions")
grep -i -E "Wellness for Life" [R2]                                → 71 hits
grep -i -E "Health Champions" [R2]                                 → 0 hits
grep -i -E "new show|new series|new channel|new format|new season|S2" [R2] → 0 hits
grep -i -E "book|publish" [R2]                                     → 仅推荐他人书，无自传出书
grep -i -E "Cumming Georgia|clinic|office" [R2]                    → 20180606 出现 "Wellness For Life Chiropractic in Cumming Georgia"
grep -i -E "retreat" [R2]                                          → 20180108 Sedona 6 日 retreat
```

---

## 二、5-10 个关键发现

### 发现 1 — 2018-04-06「Why I Make YouTube Videos」是 R2 最重要的元叙事视频

**一手** [20180406001.md 00:00:02]: "this video is about why I started my YouTube channel. I'm trained as a chiropractor but I think that if you're honest, and you keep asking questions, and you keep evolving then you're gonna end up in places you didn't really anticipate necessarily."

**R1→R2 验证**：R1 无完整自述，R2 第一次出现系统化自述视频。这是 R2 期间 Ekberg 主动向观众交代身份的转折点。

---

### 发现 2 — Sweden + 1992 Olympics + decathlete + 第九名（**首次欧洲背景公开**）

**一手** [20180406001.md 00:00:48]: "I started out as an athlete I was a decathlete in the NCAA Div 1 and then I competed for Sweden in the Olympics in 1992 and finished ninth."

**一手** [20180406001.md 00:00:54]: "I was really really fit and really really healthy, but turns out I wasn't so healthy I was just fit."

**R1→R2 验证**：
- R1 无 Sweden/Swedish 任何字样 → R2 公开 "competed for Sweden"（**一手动机兑现**）
- R1 0 个 "former Olympian" 自述 → R2 出现 "I was a decathlete" + "competed for Sweden in the Olympics in 1992"
- R1 无 "fit vs healthy" 二分 → R2 出现（这一对立成为他后续核心理念之一）
- **[我推断]** 他未点出 "former Olympic decathlete" 这个品牌化短语，但首次完整讲出 decathlete + Sweden + 1992 三要素，是品牌化前的"原料"。

---

### 发现 3 — "personal experiences" 健康危机暗示（**未完全展开**）

**一手** [20180406001.md 00:01:10]: "I had gone through chiropractic school and had some personal experiences."

**R1→R2 验证**：R1 0 个健康危机自述 → R2 出现 "personal experiences" 这个**未展开的伏笔**。R2 期间他点到为止，未给细节；这是 R3+ 调研的关键钩子。

---

### 发现 4 — 2017-11-20「Doctor Of The Future Award」是 R2 期间 YouTube 增长节点

**二手**（颁奖方叙述） [20171120002.md 00:00:42]: "the first award goes to Dr. Sten Ekberg is a former Olympic athlete our 2017 on a retreat he expressed the desire to is potentially expand his practice..."

**二手** [20171120002.md 00:00:54]: "him and his wife started a YouTube channel posting video of Cairo tips healthy recipe... his video have reached over 20 truck up to 23,000 years..."

**关键数据**：
- 2017-11 颁奖时点：YouTube 订阅 ~23,000
- "October was my first complete month" [20171120002.md 00:02:18] → Ekberg 自述 2017-10 是回 YouTube 第一个完整月
- "we created that as a patient education tool we want to provide we want it to be a resource for our local community" [20171120002.md 00:02:37] → 原始动机是**本地患者教育**，非全球内容创作

**R1→R2 验证**：R1 无第三方背书 → R2 出现 "Doctor Of The Future Award"（行业内部认证信号）。

---

### 发现 5 — 2018-01-08 Sedona 6 日 retreat（Hale Dwoskin / Sedona Method）

**一手** [20180108001.md 00:00:00]: "Hey I'm Dr. Sten Ekberg coming to you today from Sedona Arizona where I'm attending a retreat with one of my favorite teachers who I'm excited has given us a few minutes of his time this is Hale Dwoskin..."

**一手** [20180108001.md 00:05:34]: "I've certainly enjoyed we're at the end of a six day..."

**R2 期间重要内容合作**：
- Sedona Method = 情绪释放技术（dis-ease / dis-ease 文字游戏）
- 6 日 retreat = Ekberg 2018 年初的思想输入
- **[我推断]** 这是他"结构性 / 化学性 / 情绪性"三体健康框架中**情绪维度**的来源线索（R2 期间他多次提到 "structural, chemical, emotional" 三分）。

---

### 发现 6 — 2018-06-06「Cumming Georgia」公开 + 社区开放日形式扩展

**一手** [20180606001.md 00:00:00]: "Hey I'm Dr. Sten Ekberg with Wellness For Life Chiropractic in Cumming Georgia I am thrilled because for the month of June we are doing a community outreach..."

**关键节点**：
- R2 之前视频未点出诊所地理位置 → R2 末段（2018-06）首次明确 "Cumming Georgia"
- "every day for the month of June" 社区开放日 + 每日 seminars + 折扣 → **R2 末段从 YouTube 单一渠道转向线下社群运营**
- 主题：holistic health / diabetes / autism / obesity
- "there is a healthcare crisis in this country"

**R1→R2 验证**：R1 无明确地点 / 社区运营 → R2 末段双线扩展（YouTube + 线下社群）。

---

### 发现 7 — "Wellness For Life" 是 R2 唯一品牌名（非 "Health Champions"）

**Grep 验证**：
- "Wellness for Life"：71 hits（20171027 → 20180817，R2 完整区间持续使用）
- "Health Champions"：0 hits
- "WFL"：未独立使用（仅作为 Wellness for Life 缩写出现在文案中）

**R1→R2 验证**：
- R1 0 个 "Health Champions" → R2 仍是 0
- R1 "Wellness for Life" → R2 71 hits 巩固为**唯一品牌**
- **[我推断]** "Health Champions"（R1 未见）→ 进一步推断应为 R3+ 阶段才出现的节目/品牌名。

**典型开场** [20171027001.md 00:00:19]: "Hey I'm Dr Sten Ekberg with Wellness For Life and by subscribing and following these videos..."

---

### 发现 8 — 2018-01 起 "new to this channel" 拉新订阅话术成为固定结尾

**Grep 验证**：从 20180126001 开始，"if you're new to this channel" / "hit the subscribe button" / "notification" 标准化话术出现频次急剧增加。

**[我推断]** 这表明 R2 期间 Ekberg 频道从熟人圈（patient education）转向拉新阶段——但他没有任何"新节目 / 新频道 / 新形式" 官宣，新节目在 R3+ 才出现。

---

### 发现 9 — 内容形式演化：2017-10/11 短科普 → 2018 单集长元叙事

**R2 起点的内容**（2017-10-02 ~ 2017-10-27）：
- "Yogurt Recipe For Breakfast" / "How To Grind Flax Seed" / "Chia Seeds vs Flax Seeds" / "Are Expensive Eggs Worth It" / "Neck Stretches" / "Lower Back Herniated Disc" / "Swedish Meatballs" / "How To Never Get Sick Again" → **短小实操，标题 SEO 化**

**R2 中段**（2017-11 ~ 2018-02）：患者案例 + 营养科普 + "Blood Pressure Control" / "How To Lower Blood Sugar And Reverse Your Diabetes" → **主题从"怎么做"转向"为什么"**

**R2 末段**（2018-04 ~ 2018-08）：
- 2018-04-06 "Why I Make YouTube Videos" → **元叙事**（首次讲自己）
- 2018-06-06 "Health And Wellness Seminar Event" → **社区运营 + 拉新**
- 2018-07-30 / 2018-08-13 长篇科普（"a hundred thousand calories" 等深度话题） → **内容纵深加大**

**[我推断]** R2 末段（2018-04 起）是从"科普短视频"向"长内容 + 社区 + 元叙事"的关键转折，2018 是 YouTube 频道形态升级年。

---

### 发现 10 — 2018-08-17 R2 终点：仍在"WFL"单一品牌下做长科普

**一手** [20180817001.md 00:00:08]: "Hey I'm doctor Ekberg with Wellness For Life and if you like to truly master..."

**标题**："Adrenal Fatigue Symptoms, Causes, and Treatment" → 持续在"X 症状 / 原因 / 治疗"三段式科普格式内迭代。

**[我推断]** R2 终点尚未出现"Health Champions"品牌或新节目单飞迹象，R3 调研需重点验证：何时（哪一期）首次出现"Health Champions"作为节目名 / 系列名？

---

## 三、R1 → R2 重点验证表

| 验证项 | R1 结果 | R2 结果 | 结论 |
|---|---|---|---|
| Sweden/Swedish 任何字样 | 0 | 1（仅 20180406 Sweden 奥运自述） | R2 首次公开 |
| 第一人称"former Olympian" 自述 | 0 | 1（20180406 decathlete + Sweden + 1992） | R2 首次完整自述 |
| 健康危机/恢复 自述 | 0 | 1（20180406 "personal experiences" 未展开） | R2 出现伏笔，待 R3 跟进 |
| "Health Champions" 品牌 | 0 | 0 | R2 仍未出现 |
| "Wellness for Life" 品牌 | 有 | 71 hits | R2 完全巩固为唯一品牌 |
| 新节目/新系列/新频道 官宣 | — | 0 | R2 无官宣 |
| 线下社群活动（Georgia） | — | 2018-06 出现 | R2 末段扩展 |
| 内容长度/深度 变化 | — | 2018-04 起显著加深 | R2 末段转折 |

---

## 四、2018 年关键节点总结

| 日期 | 事件 | 来源类型 |
|---|---|---|
| 2018-01-08 | Sedona 6 日 retreat（Hale Dwoskin / Sedona Method） | 一手 |
| 2018-01-26 起 | "new to this channel" 拉新话术成为固定结尾 | 一手 |
| 2018-04-06 | 「Why I Make YouTube Videos」元叙事视频（Sweden + 1992 + decathlete + personal experiences 全部首次自述） | 一手 |
| 2018-06-06 | 「Health And Wellness Seminar Event」社区开放日 + 首次公开 Cumming Georgia 地点 | 一手 |
| 2018-07 → 2018-08 | 长篇深度科普（Adrenal Fatigue / calories storage 等） | 一手 |

**R2 阶段性质** [我推断]：Ekberg 从 "patient education tool"（2017-10/11）走向 "wellness educator with growing platform"（2018-08）。2018 年是 YouTube 频道形态升级年 + 元叙事公开年，但**没有**出书 / 新节目 / Health Champions 品牌化——这些是 R3+ 验证点。

---

## 五、未发现项（grep 验证后明确）

1. **R2 无 Barcelona 字样**（仅 1992 Olympics，未点城市）
2. **R2 无出书**（"book" 全部是推荐他人书：Schwartz principle、DD Palmer、undoctored 等）
3. **R2 无 Health Champions / HCL / WFL（缩写）作为独立品牌**
4. **R2 无 new show / new series / new channel 官宣**
5. **R2 无 I was born / grew up 自述**（出生地/成长地自述缺失）
6. **R2 无 medical disclaimer**（与 R1 一致）

---

## 六、给 R3 的钩子

- "personal experiences" 健康危机 → R3 找具体疾病 / 恢复细节
- Sedona Method 情绪维度来源 → R3 验证他是否在 R3+ 把"情绪"作为独立模块
- 2018-06 社区开放日 → R3 验证是否演化为固定 series / retreat
- "former Olympic decathlete" 品牌化短语 → R3 找首次出现该完整短语的视频
- Wellness for Life → R3 验证是否升级为 "Health Champions" 系列名
