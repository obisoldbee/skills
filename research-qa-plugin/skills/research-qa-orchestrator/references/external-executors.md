# External Executor Binding

## Paper acquisition

The Stage 3 paper acquisition executor is the separately registered `$paper-downloader` Skill.

In the shared `obisoldbee-skills` collection, its canonical package source is:

```text
<collection>/GitHub/paper-downloader/SKILL.md
```

The runtime consumer must be a direct Unix symlink or Windows junction to `<collection>/GitHub/paper-downloader`, never to the `paper-downloader/src/paper-downloader` wrapper projection, a former `working-skills` directory, an indirect link, or a copied Agent directory. Resolve and record the lexical link/junction target, real path, and `SKILL.md` SHA-256 before Stage 3. Stop with `acquisition_executor_unavailable` when the registered Skill is missing, unreadable, copied from another source, or resolves elsewhere.

That readback proves only `consumer_link_state: linked`. It does not prove that a runtime discovered the Skill or executed it. A successful run separately requires:

1. `skill-discovery-receipt/v1` with `evidence_origin: runtime_skill_catalog`, runtime identity, discovered consumer path, canonical real path, Skill hash, receipt ID, and observation time; and
2. one `acquisition-operation-receipt/v1` for every `download_attempted: true` source, binding the canonical Skill hash, actual Paper Downloader tool, operation ID, source identity, result status, payload path/hash/bytes, and ordered timestamps.

Missing discovery receipt is `acquisition_executor_discovery_unverified`; a local PDF without an operation receipt is `acquisition_operation_missing`. When those normalized package-local receipts are present, the offline validator can report only that their structures and byte bindings validated. Discovery and execution remain `runtime_not_verified` without independent host attestation. Synthetic fixtures, link presence, a downloader plan, a self-reported completion field, or a package-local `host_attestation` claim cannot satisfy those axes.

These bindings identify source/link facts and package-local discovery/operation claims only. They do not authorize network access, institutional access, browser effects, file writes, or paywall bypass. Every run still requires the explicit `source_rights`, network/browser authority, and output root described by the workflow contract. Structural acceptance of a normalized receipt does not prove the operation occurred or that the provider is currently available.

PaywallBuster is not a configured route in this contract. A 2026-08-17 anonymous-browser evaluation covered 30 manifest-bound publications through both routes exposed by its UI. All 30 stopped at access controls or upstream unavailability, no route produced an on-disk PDF, and all three download roots were empty. That result does not prove universal failure, but it provides no positive acquisition evidence and therefore cannot justify preferred-route status. A future change still requires separate lawful, repeatable PDF evidence while preserving the normal disk-receipt gates.
