# obisoldbee Skills

面向 AI Agent 的开源技能集合，覆盖项目治理、多 Agent 协作、研究资料获取、媒体理解与生成，以及文档工作流。每个 Skill 都有独立的入口、参考文档和验证方式，可按需要选用。

本仓库保存可分发的技能真源；本地项目记录、运行缓存和凭据应保存在仓库之外。不同 Agent 能否直接使用某个 Skill，取决于其技能加载方式、工具支持和该 Skill 的运行前提。

## 中文介绍

### 包含哪些能力

| Skill / 包 | 用途 |
|---|---|
| [project-conventions](project-conventions/) | 统一项目目录与治理入口；支持文件／目录范围写入准入、只读并发和独立 Git worktree 协作 |
| [project-handoff](project-handoff/) | 任务交接、多 Agent 调度、模型路由与执行回执；包含 Spark CLI 使用规范 |
| [document-workspace](document-workspace/) | 基于文件的文档组织、工作区治理与资料管理 |
| [web-bookmark-intelligence](web-bookmark-intelligence/) | 网页与书签内容采集、整理和研究输入处理 |
| [research-qa-plugin](research-qa-plugin/) | 研究问答编排与配套研究视角，按插件内的说明使用 |
| [paper-downloader](paper-downloader/) | 学术论文与 PDF 获取、下载验证和结果记录 |
| [media-understanding](media-understanding/) | 按宿主能力和任务需求选择图像等媒体理解路径 |
| [media-creator](media-creator/) | 跨 Agent 的媒体生成路由；包含 Agnes 图像／视频生成及参数校验 |
| [minimax-h3-prompt](minimax-h3-prompt/) | MiniMax H3 视频提示词与素材组织规范 |
| [buddy-travelling](buddy-travelling/) | Buddy 旅行任务的状态判断、交互流程和停止条件 |
| [others-manager](others-manager/) | 第三方开源仓库的获取、来源核对和本地维护 |

### 如何开始

1. 将仓库克隆到自己选定的位置，每台设备保留一个真源 checkout。
2. 打开目标包的 `SKILL.md` 或 `README.md`，确认适用任务、依赖、工具及设备／网络要求。
3. 根据所用 Agent 的加载方式，连接或安装需要的技能。仓库的共享链接脚本只处理明确允许的目标；Windows 消费者脚本目前仅支持扫描与计划，不支持 apply。
4. 使用前配置所需服务的凭据，避免将密钥、Cookie 或私人材料提交到 Git。修改技能后运行对应包的验证脚本。

项目并发采用协作式准入：同一目录下的不同输出文件可以并行写入，只读任务可以与写入并存；代码修改优先采用独立分支和 worktree。它依赖各 Agent 遵守项目入口规则，不是操作系统文件锁。已有项目若使用旧版本地准入助手，需要按 `project-conventions` 的升级说明单独更新。

下方保留英文目录布局、初始化、更新和验证说明，便于跨工具、跨设备复用。

---

Portable Git source for published Skill packages.

## Recommended local layout

Use one checkout per device and keep local project governance outside Git:

```text
<collection>/
├── GitHub/                                  # clone of this repository
│   ├── project-conventions/                 # true Skill source
│   ├── web-bookmark-intelligence/           # true Skill source
│   ├── media-understanding/                  # true Skill source
│   ├── research-qa-plugin/                   # true Agent Plugins package source
│   ├── paper-downloader/                     # true academic PDF acquisition source
│   ├── buddy-travelling/                     # true bounded Buddy travel workflow source
│   ├── media-creator/                        # true cross-Agent media generation router
│   ├── project-handoff/                      # true handoff/orchestration controller source
│   ├── others-manager/                       # true third-party checkout management source
│   ├── minimax-h3-prompt/                    # true MiniMax H3 prompt guidance source
│   └── document-workspace/                   # true file-based document governance source
├── project-conventions/                     # stable local Project Root
│   ├── docs/
│   ├── conversation/
│   ├── memory/
│   └── src/project-conventions              # projection to GitHub package
├── web-bookmark-intelligence/               # stable local Project Root
│   └── src/web-bookmark-intelligence        # projection to GitHub package
├── media-understanding/                      # stable local Project Root
│   └── src/media-understanding               # projection to GitHub package
├── research-qa-plugin/                       # stable local Project Root
│   └── src/research-qa-plugin                # projection to GitHub package
├── paper-downloader/                         # stable local Project Root
│   └── src/paper-downloader                  # projection to GitHub package
├── buddy-travelling/                         # stable local Project Root
│   └── src/buddy-travelling                  # projection to GitHub package
├── media-creator/                            # stable local Project Root
│   └── src/media-creator                     # projection to GitHub package
├── project-handoff/                          # stable local Project Root
│   └── src/project-handoff                   # projection to GitHub package
├── others-manager/                           # stable local Project Root
│   └── src/others-manager                    # projection to GitHub package
├── MiniMax-H3-prompt/                        # stable local Project Root
│   └── src/minimax-h3-prompt                 # projection to GitHub package
└── skills/                                  # local collection-control project
    └── src/
        ├── AGENTS.md -> ../../GitHub/AGENTS.md
        ├── README.md -> ../../GitHub/README.md
        ├── config -> ../../GitHub/config
        └── scripts -> ../../GitHub/scripts
```

