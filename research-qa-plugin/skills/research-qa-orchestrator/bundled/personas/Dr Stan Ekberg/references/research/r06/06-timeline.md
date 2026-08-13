# R6 时间线 (2022-06-17 → 2024-05-17, 23 个月)

## 0. 范围与切片

- 文件范围: `${HOME}/Documents/女娲造人/@drekberg/` 第 501-600 个 .md
- R6 起止: `20220617001.md` → `20240517001.md`
- 跨度: 23 个月, 100 个文件
- 源 corpus 总数: 707 个文件

## 1. Grep 命令与命中数

| 关键词 | R6 命中文件数 | 备注 |
|---|---|---|
| `Health Champions` | 91 / 100 | 91% 出现率, 开场白 |
| `Ulite` / `Uveia` | 0 / 100 | R6 整个 0 命中 |
| `Nexus` | 1 / 100 | `20240419001.md` (2024-04-19) 唯一命中 |
| `Survival Biology` | 0 / 100 | R6 整个 0 命中 |
| `former Olympic\|decathlete` | 0 / 100 | R6 整个 0 命中 |
| `Sweden\|Swedish` | 2 / 100 | `20221118001.md` + `20230106001.md` |
| `carnivore` (case-insensitive) | 11 / 100 | 散布在 2022-06, 07, 2023-04 |
| `GLP-1\|Ozempic\|Wegovy\|Mounjaro\|semaglutide\|tirzepatide` | 1 / 100 | `20230728001.md` (2023-07-28), 15 次命中(标题+正文) |
| `personal experience` | 0 / 100 | R6 整个 0 命中 (R5 状态延续) |
| `book\|publish\|author` | 100 / 100 | 全部是 published_date 元数据命中, 无内容提及 |
| `Wellness For Life` | 0 / 100 | R6 整个 0 命中 (仅 2011 早期有) |
| `User Manual` | 0 / 100 | R6 整个 0 命中 (2013 早期节目名有) |
| `keto` | 39 / 100 | 主题高频 |
| `intermittent fasting\|fasting` | 46 / 100 | 主题高频 |
| `mitochondri` | 6 / 100 | 主题中频 |
| `holistic\|alternative` | 22 / 100 | 立场高频 |
| `insulin resistance\|metabolic` | 93 / 100 | 核心高频 |
| `root cause` | 16 / 100 | 招牌词 |

## 2. 时间线发现 (5-10 条核心)

### 发现 1: Health Champions 100% 开场锁定延续, 但 2024 末段开始松动

- 2022-06 至 2024-04 中段: 91/100 文件命中 "Health Champions" 开场白
- 2024-04 末至 2024-05: 末 3 个文件 (20240419, 20240426 仍 1, 20240503 1, 20240510 1, 20240517 0) 出现不命中文件
- 具体计数:
  - `20240412001.md`: 0 次
  - `20240419001.md`: 0 次 (出现 Nexus 新开场, 见发现 3)
  - `20240517001.md`: 0 次
- 推断: 2024 年 4 月中下旬开始, 至少部分视频去掉了 "Hello Health Champions" 开场, 可能转向新节目/新频道结构
- **一手**: `20220617001.md 00:00:00.000` "Hello Health Champions. Today we're going to talk about the top 10 foods to stop sugar cravings"
- **一手**: `20240510001.md 00:00:00.040` 仍为 "Hello, Health Champions! Today, we're going to talk about..."

### 发现 2: carnivore 主题在 R6 呈"早出现 + 中期集中"两段分布

