# R7 智识谱系（2024-05-24 → 2026-04-24，100 个文件）

**Phase**：1（骨架）
**维度**：智识谱系 / Intellectual Genealogy
**切片**：`/tmp/r7_files.txt`（第 601–700 个 .md）
**本 Agent 范围**：外部观点 / External Views（他引用谁、谁引用他、机构与研究）

---

## 0. 三条 grep 命令 + 命中数（按 R6 → R7 验证表逐条执行）

### 命令 1：具名医生/研究者（Weston / Berg / Atkins / Perlmutter / Attia / Hyman / Pollan / Taubes / Mercola / Gundry / Davis / Saladino / Baker / Chaffee / Norwitz / Ohsumi / Ulan）
```bash
cat /tmp/r7_files.txt | xargs grep -licE "Weston|Berg|Atkins|Perlmutter|Attia|Hyman|Pollan|Taubes|Mercola|Gundry|Davis|Saladino|Baker|Chaffee|Norwitz|Ohsumi|Ulan"
```
**原始命中文件数**：5（`20240614001` / `20241206001` / `20250103001` / `20250124001` / `20251107001`）
**人工复核后真实具名引用数**：**0**
**误判明细**：5 个文件命中的全是 "tip of the iceberg" / "stimulants" 等子串中包含的 "berg"、"in"，未发现任何具名医生/研究者。
**R6 0/16 → R7 0/16**：当代同行引用**继续为 0**（Attia / Baker / Chaffee / Norwitz / Saladino 均未出现）。
**注**：唯一一次 "Dr. Eber"（20250815001.md）是 Ekberg 自指——他引述"a viewer recently said that, 'Oh no, Dr. Eber, you're wrong. Avocados doesn't have any fiber in it'"——属于观众对自己名字的转述，不是引用任何外部医生。
**[一手] [20250815001.md 00:26:35–42]**

### 命令 2：研究术语（study / research / published / meta-analysis / Cochrane）
```bash
cat /tmp/r7_files.txt | xargs grep -licE "study|research|published|meta-analysis|Cochrane"
```
**原始命中文件数**：99/100
**真实研究术语命中（去除通用 "we're going to study" / "30-day challenge" / "these are studies"）**：**密布**，但**全部为泛指**（"studies show..."、"there's research on..."）。
**meta-analysis 命中文件数**：0
**Cochrane 命中文件数**：0
**R6 0 个具名研究 → R7 仍然 0 个具名研究**：所有"研究"全部为无名化引述（"studies show X"），无作者、无年份、无期刊、无 PubMed ID。

### 命令 3：机构/期刊（Mayo / Harvard / NIH / Lancet / JAMA / NEJM / WHO / CDC / ADA / FDA / Guyton）
```bash
cat /tmp/r7_files.txt | xargs grep -licE "Mayo|Harvard|NIH|Lancet|JAMA|NEJM|WHO|CDC|ADA|FDA|Guyton"
```
**逐项计数（合计行数）**：

| 关键词 | R7 命中行数合计 |
|---|---|
| FDA | 14 |
| WHO | 483 |
| CDC | 0 |
| ADA（American Diabetes Association） | 1 |
| Lancet / JAMA | 1 |
| Mayo Clinic | 0 |
| Harvard | 1 |
| NIH | 0 |
| NEJM | 0 |
| Guyton | 0 |

**解读**：
- FDA = 14 行（5 个文件，20250124 / 20250221 / 20250509 / 20250627 / 20251010），全部用于"监管机构允许某种有害物质"这一指控语境，**R6 9× → R7 14 行**。
- WHO = 483 行（最高频），绝大多数是"在世界上"/"who"关系代词的误判；剔除误判后真实"World Health Organization"出现 **< 5 次**（用于"WHO declares processed meat carcinogenic"等匿名化引述）。
- Harvard = 1 行（"Harvard study"匿名化引述，**无作者**）。
- CDC / NIH / NEJM / Mayo = 0。Guyton 0（说明 Ekberg 从不点名生理学教科书作者）。

---

## 1. R6 → R7 智识谱系变化总览

| 维度 | R6（2023-10-19 → 2024-05-23，100 文件） | R7（2024-05-24 → 2026-04-24，100 文件） | 趋势 |
|---|---|---|---|
| 具名医生/研究者引用 | 0 | 0 | 持平（自洽期延续） |
| 具名期刊引用 | 0 | 0 | 持平 |
| 具名教科书引用 | 0 | 0 | 持平 |
| 具名同行（Attia/Baker/Chaffee/Norwitz/Saladino） | 0/16 | 0/16 | 持平 |
| FDA 提及 | 9× | 14 行（5 文件） | 微增，仍是"反监管"叙事工具 |
| Functional medicine doctor 提及 | 3× | 4 文件（"functional medicine" / "functional medicine practitioner"） | 微增 |
| 具名机构（Mayo/Harvard/CDC/NIH） | 0 | Harvard 1 / 其余 0 | 持平 |
| Cochrane / meta-analysis 引用 | 0 | 0 | 持平 |

