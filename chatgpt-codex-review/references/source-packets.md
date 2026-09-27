# 源码路线与固定输入

输入是原始需求、项目指引、精确审查范围、真实源码版本、披露/上传/推送权限和验收项。先核实用户提供的仓库 URL 或项目登记关联；无 local remote 只说明本地未配置，不证明 GitHub 仓库不存在。用本地 Git 工具核实根、remote、HEAD、dirty 差异及 LFS/submodule；`scripts/route_source.py` 只是本地发现辅助，不能覆盖已核实的远端仓库证据。实际远端 commit 是否存在、网页是否有读取权限，由宿主工具/网页读回填入 evidence，不从本地 remote 地址猜测。选择和权限在 run 内复用，只有事实变化才重核。

## GitHub 默认路线

发现 GitHub remote 后固定完整 commit；默认优先 `origin`，需要其他 remote 时在路由输入显式填 `github_remote`，核实仓库身份。helper 输出标准、不含凭据的仓库 URL。`evidence.github` 的 `repository`, `commit`, `remote_has_commit`, `web_can_read`, `evidence_ref` 必须来自实际核查；两项 true 才 `ready`。缺少证据就是待核查，false 就是 GitHub 路线内的访问/发布问题。HTTPS remote 含认证信息时仅用于识别，不写进可分享结果。

本地没有对应 remote、但用户已给 GitHub 地址时，可在 evidence 填 `declared_github_url`，并在 `github` 证据中填 `repository_verified=true`、仓库身份、完整 commit 与真实 `evidence_ref`。未核实身份仍是 unknown。仅核实远端、没有可检查的本地 Git 工作树时，`working_tree_dirty=null`，不能当成本地工作树干净的证明。

工作树变动默认 `freeze_commit`，避免悄悄遗漏本次修改。确认仅是范围外差异时，可提供 `dirty_scope_disposition=excluded_from_review` 与 `dirty_scope_evidence_ref`，把被排除文件和原因记录在 run；审查范围内修改须先冻结新提交。固定 commit 链接、相关入口和原始需求一同发给 Web。GitHub 路线本身不授权 push、建库、公开或合并。已获本次推送授权时，按项目规则提交/推送新版本并核实远端 SHA；未授权时保留本地成果并准确说明待发布步骤。不拿旧远端 commit 审查新代码，不因访问失败改送整个 ZIP 或切 MCP。

复审请求指向新完整 commit 和 diff 入口，附真实本地测试回执、未验项、上一轮逐项处置与待复审点。完整原始源码仍通过固定仓库版本可取，摘要不能替代。已获准的补充附件可由 Luna 发送；它们不改变 GitHub 源码 route。

## 无 GitHub 仓库时的 MCP 路线

本地 Git 但无 GitHub remote、其他托管 remote 或确无 Git 仓库，使用宿主实际已配置的 MCP 内容访问。`evidence.mcp` 必须含 `configured=true`, `server`, `tool`, `version`, `snapshot_sha256`, `manifest_sha256`, `evidence_ref`；快照只覆盖用户允许的文件与原始要求，清单记录路径/大小/hash/来源。保存工具真实读取回执，证明 Web 端能访问本轮固定内容。未配置就报告接入信息缺口；不伪造服务、不自行部署新服务、不偷偷 ZIP 回退。

原始资料全部保留在允许边界内。GitHub/MCP 的文件可见性和网页实际读到哪些内容分别核实；一个本地 PASS 不能替代网页读回。任何路线都先排除凭据、Cookie、私钥和无关私人内容。来源自报 SHA 没有可信对照时只说本次接收计算，不能称与原件一致。网页输出的 ZIP/PNG/JSON 等独立遵守 [附件合同](state-contract.md)，由 Luna 真下载保存和验证；输出附件不是源码路线。
