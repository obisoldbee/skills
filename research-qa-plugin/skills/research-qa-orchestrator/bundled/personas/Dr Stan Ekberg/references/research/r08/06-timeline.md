# R8 时间线（2026-05-08 → 2026-05-29，4 个文件）

> Phase 1 Agent 6 — 时间线维度
> 切片文件：`/tmp/r8_files.txt` → 4 个 .md
> 工作目录：`${HOME}/Documents/女娲造人/@drekberg/`

---

## 一、扫描命令与命中数（4 步扫描）

| 步骤 | grep 命令 | 命中文件数 |
|---|---|---|
| 1 | `xargs grep -licE "Uveia\|euLyte\|Ulite\|UmethylB\|Euvexia\|Nexus\|Survival Biology\|Health Champions\|Wellness For Life"` | 4/4（仅 `Health Champions` 招呼语 ×4 + `Ulite` ×3）|
| 2 | `xargs grep -licE "former Olympic\|decathlete\|Sweden\|Swedish"` | 0/4（exit 1）|
| 3 | `xargs grep -licE "carnivore\|animal-based\|beef salt water\|FMD\|fasting-mimicking\|extended fasting"` | 0/4（exit 1）|
| 4 | `xargs grep -licE "Ozempic\|Wegovy\|GLP-1\|semaglutide\|tirzepatide\|Mounjaro"` | 0/4（exit 1）|

补扫：
- 品牌单查 `Uveia|euLyte|Euvexia|Nexus`：0/4（exit 1）
- `UmethylB` 单查：0/4（exit 1）
- `book|publish|writing a book|coming out|pre.?order`：0 实质命中（只有 metadata 里的 `published_date`）

---

## 二、4 个文件（视频）一栏

| 切片 # | 发布日 | video_id | 标题（直接来自 frontmatter `title`） |
|---|---|---|---|
| 701 | 2026-05-08 | C7CKRkAIs3A | #1 Absolute Best Way To Prevent Colon Cancer |
| 702 | 2026-05-15 | xivHL3Eo4oc | Why Belly Fat Changes After 50 |
| 703 | 2026-05-22 | m65Aq4H-oic | You Cannot Heal Your THYROID If You Do These 10 Things Daily |
| 704 | 2026-05-29 | pLKMkkMt5P0 | I Ate Nothing But Sardines For 5 Days and Here's What Happened |

节奏：每 7 天一更（R8 与 R7 一致）。3 周（05-08 → 05-29）。

---

## 三、核心发现（5-10 条）

### 1. R8 **没有新品牌发布** — UmethylB / Uveia / euLyte / Euvexia / Nexus 全部 0 命中

R7 末段（2026-04-10）首次出现 `UmethylB` 命名。R8 这 4 期（05-08 / 05-15 / 05-22 / 05-29）严格 grep `UmethylB|umethylB` **0 命中**。
其他 R7 已存在品牌（`Uveia|euLyte|Euvexia|Nexus`）也是 0 命中。

`Ulite` 在 R8 出现 **3 次**，全部集中在 5-29 一期（`20260529001.md`）：
- L37 `[00:01:51]` "three scoops a day of my own brand of electrolytes called **Ulite**"
- L210 `[00:22:45]` "how the electrolyte, the **ulite** helped in my case"
- L218 `[00:23:40]` "the **Ulite** helped to compensate for"

→ **[一手 20260529 00:01:51]** R8 没有 UmethylB 的后续；Ulite 是 sardines 5 天实验的"水电解质补偿"角色被反复点出。

### 2. R8 **"Survival Biology" 命名扩展 0** — 完全缺席

R7（2026-01-16）首次出现 "Survival Biology" 概念落地。R8 4 期严格 grep `Survival Biology` **0 命中**。

### 3. R8 **Olympic / Sweden 个人身份 0 命中**

R7 在 2025-02 → 2025-06 集中回归 Olympic decathlete 身份，R8 整 3 周 **0 次** 提到 `Olympic|decathlete|Sweden|Swedish`。
→ R8 完全聚焦"健康知识输出"角色，未做个人叙事回归。 **[我推断]** 这与 R8 主题（癌症预防 / 50 岁后腹脂 / 甲状腺 / 沙丁鱼实验）偏"机制讲解"匹配——没有需要 personal anchor 的内容。