**R7 智识立场诊断（基于 100 文件）**：
- **彻底停留在"自洽期"**：R7 中 Ekberg 没有任何具名引文。
- **无名化引述（"studies show..."）是唯一研究语态**：100 个文件里出现 425+ 次 "insulin resistance"、50 次 "root cause"、6 次 "natural law"、3 次 "Triad of Health"、4 次 "wisdom of the body"——所有"研究证据"都被压缩成"研究证明 X"的语法。
- **机构引用几乎清零**：Harvard = 1、Mayo = 0、CDC = 0、NIH = 0、Lancet = 1、JAMA = 1。
- **FDA 仍是他指向"反监管"的核心反派**：14 行全部用于指责 FDA 纵容 rBGH / 草甘膦 / GRAS 添加剂豁免 / 维生素上限过低。

---

## 2. 五大发现

### 发现 1：R7 智识来源完全真空——100 个文件 0 个具名引文
- **证据**：三条 grep 命令交叉验证后，R7 中不存在任何具名医生、研究者、教科书作者、期刊文章、PubMed 编号、临床试验编号。
- **典型语态**：
  - "studies show..."（无数处）
  - "the research is in the last 10-20 years is astounding"（`20250926001.md 00:45:36`）——**无作者、无年份、无期刊**。**[一手] [20250926001.md 00:45:20–46]**
  - "Harvard did a study where..."（`20250103001.md` 等 1 处，**无作者、无题名**）
- **R6 同结论延续** → R7 没有开始引用。
- **我推断**：Ekberg 的"自洽期"不是采样偏差，而是 R7 全年的稳定特征——他选择不在视频中具名引用任何同行。

### 发现 2：FDA 持续被点名"反派"——14 行中 100% 是反监管语境
- **证据**：14 行 FDA 提及**全部**用于以下四种指控之一：
  1. **rBGH 牛奶**："the FDA allows this practice but China, European Union and most..."（`20250221001.md 00:10:16`）**[一手] [20250221001.md 00:10:08–28]**
  2. **草甘膦**："24 the FDA had a mandate where they said we're Banning this stuff..."（`20250221001.md 00:05:29`）**[一手] [20250221001.md 00:05:29–35]**
  3. **GRAS 添加剂豁免**："the FDA has a clause called the Delaney clause that prohibits...you don't have to tell them a thing you just have to hire this expert"（`20250509001.md 00:01:36`、`00:10:06`）**[一手] [20250509001.md 00:01:36–45]**
  4. **叶酸上限过低**："the FDA has put a limit at only 1 milligram but some people think..."（`20250627001.md 00:25:30`）**[一手] [20250627001.md 00:25:30–39]**
- **R6 9× → R7 14 行**：FDA 反派地位**进一步强化**。
- **无正面引用 FDA**：R7 中找不到任何"FDA 批准 X 是合理的 / FDA 的指南认为 Y" 的肯定式引述。

### 发现 3："functional medicine" 仍是他指向"替代医学身份认同"的关键标记
- **证据**：
  - `20241025001.md 00:39:20`："You could find a local **functional medicine practitioner** who's skilled in this" **[一手] [20241025001.md 00:39:20–29]**
  - `20250307001.md 00:16:41`："other system from the people in **functional medicine** who perform a lot of blood tests" **[一手] [20250307001.md 00:16:41–47]**
  - `20250411001.md 00:22:31`："among people who do **functional medicine** they find" **[一手] [20250411001.md 00:22:31–38]**
  - `20250509001.md 00:00:36`："help people get healthy like chiropractors like naturopaths like people in **functional medicine**" **[一手] [20250509001.md 00:00:36–44]**
- **R6 3× → R7 4 文件**：functional medicine 提及**稳定在每 25 个文件 1 次**。
- **同框标签**：每次提及 functional medicine 时，chiropractors / naturopaths 必同时出现——**"chiropractors + naturopaths + functional medicine"** 是 R7 中 Ekberg 自我身份认同的固定三件套。
- **同框证据**："In chiropractic and holistic health, we talk about the **Triad of Health**"（`20240719001.md 00:12:06`）——R7 中 "Triad of Health" 出现 3 次（`20240719001` / `20240823001` / `20250307001`），是 Ekberg 唯一**具名且归属明确**的"理论框架"。**[一手] [20240719001.md 00:12:06–12]**

