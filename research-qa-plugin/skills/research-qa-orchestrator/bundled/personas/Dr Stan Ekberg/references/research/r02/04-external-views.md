# R2 智识谱系 — Dr. Sten Ekberg 调研笔记（2017-10-02 → 2018-08-17）

**调研者**：fuxi-skill Phase 1 Agent 4（智识谱系）
**素材范围**：R2 第 101-200 个 .md 文件（共 100 个）
**日期跨度**：2017-10-02 → 2018-08-17

---

## 1. 主要 grep 命令 + 命中数

| grep 命令 | 命中文件数 | 命中行数 |
|---|---|---|
| `weston\|perlmutter\|blackburn\|mercola\|grain brain\|atkins\|banting\|hyman\|attia\|pollan\|campbell\|taubes\|esselstyn\|gundry\|davis\|wahls\|brod\|buckner\|sinatra` | 6 / 100 | 9 |
| `harvard\|mayo\|cleveland\|nih\|lancet\|jama\|nejm` | 1 / 100 | 1 (Mayonnaise 假阳性) |
| `study\|research\|published\|journal\|meta-analysis\|randomized` | 27 / 100 | 73 |
| `usda\|food pyramid\|food guide\|government\|cdc\|fda` | 2 / 100 | 2 |
| `keto\|ketogenic\|atkins` | 9 / 100 | 约 25+ |
| `evolution\|paleo\|ancestor\|caveman\|primitive\|wild` | 13 / 100 | 20+ |
| `wheat\|grain\|gluten\|seed oil\|vegetable oil\|soy` | 14 / 100 | 25+ |
| `autophagy\|nobel\|ohsumi\|2016` | 3 / 100 | 5 |
| `doctor mike\|sam robbins\|reacts to` | 3 / 100 | 6 |
| `american diabetes\|american heart` | 1 / 100 | 1 |

---

## 2. 关键发现（5-10 条）

### 发现 1：R1 智识三件套（Perlmutter + Blackburn + mercola.com）在 R2 完全消失
- grep 命中数：**0**（Perlmutter、Blackburn、mercola.com 全部未出现）
- Atkins / Banting / Taubes / Pollan / Campbell / Hyman / Attia / Esselstyn / Gundry / Wahls / Brod / Buckner：**0** 命中
- **[我推断]** R2 期间 Ekberg 还在建立自己的内容库，未开始大量引用其他低碳/原始饮食作者。他给出的引用集中在"反 Keys 七国研究 + Bowden/Sinatra + Davis/Undoctored"三本书。
- [一手] 20180604001.md 03:28「The Great Cholesterol Myth by Jonny Bowden and Stephen Sinatra」

### 发现 2：Ekberg 唯一正式引用的两本书都是"反胆固醇恐惧"路线
- **The Great Cholesterol Myth** by Jonny Bowden & Stephen Sinatra
- **Undoctored** by William Davis（前作 Wheat Belly 作者，前心内科 20+ 年）
- 引用语境：把 Davis 当作"内部人士揭发医学界"案例 — Davis 在书里说"37/38 阳性抗抑郁药试验发表，36 个阴性试验中 33 个被压下"。
- [一手] 20180604001.md 03:28 / 04:10
- **[我推断]** 这是 R2 期间 Ekberg "权威推荐"的最大牌面，远不及 Berg 那种密集引用 Baker/Norwitz/Chaffee 的网络。

### 发现 3：Ekberg 在 R2 直接攻击 Ancel Keys 七国研究
- 这是 R2 智识谱系最重要的"反主流科学"动作。
- 原话：「Ancel Keys just cherry picked the countries that suited his opinion and when people went back later and looked at all 22 countries there was no correlation whatsoever」
- 关键数据点：**22 个国家中只挑 7 个**；瑞士和荷兰脂肪摄入比芬兰多、心脏病只有芬兰的 1/3
- [一手] 20180604001.md 01:01 → 02:07
- **[我推断]** 这是他从 Taubes《Good Calories, Bad Calories》继承的"反 Keys"经典叙事，但他在 R2 没有引用 Taubes 本人。

### 发现 4：R2 出现"Real Doctor Reacts To..."系列（重大内容策略转向）
- 2018-06-18 「Real Doctor Reacts To Doctor Mike on Diets: Ketogenic Diet」
- 2018-06-22 「Real Doctor Reacts To Dr. Sam Robbins Intermittent Fasting: Weight Loss, Get Fat & Get Diabetes」
- 2018-08-13 「Real Doctor Reacts To The Mathematics Of Weight Loss Ruben Meerman TEDxQUT」
- 三个反应视频集中出现在 6-8 月
- [一手] 20180618001.md / 20180622001.md / 20180813001.md
- **[我推断]** 这标志 Ekberg 从"自我输出"转向"蹭同行流量"的反应类内容模式。R1 不存在这一类（需验证 R1 报告）。他的攻击对象全是比他流量大的医生。