This avoids copied package trees and nested paths such as `project-conventions/src/skills/project-conventions`.

## Fresh initialization

Clone directly into the final shared Repository Root:

```bash
mkdir -p <collection>
git clone https://github.com/obisoldbee/skills.git <collection>/GitHub
python3 -B <collection>/GitHub/scripts/verify_release.py <collection>/GitHub
python3 -B <collection>/GitHub/project-conventions/scripts/validate_package.py \
  <collection>/GitHub/project-conventions
python3 -B <collection>/GitHub/web-bookmark-intelligence/scripts/validate_skill.py
python3 -B <collection>/GitHub/media-understanding/scripts/validate_skill.py
python3 -B <collection>/GitHub/research-qa-plugin/skills/research-qa-orchestrator/scripts/validate_research_qa.py plugin
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  <collection>/GitHub/paper-downloader
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  <collection>/GitHub/buddy-travelling
python3 -B <collection>/GitHub/media-creator/scripts/validate_skill.py
python3 -B <collection>/GitHub/project-handoff/scripts/validate_package.py \
  <collection>/GitHub/project-handoff
python3 -B <collection>/GitHub/others-manager/scripts/validate_package.py \
  <collection>/GitHub/others-manager
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  <collection>/GitHub/minimax-h3-prompt
python3 -B <collection>/GitHub/document-workspace/scripts/validate_package.py \
  <collection>/GitHub/document-workspace
```

`document-workspace` needs Python 3.12 or newer for fail-closed junction detection on Windows. Version 1 supports inventory, dry-run planning, and validation there, but intentionally refuses apply; its full mutation lifecycle is supported only on macOS/Linux with the guarded filesystem primitives described by the package.

Then preview and materialize the local collection:

```bash
python3 -B <collection>/GitHub/project-conventions/scripts/initialize_skills_control_project.py \
  <collection> --distribution-root <collection>/GitHub
python3 -B <collection>/GitHub/project-conventions/scripts/initialize_skills_control_project.py \
  <collection> --distribution-root <collection>/GitHub --apply
```

The initializer creates the routing files, complete `skills/` control project, its four projections to the repository-root `AGENTS.md`, `README.md`, `config/`, and `scripts/`, the stable `project-conventions/` wrapper, and its package projection. The control project never receives an aggregate `src/skills` link or package projections. It does not install the Skill into any Agent. Additional package directories present in a checkout, such as `web-bookmark-intelligence`, `media-understanding`, `research-qa-plugin`, `paper-downloader`, `buddy-travelling`, `media-creator`, `document-workspace`, `project-handoff`, `others-manager`, and `minimax-h3-prompt`, require a separately authorized member-wrapper/index migration on each device; the fresh initializer does not invent those local members or imply that uncommitted bytes are published.

On macOS/Linux the projection is the relative link:

```text
project-conventions/src/project-conventions -> ../../GitHub/project-conventions
```

On Windows it is a directory junction to the final package path.

For the four control-project projections, macOS/Linux uses the exact relative links shown above. Windows uses file symbolic links for `AGENTS.md` and `README.md` and directory junctions for `config` and `scripts`; initialization fails clearly instead of copying files when file-symlink creation is unavailable.

## Update one Skill

Updating does not rerun initialization or links:

```bash
python3 -B <collection>/GitHub/project-conventions/scripts/update_shared_checkout.py \
  <collection>/GitHub/project-conventions
```

The helper resolves the shared checkout, permits only a clean fast-forward, validates the requested package, reports before/after commits, and stops. Dirty, ahead, detached, diverged, or wrong-remote states fail closed. It does not turn a package update into repository-root publication work.

Git advances the repository as one commit, so bytes in other published packages may also advance. That does not authorize editing, installing, or governing their local wrappers.

## Refresh this device's public Skills

In the recommended collection layout, the local `skills/` Project Root manages and records repository-wide maintenance, while this checkout remains the only versioned file source. The exact requests “本机全量同步 Skills”, “更新 GitHub 并让本机 Agent 使用”, and “同步共享 Skill 根” use this repository-root operation, not a member package.

Run plan mode first. It performs no fetch and creates no link:

