import re

with open('skillv2.16.md', 'r') as f:
    base = f.read()

# Strip subtitle file refs
pattern = r'\[20\d{6}\d{3}\.md[^\]]*\]'
base = re.sub(pattern, '', base)

new_findings = '''
## R17 新增 / 演化 (R17 阶段: 2026-02-08 → 2026-05-29, 25 文件, 最终轮)

### R17 新增核心论点 (≥3 次 = 新真信念)
- **Rivero 商业化升级** (R17 重大): Baker 在 4 个不同视频结尾反复 (逐字) 出现"saving lives, kicking butt, reversing disease"+ 双周就诊承诺, Rivero 链接从 R16 的 coaching 措辞升级到医疗级声明
- **MAHA/Trump 内部矛盾公开化** (R17 重大): 2026-03-01 视频中 Baker 承认 Trump 保护草甘膦国家利益 vs RFK 反草甘膦, Baker 站中间
- **新系列"What The Hell"启动** (R17 重大): 2 个长篇解释型视频 (Enhanced Games + Peptides), R17 标志 Baker 从"反应"转入"长科普"
- **Enhanced Games / Peter Thiel 反对** (R17 重大): Baker 第一次明确反对 Thiel 12 亿美元投资"无兴奋剂规定"的赛事, 称"society is being drugged", 引用自己 1996 年 USA Powerlifting drug-free T 恤
- **Peptides 立场** (R17 重大): Baker 自己试 BP-157 (Brigham Buhler 的 Ways to Well 诊所) = zero change; 学术中立立场; **新发现 RFK 正在 fast-track 一打 peptides 通过 FDA**
- **80 岁实证人物** (R17 重大): 具名 Dr. Kenton Brown (退休精神科医生) USA Track & Field Masters 200m 29.7 秒, Baker 反驳"他在用 TRT/peptides", 承诺自己 60 岁参加 master track
- **Carnivore 流失内部对话** (R17 重大): 3 视频 (Stopped Working / Everyone's Leaving / Why I Cheated) 构成挽留
- **"Woke Countries Top 10"国际排名** (R17 重大): 丹麦 #1, 瑞典 #2 (每周 < 350g 熟肉), Baker 称"the whole Nordic portion has gone nuts"
- **80% Americans + Bikman 引用** (R17 重大): Baker 第一次直接引用 Ben Bikman 的 Why We Get Sick + 主动引用 ApoB (立场微调)
- **Mr. Beast Future Chicken 反对** (R17 重大): Upside Foods 2 亿美元投资, 10-30 万磅产量 = "not even 1% of 1% of 1%", 论据"shifting the burden from chicken to other animals"
- **30 天 carb 重引入自实验** (R17 关键): 承认"gained 10 lb + belly fat + tendonitis", 但全程不用 "I was wrong" 而是 "I cheated"
- **Anti-longevity 产业** (R17 全新): Bryan Johnson + Dave Asprey + 反对 longevity industrial complex
- **"Moderation 是最差建议"** (R17 新)
- **Anti-GLP-1 pharma 控制** (R17 全新): Baker 用"profitable sheep" + "trillion-dollar industry" 直接攻击
- **RFK 精神分裂症治愈声明力挺** (R17 重大): 但本人未直接跟 RFK 谈过

### R17 新增术语
- **Revere App** (R17 重大 Rivero 产品定型): + 健康教练 + 医生监督复合 SaaS
- **"Diet is step one, correction is step two"** (R17 Rivero 标准化方法论)
- **Baker 每周 1-2 时段视频会议投入** (R17 Rivero)
- **"Woke Countries Top 10"** (R17 国际排名)
- **"Mr. Beast Future Chicken"** (R17)
- **Brigham Buhler + Ways to Well 诊所** (R17 BP-157 试用)
- **Anti-longevity industrial complex** (R17)
- **"Exposing" + "Scam" + "Woke"** (R17 新反建制词矩阵): 替代 R15 的 BS+garbage+ridiculous
- **Bryan Johnson + Dave Asprey** (R17 明确点名 "lifespan-extension 骗子" 二人组)
- **Enhanced Games 2026 Las Vegas** (R17)
- **Peter Thiel $1.2B** (R17)
- **Upside Foods $200M** (R17)
- **Monsanto $17B 赔偿** (R17)
- **30 天 carb 重引入** (R17)
- **"Exposing the Longevity Guru Scam"** (R17 标题)
- **"What The Hell are Peptides?"** (R17 新系列)
- **"What The Hell Are The Enhanced Games?!"** (R17 新系列)
- **"What The Hell is Glyphosate?"** (R17 新系列)
- **St. Petersburg, Florida** (R17 重大新居住地)

### R17 新盟友 / 新敌人
- **新盟友 (R17 重大)**:
  - **Amber O'Hearn** (R17 "my friend" + 营养充足性论文)
  - **Chris Palmer** (R17 关键升级: Baker 声称"我先于他写过相关主题" + "carnivore community 可能影响了他的思想形成")
  - **Jen Basuki + David Basuki** (R17 资助数百万美元研究)
  - **Ben Bikman** (R17 "my friend" + "Why We Get Sick" 书 + ApoB 引用)
  - **Andrea Craasc** (R17 波兰 carnivore 医生 + 肠道研究)
  - **Tommy Wood** (R17 代谢灵活性, "my friend")
  - **Mickey Ben-Dor + Rainer Barkai + Ralph Sirtoli** (R17 2021 人类 trophic level 研究)
  - **Dr. Kenton Brown** (R17 80 岁 USA Track & Field Masters 200m 29.7 秒)
  - **Brigham Buhler** (R17 Ways to Well 诊所, BP-157)
- **新敌人 (R17 重大)**:
  - **Bryan Johnson** (R17 Blueprint, $1M "Project Blueprint", "the ultimate in arrogance")——R17 专门做了一期 "Exposing the Longevity Guru Scam"
  - **Dave Asprey** (R17 Bulletproof, "Living to 180" + "300 supplements a day")——与 Johnson 并列为"lifespan-extension 骗子"二人组
  - **GLP-1 / Mounjaro 制药产业** (R17 "profitable sheep" + "trillion-dollar industry")
  - **Peter Thiel** (R17 Enhanced Games $1.2B)
  - **Upside Foods** (R17 Mr. Beast Future Chicken $200M)
  - **Monsanto** (R17 $17B 赔偿)
  - **Trump 保护草甘膦** (R17 站中间 vs RFK 反草甘膦)

### R17 立场演化 (后轮覆盖前轮)
- **搬到 St. Petersburg, Florida** (R17 重大): "actually moving here"
- **Anti-longevity 产业** (R17 重大): "0% 活到 150", Bryan Johnson + Dave Asprey
- **Enhanced Games 反对** (R17 重大): "society is being drugged"
- **Peptides 学术中立** (R17 重大): Baker 自己试 BP-157 = zero change
- **RFK 精神分裂症治愈声明力挺** (R17 重大)
- **ApoB 引用** (R17 立场微调): 主动引用 Ben Bikman 的 Why We Get Sick + ApoB
- **R17 智识叙事核心转变** (R17 重大):
  - R16 "我们赢了第一阶段, 我们要实操"
  - R17 "anti-longevity 骗子 + 反对 GLP-1 pharma 控制 + 强化 carnivore 历史/科学深度 + 扩展到 performance enhancement" 五层同步扩张
- **R17 是 R01-R17 的最终轮** (R17 重大结构性): Baker 智识叙事从"自下而上的倡导者"演化为"全维度反主流 + 智识影响源(对 Palmer) + 政府盟友 + 性能增强开放"复合型人物
- **从"我推荐"变成"我试过"的叙事跃迁** (R17): 30 天 carb 重引入自实验

### R17 决策变化
- **搬到 St. Petersburg, Florida** (R17 重大新居住地)
- **新书仍在写但无书名/出版日** (R17 延续 R16)
- **Rivero 拼写不统一** (R17 延续): Rivero / Revere / Rivera 三个, 正式名 = Rivero, rivero.com
- **母亲南非** (R17 重大新家庭信号): R01-R16 0 命中
- **1988 UT 生物学位** (R17 重大): 1988 故事
- **1988 救人故事** (R17 关键新披露)
- **24-25 岁入伍** (R17 重大): R01-R16 0 命中
- **2026 计划首访澳大利亚** (R17 重大)
- **妻子乳糖不耐** (R17 重大新家庭信号)
- **儿子喝 A2 长高** (R17 重大新家庭信号)
- **体重 248** (R17 重大)
- **60 岁减脂目标** (R17 重大)
- **Revere App + 健康教练 + 医生监督** 复合 SaaS (R17 Rivero 产品定型)
- **"Diet is step one, correction is step two"** 标准化方法论 (R17 Rivero)
- **Baker 每周 1-2 时段视频会议投入** (R17 Rivero)
- **30 天 carb 重引入自实验** (R17 关键): 承认"gained 10 lb + belly fat + tendonitis"
- **60 岁将入 masters 田径(USADA 药检)** (R17 重大): 6 个月专项训练 + 100m 目标
- **反对 Bryan Johnson $1M** (R17)
- **反对 Dave Asprey 300 补剂** (R17)
- **反 PED 立场** (R17 重大): + 1996 USA Powerlifting T 恤
- **Enhanced Games 2026 Las Vegas + Peter Thiel** (R17 重大)
- **Mr. Beast Upside Foods 培植肉反应视频** (R17 重大)
- **RFK 精神分裂症治愈声明力挺** (R17)
- **RFK vs Trump 草甘膦** (R17 重大)
- **Monsanto $17B 赔偿** (R17)
- **Rivero 病人 Dave 3 个月数据证言** (R17)
- **公然反对 longevity 工业** (R17)

### R17 表达 DNA 演化
- **`You know` 单文件密度达 R15 三倍以上** (R17 重大): R15=21/R16=31/R17=70 命中/文件, R15 假设 1 "天花板" 被两次推翻
- **`Uh`/`um` 犹豫符 R17 达历史新高** (R17): 33 命中/文件, 比 R16 高 30%+
- **确定性宣告** (`the truth is`/`to be clear`) **被震惊反应式** (`what the hell`) **+ 反建制揭露式** (`exposing`/`scam`/`woke`) 替代 (R17 重大)—— 庄重→反建制→震惊**第三阶段演化**
- **身份/职业词 4 倍增长** (R17 重大): R17 12 命中/文件 vs R16 抽样 2.7 命中/文件 —— **R17 最重要新趋势**: Baker 在政治/反建制视频中**主动调用"外科医生"身份作为权威背书**
- **领域术语文件间方差极大** (R17): 0-66 命中 —— 内容矩阵分裂为"领域型" (carnivore/beef/insulin 密集) 和"反建制型" (人物/事件评论, 0 命中)
- **科学引用集中于"反驳型"** (R17): "Gut Myth Exposed" 占 63 命中, 33% —— 反驳反对意见时引用密集, 日常视频引用稀疏
- **新反建制语汇矩阵** (R17): `claims`+`scam`+`exposing`+`woke`+`ruining`+`deteriorating`+`dangerous` 替代 R15 的 BS+garbage+ridiculous
- **开场白制度化** (R17): `all right + 议题 + 嘉宾/事件` (100% 命中)
- **标题矩阵强政治化 + clickbait 化** (R17): 10 视频/24 标题 = 42% 属政治/反建制/震惊类
- **六件套标志节拍** (R17): `all right guys` 开场 + `you know` 填词 + `uh`/`um` 犹豫 + `all right, [so]` 议题起跳 + `Exposing/Woke/Scam` 反建制词 + `Dr./Doctor` 权威背书
- **R15 假设验证 (R17 终结)**:
  - R15 假设 1 "`you know` 天花板" → **被两次推翻** (R15→R16→R17 连续翻倍)
  - R15 假设 2 "`BS` 归零" → **被两次兑现**
  - R16 假设 "`right?` 退场" → **继续兑现**

### R17 新增对话模式
- **"Reacting To Mr. Beast's 'Future Chicken'"** (R17 唯一一条"逐句点评第三方视频"的反应式对话): 内含 32 段 `>>` 引文 + 即时反驳, 结构最接近 podcast 风格
- **"Exposing Why I Cheated on Carnivore"** (R17 首次完整呈现"短期试错 → 后悔 → 回归 carnivore"的实证闭环): 承认"gained 10 lb + belly fat + tendonitis", 但全程不用 "I was wrong" 而是 "I cheated"
- **"Exposing the Longevity Guru Scam"** (R17 首次直接点名批判 Bryan Johnson 和 Dave Asprey): 带观众笑声反馈, 段子结构多于证据结构
- **"The Day I Thought I Would Die"** (R17 9 分半的阿富汗战争创伤叙事): 首次出现"我被同事开口打断"的转述对白, "Fuck it"是 R17 唯一脏话
- **R17 缺席的模式** (R17):
  - 0 条 1v1 podcast / AMA / 现场被追问的视频
  - 0 条 "vs. opponent" 型辩论
  - 0 次 "I was wrong" / "I changed my mind" 字样
  - 0 次 "concede / fair point / good point" 让步词
- **R17 新引用的学者** (R17): Dr. Sabine Haza, Andrea Craasc, Dr. Kenton Brown, Dr. Tom Large, Dr. Jeff Parker, David Unwin

### R17 重大时间线补充 (基于本人亲口)
- **住院医地点 = Texas Tech University** (R17 重大补完): 骨科系主任 Eugene Dabezies 时期
- **出生地 = 德国** (R17 重大补完): 父亲美国空军, 约 1 岁离德
- **成长地 = Galveston, TX 海湾沿岸** (R17 重大补完)
- **2007 部署阿富汗 Bagram Airbase 6 周时遭遇自杀式爆炸** (R17 重大补完): 与 Dr. Tom Large 搭档, 他口误说 "2017" 但上下文为 2007
- **2023 Joe Rogan 出诊 = 颈椎 jiu-jitsu 伤 + Austin Ways to Well (Brigham Buhler) + BP-157 肽 1 个月无效** (R17)
- **Rivero 业务模式 = 远程医疗 + Revere app + 医师教练双轨 + 3 月 lab 周期** (R17): 他本人每周见患者 2 次
- **29 岁 (≈1996) 首破 700 lb 硬拉 = USA Powerlifting (前 American Drug-Free Powerlifting Association)** (R17 重大锁定)
- **carnivore 10 年** (R17 重大锁定): 2026-02/04/05 三次视频确认 = 2016 起点
- **R17 期间动态** (R17): 搬到 St. Petersburg, Florida ("actually moving here"); 新书仍在写但无书名/出版日; Rivero 拼写不统一 (Rivero/Revere/Rivera 三个, 正式名 = Rivero, rivero.com)
- **仍未发现** (R17 0 命中): 妻子姓名、Belize ranch、孩子姓名、TBH 全名、新书书名/出版社

### R17 决策对比表 (R01 → R17, 最终)
| 维度 | R01 | ... | R15 | R16 | R17 (2026-02-08 → 2026-05-29) |
|------|-----|-----|-----|-----|-------------------------------------|
| 商业形态 | meatheals.com | ... | Rivero Republic 股权众筹 + 全 50 州 | Rivero 商业模式 | **Rivero 商业定型: Revere App + 健康教练 + 医生监督复合 SaaS + "Diet is step one, correction is step two"** |
| 自我角色 | 倡导者 | ... | MAHA 公开认领 | + Trump 2.0 + RFK HHS "既肯定又悲观" | **+ 主动调用"外科医生"身份作为权威背书 + "我先于 Palmer 写过相关主题"** |
| 饮食 | carnivore | ... | Grass-fed 立场软化 | + Grass-fed "标签 misleading" | **+ 30 天 carb 重引入自实验 (承认"gained 10 lb + belly fat + tendonitis" 但全程不用 "I was wrong" 而用 "I cheated")** |
| 训练 | rowing | ... | 扣篮 2 年内 | + 公开年龄 58 + 腘绳肌伤 | **+ 60 岁将入 masters 田径(USADA 药检) + 100m 目标 + 体重 248 + 60 岁减脂目标** |
| 反方 | 反主流 + 反 vegan | ... | UnitedHealthcare CEO 谋杀事件 | + Dr. Joel Fuhrman + Dr. David Sinclair | **+ Bryan Johnson + Dave Asprey (anti-longevity) + Peter Thiel (Enhanced Games) + Upside Foods (Mr. Beast) + GLP-1 / Mounjaro pharma + Monsanto** |
| 媒体合作 | Joe Rogan | ... | MAHA 公开认领 | + 2025 饮食指南 Baker 评论 | **+ Enhanced Games 反对 + Mr. Beast 培植肉反应 + RFK 精神分裂症治愈声明力挺 + RFK vs Trump 草甘膦** |
| 盟友核心 | Saladino / Rogan / Feldman | ... | Stefansson + Owsley + Chris Palmer + Senator + Fetterman | + Dr. Rolo + Dr. Salisbury + Blake Donaldson + Anderson Couple + Brooke Rollins + Tom Massie + Earl Butz + Rafael de Cabo | **+ Amber O'Hearn "my friend" + Chris Palmer 关键升级 (Baker 自承影响) + Ben Bikman "my friend" + Why We Get Sick + Andrea Craasc + Tommy Wood + Mickey Ben-Dor + Dr. Kenton Brown** |
| 智识谱系 | Paleo Medicine Hungary | ... | Stefansson 50+ 年长程 carnivore | + Harvard 2021 carnivore study (2029 人) 升格 | **+ 2018 Stanford carnitine 研究 + Ben-Dor 2021 trophic level 论文 + Keck School of Medicine 蔬菜 vs 肺癌 + Carnivore gut microbiota** |
| 居住地 | California | ... | Medford, Oregon + Oklahoma 州议会 | + 2025 夏欧洲家庭行 | **搬到 St. Petersburg, Florida ("actually moving here")** |
| 家庭 | (无) | ... | Sophie 法国 Roubaix + 1996/97 布拉格 | + 2025 夏妻子同行欧洲 | **+ 母亲南非 + 1988 救人故事 + 24-25 岁入伍 + 2026 计划首访澳大利亚 + 妻子乳糖不耐 + 儿子喝 A2 长高** |
| 智识诚实度 | 高 | ... | "对政府没信心" 显式表达 | MAHA 一年后转冷静现实主义 | **+ 从"我推荐"变成"我试过"的叙事跃迁 (30 天 carb 重引入自实验) + ApoB 引用 (立场微调)** |
| 身体状态 | 健康 | ... | 体重 260 lb + 扣篮 2 年内 | + 公开年龄 58 + 腘绳肌伤 | **+ 体重 248 + 60 岁减脂目标 + 60 岁将入 masters 田径(USADA 药检) + 100m 目标** |
| 医学院校名 | (R01-R15 0 命中) | (R15 0 命中) | University of Texas Medical Branch (UTMB) 5 年 | (R16 延续) | **+ Texas Tech University 住院医 (Eugene Dabezies 时期, R17 补完)** |
| 出生地 | (R01-R15 0 命中) | (R15 0 命中) | (R16 0 命中) | (R16 0 命中) | **德国 (父亲美国空军, 约 1 岁离德) + Galveston, TX 海湾沿岸 (R17 重大补完)** |
| 新书 | (无) | (无) | (无) | 2025-12 在写新书 | **仍在写但无书名/出版日 (R17 延续)** |
| carnivore 起始 | (无) | ... | 2016 (R12/R15 确认) | (R16 强化) | **2016 起点 (2026-02/04/05 三次视频确认) + carnivore 10 年 (R17 重大锁定)** |
| 1996 USA Powerlifting | (R01-R15 0 命中) | (R15 0 命中) | (R16 0 命中) | (R16 0 命中) | **29 岁 (≈1996) 首破 700 lb 硬拉 = USA Powerlifting (前 American Drug-Free Powerlifting Association) (R17 重大锁定)** |
| 母亲身份 | (无) | (无) | (无) | (无) | **母亲南非 (R17 重大新家庭信号)** |
| 1988 故事 | (无) | (无) | (无) | (无) | **1988 UT 生物学位 + 1988 救人故事 (R17 关键新披露)** |
| 入伍年龄 | (无) | (无) | (无) | (无) | **24-25 岁入伍 (R17 重大)** |
| 政治/MAHA | (无) | ... | 投了 Trump + RFK HHS 部长任命庆祝 | + 2025 饮食指南评论 | **+ RFK 精神分裂症治愈声明力挺 + RFK vs Trump 草甘膦 (Baker 站中间) + Anti-longevity 产业 + 反对 Bryan Johnson + Dave Asprey** |
'''

if '## 关键金句' in base:
    new_content = base.replace('## 关键金句', new_findings + '\n## 关键金句')
else:
    new_content = base + new_findings

new_content = re.sub(r'  +', ' ', new_content)
new_content = re.sub(r' +\n', '\n', new_content)

with open('skillv2.17.md', 'w') as f:
    f.write(new_content)
print('skillv2.17.md written,', len(new_content), 'chars')