- 早期零星 (2022 年夏季): `20220624001.md`, `20220715001.md`, `20220722001.md` 出现 1 次
- 中期集中 (2023-04): `20230407001.md` (2 次), `20230421001.md` (1 次)
- 2023-04 之后整个 R6 范围 (2023-05 → 2024-05) carnivore 提及归零
- 特殊对比: 整 corpus 2022-2026 中 `20230728001.md` 是 R6 之前/期间关于 GLP-1 药物 (Ozempic) 的单点爆发 (15 次), 同时也是标题级显式评论
- **一手**: `20230407001.md 00:29:07.200` "who eat carnivore they understand this people only eat animal products they don't necessarily eat all"
- **一手**: `20230407001.md 00:29:34.140` "protein and 73 from fat so even someone who is carnivore that you think they often tell you"
- **一手**: `20230728001.md 00:00:06.300` "loss medication like ozempic and I've gotten tons and tons of questions hundreds literally"
- **一手**: `20230728001.md` 标题: "You Must Know THIS Before Taking WEIGHT LOSS Meds like OZEMPIC"

### 发现 3: 2024-04-19 (R6 末段) 出现 Nexus Body Test 节目新开场

- **一手**: `20240419001.md 00:26:22.040` "the tele-health services from my clinic. It's a brand new program called Nexus Body Test Testing,"
- 这是 R6 唯一提及 Nexus 的文件, 也是 R6 唯一提及 tele-health / my clinic 的文件
- R6 之前 0 个 Nexus 节目, R6 之后 0 个 (R6 内单点出现)
- 这是 "新业务/新栏目" 的极早信号, 不构成爆发
- [我推断]: 这是 Ekberg 启动自家诊所远程医疗服务的初期宣传, 远未成为主轴

### 发现 4: Sweden 背景仅出现 2 次, 都不是 "former Olympic decathlete" 包装

- `20221118001.md 00:07:05.280` "punishable by imprisonment in many places now in many places like Sweden where I'm from it's even"
- `20221118001.md 00:07:29.520` "there was an accident or not and the reason I bring this up is that Sweden who has really"
- `20230106001.md 00:16:13.440` "Swedish Pizza salad it's essentially a version of coleslaw but it's much healthier than that because" (此处是菜名, 非背景)
- R6 0 个 "former Olympic" 或 "decathlete" 提及
- **一手**: 上述 Sweden 提及为仅有的自述出身场景
- [我推断]: R6 期间 Ekberg 极少包装自己的运动员背景, 重心完全放在知识内容 (insulin resistance 93% 命中率) 而非人设

### 发现 5: personal experience 弧线在 R6 仍未展开

- R6 整段 0 个文件命中 "personal experience"
- 对比: 2018-04-06 `20180406001.md 00:01:10.139` "school and had some personal experiences. So what I wanted to share with my" (R6 之前有, R6 0)
- R5 状态 (三段弧) → R6 维持, 没有把"健康危机 → 找到答案 → 救他人"展开为长弧
- [我推断]: R6 仍是知识传播/科普阶段, 把自身故事继续压缩为一句 "I had a health issue" (R5 已记录), 没有启动大型 first-person 长弧节目

### 发现 6: 2023-07-28 Ozempic 视频 = R6 唯一重大时事评论爆发点

- 文件: `20230728001.md`, 标题 "You Must Know THIS Before Taking WEIGHT LOSS Meds like OZEMPIC"
- 命中 15 次 (全 corpus 在 2022-2026 范围内仅这一篇 + 2026 年后续)
- 时间点: 2023-07-28, 紧跟 Wegovy 2021-06 获 FDA 批准 + Ozempic 走红 2022-2023
- 关键自述:
  - "loss medication like ozempic and I've gotten tons and tons of questions hundreds literally"
  - "my doctor is pushing me to go on ozempic I'm refusing too" (来自观众反馈)
  - "called wegovy and the other is called ozempic so these contain the active ingredient"
- 表明 Ekberg 在 2023 年中明确把 GLP-1 类药物 (semaglutide) 列入主流评论议程
- **一手**: `20230728001.md 00:00:06.300`, `00:00:23.100`, `00:00:41.640`
- [我推断]: 这构成 R6 的"重大时事评论"唯一爆发点, 回应了 2023 年 7 月前后 Wegovy/Ozempic 在主流媒体的大幅曝光

