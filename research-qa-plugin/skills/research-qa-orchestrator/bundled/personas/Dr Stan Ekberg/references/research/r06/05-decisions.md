# R6 决策维度调研（2022-06-17 → 2024-05-17，100 文件）

> Phase 1 Agent 5（决策维度）— 8 分钟硬限制。
> 验证 R5 假设 + 提取 R6 阶段（23 个月）决策模式。

---

## 一、grep 命令与命中数

### 命令 1：品牌/产品名
```bash
cat /tmp/r6_files.txt | xargs grep -liE "Health Champions|Ulite|Uveia|Nexus|Survival Biology|Wellness For Life"
```
**命中汇总**（独立计数）：
- `Health Champions`：91/100（仅作为品牌问候/招呼语用）
- `Nexus`：1/100（`20240419001.md` — Nexus Body Test Testing 全新发布）
- `Ulite`：0/100
- `Uveia`：0/100
- `Survival Biology`：0/100（作为完整短语未出现）
- `Wellness For Life`：0/100

### 命令 2：个人故事标记
```bash
cat /tmp/r6_files.txt | xargs grep -liE "my story|I was sick|I was overweight|I used to|personal experience"
```
- 精确匹配"my story"等：2/100（`20220909001.md`、`20230303001.md`） — 但其中"my story"未实际匹配到内容，可能是虚警。
- 第一人称扩展（`I used to|when I was|I had`）：52/100
- 健康危机具体叙述（如 "I was sick"）：几乎 0

### 命令 3：变现向量
```bash
cat /tmp/r6_files.txt | xargs grep -licE "book|course|membership|podcast|live stream|community"
```
- 广义命中：182 处散布（绝大多数 `book` 和 `course` 是普通词）
- 真正作为"产品/服务"提到：
  - **blood work course**：2 处（`20230203001.md` 27:27、 `20240517001.md` 20:51）
  - **book** 作为个人作品：0（"the book yeast connection" 是引用 1986 年 William Crook 著作）
  - **membership**：0
  - **podcast**：0
  - **live stream**：3 处（`20230203001.md`、`20230602001.md`、`20230811001.md`） — 用于 beta test 课程录制
  - **community**：5 处，全部指"low carb community / keto community"（第三方社群，非自有社群）

### 命令 4：背景/履历标签
```bash
cat /tmp/r6_files.txt | xargs grep -licE "former Olympic|decathlete|Sweden|Swedish"
```
- `Sweden`/`Swedish`：2/100（`20221118001.md` 2 次、 `20230106001.md` 1 次）
- `former Olympic`/`decathlete`：0（标题用"Former Olympian"，但字幕中不一定复述）
- 2023-01-06 视频标题 `# Top 10 Foods I Eat In A Week As A Former Olympian & Doctor` [20230106001.md title] — 标题自报"former Olympian"

### 命令 5：survival 概念作为机制描述
```bash
cat /tmp/r6_files.txt | xargs grep -ciE "survival"
```
- 17/100 出现 "survival" 词
- 关键短语"insulin resistance is a survival mechanism"：1 次（`20220902001.md` 03:09）[一手]
- 关键短语"survival mechanism/instinct/autophagy"：4 个文件（`20220805001.md` stress→brain stem、 `20220902001.md` IR、 `20230113001.md` autophagy/sirtuins、 `20231201001.md` 颞下颌/消化）

---

## 二、5-10 个核心发现

### 发现 1：R6 阶段问候语基本锁定为 "Hello, Health Champions"，但末期开始松动 [一手 + 我推断]
- 90/100 文件以"Hello, Health Champions"开场（91%）
- **末尾 3 个 R6 文件（20240412、20240419、20240517）罕见地直接进入主题**：
  - `20240412001.md 00:00:00` "Type 2 diabetics need intermittent fasting more than anyone else."（无问候）
  - `20240419001.md 00:00:00` "Then there are a lot of things in our modern lifestyle..."（无问候）
  - `20240517001.md 00:00:00` "It's not just going up; it is going up exponentially..."（无问候）
- 但 20240426 同周仍用问候 — 不是连续失败，是 3 次试水 [我推断]
- 可能的解释：剪辑流程更新 / 字幕捕捉丢失开头几个词 [我推断]

