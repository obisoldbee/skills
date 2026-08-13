# R1 Decisions 决策维度调研报告

**文件范围**：R1 = 20100701 → 20170929（前 100 个 .md 文件）
**调研时间**：6 分钟内
**主要方法**：grep-first，必要时 Read 一次

---

## grep 命令清单

| # | grep 命令 | 命中数 |
|---|---|---|
| 1 | `grep -l -E "I decided\|I quit\|I started\|I created\|I founded\|my journey\|my story\|my background\|Health Champions\|Wellness for Life\|Why I\|the reason I\|transition\|career change"` | 8 文件 |
| 2 | `grep -rEn -i "I decided\|I quit\|I started\|I created\|I founded\|my journey\|my story\|my background\|Health Champions\|Wellness for Life\|Why I\|the reason I\|transition\|career change"` 全文 | 76 行（覆盖全库 R1+） |
| 3 | `grep -rEn -i "Ekberg\|Dr\. Ekberg\|Sten\|decathlon\|olympic\|chiropract\|Health Champions\|Wellness for Life"` × `I \|my \|we \|founded\|created\|started\|background\|journey\|story` 过滤 | 30+ 行 |
| 4 | `grep -rEn -i "I (was\|am) (an?\|the) (decathlete\|olympian\|athlete\|chiropractor)\|former (olympi\|decath)\|became (a \|an )?(chiropractor\|doctor)\|Olympic\|decathlon\|competed\|trials\|personal (record\|best)"` | 4 命中 |
| 5 | `grep -rEn -i "Alpharetta\|Cumming\|GA\)\|moved\|relocat"` | 12+ 命中 |
| 6 | `grep -rEn -i "I have a\|here's why\|that's why I\|I started"` | 30+ 命中 |

**结论**：R1 期间（2010-2017）Ekberg **几乎没有"自我叙述式"的个人故事 / 转型决策 / 创业决策发言**。这 100 个文件里，他呈现的公开身份是 **临床执业整脊师 + 公益健康讲座主讲人**，"决策"类内容几乎都是 **病人决策（病人怎么决定来找他）** 和 **临床方法论决策**（用整脊还是手术），不是他个人的人生决策。

---

## 5–10 个发现

### D1. 职业转变：前瑞典 / 国际十项全能运动员 → 整脊师（**二手叙述** + **他未直接讲**）
- 二手（别人说他）：20130519001.md [00:00:22.199 → 00:00:32.250] 主持人介绍他："his [unclear] former Olympian he was a former Olympian in the decathlon and it was this Barcelona Olympics, 12th place"（中置信度——声音识别可能错）
- 一手痕迹（最早期）：20100701001.md 标题 `Decathlon Discus Throw - Sten Ekberg`，是第三方拍摄的他投铁饼的赛事画面（46.90m，第一名）——这条视频 2010-07-01 发布在他频道里，是**唯一一条非健康类内容**，且 100 文件里只此 1 条，2010 之后再也没有任何运动 / 训练 / 田径内容。
- 他本人未在 R1 任何文件中讲"我为什么从十项全能转行做整脊"——[我推断] 这种"自传式讲述"在 R1 期间明显被回避，公开身份是 "chiropractor in Cumming (GA)"。**[我推断]** 真正展开"former Olympian → Dr. Ekberg"叙事是 2018+ 才大量出现的（R2 之后才看到他讲自己故事）。

### D2. 地理 / 执业地址：Alpharetta → Cumming, GA（**一手**）
- 20130519001.md [00:00:11.519] 主持人问："chiropractor in well now Cumming (GA) right now Alpharetta Cumming (GA) yeah yes"——2013 年他**同时在 Alpharetta 执业**。
- 20140530001.md [00:01:24.460] 病人 Connie 描述："you came to see us in Alpharetta just a couple of months before we moved up to Cumming, so we only saw you a few times and then what happened?" Ekberg 答："after y'all moved... I thought the drive was not worthwhile"（病人因搬迁而离开 6 个月）。这说明 **2013→2014 之间他的诊所有一次搬迁**。
- 20140418001.md [00:00:06.109] 自我介绍定型为："I'm a chiropractor in Cumming, Georgia"——2014 年起地址定型 Cumming。

### D3. 临床方法论决策：拒绝"cracking"（大力 / 旋转式）整脊，**用神经学 + 上颈段 / Arthrostim 仪器方法**
- 一手，20140424001.md [00:01:18.692] 病人 Lisa："more old-school just being cracked all the time versus the education that you provide of understanding how the body works, how the brain works... and the methods that you've used thus far that are not invasive have also been the reasons that I found you"
- 一手，20140530001.md [00:01:04.750] 病人 Connie："I had finished some other chiropractors who like to do lots of cracking and I decided that was not the type of treatment that I wanted"
- 一手，20140825001.md [00:04:55.699] 他向观众解释自己用的工具："this is called an Arthrostim, which is like a mini jackhammer, which is very gentle, it can go from a few grams of pressure up to several pounds... kids have explained it as tickling or feeling like a massage"
- **决策内容**：他**主动选择"神经学基础的、仪器辅助、不大力扭转"的整脊手法**，并把它作为差异化卖点告诉每个病人。
- 自我叙述（20140211001.md [00:00:01.849]）："I'm a chiropractor who practices neurologically based chiropractic and we're going to talk about more holistic approach"

