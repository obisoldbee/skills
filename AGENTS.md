# OB Skills Distribution Repository

Background:
This is the owned portable Git source for public Skill packages. A package present only in an unpushed local commit is not remotely published. In the standard local Skills Project Collection, clone this repository exactly once as `<collection>/GitHub`.

Materials:
- `<checkout-root>` is the real Git worktree that owns this file. The same bytes may be read through `<collection>/skills/src/AGENTS.md`; that projection path is not a Git root.
- Root-owned publication files are `.gitattributes`, `.github/workflows/verify.yml`, `.gitignore`, `AGENTS.md`, `README.md`, `ROOT-MANIFEST.sha256`, `config/`, and `scripts/`.
- Each top-level Skill package, such as `project-conventions/`, `web-bookmark-intelligence/`, `media-understanding/`, `research-qa-plugin/`, `paper-downloader/`, `buddy-travelling/`, `media-creator/`, `project-handoff/`, `others-manager/`, `minimax-h3-prompt/`, or `document-workspace/`, is an independently validated managed scope.
- A local collection wrapper, control project, member records, and Agent links live outside this repository.

Constraints:
- Resolve the lifecycle before any write: clone/bootstrap, update-only, package maintenance, or repository-root maintenance.
- When entered through a `skills/src/{AGENTS.md,README.md,config,scripts}` projection, resolve the matching physical entry under `<collection>/GitHub` before running Git or repository validation.
- Do not initialize Git at the surrounding Project Collection root.
- Do not clone this repository into a member package path when the target uses the shared collection profile; use the exact collection-local `GitHub` path.
- Do not create application-data or user-global source directories in place of a user-selected target.
- A repository-root manifest PASS verifies only root-owned files. Validate a named package separately.
- Package-change authority is not implied by repository-root maintenance authority.
- Update-only may fast-forward this checkout and validate one named package; it must not initialize wrappers, edit local indexes/records, scan siblings, or relink Agent consumers.
- Repository-wide device refresh is a separate root operation. It may fast-forward this one checkout and reconcile only missing links declared by the repository-root allowlists in already existing Agent roots; it must not modify member packages, local wrappers, indexes, records, or export policy.
- Never create missing Agent parents or replace real paths, wrong links, or dangling links without explicit conflict-preservation authority.
- Root refresh validates candidate files as data with the current trusted verifier, checks whole-update landing conflicts, freezes the actual index as well as Git refs, and fast-forwards only the validated SHA without overwriting ignored files.
- Consumer checks use filesystem identities for the confirmed collection boundary and its aliases. Unix creation requires the directory-fd helper; Windows apply is unsupported and must stop before any repository update or consumer write. Do not substitute `ln` or `New-Item` after a safe-create failure.
- Do not expose credentials, caches, local inventories, or machine-specific paths.
- Base completion claims on current Git/disk/link readback and reply in the user's language.

Lifecycle routing:

1. **Clone/bootstrap only**: clone to the exact named destination, verify Git identity, run root validation and the named package validator, report commit, and stop.
2. **Fresh shared Skills collection**: clone this repository as `<collection>/GitHub`, then run `project-conventions/scripts/initialize_skills_control_project.py` dry-run and apply from that checkout. It creates the collection overlay, the control project's four root-management projections, the stable member wrapper, and the member projection. It creates no Agent links.
3. **Update-only**: run the requested package's `scripts/update_shared_checkout.py`. It permits only clean, attached, ahead-zero fast-forward behavior, validates that named package, and stops.
4. **Device refresh**: for “本机全量同步 Skills”, run `scripts/link-macos.sh --sync-device` or `scripts/link-windows.ps1 -SyncDevice` without apply first. Supported Unix apply may update this checkout and create only missing allowlisted public Skill links in existing compatible Agent roots. Windows is plan/scan-only; report unsupported apply rather than attempting a fallback.
5. **Package maintenance**: modify only the explicitly authorized top-level package and run its validators/tests.
6. **Repository-root maintenance**: modify only root-owned files, rebuild `ROOT-MANIFEST.sha256`, verify it, and do not modify package content.
7. **Agent installation**: separately scan and apply only exact authorized consumers using the collection control scripts or this checkout's scoped link scripts.

Shared collection invariants:

```text
<collection>/skills/src/AGENTS.md -> ../../GitHub/AGENTS.md
<collection>/skills/src/README.md -> ../../GitHub/README.md
<collection>/skills/src/config    -> ../../GitHub/config
<collection>/skills/src/scripts   -> ../../GitHub/scripts

<collection>/GitHub/project-conventions                  # true source
<collection>/project-conventions/src/project-conventions # member projection
<agent-root>/project-conventions                         # direct consumer link to true source

<collection>/GitHub/web-bookmark-intelligence                  # true source
<collection>/web-bookmark-intelligence/src/web-bookmark-intelligence # member projection
<agent-root>/web-bookmark-intelligence                         # direct consumer link to true source

<collection>/GitHub/media-understanding                        # true source
<collection>/media-understanding/src/media-understanding       # member projection
<agent-root>/media-understanding                               # direct consumer link to true source

<collection>/GitHub/research-qa-plugin                         # true package source
<collection>/research-qa-plugin/src/research-qa-plugin         # member projection
<agent-root>/research-qa-orchestrator                           # direct link to first-level Skill

<collection>/GitHub/paper-downloader                            # true source
<collection>/paper-downloader/src/paper-downloader              # member projection
<agent-root>/paper-downloader                                   # direct consumer link to true source

<collection>/GitHub/media-creator                               # true source
<collection>/media-creator/src/media-creator                    # member projection
<agent-root>/media-creator                                      # direct consumer link to true source

<collection>/GitHub/project-handoff                             # true source
<collection>/project-handoff/src/project-handoff                # member projection
<agent-root>/project-handoff                                    # direct consumer link to true source

<collection>/GitHub/others-manager                              # true source
<collection>/others-manager/src/others-manager                  # member projection
# no Agent consumer export is declared for others-manager

<collection>/GitHub/minimax-h3-prompt                           # true source
<collection>/MiniMax-H3-prompt/src/minimax-h3-prompt            # member projection
<agent-root>/minimax-h3-prompt                                  # direct consumer link to true source
```

- The control project has exactly those four repository-root management projections. It has no aggregate `src/skills` link and no package projection.
- Unix member projection: relative symlink `../../GitHub/<package>`.
- Windows member projection: junction to the final absolute package path.
- Agent consumer links point directly to the true source, not through the member projection.
- A link proves filesystem state only, not runtime discovery or execution.
- `document-workspace/` is currently a published package without a collection wrapper or Agent export declaration. Do not invent either during unrelated maintenance.

Validation:

```text
python3 -B scripts/verify_release.py <checkout-root>
python3 -B scripts/test_repository_refresh.py
python3 -B scripts/test_consumer_boundaries.py
python3 -B project-conventions/scripts/validate_package.py <checkout-root>/project-conventions
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

For an authorized repository-root edit, use `--rebuild-root-manifest` and then verify again. For a package edit, do not rebuild the root manifest unless root-owned files also changed.

Output:
Report lifecycle, exact paths, before/after commit where relevant, validators, link/projection readback, stop boundary, and unresolved blockers. Distinguish cloned, Git-backed, projected, linked, discovered, and executed states.

Entry points:

| Path | Purpose |
|---|---|
| `README.md` | Bootstrap, update, validation, and linking overview |
| `ROOT-MANIFEST.sha256` | Digests for repository-root files only |
| `scripts/verify_release.py` | Offline root verifier and strict repository check/fast-forward gate |
| `scripts/link-macos.sh` | Scoped Unix Agent consumer link tool |
| `scripts/link-windows.ps1` | Read-only Windows Agent consumer junction scan; apply unsupported |
| `scripts/consumer_paths.py` | Shared identity-based consumer boundary and handle-bound Unix link creation |
| `project-conventions/SKILL.md` | Lifecycle and filesystem-governance package |
| `web-bookmark-intelligence/SKILL.md` | Receipted public-web and bookmark evidence package |
| `media-understanding/SKILL.md` | Multimodal task router and provider-binding package |
| `research-qa-plugin/plugin.json` | Agent Plugins v1 research QA package manifest |
| `research-qa-plugin/skills/research-qa-orchestrator/SKILL.md` | Audited five-stage research QA entry point |
| `paper-downloader/SKILL.md` | Lawful academic PDF acquisition and disk-receipt verification |
| `buddy-travelling/SKILL.md` | Bounded daily Buddy gift and travel workflow |
| `media-creator/SKILL.md` | Non-native cross-Agent image and video generation router |
| `project-handoff/SKILL.md` | Portable handoff and verified visible-task orchestration controller |
| `others-manager/SKILL.md` | Plan-gated management of independent third-party GitHub checkouts |
| `minimax-h3-prompt/SKILL.md` | MiniMax H3 input routing and prompt-authoring guidance |
| `document-workspace/SKILL.md` | Local-first document workspace lifecycle and evidence package |