### 4. R8 **个人健康危机细节 0 展开**

R7 personal narrative 4 段弧标记为"未开"。R8 唯一带 personal anchor 的内容是 **5-29 sardines 5 天实验**，且是**新做的 n=1 实验**，不是历史健康危机的复盘。
- `[20260529 00:14:08]` "on day one, it was very easy. It was novel…"
- `[20260529 00:15:15]` "my mood and my attitude kind of shifted to if I have to choke down one more tin of sardines, then blank."
- `[20260529 00:16:53]` "I have to be honest, I was not perfectly fat adapted prior to going into this. I basically went straight to a keto diet from a moderate carb diet."
- `[20260529 00:20:39]` "I probably lost about two pounds of actual fat tissue, and the rest of it I lost one pound of glycogen and three pounds of water."

→ R8 personal narrative 仅 1 段（"我自己做了 5 天沙丁鱼实验"），**与 R7 personal 4 段弧（健康危机）不重叠**。健康危机 4 段弧仍**未开**。

### 5. R8 **0 个出书信号** — 严格 0 命中

`grep -iE "book|publish|writing a book|coming out|pre.?order"` 仅匹配到 `published_date` 这种 metadata 字段。0 次实质出书/出版意图。 **[我推断]** R8 没有任何 book launch / pre-order / "my book" 的话术。

### 6. R8 **3 周 = 3 个机制题 + 1 个 n=1 实验题** — 内容架构非常稳

| 周 | 类型 | 主题 |
|---|---|---|
| 5-08 | 机制题（疾病）| 结肠癌 — 1 个机制路径（胰岛素 → 葡萄糖喂养 → 慢性炎症） |
| 5-15 | 机制题（年龄）| 50 岁后腹脂 — 激素轴（睾酮↓/雌二醇↓ → 内脏脂肪↑ → 芳香化酶 → 自我强化）|
| 5-22 | 机制题（症状）| 甲状腺 10 个 daily habits — 倒计时 + 7 因素轴（TPO / T4→T3 / iodine 竞争 / 自身免疫）|
| 5-29 | n=1 实验题 | 5 天只吃沙丁鱼 — 自我实验 → 失败/不舒服 → 解释机制 |

→ **[我推断]** R8 没有任何"产品发布 / 嘉宾访谈 / news reaction"类型，全部是 **讲课型 + n=1 实验型**。

### 7. R8 **"my clinic" 提到 1 次** — 2026-05-22

`[20260522 00:18:16]` "At my clinic, we always test thyroid antibodies because it's such a critical part of health that we need to understand if we have that."

→ 这是 R8 唯一一次直接提到"我的诊所"。 **[一手 20260522 00:18:16]**。R7 也有 my clinic 提及，R8 不是新出现，但**继续使用**说明 Ekberg 仍以"clinician + educator"双身份运营。

### 8. R8 **GLP-1 药物 0 命中**

`Ozempic|Wegovy|GLP-1|semaglutide|tirzepatide|Mounjaro` 在 R8 4 期字幕里 **0 次** 出现。 **[我推断]** 2026-05 这个时段，Ekberg 没有在内容层面"接招" GLP-1 这波热度——这是他 R8 时刻意留白的话题（与 Berg 大量拆 Ozempic 形成对比）。

### 9. R8 **carnivore / animal-based 0 命名命中**

R7 已有"动物性饮食"框架的零星出现。R8 严格 `carnivore|animal-based|beef salt water` **0 命中**。 **[我推断]** R8 没有"carnivore 自我认同"的话术——他 5-29 这期 5 天沙丁鱼是单食物实验，**没有把它命名成 "carnivore"**。这是一个**有意识的措辞选择**。

### 10. R8 **接住了 R7 "insulin resistance" 主轴**

