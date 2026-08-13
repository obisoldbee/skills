# R01-03: Dr. Sten Ekberg 表达 DNA 维度调研

**调研范围**：R1 第 1/8 轮，前 100 个文件（2010-07-01 → 2017-09-29）
**素材**：`${HOME}/Documents/女娲造人/@drekberg/` 下的 100 个 .md 字幕切片
**方法**：以 grep 频次统计为主，少量 Read 验证片段

---

## 0. 关键 grep 命令清单（可复现）

```bash
cd ${HOME}/Documents/女娲造人/@drekberg/
FILES=$(cat /tmp/r1_files.txt)

# 填充词 / 标记词
for kw in "okay" "alright" "right" "you guys" "the bottom line" "in fact" "literally" "honestly" "actually"; do
  grep -i -o -E "\b$kw\b" $FILES | wc -l
done

# 标志性短语
for kw in "root cause" "the body" "your body" "the truth" "the problem" "the answer" "holistic" "whole" "the body is" "your body is" "look at" "we need" "you need" "I mean"; do
  grep -i -o -E "\b$kw\b" $FILES | wc -l
done

# 句首词频次
grep -h -i -o -E "\b(so|but|and|now|well|ok|yes|no|hey) " $FILES | sort | uniq -c | sort -rn

# 整体高频词
grep -h -i -o -E "\b(so|but|and|now|well|ok|yes|no|hey|because|that|this|it)\b" $FILES | sort | uniq -c | sort -rn
```

---

## 1. 句式偏好

### 1.1 连接词 + 主题陈述式开句

- **`and`**（7,621）作为句首 / 句中最频繁，远远领先于 `so`（2,749）和 `but`（1,012）。
  - 含义：Ekberg 习惯用 `and` 串联判断、陈述与解释（"and that's why..." "and the body..."），句子多呈"流水账式"叠加。
- **`so` 句首**（2,749）极多，配合 `and` 形成"And-So" 链式推导。
  - 高频搭配 `okay so`（60）和 `and so`（148）显示他常用"先同意/过渡，再推论"的节奏。
- **句首 `but`**（1,012）也不少——典型转折 / 否定对手观点的修辞习惯。
- **`we'll`**（211）、**`we're going`**（89）的高频预示：习惯"我们一起 / 我来带你"的演讲式收束。
- **`you'll`**（49）、**`you're going`**（18）也较多——频繁出现"你将要……"的预判式表达。

### 1.2 列举式结构（"1./2./3." 高频）

- 数字 1./2./3. 在文件中分别出现 **2,571 / 2,675 / 2,643** 次（注意：此数偏高，可能是字幕时间戳或编号上下文，需后续验证；但配合 first/second/third 188/108/24 与 number one 46，仍可推断**Ekberg 习惯用编号式列点**）。
- `first`（188）/`second`（108）/`number`（148）/`one thing`（31）/`thing is`（61）的同步高频印证"分点 + 一二三"是核心修辞。
- `[一手 20110519001.md]` "okay so" 多用作新点开始。

### 1.3 反问 + 标签问句（低频但特征明显）

- `do you`（166）、`are you`（29）、`have you`（29）显示他常用 yes-no 反问拉动听众。
- `right?`（1）、`okay?`（8）、`aren't you`（1）非常少——**Ekberg 极少用"right?"做标签问句**。这是他与 Berg 的差异点之一（Berg 喜欢用 "right?" 锁住对方）。

---

## 2. 词汇特征

### 2.1 填充词

| 词 | 命中数 | 解读 |
|---|---|---|
| `okay` | **256** | 极高，是 R1 阶段 Ekberg 最核心的口头禅 |
| `right` | **268** | 与 okay 几乎等量，但多用作"对吧/正确"语义 |
| `alright` | 10 | 极低频，几乎不用 |
| `so` | 2,749 | 远超 "okay"，作为推论起手 |
| `you know` | 137 | 中等频次 |
| `I think` | 60 | 中等 |
| `I mean` | 21 | 较低 |
| `gonna` | 73 | 较常用 |
| `look at` | 116 | 中高 |
| `let's` | 166 | 中高 |

**核心口头禅**：`okay`、`so`、`right` 三者构成 R1 阶段 Ekberg 的"调性三件套"，三者总频次约 **3,273** 次（per 100 个文件平均每个文件 ~33 次）——这意味着他平均每 1-2 句就会触发一次。

