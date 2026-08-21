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

`browser_required` and `manual_browser_required` are queue states. `downloaded` requires disk validation. A planning-only response is allowed when authorization or runtime prerequisites are missing, but the Skill itself must not be redefined as plan-only.

Network concurrency defaults to one active lane per public egress IP. Multiple
workers may run offline validation concurrently, but disjoint output paths are
not evidence that their network effects are independent. Interactive browser
follow-up prefers the registered `$ego-browser`; a different browser is a
recorded fallback, not an implicit substitute.
