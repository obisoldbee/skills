#!/usr/bin/env python3
"""Deterministic tests for validate_research_qa.py; no network or models."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import validate_research_qa as validator  # noqa: E402


VERIFY_BUNDLED_PATH = SKILL_ROOT / "bundled" / "verify_bundled.py"
VERIFY_SPEC = importlib.util.spec_from_file_location(
    "research_qa_verify_bundled",
    VERIFY_BUNDLED_PATH,
)
assert VERIFY_SPEC is not None and VERIFY_SPEC.loader is not None
verify_bundled = importlib.util.module_from_spec(VERIFY_SPEC)
VERIFY_SPEC.loader.exec_module(verify_bundled)


NOW = "2026-08-07T12:00:00+08:00"


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_jsonl(path: Path, values: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = b"".join(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        + b"\n"
        for value in values
    )
    path.write_bytes(data)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def rehash_source(row: dict[str, Any]) -> None:
    row["record_sha256"] = validator.sha256_bytes(
        validator.canonical_without(row, "record_sha256")
    )


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_directory_link(link: Path, target: Path) -> None:
    if os.name == "nt":
        result = subprocess.run(
            ["cmd", "/d", "/c", "mklink", "/J", str(link), str(target)],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip()
            raise OSError(f"junction creation failed: {detail}")
    else:
        link.symlink_to(target, target_is_directory=True)


def build_plugin(root: Path) -> tuple[Path, dict[str, dict[str, Any]]]:
    repository = root / "collection" / "GitHub"
    plugin = repository / "research-qa-plugin"
    paper_downloader = repository / validator.PAPER_DOWNLOADER_NAME
    paper_downloader.mkdir(parents=True)
    (paper_downloader / "SKILL.md").write_text(
        "---\nname: paper-downloader\ndescription: fixture\n---\n\n# Fixture\n",
        encoding="utf-8",
    )
    skill = plugin / "skills" / validator.SKILL_NAME
    bundled = skill / "bundled"
    write_json(
        plugin / "plugin.json",
        {
            "$schema": validator.PLUGIN_SCHEMA,
            "name": validator.PLUGIN_NAME,
            "version": validator.PLUGIN_VERSION,
            "description": "Synthetic deterministic test fixture.",
        },
    )
    (skill / "SKILL.md").parent.mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(
        "---\nname: research-qa-orchestrator\n"
        'description: "Synthetic deterministic test fixture."\n---\n\n# Fixture\n',
        encoding="utf-8",
    )
    components: list[dict[str, Any]] = []
    expected = list(validator.EXPERT_COMPONENTS) + [validator.FUXI_COMPONENT]
    for component_id, source_name in expected:
        target = (
            Path("fuxi-skill")
            if component_id == "fuxi-skill"
            else Path("personas") / source_name
        )
        component_root = bundled / target
        component_root.mkdir(parents=True, exist_ok=True)
        (component_root / "SKILL.md").write_text(
            f"---\nname: {component_id}\ndescription: fixture\n---\n\n{source_name}\n",
            encoding="utf-8",
        )
        files, total_bytes = validator.inventory_tree(component_root)
        components.append(
            {
                "id": component_id,
                "source_scope": (
                    "claude-user-skills"
                    if component_id == "fuxi-skill"
                    else "minimax-user-skills"
                ),
                "source_name": source_name,
                "target": target.as_posix(),
                "file_count": len(files),
                "total_bytes": total_bytes,
                "skill_md_sha256": sha(component_root / "SKILL.md"),
                "tree_sha256": validator.tree_sha256(files),
            }
        )
    write_json(
        bundled / "source-manifest.json",
        {
            "schema": validator.BUNDLED_SCHEMA,
            "portable": True,
            "absolute_source_paths_persisted": False,
            "symlinks_allowed": False,
            "payload_excludes": [".DS_Store", ".git", "__pycache__", "*.pyc"],
            "tree_hash_algorithm": validator.TREE_HASH_ALGORITHM,
            "components": components,
        },
    )
    for relative in validator.CRITICAL_RUNTIME_RELATIVES:
        path = plugin / relative
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"# Deterministic fixture for {relative.as_posix()}\n",
            encoding="utf-8",
        )
    _, records = validator.validate_bundled_manifest(
        plugin.resolve(),
        (bundled / "source-manifest.json").resolve(),
    )
    return plugin, records


def source_row(index: int, reviewable: bool = True) -> dict[str, Any]:
    row: dict[str, Any] = {
        "source_id": f"src-{index:03d}",
        "title": f"Publication {index}",
        "authors": ["Author A"],
        "year": 2020,
        "source_type": "article",
        "document_kind": "paper",
        "publication_identity": f"doi:10.0000/fixture.{index}",
        "doi": f"10.0000/fixture.{index}",
        "pmid": None,
        "pmcid": None,
        "original_publication_url": f"https://example.invalid/paper/{index}",
        "source_origin": "online",
        "local_source_path": None,
        "online_source_url": f"https://example.invalid/paper/{index}",
        "access_depth": "fulltext",
        "access_status": "downloaded",
        "download_attempted": True,
        "local_payload_path": f"payload/sources/files/src-{index:03d}.pdf",
        "payload_sha256": None,
        "payload_bytes": None,
        "acquisition_receipt_path": f"payload/sources/acquisition-receipts/src-{index:03d}.json",
        "akashic_registry_path": None,
        "failure_reason": None,
        "duplicate_of": None,
        "on_scope": True,
        "identifier_verified": True,
        "reviewable": reviewable,
        "evidence_quality": "medium",
        "usage_role": "support",
        "review_depth": "screened",
        "local_grade": "unknown",
        "method_flags": [],
        "funding_flags": [],
        "diet_flags": [],
        "record_sha256": "",
    }
    row["record_sha256"] = validator.sha256_bytes(
        validator.canonical_without(row, "record_sha256")
    )
    return row


def minimal_valid_pdf_bytes(label: str) -> bytes:
    """Build a real classic-xref PDF larger than the validator's 5 KiB gate."""

    content = (
        b"q\n0 0 100 100 re S\nQ\n" * 260
        + f"% fixture {label}\n".encode("utf-8")
    )
    objects = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        3: (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 100 100] "
            b"/Contents 4 0 R >>"
        ),
        4: (
            f"<< /Length {len(content)} >>\nstream\n".encode("ascii")
            + content
            + b"endstream"
        ),
    }
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets: dict[int, int] = {}
    for object_number, body in objects.items():
        offsets[object_number] = len(output)
        output.extend(f"{object_number} 0 obj\n".encode("ascii"))
        output.extend(body)
        output.extend(b"\nendobj\n")
    xref_offset = len(output)
    output.extend(b"xref\n0 5\n")
    output.extend(b"0000000000 65535 f \n")
    for object_number in range(1, 5):
        output.extend(f"{offsets[object_number]:010d} 00000 n \n".encode("ascii"))
    output.extend(b"trailer\n<< /Size 5 /Root 1 0 R >>\n")
    output.extend(f"startxref\n{xref_offset}\n%%EOF\n".encode("ascii"))
    assert len(output) > validator.MIN_PDF_BYTES
    return bytes(output)


def minimal_xref_stream_pdf_bytes() -> bytes:
    output = bytearray(b"%PDF-1.5\n%\xe2\xe3\xcf\xd3\n")
    offsets: dict[int, int] = {}
    objects = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: b"<< /Type /Pages /Kids [] /Count 0 >>",
    }
    for object_number, body in objects.items():
        offsets[object_number] = len(output)
        output.extend(f"{object_number} 0 obj\n".encode("ascii"))
        output.extend(body)
        output.extend(b"\nendobj\n")
    xref_offset = len(output)
    entries = [
        (0, 0, 65535),
        (1, offsets[1], 0),
        (1, offsets[2], 0),
        (1, xref_offset, 0),
    ]
    xref_data = b"".join(
        entry_type.to_bytes(1, "big")
        + field_two.to_bytes(4, "big")
        + field_three.to_bytes(2, "big")
        for entry_type, field_two, field_three in entries
    )
    output.extend(b"3 0 obj\n")
    output.extend(
        (
            "<< /Type /XRef /Size 4 /Root 1 0 R /W [1 4 2] "
            f"/Index [0 4] /Length {len(xref_data)} >>\nstream\n"
        ).encode("ascii")
    )
    output.extend(xref_data)
    output.extend(b"\nendstream\nendobj\n")
    output.extend(f"startxref\n{xref_offset}\n%%EOF\n".encode("ascii"))
    return bytes(output)


