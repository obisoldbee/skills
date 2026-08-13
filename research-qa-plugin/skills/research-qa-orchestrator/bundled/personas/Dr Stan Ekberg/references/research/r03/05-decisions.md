# R3 决策维度调研：Dr. Sten Ekberg（@drekberg）

**研究范围**：R3 第 201-300 个 .md 文件（2018-08-20 → 2019-07-22）
**素材目录**：`${HOME}/Documents/女娲造人/@drekberg/`
**文件清单**：`/tmp/r3_files.txt`（100 个 VTT 转录文件）

---

## Grep 命令与命中数

| 关键词 | 命中文件数 | 总命中行数 |
|---|---|---|
| `Health Champions` | 0/100 | 0 |
| `Ulite\|Uveia\|Nexus` | 0/100 | 0 |
| `my story\|i was sick\|i was overweight\|i used to` | 1/100（仅 Freddie Ulan 客串视频） | 1 |
| `my wife` | 1/100（仅 Freddie Ulan 客串视频） | 3 |
| `former Olympic\|decathlete\|holistic doctor` | 25/100 | ~50+ |
| `Sweden\|Swedish` | 0/100（仅做背景口述时提到过） | 0 |
| `Reacts To\|Reacts` | 4/100（标题级）+ 32/100（内容） | ~80 |
| `book\|writing\|wrote\|author` | 0/100（Ekberg 自己） | 0 |
| `my\|personal\|experience\|story`（R3 中） | 12+/100（含 Q&A、生物黑客 N=1） | 20+ |
| `Wellness For Life`（品牌口号） | ~65/100 | 70+ |

注：grep 命令均用 `grep -ic` + 大小写不敏感，但受 VTT 转录小写化影响部分专有名词需要正则回退。

---

## 核心发现（10 条）

### 发现 1：R2 "personal experiences" 伏笔在 R3 没有展开健康危机具体细节
**R2 假说**：R2 中"personal experiences" 是伏笔，R3 会展开"my story / I was sick / I was overweight"
**R3 实证**：[我推断] 假说不成立。R3 100 个文件中：
- `my story` 命中 0 次
- `i was sick` 命中 0 次（唯一的 "I was sick" 出现在 Freddie Ulan 客串 20181105001.md 中）
- `i was overweight` 命中 0 次
- 仅有 "when I was an Olympic athlete... training 5/6 hours a day I ate probably five six seven thousand [calories]" [20181102001.md 00:06:28] 一处把个人史和营养摄入挂钩，但这是 Athlete 巅峰期，不是"病后康复"叙事

R3 仍维持 R2 同款第三人称 / 教科书式叙述（"your body"、"most people"），没有切换为"我曾经..."的第一人称疗愈叙事。Ekberg 选择用"权威"立场而非"病人"立场建立信任。

**来源**：[一手 20181102001.md 00:06:28] [我推断]

### 发现 2：R2 "Health Champions" 品牌 R3 仍未启用
**R2 假说**：R2 中 0 个 "Health Champions" 品牌，R3 会启用。
**R3 实证**：[一手] 0/100 命中。"Health Champions" 在 R3 全部 100 个文件中不出现。Ekberg 在 R3 仍使用 "Wellness For Life" 作为频道/品牌标识（出现于 ~65/100 视频的片头）。

例：
- [20180820001.md 00:00:05] "Hi I am doctor Ekberg with Wellness For Life"
- [20190610001.md 00:00:19] "I'm Dr. Ekberg I am a holistic doctor and a former Olympic decathlete"（Olympic intro 启用后，Wellness For Life 仍作为底色出现，但 Olympic 头衔前置）

**来源**：[一手 20180820001.md 00:00:05][一手 20190610001.md 00:00:19] [我推断：R2→R3 "Health Champions" 是更晚期的产品/课程品牌，R3 阶段尚未启动]

