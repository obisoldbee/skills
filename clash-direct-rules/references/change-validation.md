# Change, validation and recovery

## Keep the layers distinct

| Layer | Evidence |
|---|---|
| Durable enhancement | Current script bytes/SHA and ordered custom rules; backup before change |
| Generated configuration | Actual generated rule list, order and preserved subscription/fallbacks; safely read only required fields |
| Running core | Current rule-mode/config metadata and normalized runtime rule entries, including policy and order |
| Fresh connections | The actual destination, matched rule and outbound chain after reload, with timestamp |

A configuration count alone is insufficient. Match custom rules by type, payload and outbound after normalizing the runtime's documented representation. Check that new rules precede the former match and that non-target subscription rules retain order and fallback. Distinguish parse/load success from service reachability and from application success. An authenticated TLS response with a root-path 404 proves a limited route/service observation, not full feature acceptance. Use an appropriate feature URL when the task requires it, and retain a non-target control route.

Use the installed app's supported enhancement and reload workflow. Read its current documentation when behavior is uncertain. Avoid editing generated YAML as the persistent fix. Back up source and narrowly relevant runtime settings in a private directory; never output full configuration, controller secrets, subscription URLs, cookies or raw unrelated browsing history. Read-only runtime queries use the already-authorized local controller, with credentials handled in memory and redacted from output. Do not silently open a remote controller or disable authentication.

If the generated configuration's controller endpoint is absent or refuses connection, inspect the current app/service binding for its supported control endpoint. Service mode can use a different Unix socket. Verify that endpoint before declaring the core stopped or considering a restart. Store the verified locator privately and recheck it on later runs. Normalize documented runtime rule representations before comparison; for example, an AND payload may display `&&` between its conditions instead of the configuration's comma-separated form.

Only close a specifically identified stale connection when needed, authorized, and scoped to the affected destination. New connections are preferred. Preserve healthy application processes and unrelated sessions. A user-proven IPv6/DNS repair is a retained environment fact, not a reason to disable IPv6 on other machines. Verify this device's current state before drawing a network conclusion.

## Record and recover

For a normal edit, retain pre-change source bytes/hash, candidate hash/delta, actual reload receipt and four-layer checks. Update the inventory from the **actual saved source**, not from a candidate file, then rerun `check`. Failed runtime verification stays explicit even when the inventory accurately matches the saved source.

For rollback, compare the current source with the version actually applied. If they still match, restore the verified pre-change enhancement and reload. If later changes exist, remove/reverse only this task's delta while preserving later approved work. Recheck all affected layers and record a new revision rather than erasing history.

For configuration loss/reset:

1. Separate lost enhancement, lost subscription, failed core binary and stopped runtime. Preserve surviving files and look for a supported app recovery path.
2. Read the private CURRENT inventory and checksum-verified history. Use `restore-plan` only for missing/recognized-empty enhancement; unknown live code gets a reviewed merge. Verify the candidate's full ordered rule list and current exclusions.
3. Apply within the user's restoration scope, through the actual durable enhancement and app reload. Restore subscription/provider material only from separately authorized private backups. The rules inventory does not contain those credentials.
4. Check generated and runtime rules, representative fresh connections and retained network settings. Synchronize a new inventory version and record the incident. A historical backup containing revoked rules must not reintroduce them.

## Source basis

Mihomo evaluates ordered routing rules and supports logical combinations of conditions; use the exact domain plus CN condition for a geographically conditional exception. See [Mihomo routing rules](https://wiki.metacubex.one/config/rules/). Clash Verge's enhancement script modifies the generated configuration through `main`; use the app-supported global script entry and reload for the installed version. See [Clash Verge custom scripts](https://www.clashverge.dev/guide/script.html). These pages were checked on 2026-10-19; they document mechanisms, not this device's policy or route success.