class RunFixture:
    def __init__(
        self,
        root: Path,
        plugin: Path,
        components: dict[str, dict[str, Any]],
        *,
        reviewable_count: int = 30,
        expert_reworks: dict[str, int] | None = None,
        exhausted_expert: str | None = None,
        synthesis_reworks: int = 0,
        omit_retry_event: bool = False,
        topic_context_reuse: bool = False,
        expert_context_reuse: bool = False,
        tiny_expert: str | None = None,
        reuse_first_source: bool = False,
        early_expert_event: bool = False,
    ) -> None:
        self.root = root
        self.plugin = plugin
        self.components = components
        self.submissions_root = root / "12-agent-submissions"
        self.submissions_root.mkdir()
        self.package_date = "2026-08-07"
        self.package_relative_path = "2026/08/07/research-qa-fixture"
        self.day_dir = self.submissions_root / "2026" / "08" / "07"
        self.day_dir.mkdir(parents=True)
        self.package = self.day_dir / "research-qa-fixture"
        self.package.mkdir()
        write_json(
            self.package / ".reservation.json",
            {
                "schema": "akashic-package-reservation/v2",
                "package_id": self.package.name,
                "path": f"12-agent-submissions/{self.package_relative_path}",
                "agent": "codex",
                "created_at": NOW,
                "lifecycle_state": "pending",
            },
        )
        (self.package / "manifest.yaml").write_text(
            "schema_version: 2\n"
            f"package_id: {self.package.name}\n"
            "agent: codex\n"
            "status: pending\n"
            f"created_at: '{NOW}'\n"
            f"updated_at: '{NOW}'\n"
            "task: fixture research QA run\n"
            "formal_absorption: false\n"
            "next_action: review candidate\n",
            encoding="utf-8",
        )
        (self.package / "submission.md").write_text("# Reserved fixture\n", encoding="utf-8")
        self.rule = root / "live-rule-fixture.md"
        self.rule.write_text("# live Akashic rule fixture\n", encoding="utf-8")
        self.rule_sha = sha(self.rule)
        self.runtime = {"kind": "codex", "auditor_kind": "codex-independent"}
        self.paper_downloader_root = self.plugin.parent / validator.PAPER_DOWNLOADER_NAME
        self.paper_downloader_consumer = root / "agent-skills" / validator.PAPER_DOWNLOADER_NAME
        self.paper_downloader_consumer.parent.mkdir()
        create_directory_link(
            self.paper_downloader_consumer,
            self.paper_downloader_root,
        )
        self.reviewable_count = reviewable_count
        self.expert_reworks = expert_reworks or {}
        self.exhausted_expert = exhausted_expert
        self.synthesis_reworks = synthesis_reworks
        self.omit_retry_event = omit_retry_event
        self.topic_context_reuse = topic_context_reuse
        self.expert_context_reuse = expert_context_reuse
        self.tiny_expert = tiny_expert
        self.reuse_first_source = reuse_first_source
        self.early_expert_event = early_expert_event
        self.akashic_root = root / "Akashic"
        (self.akashic_root / "03-metadata" / "registry").mkdir(parents=True)
        self.events: list[dict[str, Any]] = []
        self.state: str | None = None
        self.accepted_experts: dict[str, dict[str, Any]] = {}
        self.expert_audits: dict[str, list[dict[str, Any]]] = {}
        self.synthesis_audits: list[dict[str, Any]] = []
        self.plugin_report = validator.validate_plugin(plugin)
        self._build()

    def rel(self, path: Path) -> str:
        return path.relative_to(self.package).as_posix()

    def add_event(
        self,
        event_type: str,
        state_to: str,
        artifact: Path | None = None,
    ) -> None:
        self.events.append(
            {
                "event_type": event_type,
                "state_from": self.state,
                "state_to": state_to,
                "artifact": artifact,
            }
        )
        self.state = state_to

    def _operation_receipt_path(self, role: str, key: str) -> Path:
        safe_key = key.replace("/", "-")
        return (
            self.package
            / "payload"
            / "runtime-receipts"
            / "tasks"
            / f"{role}-{safe_key}.json"
        )

    def _executor_record(
        self,
        *,
        kind: str,
        role: str,
        context_id: str,
        key: str,
    ) -> dict[str, Any]:
        return {
            "runtime": "codex",
            "kind": kind,
            "context_id": context_id,
            "operation_receipt_path": self.rel(
                self._operation_receipt_path(role, key)
            ),
        }

    def _write_runtime_operation(
        self,
        artifact: Path,
        *,
        role: str,
        context_id: str,
        key: str,
    ) -> None:
        receipt_path = self._operation_receipt_path(role, key)
        write_json(
            receipt_path,
            {
                "schema": validator.RUNTIME_OPERATION_SCHEMA,
                "evidence_origin": "runtime_tool_result",
                "runtime": "codex",
                "role": role,
                "operation_id": f"operation-{role}-{key}",
                "status": "succeeded",
                "context_id": context_id,
                "artifact_path": self.rel(artifact),
                "artifact_sha256": sha(artifact),
                "started_at": NOW,
                "completed_at": NOW,
                "create_thread": {
                    "actual_tool": "codex_app__create_thread",
                    "status": "created_confirmed",
                    "surface": "visible_thread",
                    "requested_route": "sol-max",
                    "task_kind": "codex",
                    "thread_id": context_id,
                    "client_thread_id": None,
                    "host_id": "local-host",
                    "prompt_verified": "readback",
                    "failure": None,
                },
                "result_readback": {
                    "status": "succeeded",
                    "thread_id": context_id,
                    "host_id": "local-host",
                    "artifact_path": self.rel(artifact),
                    "artifact_sha256": sha(artifact),
                    "read_at": NOW,
                },
            },
        )

    def _write_attempt(
        self,
        lane: Path,
        artifact_type: str,
        artifact_id: str,
        attempt: int,
        decision: str,
        previous_audit_sha: str | None,
    ) -> tuple[dict[str, Any], str]:
        prefix = f"attempt-{attempt:02d}"
        candidate = lane / f"{prefix}.md"
        candidate.parent.mkdir(parents=True, exist_ok=True)
        if artifact_type == "expert" and artifact_id == self.tiny_expert:
            candidate_text = "# placeholder\n"
        else:
            sections = 14 if artifact_type == "expert" else 28
            candidate_text = f"# {artifact_id} candidate attempt {attempt}\n\n" + "\n\n".join(
                f"## Evidence section {index}\nSource-backed reasoning, counterevidence, uncertainty, and scope boundary for {artifact_id}."
                for index in range(1, sections + 1)
            ) + "\n"
        candidate.write_text(candidate_text, encoding="utf-8")
        author_context = (
            "shared-expert-context"
            if artifact_type == "expert" and attempt == 1 and self.expert_context_reuse
            else f"author-{artifact_id}-{attempt}"
        )
        author_role = f"{artifact_type}_author"
        author_key = f"{artifact_id}-{attempt:02d}-author"
        receipt: dict[str, Any] = {
            "schema_version": 1,
            "artifact_type": artifact_type,
            "artifact_id": artifact_id,
            "attempt": attempt,
            "candidate_path": self.rel(candidate),
            "candidate_sha256": sha(candidate),
            "source_set_sha256": self.source_set_sha,
            "corpus_delivery": {
                "frozen_set_path": "payload/sources/frozen-set.json",
                "frozen_set_sha256": self.frozen_set_sha,
                "source_set_sha256": self.source_set_sha,
                "reviewable_source_count": self.reviewable_count,
                "reviewable_source_ids_sha256": self.reviewable_ids_sha,
                "delivered_at": NOW,
            },
            "akashic_rule": {
                "path": str(validator.LIVE_RULE),
                "sha256": self.rule_sha,
                "bytes": self.rule.stat().st_size,
                "read_at": NOW,
            },
            "executor": self._executor_record(
                kind="author",
                role=author_role,
                context_id=author_context,
                key=author_key,
            ),
            "retry_of_audit_sha256": previous_audit_sha,
            "created_at": NOW,
        }
        self._write_runtime_operation(
            candidate,
            role=author_role,
            context_id=author_context,
            key=author_key,
        )
        if artifact_type == "expert":
            component = self.components[artifact_id]
            receipt["bundled_skill"] = {
                "manifest_component_id": artifact_id,
                "source_name": component["source_name"],
                "path": component["skill_path"],
                "skill_md_sha256": component["skill_md_sha256"],
                "tree_sha256": component["tree_sha256"],
            }
            coverage_path = lane / f"{prefix}.coverage.json"
            write_json(
                coverage_path,
                {
                    "schema_version": 1,
                    "artifact_id": artifact_id,
                    "attempt": attempt,
                    "source_set_sha256": self.source_set_sha,
                    "reviewed_source_ids": self.reviewable_source_ids,
                    "completed_at": NOW,
                },
            )
            receipt["source_coverage_path"] = self.rel(coverage_path)
            receipt["source_coverage_sha256"] = sha(coverage_path)
        else:
            receipt["accepted_expert_inputs"] = [
                {
                    key: self.accepted_experts[component_id][key]
                    for key in (
                        "artifact_id",
                        "candidate_path",
                        "candidate_sha256",
                        "audit_path",
                        "audit_sha256",
                    )
                }
                for component_id, _ in validator.EXPERT_COMPONENTS
            ]
        receipt_path = lane / f"{prefix}.receipt.json"
        write_json(receipt_path, receipt)
        auditor_context = f"auditor-{artifact_id}-{attempt}"
        auditor_role = f"{artifact_type}_auditor"
        auditor_key = f"{artifact_id}-{attempt:02d}-auditor"
        audit = {
            "schema_version": 1,
            "artifact_type": artifact_type,
            "artifact_id": artifact_id,
            "attempt": attempt,
            "decision": decision,
            "findings": [] if decision == "pass" else ["fixture rejection"],
            "required_changes": [] if decision == "pass" else ["make fixture revision"],
            "evidence_refs": [self.rel(candidate)],
            "quality_checks": {
                "nonempty": decision == "pass",
                "substantive": decision == "pass",
                "citations_traceable": decision == "pass",
                "counterevidence_addressed": decision == "pass",
                "uncertainty_stated": decision == "pass",
                "medical_boundary_observed": decision == "pass",
                (
                    "source_coverage_complete"
                    if artifact_type == "expert"
                    else "expert_roster_complete"
                ): decision == "pass",
            },
            "auditor": self._executor_record(
                kind="codex-independent",
                role=auditor_role,
                context_id=auditor_context,
                key=auditor_key,
            ),
            "input_sha256": sha(receipt_path),
            "artifact_sha256": sha(candidate),
            "akashic_rule": {
                "path": str(validator.LIVE_RULE),
                "sha256": self.rule_sha,
                "bytes": self.rule.stat().st_size,
                "read_at": NOW,
            },
            "decided_at": NOW,
        }
        audit_path = lane / f"{prefix}.audit.json"
        write_json(audit_path, audit)
        self._write_runtime_operation(
            audit_path,
            role=auditor_role,
            context_id=auditor_context,
            key=auditor_key,
        )
        record = {
            "attempt": attempt,
            "decision": decision,
            "receipt_path": self.rel(receipt_path),
            "receipt_sha256": sha(receipt_path),
            "audit_path": self.rel(audit_path),
            "audit_sha256": sha(audit_path),
        }
        binding = {
            "artifact_id": artifact_id,
            "attempt": attempt,
            "candidate_path": self.rel(candidate),
            "candidate_sha256": sha(candidate),
            "audit_path": self.rel(audit_path),
            "audit_sha256": sha(audit_path),
        }
        return {"record": record, "binding": binding}, sha(audit_path)

    def _build_topic(self) -> None:
        topic = self.package / "payload" / "topic"
        question = topic / "question.json"
        write_json(
            question,
            {
                "schema_version": 1,
                "initiated_by": "user",
                "question": "What does the complete evidence base show?",
                "output_language": "zh-CN",
                "exclusions": ["personal diagnosis"],
                "locked_at": NOW,
            },
        )
        contribution_bindings: list[dict[str, str]] = []
        for component_id, _ in validator.EXPERT_COMPONENTS:
            component = self.components[component_id]
            contribution = topic / "contributions" / f"{component_id}.json"
            context_id = (
                "shared-topic-context"
                if self.topic_context_reuse
                else f"topic-author-{component_id}"
            )
            operation_key = f"topic-{component_id}"
            write_json(
                contribution,
                {
                    "schema_version": 1,
                    "artifact_id": component_id,
                    "bundled_skill": {
                        "manifest_component_id": component_id,
                        "source_name": component["source_name"],
                        "path": component["skill_path"],
                        "skill_md_sha256": component["skill_md_sha256"],
                        "tree_sha256": component["tree_sha256"],
                    },
                    "executor": self._executor_record(
                        kind="author",
                        role="topic_expert",
                        context_id=context_id,
                        key=operation_key,
                    ),
                    "research_angles": [f"Angle from {component_id}"],
                    "search_terms": [f"query {component_id}"],
                    "candidate_exclusions": [],
                    "created_at": NOW,
                },
            )
            self._write_runtime_operation(
                contribution,
                role="topic_expert",
                context_id=context_id,
                key=operation_key,
            )
            contribution_bindings.append(
                {
                    "artifact_id": component_id,
                    "path": self.rel(contribution),
                    "sha256": sha(contribution),
                }
            )
        self.research_brief = topic / "research-brief.json"
        brief_context = "topic-integrator"
        brief_operation_key = "research-brief"
        write_json(
            self.research_brief,
            {
                "schema_version": 1,
                "question_path": self.rel(question),
                "question_sha256": sha(question),
                "contributions": contribution_bindings,
                "author_context_id": brief_context,
                "executor": self._executor_record(
                    kind="integrator",
                    role="topic_integrator",
                    context_id=brief_context,
                    key=brief_operation_key,
                ),
                "search_queries": ["complete fixture evidence query"],
                "inclusion_criteria": ["eligible scholarly publication"],
                "exclusion_criteria": ["duplicate or non-scholarly item"],
                "frozen_at": NOW,
            },
        )
        self._write_runtime_operation(
            self.research_brief,
            role="topic_integrator",
            context_id=brief_context,
            key=brief_operation_key,
        )

    def _build_sources(self) -> None:
        sources = self.package / "payload" / "sources"
        sources.mkdir(parents=True)
        rows = [source_row(index) for index in range(1, self.reviewable_count + 1)]
        self.acquisition_operation_receipts_structurally_validated = 0
        for index, row in enumerate(rows, 1):
            payload = self.package / row["local_payload_path"]
            payload.parent.mkdir(parents=True, exist_ok=True)
            pdf_bytes = minimal_valid_pdf_bytes(f"publication-{index}")
            payload.write_bytes(pdf_bytes)
            lookup: dict[str, Any] = {
                "performed": True,
                "result": "miss",
                "checked_at": NOW,
            }
            validation_kind = "pdf"
            download_started_at: str | None = NOW
            download_completed_at: str | None = NOW
            if index == 1 and self.reuse_first_source:
                external_relative = Path("01-sources/pdf/src-001.pdf")
                external = self.akashic_root / external_relative
                external.parent.mkdir(parents=True, exist_ok=True)
                external.write_bytes(pdf_bytes)
                registry = self.akashic_root / "03-metadata" / "registry" / "src-akashic-001.json"
                write_json(
                    registry,
                    {
                        "contract": "akashic-v2-source-record/v1",
                        "source_id": "src-akashic-001",
                        "source_file_path": external_relative.as_posix(),
                    },
                )
                row.update(
                    {
                        "source_origin": "local",
                        "local_source_path": str(external),
                        "online_source_url": None,
                        "access_status": "akashic_reused",
                        "download_attempted": False,
                        "akashic_registry_path": str(registry),
                    }
                )
                lookup = {
                    "performed": True,
                    "result": "reused",
                    "source_id": "src-akashic-001",
                    "checked_at": NOW,
                }
                validation_kind = "akashic_reuse"
                download_started_at = None
                download_completed_at = None
            row["payload_sha256"] = sha(payload)
            row["payload_bytes"] = payload.stat().st_size
            row["record_sha256"] = validator.sha256_bytes(
                validator.canonical_without(row, "record_sha256")
            )
            operation_relative: str | None = None
            if row["download_attempted"]:
                operation_path = (
                    self.package
                    / "payload"
                    / "runtime-receipts"
                    / "acquisition"
                    / f"{row['source_id']}.json"
                )
                write_json(
                    operation_path,
                    {
                        "schema": validator.ACQUISITION_OPERATION_SCHEMA,
                        "evidence_origin": "runtime_tool_result",
                        "executor_name": validator.PAPER_DOWNLOADER_NAME,
                        "executor_skill_sha256": sha(
                            self.paper_downloader_root / "SKILL.md"
                        ),
                        "actual_tool": "paper-downloader",
                        "operation_id": f"acquire-{row['source_id']}",
                        "status": "completed",
                        "source_id": row["source_id"],
                        "publication_identity": row["publication_identity"],
                        "result": {
                            "access_status": row["access_status"],
                            "local_payload_path": row["local_payload_path"],
                            "payload_sha256": row["payload_sha256"],
                            "payload_bytes": row["payload_bytes"],
                        },
                        "started_at": NOW,
                        "completed_at": NOW,
                    },
                )
                operation_relative = self.rel(operation_path)
                self.acquisition_operation_receipts_structurally_validated += 1
            receipt = self.package / row["acquisition_receipt_path"]
            write_json(
                receipt,
                {
                    "schema_version": 1,
                    "source_id": row["source_id"],
                    "publication_identity": row["publication_identity"],
                    "status": row["access_status"],
                    "download_attempted": row["download_attempted"],
                    "local_payload_path": row["local_payload_path"],
                    "payload_sha256": row["payload_sha256"],
                    "payload_bytes": row["payload_bytes"],
                    "akashic_lookup": lookup,
                    "download_started_at": download_started_at,
                    "download_completed_at": download_completed_at,
                    "validation": {
                        "exists": True,
                        "kind": validation_kind,
                        "magic": "%PDF" if validation_kind == "pdf" else None,
                    },
                    "executor_operation_receipt_path": operation_relative,
                    "recorded_at": NOW,
                },
            )
        write_jsonl(sources / "inventory.jsonl", rows)
        (sources / "search-log.md").write_text("# fixture search log\n", encoding="utf-8")
        (sources / "access-log.jsonl").write_bytes(b"")
        self.reviewable_source_ids = sorted(row["source_id"] for row in rows if row["reviewable"])
        self.reviewable_ids_sha = validator.source_ids_sha256(self.reviewable_source_ids)
        status_counts: dict[str, int] = {}
        for row in rows:
            status_counts[row["access_status"]] = status_counts.get(row["access_status"], 0) + 1
        acquisition_summary = sources / "acquisition-summary.json"
        collector_context = "source-collector"
        collector_operation_key = "source-collection"
        write_json(
            acquisition_summary,
            {
                "schema_version": 1,
                "total_source_rows": len(rows),
                "reviewable_source_count": self.reviewable_count,
                "unique_publication_count": len(rows),
                "status_counts": status_counts,
                "all_akashic_lookups_completed": True,
                "download_payloads_structurally_validated": True,
                "executor_operation_receipts_structurally_validated": (
                    self.acquisition_operation_receipts_structurally_validated
                ),
                "runtime_execution_verified": False,
                "collector_context_id": collector_context,
                "executor": self._executor_record(
                    kind="collector",
                    role="source_collector",
                    context_id=collector_context,
                    key=collector_operation_key,
                ),
                "completed_at": NOW,
            },
        )
        self._write_runtime_operation(
            acquisition_summary,
            role="source_collector",
            context_id=collector_context,
            key=collector_operation_key,
        )
        source_files, _ = validator.inventory_tree(
            sources,
            exclude_relatives={"frozen-set.json"},
        )
        self.source_set_sha = validator.tree_sha256(source_files)
        write_json(
            sources / "frozen-set.json",
            {
                "schema_version": 1,
                "inventory_path": "payload/sources/inventory.jsonl",
                "inventory_sha256": sha(sources / "inventory.jsonl"),
                "tree_hash_algorithm": validator.TREE_HASH_ALGORITHM,
                "source_set_sha256": self.source_set_sha,
                "reviewable_source_count": self.reviewable_count,
                "reviewable_source_ids_sha256": self.reviewable_ids_sha,
                "acquisition_summary_sha256": sha(acquisition_summary),
                "frozen_at": NOW,
            },
        )
        self.frozen_set_sha = sha(sources / "frozen-set.json")

    def _build_receipts(self) -> None:
        receipts = self.package / "payload" / "receipts"
        discovery_path = (
            self.package
            / "payload"
            / "runtime-receipts"
            / "paper-downloader-discovery.json"
        )
        write_json(
            discovery_path,
            {
                "schema": validator.SKILL_DISCOVERY_SCHEMA,
                "evidence_origin": "runtime_skill_catalog",
                "runtime": "codex",
                "status": "discovered",
                "receipt_id": "discovery-paper-downloader-001",
                "consumer_skill_path": str(
                    self.paper_downloader_consumer / "SKILL.md"
                ),
                "canonical_realpath": str(self.paper_downloader_root.resolve()),
                "skill_sha256": sha(self.paper_downloader_root / "SKILL.md"),
                "observed_at": NOW,
            },
        )
        write_json(
            receipts / "run-init.json",
            {
                "schema_version": 1,
                "task_id": "fixture-task",
                "package_id": self.package.name,
                "package_date": self.package_date,
                "package_relative_path": self.package_relative_path,
                "package_path": str(self.package.resolve()),
                "creation_mode": "akashic_v2_reserved",
                "reservation_path": ".reservation.json",
                "reservation_sha256": sha(self.package / ".reservation.json"),
                "akashic_manifest_path": "manifest.yaml",
                "akashic_manifest_sha256": sha(self.package / "manifest.yaml"),
                "runtime": self.runtime,
                "acquisition_executor": {
                    "name": validator.PAPER_DOWNLOADER_NAME,
                    "registered_skill_path": str(
                        self.paper_downloader_consumer / "SKILL.md"
                    ),
                    "canonical_realpath": str(self.paper_downloader_root.resolve()),
                    "skill_sha256": sha(self.paper_downloader_root / "SKILL.md"),
                    "verified_at": NOW,
                    "consumer_link_state": "linked",
                    "discovery_receipt_path": self.rel(discovery_path),
                    "discovery_receipt_sha256": sha(discovery_path),
                },
                "initialized_at": NOW,
            },
        )
        plugin_result = (
            self.package
            / "payload"
            / "validation"
            / "plugin-validator-result.json"
        )
        write_json(plugin_result, self.plugin_report)
        plugin_validation_path = receipts / "plugin-validation.json"
        write_json(
            plugin_validation_path,
            {
                "schema": validator.PLUGIN_RECEIPT_SCHEMA,
                "schema_version": 2,
                "ok": True,
                "plugin": self.plugin_report["plugin"],
                "runtime_tree": self.plugin_report["runtime_tree"],
                "critical_files": self.plugin_report["critical_files"],
                "bundled": {
                    "manifest_path": validator.SOURCE_MANIFEST_RELATIVE.as_posix(),
                    "manifest_sha256": self.plugin_report[
                        "bundled_manifest_sha256"
                    ],
                    "tree": self.plugin_report["bundled_tree"],
                },
                "validator": {
                    "path": validator.VALIDATOR_RELATIVE.as_posix(),
                    "sha256": self.plugin_report["critical_files"][
                        validator.VALIDATOR_RELATIVE.as_posix()
                    ],
                    "command": validator.plugin_validation_command(
                        self.plugin.resolve()
                    ),
                },
                "validator_result": {
                    "path": self.rel(plugin_result),
                    "sha256": sha(plugin_result),
                },
                "git_observation": self.plugin_report["git_observation"],
                "validated_at": NOW,
            },
        )
        self.plugin_validation_binding = {
            "path": self.rel(plugin_validation_path),
            "sha256": sha(plugin_validation_path),
            "schema": validator.PLUGIN_RECEIPT_SCHEMA,
            "runtime_tree_sha256": self.plugin_report["runtime_tree"][
                "tree_sha256"
            ],
            "git_observation": self.plugin_report["git_observation"],
        }
        write_json(
            receipts / "live-rule.json",
            {
                "schema_version": 1,
                "path": str(validator.LIVE_RULE),
                "sha256": self.rule_sha,
                "bytes": self.rule.stat().st_size,
                "read_at": NOW,
            },
        )
        material_audit_path = receipts / "material-audit.json"
        material_auditor_context = "material-auditor"
        material_auditor_key = "material-audit"
        write_json(
            material_audit_path,
            {
                "schema_version": 1,
                "artifact_type": "materials",
                "decision": "pass",
                "source_set_sha256": self.source_set_sha,
                "reviewable_source_count": self.reviewable_count,
                "reviewable_source_ids_sha256": self.reviewable_ids_sha,
                "acquisition_summary_sha256": sha(
                    self.package / "payload" / "sources" / "acquisition-summary.json"
                ),
                "quality_checks": {
                    "akashic_reuse_verified": True,
                    "download_claims_verified": True,
                    "publication_identities_unique": True,
                    "reviewable_threshold_met": True,
                    "corpus_complete": True,
                },
                "evidence_refs": ["payload/sources/acquisition-summary.json"],
                "akashic_rule": {
                    "path": str(validator.LIVE_RULE),
                    "sha256": self.rule_sha,
                    "bytes": self.rule.stat().st_size,
                    "read_at": NOW,
                },
                "author_context_id": "source-collector",
                "auditor": self._executor_record(
                    kind="codex-independent",
                    role="material_auditor",
                    context_id=material_auditor_context,
                    key=material_auditor_key,
                ),
                "decided_at": NOW,
            },
        )
        self._write_runtime_operation(
            material_audit_path,
            role="material_auditor",
            context_id=material_auditor_context,
            key=material_auditor_key,
        )

    def _build_experts(self) -> None:
        for component_id, _ in validator.EXPERT_COMPONENTS:
            lane = self.package / "payload" / "experts" / component_id
            reworks = (
                3
                if component_id == self.exhausted_expert
                else self.expert_reworks.get(component_id, 0)
            )
            attempts = reworks + 1
            previous_sha: str | None = None
            records: list[dict[str, Any]] = []
            last_binding: dict[str, Any] | None = None
            for attempt in range(1, attempts + 1):
                decision = (
                    "reject"
                    if component_id == self.exhausted_expert or attempt <= reworks
                    else "pass"
                )
                built, previous_sha = self._write_attempt(
                    lane,
                    "expert",
                    component_id,
                    attempt,
                    decision,
                    previous_sha,
                )
                records.append(built["record"])
                last_binding = built["binding"]
            self.expert_audits[component_id] = records
            if component_id != self.exhausted_expert:
                assert last_binding is not None
                write_json(lane / "accepted.json", {"schema_version": 1, **last_binding})
                self.accepted_experts[component_id] = last_binding

    def _build_synthesis(self) -> None:
        if self.exhausted_expert:
            return
        lane = self.package / "payload" / "synthesis"
        previous_sha: str | None = None
        last_binding: dict[str, Any] | None = None
        for attempt in range(1, self.synthesis_reworks + 2):
            decision = "reject" if attempt <= self.synthesis_reworks else "pass"
            built, previous_sha = self._write_attempt(
                lane,
                "synthesis",
                "final-synthesis",
                attempt,
                decision,
                previous_sha,
            )
            self.synthesis_audits.append(built["record"])
            last_binding = built["binding"]
        assert last_binding is not None
        write_json(lane / "accepted.json", {"schema_version": 1, **last_binding})
        accepted_candidate = self.package / last_binding["candidate_path"]
        (self.package / "submission.md").write_bytes(accepted_candidate.read_bytes())
        self.accepted_synthesis = last_binding

    def _build_manifest(self) -> None:
        synthesis_attempt = getattr(self, "accepted_synthesis", {"attempt": None})["attempt"]
        runtime_operation_receipts_structurally_validated = (
            11
            + 2 * sum(len(records) for records in self.expert_audits.values())
            + 2 * len(self.synthesis_audits)
        )
        write_json(
            self.package / "payload" / "receipts" / "run-manifest.json",
            {
                "schema_version": 1,
                "package_id": self.package.name,
                "package_date": self.package_date,
                "package_relative_path": self.package_relative_path,
                "status": validator.STRUCTURAL_RUN_STATUS,
                "runtime_attestation": {
                    "evidence_scope": "package_local_only",
                    "independent_host_attestation": "not_provided",
                    "runtime_execution_verified": False,
                    "run_success_verified": False,
                },
                "task_id": "fixture-task",
                "runtime": self.runtime,
                "plugin": {
                    "name": validator.PLUGIN_NAME,
                    "version": validator.PLUGIN_VERSION,
                },
                "plugin_validation": self.plugin_validation_binding,
                "formal_absorption": "not_authorized",
                "plugin_installation": "not_performed",
                "fuxi": "available_not_invoked",
                "reviewable_source_count": self.reviewable_count,
                "reviewable_source_ids_sha256": self.reviewable_ids_sha,
                "source_set_sha256": self.source_set_sha,
                "acquisition_executor_evidence": {
                    "source_state": "validated",
                    "consumer_link_state": "linked",
                    "runtime_discovery_state": validator.RUNTIME_NOT_VERIFIED,
                    "discovery_receipt_structurally_validated": True,
                    "operation_receipts_structurally_validated": (
                        self.acquisition_operation_receipts_structurally_validated
                    ),
                    "runtime_execution_verified": False,
                },
                "research_brief": {
                    "path": self.rel(self.research_brief),
                    "sha256": sha(self.research_brief),
                },
                "akashic_rule": {
                    "path": str(validator.LIVE_RULE),
                    "sha256": self.rule_sha,
                },
                "material_audit": {
                    "decision": "pass",
                    "receipt": "payload/receipts/material-audit.json",
                },
                "experts_passed": len(self.accepted_experts),
                "synthesis_audit": {
                    "decision": "pass",
                    "accepted_attempt": synthesis_attempt,
                },
                "receipt_chain_complete": True,
                "runtime_operation_receipts_structurally_validated": (
                    runtime_operation_receipts_structurally_validated
                ),
            },
        )

    def _build_events(self) -> str:
        receipts = self.package / "payload" / "receipts"
        self.add_event("run_initialized", "initialized", receipts / "run-init.json")
        self.add_event("plugin_validated", "plugin_validated", receipts / "plugin-validation.json")
        self.add_event("live_rule_pinned", "live_rule_pinned", receipts / "live-rule.json")
        self.add_event("topic_locked", "topic_locked", self.package / "payload/topic/question.json")
        self.add_event("topic_experts_completed", "topic_experts_completed")
        self.add_event("research_brief_frozen", "research_brief_frozen", self.research_brief)
        self.add_event("collection_started", "collection_in_progress")
        acquisition_summary = self.package / "payload/sources/acquisition-summary.json"
        self.add_event("akashic_reuse_checked", "collection_in_progress", acquisition_summary)
        self.add_event("collection_completed", "collection_completed", acquisition_summary)
        self.add_event("material_audit_passed", "sources_audited", receipts / "material-audit.json")
        if self.early_expert_event:
            first = self.expert_audits[validator.EXPERT_COMPONENTS[0][0]][0]
            self.add_event(
                "expert_passed",
                "experts_in_progress",
                self.package / first["audit_path"],
            )
        self.add_event("sources_frozen", "sources_frozen", self.package / "payload/sources/frozen-set.json")
        for component_id, _ in validator.EXPERT_COMPONENTS:
            for position, record in enumerate(self.expert_audits[component_id]):
                audit_path = self.package / record["audit_path"]
                if record["decision"] == "pass":
                    self.add_event("expert_passed", "experts_in_progress", audit_path)
                else:
                    self.add_event("expert_attempt_rejected", "experts_in_progress", audit_path)
                    if position + 1 < len(self.expert_audits[component_id]):
                        next_receipt = self.package / self.expert_audits[component_id][position + 1]["receipt_path"]
                        if not self.omit_retry_event:
                            self.add_event("expert_retry_dispatched", "experts_in_progress", next_receipt)
        self.add_event("experts_8_of_8_passed", "experts_8_of_8_passed")
        for position, record in enumerate(self.synthesis_audits):
            audit_path = self.package / record["audit_path"]
            if record["decision"] == "pass":
                self.add_event("synthesis_passed", "synthesis_passed", audit_path)
            else:
                self.add_event("synthesis_attempt_rejected", "synthesis_in_progress", audit_path)
                next_receipt = self.package / self.synthesis_audits[position + 1]["receipt_path"]
                if not self.omit_retry_event:
                    self.add_event("synthesis_retry_dispatched", "synthesis_in_progress", next_receipt)
        self.add_event("chain_validated", "chain_validated")
        self.add_event(
            "structure_validated_runtime_unverified",
            validator.RUNTIME_NOT_VERIFIED,
        )
        output: list[bytes] = []
        previous: str | None = None
        for sequence, item in enumerate(self.events, 1):
            artifact = item["artifact"]
            row = {
                "sequence": sequence,
                "event_id": f"evt-{sequence:03d}",
                "event_type": item["event_type"],
                "state_from": item["state_from"],
                "state_to": item["state_to"],
                "artifact_path": self.rel(artifact) if artifact else None,
                "artifact_sha256": sha(artifact) if artifact else None,
                "previous_event_sha256": previous,
                "recorded_at": NOW,
            }
            raw = (
                json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
                + b"\n"
            )
            output.append(raw)
            previous = hashlib.sha256(raw).hexdigest()
        events_path = self.package / "payload" / "events.jsonl"
        events_path.parent.mkdir(parents=True, exist_ok=True)
        events_path.write_bytes(b"".join(output))
        assert previous is not None
        return previous

    def _build(self) -> None:
        self._build_topic()
        self._build_sources()
        self._build_receipts()
        self._build_experts()
        self._build_synthesis()
        self._build_manifest()
        if not self.exhausted_expert:
            event_head = self._build_events()
            runtime_operation_receipts_structurally_validated = (
                11
                + 2 * sum(
                    len(records) for records in self.expert_audits.values()
                )
                + 2 * len(self.synthesis_audits)
            )
            write_json(
                self.package / "payload" / "receipts" / "completion.json",
                {
                    "schema_version": 1,
                    "status": validator.STRUCTURAL_RUN_STATUS,
                    "reviewable_source_count": self.reviewable_count,
                    "reviewable_source_ids_sha256": self.reviewable_ids_sha,
                    "topic_experts_completed": 8,
                    "akashic_lookup_complete": True,
                    "download_payloads_structurally_validated": True,
                    "acquisition_operation_receipts_structurally_validated": (
                        self.acquisition_operation_receipts_structurally_validated
                    ),
                    "experts_passed": 8,
                    "synthesis_passed": True,
                    "runtime_operation_receipts_structurally_validated": (
                        runtime_operation_receipts_structurally_validated
                    ),
                    "runtime_execution_verified": False,
                    "run_success_verified": False,
                    "event_chain_head_sha256": event_head,
                    "completed_at": NOW,
                },
            )


