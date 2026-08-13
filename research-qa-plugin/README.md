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

For a real candidate package:

```bash
python3 -B skills/research-qa-orchestrator/scripts/validate_research_qa.py destination --package <absolute-new-path>
python3 -B skills/research-qa-orchestrator/scripts/validate_research_qa.py run --package <absolute-reserved-package-path>
```

The destination command only preflights a nonexistent calendar path. The package must then be reserved through the Akashic v2 ordinary-submission workflow. A passing run is still `pending` and not formally absorbed.

## External dependencies

Real execution requires a live Akashic registry/rule, a lawful paper acquisition executor, eight independent author contexts, and independent semantic audit capacity. Static validation does not prove any provider call, literature download, plugin installation, or formal adoption.

## Publication boundary

This directory is the local canonical source inside the shared Git worktree. It
is currently untracked, so no tracked, committed, pushed, or published state is
implied. Review [NOTICE.md](NOTICE.md) before any remote publication or
redistribution of bundled persona material.