```bash
bash scripts/link-macos.sh --sync-device
bash scripts/link-macos.sh --sync-device --agent codex
```

Apply only when the request authorizes both the repository refresh and allowlisted public consumer reconciliation:

```bash
bash scripts/link-macos.sh --sync-device --apply
```

Windows (read-only plan; apply is currently unsupported):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\link-windows.ps1 -SyncDevice
```

The operation requires this exact checkout to be a clean attached `main` tracking `origin/main` with no local-ahead commits or Git operation in progress. Unix apply fetches and pins a full candidate commit, extracts only its root-managed files as data, and checks them with the currently running trusted verifier. It never executes the candidate verifier. Before fast-forwarding that exact SHA it checks landing conflicts across the whole update, rechecks HEAD/branch/upstream/remote/operation state and the real index's identity, bytes and entry flags, and uses `--no-overwrite-ignore`. Ignored local files are not permission to overwrite user content.

After updating, it rereads `config/skill-exports.tsv` and `config/agent-paths.tsv`, preflights every selected existing compatible Agent root, then creates only missing declared links. It skips missing Agent roots during an all-Agent run and fails for a specifically requested missing Agent. This is not a transaction across the repository and all consumers: a later consumer failure does not roll back a completed repository update.

It never creates another checkout or a missing Agent root, modifies a member package, changes export policy, replaces a real path or wrong/dangling link, touches local wrappers/indexes/records, or proves runtime discovery. Packages not declared in the public export allowlist are not installed by this operation.

## Agent installation

Agent installation is a separate explicit action. Exports are declared in [`config/skill-exports.tsv`](config/skill-exports.tsv), and target candidates are declared in [`config/agent-paths.tsv`](config/agent-paths.tsv).

Both link entry points require Python 3.11 or newer (Unix defaults to `python3`, Windows to `python`; `PYTHON` can select the executable). They share `scripts/consumer_paths.py` for filesystem-identity checks: a confirmed Skills collection, including its root, `skills/src`, members and aliases, is never a consumer. Case aliases follow the actual filesystem, not unconditional lowercasing. A standalone repository does not implicitly own its parent.

Unix apply requires exclusive directory-fd symlink creation: it binds the write to the verified parent and never follows an existing leaf as a container. A concurrent leaf causes failure; if the parent pathname changes at creation, the operation reports failure and may leave the authorized link in the original pinned directory, never following the replacement for cleanup. Inspect that directory before retrying. Platforms without this primitive fail closed; there is no fallback to `ln` or `New-Item`.

Windows supports read-only scan and existing-junction inspection only. Every `-Apply`, including `-SyncDevice -Apply`, stops before repository refresh or consumer writes until a handle-bound Windows creation primitive is implemented and verified.

Publication does not imply Agent exposure. `document-workspace` and `others-manager` are validated packages but are not currently declared in `config/skill-exports.tsv`; adding either consumer link requires a separate explicit decision.

Cross-Agent packages can be scoped to the shared `agents` consumer so runtimes that already scan `~/.agents/skills` do not receive duplicate same-name brand-root links.

Scan one exact Agent and Skill first:

```bash
./scripts/link-macos.sh --agent codex --skill project-conventions
```

Apply only after reviewing the source and destination:

```bash
./scripts/link-macos.sh --apply --agent codex --skill project-conventions
```

Windows scan:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\link-windows.ps1 `
  -Agent codex -Skill project-conventions
