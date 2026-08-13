# obisoldbee Skills

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
│   ├── media-creator/                        # true cross-Agent media generation router
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
├── media-creator/                            # stable local Project Root
│   └── src/media-creator                     # projection to GitHub package
└── skills/                                  # local collection-control project
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
python3 -B <collection>/GitHub/media-creator/scripts/validate_skill.py
python3 -B <collection>/GitHub/document-workspace/scripts/validate_package.py \
  <collection>/GitHub/document-workspace
```

Then preview and materialize the local collection:

```bash
python3 -B <collection>/GitHub/project-conventions/scripts/initialize_skills_control_project.py \
  <collection> --distribution-root <collection>/GitHub
python3 -B <collection>/GitHub/project-conventions/scripts/initialize_skills_control_project.py \
  <collection> --distribution-root <collection>/GitHub --apply
```

The initializer creates the routing files, complete `skills/` control project, stable `project-conventions/` wrapper, and member projection. It does not install the Skill into any Agent. Additional published packages such as `web-bookmark-intelligence`, `media-understanding`, `research-qa-plugin`, `media-creator`, and `document-workspace` require a separately authorized member-wrapper/index migration on each device; the fresh initializer does not invent those local members.

On macOS/Linux the projection is the relative link:

```text
project-conventions/src/project-conventions -> ../../GitHub/project-conventions
```

On Windows it is a directory junction to the final package path.

## Update one Skill

Updating does not rerun initialization or links:

```bash
python3 -B <collection>/GitHub/project-conventions/scripts/update_shared_checkout.py \
  <collection>/GitHub/project-conventions
```

The helper resolves the shared checkout, permits only a clean fast-forward, validates the requested package, reports before/after commits, and stops. Dirty, ahead, detached, diverged, or wrong-remote states fail closed. It does not turn a package update into repository-root publication work.

Git advances the repository as one commit, so bytes in other published packages may also advance. That does not authorize editing, installing, or governing their local wrappers.

## Agent installation

Agent installation is a separate explicit action. Exports are declared in [`config/skill-exports.tsv`](config/skill-exports.tsv), and target candidates are declared in [`config/agent-paths.tsv`](config/agent-paths.tsv).

Publication does not imply Agent exposure. For example, `document-workspace` is published and validated here but is not currently declared in `config/skill-exports.tsv`; adding a consumer link requires a separate explicit decision.

Cross-Agent packages can be scoped to the shared `agents` consumer so runtimes that already scan `~/.agents/skills` do not receive duplicate same-name brand-root links.

Scan one exact Agent and Skill first:

```bash
./scripts/link-macos.sh --agent codex --skill project-conventions
```

Apply only after reviewing the source and destination:

```bash
./scripts/link-macos.sh --apply --agent codex --skill project-conventions
```

Windows:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\link-windows.ps1 `
  -Agent codex -Skill project-conventions
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\link-windows.ps1 `
  -Apply -Agent codex -Skill project-conventions
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

The non-native media generation router is exported to every declared consumer. Codex-native generic image generation remains owned by the built-in `imagegen` Skill and bypasses this router:

```bash
./scripts/link-macos.sh --agent agents --skill media-creator
./scripts/link-macos.sh --apply --agent agents --skill media-creator
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
python3 -B media-creator/scripts/validate_skill.py
python3 -B -m unittest discover -s media-creator/tests -p 'test_*.py'
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
├── media-creator/
│   ├── SKILL.md
│   ├── agents/
│   ├── config/
│   ├── references/
│   ├── scripts/
│   └── tests/
└── document-workspace/
    ├── SKILL.md
    ├── agents/
    ├── references/
    ├── scripts/
    └── tests/
```
