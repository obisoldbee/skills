# Benchmark Human Ranking

## Purpose

Use top-three preference per fixed case when selecting a default for real media-understanding work. It is faster and less ambiguous than asking for an absolute score for every output.

## Score and ordering

- First place: 3 points.
- Second place: 2 points.
- Third place: 1 point.
- Failed or unranked: 0 points.

Order the leaderboard by total points, then first-place votes, second-place votes, third-place votes, and finally stable participant ID. Report coverage as ranked cases divided by total cases; do not call a leaderboard final while coverage is incomplete.

## Bias controls and decision use

- Use blind aliases for quality judgment, and keep source media and prompt constant.
- Do not show automated scores in the ranking table by default. Read the full human-readable projection before ranking; open raw evidence only to verify extraction or layout behavior.
- Revisit only tied or near-tied cases after the first pass rather than repeatedly rescoring every case.
- Human points answer which output is most useful. Correctness gates, reliability, latency, price, privacy, endpoint availability, and task-family evidence remain separate operational gates.

Validate the exported ranking JSON with `scripts/validate_human_rankings.py` before recording a route conclusion.
