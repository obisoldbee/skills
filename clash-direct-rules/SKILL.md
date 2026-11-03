---
name: clash-direct-rules
description: >-
  Audit and maintain Clash Verge/mihomo custom DIRECT routing rules, reconcile
  current durable source with a private versioned inventory, prepare minimal
  rule changes, and recover verified rules after configuration loss. Use for
  missed domestic routes, rule precedence, current rule inventories and restores.
  General proxy/core startup failures belong to mac-agent-proxy-diagnostics.
---

# Clash Direct Rules

Maintain the user's approved direct-routing policy from current evidence. The durable enhancement is the source of truth; the private inventory records a verified version. Return findings and changes in the user's language. Keep real domains, process paths, machine bindings and incident evidence outside this portable package.

## Bind the task

Read the project's AGENTS.md and its explicit private `binding.json` location. Bind the device, enhancement source, literal rule-array name, private inventory directory, optional generated configuration, protected rules and revoked rules. See [private state and commands](references/private-state.md). If the binding is absent, obtain the actual configuration location before touching that device; portable examples are not a machine binding.

Read existing authorization and select the needed work. Audit reads state. Maintaining the inventory writes only private records. A requested rule fix includes its bounded backup, minimal edit, supported reload and verification. A Skill-authoring or record-only request does not change the live proxy. Reuse authorization that already covers the action; identify only a concrete missing input or consequential scope change.

If available, use `mac-agent-proxy-diagnostics` for missing/zero-byte cores, process environment inheritance or startup failures. Keep rule maintenance here. Do not copy or replace that installed Skill as a side effect.

## Reconcile before acting

```sh
python3 -B <skill-root>/scripts/rules_inventory.py --binding <private-binding.json> check
```

`current` means the saved script bytes and ordered custom rules match the inventory at this observation. With a generated-config binding, also require its rule prefix to match. 随后用新连接检查实际匹配规则和出站链。

- `stale_source` means something changed since the recorded version. Read the current source and diff against the last verified inventory; preserve legitimate later edits. Continue investigation, then reconcile the records after review. Do not restore an old snapshot over it.
- Missing source, malformed literals or policy violations need diagnosis. Keep the previous verified version available; a reset or parser failure must not publish an empty inventory as the new policy.
- Rules are ordered. Matching counts alone cannot establish that routing is unchanged.

“Latest” is an execution-time contract. Run this check at entry, immediately before any authorized config write, after reload, and after a subscription change, restore or upgrade that is part of the task. Update the private version after a verified change. Between invocations, record the last observation time; this Skill installs no watcher or timer.

## Find justified candidates

Read only relevant connection/log fields in the authorized window. Preserve timestamp, host, **destination** IP, matched rule and actual outbound chain. Distinguish a proxy-node address and fake-IP from the service destination. An empty `destinationGeoIP` remains unknown until a real destination address and trusted local IP database or runtime evidence can resolve it. Keep service tags such as `GOOGLE` or `CLOUDFLARE` verbatim; only an explicit CN result is CN.

Today's DNS lookup describes today's resolution. Use a fresh connection to reproduce a current route; do not assign today's IP or country to an old record with missing addresses. Preserve warning-only records as unknown final routes. Log retention defines the sample, so report its real dates rather than implying recent or complete coverage.

Confirm the service should be direct and check earlier matching rules. For a CDN that should be direct only on a CN destination, preserve both conditions, for example `AND,((DOMAIN,cdn.example),(GEOIP,CN)),DIRECT`. A foreign destination falls through to the existing policy. Do not expand that decision to an entire vendor suffix, shared CDN range or all CN traffic without supporting scope and evidence. Existing explicitly approved process/LAN/suffix rules remain distinct from these new conditional rules.

## Prepare and apply a bounded change

Read [change, validation and recovery](references/change-validation.md). Prepare an exact `add`/`remove` JSON delta and generate a **private candidate** with `plan`, pinned to both source SHA and inventory SHA. Review its ordered diff and the rest of the script. The helper preserves the non-array bytes and never writes live configuration.

On an authorized live change, back up the actual current durable source, recheck the expected SHA immediately before writing, apply only the reviewed delta, and use the installed app's supported reload/reactivate route. Preserve subscription rules, final fallbacks, nodes, credentials, DNS, IPv6, TUN and healthy processes unless the task separately changes them. If the generated file or UI list is missing, inspect the durable source before recovery.

Check saved source, generated config, runtime rules and new connection routes separately. Record failed or unperformed checks. Do not close all connections or restart a healthy client to force a single rule live. After verification, write a new private inventory revision with the actual source SHA, ordered-rules SHA, observation time, prior inventory SHA and evidence reference. Retain previous revisions and script backups.

For reset recovery, `restore-plan` can produce a candidate from the latest verified script when the source is absent or a recognized empty enhancement. It refuses divergent live code. Reconcile later edits manually within the task's authority rather than replacing them. Applying any restore still follows the same live-change checks.

## Complete on evidence

Report rule deltas and preservation, inventory revision/hashes/time, exact private artifact paths, which of the four checks passed, remaining uncertainties and recovery entry. `candidate_only`, `snapshot_saved` and a successful syntax test describe their own stage. Finish an audit with findings; finish a requested live fix after the applicable route checks and private record update. Do not claim perpetual monitoring or a successful live route from a saved file.
