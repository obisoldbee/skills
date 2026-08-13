# R2 Decision Dimension — Dr. Sten Ekberg (@drekberg)

**R2 切片**：`/tmp/r2_files.txt`（100 个文件，2017-10-02 → 2018-08-17）
**调研方法**：grep-first，仅在命中高价值片段时 Read 全文。
**时间**：2026-06-05
**核心问题**：R1（2017 早中期）未出现的"自传 / 品牌 / 瑞典背景 / 自述健康危机"是否在 R2 出现？公开决策（节目改版 / 品牌重塑 / 课程付费 / 出版书）是否发生？

---

## Grep 命令与命中数

| 命令 | 命中文件数 | 备注 |
|---|---|---|
| `grep -lE "I was\|I am\|former Olympic\|former Olympian\|decathlon\|Sweden\|Swedish\|my story\|my journey\|Health Champions\|Wellness for Life\|I decided\|I created\|I founded\|book\|I wrote"` | 23 / 100 | 23% 文件含 R1→R2 关键词 |
| `grep -nHE "...\|now I\|back then\|I used to\|I started\|I quit"`（同上文件） | ~80 行 | "I was" / "I started" / "I am" 高频 |
| `grep -lE "Wellness For Life\|Wellness for Life"` | 70+ / 100 | 品牌名贯穿 R2 |
| `grep -lE "Health Champions"` | 0 / 100 | **未出现** Health Champions 品牌 |
| `grep -lE "Sweden\|Swedish"` | 1 / 100 | 1 个烹饪视频（背景身份提及） + 1 个核心故事视频 |
| `grep -lE "former Olympic\|decathlon\|Olympics\|NCAA"` | 1 / 100 | 仅 20180406001.md 一手讲述 |
| `grep -lE "my story\|my journey\|my background"` | 0 / 100 | **未出现** |
| `grep -lE "I was sick\|my health crisis\|I was diagnosed"` | 0 / 100 | **未出现**自述健康危机 |
| `grep -lE "I wrote\|I published\|book"` | 0（self-authored book） / 100 | 推荐他人书，无自出版 |
| `grep -lE "course\|online course\|paid program\|tuition"` | 0 / 100 | **未出现**付费课程/出版书 |

---

## 8 大决策发现（R2 重点验证）

### 1. 瑞典 + 奥运 + NCAA 背景首次公开（一手）
**来源**：`20180406001.md` [00:00:42-01:15]（视频标题 *"Why I Make YouTube Videos - Dr Ekberg"*）
**他说的**：
> "I started out as an athlete I was a decathlete in the NCAA Div 1 and then I competed for Sweden in the Olympics in 1992 and finished ninth. And at the time I thought I was really really fit and really really healthy, but turns out I wasn't so healthy I was just fit. And later on in life I understood more about what health is after I had gone through chiropractic school and had some personal experiences."

**R1→R2 验证**：R1 完全无此背景。R2 是 Ekberg 第一次在视频中系统讲述"运动员→整脊师→内容创作者"的身份转换。
**信息类型**：**一手**（他自述）。

### 2. "Wellness For Life" 品牌名从无到全勤
**来源**：70+ 文件出现 "Dr. Ekberg with Wellness For Life"（intro/口头禅），首次 `20171027001.md`。
**演变**：
- 2017-10-09 / 10-16：`Hello I'm Dr. Ekberg`（无品牌）
- 2017-10-27 起：`Hey I'm Dr Sten Ekberg with Wellness For Life`
- 2018-02-19 起：`I am Dr. Ekberg with Wellness For Life`（语序固定化）
- 2018-06-06：`Wellness For Life Chiropractic in Cumming Georgia`（`20180606001.md:20`）—— 品牌与诊所地址绑定

**R1→R2 验证**：品牌 "Wellness For Life" 在 R2 期间定型为 intro 必备，但仅 R2 末段（6 月）才公开挂上"Chiropractic"实体。
**信息类型**：**一手**（intro 文本）+ **[我推断]** 品牌定型时间窗。

### 3. "Health Champions" 品牌 **未出现**（R2 仍未启用）
**来源**：0 个 R2 文件含 "Health Champions"。
**R1→R2 验证**：R1 没出现，R2 仍未出现。说明 "Health Champions" 品牌 **早于 2018-08-17 之后**才创立（待 R3+ 验证）。
**信息类型**：**[我推断]** 缺席证据。

### 4. YouTube 频道创建动机（一手公开决策）
**来源**：`20180406001.md` [00:01:15-03:00]
**他说的**（决策理由）：
- **杠杆问题**："I don't want to see dozens of people. I want to see thousands of people... I needed a way to leverage myself."
- **患者档案/图书馆**："with the YouTube channel I wanted to create an archive, a library, for my patients so that they could go in and watch. So whenever I had had a seminar I would record it and post it."
- **地理覆盖**："And then over time I realized that they would ask me, 'Well do you have a doctor that does what you do in Kentucky or California or New York State...'"
- **规模目标**："to help people... not just dozens face to face but tens of thousands and hundreds of thousands and millions"

**R1→R2 验证**：R2 是首次系统化讲述"为什么做 YouTube"——这是一次**公开的事业决策**。
**信息类型**：**一手**（他自述）。

