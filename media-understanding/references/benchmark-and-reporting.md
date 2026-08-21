# Benchmark And Reporting

Benchmark 是可选模式，不是每次媒体理解的必经流程。

## 本 skill 内置的 runner、HTML、评分与历史入口

不要单独安装或调用 `visual-model-benchmark`。本 skill 已内置比赛的最小可执行模块：

- `scripts/validate_benchmark.py`：校验 immutable manifest、participant×case exact union、重复、遗漏与终态；不调用 provider。
- `scripts/build_review_matrix.py`：从 manifest 和 normalized results 生成自包含宽屏 HTML；不调用 provider。
- `scripts/validate_human_rankings.py`：校验前三名排名并复算 3/2/1 榜单；不调用 provider。
- [benchmark-runner-architecture.md](benchmark-runner-architecture.md)：adapter、证据隔离与停止规则。
- [benchmark-human-ranking.md](benchmark-human-ranking.md)：人工前三名评分、覆盖率与盲评规则。
- [benchmark-history-and-routing.md](benchmark-history-and-routing.md)：已封存的 VU01–VU10、OCR 和表情包任务族结论，以及需要重新评估的套餐状态。

这些模块只在用户明确要求比较、比赛、回归或更新默认时使用；结构/报告脚本可以本地运行，任何 provider 调用仍需要当前授权。无视觉宿主的单图 MiniMax 默认授权只覆盖一次常规识图，不自动授权 benchmark 的重复或多 provider 调用。

## 触发条件

仅当用户要求以下任一目标时进入：

- 比较多个模型/provider；
- 选择或更新默认路线；
- 对新模型做回归；
- 追加参赛者或案例；
- 生成横评/人工打分页面。

## 执行流程

1. 按 [benchmark-contract.md](benchmark-contract.md) 固定 case manifest、媒体 SHA-256、prompt version、participant/profile 和执行政策。
2. 读取已有结果，只运行缺失的 participant×case；不重跑已验证 success。
3. 每个 participant 调用所属媒体赛道的 provider adapter。URL、key、并发、重连和 payload 均来自该 provider profile；不自动 fallback。
4. 每次尝试立即保存 raw artifact。成功结果写原文和可读投影；失败写 failure class、retry count 与证据指针。
5. 用 `python3 scripts/validate_benchmark.py manifest.json normalized/results.json` 校验 exact union、重复、遗漏与终态。
6. 用 `python3 scripts/build_review_matrix.py --manifest manifest.json --results normalized/results.json --output review/visual-output-review.html` 生成自包含宽屏 HTML。
7. 用户在页面完成每个 case 的前三名后导出 JSON；用 `python3 scripts/validate_human_rankings.py rankings.json --expected-cases N` 复算 3/2/1 榜单。
8. 按 [evaluation-policy.md](evaluation-policy.md) 把正确性、质量、连接可用性、模型返回可靠性、机器可用性与成本分开，最后写回按 `task_family` 限定的路由决定和有效期。

这三个脚本已直接随 `media-understanding` 交付，不需要再依赖相邻 helper skill。它们只校验、投影和生成报告，不调用 provider；真正的模型请求仍由各 provider adapter 执行。

## 产物目录约定

```text
benchmark-run/
├── manifest.json
├── raw/<participant_id>/<case_id>/...
├── normalized/results.json
├── review/visual-output-review.html
├── review/rankings.json
└── decision.md
```

## HTML 形态

- 普通批量图片：卡片或表格即可，不强制打分。
- 图片/OCR 比赛：行=模型、列=图片的宽屏矩阵；图片放大、摘要格、唯一“全文”入口、显式原始证据、失败标记、盲评和前三名。
- 宽屏矩阵随页面自然展开，不设置内部纵向高度上限；避免矩阵内部滚动条遮挡更多模型行。
- 可读层隐藏 JSON 控制字段和 OCR det/bbox；原始输出不删除，只在用户主动查看原始证据时展示。
- 视频：播放器 + 时间线 + 关键帧/字幕，不使用图片矩阵替代。
- 音频：播放器 + 波形/时间轴 + 转写/说话人/纪要，不使用图片矩阵替代。

## 决策顺序

1. 明显识别错误或幻觉直接 OUT。
2. 区分连接失败与模型返回失败；按已声明的有限重连后统计可靠性。
3. 看人工偏好与任务族质量。
4. 再比较价格、套餐系数、额度池、剩余量、到期日和机会成本。
5. 默认模型必须绑定 `task_family` 与有效期。
