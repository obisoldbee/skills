#!/usr/bin/env python3
"""Plan/apply a four-file access upgrade in one already adopted Project Root."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

import initialize_project_root as initializer
import project_access as access
import validate_project_root as validator


class UpgradeError(RuntimeError):
    pass


FILES = ("AGENTS.md", ".project-conventions/ACCESS.md",
         ".project-conventions/project_access.py", ".project-conventions/project.json")
LEGACY_LINES = {
    "- Record significant decisions and substantive work that adds useful continuity; update indexes only when their represented facts change. Response-only tasks create no project records. Required records are written under the exclusive writer claim.":
        "- Record significant decisions and substantive work that adds useful continuity; update indexes only when their represented facts change. Response-only tasks create no project records. Claim the exact record files with scoped-writer only for their write batch; "
        "reserve conversation/ briefly when allocating its next sequence number.",
    "- Do not initialize Git, move material, publish, or create worktrees unless the user separately authorizes that action.":
        "- Do not initialize Git, move material, or publish without task authorization. "
        "A temporary task-specific worktree can support authorized code changes; choose "
        "its exact repository, base, branch and path before creating it. Initialization itself creates no worktree.",
}


# Migrate only recognized generated record instructions, never arbitrary user rules.
WORKTREE_RECORD_LINE = "- Record significant decisions and substantive work that adds useful continuity; update indexes only when their represented facts change. Response-only tasks create no project records. Use separate task records and one integrator for canonical logs and sequence numbers."
LEGACY_RECORD_LINE = "- Record significant decisions and substantive work that adds useful continuity; update indexes only when their represented facts change. Response-only tasks create no project records. Claim the exact record files with scoped-writer only for their write batch; reserve conversation/ briefly when allocating its next sequence number."


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def plan(target: Path, coordination_policy: str | None = None) -> tuple[dict, dict[str, bytes], dict[str, bytes]]:
    raw = target.expanduser().absolute()
    root, control, config = access.resolve_control(raw / ".project-conventions/project_access.py")
    # Validate as data; do not execute the target's helper in a dry-run.
    validator.validate(root, run_access_check=False)
    if coordination_policy == "worktree-first" or config.get("coordination_policy") == "worktree-first":
        runtime, storage = control / "runtime", "legacy-registry-not-consulted"
    else:
        runtime, storage = access.runtime_root(root, control, config)
    before = {name: (root / name).read_bytes() for name in FILES}
    agents = before["AGENTS.md"].decode("utf-8")
    newline = "\r\n" if "\r\n" in agents else "\n"
    start = agents.index(access.MANAGED_START)
    end = agents.index(access.MANAGED_END, start) + len(access.MANAGED_END)
    policy = coordination_policy or config.get("coordination_policy", "legacy-claims")
    block = initializer.render_access_block(config["project_profile"], config["skill_package"], policy)
    outside_before, outside_after = agents[:start], agents[end:]
    replacements = dict(LEGACY_LINES)
    if policy == "worktree-first":
        replacements[LEGACY_RECORD_LINE] = WORKTREE_RECORD_LINE
        for key in replacements:
            if "Record significant decisions" in key:
                replacements[key] = WORKTREE_RECORD_LINE
        # Previous shared-wrapper templates also emitted this line outside the block.
        pattern = re.compile(
            r"^- This member's local helper stores claims in `\.\./[\w-]+/\.project-conventions/runtime`, "
            r"so one local `enter` automatically shares the collection-wide gate used by every member "
            r"and the control project\. Do not bypass it by entering `\.\./([\w-]+)` directly\.$"
        )
        for line in (outside_before + outside_after).splitlines():
            match = pattern.fullmatch(line)
            if match:
                replacements[line] = (
                    f"- This member uses worktree-first. Resolve the true source in `../{match[1]}` "
                    "before Git operations; independent wrapper reports need no claim. "
                    "The old collection runtime is compatibility metadata only."
                )
    def migrate_generated_lines(text: str) -> str:
        return "".join(replacements.get(line.rstrip("\r\n"), line.rstrip("\r\n"))
                       + line[len(line.rstrip("\r\n")):] for line in text.splitlines(keepends=True))
    outside_before = migrate_generated_lines(outside_before)
    outside_after = migrate_generated_lines(outside_after)
    after = {
        "AGENTS.md": (outside_before + block.replace("\n", newline) + outside_after).encode("utf-8"),
        ".project-conventions/ACCESS.md": initializer.render_access_readme(policy).encode("utf-8"),
        ".project-conventions/project_access.py": Path(access.__file__).read_bytes(),
    }
    updated = dict(config)
    if coordination_policy is not None:
        updated["coordination_policy"] = policy
    updated.update(
        agents_block_sha256=digest(block.encode("utf-8")),
        access_readme_sha256=access.portable_text_sha256(after[".project-conventions/ACCESS.md"]),
        helper_sha256=access.portable_text_sha256(after[".project-conventions/project_access.py"]),
    )
    after[".project-conventions/project.json"] = (json.dumps(updated, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    changes = [{"path": name, "before_sha256": digest(before[name]), "after_sha256": digest(after[name])}
               for name in FILES if before[name] != after[name]]
    payload = {"project_root": str(root), "runtime_storage": storage, "runtime": str(runtime),
               "protocol_version": access.PROTOCOL_VERSION, "changes": changes,
               "preconditions": {name: digest(content) for name, content in before.items()}}
    payload["plan_sha256"] = digest(json.dumps(payload, sort_keys=True).encode("utf-8"))
    payload["status"] = "would_upgrade" if changes else "already_current"
    return payload, before, after


def target_command(root: Path, *arguments: str) -> dict:
    completed = subprocess.run([sys.executable, "-B", str(root / FILES[2]), *arguments],
                               capture_output=True, text=True, check=False)
    if completed.returncode:
        raise UpgradeError(completed.stderr.strip() or completed.stdout.strip())
    return json.loads(completed.stdout)


def database_version(database: Path) -> str | None:
    if not database.exists():
        return None
    access.ensure_runtime_boundary(database, create=False)
    connection = sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)
    try:
        connection.execute("PRAGMA query_only = ON")
        row = connection.execute("SELECT value FROM meta WHERE key = 'protocol_version'").fetchone()
        return row[0] if row else None
    finally:
        connection.close()


def replace_owned(path: Path, expected: bytes, content: bytes) -> None:
    if access.is_link_or_junction(path) or not path.is_file() or path.read_bytes() != expected:
        raise UpgradeError(f"upgrade target changed: {path}")
    mode = path.stat().st_mode & 0o777
    descriptor, temporary = tempfile.mkstemp(prefix=".access-upgrade-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temporary, mode)
        if access.is_link_or_junction(path) or path.read_bytes() != expected:
            raise UpgradeError(f"upgrade target changed before replace: {path}")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def apply(target: Path, expected_plan: str) -> dict:
    proposal, before, after = plan(target)
    config = json.loads(before[FILES[3]])
    if config.get("coordination_policy") == "worktree-first":
        from migrate_worktree_policy import migrate
        if proposal["plan_sha256"] != expected_plan:
            raise UpgradeError("reviewed plan changed")
        return migrate(target, apply=True)
    if proposal["plan_sha256"] != expected_plan:
        raise UpgradeError("reviewed plan changed; inspect a new dry-run before apply")
    if not proposal["changes"]:
        return proposal
    root = Path(proposal["project_root"])
    runtime = Path(proposal["runtime"])
    database = runtime / access.DATABASE_FILE
    original_version = database_version(database)
    if original_version == str(access.PROTOCOL_VERSION):
        # Another explicitly upgraded copy may share this registry. Use the
        # current trusted maintenance implementation, never the old conflict code.
        claim = access.enter(root, database, proposal["runtime_storage"], "writer", None,
                             "project-access-upgrade", [], None, registry_maintenance=True)
    else:
        claim = target_command(root, "enter", "--mode", "writer", "--actor", "project-access-upgrade")
    backup: Path | None = None
    replaced: list[str] = []
    activated = False
    try:
        current, _, _ = plan(root)
        if current["plan_sha256"] != expected_plan:
            raise UpgradeError("target changed after maintenance admission")
        backup = runtime / ("upgrade-" + claim["session_id"])
        backup.mkdir(mode=0o700)
        for name, content in before.items():
            dest = backup / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content)
        # Private release material is retained only if interruption needs repair.
        journal = backup / "claim.json"
        descriptor = os.open(journal, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            json.dump(claim, output, ensure_ascii=False)
        (backup / "plan.json").write_text(json.dumps(proposal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for change in proposal["changes"]:
            name = change["path"]
            replace_owned(root / name, before[name], after[name])
            replaced.append(name)
        validator.validate(root, run_access_check=False)
        # All four files are valid before the transactional registry activation.
        access.check_claim(root, database, claim["session_id"], claim["token"])
        activated = True
        access.finish(root, database, claim["session_id"], claim["token"], "success")
        journal.unlink()
        result = dict(proposal, status="upgraded", backup=str(backup),
                      claim_released=True, database_protocol=database_version(database))
        (backup / "receipt.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result
    except Exception as error:
        if original_version != str(access.PROTOCOL_VERSION) and database_version(database) == str(access.PROTOCOL_VERSION):
            activated = True
        if activated:
            # Never restore an older helper over an activated newer-protocol DB.
            raise UpgradeError(f"protocol activated; release/receipt needs repair; backup={backup}; {error}") from error
        preserved = []
        for name in reversed(replaced):
            try:
                replace_owned(root / name, after[name], before[name])
            except (OSError, UpgradeError):
                preserved.append(name)
        try:
            if original_version == str(access.PROTOCOL_VERSION):
                access.finish(root, database, claim["session_id"], claim["token"], "failed")
            else:
                target_command(root, "finish", "--session", claim["session_id"], "--token", claim["token"], "--outcome", "failed")
            if backup is not None:
                (backup / "claim.json").unlink(missing_ok=True)
        except Exception:
            preserved.append("maintenance claim (private recovery material in backup)")
        raise UpgradeError(f"upgrade failed; owned files rolled back; preserved={preserved}; backup={backup}; {error}") from error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--plan-sha256")
    arguments = parser.parse_args()
    try:
        if arguments.apply:
            if not arguments.plan_sha256:
                raise UpgradeError("--apply requires the reviewed --plan-sha256")
            result = apply(arguments.target, arguments.plan_sha256)
        else:
            result, _, _ = plan(arguments.target)
    except (UpgradeError, access.AccessError, validator.ProjectValidationError,
            OSError, sqlite3.Error, ValueError) as error:
        print(json.dumps({"status": "error", "reason": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
