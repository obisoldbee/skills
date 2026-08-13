# Image Understanding

## 任务分类

| 用户目标 | 路线类型 | 核心输出 |
| --- | --- | --- |
| 看懂照片、海报、截图或表情包 | holistic vision | 画面概述、主体、关系、文字、配图/颜色作用、不确定项 |
| 准确读字 | OCR-assisted vision | 原样文字、阅读顺序、疑似误读；整体含义单独输出 |
| 描述 UI/信息图布局 | layout understanding | 区域、相对位置、层级、箭头/连线、颜色编码、整体用途 |
| 找目标并给坐标 | grounding | 目标、bbox、confidence、坐标系 |
| 从 GUI 推导操作 | GUI understanding | 当前状态、可操作元素、顺序、风险，不直接点击 |
| 批量网页/收藏夹图片 | batch understanding | 逐图用途、与正文关系、重复/噪声、需要进一步 OCR 或视觉复核的项 |

## 人类可读结果

默认输出：

1. 画面概述。
2. 识别到的关键文字；不确定字明确标注。
3. 主体、位置、层级、配图、颜色和关系。
4. 整体含义与可能用途。
5. 不确定项或需要核对的外部事实。

不要把 `case_id`、provider 控制字段、JSON 大括号、`<|det|>`、bbox 或图片哈希直接展示成正文。需要坐标时，将 bbox 放在独立“布局/定位”字段；原始结果保留在证据入口。

## 正确性门槛

- 明显错字、主体误认、情绪反转、文化梗解释错误或无依据补全属于实质错误。
- 文字正确但忽略配图、颜色、箭头和相对位置，只能算 OCR，不算完整图像理解。
- OCR 适合核实可见文字，不替代整体语义。
- 表情包应额外判断视角、情绪极性、原梗、低清/裁切是否本身携带语义。

## 外部专项执行器

- `agnes-image` 使用包内 `scripts/providers/agnes_vision.py` 与 `agnes-2.5-flash`；输入必须是 provider 可读取的 URL，调用前仍需当前外发授权与 route check。
- MiniMax 快速单图使用 `$mmx-cli`；MiniMax-M3 direct 图片在 adapter 未显式绑定前保持 `needs_explicit_binding`。
- 历史火山图片独立 Skill 已退役；火山请求只按 `provider-routing.md` 的普通 Platform 或 Ark CLI 路线执行。

## 普通图片与表情包的独立默认/降级

- 单张已附、可读的普通照片或截图，仅需描述、理解、粗略读字或直接问答，且用户未点名本 Skill、外部 provider/model、精确 OCR、坐标、批量、证据产物或评测时，默认由 Codex 原生视觉直接回答，不触发本 Skill。
- 用户明确点名本 Skill，或任务涉及复杂信息图/布局、grounding、批量、外部模型选型或正式证据时，才选择已验证的 provider/profile；仍先做整体视觉理解，不先走 OCR。外部调用必须有当前请求对 provider、素材范围和成本边界的明确授权。
- 表情包先走 Codex 原生视觉。只有用户明确授权外部 provider 或要求历史 benchmark 复现时，才按 [provider-routing.md](provider-routing.md) 选择一个当前可检查的 route；历史排名见 [benchmark-history-and-routing.md](benchmark-history-and-routing.md)，不构成永久默认模型。
- 对低清、裁切、双关或缺少上下文的表情包，先输出可见角色、文字、视角、情绪线索和不确定项；不要自动切外部 provider 或 OCR，也不要把猜测写成梗的事实。
- OCR 只能在用户目标是转录、扫描文档、文本精确提取或 Akashic 正式入库确有需要时作为辅助；它不会在普通图片或表情包失败时自动成为 fallback。详见 [provider-routing.md](provider-routing.md) 与 [ocr-and-document-understanding.md](ocr-and-document-understanding.md)。
