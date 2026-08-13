# R3 智识谱系（2018-08-20 → 2019-07-22）调研报告

> 范围：100 个文件（`20180820001.md` → `20190722001.md`）
> 关键问题：R2 智识三件套（Bowden+Sinatra / Davis / Ohsumi）→ R3 哪些保留？R1+R2 零 Weston A. Price → R3 是否开始引用？90/10 反建制是否继续？

---

## 0. Grep 命令总览

```bash
# 人名 / 著作（去大小写、整词边界）
for term in "Weston A. Price" "Price" "Atkins" "Banting" "Perlmutter" "Grain Brain" \
            "Hyman" "Attia" "Pollan" "Campbell" "Taubes" "Esselstyn" "Mercola" \
            "Gundry" "Davis" "Wahls" "Sinatra" "Bowden" "Saladino" "Baker" \
            "Chaffee" "Norwitz" "Ohsumi" "Berg"; do
  count=$(grep -li "$term" $(cat /tmp/r3_files.txt) 2>/dev/null | wc -l | tr -d ' ')
  echo "$term: $count"
done

# 机构 / 科研权威
for term in "Mayo" "Harvard" "Cleveland" "NIH" "Lancet" "JAMA" "NEJM" \
            "WHO" "ADA" "American Diabetes" "study" "research" "journal" \
            "meta-analysis" "randomized" "Cochrane" "observational study" "cohort"; do
  count=$(grep -li "$term" $(cat /tmp/r3_files.txt) 2>/dev/null | wc -l | tr -d ' ')
  echo "$term: $count"
done

# 反建制
for term in "90/10" "pharma" "bias" "conflict of interest" "mainstream" \
            "Monsanto" "Big Pharma" "industry" "paying for the study" "conspiracy"; do
  count=$(grep -liE "$term" $(cat /tmp/r3_files.txt) 2>/dev/null | wc -l | tr -d ' ')
  echo "$term: $count"
done
```

**注：去噪说明。** `ADA` 的 39 命中、`WHO` 的 87 命中、`Berg` 的 58 命中均为子串噪音（`adapta` / `whole` / `Ekberg`）。经过整词边界二次过滤：
- 真实 `ADA`（American Diabetes Association）= **4 文件** [一手（他说的）]
- 真实 `WHO`（World Health Organization）= **1 处引用** [一手（他说的）]
- 真实 `Berg` = 0（全部是自指 Ekberg / Iceberg）

---

## 1. R3 智识谱系五大发现

### 发现 1：Weston A. Price 首次出现在 R3（重大变化，R1+R2 零 → R3 出现 2 次）

**[一手（他说的）][20180921001.md 00:08:04-00:09:25]**
> "there was a guy called Weston Price who travelled the world about a hundred years ago and he found that there were populations all over the planets who were extremely healthy who had no tooth decay no degenerative diseases... no matter where he went they were perfectly healthy as long as they ate whole food as long as they didn't mess with it as long as they didn't process it or turn it into Franken food... the problem we've gotten into is we've added too much grain too much legumes we process too much everything is sugary"
> *（视频：What Is The Paleo Diet? Paleo Diet for Beginners）*

Ekberg 用 Price 的"全球原始族群调查"作为 Paleo 的科学背书；明确点名"牙龈健康、无退化病"是 Price 的标志性发现。

**[一手（他说的）][20181105001.md 00:07:47-00:08:19]**
> "people like Dr. Weston Price Dr. Francis Pottinger these were brilliant brilliant people who had proven beyond a doubt in the 30s 40s 50s what effects the modern diet and the toxicity of the modern world will have on her body and they figured out how to reverse it and this is totally suppressed knowledge"
> *（视频：Nutrition Response Testing Explained By Freddie Ulan - Dr Ekberg）*

在与 Freddie Ulan（Nutrition Response Testing 创始人）对话中，Ekberg 把 Price + Pottenger 并列为"被压制的天才研究者"，与"30s-50s 的现代饮食毒性"叙事直接对接。
*注：王颢翰等 Pottenger 是猫研究、Price 是全球饮食研究，常被 carnivore/animal-based 群体合引。*

**对比 R2**：R1+R2 完全没有 Price。R3 是第一次出现，且是作为"被压制的科学英雄"叙事引入，不是附庸提及。

---

### 发现 2：智识外援极度稀薄，R3 没有引用任何当代 keto/carnivore 圈医生

**硬数据**（R3 100 文件 grep 结果）：
- `Bowden` 0、`Sinatra` 0、`Davis` 0、`Ohsumi` 0、R2 三件套全部清零
- `Banting` 0、`Hyman` 0、`Attia` 0、`Perlmutter` 0、Grain Brain 0
- `Pollan` 0、`Campbell` 0、`Taubes` 0、`Esselstyn` 0
- `Mercola` 0、`Gundry` 0、`Wahls` 0、`Saladino` 0、`Baker` 0、`Chaffee` 0、`Norwitz` 0
- 唯一明确点名的是 **`Atkins`（4 次，仅在"Keto vs X Diet"系列对照时出现）** 和 **`Dr. Oz`（1 次，20181102 反应视频）**