### D4. 品牌化决策：节目叫"User Manual for Humans"（**一手**）
- 20110531001.md [00:00:06.240] 起头："we're going to talk about user manual for humans part three, and today is the first... food for humans"——**2011 年 5 月，他就把自己的公益讲座系列命名为 "User Manual for Humans"**。
- 20110710001.md / 20110710002.md 重复："i am Dr. Sten Ekberg and i'm excited to have you here we're going to talk about user manual for humans"
- 20130519001.md 标题系列之一："Food For Humans - Your Cumming Chiropractor Dr Ekberg"——这成为他长期科普系列的子品牌。
- **[我推断]** "Health Champions" 这个称呼在 R1 100 文件里**一次都没有出现**——最早出现是在 2017+ 或更晚（系统全局 grep 显示 2017 后的视频才稳定出现 "Hello Health Champions" 开场白）。"Health Champions" 是 R2 / R3 阶段的产物，不是 R1 决策。

### D5. 写作策略决策：拒绝"你应该吃这个 / 别吃那个"式清单，**坚持讲"为什么"（principles）**
- 20110531001.md [00:02:48.239 → 00:02:59.370] 反复强调："everybody knows that you're supposed to eat more vegetables and you're supposed to eat less sugar and don't drink too many beers everybody knows that but we want to focus on are the whys... why don't we want to do that"
- 20130519001.md [00:01:57.540] 重复："we will go into very little detail as far as telling you to eat this and this and this and this because you've already heard that all your life... but what we will talk about is principles of why is it that way what how does the body work"
- **决策内容**：R1 全程他**主动选择不写"该吃什么"的清单 / 文章结构**，而是每次都问"为什么"。这是 R1 期间最稳定、最可被反复验证的方法论决策。

### D6. 公共讲座 vs 一对一诊疗：并行双轨
- R1 文件结构明确分两类：
  - **大型健康讲座**（20110516, 20110519, 20110531, 20110612, 20110706, 20110710, 20110715, 20130127, 20130327, 20130401, 20130505, 20130511, 20130519, 20130918, 20140211, 20140415, 20140424, 20140516, 20140530, 20140825）——"good evening and welcome everybody" 风格
  - **病人 testimonial 一对一录像**（20140211, 20140415, 20140418, 20140424, 20140516, 20140519, 20140521, 20140530, 20140825, 20160515, 20170820）——"Hello I am Dr Ekberg and I have a patient here" 风格
- 20130519001.md [00:00:38.100] 主持人："so so he's been here you see you're talking about few for humans how to fuel your body properly"——**他已经持续做同一主题的系列讲座至少 2 年**。
- **决策内容**：**[我推断]** 2011-05 起，Ekberg 决定**用 YouTube 公开录像"健康讲座"**（潜在数千观众）+ **把"病人 testimonial"作为社会认同素材**（潜在新病人），双轨并行。这是 R1 期间最稳定的 **内容 / 营销决策**。

### D7. "Wellness For Life" 品牌名称出现节点（**一手**）
- R1 内 2017 年下半年才开始出现 "Wellness For Life" 称呼：
  - 20170820001.md [00:00:00.290]："Hi I'm Dr. Sten Ekberg with Wellness For Life where we do nutritionally and neurologically based chiropractic and healthcare"
- 2017-08-20 之前 99 个文件里**没有 "Wellness For Life" 这个完整短语**——它最迟在 2017 年 8 月成为他的主品牌。
- **[我推断]** 这是他在 R1 末尾的命名决策：从 2011 的 "User Manual for Humans" 讲座系列 → 2017 的 "Wellness For Life" 执业品牌。

### D8. 决策"不写"的部分（negative findings）—— 这些**在 R1 完全没出现过**
- 没有任何文件提到"我从十项全能退役" / "为什么不当运动员" / "我的人生转型"
- 没有任何文件提到"我创立 Health Champions for Humanity"
- 没有任何文件提到"我结婚 / 家庭" / 个人生活
- 没有任何文件提到"我从瑞典来" / 出生地 / 移民决策
- **没有"我为什么做 X" 的自传式叙述**——R1 的他完全是"职业医生"公开形象，不展示个人故事

---

## 总结

R1 期间（2010-2017）的 Ekberg **公开可观察的决策**集中在 3 件事：
1. **职业方法论**：神经学 + 仪器辅助整脊 vs "cracking"（2011 起贯穿）
2. **公开教育形式**：把"健康讲座"做成长系列 + 病人 testimonial 录像（2011-05 起）
3. **品牌命名**：User Manual for Humans (2011) → Wellness For Life (2017-08 起)

而通常人们以为的"重磅决策"——**从奥运十项全能转行做整脊、创建 Health Champions、写书**——在 R1 100 文件里**完全找不到他本人讲述**。这些叙事都是 R2+ (2018+) 阶段才大量出现的内容。