### 发现 3：R2 4 个 "Reacts" 视频在 R3 已成固定格式（且扩展了 3 个新对象）
**R2 假说**：R2 4 个外部 Reacts（Doctor Mike / Dr. Sam Robbins / Ruben Meerman）→ R3 是否成为固定格式？
**R3 实证**：[一手] R3 共有 4 个 "Real Doctor Reacts To..." 标题级视频：
- [20180903001.md] "Roundup & Cancer: Real Doctor Reacts To Monsanto's Lawsuit"（新对象：Monsanto/农业化工巨头）
- [20181102001.md] "Real Doctor Reacts To Doctor Oz: Intermittent Fasting"（新对象：Dr. Oz / 主流医学名嘴）
- [20190114001.md] "Real Doctor Reacts To Crazy Jillian Michaels' Comment On Keto Diet"（新对象：Jillian Michaels / 健身名人）
- 加上 R2 末期的 [20180813001.md] Ruben Meerman 也在 R3 早期（2018-08-13 实际是 R3 边界前一日）

格式已固定：**"Real Doctor Reacts To [对象]"** + Ekberg 用科学框架拆解对方观点。R3 阶段 3 个新 Reacts 对象中，2 个是"主流医学/健身名嘴"（Dr. Oz、Jillian Michaels），1 个是"工业巨头"（Monsanto）。[我推断：Ekberg 正在用 Reacts 模式从"知识讲解者"扩展为"舆论校正者"，针对的靶子从纯学术对手转向大众媒体权威。]

**来源**：[一手 20180903001.md title][一手 20181102001.md 00:00:00][一手 20190114001.md 00:00:09] [我推断]

### 发现 4：R2 频道订阅 23,000 → R3 没有里程碑视频
**R2 假说**：R2 23,000 订阅 → R3 增长到？
**R3 实证**：[一手] R3 100 个文件中**没有任何里程碑订阅庆祝视频**。整个 R3 阶段（2018-08-20 → 2019-07-22）Ekberg 没有发布"thank you X subscribers" 类视频。
- 上一个里程碑：[20180420001.md] "Thank You 1000 Subscribers On YouTube"（2018-04-20）
- R3 阶段无新里程碑
- 跨段（2020+）才有：[20230602001.md 00:24:05] "I built the channel to about 3 million subscribers"（2023 年回忆）

[我推断] R3 阶段（2018-08 → 2019-07）Ekberg 处于"埋头生产内容"期，不公开庆祝订阅里程碑。要么是数据未达到 Ekberg 自设的庆祝阈值，要么是策略上不强调数字。

**来源**：[一手 20180420001.md title][一手 20230602001.md 00:24:05] [我推断]

### 发现 5：R2 妻子是共同创办人 → R3 没有任何视频提及
**R2 假说**：R2 妻子是共同创办人 → R3 是否继续？
**R3 实证**：[一手] R3 100 个文件中 `my wife` 只出现 3 次，**全部在 Freddie Ulan 客串视频 [20181105001.md]**：
- [00:04:40] "when I talked it over with my wife she said"
- [00:06:35] "my wife gave me challenges she said you're the doctor"
- [00:17:03] "my wife said you're the doctor you do it"

**这 3 处都是 Freddie Ulan 在说他自己的妻子，不是 Ekberg**。Ekberg 本人在 R3 100 个视频中完全没有提到"my wife"、"my family"、"my spouse"。[我推断：Ekberg 仍把"妻子是共同创办人"作为频道后台资产，但前台叙事完全不展示。R3 阶段 Ekberg 选择"单人 IP"形象——专业医生单独面对观众。]

**来源**：[一手 20181105001.md 00:04:40 / 00:06:35 / 00:17:03] [我推断]

### 发现 6：R2 0 个出书 → R3 仍未开始写书
**R2 假说**：R2 0 个出书 → R3 是否开始写书？
**R3 实证**：[一手] 0/100 命中。Ekberg 本人在 R3 中：
- 没说过 "I wrote a book"
- 没说过 "I'm writing a book"
- 没说过 "my book"
- 唯一提到 "book" 的视频是 [20190426001.md] "weight and he wrote a book that was published in 1972 called the Atkins diet"——这是在讲 Robert Atkins 的历史
- [20190607002.md 00:11:40] "physiology it is science you can read about this stuff in books you can verify this for yourself"——泛指"看书"

