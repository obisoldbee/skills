# OB Skills Distribution

这是 `obisoldbee/skills` 的公共发行源码。先确定本次操作和包范围，再读取对应 wrapper、包内指引和当前 Git 状态。

## 源码位置

- 根文件由 `AGENTS.md`、`README.md`、`.gitattributes`、`.gitignore`、`.github/workflows/verify.yml`、`ROOT-MANIFEST.sha256`、`config/`、`scripts/` 组成。
- 每个顶层包是独立维护范围。嵌套研究 Skill 的入口在 `research-qa-plugin/skills/research-qa-orchestrator/`。
- 合集中的 canonical 路径为 `<collection>/GitHub`。从 `skills/src/` 进入时，解析到本仓库同名项后再运行 Git。
- wrapper 保存本地 docs、conversation、memory；公共源码留在本仓库。消费者直接指向 allowlist 声明的真源。
- `skills/src/` 恰好映射本仓库根的 `AGENTS.md`、`README.md`、`config`、`scripts` 四项。

## 操作选择

| 操作 | 做法 |
|---|---|
| Bootstrap | 克隆到指定 canonical 路径，核对来源，验证根文件与指定包 |
| Fresh collection | 运行 `project-conventions/scripts/initialize_skills_control_project.py` dry-run，审核后 apply，读回目录与投影 |
| Update-only | 运行指定包的 `scripts/update_shared_checkout.py`，验证固定候选包并快进后报告 |
| Device refresh | `scripts/link-macos.sh --sync-device` 或 Windows `-SyncDevice` 先生成计划；Unix 按已有授权 apply；Windows 更新与指定消费者安装分开执行 |
| Package maintenance | 修改用户指定包，运行该包 validator 和受影响检查 |
| Root maintenance | 修改根文件，重建 `ROOT-MANIFEST.sha256` 并验证 |
| Consumer installation | 扫描已有目标，按 `config/skill-exports.tsv` 和 `config/agent-paths.tsv` 逐个处理授权消费者 |

消费者创建使用本仓库安全链接工具。缺失 Agent 根、真实目录、错误链接或失效链接发生冲突时，保留现场并报告具体条目；已获冲突处理授权时，先保存旧内容再操作。安全创建失败后保留错误，按工具实际条件诊断。

仓库刷新核对 clean、attached、tracked、ahead=0 和可快进状态，用当前 verifier 检查固定候选根文件，再核对 refs、真实 index 和落地冲突。凭据、缓存、本机清单和私密数据留在发行源码外。

## 协作

读取直接进行。独立记录使用精确任务路径和不覆盖创建；并发 Git 写入各用独立分支和 linked worktree，保留并转入本任务需要的未提交输入。一个整合者更新 canonical 文件和共享索引。服务、数据库、端口和构建输出按实际资源协调。

在已授权范围内完成修正和受影响检查。提交、推送、发布、消费者变更或新增依赖按相应请求执行。

## 浏览器和文字

需要页面操作时，默认依次选用 Ego lite、Tabbit、系统默认或 harness 已记录常用浏览器、harness 内置浏览器。用户当次指定和需继续的已登录会话优先。使用对应浏览器自己的工具；固定执行器的产品依赖在包内说明。

入口和 Skill 只写会改变任务执行的事实、动作和条件。具体前置条件写清核对方法，删掉重复免责声明、假想误解和泛泛的完成状态口号。

## 验证

按改动范围选择检查。根文件改动执行下面两条命令；单包改动运行包内 validator。元数据与指引修改另用 skill-creator quick_validate，脚本和行为修改运行受影响测试。

```text
python3 -B scripts/verify_release.py . --rebuild-root-manifest
python3 -B scripts/verify_release.py .
```

根 verifier 检查根文件，包 validator 检查对应包。每个包的测试入口在其 README 或 scripts 中。报告实际改动、路径、验证结果和剩余阻塞。
