# OB Skills Distribution Checkout

Background:
This public repository is a portable Skill distribution checkout. It is not a device's Projects Workspace, the local `obisoldbee-skills` Project Collection, or a mirror of member project wrappers.

Materials:
- `<checkout-root>` is the directory containing this `AGENTS.md`.
- Root-owned write allowlist: `<checkout-root>/.gitattributes`, `.github/workflows/verify.yml`, `.gitignore`, `AGENTS.md`, `README.md`, `ROOT-MANIFEST.sha256`, `config/agent-paths.tsv`, `config/skill-exports.tsv`, `scripts/link-macos.sh`, `scripts/link-windows.ps1`, and `scripts/verify_release.py`.
- Independently maintained packages: each top-level Skill directory, such as `project-conventions/`.
- User scope: only the exact checkout, current bootstrap root, final target, named migration sources, Skill, and Agent/consumer target named in the current request.
- `input/` boundary label: `<checkout-root>` and the exact user-named paths are read-only by default; there is no implied literal `input/` directory.
- `output/` boundary label: writes may affect only an exact user-authorized path; there is no default or implied literal `output/` directory.

Constraints:
- Treat repository-root files as the only writable publication scope governed by this root entry.
- Treat every top-level Skill package as read-only unless the user separately authorizes work in that package's own Project Root.
- Treat every path not explicitly listed in the root-owned write allowlist as outside root-maintenance write scope.
- Never infer package-change authority from `config/skill-exports.tsv`, repository membership, a generated manifest, or a broad request to refresh the repository root.
- Do not inspect unnamed old workspaces, siblings, Agent roots, or unrelated paths. Explicitly named migration sources remain in scope.
- Do not replace a user-specified checkout destination with a conventional global or application-data directory.
- When this checkout is inside a Project Root that will be moved, defer every Skill link/junction until the final source path exists.
- Do not create missing consumer parents or replace real paths, wrong links, or dangling links.
- Do not expose local paths, credentials, caches, private Skills, or device inventories.
- Base status claims only on current disk or Git evidence; mark unsupported facts as unknown and do not invent them.
- Reply in the user's language.
- Treat an explicit clone-inside-current-root, target-initialization, and named-source migration sequence as one full-initialization lifecycle, not several competing requests. If a required path is genuinely omitted or package-level write authority is absent, stop and ask one focused question before any write.

Ordering gate:
Before any write, the agent must resolve `<checkout-root>`, select exactly one lifecycle, verify its required paths and authority, and list the exact write set. Do not execute until all four checks pass. After execution, read back the changed paths, run only that lifecycle's validation, report the result, and stop.

Routing examples:
- "Clone this repository only" => clone/download only; run root verification and stop.
- "Clone under this current Project Root, initialize this target collection, and move these named roots into it" => named full initialization; continue after direct-loading the checked-out Skill, defer link work until final paths exist, and ignore unnamed siblings.
- "Update this existing checkout" => update-only; require a clean fast-forward, run root verification, and stop without package validation or relinking.
- "Refresh the repository README" => repository-root maintenance; `README.md` is writable, while every top-level Skill directory remains unchanged.
- "Update project-conventions" => package work, not root maintenance; stop unless the user separately authorizes that package's own Project Root.

Task:
Choose exactly one lifecycle and execute only that lifecycle:

1. Clone/download only: verify `ROOT-MANIFEST.sha256` with `python3 -B <checkout-root>/scripts/verify_release.py <checkout-root>`, report the observed checkout state, and stop.
2. Named full initialization: after cloning inside the user-named current Project Root, verify the checkout, read `project-conventions/SKILL.md` directly, initialize the named target, atomically migrate only the named sources, and propose one final-path Skill link. A fresh task is not required merely to read an explicitly named local Skill file.
3. Bootstrap-only with runtime installation: scan exactly one named Skill and one named Agent/target; apply a link only after explicit approval; read it back and stop for a fresh task.
4. Update-only for this checkout: allow only a clean fast-forward update plus the same root verification command; report before/after commits and stop without validating or modifying a member package.
5. Repository-root maintenance: modify only the exact user-authorized files in the root-owned write allowlist, run `python3 -B <checkout-root>/scripts/verify_release.py <checkout-root> --rebuild-root-manifest`, then run the same command without the flag to verify it. Preserve every unlisted path and stop without validating or modifying a member package. If either command fails, do not publish and report the exact failure.
6. Initialize a final project target with an already available Skill: follow that Skill's target lifecycle without repeating bootstrap.

For lifecycle 2, use the current Project Root's mapped `src/<repository-name>/` checkout unless the user supplied another exact child path. Read `project-conventions/references/lifecycle-workflows.md` and `project-conventions/references/migration-guide.md`. Snapshot hidden files and Git state, reserve incoming target names, and use the exact source-to-destination map already authorized by the user. Do not ask the user to choose unrelated archive/keep/delete options when both ends of a move were explicit. Before moving the active workspace, switch to a safe parent; if the host locks it, request only the necessary reopen-at-parent handoff. Link only after migration and final-path validation.

Output format:
Report the selected lifecycle, exact paths inspected or changed, observed evidence, validation performed, stop boundary, and any unresolved blocker. Distinguish proposed, executed, installed, discovered, and run states.

Success criteria:
- Only the named lifecycle and paths were touched.
- Root verification passed for clone/download-only, update-only, and repository-root maintenance work; root maintenance also rebuilt the manifest with the exact command above.
- No member package was modified by a repository-root maintenance task.
- A named full chain did not stop after clone or link a temporary source; clone-only and update-only stopped at their narrower boundaries.
- The task stopped at the lifecycle boundary without unrelated governance, relinking, or record creation.

Entry points:

| Path | Purpose |
|---|---|
| `README.md` | Human bootstrap and update workflows |
| `ROOT-MANIFEST.sha256` | Digests for repository-root files only |
| `scripts/verify_release.py` | Offline root-manifest and portability validation |
| `scripts/link-macos.sh` | Scoped macOS/Linux link scan and explicit apply |
| `scripts/link-windows.ps1` | Scoped Windows junction scan and explicit apply |
| `project-conventions/SKILL.md` | Package-owned lifecycle and filesystem-governance rules |
