# Provenance

The frozen comparison package `20260807001-codex` contains five unique content lines and records that same version labels do not imply identical bytes.

Selected implementation baseline:

- source: `20260804002-codex/payload/skills/legacy-vault-00-agent-skills/tree/00-agent-skills/60-toolkits/paper-downloader/`;
- source `SKILL.md` SHA-256: `869ae8fdeddd320ef1cca28889db56751ac13c13835965142c54cfe9c4fab56e`;
- source tree SHA-256: `ae324842a1d78b8295e0460864dcd2259380bace9ceb46cedae5b25eb897a3da`;
- reason: it contains the v3 browser downloaders plus the later manifest-first pass, runtime wrapper, coverage summarizer, failure screenshots, package contract, and regression test absent from the earlier v3 package snapshots.

Other compared lines:

- MiniMax/Trae/Qwen runtime v2.1.0 tree: `cd0e39268c4213c85dd537277daa8162e881983c33dff43164bc3c21545a19da`;
- 20260623002 v3 tree: `817cb8a9c2c5bb9a535adf390299d4fa23f822eba7e1264b2763a8040ec3a28d`;
- 20260628002 v3 tree: `ef3485ad51c7b26f74a992187665e89d1b8904f82c238662f2f7b8cd7cfafab3`.

The selected implementation removes the old plan-only contraction and adds a text-only Shoulong article-page branch that delegates to the single working web capture engine. It explicitly excludes image understanding, OCR, and image-derived paper discovery.

## Canonical source migration

On 2026-08-17, the complete active candidate tree moved atomically from the local `working-skills` workflow scope into the public shared-repository package `GitHub/paper-downloader`. The portable pre-move and post-move tree digest was identical: `d2eb67ebd43802d3fa6c95913f6e60c71f72ecf5b2521df470a8bce77fdd1001`.

`GitHub/paper-downloader` is now the only editable package source. Member wrappers are projections, and Agent consumers must link directly to this package. Historical package snapshots and pre-migration consumer copies remain evidence only; they are not active sources. A source tree, projection, or link still does not prove runtime discovery, execution, paper acquisition, publication, or formal Akashic absorption.