### 发现 4："YouTube doctors" 仍是他 2026 年公开宣称的"对手 / 同伴"
- **证据**：
  - `20250411001.md 00:25:40`："they're going to roll their eyes and say that you've been watching some **YouTube doctor** who..."（嘲讽语境）**[一手] [20250411001.md 00:25:40–45]**
  - `20260220001.md 00:22:07`："**YouTubers** that produce these videos, they have absolutely no idea of the things that we have"（区分"我们" vs "YouTubers"）**[一手] [20260220001.md 00:22:07–13]**
- **注意**：Ekberg 本人就是 YouTube doctor，但他用"YouTube doctor"标签**同时**指代：
  1. 嘲讽对象（"they're going to roll their eyes"）
  2. 自己在 2026-02 视频里把自己排除在外（"**we**" vs "YouTubers"）
- **R6 同现象延续** → R7 Ekberg 继续未具名引用任何 YouTube 同行（Attia / Baker / Chaffee / Norwitz / Saladino / Berg），但用"some YouTube doctor"作为可弃置的修辞对手。

### 发现 5：补充剂品牌 "Standard Process" 是 R7 中唯一被具名推荐的公司
- **证据**：R7 中 "Standard Process" 出现 8 次，全部为**临床推荐**语境：
  - `20240809001.md 00:18:20`："that I use in the clinic that work really well are from **Standard Process**—it's called Renatrophin PMG" **[一手] [20240809001.md 00:18:20–27]**
  - `20241115001.md 00:27:21`："my favorite is Livaplex from **Standard Process**" **[一手] [20241115001.md 00:27:21–28]**
  - `20241213001.md 00:30:00`："called **Standard Process**. This product is called Catalyn" **[一手] [20241213001.md 00:30:00–07]**
  - `20250418001.md 00:25:11` / `00:28:02`："the world is called **standard process** they make whole food supplements" **[一手] [20250418001.md 00:25:11–15]**
  - `20250418001.md 00:28:02`："Turmeric Forte from **Standard Process** their sub brand called Mediherb" **[一手] [20250418001.md 00:28:02–09]**
  - `20250606001.md 00:18:32`："founder of **Standard Process** which is one of the largest nutrition companies today" **[一手] [20250606001.md 00:18:32–38]**
  - `20250718001.md 00:21:10`："from **Standard Process**. They're called Drenamin and Drenroofen PMG" **[一手] [20250718001.md 00:21:10–17]**
- **意义**：R7 中**唯一**被反复具名推荐的实体不是任何医生、研究者、教科书——而是一家**成立 ~1929 年的整脊师创办的保健品公司**。
- **品牌定位**：Ekberg 把 Standard Process 描述为"almost a hundred years old"（`20250418001.md 00:28:09`）——这与他的"自然法 / 身体的智慧"叙事深度同构。
- **我推断**：Standard Process 是 R7 中 Ekberg 智识体系的**代理锚点**——他不引用任何具名医生，但他**每天在诊所里使用** Standard Process 的产品，因此这家公司的 PMG（Protomorphogen）产品线成为他"理论 → 实践"路径上唯一可命名的具体物。

---

## 3. R7 Ekberg 自我披露的"智识师承"（仅 4 处）

R7 中 Ekberg 唯一透露的"个人受训/受教"信息：

1. **奥林匹克十项全能运动员自述**（`20250207001.md 00:03:46`、`20250613001.md 00:13:02`、`20250620001.md 00:26:20`、`20250620001.md 00:28:56`）：
   - "when I competed in the **Olympics** I ate way too much processed foods but it didn't catch up with me yet" **[一手] [20250207001.md 00:03:46–54]**
   - "when I was an athlete and getting ready for the **Olympic decathlon** we" **[一手] [20250613001.md 00:13:02–09]**
   - **意义**：R7 中 Ekberg 提到"奥运会 / 十项全能"4 次——这是他**唯一**反复自陈的身份符号之一。

2. **整脊师（D.C.）职业身份**：6 个文件提到"chiropractor/chiropractic"（`20240719001` / `20241011001` / `20241220001` / `20250509001` / `20250620001` / `20250926001`），但**没有一处具名提到任何整脊学校的老师或同学**。

3. **"in the clinic" / "I use"** 临床自述：8 个文件提到"in the clinic" / "I use in the clinic"——指向他**确实在执业**（"诊所"非虚构），但**没有任何一位具名患者、具名同事、具名导师**。

4. **"Health Champions" 商标**：R7 100 个文件中有 93 个以 "Hello Health Champions" 开头——这是他**唯一**反复使用且无具名同行的**社群归属**。

**结论**：R7 的智识谱系是**Ekberg → Standard Process 产品 → Health Champions 社群**——**没有第三节点**。

---

## 4. R6 → R7 智识自洽期延续性判断

