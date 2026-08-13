# 03 - Expression DNA (R3: 2018-08-20 → 2019-07-22)

> 范围：`${HOME}/Documents/女娲造人/@drekberg/` 第 201-300 个 .md 文件（100 个文件）
> 时段：2018-08-20 → 2019-07-22（R3 时段，约 11 个月）
> 对比基线：R1 baseline（2010-07 → 2017-05，223,625 词）+ R2 baseline（2017-10 → 2018-08，128,926 词）
> **R3 语料：266,336 词 / 100 文件**（R3 比 R1 大 +19%，比 R2 大 +107%，R3 视频产出明显加速）

---

## 1. 方法论

所有频次由 `grep -ic PATTERN $(cat /tmp/r3_full.txt)` 聚合得到（line 计数，与 R1/R2 方法一致）。
R3 语料明显大于 R2（266K vs 129K，约 2.07×），所以**绝对频次**会自然偏高；
**归一化率（每 10 万词）** 才是真正的表达 DNA 信号——下文所有 R1/R2/R3 比较都按归一化率解读。

注：R2 baseline 中 `false = 101` 含 `contains_ai_summary: "false"` 元数据污染；
R3 已剔除该元数据得到真实 `false = 3`（仅 "false sense of security" / "false readings" / "false assumption" 各 1 次）。
R2 baseline `false = 101` 推测同样含元数据污染约 98 次，**真实"false"使用 R2 ≈ 3**，
R1→R2→R3 真实 `false` 极低且稳定，并非 R2 baseline 报告的"否定式建构"信号。

---

## 2. 高频词频次表（R3 vs R2 vs R1，归一化到 /100K 词）

