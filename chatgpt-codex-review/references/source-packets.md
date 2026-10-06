# 审查材料路线与固定输入

输入为原始需求、项目指引、完整审查范围、真实文件版本、披露/上传权限和验收项。
代码、文档与研究资料都可以使用本地包，不要求资料项目先有 Git 或 MCP。
仅准备材料与实际网页 review 分开；复用当前任务已覆盖的打包/上传授权，不要求重复批准。

## 选择路线

使用 `scripts/route_source.py --project <project> --evidence <tool-observations.json>`。
`evidence.source_route` 可为 `auto`（默认）、`github`、`mcp`、`local_packet`。
显式路线优先；未指定时：

| 事实 | 结果 |
|---|---|
| 已核实 GitHub 仓库、固定版本且 Web 可读 | github |
| GitHub 存在但本轮修改未提交，或已证实远端/网页访问不可用 | local_packet，冻结当前授权范围原件 |
| 无 GitHub，且已有配置/真实读回支持的 MCP 快照 | mcp |
| 本地文档、其他托管或无可用 MCP | local_packet；未打包返回 packet_needed，继续准备包 |
| 用户指定本地打包上传 | local_packet；不让仓库/发布/MCP 状态阻挡 |
| 用户只许 GitHub 或 MCP，所选路线缺条件 | 报告该路线的真实缺口，不擅改用户约束 |

GitHub 探测 unknown 时查明；不能凭缺少 local remote 否定用户已给的仓库 URL。
用户已指定本地包时无需先查远端。初次自动选路和已发送 run 的绑定不同：后者不能原地换 source_route；
确需换路时冻结新 run，关联旧 run 和旧资料，沿用原网页对话及已有授权，不重发已发送消息。

## 本地打包上传

Controller 冻结 `<MATERIAL_ROOT>`、本轮 `<RUN_ROOT>`、完整文件清单和来源；输入只读，
输出是 RUN_ROOT 下不存在的独立目录。多个来源可由调用方在既有授权下按来源目录保留原件，
不得因打包方便遗漏原始要求、在范围内的未提交/未跟踪文件、规则、差异或必要测试证据。
目录选择不自动涵盖其中秘密或无关文件。清单中的排除项逐项说明原因，缺失材料不得伪装已收录。
Git 项目还需核对根、remote、HEAD、dirty、LFS 和 submodule；指针文件或 gitlink 不代表已包含对应原件。
本地包读取当前实际文件，不能只用 git archive HEAD 而漏掉本轮未提交修改。

将实际相对文件路径写到 selection.json，不递归盲打整个工作区。示例字段需绑定当前请求：

```json
{
  "scope": "本轮文档结论与对应规则原件的 review",
  "authority_ref": "当前用户要求网页复审这些材料的消息",
  "files": ["原始要求.md", "规则/任务书.md", "研究/结论.md", "验证/测试.txt"],
  "exclusions": [{"path": "缺失附件.pdf", "reason": "来源未提供下载权限；不声称已覆盖"}]
}
```

```bash
python3 -B <skill-root>/scripts/local_packet.py build \
  --root <MATERIAL_ROOT> --selection <RUN_ROOT/selection.json> \
  --output <RUN_ROOT/source-round-1>
python3 -B <skill-root>/scripts/local_packet.py verify \
  --archive <RUN_ROOT/source-round-1/source.zip> \
  --manifest <RUN_ROOT/source-round-1/SOURCE_MANIFEST.json>
```

helper 不执行上传，拒绝现有输出目录、越界/链接/重复路径及明确的凭据文件名；不会代替内容披露审查。
ZIP 内为 `files/<原相对路径>` 的原字节及 SOURCE_MANIFEST.json；外部清单与内部清单相同，
逐文件记录 bytes/SHA-256。打包时源文件变化或校验不一致就失败，重新冻结一致版本后继续。
不覆盖旧包。helper 校验实际 ZIP/清单，返回 `ready_to_upload`、`uploaded=false`、
`web_read_verified=false` 和 source binding；这三项不能混写成 review 完成。

将输出路径交给 route helper：

```json
{
  "source_route": "local_packet",
  "local_packet": {
    "archive_path": "<absolute RUN_ROOT/source-round-1/source.zip>",
    "manifest_path": "<absolute RUN_ROOT/source-round-1/SOURCE_MANIFEST.json>"
  }
}
```

route helper 会重新读回实际文件，不接受仅自报一个 hash；`source_id=packet:<archive_sha256>`，
`source_binding` 精确包含 `archive_sha256`、`manifest_sha256`。绝对本地路径与验证回执另存，
不把它们当作 Web 可访问 URL。若运行主机不同，Luna 先核验其可读的同一包字节。

Luna 使用已验证浏览器能力上传 source.zip，可附清单便于查阅；UI 核对文件名、上传完成，
发送后核对本轮消息附件。保存 `source_upload` 回执：archive_sha256、manifest_sha256、
archive_name、upload_complete=true、evidence_ref；证据必须来自真实上传与读回，不得从本地 PASS 推导。
未知发送/上传状态先核对原消息和草稿，不能重复上传/提交。请网页 reviewer 先列实际可读原件、
清单与缺口，再分析；需要工具展开 ZIP 时核实实际支持，不能把上传卡片当已阅读。
完整覆盖 assessment 还需绑定本轮 `source_readback_id` 与实际内容读取证据 `source_readback_ref`。

大小/格式不支持时，在同一授权范围分批传原件，维护覆盖全部输入的总清单与每批摘要，
记录实际上传表示与原 packet 的映射；不能把“摘要包”冒充完整包。当前 helper 的 source_upload
结构只验证单个原 ZIP 上传；分批路径保留原件和回执后扩展相应合同，不能伪造单包上传成功。
修复后重新打包、验证新 hash/清单，产生新 source 身份；旧网页意见不能验收新版本。

## GitHub 路线

使用实际核实的 remote/用户给出的仓库身份和完整 commit。evidence.github 包含 repository、commit、
remote_has_commit、web_can_read、evidence_ref；两项 true 才 ready。本地 remote 或 commit 不证明网页可读。
用户给 URL 但本地无对应 remote 时，使用 declared_github_url，加 repository_verified=true 和真实证据。

自动路线下当前修改可直接打包；显式 GitHub 路线须冻结新提交并按已有授权发布。
仅范围外 dirty 变动可用 dirty_scope_disposition=excluded_from_review 与 dirty_scope_evidence_ref 排除。
不得用旧远端版本验当前未提交文件。无推送授权不强迫用户授权发布；本地上传有独立的正式分支。
补充附件不会悄悄改变当前已发送 run 的源码身份。

## MCP 路线

只用真实已配置且可供网页读取的内容快照。evidence.mcp 包含 configured=true、server、tool、version、
snapshot_sha256、manifest_sha256、evidence_ref，范围清单记录路径/大小/hash/来源，并保留原文读取证据。
默认选路缺少 MCP 就继续本地打包，不把安装/部署服务作为 review 前置要求。
用户明确只许 MCP 时才保留 mcp_connection_needed；不伪造连接或自行公开文件服务。

三种路线都保存完整原始材料，记录已知缺口；源码/资料可见与 Web 实际读取分别核实。
网页返回的报告/ZIP/PNG/JSON 是输出附件，继续由 verify_artifacts.py 按独立附件合同验证。