### 发现 5：Ekberg 提出"研究可信度 90/10 规则"
- 原话：「90% of research is going to be published if it's favorable to whoever paid for the study and 10% is gonna be published if it's not favorable」
- 同 20180604001 引用 Davis 的数据：抗抑郁药 37/38 vs 3/36 阴性发表率
- 攻击对象：「pharmaceutical companies and processed food industries」是 medical organizations 和 government agencies 的主要资助者
- [一手] 20180618001.md 11:03 / 20180604001.md 04:35
- **[我推断]** 这是 R2 最强反建制立场 — 把整个科研发表体系定性为系统性偏倚。R1 报告需对照是否有同样表述。

### 发现 6：R2 唯一被引用的"科研权威奖项"是 2016 年诺贝尔生理学/医学奖（Yoshinori Ohsumi，自噬）
- 原话：「there was a Nobel price in 2016 awarded to a person who proved the mechanics of autophagy」
- 用法：用来背书 keto + IF → autophagy → cancer preventing + anti aging
- 注意：他发音是"Nobel price"（错读，"prize"才对）
- [一手] 20180618001.md 04:14 / 20180622001.md 06:21
- **[我推断]** Ekberg 把诺奖当作"前沿科学背书"，但对获奖者（Ohsumi）本人、其原始论文、他引都不做引用 — 只是把诺奖权威符号化。

### 发现 7：R2 反建制机构清单 — 极简且靶向
- 直接被攻击的机构/概念：
  - **American Diabetes Association** —「following the guidelines of the American Diabetes Association will give you diabetes」（20171204001 开头 hook）
  - **Food Pyramid 制定者** —「guidelines have been put together by the same people who promote the food pyramid」（20180413001.md 06:45）
  - **Standard American Diet** —「3 400 grams of carbs per day」
  - **3.2 trillion 美元医疗系统**（20180618001 07:35）
- [一手] 20171204001.md 00:00 / 20180413001.md 06:45 / 20180618001.md 07:35
- **[我推断]** R2 没有提到任何具体主流机构名（Mayo/Harvard/Cleveland/NIH/Lancet/JAMA/NEJM 全部 0 命中；Mayo 命中是食谱里的"mayonnaise"假阳性）。他攻击的是"抽象的医学指南制定者" + ADA 这种疾病协会 + "药企+加工食品"组合，没有具体到 JAMA 文章或 NIH 资助。

### 发现 8：R2 没有 Weston A. Price / Price-Pottenger / 原始饮食学派引用
- grep 命中：0
- [我推断] 与 Berg 强烈依赖 Price-Pottenger 营养学形成鲜明对比。Ekberg 在 R2 的"祖先/历史"论证完全靠自己口头说（"humans have done this for since we've been around"、"nothing in grocery store existed 10,000 years ago"），不引用任何人类学/营养人类学权威。

### 发现 9：R2 出现"1850 年"这一关键时间锚点
- 原话：「this has been established since 1850 even before we knew what insulin was or how insulin works」
- 上下文：讲低碳水饮食/胰岛素抵抗的关系在 1850 年已被认识
- [一手] 20171204001.md 01:34
- **[我推断]** Ekberg 暗示"低碳水能治糖尿病"这件事 170 年前就知道，但现代医学/营养学假装不知道。这是 R2 的"被压制的历史真相"叙事核心。

### 发现 10：R2 没有出现任何"反 USDA / 反 Food Pyramid"长篇系统论证
- 只有 20180413001.md 06:45 一句"guidelines have been put together by the same people who promote the food pyramid"
- **[我推断]** 与 Berg 那种系统化反 USDA Food Pyramid 路线不同，Ekberg 在 R2 把"反主流指南"压缩成了一句口头评论，没有展开成专题视频。

---

## 3. R1 → R2 对照验证总结

| 验证项 | R1 状态 | R2 状态 | 变化 |
|---|---|---|---|
| Perlmutter / Grain Brain | 引用 | **0 命中** | 消失 |
| Blackburn | 引用 | **0 命中** | 消失 |
| mercola.com | 引用 | **0 命中** | 消失 |
| Weston A. Price | 0 | 0 | 维持空白 |
| Atkins / Taubes / Hyman / Attia | 0 | 0 | 维持空白 |
| 反 USDA Food Pyramid | 有 | **仅 1 句**（20180413001） | 退化为附带评论 |
| 反医学教材 | 有 | 升级为"反研究发表体系"（90/10 规则） | 升级 |
| 引用的具体医生/书 | Perlmutter/Blackburn | **Bowden/Sinatra + Davis** | 全部换人 |

**[我推断]** R2 期间 Ekberg 处于"内容品牌建立期"，智识引用体系是**松散且未成型**的 — 偶尔引一两个对胃口的反主流医生，没有像 R1 那样稳定引用 Perlmutter+Blackburn 的双核 + mercola.com 作为信息源。

---

## 4. R2 智识谱系画像（一句话）

> R2 期间 Ekberg 智识谱系 = "反 Keys 七国研究 + 反 ADA 指南 + 反制药/食品工业资助研究 + 引 Davis/Bowden/Sinatra + 用 Ohsumi 诺奖背书 autophagy"，**没有任何人类学/营养学/进化医学的引用骨架**，**对同期 YouTube 同行的引用为零**（直到 2018-06 才出现"Real Doctor Reacts"系列反应视频）。
