# OCR And Document Understanding

OCR/文档是独立任务轨，不是图像理解的低配替代品。先确认目标是逐字读取、版式还原、表格/公式、跨页结构，还是画面整体含义。

## 候选路线

| 目标 | 路径 | 选择条件 |
|---|---|---|
| 少量可见文字粗读 | `host_native` 会话旁路（非 route） | 当前宿主/模型已确认实际读取本次附件；明确标注为非归档粗读 |
| 精确 OCR、版式、坐标 | `local-ocr-document` | 当前任务已绑定并核验具体本地服务 |
| 火山生产 PDF 理解 | `volcengine-platform-responses-files` | 普通 Platform adapter、key/model 和授权已显式绑定 |
| 火山交互式 PDF 抽取 | `volcengine-arkcli-understand` → `doc-extract` | recipe 实际模型与认证已核对 |

本公共包不嵌入局域网 IP、端口或 token。本地 endpoint 是设备配置，必须在当前任务中显式绑定；同一 IP 也不代表共用 payload、token、并发或显存。

## 输入处理

- 读取真实 MIME、页数、文本层和图像层，不只看扩展名。
- 图片服务只接受图片时，逐页渲染并保留页码和源 PDF SHA；不要声称保留了跨页结构。
- 文档服务支持完整 PDF 时，把整份文档作为一个 case，避免跨页关系被拆散。
- 火山 PDF 底层合同是 Files API → active `file_id` → Responses `input_file`；小于 50MB 的一次性 PDF 也可使用 Base64/公网 URL。Ark CLI `doc-extract` 是同一数据面的包装层。
- 官方文档只明确证明 PDF；不要把其他扩展名推断为已支持文档格式。
- 不把本地路径、PDF 二进制或 token 发给只接受公网 URL 的服务。
- 数字、表格和公式保留原页位置证据并独立核验。

## 双层以上输出

1. `raw_artifact`：原始响应、bbox、Markdown、JSON 或 ZIP，不改写。
2. `readable_text`：按阅读顺序清理后的正文。
3. `layout_evidence`：页码、区域、坐标、表格/分栏/标题关系。
4. `semantic_interpretation`：只有任务要求整体理解时才生成，并引用具体页面证据。

OCR 成功不等于完成画面语义；视觉摘要也不能冒充逐字 OCR。endpoint 不可用时保存失败并停止，除非当前请求明确授权一个具体 fallback。