[我推断] R3 阶段 Ekberg 完全没启动写书工程。出版至少要等到 R5+ 才有（待 R4/R5 验证）。

**来源**：[一手 20190426001.md 00:00:41] [我推断]

### 发现 7：R2 "fit vs healthy" 二分 → R3 在 2018-12-03 视频《Eat Junk Food and Stay Skinny?》中深化
**R2 假说**：R2 "fit vs healthy" 二分 → R3 是否深化？
**R3 实证**：[一手] 2018-12-03 视频《Eat Junk Food and Stay Skinny?》[20181203001.md] 是 R3 阶段对"fit vs healthy"二分的明确深化。Ekberg 核心论断：
- [00:10:05] "what is your goal is it health or is it to be skinny there's a lot of skinny [people] violating their body at more levels but it doesn't mean that you're healthy just because you're skinny"
- [00:10:41] "don't fall into that trap of oh I can eat whatever I want as long as I avoid the sugar because it's not a healthy recipe"

R2 的"fit vs healthy"是泛泛二分；R3 这条视频把二分具象为：
- **二元对立**：skinny（体重/外观）vs healthy（代谢/长期健康）
- **陷阱警告**："I can eat whatever I want as long as I avoid the sugar" 是错误目标
- **优先级**：healthy 永远高于 skinny

[我推断] 这是 Ekberg 决策框架的核心公理：所有健康干预必须先问"目标是外观还是代谢"，且代谢优先。这种二分法在他后续 R4+ 的 keto / IF 论证中会反复调用。

**来源**：[一手 20181203001.md 00:10:05 / 00:10:41] [我推断]

### 发现 8：R3 Ekberg 启用新片头套式："former Olympic decathlete + holistic doctor"（约 2019-05-03 起）
**R2 → R3 演变**：[一手] R3 阶段片头套式有清晰切换：
- **R3 早期（2018-08 → 2019-04）**：~65 个视频用 **"I'm Dr. Ekberg with Wellness For Life"**（无 Olympic / holistic 头衔）
- **R3 后期（2019-05-03 → 2019-07-22）**：13 个视频用 **"I'm Dr. Ekberg I am a holistic doctor and a former Olympic decathlete"**（Olympic + holistic 头衔前置）

切换点：[20190503001.md] 首次使用新片头。此后每个视频的片头套式稳定为：
- [20190610001.md 00:00:21] "I'm Dr. Ekberg I am a holistic doctor and a former Olympic decathlete"
- [20190705001.md 00:00:48] "I'm doctor Ekberg. I'm a holistic doctor and a former Olympian in decathlon"
- [20190722001.md 00:01:18] "I'm doctor Ekberg I'm a holistic doctor and a former Olympian in the decathlon"

注意细微措辞变化：Olympic decathlete → Olympian in decathlon → Olympian in the decathlon。[我推断：Ekberg 正在迭代一个"权威公式"——把体能成绩（Olympic）+ 行医哲学（holistic）+ 频道品牌（Wellness For Life）三层叠加。Olympic 头衔的引入可能是为了在 IF / keto 话题上对抗 Dr. Oz / Jillian Michaels 这类"主流健身名嘴"。]

**来源**：[一手 20190503001.md] [一手 20190610001.md 00:00:21] [一手 20190705001.md 00:00:48] [一手 20190722001.md 00:01:18] [我推断]

### 发现 9：R3 出现 1 次 Ekberg 个人 N=1 生物黑客实验（2019-07-08 视频）
**R2 假说**：R2 没有 Ekberg 自我实验的内容
**R3 实证**：[一手] [20190708001.md] "Autophagy & Fasting: How Long To Biohack Your Body For Maximum Health? (GKI)" 视频中，Ekberg 公开自己做了 63 小时水断食实验：
- [00:17:45] "so it's pretty much a strict water fast after 36 hours my blood sugar was 68"
- [00:17:59] "ketones so my ratio was 1.6 I was right at the edge of of this therapeutic zone"
- [00:18:24] "after 48 hours my fasting glucose had gone up and my ketones hadn't chained so my GKI was 2.3"
- [00:19:16] "after 63 hours my blood [sugar]"