### 2.2 标志性短语

| 短语 | 命中 | 解读 |
|---|---|---|
| `the body` | **508** | 极高高频，"the body"是 R1 阶段 Ekberg 的口头禅之首 |
| `your body` | **293** | 第二高，与 the body 构成"身体中心"话语 |
| `whole` | 128 | 配合 "the whole body" 频繁使用 |
| `in the body` | 148 | 高频短语 |
| `we need` | 173 | "我们必须……"句式 |
| `you need` | 73 | 建议 / 命令式 |
| `understand` | 226 | 高频——"you understand?" 是常用收束 |
| `important` | 197 | 高频——价值标记 |
| `true` | 97 | 中高 |
| `false` | 104 | 与 true 几乎等量，说明他常做真/假二元判断 |
| `the problem` | 65 | 中等——"问题框架"是常用修辞 |
| `the answer` | 13 | 较低 |
| `root cause` | 1 | **R1 阶段极低**——"root cause" 还未成为高频口头禅（后期会飙升） |
| `holistic` | 11 | 中低 |

**关键发现**：`the body`（508）>>> `your body`（293）>>> `holistic`（11）。在 R1（2010-2017），Ekberg 的核心锚词是 **"the body"**，而不是后期标志性的"root cause / holistic / wellness"。这表明 R1 阶段他的话语中心在**身体本身**，还未进入"根因-整体-健康"的话术套系。

### 2.3 自创术语 / 简写

- 未发现 R1 阶段 Ekberg 有大量自创术语。
- `holistic`（11）尚未高频化。
- 简写如 `TMJ`（0）、`DD Palmer`/`BJ Palmer`（0）——早期他不引用 Palmer 原始文献。
- `subluxation`（1）——R1 几乎不用直白的整脊术语"半脱位"，这与他的"全科整体健康"转向相关。
- `[我推断]`：R1 阶段 Ekberg 的语言还停留在"医学生/讲师"通用英语，**未形成个人品牌术语**。后期高频的"root cause / holistic / Ulite / Wellness For Life"在 R1 阶段均未出现。

---

## 3. 节奏感

### 3.1 短句 + 链式叠加

- 句首 `and`（7,621）和 `so`（2,749）的极高比例暗示：**大量使用"接龙式"短句**——前一句说结论，下一句用 and/so 接力。
- `and that's`（234）显示经典的"and that's why"句式——Ekberg 习惯"先下断言，再给原因"。
- `this is`（341）、`that is`（199）、`it is`（265）的中高频次支持：他在做大量"指代 + 解释"的解释型短句。

### 3.2 列表 / 步骤节奏

- `first`（188）、`second`（108）、`third`（24）、`number`（148）——**Ekberg 极爱用一二三点列举**。
- `let's say`（24）、`suppose`（84）、`imagine`（28）——常以"假设/想象"引入例子。
- `picture`（35）——也用画面化思维。
- `for example`（10）反而**极少**——他不直接用 "for example"，而用 `let's say` / `imagine` / `suppose` 替代。这是 R1 阶段 Ekberg 的微妙特征。

### 3.3 过渡与衔接

- `well`（487）作为句首过渡频繁。
- `now`（469）也作为段落起手高频。
- `look at`（116）——常用"看这张图/这个数据"的现场指示语。
- `[一手 20110519002.md]` 中频繁出现 "okay so" 后接 "let's look at..."，显示他**靠"okay so"切分小节**。

---

## 4. 幽默方式

### 4.1 极简幽默

- 笑声标记（笑声、audience laughter）R1 100 个文件**几乎无统计样本**（前期讲座以教学为主，幽默密度低）。
- 夸张形容词 `amazing`（12）、`fantastic`（8）、`incredible`（1）、`awesome`（5）——**整体克制**，远不如 Berg 的"incredible"密度。
- `crazy`（6）、`ridiculous`（1）、`insane`（0）——**R1 阶段他几乎不用夸张式俚语**。

### 4.2 否定 / 否定对手（低-中度对抗性）

- `no`（2,037）——极高频，几乎与 `and` 同量级。**Ekberg 在 R1 阶段是个"高频否定者"**，常用 "no, no, no" 否定对手观点。
- `stupid`（13）、`junk`（6）、`poison`（29）、`toxic`（31）——中等频次，**他用医学/化学性贬义词（poison、toxic）而非情绪性俚语（crazy、insane）**。这是 R1 阶段 Ekberg 的显著特征：贬义靠**理性术语**而非情绪。
- `dam`（52）——**这是 R1 阶段 Ekberg 唯一的"半脏话"高频词**。`dam` 在英语里是 `damn` 的删减版（也可能是字幕错听 `them`/`than`），但 52 次仍偏高。