R8 4 期全部以"胰岛素抵抗是根因"为枢纽：
- 5-08 结肠癌：胰岛素是 mitogenic + anabolic → 驱动细胞分裂 → 高血糖选择性喂癌细胞
- 5-15 50 岁后腹脂：胰岛素抗性 → 内脏脂肪储存 → 芳香化酶 → 雌激素/睾酮比改变
- 5-22 甲状腺：胰岛素抗性 → 肝脏 T4→T3 转换被卡（肝脏做 60% 的转换）→ 减少活性激素
- 5-29 沙丁鱼实验：低碳水 → 胰岛素↓ → 肾排钠↑ → 电解质流失 → "keto flu 实为矿物质流失"

→ **[我推断]** R8 是 **"胰岛素抵抗作为总根因"的集中输出期**——4 期从 4 个不同症状（癌症 / 腹脂 / 甲状腺 / 低碳水反应）反推到同一个机制。这是 R8 内容架构的"硬骨架"。

---

## 四、与 R7 对照（R7 → R8 验证清单）

| R7 末段线索 | R8 是否接住？| 证据 |
|---|---|---|
| UmethylB 命名首次落地 | **未接** | 0 命中（`UmethylB|umethylB`）|
| "Survival Biology" 概念 | **未扩展** | 0 命中（`Survival Biology`）|
| Olympic / Sweden 身份回归 | **未继续** | 0 命中（`Olympic|decathlete|Sweden`）|
| personal narrative 4 段弧（健康危机）| **未开** | R8 唯一 personal 是 sardines n=1 实验，非健康危机 |
| 出书 | **未启动** | 0 命中（`book|publish|writing a book`）|
| Ulite 落地 | **继续用** | 3 次提到，作为 sardines 5 天实验的电解质补偿 |

→ **[我推断]** R8 是一个**"内容稳定期"**——不发布新产品、不扩展新概念、不开新个人叙事弧，只在已建立的"胰岛素抵抗根因"框架内做 4 个症状题。这是 Ekberg 的**内容节奏控制**的体现：每 8-12 周一个产品/概念周期（推测，需对照 R5/R6），中间段是"机制输出期"。

---

## 五、本期新增信号 vs 既有模式

新增信号：
- **[一手 20260529 00:14:08 → 00:20:39]** 5 天沙丁鱼 n=1 实验——这是 R8 唯一一个"做了一次"的内容，提供了可量化的个人数据（5-6 lb loss = 2 lb 脂肪 + 1 lb 糖原 + 3 lb 水；3 scoops Ulite/day；~5,000 mg EPA+DHA/day；~1,600 mg 钙/day；~15 mg 铁/day；~265 μg 硒/day）。
- **[一手 20260522]** "10 个 daily habits" 倒计时结构（#10 = 缺脂肪 / #9 = 自来水氟 / #8 = 非发酵大豆 / #7 = cardio 过量 / #6 = 缺硒锌碘 / #5 = 种子油 / #4 = 蓝光 / #3 = 慢性应激 / #2 = 麸质 / #1 = 胰岛素抵抗）——这是 R7 还未出现过的新话术结构（之前多用 "5 things" / "3 reasons"）。

既有模式的延续：
- 每期 0:20 招呼语 "Hello, health champions" 4/4
- 每期结尾 "If you enjoyed this video, you're going to love that one. And if you truly want to master health…" 标准 CTA 4/4
- "Three legs on a table / triangle" 类比（5-08 食物/睡眠/运动）4/4 反复
- "Three categories: structural, emotional, chemical" 框架（5-08）

---

## 六、3 周核心节点小结

> **[我推断]** R8 这 3 周的"核心节点"是 **2026-05-29 的 sardines 5 天 n=1 实验**——它（a）打破连续 3 期"纯机制题"的节奏、（b）首次大量点名 Ulite 产品（R8 唯一提到自己产品的那期）、（c）给出可量化的个人数据，**为 R9 后续可能的"产品复盘 / carnivore 试水 / 出书预告"留下钩子**。但 R8 内部**没有任何**关于 R9 走向的明示。

---

**Agent 6（时间线）结束** — 写入 `${HOME}/Documents/女娲造人/skills/MiniMax-M3-Claude/drekberg-perspective/references/research/r08/06-timeline.md`