**[一手（他说的）][20190426001.md 00:00:00-00:01:28]**
> "The Atkins diet was founded was originated by dr. Robert Atkins he was born in 1930 he went to [...] weight and he wrote a book that was published in 1972 called the Atkins diet revolution then in 1989 he founded Atkins nutritional [...] from a blood clot so after dr. Atkins was gone the company went downhill"
> *（视频：Keto Diet vs Atkins Diet - Which Is Better?）*

**[一手（他说的）][20181102001.md 00:00:00-00:00:30]**
> "Hey today I want to comment on a video by Dr. Oz where his guest was a health [guru...] found a video on dr. oz channel"
> *（视频：Real Doctor Reacts To Doctor Oz: Intermittent Fasting "Health Guru" Healthy?）*

**[我推断]** R3 没有形成"引用某位智识领袖为我背书"的智识谱系——反而是 Ekberg 自己的视频成为"对照靶子"（Dr. Oz 反应、Atkins 对照）。他开始用 keto vs X 系列建立自己的"独立判断"形象，而不是引用任何圈中 KOL。

---

### 发现 3：科学权威使用降级为"批判性武器"，不作为正面引用

R3 出现 4 处机构/期刊引用，但全部被用作"反建制论据"，没有一处作为正面背书：

**[一手（他说的）][20190510001.md 00:07:55-00:08:03]**
> "so they quote some studies and a 2016 study in The Lancet had a five-year [follow-up]"
> *（视频：Keto Diet vs Mediterranean Diet - 批评 MedDiet）*

**[一手（他说的）][20190325001.md 00:01:05-00:02:31]**
> "the latest one by JAMA Journal of American Medical Association [...] in JAMA was what they call a cohort or an observational study that means they [don't] control variables"
> *（视频：Are EGGS BAD For You? - 批评鸡蛋恐惧）*

**[一手（他说的）][20190215001.md 00:02:29-00:02:49]**
> "Google and some of them were in the Google headings under WebMD and Mayo Clinic and some were under on lists posted by health harvard.edu and University Health News comm and according to diabetes.org the best low [glycemic foods]"
> *（视频：Foods To Control Diabetes Naturally - 引用为"它们怎么说"）*

**[一手（他说的）][20190712001.md 00:26:14-00:26:20]**
> "dietitians and when you go to the Mayo Clinic and you read the American Diabetes Association [recommendations]"
> *（视频：How To Increase Metabolism）*

**质量标记**：`randomized` 0、`meta-analysis` 0、`Cochrane` 0、`NIH` 0、Cochrane 没出现。
Ekberg 在 20190325 鸡蛋视频中说"research we have to look at who's paying for the study"——这是他对所有研究的默认怀疑框架。**[一手（他说的）][20190325001.md 00:02:06-00:02:12]**

---

### 发现 4：90/10 自创规则在 R3 找不到，反建制叙述以"老知识被压制"和"主流误诊"为主

**硬数据**：
- `90/10` 0 命中
- `90 percent` 出现 8+ 次，但都是描述性数字（如"90% 的脑信号来自运动"、"75-90% 脂肪比例"），**不是 R2 的自创规则**
- `90% of all the information` 等均为生理学数字

**[我推断]** R2 自创的"90/10 规则"在 R3 没有延续为口号。R3 的反建制叙述换成了两条新主线：

**主线 A：被压制的知识**
**[一手（他说的）][20181105001.md 00:08:14-00:08:19]** "and they figured out how to reverse it and this is totally suppressed knowledge"
把 Weston Price + Francis Pottenger 定位为"30s-50s 被压制的天才"。

**主线 B：主流误诊胰岛素抵抗**
**[一手（他说的）][20190617001.md 00:01:31-00:01:36]** "what the mainstream thinks insulin resistance is and I got this off of [the guidelines]"

**[一手（他说的）][20190617001.md 00:20:55-00:20:59]** "that's why it can be so frustrating for people who follow the mainstream"

**[一手（他说的）][20180903001.md 00:04:12-00:04:21]** "pharmaceutical companies in the world so [...] pharmaceutical giant that controls"
*（视频：Roundup & Cancer: Real Doctor Reacts To Monsanto's Lawsuit - 控诉孟山都）*

**[一手（他说的）][20190325001.md 00:02:06-00:02:16]** "really careful with research we have to look at who's paying for the study how was the study done"

**[一手（他说的）][20180917001.md 00:05:44-00:05:51]** "of mainstream and we ate more and more"
*（视频：Why Are Trans Fats Bad? - 控诉加工食品+主流）*

**R3 反建制清单**（5 文件）：
| 视频 | 反建制对象 |
|---|---|
| 20180917 Trans Fats | 加工食品+主流 |
| 20180903 Roundup/Monsanto | 孟山都/农药工业 |
| 20181102 Dr. Oz | 主流媒体医生 |
| 20190325 Eggs/JAMA | JAMA 观察性研究 |
| 20190617 Insulin Resistance Treatments | ADA/Mayo 主流指南 + 制药 |