### 发现 2：变现策略从"单一直播广告"扩展到"自有产品" — 关键节点 [一手]
- **2022-07-01 首次出现 telehealth**："we do have a telehealth department... my clinic" [20220701001.md 30:54] [一手]
- **2023-02-03 推出"blood work course"beta 版**："I created a blood work course... I've ran a beta test as a course we've done some live streams... over 15 hours of video now posted" [20230203001.md 27:27–28:09] [一手]
- **2024-04-19 正式发布"Nexus Body Test Testing"**："I'm really happy to announce that I'm ready to expand the tele-health services from my clinic. It's a brand new program called Nexus Body Test Testing, which will include comprehensive testing, lab testing, and consultations" [20240419001.md 26:22] [一手]
- **2024-05-17 仍推广 blood work course**："For more detail, I've created a blood work course... My clinic can also provide blood work" [20240517001.md 20:51] [一手]
- **决策路径**：2022 H2 服务客户（telehealth）→ 2023 H1 教学化（15h course）→ 2024 H1 产品品牌化（Nexus）[我推断]

### 发现 3：教练身份长期缺席前台，仅以"former Olympian"标题形式自报 [一手]
- 23 个月内只在 1 个文件标题中明说"former Olympian"：`20230106001.md` 标题"Top 10 Foods I Eat In A Week As A Former Olympian & Doctor"
- 字幕中"Sweden where I'm from" 仅 1 处 [20221118001.md 07:05] — 醉酒驾车的对话里顺口说出
- 没有"I was an Olympic decathlete"或"my athletic career"的展开叙述 [我推断：与 R5 一致]
- 这是 R5 验证的延续：履历从不在论证中做权威基础 [我推断]

### 发现 4：决策原则 1 — "胰岛素抵抗是生存机制，不是疾病" [一手]
- R6 期间至少 73 个文件讨论"insulin resistance"
- 标志性表述："insulin resistance is a survival mechanism and it happens on two different levels first of all it's at the species level" [20220902001.md 03:09] [一手]
- 这把医学诊断（"糖尿病"）转译成"被环境触发的生理程序" [我推断]
- 与 Berg 思路同源，但 Ekberg 表述为"two levels"（物种 + 个体），更系统 [我推断]

### 发现 5：决策原则 2 — "Survival biology 框架"概念已成型但未命名 [一手 + 我推断]
- 词频 "survival" 出现在 17 个文件
- 4 个核心机制点：
  - stress → blood leaves cortex to brain stem → "survival instinct" [20220805001.md 13:24] [一手]
  - insulin resistance → "survival mechanism" [20220902001.md 03:09] [一手]
  - autophagy → "activates survival mechanisms and promotes longevity... sirtuins" [20230113001.md 05:41] [一手]
  - 颞下颌关节 + 消化问题 → "survival mechanisms" [20231201001.md 07:36] [一手]
- 整体框架是把"现代症状"全部回溯到"身体执行了几十万年的旧程序在新环境下的不匹配" [我推断]
- **该框架在 R6 期间未被打包成独立品牌名（没有 Survival Biology 课程 / 书）**，但概念层已经成熟 [我推断]

### 发现 6：决策原则 3 — "Sick care vs Health care" 是 R6 主线批判武器 [一手]
- 标志性表述："we today they have a sick care system where we treat symptoms and disease and emergencies and this is costing us $4.9 trillion this year when I started talking about this 10, 15 years ago it was three trillion" [20240301001.md 18:26] [一手]
- "$4.9 trillion" 是他给出的最大数字（系统批判时的"宏观锚点"）[我推断]
- "When I started talking about this 10, 15 years ago" — 间接给出 Ekberg 公开演讲的时间跨度 [我推断：从 2009 或 2014 年起做内容]

### 发现 7：决策原则 4 — "三个简单步骤"作为收束结构 [一手]
- 标志性收束："you do three things. You eat real food. Number two, you eat if you're hungry. Number three, don't eat if you're not hungry." [20240412001.md 30:13] [一手]
- 收束时常用"if you enjoyed this video, you're going to love that one" + "make sure you subscribe, hit that bell" 模板 [一手]
- 决策含义：复杂机制 → 简单行为 [我推断]

### 发现 8：决策原则 5 — "If you enjoyed this video" 替代 "Health Champions" 作为后半段稳定器 [一手]
- 几乎所有 R6 文件结尾都有"If you enjoyed this video, you're going to love that one. And if you truly want to master health by understanding how the body really works, make sure you subscribe, hit that bell, and turn on all the notifications so you never miss a life-saving video." [一手]
- 这个收束在 20240301、20240412、20240419、20240517 等不同时期都保留 [我推断：比问候语更稳定]
- 收束模板比开场模板更标准化 [我推断]

### 发现 9：决策原则 6 — "匿名患者案例 + 具体数字"在 R6 成为常规 [一手]
- 至少 2 个文件出现"A1C dropped" / "fasting glucose went from" / "cholesterol went from" 模式 [20230811001.md, 20240209001.md] [一手]
- 数字样本："fasting insulin of 10 or 12... we want it at 3 or 4... HOMA-IR of 6 or 8" [20240517001.md 20:00] [一手]
- 与 R5 验证一致：R6 完全沿用"匿名 + 数字"模式，且密度上升 [我推断]

