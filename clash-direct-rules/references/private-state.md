# Private binding and versioned state

Use a private, non-Git project directory. `binding.json` is a device-specific locator, not a secret store. Resolve the paths on the execution device. The helper accepts this shape; placeholders must be replaced with real absolute paths before execution.

```json
{
  "schema_version": 1,
  "device_id": "verified-local-device",
  "source": "<absolute durable enhancement Script.js>",
  "rule_array": "restoredRules",
  "state_dir": "<absolute private inventory directory>",
  "generated_config": "<optional absolute generated YAML>",
  "protected_rules": [],
  "excluded_rules": []
}
```

Keep local protected/revoked decisions and their provenance in the wrapper. Changes to that policy require the same task evidence as the rules they constrain. Runtime availability is independent of package distribution. The helper needs Python 3.10+ and local file access; it makes no network requests, invokes no JavaScript and applies no proxy settings.

## Read and synchronize

`check` emits only status, hashes, counts, revision and order/prefix comparison. It does not print domains, process paths, nodes, secret values or source snippets. Exit 0 means current; exit 2 requires reconciliation or indicates a missing/unsupported input. Its narrow parser recognizes one `const <rule_array> = <JSON array>;` outside strings/comments. A computed array, duplicate declaration or unsupported generated YAML yields an error; inspect the real source before adapting the parser. Do not execute an unknown enhancement to extract its rules.

To record an independently reviewed current source, first run the preview, then the same command with `--write`:

```sh
python3 -B <skill-root>/scripts/rules_inventory.py --binding <binding.json> snapshot \
  --expected-source-sha256 <fresh source SHA> \
  --expected-current-sha256 <check.inventory_sha256 or absent for initialization> \
  --evidence <actual private verification receipt.json>
```

Review changes first. Removing recorded rules requires `--allow-removals`, and protected/revoked policy still applies. The flag acknowledges that the record delta was reviewed; it grants no live-write authority. Unchanged checks need no new revision. Source changes outside the literal array still produce stale status and need review.

A write uses a single inventory lock and atomically replaces `CURRENT.json`; competing or stale writes fail. It creates immutable `history/<revision>-<inventory SHA>.json` and `history/source-<source SHA>.js`, with private directory/file permissions. The script backup is only the enhancement, never a whole subscription/config export. `CURRENT.json` contains the source identity, all ordered rules, revision, hashes, `updated_at`, prior inventory SHA and evidence file hash. These records describe an observation; independent edits after it will be detected on the next check. A writer lock left after interruption needs inspection before cleanup.

## Prepare candidates

A change file contains exactly `add` and `remove` arrays of full rule strings. Additions must target DIRECT. Retained rules keep their order; new rules prepend. Existing additions are not duplicated. Only explicitly named removals are removed; protected and revoked rules are enforced.

```sh
python3 -B <skill-root>/scripts/rules_inventory.py --binding <binding.json> plan \
  --expected-source-sha256 <check.source_sha256> \
  --expected-current-sha256 <check.inventory_sha256> \
  --changes <private change.json> --out <new private candidate directory>
```

The output directory's parent must exist. The directory must be absent and outside Git and the package. Outputs are `candidate.js` and `plan.json`. The plan pins both inputs, names the delta and hashes the candidate. Recheck those inputs before applying it. The helper leaves source, inventory and running config untouched.

For an absent or known-empty enhancement, `restore-plan` creates the same two private outputs using the latest inventory's verified script backup:

```sh
python3 -B <skill-root>/scripts/rules_inventory.py --binding <binding.json> restore-plan \
  --expected-source-sha256 <fresh source SHA or absent> \
  --expected-current-sha256 <current inventory file SHA> \
  --out <new private recovery directory>
```

Unknown or changed live code returns `live_source_diverged_manual_merge_required`. Read both versions, preserve newer approved rules and other enhancement logic, and prepare a scoped merge. A stale snapshot is never applied automatically. Backup checksum failure keeps the live state unchanged.
