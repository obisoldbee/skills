#!/usr/bin/env python3
"""Switch one adopted project's four governance files without entering its claim registry."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys
import uuid

import project_access as access
import upgrade_project_access as upgrade
import validate_project_root as validator


@contextmanager
def migration_lock(control: Path):
    runtime = control / "runtime"
    if access.is_link_or_junction(runtime):
        raise upgrade.UpgradeError("migration runtime is linked")
    runtime.mkdir(exist_ok=True)
    path = runtime / "policy-migration.lock"
    if access.is_link_or_junction(path):
        raise upgrade.UpgradeError("migration lock is linked")
    with path.open("a+b") as stream:
        # The file may persist; ownership exists only while the OS lock is held.
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        stream.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield runtime
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def migrate(target: Path, apply: bool = False) -> dict:
    proposal, _, _ = upgrade.plan(target, "worktree-first")
    proposal.update(coordination_policy="worktree-first", legacy_registry_consulted=False)
    if not apply or not proposal["changes"]:
        return proposal
    root = Path(proposal["project_root"])
    with migration_lock(root / ".project-conventions") as runtime:
        current, before, after = upgrade.plan(root, "worktree-first")
        if current["plan_sha256"] != proposal["plan_sha256"]:
            raise upgrade.UpgradeError("governance files changed; inspect and retry migration")
        backup = runtime / ("worktree-policy-" + uuid.uuid4().hex)
        backup.mkdir(mode=0o700)
        for name, content in before.items():
            dest = backup / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content)
        (backup / "plan.json").write_text(json.dumps(proposal, indent=2) + "\n", encoding="utf-8")
        replaced = []
        try:
            for change in current["changes"]:
                name = change["path"]
                upgrade.replace_owned(root / name, before[name], after[name])
                replaced.append(name)
            validator.validate(root)  # New status path never opens the old registry.
        except Exception as error:
            preserved = []
            for name in reversed(replaced):
                try:
                    upgrade.replace_owned(root / name, after[name], before[name])
                except (OSError, upgrade.UpgradeError):
                    preserved.append(name)
            raise upgrade.UpgradeError(
                f"migration failed; owned files rolled back; preserved={preserved}; backup={backup}; {error}"
            ) from error
        result = dict(proposal, status="migrated", backup=str(backup))
        (backup / "receipt.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument("--apply", action="store_true", help="Apply the already authorized policy change")
    args = parser.parse_args()
    try:
        result = migrate(args.target, args.apply)
    except (OSError, ValueError, access.AccessError, upgrade.UpgradeError,
            validator.ProjectValidationError) as error:
        print(json.dumps({"status": "error", "reason": str(error)}), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
