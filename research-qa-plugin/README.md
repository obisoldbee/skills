# research-qa-plugin

Agent Plugins v1 package for an audited five-stage research workflow:

1. lock the user's topic;
2. collect independent additions from eight fixed persona Skills;
3. query Akashic first, then lawfully acquire and independently audit literature;
4. send the full frozen 30-plus publication corpus to eight clean expert contexts and independently audit every output;
5. synthesize and independently audit the final candidate report.

The package exposes one first-level Skill, `research-qa-orchestrator`. The eight personas and Fuxi are manifest-bound internal materials; Fuxi is never invoked by this workflow.

## Validation

```bash
python3 -B skills/research-qa-orchestrator/scripts/validate_research_qa.py plugin
python3 -B -m unittest discover -s skills/research-qa-orchestrator/tests -p 'test_*.py' -v
python3 -B skills/research-qa-orchestrator/bundled/verify_bundled.py
```

The default bundled verifier validates the committed manifest/tree only and reports upstream comparison as `source_comparison: not_compared` with `sources_ok: null`. For a strict upstream comparison, supply both roots:

```bash
python3 -B skills/research-qa-orchestrator/bundled/verify_bundled.py \
  --require-source-match \
  --minimax-root <minimax-skills-root> \
  --claude-root <claude-skills-root>
```

Strict mode fails unless both roots exist and every declared component has identical names and content.

For a real candidate package:

```bash
python3 -B skills/research-qa-orchestrator/scripts/validate_research_qa.py destination --package <absolute-new-path>
python3 -B skills/research-qa-orchestrator/scripts/validate_research_qa.py run --package <absolute-reserved-package-path>
```

The destination command only preflights a nonexistent calendar path. The package must then be reserved through the Akashic v2 ordinary-submission workflow. Run validation is deliberately fail-closed: package-local receipts can establish structural consistency only, so a structurally complete run returns `ok: false`, `structural_validation_ok: true`, `runtime_execution_verified: false`, and `status: runtime_not_verified` with exit 3. It remains `pending` and cannot claim candidate success or formal absorption without independently verified host attestation outside the package.

## External dependencies

Real execution requires a live Akashic registry/rule, the separately registered `$paper-downloader` executor, eight independent author contexts, and independent semantic audit capacity. In this collection, the executor consumer must resolve directly to `GitHub/paper-downloader`; the wrapper projection and former `working-skills` path are not callable sources. A correct symlink/junction proves only `linked`: runtime discovery and every attempted acquisition require separate receipts. Author, auditor, integrator, and collector success also requires artifact-bound runtime operation receipts; Codex uses confirmed visible `create_thread` plus result readback. See `skills/research-qa-orchestrator/references/external-executors.md`.

Static validation checks package layout, retained receipt shape, and byte bindings. `discoverable_skills` is a layout result and `runtime_discovery_state` remains `not_evaluated`; neither proves that a consumer runtime loaded the plugin. For run packages, normalized discovery/operation/create-thread receipts are reported only as structurally validated receipt counts; runtime discovery and execution stay `runtime_not_verified`. Static validation also does not prove current provider availability, a provider call, plugin installation, or formal adoption. Synthetic PDFs, context strings, hidden subagent metadata, and package-local host-attestation claims cannot stand in for runtime execution evidence.

## Current-state reporting

Plugin validation reports source/runtime-tree validity separately from current Git `head_commit`, `runtime_tree_tracked`, and `package_dirty`. Those are live observations, not a checked-in status slogan: a clean checkout must report `package_dirty: false`, while a non-Git copy reports null commit/tracked/dirty values. Source presence, Git state, consumer link, runtime discovery, runtime execution, remote publication, and formal adoption remain separate claims.

## Publication boundary

This directory is the local canonical source inside the shared Git worktree.
Its presence in a checkout, and any local modifications, do not by themselves
prove that the current bytes were committed, pushed, or published. Review
[NOTICE.md](NOTICE.md) before any remote publication or redistribution of
bundled persona material.
