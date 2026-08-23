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
- 无视觉宿主的默认单图路线是 `minimax-mmx-image`，使用 `$mmx-cli`；MiniMax-M3 direct 图片在 adapter 未显式绑定前保持 `needs_explicit_binding`。
- 历史火山图片独立 Skill 已退役；火山请求只按 `provider-routing.md` 的普通 Platform 或 Ark CLI 路线执行。

## 普通图片与表情包的宿主旁路/路由

- 当前宿主/模型已确认具备原生视觉并实际读到所需附件时，普通单图或多图的描述、理解、粗略读字、分类、核价或直接问答默认走 `host_native`，不因图片数量而隐式触发本 Skill。
- 多张普通图片不自动等于 `batch understanding`。只有用户明确要求批处理工作流、manifest、逐项结构化证据或媒体模型评测，才按批量专项任务进入。
- 用户明确点名本 Skill 时必须进入路由，但进入后仍优先使用已确认可用的 `host_native`；显式调用不等于指定外部 provider。当前宿主/模型不能读取本次附件或能力未知时也必须进入；不要把 `host_native` 写进 portable registry。
- 无视觉宿主收到本次单张图片，且用户要求描述、读图或回答图片问题时，“附图 + 要求理解”即授权该图片默认走 `minimax-mmx-image`，无需重复询问 provider 或普通单次调用成本。用户指定其他 provider/model 或禁止外发时覆盖默认。
- 该默认授权只覆盖本次图片和一次常规 MiniMax 识图；不覆盖批量、其他媒体、后续素材或失败后的其他 provider。MiniMax 未配置或失败时停止并请用户决定，不自动 fallback。
- 表情包同样先按当前宿主的实际附件能力判断。宿主已确认可读时走 `host_native`，即使用户显式进入本 Skill也不强制外部 provider；无视觉宿主未收到其他 provider 指令时仍默认 `minimax-mmx-image`。历史排名见 [benchmark-history-and-routing.md](benchmark-history-and-routing.md)，只作评测证据，不覆盖当前运行默认。
- 对低清、裁切、双关或缺少上下文的表情包，先输出可见角色、文字、视角、情绪线索和不确定项；不要自动切外部 provider 或 OCR，也不要把猜测写成梗的事实。
- OCR 只能在用户目标是转录、扫描文档、文本精确提取或 Akashic 正式入库确有需要时作为辅助；它不会在普通图片或表情包失败时自动成为 fallback。详见 [provider-routing.md](provider-routing.md) 与 [ocr-and-document-understanding.md](ocr-and-document-understanding.md)。
