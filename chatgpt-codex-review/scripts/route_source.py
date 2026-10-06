#!/usr/bin/env python3
"""Inspect local Git identity and select a GitHub, configured MCP, or local upload source route.

This helper is read-only. Remote visibility and MCP configuration are supplied as
tool-observed evidence; the helper never pushes, publishes, or calls a provider.
"""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from local_packet import verify_packet

SHA = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
SCP = re.compile(r"^(?:ssh://)?git@github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$")


def git(project, *args):
    return subprocess.run(["git", "-C", str(project), *args], capture_output=True,
                          text=True, check=False)


def github_repo(url):
    match = SCP.fullmatch(url)
    if match:
        owner, repo = match.groups()
    else:
        parsed = urlsplit(url)
        if parsed.scheme not in {"https", "git"} or parsed.hostname != "github.com":
            return None
        bits = parsed.path.strip("/").removesuffix(".git").split("/")
        if len(bits) != 2:
            return None
        owner, repo = bits
    if not all(re.fullmatch(r"[A-Za-z0-9_.-]+", x) for x in (owner, repo)):
        return None
    return f"{owner}/{repo}"


def local_route(evidence, reason):
    packet = evidence.get("local_packet")
    if packet is None:
        return {"route": "local_packet", "status": "packet_needed", "reason": reason,
                "next_action": "freeze the authorized original files with local_packet.py, then upload"}
    if not isinstance(packet, dict) or any(
            not isinstance(packet.get(k), str) or not Path(packet[k]).is_absolute()
            for k in ("archive_path", "manifest_path")):
        raise ValueError("local_packet needs absolute archive_path and manifest_path")
    return {**verify_packet(Path(packet["archive_path"]), Path(packet["manifest_path"])),
            "selection_reason": reason}


def mcp_route(evidence, git_root=None):
    mcp = evidence.get("mcp", {})
    if not isinstance(mcp, dict):
        raise ValueError("mcp evidence must be an object")
    base = {"route": "mcp", "git_root": git_root}
    required = ("server", "tool", "version", "snapshot_sha256", "manifest_sha256", "evidence_ref")
    if mcp.get("configured") is not True or any(not isinstance(mcp.get(k), str) or not mcp[k].strip() for k in required):
        return {**base, "status": "mcp_connection_needed",
                "reason": "explicit MCP route needs a real configured server/tool/version and snapshot"}
    if not SHA256.fullmatch(mcp["snapshot_sha256"]) or not SHA256.fullmatch(mcp["manifest_sha256"]):
        raise ValueError("MCP snapshot and manifest need SHA-256")
    return {**base, "status": "ready", "source_id": "mcp:" + mcp["snapshot_sha256"],
            "mcp": {k: mcp[k] for k in required}}


