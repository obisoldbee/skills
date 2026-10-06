# Canonical execution contract

The canonical Skill package is an executable downloader after fresh, scoped authorization. Runtime consumers must resolve `$paper-downloader` directly to this package; a copied wrapper or historical runtime directory is not an authorized source. Route selection alone does not grant network, browser, write, or institutional-access authority.

The execution envelope must record:

- frozen input inventory and SHA-256;
- lawful source/access statement;
- exact permitted network/browser effects;
- one writable output root;
- selected route family and runtime prerequisites;
- the `shared-egress-ip:paper-download` token owner and transfer checkpoints;
- per-attempt receipts, disk readback, and final coverage.

All persisted outputs are explicit required CLI arguments and must resolve
inside the declared output root. The Skill package/source directory is never a
valid output root, nor is any ancestor or descendant of the package. Inputs and
outputs may not alias after path resolution. Importing a module performs no argument parsing, directory
creation, browser startup, or file write.

The canonical manifest is `paper-downloader/download-manifest/v2`. It preserves
every frozen-inventory row and exact inventory SHA/row-id order. Browser work
writes a row-and-identifier-bound result journal; it never maintains a second
status manifest. Reconciliation records `reconciled_at`, preserves an unknown
`downloaded_at` as unknown, and never fabricates a historical timestamp.

`browser_required` and `manual_browser_required` are queue states. `downloaded` requires disk validation. A planning-only response is allowed when authorization or runtime prerequisites are missing, but the Skill itself must not be redefined as plan-only.

Inventory parsing is explicit `auto|markdown|csv`; zero parsed rows fail. The
manifest binds the inventory bytes, ordered row ids, and full frozen row
projection. PDF identity comes from a primary identifier in the referenced PDF Info
metadata or an exact PDF Title metadata match; conflicting titles reject a match, never a filename, route, or header.
Final reporting rereads manifest, inventory and disk after persistence and
refuses target-processing closure while any target queue/follow-up/manual-review gate or
required blocker evidence remains. Supplementary pending states are disclosed separately.

Network concurrency defaults to one active lane per public egress IP. Multiple
workers may run offline validation concurrently, but disjoint output paths are
not evidence that their network effects are independent. Interactive browser
follow-up uses the contract in [browser routing](ego-browser-route.md): explicit choice, then applicable caller preferences among callable, task-capable routes, then platform defaults and verified fallbacks. Browser choice never removes shared-egress serialization.

### Supplementary collection and quota

Freeze optional `collection_role` (`target` by default, or `supplementary`) and
`collection_role_reason` with each inventory row. The role is bound by the row hash.
Set manifest `target_count` from the requested quota (`--target-count`); supplementary
rows never satisfy it. Report target and supplementary totals separately, deduplicated
by publication identity. Unresolved supplementary candidates do not block target processing
closure, but remain explicitly pending; they do not count as downloaded. A complete
processing receipt is not a claim that `quota.target_quota_met` is true. Keep and analyze
counterevidence under its own true identity rather than relabeling it as a requested paper.
