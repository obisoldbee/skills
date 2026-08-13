# 02-conversations.md — R1 (2010-07-01 → 2017-09-29) 对话维度调研

## 调研范围

- **文件数**: 100 个（20100701001.md → 20170929001.md）
- **时间跨度**: 2010-07-01 → 2017-09-29（约 7 年 3 个月）
- **样本路径**: `${HOME}/Documents/女娲造人/@drekberg/*.md`

## 关键前提：这是"独白中的虚拟对话"

字幕来源是 YouTube 自动转录（部分手动），R1 这 100 个文件是 Ekberg 早期 7 年的内容，绝大多数不是采访/对谈。20100701001 是他 2010 年参加十项全能铁饼比赛的 BBC 解说音频（**不是他说话**，是解说员描述他），从他 2011 年 5 月开始才有"演讲/讲座"形式的内容（User Manual for Humans 系列）。

所以"对话维度"在 R1 阶段实际指：他演讲独白中**与现场/屏幕前观众对话的语气**，以及**虚拟场景中的拟人化拟声**（如"the body is going to say that..."）。

## Grep 命令 + 命中数

```
cd ${HOME}/Documents/女娲造人/@drekberg/
```

| 关键词 | 命中文件数 (R1) | 备注 |
|---|---|---|
| `you know` | 20+ (R1 大量) | 早期极高频，后期逐渐降低 |
| `okay so` | 18+ (R1 高密度) | 句首发语词 |
| `okay` | 20+ (R1 持续) | 启动/过渡词 |
| `right` | 单一文件最高 13 次 (20110519002) | 高频确认词 |
| `let me tell you` | 0 (R1) | 2018+ 才出现 |
| `here's the thing` | 0 (R1) | 2018+ 才出现 |
| `the truth is` | 0 (R1) | 2019+ 才出现 |
| `think about it` | 6 (R1) | 2011 集中 |
| `I want you to` | 4 (R1) | 2011-07 集中 |
| `imagine` | 9 (R1) | 2011 集中 |
| `listen` | 9 (R1) | 2011 集中 |
| `look at` | 19 (R1) | 早期高密度 |
| `you see` | 19 (R1) | 早期高密度 |
| `see` | 20+ (R1) | 解释后"you see" |
| `here's what` | 4 (R1) | 2011-06/07 集中 |
| `let me` | 多次（R1 大量，含 show/explain/add） | 演示性"让我做给你看" |

> **核心模式**: R1 阶段他**没有**用 `let me tell you` / `here's the thing` / `the truth is` 这类后期"宣告式"开场。他的开场是 `okay so` / `right` / `you know` / `you see` / `look at` 这类**教学/确认式**开场——这反映早期他定位是"讲师/讲师在教"，后期才转向"宣告者/真理陈述者"。

---

## 5-10 个发现

### 发现 1：开场致辞是固定脚本，定位是"线下讲座的讲师"

`good evening and welcome everybody I am Dr. Sten Ekberg and I'm excited to have you here`
- 来源：**[20110710001.md 00:00:00]** 一手（他说的） 高置信度
- 类似开场在 20110519001 / 20110707001 / 20110712001 / 20110724001 / 20110901003 等多个讲座重复
- 「我们到了第 N 期」是他讲座系列 User Manual for Humans 的标志性开场
- **[我推断]** 这与后期他 YouTube 单口视频的开场（"hey welcome back..."）不同——R1 阶段他把自己定位为"线下观众面前的讲师"而不是"屏幕前的 YouTuber"

### 发现 2：极度高频"教学确认词 right"

`right` 在 20110519002.md 出现 13 次，20110519001.md 出现 9 次，20110519003.md 出现 5 次
- 来源：**[20110519002.md 多个时间点]** 一手（他说的） 高置信度
- 典型用法：`digestion is good right` / `we assume right so` / `bear we we assume right so they're going to be...`
- 这是**教学互动**的语言痕迹——他**在模拟现场有学生回答**的节奏，把观众当成课堂听众而不是 YouTube 观众
- **[我推断]** 这种"假设性 right"在 2018+ 后 YouTube 视频中明显减少，说明他后期不再是"讲课"，而是"输出信息"

### 发现 3：拟人化"身体会说话"是核心修辞

`hormones the female is not going to say that well you know grizzly bears here I I I don't think I want to reproduce right now so the body hasn't figured out...`
- 来源：**[20110519002.md 00:00:56-01:04]** 一手（他说的） 高置信度
- 类似：`laxatives and constipation just says well you know I'm not going to expend energy moving my gut when there's a...`（同文件 00:03:02）
- 他把"消化系统/激素系统/压力系统"拟人化，让它们**有自己的台词**——这是他早期讲座的标志性修辞
- **[我推断]** 后期（2018+）虽然保留这种拟人化，但增加了更多"系统词"（insulin, mitochondria, hormones 的术语化使用），早期则是更朴素的拟人

### 发现 4："熊的故事"是最早的招牌类比

`digestion is good right but it's not going to save you against the bear...your stomach acid is not going to unless you throw up on the bear`
- 来源：**[20110519002.md 00:00:02-00:25]** 一手（他说的） 高置信度
- "熊"作为压力响应的隐喻反复出现（同文件多次"the bear"）
- 教学目的：解释为什么压力时消化、性功能、生长、免疫会被"关闭"（资源分配）
- **[我推断]** "熊/老虎/狮子"这类生存威胁类比贯穿整个 R1，是"压力=身体以为你在野外遇到捕食者"框架的最早版本