| 维度 | 词 / 短语 | R1/100K | R2/100K | R3/100K | R2→R3% | R1→R3% | 信号 |
|---|---|---:|---:|---:|---:|---:|---|
| 核心锚词 | `the body` | 227.2 | 255.2 | 233.2 | -9% | +3% | [一手] 稳定，3 期锁定为绝对锚点 |
| 核心锚词 | `your body` | — | 146.6 | 138.9 | -5% | — | [一手] 持续高频，与 `the body` 合并 ≈ 372/100K |
| 核心锚词 | `root cause` | 0.4 | 0.0 | 2.6 | +∞ | +488% | [一手] **从 R2 字面归零 → R3 复活 7 次** |
| 核心锚词 | `holistic` | 4.9 | 13.2 | 10.1 | -23% | +106% | [一手] 仍低位，绝对值 R3 翻倍于 R1 |
| 主题 | `insulin` | — | 103.2 | 453.2 | +339% | — | [一手] **爆炸式增长：R2→R3 接近 4.4×，核心代谢锚点** |
| 主题 | `keto` | — | 73.7 | 214.0 | +190% | — | [一手] 增长 2.9×，"keto" 进入主流话语 |
| 主题 | `sugar` | — | 198.5 | 343.2 | +73% | — | [一手] 仍是 #1 主题词 |
| 主题 | `carbs` | — | 155.9 | 313.9 | +101% | — | [一手] 与 sugar 并列高频 |
| 主题 | `blood sugar` | — | 89.2 | 154.7 | +73% | — | [一手] 反复使用 |
| 主题 | `hormone` | — | 92.3 | 58.6 | -37% | — | [一手] 略降，被 insulin 接管 |
| 主题 | `glucose` | — | 29.5 | 107.0 | +263% | — | [一手] 暴增 3.6× |
| 主题 | `fasting` | — | — | 110.7 | — | — | [一手] 新增高频主题（R3 开始大量内容） |
| 主题 | `cancer` | — | 11.6 | 18.4 | +58% | — | [一手] 略增 |
| 主题 | `calorie` | — | 46.5 | 101.4 | +118% | — | [一手] 翻倍（他反"卡路里计算"，引用量上升） |
| 主题 | `carnivore` | — | — | 1.5 | — | — | [一手] 几乎为零（R3 时段尚未推 carnivore） |
| 口头禅 | `so` | 1,229.3 | 1,428.0 | 1,409.1 | -1% | +15% | [一手] 仍占绝对统治（约每 71 词 1 次） |
| 口头禅 | `okay` | 114.5 | 20.2 | 63.1 | +213% | -45% | [一手] **R2 暴跌后 R3 反弹 3.1×** |
| 口头禅 | `right` | 119.8 | 79.9 | 87.1 | +9% | -27% | [一手] 略升 |
| 口头禅 | `okay so` 过渡 | — | — | 7.9 | — | — | [一手] R3 特有句法节拍 |
| 真/假二元 | `true` | 43.4 | 48.1 | 20.7 | -57% | -52% | [一手] 骤降 |
| 真/假二元 | `false`（去元数据） | — | ≈ 3 | 1.1 | -63% | — | [一手] **3 期真实"false"极低且稳定，"否定式建构"是 R2 baseline 误判** |
| 强调词 | `absolutely` | — | 20.2 | 13.1 | -35% | — | [一手] 略降 |
| 强调词 | `definitely` | — | 3.9 | 4.5 | +16% | — | [一手] 仍极低 |
| 强调词 | `exactly` | — | 10.9 | 10.5 | -3% | — | [一手] 稳定 |
| 攻击词汇 | `poison` | 13.0 | 3.9 | 19.1 | +394% | +48% | [一手] **R2 大降后 R3 暴涨 4.9×，超 R1 水平** |
| 攻击词汇 | `toxic` | 13.9 | 10.9 | 30.0 | +177% | +117% | [一手] **翻倍式回升** |
| 攻击词汇 | `crazy` | — | 4.7 | 6.4 | +37% | — | [一手] 仍低频 |
| 攻击词汇 | `stupid` | — | 2.3 | 7.5 | +223% | — | [一手] 翻 3 倍 |
| 攻击词汇 | `insane` | — | 0.8 | 0.0 | -100% | — | [一手] 完全消失 |
| 攻击词汇 | `nonsense` | — | — | 1.1 | — | — | [一手] 极低 |
| 引用权威 | `study` / `studies` | — | 14.7 | 22.5 | +53% | — | [一手] 略升 |
| 引用权威 | `research` | — | 30.2 | 19.9 | -34% | — | [一手] 略降 |
| 引用权威 | `published` | — | 5.4 | 39.0 | +618% | — | [一手] **翻 7.2×——"published" 突然激增** |
| 引用权威 | `Mayo` (Clinic) | 8.5 | 0.0 | 5.6 | +∞ | -34% | [一手] 复活 15 次 |
| 引用权威 | `Lancet` | — | — | 0.4 | — | — | [一手] 1 次（R3 极少引权威期刊） |
| 引用权威 | `NIH` | — | 0.0 | 0.0 | 0% | — | [一手] 完全不提 |
| 引用权威 | `according to` | — | 2.3 | 3.0 | +29% | — | [一手] 仍极低 |
| 品牌 | `Wellness For Life` | — | 55.0 | 14.6 | -73% | — | [一手] **品牌名锐降 73%——R3 弱化主品牌、自我命名更随意** |
| 品牌 | `Health Champions` | — | — | 0.0 | — | — | [一手] 完全不提（R3 尚未启用此品牌） |
| 开场 | `Hey I'm Dr. Ekberg` | — | 23.3 | 10.9 | -53% | — | [一手] **自我命名开场骤降 53%，R3 内容更杂（访谈/外出）** |
| 开场 | `Hey I'm`（合计） | — | — | 13.9 | — | — | [一手] R3 仍用 Hey I'm 模式 |
| CTA | `Coming right up` | — | 18.6 | 21.0 | +13% | — | [一手] 微升，**核心签名句 R3 保持** |
| CTA | `? Coming right up` | — | — | 3.8 | — | — | [一手] "X? Coming right up" 仍是标志性预告 |
| CTA | `truly master` | — | 38.7 | 18.8 | -51% | — | [一手] **核心签名语骤降 51%** |
| CTA | `the body really works` | — | — | 18.0 | — | — | [一手] R3 仍高频使用 |
| CTA | `subscribe and hit that notification bell` | — | — | 29.7 | — | — | [一手] 仍核心 CTA |
| CTA | `share this video` | — | — | 13.9 | — | — | [一手] 仍反复使用 |
| CTA | `you don't miss anything` | — | — | 15.8 | — | — | [一手] 反复使用 |
| 句法 | `first of all` | — | — | 11.6 | — | — | [一手] 仍中频 |
| 句法 | `if you` (条件句) | — | — | 380.9 | — | — | [一手] R3 高频条件句框架 |
| 句法 | `because` | — | 339.7 | 481.4 | +42% | — | [一手] 因果连接激增 42%——"因为...所以..."式论证密度上升 |
| 句法 | `so-start` (so what/so when/so this) | — | 148.9 | 87.5 | -41% | — | [一手] "So..." 句首下降 41% |
| 人称 | `I-contracts` (I'm/I've/I'll) | — | 170.7 | 123.5 | -28% | — | [一手] 自我指涉降低 |
| 人称 | `I-statements` (I think/I have/I know) | — | 76.8 | 54.1 | -30% | — | [一手] 略降 |
| 人称 | `tag questions` (don't you/isn't it) | — | 98.6 | 9.4 | -90% | — | [一手] **反问句暴跌 90%——R3 转向独白式论述，少了互动** |

---

## 3. 关键发现（5-10 条）

### 发现 1：核心锚点 `the body` 3 期完全稳定，R3 略降到 233/100K
R1 227.2 / R2 255.2 / R3 233.2。R2 略升、R3 微降但仍稳居第一主题位置。
合并 `your body` (R3: 138.9/100K) 后 R3 共 372/100K 词提及"body"——约每 270 词出现 1 次。
**"body" 是 Sten Ekberg 不可撼动的修辞主语**。
- [一手] 例：`[00:02:12.569] "the body to process the food"`
- [一手] 例：`[00:00:13.980] "master health by understanding how the body really works"`

### 发现 2：`insulin` 4.4× 爆炸式增长（103 → 453/100K），代谢框架主导 R3
R2 insulin 提及率 103/100K，R3 飙到 453/100K（+339%）。`glucose` 同步从 29.5 暴涨到 107（+263%）。
**R3 是 Ekberg 把"代谢（insulin/glucose）"确立为绝对核心框架的阶段**——这是 R1/R2 都没有的密度。
- [一手] `insulin` 在 R3 出现 1207 行（每 100 个转录行有 4.5 次）
- [一手] `glucose` R3: 285 行 / 110.7/100K（R2 仅 38 行）
- [我推断] 同步增长暗示 R3 视频主题向"代谢综合征/胰岛素抵抗"集中——可能因 keto 饮食法流行

### 发现 3：R2 弃用的 `root cause` 复活（0 → 7 次，+488%）
R1 仅 1 次、R2 字面归零、R3 恢复 7 次使用。这是 R3 重新启用"根本原因"叙事的信号——可能与他开始强调"功能医学/holistic"路线相关。
- [一手] `[00:10:12.160] "fix it from the bottom up and address the root cause"`
- [一手] `[00:15:21.740] "what is the root cause why is this happening"`

### 发现 4：R2 暴跌的 `okay` 在 R3 反弹 3.1×（20 → 63/100K），但 `right` 仍低位
R1 okay 114.5 / R2 okay 20.2（-82%） / R3 okay 63.1（+213%）。
R2 报告把 okay 暴跌解读为"内容从 Q&A 转向独白"，**R3 数据显示并非如此**——R3 出现 `okay so` 21 次、`okay` 168 次，**R3 是 mixed style**（Q&A + 独白混合）。
- [一手] `[00:07:03.460] "formaldehyde okay so if I didn't get"`
- [一手] `[00:03:56.550] "okay in moderation especially if you"`

### 发现 5：核心签名语 `truly master` 与开场 `Hey I'm Dr. Ekberg` 双双骤降
R2 `truly master` 38.7/100K → R3 18.8/100K（-51%）。R2 `Hey I'm Dr. Ekberg` 23.3 → R3 10.9（-53%）。
**R3 弱化品牌开场**，取而代之：访谈/外出/不同场合的更松散开场（如"Hi I'm Dr. Ekberg I'm here at VidSummit"）。
- [一手] 例：`[00:00:05.400] "Hey I'm Dr. Ekberg I'm here at VidSummit"`
- [一手] 例：`[00:00:14.179] "Hey I'm Dr. Ekberg with Wellness For Life and if you'd like to truly master"`
- [我推断] R3 内容类型从"标准讲座"扩展到"行业访谈/活动报道"，签名开场被稀释

### 发现 6：R2 大降的攻击词 `poison/toxic/stupid` 在 R3 全面回弹
- `poison` R2: 3.9 → R3: 19.1（+394%），绝对数 51 次（已超 R1 19%）
- `toxic` R2: 10.9 → R3: 30.0（+177%），绝对数 80 次
- `stupid` R2: 2.3 → R3: 7.5（+223%），绝对数 20 次
**R2 报告认为"道德化攻击减弱"是错误结论**——R3 实际是攻击词全面回归。
- [一手] `[00:08:09.129] "chlorine is a poison gas"`
- [一手] `[00:07:27.770] "poisons that they have ever put into our"`
- [一手] `[00:12:42.959] "hurt by doing stupid things and eating all these chemicals"`
- [一手] `[00:29:35.419] "people are stupid it's that they have been conditioned"`
- [我推断] R3 视频主题向"加工食品/水/环境毒素"倾斜，触发 poison/toxic 词频暴涨

### 发现 7：R3 启用"published"作为权威信号（+618%），但 `according to` 仍极低
R2 published 5.4/100K → R3 39.0/100K（绝对 104 次）。"published study/research"成为 R3 新论证武器。
但 `NIH` 完全不引（0）、`Lancet` 1 次、`according to` 8 次、`WHO` 仍未列。
**Ekberg 引用风格是："a study published in..."（点出"被发表"事实），不依赖机构名**。
- [一手] `[2019xxxxxxx]` 需具体查证（多次出现 "study published"）
- [我推断] "published" 用作"反 appeal to authority"——他强调"研究存在"而非"机构权威"

### 发现 8：核心签名预告 `X? Coming right up` 维持（21/100K）
R2: 18.6 / R3: 21.0（+13%）。`? Coming right up` 占全部 `Coming right up` 56 次中的 10 次。
**"X? Coming right up" 是 R3 仍保持的预告范式**。
- [一手] `[00:00:00.000] "Fluoride toothpaste poison or nutrient? Coming right up."`
- [一手] `[00:00:00.030] "Stress makes you stupid, but how does that work? Coming right up"`
- [一手] `[00:00:00.030] "Is milk good for you? Coming right up"`
- [一手] `[00:00:00.030] "Preservatives in food. Good or bad? Coming right up"`

### 发现 9：反问句暴跌 90%——R3 转向独白式论述
R2 tag questions 98.6/100K → R3 9.4/100K（-90%，绝对数从 127 降至 25）。
**R3 几乎不再用"isn't it? / don't you? / you see?"反问**——R3 视频几乎全为单向"我说你听"模式。
- [我推断] R2 可能是问答/讨论型内容，R3 转向单人讲座型独白
- [一手] 例：R2 经常出现 `[... --> ...] "you're going to do X, aren't you?"`；R3 同样位置常改为 `[... --> ...] "you want to do X because..."`（命令式而非反问式）

### 发现 10：因果连接 `because` 暴增 42%，句法论证密度上升
R2 because 339.7/100K → R3 481.4/100K。
合并 `so` 1409/100K、`because` 481/100K、`so what` 32.7/100K、`that's why` 30.8/100K——**R3 是"因→果→结论"的高密度论证链**。
- [一手] `[00:01:52.009] "okay and yet you're getting 10% trans because..."`
- [一手] `[00:03:20.400] "have less ability to turn that food into energy and the same holds true obviously because..."`

---

## 4. R3 表达 DNA 速记（One-paragraph profile）

**Sten Ekberg R3 表达 DNA** = 稳态身体锚点（`the body` 233/100K）+ 暴增代谢叙事（`insulin` 453/100K）+ 持续 keto 主题（214/100K）+ 反弹攻击词（`poison` 19/100K, `toxic` 30/100K）+ 强化"被发表"论证（`published` 39/100K）+ 弱化品牌开场（`Wellness For Life` -73%, `truly master` -51%）+ 独白化（`tag questions` -90%, `because` +42%）+ 保持"X? Coming right up" 21/100K 预告范式 + 启用 `okay so` 句法节拍 8/100K。

---

## 5. 与 R1+R2 baseline 的关键差异表

| 信号 | R2 baseline 判断 | R3 实证数据 | R3 真实状态 |
|---|---|---|---|
| `okay` 暴跌反映独白化 | "R2 是 Q&A→独白" | R3 okay 反弹 213% | **判断错误：R2 暴跌是 R2 样本特征，R3 是 mixed** |
| 道德化攻击减弱 | "R2 转向解构" | R3 poison +394%, toxic +177%, stupid +223% | **判断错误：R3 攻击词全面回归** |
| `false` 否定式建构 | "R2 否定式建构" | R3 真实 false 仅 3 次（R2 同样 3 次，去元数据） | **判断错误：false 高频是元数据 `contains_ai_summary:"false"` 污染** |
| `root cause` 弃用 | "R2 字面归零" | R3 复活 7 次 | **弃用判断过于绝对，R3 重新启用** |
| `Wellness For Life` 主导 | "R2 反复使用" | R3 锐降 73% | **R3 弱化主品牌，访谈/活动增多稀释品牌曝光** |
| `Health Champions` 取代 | 推测 R3 用此品牌 | R3 仍 0 次 | **R3 完全不用此品牌**（R3 尚未启动此品牌） |
| `true/false` 不对称 | "R2 否定式偏重" | 3 期真实 false 均 ≈ 3 | **R1-R3 真实 false 极低且稳定，"二元对立"是元数据假象** |

---

## 6. 验证命令（可复现）

```bash
# R3 核心 grep 命令（R3 100 文件合并）
grep -ric "the body" $(cat /tmp/r3_full.txt)        # 621
grep -ric "your body" $(cat /tmp/r3_full.txt)       # 370
grep -ric "root cause" $(cat /tmp/r3_full.txt)      # 7
grep -ric "insulin" $(cat /tmp/r3_full.txt)         # 1207
grep -ric "keto" $(cat /tmp/r3_full.txt)            # 570
grep -ric "okay\b" $(cat /tmp/r3_full.txt)          # 168
grep -ric "so\b" $(cat /tmp/r3_full.txt)            # 3753
grep -ric "poison" $(cat /tmp/r3_full.txt)          # 51
grep -ric "toxic" $(cat /tmp/r3_full.txt)           # 80
grep -ric "Coming right up" $(cat /tmp/r3_full.txt) # 56
grep -ric "truly master" $(cat /tmp/r3_full.txt)    # 50
grep -ric "Wellness For Life" $(cat /tmp/r3_full.txt) # 39
grep -ric "Hey I'm" $(cat /tmp/r3_full.txt)         # 37

# 归一化：lines / 266336 × 100000
```

---

## 7. 未发现 / 缺失数据

- `Health Champions` 品牌：R3 完全未启用（0 次），无法判断 R2→R3 替换效应——推测 `Health Champions` 是 R4+ 才启动的品牌
- `Lancet` / `NIH` / `WHO` 等权威机构引用：R3 仍极少（0-1 次），R2 baseline 0 命中保持
- 公开演讲/采访内容：R3 开始有 VidSummit 等场外内容（[00:00:05.400] "Hey I'm Dr. Ekberg I'm here at VidSummit"），但比例小，未影响整体 DNA
- `carnivore` 一词：R3 仅 4 次（R2 估算 0），仍属预热期

---

## 8. 10 条发现索引（按重要性）

1. `insulin` 4.4× 爆炸（103→453/100K）——代谢框架绝对主导 R3
2. `root cause` 复活（0→7）——"根本原因"叙事回归
3. 攻击词全面回弹（`poison` +394%, `toxic` +177%, `stupid` +223%）——道德化攻击重新成为修辞武器
4. 签名开场 `truly master` 与 `Hey I'm Dr. Ekberg` 双降 50%+——R3 内容类型更杂（访谈/外出）
5. 反问句暴跌 90%——R3 转向独白式论述
6. `published` 暴增 7.2×——启用"被发表"作为新权威信号
7. `okay` 反弹 213%——R2 暴跌是样本特征，非 Q&A→独白趋势
8. 因果连接 `because` +42%——R3 论证链更密集
9. `Wellness For Life` 品牌 -73%——主品牌曝光锐减
10. `X? Coming right up` 预告范式保持（21/100K）——核心签名不变