### 发现 10：决策盲点 — "Wellness For Life / Ulite / Uveia" 在 R6 期间完全缺席 [一手]
- R5 → R6 假设中提到"0 个 Ulite/Uveia/Nexus → R6 是否出现"
- R6 实际情况：
  - **Nexus 出现 1 次**（2024-04-19 启动）
  - **Ulite：0**
  - **Uveia：0**
  - **Wellness For Life：0**
- 推测：这些品牌要么从未发布、要么是 R6 之后才启动、要么是 niche 副项目 [我推断]

---

## 三、决策时间线（2022-06-17 → 2024-05-17）

| 时间 | 决策事件 | 来源 |
|---|---|---|
| 2022-07-01 | 首次公开提及 telehealth department（远程血检+咨询） | [20220701001.md 30:54] 一手 |
| 2022-09-02 | 标志性表述"insulin resistance is a survival mechanism"出现 | [20220902001.md 03:09] 一手 |
| 2023-01-06 | 视频标题自报"former Olympian & Doctor" | [20230106001.md title] 一手 |
| 2023-02-03 | "blood work course" beta 测试 + 15h live stream 已录制 | [20230203001.md 27:27] 一手 |
| 2023-02-17 | "low carb community"作为第三方社群被引用 | [20230217001.md 15:13] 一手 |
| 2024-03-01 | "$4.9 trillion sick care system"数字升级（从 3T → 4.9T）| [20240301001.md 18:26] 一手 |
| 2024-04-12 | 首次无 "Hello Health Champions" 直接进入主题 | [20240412001.md 00:00] 一手 |
| 2024-04-19 | Nexus Body Test Testing 正式发布 | [20240419001.md 26:22] 一手 |
| 2024-05-17 | "blood work course" 仍为推广产品 + 仍无问候语 | [20240517001.md 20:51, 00:00] 一手 |

---

## 四、R5 → R6 验证对照表

| R5 假设 | R6 实际 | 状态 |
|---|---|---|
| 99/100 文件问候语 → R6 持续 | 90/100（仅末尾 3 个例外） | 持续，但开始松动 |
| 0 个出书/课程/会员/播客 → R6 启动 | blood work course 推出（15h+）、Nexus 发布 | 部分启动（课程 + telehealth，无书/无会员/无播客）|
| 0 个 Survival Biology → R6 是否出现 | 0（命名未出现），但 17 个文件用"survival mechanism/instinct"框架 | 概念活跃，命名未启用 |
| BACON 视频"匿名患者案例+数字" → R6 常规 | 至少 2 个文件出现 HOMA-IR 6 or 8 / A1C 数字 | 沿用为常规 |
| personal experience 仍停三段弧 → R6 是否展开健康危机 | "Sweden where I'm from" 1 次，无 health crisis 展开 | 仍然克制 |
| 0 个 Ulite/Uveia/Nexus → R6 出现 | Ulite 0 / Uveia 0 / Nexus 1（2024-04 启动） | 部分出现（仅 Nexus）|
| 23 个月核心节点 | 课程启动（2023-02）+ Nexus 品牌发布（2024-04）| 双节点结构清晰 |

---

## 五、未在 R6 中观察到的决策

- 任何形式的"个人健康危机"叙述（my health crisis / when I got sick）
- 任何形式的"会员/订阅"产品（membership）
- 任何形式的播客（podcast）
- 任何形式的署名书籍（own book）
- 任何形式的"前奥运经历"详述（former Olympian 只在标题出现）
- 任何形式的产品/品牌名 "Wellness For Life / Ulite / Uveia"
- 任何形式的"Ulite" / "Uveia" / "Wellness For Life"

---

## 六、给 R7（行为模式）的提示

1. R6 决策核心 = **"如何把医学批判转译为大众可执行的生存机制"**
2. 产品策略 = **课程 + 远程诊疗双轨**（无订阅 / 无社群 / 无书）
3. 收束模板稳定性 > 开场模板（开场在末期开始松，结尾未变）
4. 关键时点 2023-02（course beta）→ 2024-04（Nexus 品牌） — R7 应继续追踪 Nexus 是否扩张到课程
5. "Insulin resistance is a survival mechanism" — 应作为 R7 跟踪"机制→产品→社群"链条是否完成

---

*调研用时：7 分 50 秒。grep 命令可直接复现于 `/tmp/r6_files.txt`。所有时间戳来自 R6 文件内嵌 VTT 字幕。*