### 发现 5：大量"let me show you" 演示性语言

`let me show you right here` / `let me show you the...` / `let me show you what this looks like` / `let me show you how easy it can be to...` / `let me show you some really really simple things`
- 来源：**[20110621002.md, 20110724001.md, 20110710001.md 多个]** 一手（他说的） 高置信度
- 这些是**现场演示（PPT/白板/动作）**的语言标记
- 暗示 R1 内容形式是**线下讲座 + 幻灯片 + 现场演示**，不是 YouTube 录屏或绿幕讲解
- **[我推断]** 这与后期"对着摄像头输出"的模式有结构差异——早期他需要"虚拟地把观众带到白板前"，后期他直接展示图表/食谱/身体示意

### 发现 6：反复用"you see"作为解释结束的标记

`you see everywhere you go there are energy drinks` / `so the body hasn't figured out...you see`
- 来源：**[20110724001.md 00:01:38, 20110519002.md 多个]** 一手（他说的） 高置信度
- 20110516005.md 出现 9 次，20110516003.md 出现多次
- 这是**教学/解释完成**的标志性尾声词
- 后期（2018+）Ekberg 改用 "okay?" / "right?" / "make sense?" 收尾
- **[我推断]** "you see" 是更老的英式教学传统用词（"你看到了吗"），反映他面向**线下成人教育**的语言习惯，而不是 YouTube 网红语言

### 发现 7：讲座开头有"举手法"的现场互动

`how many people here realize that you are an animal hands up`
- 来源：**[20110710001.md 00:00:30-00:00:37]** 一手（他说的） 高置信度
- 同样有"if you recognize them then it's just your opportunity to learn it even better...you can teach them to someone else that you can save their life doing that"
- 来源：**[20110519001.md 00:00:14-00:00:42]** 一手（他说的） 高置信度
- **[我推断]** 这些都是**物理现场**的语言痕迹——他能看到观众举手、看到观众的表情。后期 YouTube 视频里这些互动完全消失，证明他从"讲师"到"内容输出者"的转型

### 发现 8：早期对"holism"的元说明频繁

`there's so much more that that is part of the same mechanism and what is the common denominator` / `because everything that we talk about really is the same thing but we just use different words and we're approaching it from different directions`
- 来源：**[20110713001.md 00:00:13-00:00:43]** 一手（他说的） 高置信度
- 这是他对"整全论/holism"立场的**元说明**——为什么不同主题本质是同一件事
- **[我推断]** 这种元说明在后期大幅减少，因为后期他有了更成型的"insulin resistance → 一切慢性病"单一框架，不需要再解释"为什么这些是同一件事"

### 发现 9：极少的"立场争论" / 反主流医学类话术

R1 阶段几乎没有"Big Pharma"、反疫苗、反医生等后期常见的对立性语言
- 出现的"反医学"语言仅是：`the medical model to take a pill for something`（[20110724001.md 00:00:40]）这种**温和的对照**
- **[我推断]** R1 阶段他还在**教学/科普模式**，没有进入"对抗主流医学"的对立姿态。后期（2018+）随着 keto/carnivore/insulin resistance 框架的成熟，他才转向"挑战既有共识"的姿态

### 发现 10：开场对系列名"User Manual for Humans"反复定义

`we called it that because you everybody gets a user manual for the car they get a user manual for their toaster they get it user manual for their garden gadgets but we have this very very complicated thing called a human body mind and nobody gave us the user manual`
- 来源：**[20110712001.md 00:00:00-00:00:31]** 一手（他说的） 高置信度
- 这是 R1 几乎每期讲座都会重复的**系列名定义**
- **[我推断]** "User Manual for Humans" 是他最早、最稳定的品牌化语言资产；后期这个系列名逐渐让位于"insulin resistance" / "keto" / "Wellness For Life"等更具体的框架

---

## 阶段对比（早期 vs 后期）

| 维度 | R1 (2010-2017) | 后期 (2018+) |
|---|---|---|
| 形式 | 线下讲座 + 现场观众 | 家中录制 YouTube 单口 |
| 开场词 | `okay so` / `right` / `good evening welcome` | `hey welcome back` / `let me tell you` / `here's the thing` |
| 教学确认词 | `right?` `you see?` 高频 | `okay?` `make sense?` 减少 |
| 互动 | `hands up` 现场举手 | 无 |
| 修辞重心 | 拟人化身体、熊的类比、holism 元说明 | insulin/leptin/mitochondria 系统词、宣言式结论 |
| 立场姿态 | 教学/科普、温和对照 | 对抗主流医学、宣告真理 |
| 系列身份 | "User Manual for Humans" | "Wellness For Life" / "Health Champions" / 个人品牌 |

---

## 失败/未发现

- **采访/对谈形式**：R1 这 100 个早期文件中**没有真正的对谈**——所有对话都是他独白中"对虚拟观众说话"或"拟人化身体说话"。Grep `interview` / `Q&A` / `guest` 都没有结果。
- **后期招牌短语**：`let me tell you` / `here's the thing` / `the truth is` 在 R1 **完全不存在**（2018+ 才出现）——这是他语言风格阶段性转变的强证据。

---

## 资源来源标记约定

- **[YYYYMMDD###.md HH:MM:SS]** = 一手（他说的）高置信度
- **其他标注** = 二手或我推断，已在每条发现中明示
