# External Executor Binding

## Paper acquisition

The Stage 3 paper acquisition executor is the separately registered `$paper-downloader` Skill.

In the shared `obisoldbee-skills` collection, its canonical package source is:

```text
<collection>/GitHub/paper-downloader/SKILL.md
```

The runtime consumer must resolve directly to `<collection>/GitHub/paper-downloader`, never to the `paper-downloader/src/paper-downloader` wrapper projection, a former `working-skills` directory, or a copied Agent directory. Resolve and record the real path and `SKILL.md` SHA-256 before Stage 3. Stop with `acquisition_executor_unavailable` when the registered Skill is missing, unreadable, copied from another source, or resolves elsewhere.

This binding identifies the executor contract only. It does not authorize network access, institutional access, browser effects, file writes, or paywall bypass. Every run still requires the explicit `source_rights`, network/browser authority, and output root described by the workflow contract.

PaywallBuster is not a configured route in this contract. A 2026-08-17 anonymous-browser evaluation covered 30 manifest-bound publications through both routes exposed by its UI. All 30 stopped at access controls or upstream unavailability, no route produced an on-disk PDF, and all three download roots were empty. That result does not prove universal failure, but it provides no positive acquisition evidence and therefore cannot justify preferred-route status. A future change still requires separate lawful, repeatable PDF evidence while preserving the normal disk-receipt gates.