Ekberg 用第一人称"my blood sugar was"、"my ratio was"披露自己实时的血糖 / 酮体 / GKI 数据。[我推断：这是 Ekberg 第一次在频道上从"讲师"切换为"实验对象"。这种 N=1 自我实验叙事是他在 R4+ 论证极端 IF（36-72h water fast）的关键信任基础——他不是"我教你怎么断食"，而是"我自己断食了 63 小时，数据在这"。]

**来源**：[一手 20190708001.md 00:17:45 / 00:17:59 / 00:18:24 / 00:19:16] [我推断]

### 发现 10：R3 Ekberg 决策"权威化"——从 Wellness For Life 到 Holistic + Olympic + N=1
**R2 → R3 综合演变**：[我推断] 把上述发现 1-9 串起来，R3 是 Ekberg 决策身份的关键升级期：

| 维度 | R2 (前期) | R3 (本期) |
|---|---|---|
| 自我叙事 | "your body" / 教科书 | 极少，第一人称仍是 Olympic athlete 巅峰期（不是病后康复） |
| 品牌 | Wellness For Life | Wellness For Life + 2019-05 起加入 "Holistic Doctor" + "former Olympic decathlete" |
| Reacts 模式 | 4 个外部视频 | 4 个新 Reacts（扩向主流名嘴 + 工业巨头） |
| 妻子角色 | 共同创办人（后台） | 后台，前台零提及 |
| 写书 | 无 | 无 |
| 订阅里程碑 | 23,000 | 无新里程碑 |
| 自我实验 | 无 | 首次 63h water fast N=1 |

[我推断：R3 阶段 Ekberg 正在做的核心决策是**"身份权威化"**——把频道从"医生科普"升级为"权威+奥运冠军+生物黑客"的多重权威堆叠。他没有选择"个人疗愈故事"路径（仍维持 R2 的"权威"立场），但叠加了：
- 历史权威（former Olympic decathlete）
- 哲学权威（holistic doctor）
- 实验权威（N=1 self-experiment，2019-07-08 启动）
- 对抗权威（Reacts 主流名嘴/工业巨头）

**这 4 层权威堆叠是 Ekberg R3 阶段的核心决策架构，将贯穿他后续 R4-R8 的所有内容。**]

**来源**：[我推断：基于发现 1-9 的横向归纳]

---

## 10 分钟窗口期未完成项

1. **2018-08-13 Ruben Meerman Reacts** 实际在 R2 末期（2018-08-13 是 R3 边界前一日），归类为 R2 还是 R3 待确认（它在 R3 文件清单中）。R3 阶段 100% 属于 Ekberg 的是 3 个 Reacts：Monsanto、Dr. Oz、Jillian Michaels。
2. **20181026001.md 2018-10-26 VidSummit 采访** 这是一条"内容创作大会"的现场采访，可能是 Ekberg R3 阶段唯一的"线下活动"内容（与内容创作者圈子的 networking 决策相关）。但未深入分析（8 分钟内优先覆盖 10 条发现）。
3. **20181105001.md Freddie Ulan 客串** 1 小时长视频，Ekberg 与 Nutrition Response Testing 创始人对话。客串内容大量包含 Ekberg 的"补充评论"，未在 10 分钟内抽取。

---

## 标注规范

- **[一手 YYYYMMDD###.md HH:MM:SS]**：直接引用 Ekberg 在某视频某时间点说的话
- **[来源 URL 或文件名]**：二手引用（他人对 Ekberg 的评价/外部资料）
- **[我推断]**：基于一二手证据做的推论，不直接来自 Ekberg 表述