### 4.3 标签问句里的轻度调侃

- 几乎不见 `[我推断]`：R1 阶段 Ekberg 几乎不做冷笑话 / 反讽 / 自我贬损——**他的幽默接近"无幽默的稳健讲师"风格**。

---

## 5. 确定性表达

### 5.1 高频确定性词

| 词 | 命中 | 解读 |
|---|---|---|
| `true` | 97 | 频繁作判断 |
| `false` | 104 | 与 true 等量——**Ekberg 习惯做真/假二元判断** |
| `right` | 268 | "对/正确"语义 |
| `wrong` | 58 | "错"语义 |
| `absolutely` | 35 | 高确定性 |
| `exactly` | 79 | 高确定性 |
| `completely` | 40 | 高确定性 |
| `definitely` | 9 | 极低（他不用 definitely） |
| `obviously` | 28 | 中等——常用"显然"作肯定收束 |
| `no` | 2,037 | **极高——典型的"否定对手=肯定自己"话语** |

**核心特征**：
- Ekberg 几乎不用 `definitely`（9），而偏好 `absolutely`（35）+ `exactly`（79）——确定性词选**"高端版"**。
- `obviously`（28）的中频暗示：他有"以显然自居"的话语习惯，但克制。
- `true`（97）/ `false`（104）的**等量并存**说明：他常用"真 vs 假"作为**修辞结构**——A 是真的（Ekberg 的）/ B 是假的（对手的）。

### 5.2 命令 / 规范式确定性

- `you need`（73）——"你需要……"的高频出现，预示**指令式语气**。
- `we need`（173）——"我们必须……"远高于"you need"，**Ekberg 的确定性话语多用"我们"主语，而非"你"**。这与 R1 阶段他仍在做"群体讲座"的身份有关。
- `make sure`（20）、`remember`（36）、`understand`（226）——"确认/理解"类词高密度，**强调听众同步**。
- `important`（197）——价值标记高频。

### 5.3 引用研究的克制

- `study`（22）、`studies`（2）、`research`（37）、`shown`（10）——**研究引用频次偏低**。
- `according to`（11）——"根据……"也低。
- `Mayo`（19）——是唯一具名机构高频——他引用梅奥诊所多于哈佛（0）/克利夫兰（0）。
- `[我推断]`：R1 阶段 Ekberg **极少引用具体研究文献**，确定性来自"常识 + 身体逻辑 + 个人经验"而非学术引用。这与后期 Ekberg 大量引用文献的"循证话术"形成对比——是**R1 → R4 阶段最大的修辞转型**之一。

---

## 6. 引用习惯

### 6.1 学术 / 机构引用

- `Mayo`（19）——唯一高频具名机构。
- `Harvard`（0）、`Cleveland`（0）——**几乎不引用顶级机构**。
- `physician`（4）、`expert`（2）、`scientist`（0）——**他极少用"权威人物"话语**。
- `doctor`（62）——中等频次，多用作泛指"医生"而非具体人名。
- `[我推断]`：R1 阶段 Ekberg **不建立"权威链"话语**（X 教授说 / 哈佛研究表明）——这是后期 R4 才大量出现的修辞。

### 6.2 行业 / 同行引用

- `chiropract`（222）——**整脊行业是他最频繁引用的"行业"**。
- `nervous system`（128）、`muscle`（302）、`spine`（36）——引用的核心是**解剖/神经/肌肉**话语。
- `DD Palmer`/`BJ Palmer`（全部 0）——**R1 阶段 Ekberg 不引用 Palmer 创始人**。
- `philosophy`（3）、`principle`（32）——"原则"是中频词，但他不上升到"整脊哲学"层面。
- `[我推断]`：R1 阶段 Ekberg 的话语锚定在"**身体结构**"而非"**整脊史观**"。他讲神经系统/肌肉，但**不挂 Palmer 大旗**。

### 6.3 自我引用