def select(project, evidence):
    if not project.is_dir():
        raise ValueError("project directory does not exist")
    if not isinstance(evidence, dict):
        raise ValueError("evidence must be an object")
    requested = evidence.get("source_route", "auto")
    if not isinstance(requested, str) or requested not in {"auto", "github", "mcp", "local_packet"}:
        raise ValueError("source_route must be auto, github, mcp or local_packet")
    if requested == "local_packet":
        return local_route(evidence, "caller selected local packaging")
    if requested == "mcp":
        return mcp_route(evidence)
    root = git(project, "rev-parse", "--show-toplevel")
    if root.returncode and "not a git repository" not in root.stderr.lower():
        return {"route": "unknown", "status": "inspect_git", "reason": root.stderr.strip()}
    repo = None
    remote_url = None
    head = None
    dirty = None
    if root.returncode == 0:
        names = git(project, "remote")
        if names.returncode:
            return {"route": "unknown", "status": "inspect_remotes", "reason": names.stderr.strip()}
        selected = evidence.get("github_remote")
        remote_names = names.stdout.splitlines()
        if selected is not None and selected not in remote_names:
            raise ValueError("selected GitHub remote is not configured")
        ordered = [selected] if selected else sorted(remote_names, key=lambda name: (name != "origin", name))
        for name in ordered:
            fetched = git(project, "remote", "get-url", name)
            if fetched.returncode:
                return {"route": "unknown", "status": "inspect_remotes", "reason": fetched.stderr.strip()}
            url = fetched.stdout.strip()
            candidate = github_repo(url)
            if candidate:
                repo, remote_url = candidate, f"https://github.com/{candidate}.git"
                break
            if "github.com" in url.lower():
                return {"route": "unknown", "status": "inspect_remotes", "reason": "unrecognized GitHub remote URL"}
        if selected and not repo:
            raise ValueError("selected remote is not a GitHub repository")
        if repo:
            rev = git(project, "rev-parse", "HEAD")
            if rev.returncode or not SHA.fullmatch(rev.stdout.strip()):
                if requested == "auto":
                    return local_route(evidence, "local review does not require an initial commit")
                return {"route": "github", "status": "freeze_commit", "repository": repo,
                        "reason": "no full local commit could be pinned"}
            head = rev.stdout.strip()
            status = git(project, "status", "--porcelain")
            if status.returncode:
                return {"route": "unknown", "status": "inspect_worktree", "reason": status.stderr.strip()}
            dirty = bool(status.stdout.strip())
    declared = evidence.get("declared_github_url")
    if not repo and declared is not None:
        candidate = github_repo(declared) if isinstance(declared, str) else None
        if not candidate:
            return {"route": "unknown", "status": "verify_declared_github",
                    "reason": "declared GitHub URL could not be normalized"}
        declared_evidence = evidence.get("github", {})
        if (not isinstance(declared_evidence, dict) or declared_evidence.get("repository_verified") is not True
                or not isinstance(declared_evidence.get("evidence_ref"), str)
                or not declared_evidence["evidence_ref"].strip()):
            return {"route": "unknown", "status": "verify_declared_github",
                    "repository": candidate, "reason": "bind the declared repository with tool evidence"}
        repo, remote_url = candidate, f"https://github.com/{candidate}.git"
        if root.returncode == 0:
            rev = git(project, "rev-parse", "HEAD")
            head = rev.stdout.strip() if rev.returncode == 0 else None
            status = git(project, "status", "--porcelain")
            dirty = bool(status.stdout.strip()) if status.returncode == 0 else True
        else:
            head = declared_evidence.get("commit")
        if not isinstance(head, str) or not SHA.fullmatch(head):
            return {"route": "github", "status": "freeze_commit", "repository": repo,
                    "reason": "declared GitHub repository needs a fixed full commit"}
    if repo:
        remote = evidence.get("github", {})
        if not isinstance(remote, dict):
            raise ValueError("github evidence must be an object")
        if remote and (remote.get("repository") != repo or remote.get("commit") != head):
            raise ValueError("GitHub evidence does not bind the observed repository and HEAD")
        base = {"route": "github", "repository": repo, "remote_url": remote_url,
                "source_id": "git:" + head, "working_tree_dirty": dirty,
                "commit_url": f"https://github.com/{repo}/tree/{head}"}
        excluded = (remote.get("dirty_scope_disposition") == "excluded_from_review"
                    and isinstance(remote.get("dirty_scope_evidence_ref"), str)
                    and bool(remote["dirty_scope_evidence_ref"].strip()))
        if dirty and not excluded:
            if requested == "auto":
                return local_route(evidence, "freeze current worktree bytes including in-scope uncommitted changes")
            return {**base, "status": "freeze_commit", "reason": "working tree has changes outside pinned HEAD"}
        if excluded:
            base["dirty_scope_evidence_ref"] = remote["dirty_scope_evidence_ref"]
        if remote.get("remote_has_commit") is False or remote.get("web_can_read") is False:
            if requested == "auto":
                return local_route(evidence, "GitHub version is unavailable to Web; upload the authorized local snapshot")
            return {**base, "status": "github_access_blocked", "reason": "explicit GitHub route needs publication or access"}
        if remote.get("remote_has_commit") is True and remote.get("web_can_read") is True:
            if not isinstance(remote.get("evidence_ref"), str) or not remote["evidence_ref"].strip():
                raise ValueError("ready GitHub route needs tool evidence_ref")
            return {**base, "status": "ready", "evidence_ref": remote["evidence_ref"]}
        return {**base, "status": "verify_remote_commit_and_web_access",
                "reason": "local Git remote does not prove the web reviewer can read this commit"}
    if requested == "github":
        return {"route": "unknown", "status": "verify_declared_github",
                "reason": "explicit GitHub route needs a verified repository"}
    if isinstance(evidence.get("mcp"), dict) and evidence["mcp"].get("configured") is True:
        observed = mcp_route(evidence, root.stdout.strip() if root.returncode == 0 else None)
        if observed["status"] == "ready":
            return observed
    return local_route(evidence, "no verified GitHub or ready MCP source; use a local upload packet")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    try:
        evidence = json.loads(args.evidence.read_text(encoding="utf-8")) if args.evidence else {}
        answer = select(args.project, evidence)
    except (ValueError, OSError, RuntimeError, zipfile.BadZipFile) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"valid": True, **answer}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