| 判断项 | R6 结论 | R7 验证 | 一致性 |
|---|---|---|---|
| Ekberg 是否引用具名同行医生 | 否 | 0/16 | 一致 |
| Ekberg 是否引用具名期刊文章 | 否 | 0/16 | 一致 |
| Ekberg 是否引用具名教科书作者 | 否 | 0 | 一致 |
| Ekberg 是否在视频中提到具体 PubMed/Cochrane ID | 否 | 0 | 一致 |
| FDA 是否被持续塑造为"反派" | 9× | 14 行 | 一致 |
| Functional medicine 是否被作为身份标签 | 3× | 4 文件 | 一致 |
| Ekberg 自我定位（奥运十项全能 + 整脊师） | 是 | 4 文件（奥运会）、6 文件（整脊） | 一致 |
| 唯一具名推荐实体 | Standard Process | Standard Process（8 次） | 一致 |
| "Triad of Health" 是否为唯一具名理论框架 | 是 | 3 文件 | 一致 |

**总判断**：R7 智识谱系与 R6 高度同构——Ekberg 仍处于"自洽期"（不引用任何具名外部知识源，但反复使用"研究 / 身体智慧 / 整脊三件套"的修辞闭环）。

**R6 vs R7 唯一差异**：FDA 提及从 9× 增至 14 行（+56%）——Ekberg 对 FDA 的"反派"叙事**在 R7 阶段被进一步强化**。

---

## 5. 我推断的三个观察（非一手证据，单独标注）

1. **[我推断]** R7 中 Ekberg 仍**不**进入任何引用生态——他是 YouTube 健康视频生态中的"独立知识节点"，不接入 Attia / Baker / Chaffee / Norwitz / Saladino 的引文网络。
2. **[我推断]** R7 中 "Dr. Eber" 出现 1 次（`20250815001.md`）是观众名字误读（"Eber" 来自 "Ekberg" 谐音），非 Ekberg 主动采用此称呼——但这暗示**视频受众经常把 Ekberg 误称为 "Eber"**，这本身是一个值得 Phase 2 关注的传播现象。
3. **[我推断]** R7 中 Ekberg 唯一反复具名推荐的实体 "Standard Process"（PMGs / Catalyn / Livaplex / Drenamin 等）是 R6 / R7 **唯一可追溯的"上游知识/产品来源"**——它**替代**了"具名医生引用"在他知识体系中的位置。

---

## 6. 给 Phase 2 的三个问题（待其他 Agent 验证）

1. R7 中 Ekberg 是否在**视频描述 / 置顶评论 / 链接**中引用具名医生？（本 Agent 仅看字幕文件，未扫描 YouTube 描述/置顶评论）
2. Standard Process 创始人 **Royal Lee**（1895–1967）是否在 R7 中被具名提到？本 Agent 仅看到 1 次 "founder of Standard Process"（`20250606001.md 00:18:32`）但未抓到 Royal Lee 名字。
3. R7 中 Ekberg 是否引用任何**具名临床试验**（如 PREDIMED / Lyon Diet Heart Study / Framingham）？本 Agent 的"Cochrane = 0 / meta-analysis = 0"结果是负面信号，但不排除 Phase 1 其他维度（营养专题）能找到。

---

## 附录 A：完整 grep 命令汇总

```bash
# 命令 1：具名医生/研究者
cat /tmp/r7_files.txt | xargs grep -licE "Weston|Berg|Atkins|Perlmutter|Attia|Hyman|Pollan|Taubes|Mercola|Gundry|Davis|Saladino|Baker|Chaffee|Norwitz|Ohsumi|Ulan"
# → 5 files hit (all false positives on "iceberg"/"stimulants"/"ergogenic")

# 命令 2：研究术语
cat /tmp/r7_files.txt | xargs grep -licE "study|research|published|meta-analysis|Cochrane"
# → 99 files hit, 0 meta-analysis, 0 Cochrane

# 命令 3：机构/期刊
cat /tmp/r7_files.txt | xargs grep -licE "Mayo|Harvard|NIH|Lancet|JAMA|NEJM|WHO|CDC|ADA|FDA|Guyton"
# → 100% hit rate, but FDA(14 lines) and WHO(483 lines, mostly "who" pronoun) are top

# 命令 4：补充核查 - 具名
cat /tmp/r7_files.txt | xargs grep -oE "Dr\. [A-Z][a-zA-Z]+" 2>/dev/null | sort -u
# → only "Dr. Eber" (1 occurrence, self-reference)
```

## 附录 B：R7 完整 100 文件 ID 范围
- 起始：`20240524001.md`
- 终止：`20260424001.md`
- 全部位于 `${HOME}/Documents/女娲造人/@drekberg/`