### 5. "Doctor Of The Future Award"（2017-11-20）+ 妻子合作 + 诊所扩张
**来源**：`20171120004.md` + `20171120002.md`（同 video_id `KMgz7WkWllw`，应为切片重复）
**颁奖人描述**（二手）[00:00:42-01:39]：
> "the first award goes to Dr. Sten Ekberg is a former Olympic athlete our 2017 on a retreat he expressed the desire to is potentially expand his practice and he did he already has an associate that completed pro level training him and his wife started a YouTube channel posting video of [c]hiropractic tips healthy recipe has the [f]amily remedy and nutrition response testing in related videos his video have reached over 20 [thousand] up to 23,000 [views] is working with [the] doctor [unit] on a solution to handle neurological brain pathway with nutrition and chiropractic care he increases visit to a total of 150 week 50 which are nutritional last Monday's office hit their high [score] with 552 visit"

**他自述的（答谢）**[00:02:06-03:30]：
> "October was my first complete month in [the office] in about a year and a half... thank you for mentioning our YouTube we created that as a patient education tool we want to provide we want it to be a resource for our local community but also for the global community and I have to thank my better half my my secret weapon who spends more more time than I can imagine on on creating and editing these videos and promoting everything"

**R1→R2 验证**：
- 首次公开提到 **妻子** 是共同创办人（内容创作/编辑/推广）
- 首次公开提到 **诊所扩张**（associate 完成 pro level 培训，访问量 150/周，含 50 营养咨询，周一高峰 552 人次）
- 首次公开频道**已触达 23,000 观看**
- 2017 年 10 月是 Ekberg 回办公室的"第一个完整月"——**约 1.5 年没全职坐诊**（这暗示 2016 年中可能因伤病/转型离开全职临床）

**信息类型**：颁奖词 = **二手**（标准健康集团/营养反应测试机构颁奖人描述）；答谢 = **一手**（Ekberg 本人）。

### 6. 自述健康危机 **未出现**（R2 仍缺席）
**来源**：grep 0 命中（`I was sick` / `my story` / `my journey` / `I was diagnosed`）。
**仅有的"健康相关第一人称"**：
- `20180406001.md` 泛指 "personal experiences"（无具体疾病）
- `20180409001.md` 描述一个 patient case（他患者，不是他自己）
- `20180608001.md` 完全是患者 Carlos 的 testimony

**R1→R2 验证**：R2 仍未出现"我曾经生过 XX 病"的具体健康危机叙事。Ekberg 在 R2 的"自传"只到"我是前奥运选手+整脊师"为止，**没有"我曾经被误诊/我有桥本/我自闭症谱系..."这种康复叙事**。
**信息类型**：**[我推断]** 缺席证据 + 偶尔泛指。

### 7. 节目 intro 改版（公开的"小决策"）
**来源**：intro 文本演变（grep 结果）
| 阶段 | intro 格式 | 起始文件 |
|---|---|---|
| 阶段 1 | `Hello I'm Dr. Ekberg` | 20171009, 20171016 |
| 阶段 2 | `Hey I'm Dr Sten Ekberg with Wellness For Life` | 20171027 |
| 阶段 3 | `Hey I'm Dr. Ekberg with Wellness For Life and if you'd like to [truly] master health` | 20171109 之后定型 |
| 阶段 4 | `I am Dr. Ekberg with Wellness For Life`（语序变化） | 20180219 起 |

**R1→R2 验证**：R2 期间发生至少 3 次 intro 改版，每次都对应着"加品牌名 / 加 master health CTA / 改 'hey'→'I am' 语气"。**这是 R2 期间最显著的可观察决策**。
**信息类型**：**一手**（脚本文本）+ **[我推断]** 阶段划分。

### 8. 节目形式："holistic health / how the body really works" 主题定型
**来源**：`20180312001.md`（"What Is Holistic Health?"）+ 70+ intro 文本。
**关键定义**（一手）`20180312001.md:64-70`：
> "holistic health simply means that you address all of the person you address all of the factors that influence health... chemical side / physical mechanical side / emotional thinking side... every one of those is equally important"

**R1→R2 验证**：R2 中期（2018-03）Ekberg 公开把频道定位为"holistic health + body really works"赛道，并在 intro 中固化为"if you'd like to truly master health by understanding how the body really works"。这是 **节目定位的公开决策**。
**信息类型**：**一手**（定义来源） + **[我推断]** 定位定型时间。

---

## 决策维度总结（5 大公开决策）

1. **事业决策**（2017 中 - 2018 早期）：从全职诊所 → 频道 + 诊所双轨
   - 一手：`20180406001.md`（杠杆 / archive / 患者教育）
   - 二手：`20171120004.md`（颁奖人描述：2017 retreat 表达扩张欲望）
2. **品牌决策**：从"无品牌 intro" → "Wellness For Life" → 后期绑定 Cumming Georgia 实体
   - 一手：70+ intro 文本 + `20180606001.md`
3. **合作决策**：与妻子共同创办频道（妻子负责编辑/推广）
   - 一手：`20171120004.md` 答谢词
4. **节目定位决策**："holistic health + body really works" 主题
   - 一手：`20180312001.md`
5. **intro 改版决策**：3 次小改版（R2 期间最频繁的可观察决策）
   - 一手：intro 文本演变

---

## 未发现（8 分钟内未找到的预期信号）

- **"Health Champions"** 品牌：0 命中 → R2 仍未启用
- **自述健康危机 / "I was sick"** 叙事：0 命中 → Ekberg 在 R2 仍坚持"我是奥运选手/整脊师"的事实型自传，无康复/逆袭故事
- **付费课程 / 自出版书**：0 命中 → 商业模式 R2 仍依赖 YouTube + 诊所
- **节目大规模改版**（如加新主持人、加新场景）：R2 内未观察到
- **家庭背景**（父母/兄弟姐妹/童年）：0 命中 → R2 仍不公开