### 发现 7: Baker/Chaffee 流量爆发期, Ekberg 几乎无反应

- 2023 末-2024 初 carnivore 圈 (Baker Chaffee Norwitz) 流量爆发
- R6 范围内 carnivore 提及集中在 2023-04 (2 个文件, 1+1 次), 此后归零
- 2023-07 之后整个 R6 内 carnivore 0 命中
- 0 个文件提及 "animal-based" 或 "beef salt water"
- 0 个文件提及 "Baker" 或 "Chaffee" (交叉验证未在 grep 中发现)
- [我推断]: Ekberg 没有"加入 carnivore 圈流量战", 维持自己的 insulin resistance 主轴不变. 这是 R6 内"无明显事件" 的具体含义: 行业热点同期发生, Ekberg 不参与

### 发现 8: 出书 0 个证据

- 0 个文件提到 "book" 作为内容 (所有 100 命中均为 published_date 元数据)
- 0 个文件提到 "User Manual" 作为 Ekberg 自己的产品 (2013 年同名节目已结束)
- 0 个文件提到 "Wellness For Life" (2011 早期)
- **结论**: R6 期间 Ekberg 没有启动出书计划 (至少在本切片内 0 自述)
- 与 R5 结论一致, R6 仍未启动

### 发现 9: 主轴不变, 内容侧 R6 仍是"知识+科普" 23 个月

- `insulin resistance` / `metabolic`: 93/100 (核心)
- `holistic` / `alternative`: 22/100 (立场)
- `root cause`: 16/100 (招牌词)
- `keto`: 39/100 (方法)
- `intermittent fasting` / `fasting`: 46/100 (方法)
- `mitochondri`: 6/100 (进阶)
- [我推断]: R6 是 Ekberg 频道的"稳定知识输出期", 23 个月无重大结构性变化, 只有 2023-07 Ozempic 1 次时事爆发和 2024-04 末 Nexus 极早信号

## 3. R5 → R6 对照表

| 维度 | R5 状态 | R6 状态 | 是否改变 |
|---|---|---|---|
| Health Champions 开场 | 100% 锁定 | 91% 命中, 2024 末段开始出现不命中文件 | 末段松动 |
| personal experience | 停三段弧 | 0 命中 | 未展开 |
| Survival Biology 节目 | 0 个 | 0 个 | 不变 |
| 出书 | 0 启动 | 0 启动 | 不变 |
| carnivore 流量参与 | 0 | 11 个文件零星提及, 2023-04 后归零 | 不参与 Baker/Chaffee 流量战 |
| GLP-1 药物评论 | 无 | 1 个文件 (2023-07-28) 爆发 (15 次) | 2023 年中明确评论 |
| 业务/产品扩张 | 无 | Nexus Body Test 极早信号 (2024-04-19) | 单点出现, 不构成爆发 |
| Sweden 背景 | 提及 | 2 次, 非包装 | 不变 |
| Olympic 背景 | 提及 | 0 次 | R5 提到, R6 不再包装 |

## 4. 总结

R6 (23 个月) 是 Dr. Sten Ekberg 频道的**知识输出稳定期 + 一次时事爆发 + 一个新业务极早信号**:

1. **主轴稳定**: insulin resistance 93%, Health Champions 91%, keto/fasting 40%+, 内容侧几乎不变
2. **唯一时事爆发**: 2023-07-28 Ozempic/Wegovy 评论视频 (15 次命中, 单点)
3. **唯一新业务信号**: 2024-04-19 Nexus Body Test 远程医疗服务提及 (单点)
4. **不出书、不加入 carnivore 圈流量战、不展开 personal experience 长弧**
5. **2024-05 末段**: Health Champions 开场开始出现不命中文件, 但 R6 切片看不到完整新结构, 留待 R7

---

**完整文件路径**: `${HOME}/Documents/女娲造人/skills/MiniMax-M3-Claude/drekberg-perspective/references/research/r06/06-timeline.md`