```

The repository scripts derive each exported source from the current checkout, so consumers point directly to the declared path inside the matching `GitHub/<package>` scope when run from the recommended layout. They never create missing target parents or replace conflicts.

For the cross-Agent web package, use the shared consumer id:

```bash
./scripts/link-macos.sh --agent agents --skill web-bookmark-intelligence
./scripts/link-macos.sh --apply --agent agents --skill web-bookmark-intelligence
```

The multimodal router is scoped to the Codex consumer:

```bash
./scripts/link-macos.sh --agent codex --skill media-understanding
./scripts/link-macos.sh --apply --agent codex --skill media-understanding
```

The research QA plugin exposes one first-level Skill for the Codex consumer:

```bash
./scripts/link-macos.sh --agent codex --skill research-qa-orchestrator
./scripts/link-macos.sh --apply --agent codex --skill research-qa-orchestrator
```

Paper Downloader is exported to the shared `.agents` root plus the explicit Codex, MiniMax, and WorkBuddy roots. Scan and apply each exact consumer separately:

```bash
./scripts/link-macos.sh --agent agents --skill paper-downloader
./scripts/link-macos.sh --apply --agent agents --skill paper-downloader
./scripts/link-macos.sh --agent codex --skill paper-downloader
./scripts/link-macos.sh --apply --agent codex --skill paper-downloader
./scripts/link-macos.sh --agent minimax --skill paper-downloader
./scripts/link-macos.sh --apply --agent minimax --skill paper-downloader
./scripts/link-macos.sh --agent workbuddy --skill paper-downloader
./scripts/link-macos.sh --apply --agent workbuddy --skill paper-downloader
```

The non-native media generation router is exported to every declared consumer. Codex-native generic image generation remains owned by the built-in `imagegen` Skill and bypasses this router:

```bash
./scripts/link-macos.sh --agent agents --skill media-creator
./scripts/link-macos.sh --apply --agent agents --skill media-creator
```

The handoff controller is exported only to Codex consumers:

```bash
./scripts/link-macos.sh --agent codex --skill project-handoff
./scripts/link-macos.sh --apply --agent codex --skill project-handoff
```

MiniMax H3 prompt guidance is exported through the shared `.agents` root:

```bash
./scripts/link-macos.sh --agent agents --skill minimax-h3-prompt
./scripts/link-macos.sh --apply --agent agents --skill minimax-h3-prompt
```

## Validation boundaries

Repository root:

```bash
python3 -B scripts/verify_release.py .
```

Named package:

```bash
python3 -B project-conventions/scripts/validate_package.py project-conventions
python3 -B project-conventions/scripts/test_inspect_projects_workspace.py
python3 -B project-conventions/scripts/test_lifecycle_workflows.py
python3 -B web-bookmark-intelligence/scripts/validate_skill.py
python3 -B -m unittest discover -s web-bookmark-intelligence/tests -p 'test_*.py'
python3 -B media-understanding/scripts/validate_skill.py
python3 -B -m unittest discover -s media-understanding/tests -p 'test_*.py'
python3 -B research-qa-plugin/skills/research-qa-orchestrator/scripts/validate_research_qa.py plugin
python3 -B -m unittest discover -s research-qa-plugin/skills/research-qa-orchestrator/tests -p 'test_*.py'
python3 -B research-qa-plugin/skills/research-qa-orchestrator/bundled/verify_bundled.py
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" paper-downloader
python3 -B -m unittest discover -s paper-downloader/scripts/tests -p 'test_*.py'
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" buddy-travelling
python3 -B -m unittest discover -s buddy-travelling/tests -p 'test_*.py'
python3 -B media-creator/scripts/validate_skill.py
python3 -B -m unittest discover -s media-creator/tests -p 'test_*.py'
python3 -B project-handoff/scripts/validate_package.py project-handoff
python3 -B -m unittest discover -s project-handoff/tests -p 'test_*.py'
python3 -B others-manager/scripts/validate_package.py others-manager
python3 -B -m unittest discover -s others-manager/tests -p 'test_*.py'
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" minimax-h3-prompt
python3 -B document-workspace/scripts/validate_package.py document-workspace
python3 -B -m unittest discover -s document-workspace/tests -p 'test_*.py'
```

`ROOT-MANIFEST.sha256` intentionally lists only root-owned files. Root verification does not validate package contents. A filesystem link also does not prove that an Agent discovered, loaded, or executed a Skill; verify that in a fresh Agent task.

## Repository structure

```text
.
├── .github/workflows/verify.yml
├── AGENTS.md
├── README.md
├── ROOT-MANIFEST.sha256
├── config/
├── scripts/
├── project-conventions/
│   ├── SKILL.md
│   ├── agents/
│   ├── assets/
│   ├── references/
│   └── scripts/
├── web-bookmark-intelligence/
│   ├── SKILL.md
│   ├── fixtures/
│   ├── references/
│   ├── scripts/
│   └── tests/
├── media-understanding/
│   ├── SKILL.md
│   ├── config/
│   ├── references/
│   ├── scripts/
│   └── tests/
├── research-qa-plugin/
│   ├── plugin.json
│   ├── README.md
│   └── skills/research-qa-orchestrator/
├── paper-downloader/
│   ├── SKILL.md
│   ├── agents/
│   ├── references/
│   └── scripts/
├── buddy-travelling/
│   ├── SKILL.md
│   ├── agents/
│   ├── scripts/
│   └── tests/
├── media-creator/
│   ├── SKILL.md
│   ├── agents/
│   ├── config/
│   ├── references/
│   ├── scripts/
│   └── tests/
├── project-handoff/
│   ├── SKILL.md
│   ├── agents/
│   ├── references/
│   ├── scripts/
│   └── tests/
├── others-manager/
│   ├── SKILL.md
│   ├── agents/
│   ├── references/
│   ├── scripts/
│   └── tests/
├── minimax-h3-prompt/
│   ├── SKILL.md
│   ├── agents/
│   └── references/
└── document-workspace/
    ├── SKILL.md
    ├── agents/
    ├── references/
    ├── scripts/
    └── tests/
```