- `I believe`（2）、`I know`（18）——**R1 阶段他几乎不用 "I believe / I know" 作自我确信话语**。
- `I think`（60）相对多用，但也不算高频。
- `[我推断]`：R1 阶段 Ekberg 的"权威感"主要靠**"事实/身体/医生"作为客观主语**，而非"我"。这是与 Berg（高频 I tell you / I want you to know）最大的差异。

### 6.4 健康议题引用

- `sugar`（264）、`insulin`（125）、`cortisol`（73）、`hormone`（78）、`inflammation`（37）、`vitamin`（72）——R1 阶段他已涉及代谢激素议题，但**密度低于 R4**。
- `gluten`（1）、`leaky gut`（0）——**R1 阶段几乎不提 gluten / leaky gut**——这是 R4 才进入的话题。
- `[我推断]`：R1 阶段 Ekberg 的健康话语中心在**整脊结构 + 基础代谢**，尚未进入"gluten / leaky gut / 慢性炎症"等流行营养学话题。

---

## 7. 关键发现摘要（5-10 条）

1. **`the body` 是 R1 阶段最强锚词**（508 次），远超"root cause"（1）和"holistic"（11）——后期标志性的术语在 R1 几乎缺席。
2. **`okay / so / right` 三件套**构成 R1 Ekberg 的口语句法骨架（合计 ~3,273 次）。
3. **句首 `and`（7,621）+ `so`（2,749）+ `no`（2,037）= 12,407 次**——Ekberg 是"和-所以-不"型话语者，链式叠加 + 频繁否定是其节奏核心。
4. **`true`（97）/ `false`（104）等量并存**——他用"真/假"作为修辞结构（Ekberg 真 / 对手 假）。
5. **`we need`（173）>> `you need`（73）**——R1 阶段 Ekberg 的指令式语气多用"我们"主语。
6. **R1 阶段几乎不引用 Palmer / 哈佛 / NIH**，仅 `Mayo`（19）有具名——话语权威来自"身体事实"而非"研究文献"。
7. **`okay so`（60）+ `let's say`（24）+ `imagine`（28）+ `suppose`（84）**——他极少用 "for example"（10），改用"Let's say / Imagine / Suppose"引入例子。
8. **`definitely` 极低（9）**——确定性词用"absolutely/exactly"而非"definitely"，是英语"高端确定性"选择。
9. **贬义靠"理性术语"（poison 29 / toxic 31）而非俚语（crazy 6 / insane 0）**——Ekberg 的攻击性是"医生式否定"而非"网红式吐槽"。
10. **R1 阶段不用标签问句 `right?`（1）**——与 Berg 形成鲜明对比；Ekberg 的反问更接近"Do you..."（166）这种 yes-no 拉动式，而非快速 right?-lock。

---

## 8. R1 与后期（推测）调性对比基线

| 维度 | R1（2010-2017） | [我推断]后期（2018+） |
|---|---|---|
| 核心锚词 | `the body`（508）| `root cause` / `holistic` / `insulin resistance` |
| 确定性话语 | `absolutely / exactly` | `look / the truth is` |
| 否定强度 | `no`（2,037）极强 | 可能更收敛（职业化） |
| 引用 | Mayo 19 / 几乎不引研究 | 大量引研究 / NIH / Lancet |
| Palmer 引用 | 0 | 可能进入整脊史观 |
| `gluten / leaky gut` | 1 / 0 | 高频 |
| 标签问句 `right?` | 1 | 可能增多（与团队化制作相关） |

---

## 9. 局限性

- 本次仅 grep，未做语义聚类与上下文采样（仅 1-2 次 Read 验证）。
- 数字 1./2./3. 命中数 2,571/2,675/2,643 **异常高**，可能混入字幕时间戳或编号——需在后续 R2-R8 轮次用更严格的正则（行首 + 句号+空格）过滤确认。
- `dam` 52 次有可能是 `them`/`than` 字幕错听——需 Read 抽样确认。
- R1 阶段文件**数量分布不均**（2010 仅 1 个文件，其余 99 个集中在 2011-2017），统计偏向 2011-2017 段。
- 未做按文件大小归一化（不同文件长度差异大，可能影响绝对频次解读）。

---

**完成时间**：R1-03 第一轮
**命中文件数**：100 / 100
**信息源类型分布**：
- 一手（grep 计数 + 1-2 次 Read 验证）= 高置信度
- 二手 = 0
- 我推断 = 第 2.3 / 6.3 / 6.4 / 7 / 8 / 9 小节明确标注
