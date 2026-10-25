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

## Runtime prerequisites

Real execution needs the live Akashic registry and rule, the registered `$paper-downloader`, eight independent author contexts, and independent semantic auditors. Resolve the downloader consumer directly to `GitHub/paper-downloader` and verify runtime discovery before collection. Preserve the original runtime operation result and readback for each author, auditor, integrator, collector and acquisition. Codex uses confirmed visible tasks. See [external-executors.md](skills/research-qa-orchestrator/references/external-executors.md).

Plugin validation checks layout, manifest hashes and the current Git observation. Run validation checks the retained receipt chain and artifact bytes. Record the validator’s actual `runtime_not_verified` result when independent host attestation remains unavailable. Keep the Akashic package pending.

## Publication

This is the local canonical package source. Before remote publication or redistribution of bundled persona material, complete the review in [NOTICE.md](NOTICE.md).