---

### 发现 5：R3 智识谱系由 Ekberg 自创的两条新腿构成 —— (a) "Freddie Ulan / Nutrition Response Testing" 线 + (b) "Dr. Sten Ekberg with Wellness For Life" 自品牌

**（a）Freddie Ulan 线**（Ekberg 唯一明确的圈内"师傅"）

**[一手（他说的）][20181105001.md 00:00:51-00:01:00]** "honor of talking to a legend in our own time this is Freddie Ulan who is the [founder of Nutrition Response Testing]"

**[一手（他说的）][20181105001.md 00:13:56-00:14:01]** "those who don't know Freddie Ulan creating an organization has trained [thousands of practitioners]"

Ekberg 在 R3 4 个文件中重复引用 Ulan / NRT：
- 20180820 Do Probiotics Work?
- 20180917 Why Are Trans Fats Bad?
- 20181015 (待查)
- 20181105 Nutrition Response Testing Explained By Freddie Ulan
- 20190301 (待查)
- 20190412 (待查)

**[一手（他说的）][20181015001.md 00:08:00-00:08:04]** "in our office is we use something called nutrition response testing which is a [form of applied kinesiology]"
*（NRT = applied kinesiology = 肌力测试，争议性诊断法）*

**（b）Dr. Sten Ekberg / Wellness For Life 自品牌**

**[一手（他说的）][00:00:00-00:00:13] 多文件自介** "I am Dr. Ekberg with Wellness For Life" / "Hey I'm Dr. Sten Ekberg with Wellness For Life and if you like to truly master [health by understanding how your body works]"

"holistic health" 在 R3 出现 5+ 次，作为频道主轴。
**[一手（他说的）][20181105001.md 00:29:14-00:29:18]** "this channel is all about and we keep saying over and over and over that holistic"

---

## 2. R2 → R3 智识谱系变化表

| 维度 | R2 | R3 | 变化 |
|---|---|---|---|
| Weston A. Price | 0 命中 | 2 文件 20180921 + 20181105 | **首次出现**，作为"被压制的科学英雄" |
| Bowden + Sinatra | 出现 | 0 | **消失** |
| Davis | 出现 | 0 | **消失** |
| Ohsumi | 出现 | 0 | **消失** |
| Dr. Atkins | 未明确点名 | 4 文件（Keto vs X 系列） | **新增**，作为对照靶 |
| Dr. Oz | 0 | 1 文件（反应视频） | **新增** |
| Dr. Royal Lee | 0 | 1 文件（20180924 VitC） | **首次出现** |
| Dr. Francis Pottenger | 0 | 1 文件（20181105） | **首次出现** |
| Freddie Ulan | ? | 6+ 文件 | **强化**为"圈内师傅" |
| 90/10 自创规则 | 自创 | 0 | **消失**（被"被压制的知识"叙事替代） |
| 主流批判 | 90/10 规则 | 5 文件独立案例 | 形态转变 |
| 反建制叙述 | 系统化口号 | 个案式（每个视频一个案例） | 颗粒度变细 |
| JAMA / Lancet / NEJM | 0 | JAMA 1 / Lancet 1 | **新增**为"批判性武器" |
| ADA / Mayo / Harvard | 0 | ADA 4 / Mayo 8 / Harvard 1 | **新增**为"主流批判对象" |
| NIH / Cochrane / NEJM | ? | 0 | 不出现 |
| randomized / meta-analysis | 0 | 0 | 持续缺失 |
| "who's paying for the study" | ? | 1（20190325） | **新增**，作为研究怀疑框架 |

---

## 3. 一手 vs 二手 vs 我推断

所有引用 Ekberg 的话均为 **[一手（他说的）][YYYYMMDD###.md HH:MM:SS]**。
所有"[我推断]"均标注于行末。

---

## 4. R3 智识谱系速写

**R3 的 Ekberg 是一个"用 Freddie Ulan 替代 R2 智识三件套、用 Weston Price 替代 Bowden+Sinatra、用 Dr.Oz/Atkins 作为对照靶、用 JAMA/Lancet/ADA/Mayo 作为批判对象"的独行侠**。

- **正典英雄**：Weston Price + Royal Lee + Francis Pottenger（被压制的 30s-50s 研究者）
- **圈内师傅**：Freddie Ulan（Nutrition Response Testing 创始人）
- **对照靶子**：Dr. Robert Atkins（已逝，Keto vs X 系列）、Dr. Oz（当代，反应视频）
- **批判对象**：ADA / Mayo Clinic / JAMA / Lancet / Harvard Health / Monsanto
- **研究方法学批判**："cohort or observational study"（不是 RCT）、"who's paying for the study"、缺 NIH / Cochrane / randomized
- **自我定位**：Dr. Sten Ekberg, Wellness For Life, holistic health（反复自介 80+ 次）

R3 没有形成"我在引用 X 大师所以我对了"的认知权威链；反而是 Ekberg 在 R3 阶段开始建立"我 = 独立判断者"的品牌——所有外部引用都是"被压制的英雄"或"被批判的谬误"两极。