class ValidatorTests(unittest.TestCase):
    def test_bundled_verifier_without_upstream_roots_is_not_compared(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(VERIFY_BUNDLED_PATH)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["source_comparison"], "not_compared")
        self.assertIsNone(report["sources_ok"])
        self.assertEqual(report["source_comparisons"], [])

    def test_bundled_verifier_strict_match_requires_both_roots(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(VERIFY_BUNDLED_PATH),
                "--require-source-match",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertEqual(report["source_comparison"], "not_compared")
        self.assertIsNone(report["sources_ok"])
        self.assertIn("requires both", report["error"])

    def test_bundled_source_comparison_checks_every_component(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target_root = root / "bundled"
            minimax_root = root / "minimax"
            claude_root = root / "claude"
            for component in verify_bundled.COMPONENTS:
                target = target_root / component["target"]
                upstream_root = (
                    minimax_root
                    if component["source_scope"] == "minimax-user-skills"
                    else claude_root
                )
                upstream = upstream_root / component["source_name"]
                target.mkdir(parents=True)
                upstream.mkdir(parents=True)
                content = f"{component['id']}\n"
                (target / "SKILL.md").write_text(content, encoding="utf-8")
                (upstream / "SKILL.md").write_text(content, encoding="utf-8")
            original_root = verify_bundled.ROOT
            verify_bundled.ROOT = target_root
            try:
                comparisons = verify_bundled.compare_sources(
                    minimax_root,
                    claude_root,
                )
                self.assertEqual(len(comparisons), len(verify_bundled.COMPONENTS))
                self.assertTrue(
                    all(
                        not item["missing"]
                        and not item["extra"]
                        and not item["content_mismatch"]
                        for item in comparisons
                    )
                )
                drifted = minimax_root / "Nick Norwitz" / "SKILL.md"
                drifted.write_text("drift\n", encoding="utf-8")
                comparisons = verify_bundled.compare_sources(
                    minimax_root,
                    claude_root,
                )
                nick = next(item for item in comparisons if item["id"] == "persona-01")
                self.assertEqual(nick["content_mismatch"], ["SKILL.md"])
            finally:
                verify_bundled.ROOT = original_root

    def test_bundled_inventory_rejects_symlinked_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tree = root / "tree"
            external = root / "external"
            tree.mkdir()
            external.mkdir()
            (external / "SKILL.md").write_text("linked payload\n", encoding="utf-8")
            try:
                create_directory_link(tree / "linked-directory", external)
            except OSError as error:
                self.skipTest(str(error))
            with self.assertRaisesRegex(ValueError, "symlink is forbidden"):
                verify_bundled.inventory(tree)

    def test_windows_link_targets_drop_nt_namespace_prefixes(self) -> None:
        self.assertEqual(
            validator.normalize_windows_link_target(r"\\?\C:\repo\paper-downloader"),
            r"C:\repo\paper-downloader",
        )
        self.assertEqual(
            validator.normalize_windows_link_target(
                r"\\?\UNC\server\share\paper-downloader"
            ),
            r"\\server\share\paper-downloader",
        )

    def test_paper_downloader_binding_uses_registered_canonical_source(self) -> None:
        binding = (SKILL_ROOT / "references" / "external-executors.md").read_text(
            encoding="utf-8"
        )
        workflow = (SKILL_ROOT / "references" / "workflow-contract.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("$paper-downloader", binding)
        self.assertIn("<collection>/GitHub/paper-downloader/SKILL.md", binding)
        self.assertIn("never to the `paper-downloader/src/paper-downloader`", binding)
        self.assertIn("Windows junction", binding)
        self.assertIn("proves only `consumer_link_state: linked`", binding)
        self.assertIn("acquisition-operation-receipt/v1", binding)
        self.assertIn("registered `$paper-downloader` consumer", workflow)

    def assert_run_error(
        self,
        fixture: RunFixture,
        plugin: Path,
        expected_code: str,
    ) -> None:
        with self.assertRaises(validator.ValidationError) as raised:
            validator.validate_run(
                plugin,
                fixture.package,
                submissions_root_input=fixture.submissions_root,
                live_rule_input=fixture.rule,
                akashic_root_input=fixture.akashic_root,
            )
        self.assertEqual(raised.exception.code, expected_code)

    def rewrite_download_payload(
        self,
        fixture: RunFixture,
        source_index: int,
        data: bytes,
    ) -> None:
        inventory = fixture.package / "payload/sources/inventory.jsonl"
        rows = read_jsonl(inventory)
        row = rows[source_index]
        payload = fixture.package / row["local_payload_path"]
        payload.write_bytes(data)
        row["payload_sha256"] = sha(payload)
        row["payload_bytes"] = payload.stat().st_size
        rehash_source(row)
        write_jsonl(inventory, rows)
        receipt_path = fixture.package / row["acquisition_receipt_path"]
        receipt = read_json(receipt_path)
        receipt["payload_sha256"] = row["payload_sha256"]
        receipt["payload_bytes"] = row["payload_bytes"]
        write_json(receipt_path, receipt)
        operation_path = (
            fixture.package / receipt["executor_operation_receipt_path"]
        )
        operation = read_json(operation_path)
        operation["result"]["payload_sha256"] = row["payload_sha256"]
        operation["result"]["payload_bytes"] = row["payload_bytes"]
        write_json(operation_path, operation)

    def test_repository_plugin_passes_and_exposes_one_discoverable_skill(self) -> None:
        report = validator.validate_plugin(validator.DEFAULT_PLUGIN_ROOT)
        self.assertTrue(report["ok"])
        self.assertEqual(report["discoverable_skills"], [validator.SKILL_NAME])
        self.assertEqual(report["runtime_discovery_state"], "not_evaluated")
        self.assertEqual(report["component_count"], 9)
        self.assertFalse(report["mcp_present"])
        self.assertEqual(
            set(report["git_observation"]),
            {
                "repository_present",
                "repository_root",
                "head_commit",
                "runtime_tree_tracked",
                "package_dirty",
            },
        )
        expected_dirty = bool(
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(validator.DEFAULT_PLUGIN_ROOT.parent),
                    "status",
                    "--porcelain=v1",
                    "--",
                    validator.DEFAULT_PLUGIN_ROOT.name,
                ],
                check=True,
                capture_output=True,
            ).stdout
        )
        self.assertIs(report["git_observation"]["package_dirty"], expected_dirty)

    def test_missing_bundled_manifest_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            plugin, _ = build_plugin(Path(temporary))
            (plugin / validator.SOURCE_MANIFEST_RELATIVE).unlink()
            with self.assertRaises(validator.ValidationError) as raised:
                validator.validate_plugin(plugin)
            self.assertEqual(raised.exception.code, "missing_file")

    def test_bundled_skill_hash_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            plugin, _ = build_plugin(Path(temporary))
            skill = plugin / validator.BUNDLED_RELATIVE / "personas" / "Nick Norwitz" / "SKILL.md"
            skill.write_text(skill.read_text(encoding="utf-8") + "drift\n", encoding="utf-8")
            with self.assertRaises(validator.ValidationError) as raised:
                validator.validate_plugin(plugin)
            self.assertEqual(raised.exception.code, "component_skill_hash_mismatch")

    def test_codex_cannot_use_minimax_default_verifier(self) -> None:
        with self.assertRaises(validator.ValidationError) as raised:
            validator.validate_runtime(
                {"kind": "codex", "auditor_kind": "minimax-default-verifier"}
            )
        self.assertEqual(raised.exception.code, "verifier_route_mismatch")

    def test_complete_package_local_fixture_is_runtime_not_verified(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            report = validator.validate_run(
                plugin,
                fixture.package,
                submissions_root_input=fixture.submissions_root,
                live_rule_input=fixture.rule,
            )
            self.assertFalse(report["ok"])
            self.assertTrue(report["structural_validation_ok"])
            self.assertFalse(report["runtime_execution_verified"])
            self.assertFalse(report["run_success_verified"])
            self.assertEqual(report["status"], validator.RUNTIME_NOT_VERIFIED)
            self.assertEqual(
                report["runtime_attestation"],
                {
                    "required_source": "independent_host",
                    "provided": False,
                    "verified": False,
                    "status": validator.RUNTIME_NOT_VERIFIED,
                    "reason": (
                        "package-local normalized receipts are structurally valid but are "
                        "not independent host attestation"
                    ),
                },
            )
            self.assertEqual(report["package_date"], "2026-08-07")
            self.assertEqual(
                report["package_relative_path"],
                "2026/08/07/research-qa-fixture",
            )
            self.assertEqual(report["reviewable_source_count"], 30)
            self.assertEqual(
                report["expert_pass_receipts_structurally_validated"],
                8,
            )
            self.assertTrue(
                report["synthesis_audit_receipt_structurally_validated"]
            )
            self.assertEqual(
                report["acquisition_executor"]["canonical_realpath"],
                str(fixture.paper_downloader_root.resolve()),
            )
            self.assertEqual(
                report["acquisition_executor"]["consumer_link_state"],
                "linked",
            )
            self.assertEqual(
                report["acquisition_executor"]["runtime_discovery_state"],
                validator.RUNTIME_NOT_VERIFIED,
            )
            self.assertTrue(
                report["acquisition_executor"]
                ["discovery_receipt_structurally_validated"]
            )
            self.assertFalse(
                report["acquisition_executor"]["runtime_execution_verified"]
            )
            self.assertEqual(
                report[
                    "acquisition_operation_receipts_structurally_validated"
                ],
                30,
            )
            self.assertEqual(
                report["runtime_operation_receipts_structurally_validated"],
                29,
            )

    def test_package_local_candidate_success_claim_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            manifest_path = (
                fixture.package / "payload/receipts/run-manifest.json"
            )
            manifest = read_json(manifest_path)
            manifest["status"] = "candidate_success"
            write_json(manifest_path, manifest)
            self.assert_run_error(fixture, plugin, "runtime_success_overclaim")

    def test_package_local_host_attestation_claim_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            manifest_path = (
                fixture.package / "payload/receipts/run-manifest.json"
            )
            manifest = read_json(manifest_path)
            manifest["runtime_attestation"] = {
                "evidence_scope": "package_local_only",
                "independent_host_attestation": "verified",
                "runtime_execution_verified": True,
                "run_success_verified": True,
            }
            write_json(manifest_path, manifest)
            self.assert_run_error(
                fixture,
                plugin,
                "runtime_attestation_boundary",
            )

    def test_plugin_validation_v1_cannot_impersonate_v2(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            receipt_path = fixture.package / "payload/receipts/plugin-validation.json"
            receipt = read_json(receipt_path)
            receipt["schema_version"] = 1
            receipt.pop("schema")
            write_json(receipt_path, receipt)
            self.assert_run_error(fixture, plugin, "plugin_validation_binding")

    def test_plugin_receipt_rejects_runtime_contract_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            contract = (
                plugin
                / validator.SKILL_RELATIVE
                / "references"
                / "workflow-contract.md"
            )
            contract.write_text(
                contract.read_text(encoding="utf-8") + "drift\n",
                encoding="utf-8",
            )
            self.assert_run_error(fixture, plugin, "plugin_validation_binding")

    def test_plugin_receipt_rejects_validator_result_tamper(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            result_path = (
                fixture.package
                / "payload/validation/plugin-validator-result.json"
            )
            result = read_json(result_path)
            result["candidate_only"] = False
            write_json(result_path, result)
            receipt_path = fixture.package / "payload/receipts/plugin-validation.json"
            receipt = read_json(receipt_path)
            receipt["validator_result"]["sha256"] = sha(result_path)
            write_json(receipt_path, receipt)
            self.assert_run_error(fixture, plugin, "plugin_validation_binding")

    def test_plugin_receipt_rejects_combined_static_git_pass_label(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            receipt_path = fixture.package / "payload/receipts/plugin-validation.json"
            receipt = read_json(receipt_path)
            receipt["git_status"] = "Git-untracked 30/30 PASS"
            write_json(receipt_path, receipt)
            self.assert_run_error(fixture, plugin, "plugin_validation_binding")

    def test_consumer_link_without_discovery_receipt_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            run_init = read_json(
                fixture.package / "payload/receipts/run-init.json"
            )
            discovery = (
                fixture.package
                / run_init["acquisition_executor"]["discovery_receipt_path"]
            )
            discovery.unlink()
            self.assert_run_error(
                fixture,
                plugin,
                "acquisition_executor_discovery_unverified",
            )

    def test_downloaded_fixture_without_operation_receipt_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            rows = read_jsonl(
                fixture.package / "payload/sources/inventory.jsonl"
            )
            acquisition = read_json(
                fixture.package / rows[0]["acquisition_receipt_path"]
            )
            operation = (
                fixture.package / acquisition["executor_operation_receipt_path"]
            )
            operation.unlink()
            self.assert_run_error(
                fixture,
                plugin,
                "acquisition_operation_missing",
            )

    def test_self_reported_context_without_operation_receipt_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            contribution_path = (
                fixture.package / "payload/topic/contributions/persona-01.json"
            )
            contribution = read_json(contribution_path)
            contribution["executor"].pop("operation_receipt_path")
            write_json(contribution_path, contribution)
            self.assert_run_error(fixture, plugin, "execution_receipt_missing")

    def test_hidden_subagent_receipt_cannot_impersonate_visible_execution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            contribution = read_json(
                fixture.package / "payload/topic/contributions/persona-01.json"
            )
            operation_path = (
                fixture.package
                / contribution["executor"]["operation_receipt_path"]
            )
            operation = read_json(operation_path)
            operation["agentPath"] = "/root/hidden-agent"
            write_json(operation_path, operation)
            self.assert_run_error(fixture, plugin, "hidden_subagent_evidence")

    def test_package_local_operation_cannot_claim_runtime_verified(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            contribution = read_json(
                fixture.package / "payload/topic/contributions/persona-01.json"
            )
            operation_path = (
                fixture.package
                / contribution["executor"]["operation_receipt_path"]
            )
            operation = read_json(operation_path)
            operation["runtime_execution_verified"] = True
            operation["host_attestation"] = {"status": "self_reported"}
            write_json(operation_path, operation)
            self.assert_run_error(
                fixture,
                plugin,
                "runtime_attestation_boundary",
            )

    def test_unconfirmed_create_thread_is_not_execution_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            contribution = read_json(
                fixture.package / "payload/topic/contributions/persona-01.json"
            )
            operation_path = (
                fixture.package
                / contribution["executor"]["operation_receipt_path"]
            )
            operation = read_json(operation_path)
            operation["create_thread"]["status"] = "created_unconfirmed"
            operation["create_thread"]["prompt_verified"] = False
            write_json(operation_path, operation)
            self.assert_run_error(
                fixture,
                plugin,
                "invalid_visible_task_evidence",
            )

    def test_copied_paper_downloader_consumer_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            copied = root / "copied-paper-downloader" / "SKILL.md"
            copied.parent.mkdir()
            copied.write_bytes((fixture.paper_downloader_root / "SKILL.md").read_bytes())
            receipt_path = fixture.package / "payload/receipts/run-init.json"
            receipt = read_json(receipt_path)
            receipt["acquisition_executor"]["registered_skill_path"] = str(copied)
            write_json(receipt_path, receipt)
            self.assert_run_error(fixture, plugin, "acquisition_executor_unavailable")

    def test_wrapper_paper_downloader_projection_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            wrapper = (
                plugin.parent.parent
                / validator.PAPER_DOWNLOADER_NAME
                / "src"
                / validator.PAPER_DOWNLOADER_NAME
            )
            wrapper.parent.mkdir(parents=True)
            create_directory_link(wrapper, fixture.paper_downloader_root)
            receipt_path = fixture.package / "payload/receipts/run-init.json"
            receipt = read_json(receipt_path)
            receipt["acquisition_executor"]["registered_skill_path"] = str(
                wrapper / "SKILL.md"
            )
            with self.assertRaises(validator.ValidationError) as raised:
                validator.validate_acquisition_executor(
                    receipt["acquisition_executor"],
                    plugin,
                    fixture.package,
                    fixture.runtime,
                )
            self.assertEqual(raised.exception.code, "acquisition_executor_unavailable")

    def test_consumer_link_via_wrapper_projection_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            wrapper = (
                plugin.parent.parent
                / validator.PAPER_DOWNLOADER_NAME
                / "src"
                / validator.PAPER_DOWNLOADER_NAME
            )
            wrapper.parent.mkdir(parents=True)
            create_directory_link(wrapper, fixture.paper_downloader_root)
            indirect_consumer = (
                root / "indirect-agent-skills" / validator.PAPER_DOWNLOADER_NAME
            )
            indirect_consumer.parent.mkdir()
            create_directory_link(indirect_consumer, wrapper)
            receipt = read_json(
                fixture.package / "payload/receipts/run-init.json"
            )
            receipt["acquisition_executor"]["registered_skill_path"] = str(
                indirect_consumer / "SKILL.md"
            )
            with self.assertRaises(validator.ValidationError) as raised:
                validator.validate_acquisition_executor(
                    receipt["acquisition_executor"],
                    plugin,
                    fixture.package,
                    fixture.runtime,
                )
            self.assertEqual(raised.exception.code, "acquisition_executor_unavailable")

    def test_paper_downloader_hash_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            receipt_path = fixture.package / "payload/receipts/run-init.json"
            receipt = read_json(receipt_path)
            receipt["acquisition_executor"]["skill_sha256"] = "0" * 64
            write_json(receipt_path, receipt)
            self.assert_run_error(fixture, plugin, "acquisition_executor_hash_mismatch")

    def test_akashic_root_manifest_must_remain_pending(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            manifest = fixture.package / "manifest.yaml"
            manifest.write_text(
                manifest.read_text(encoding="utf-8").replace(
                    "status: pending",
                    "status: completed",
                ),
                encoding="utf-8",
            )
            self.assert_run_error(fixture, plugin, "akashic_manifest_boundary")

    def test_twenty_nine_sources_cannot_enter_success(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components, reviewable_count=29)
            with self.assertRaises(validator.ValidationError) as raised:
                validator.validate_run(
                    plugin,
                    fixture.package,
                    submissions_root_input=fixture.submissions_root,
                    live_rule_input=fixture.rule,
                )
            self.assertEqual(raised.exception.code, "collection_not_ready")

    def test_duplicate_doi_cannot_count_twice(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            inventory = fixture.package / "payload/sources/inventory.jsonl"
            rows = read_jsonl(inventory)
            rows[1]["doi"] = rows[0]["doi"]
            rows[1]["publication_identity"] = rows[0]["publication_identity"]
            write_jsonl(inventory, rows)
            self.assert_run_error(fixture, plugin, "duplicate_publication_identity")

    def test_failed_access_status_cannot_be_reviewable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            inventory = fixture.package / "payload/sources/inventory.jsonl"
            rows = read_jsonl(inventory)
            rows[0]["access_status"] = "failed"
            rows[0]["failure_reason"] = "fixture failure"
            rehash_source(rows[0])
            write_jsonl(inventory, rows)
            receipt_path = fixture.package / rows[0]["acquisition_receipt_path"]
            receipt = read_json(receipt_path)
            receipt["status"] = "failed"
            write_json(receipt_path, receipt)
            operation_path = (
                fixture.package / receipt["executor_operation_receipt_path"]
            )
            operation = read_json(operation_path)
            operation["result"]["access_status"] = "failed"
            write_json(operation_path, operation)
            self.assert_run_error(fixture, plugin, "invalid_reviewable_source")

    def test_non_scholarly_document_cannot_be_reviewable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            inventory = fixture.package / "payload/sources/inventory.jsonl"
            rows = read_jsonl(inventory)
            rows[0]["document_kind"] = "blog_post"
            write_jsonl(inventory, rows)
            self.assert_run_error(fixture, plugin, "invalid_document_kind")

    def test_downloaded_claim_requires_real_pdf_magic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            inventory = fixture.package / "payload/sources/inventory.jsonl"
            rows = read_jsonl(inventory)
            payload = fixture.package / rows[0]["local_payload_path"]
            payload.write_bytes(b"<html>not a PDF</html>" * 400)
            rows[0]["payload_sha256"] = sha(payload)
            rows[0]["payload_bytes"] = payload.stat().st_size
            rehash_source(rows[0])
            write_jsonl(inventory, rows)
            receipt_path = fixture.package / rows[0]["acquisition_receipt_path"]
            receipt = read_json(receipt_path)
            receipt["payload_sha256"] = rows[0]["payload_sha256"]
            receipt["payload_bytes"] = rows[0]["payload_bytes"]
            write_json(receipt_path, receipt)
            operation_path = (
                fixture.package / receipt["executor_operation_receipt_path"]
            )
            operation = read_json(operation_path)
            operation["result"]["payload_sha256"] = rows[0]["payload_sha256"]
            operation["result"]["payload_bytes"] = rows[0]["payload_bytes"]
            write_json(operation_path, operation)
            self.assert_run_error(fixture, plugin, "invalid_downloaded_pdf")

    def test_pdf_magic_plus_padding_is_not_a_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            self.rewrite_download_payload(
                fixture,
                0,
                b"%PDF-1.7\n" + b"self-reported fixture padding\n" * 300,
            )
            self.assert_run_error(fixture, plugin, "invalid_downloaded_pdf")

    def test_pdf_xref_stream_structure_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "xref-stream.pdf"
            path.write_bytes(minimal_xref_stream_pdf_bytes())
            validator.validate_pdf_structure(path, "src-xref-stream")

    def test_pdf_startxref_must_point_to_the_real_xref(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            data = minimal_valid_pdf_bytes("bad-startxref")
            terminal = validator.PDF_TERMINAL_PATTERN.search(data)
            assert terminal is not None
            replacement = b"1".rjust(len(terminal.group(1)), b"0")
            corrupted = (
                data[: terminal.start(1)]
                + replacement
                + data[terminal.end(1) :]
            )
            self.rewrite_download_payload(fixture, 0, corrupted)
            self.assert_run_error(fixture, plugin, "invalid_downloaded_pdf")

    def test_pdf_trailer_root_must_resolve_through_xref(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            data = minimal_valid_pdf_bytes("bad-root")
            corrupted = data.replace(b"/Root 1 0 R", b"/Root 9 0 R", 1)
            self.assertNotEqual(data, corrupted)
            self.rewrite_download_payload(fixture, 0, corrupted)
            self.assert_run_error(fixture, plugin, "invalid_downloaded_pdf")

    def test_akashic_reuse_passes_without_download_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components, reuse_first_source=True)
            report = validator.validate_run(
                plugin,
                fixture.package,
                submissions_root_input=fixture.submissions_root,
                live_rule_input=fixture.rule,
                akashic_root_input=fixture.akashic_root,
            )
            self.assertTrue(report["akashic_lookup_complete"])
            rows = read_jsonl(fixture.package / "payload/sources/inventory.jsonl")
            self.assertEqual(rows[0]["access_status"], "akashic_reused")
            self.assertFalse(rows[0]["download_attempted"])

    def test_akashic_match_cannot_be_redownloaded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components, reuse_first_source=True)
            inventory = fixture.package / "payload/sources/inventory.jsonl"
            rows = read_jsonl(inventory)
            rows[0]["download_attempted"] = True
            rehash_source(rows[0])
            write_jsonl(inventory, rows)
            receipt_path = fixture.package / rows[0]["acquisition_receipt_path"]
            receipt = read_json(receipt_path)
            receipt["download_attempted"] = True
            receipt["download_started_at"] = NOW
            receipt["download_completed_at"] = NOW
            write_json(receipt_path, receipt)
            self.assert_run_error(fixture, plugin, "akashic_redownload")

    def test_topic_expansion_requires_all_eight_experts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            (fixture.package / "payload/topic/contributions/persona-08.json").unlink()
            self.assert_run_error(fixture, plugin, "topic_contribution_roster")

    def test_topic_expansion_requires_distinct_contexts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components, topic_context_reuse=True)
            self.assert_run_error(fixture, plugin, "topic_context_reuse")

    def test_expert_review_requires_eight_distinct_contexts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components, expert_context_reuse=True)
            self.assert_run_error(fixture, plugin, "expert_context_reuse")

    def test_expert_must_bind_full_source_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            lane = fixture.package / "payload/experts/persona-01"
            coverage_path = lane / "attempt-01.coverage.json"
            coverage = read_json(coverage_path)
            coverage["reviewed_source_ids"] = coverage["reviewed_source_ids"][:-1]
            write_json(coverage_path, coverage)
            receipt_path = lane / "attempt-01.receipt.json"
            receipt = read_json(receipt_path)
            receipt["source_coverage_sha256"] = sha(coverage_path)
            write_json(receipt_path, receipt)
            self.assert_run_error(fixture, plugin, "source_coverage_incomplete")

    def test_obviously_thin_expert_output_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components, tiny_expert="persona-01")
            self.assert_run_error(fixture, plugin, "candidate_too_thin")

    def test_expert_event_before_sources_frozen_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components, early_expert_event=True)
            self.assert_run_error(fixture, plugin, "event_stage_order")

    def test_live_rule_drift_stops_the_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(root, plugin, components)
            fixture.rule.write_text("# changed live Akashic rule fixture\n", encoding="utf-8")
            with self.assertRaises(validator.ValidationError) as raised:
                validator.validate_run(
                    plugin,
                    fixture.package,
                    submissions_root_input=fixture.submissions_root,
                    live_rule_input=fixture.rule,
                )
            self.assertEqual(raised.exception.code, "rule_drift")

    def test_one_expert_without_pass_blocks_synthesis(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(
                root,
                plugin,
                components,
                exhausted_expert="persona-08",
            )
            with self.assertRaises(validator.ValidationError) as raised:
                validator.validate_run(
                    plugin,
                    fixture.package,
                    submissions_root_input=fixture.submissions_root,
                    live_rule_input=fixture.rule,
                )
            self.assertEqual(raised.exception.code, "artifact_not_accepted")

    def test_three_reworks_are_allowed_for_expert_and_synthesis(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(
                root,
                plugin,
                components,
                expert_reworks={"persona-01": 3},
                synthesis_reworks=3,
            )
            report = validator.validate_run(
                plugin,
                fixture.package,
                submissions_root_input=fixture.submissions_root,
                live_rule_input=fixture.rule,
            )
            self.assertEqual(report["expert_attempts"]["persona-01"], 4)
            self.assertEqual(report["synthesis_attempts"], 4)

    def test_missing_retry_event_breaks_receipt_chain(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            plugin, components = build_plugin(root)
            fixture = RunFixture(
                root,
                plugin,
                components,
                expert_reworks={"persona-01": 1},
                omit_retry_event=True,
            )
            with self.assertRaises(validator.ValidationError) as raised:
                validator.validate_run(
                    plugin,
                    fixture.package,
                    submissions_root_input=fixture.submissions_root,
                    live_rule_input=fixture.rule,
                )
            self.assertEqual(raised.exception.code, "event_missing")

    def test_new_calendar_destination_preflight_passes_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            submissions_root = Path(temporary) / "12-agent-submissions"
            submissions_root.mkdir()
            destination = submissions_root / "2028" / "02" / "29" / "new-package"
            report = validator.validate_new_package_destination(
                destination,
                submissions_root_input=submissions_root,
            )
            self.assertTrue(report["ok"])
            self.assertEqual(report["package_date"], "2028-02-29")
            self.assertEqual(
                report["package_relative_path"],
                "2028/02/29/new-package",
            )
            self.assertFalse(destination.exists())

    def test_existing_package_destination_is_never_reused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            submissions_root = Path(temporary) / "12-agent-submissions"
            destination = submissions_root / "2026" / "08" / "07" / "existing"
            destination.mkdir(parents=True)
            with self.assertRaises(validator.ValidationError) as raised:
                validator.validate_new_package_destination(
                    destination,
                    submissions_root_input=submissions_root,
                )
            self.assertEqual(raised.exception.code, "package_exists")

    def test_impossible_calendar_date_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            submissions_root = Path(temporary) / "12-agent-submissions"
            submissions_root.mkdir()
            destination = submissions_root / "2026" / "02" / "30" / "new-package"
            with self.assertRaises(validator.ValidationError) as raised:
                validator.validate_new_package_destination(
                    destination,
                    submissions_root_input=submissions_root,
                )
            self.assertEqual(raised.exception.code, "invalid_package_date")

    def test_non_padded_calendar_component_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            submissions_root = Path(temporary) / "12-agent-submissions"
            submissions_root.mkdir()
            destination = submissions_root / "2026" / "8" / "07" / "new-package"
            with self.assertRaises(validator.ValidationError) as raised:
                validator.validate_new_package_destination(
                    destination,
                    submissions_root_input=submissions_root,
                )
            self.assertEqual(raised.exception.code, "package_calendar_path")

    def test_package_must_be_immediate_child_of_day_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            submissions_root = Path(temporary) / "12-agent-submissions"
            submissions_root.mkdir()
            destination = (
                submissions_root / "2026" / "08" / "07" / "extra" / "new-package"
            )
            with self.assertRaises(validator.ValidationError) as raised:
                validator.validate_new_package_destination(
                    destination,
                    submissions_root_input=submissions_root,
                )
            self.assertEqual(raised.exception.code, "package_calendar_path")

    def test_old_direct_child_layout_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            submissions_root = Path(temporary) / "12-agent-submissions"
            submissions_root.mkdir()
            destination = submissions_root / "old-direct-child"
            with self.assertRaises(validator.ValidationError) as raised:
                validator.validate_new_package_destination(
                    destination,
                    submissions_root_input=submissions_root,
                )
            self.assertEqual(raised.exception.code, "package_calendar_path")

    def test_destination_escape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            submissions_root = root / "12-agent-submissions"
            submissions_root.mkdir()
            destination = root / "2026" / "08" / "07" / "escaped-package"
            with self.assertRaises(validator.ValidationError) as raised:
                validator.validate_new_package_destination(
                    destination,
                    submissions_root_input=submissions_root,
                )
            self.assertEqual(raised.exception.code, "package_escape")


if __name__ == "__main__":
    unittest.main()
