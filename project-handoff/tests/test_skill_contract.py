#!/usr/bin/env python3
import json
from pathlib import Path
import subprocess
import sys
import os
import tempfile
import unittest


TEST_ROOT = Path(__file__).resolve().parent
SKILL_ROOT = TEST_ROOT.parent
WORKSPACE_ROOT = SKILL_ROOT


class ProjectHandoffContractTests(unittest.TestCase):
    def test_skill_frontmatter_and_triggers(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        frontmatter = text.split("---", 2)[1]
        self.assertIn("name: project-handoff", frontmatter)
        for required in (
            "sol-ultra",
            "sol-max",
            "terra-max",
            "luna-max",
            "spark",
            "完整交接",
            "任务分解",
            "并行 Agent",
            "编排派发",
            "可见任务派发",
            "阶段交接",
            "新对话",
            "worktree",
            "cross-harness",
        ):
            self.assertIn(required, frontmatter)

        self.assertIn("references/orchestration-control.md", text)
        self.assertIn("scripts/validate_dispatch_route.py", text)
        self.assertIn("scripts/validate_orchestration_plan.py", text)
        self.assertIn("Using multiple Agents", text)
        self.assertIn("Never create, fork, hand off, or retry a visible Spark task", text)
        self.assertIn("not evidence that Spark is unavailable", text)
        self.assertIn("create_thread", text)
        self.assertIn("spawn_agent", text)
        self.assertIn("scripts/validate_visible_task_receipt.py", text)
        self.assertIn("PROJECT_HANDOFF_SPARK_TERMINAL_FAILURE", text)
        self.assertIn("new explicit user request", text)
        self.assertIn("references/execution-isolation.md", text)

    def test_openai_metadata_invokes_skill(self):
        text = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Project Handoff Controller"', text)
        self.assertIn("$project-handoff", text)
        self.assertIn("plan tasks by file access", text)
        self.assertIn("actual workspace and base revision", text)
        self.assertIn("visible Codex tasks", text)
        self.assertIn("never as subagents", text)
        self.assertIn("external-harness lanes on standby", text)
        self.assertIn("isolated bundled read-only CLI route", text)
        self.assertIn("no App fallback", text)

    def test_public_package_validator_passes(self):
        script = SKILL_ROOT / "scripts" / "validate_package.py"
        self.assertTrue(os.access(script, os.X_OK))
        proc = subprocess.run(
            [sys.executable, "-B", str(script), str(SKILL_ROOT)],
            text=True,
            capture_output=True,
            check=True,
            timeout=10,
        )
        result = json.loads(proc.stdout)
        self.assertEqual("validated", result["status"])
        self.assertEqual("project-handoff", result["package"])

    def test_seven_routing_cases_use_supported_contract(self):
        cases = json.loads(
            (TEST_ROOT / "routing-cases.json").read_text(encoding="utf-8")
        )
        self.assertEqual(7, len(cases))

        allowed = {
            ("gpt-5.6-sol", "max", "visible_thread"),
            ("gpt-5.6-terra", "max", "visible_thread"),
            ("gpt-5.6-luna", "max", "visible_thread"),
            ("gpt-5.3-codex-spark", "xhigh", "bundled_cli"),
        }

        for case in cases:
            expected = case["expected"]
            if expected.get("mode") == "complete_handoff":
                self.assertEqual("portable_prompt_or_file", expected["surface"])
                continue
            if "sequence" in expected:
                self.assertEqual("visible_thread_pipeline", expected["surface"])
                self.assertEqual(
                    [
                        {"model": "gpt-5.6-sol", "reasoning": "max"},
                        {"model": "gpt-5.6-terra", "reasoning": "max"},
                    ],
                    expected["sequence"],
                )
                continue

            contract = (
                expected["model"],
                expected["reasoning"],
                expected["surface"],
            )
            self.assertIn(contract, allowed)

        large_case = next(
            case for case in cases
            if case["id"] == "sol-ultra-controller-development"
        )
        self.assertEqual(
            {
                "controller_model": "gpt-5.6-sol",
                "controller_reasoning": "ultra",
                "project_scale": "super-large",
            },
            large_case["context"],
        )

    def test_orchestration_cases_and_validator(self):
        cases = json.loads(
            (TEST_ROOT / "orchestration-cases.json").read_text(encoding="utf-8")
        )
        required_cases = {
            "parallel-read-only-reviewers",
            "reject-shared-reviewers-with-different-bases",
            "reject-git-content-digest-base",
            "reject-unordered-shared-writers",
            "parallel-worktree-writers",
            "reject-worktree-same-file",
            "reject-windows-case-alias-logical-file",
            "different-repositories-same-relative-path",
            "reject-cross-harness-shared-writers",
            "parallel-cross-harness-worktrees",
            "reject-windows-duplicate-worktree-roots",
            "reject-read-only-writes",
            "reject-worker-canonical-record-write",
            "reject-worker-broad-scope-containing-canonical-records",
            "non-git-document-editor",
            "resource-owning-read-only-audit",
        }
        self.assertTrue(required_cases.issubset({case["id"] for case in cases}))

        script = SKILL_ROOT / "scripts" / "validate_orchestration_plan.py"
        self.assertTrue(os.access(script, os.X_OK))

        with tempfile.TemporaryDirectory() as temp_dir:
            for case in cases:
                plan_path = Path(temp_dir) / f"{case['id']}.json"
                plan_path.write_text(
                    json.dumps(case["plan"], ensure_ascii=False), encoding="utf-8"
                )
                proc = subprocess.run(
                    [sys.executable, "-B", str(script), str(plan_path), "--format", "json"],
                    text=True,
                    capture_output=True,
                    check=False,
                    timeout=10,
                )
                result = json.loads(proc.stdout)
                expected = case["expected"]
                self.assertEqual(expected["valid"], result["valid"], case["id"])
                self.assertEqual(0 if expected["valid"] else 2, proc.returncode)
                if "launch_receipt_required" in expected:
                    self.assertEqual(
                        expected["launch_receipt_required"],
                        result["launch_receipt_required"],
                        case["id"],
                    )
                if "base_pending" in expected:
                    self.assertEqual(
                        expected["base_pending"], result["base_pending"], case["id"]
                    )
                if expected["valid"]:
                    self.assertEqual(
                        expected["ready_groups"], result["ready_groups"], case["id"]
                    )
                    self.assertEqual(
                        expected["execution_contract_complete"],
                        result["execution_contract_complete"],
                        case["id"],
                    )
                    self.assertEqual(
                        expected["initial_execution_ready"],
                        result["initial_execution_ready"],
                        case["id"],
                    )
                    if "environment_pending" in expected:
                        self.assertEqual(
                            expected["environment_pending"],
                            result["environment_pending"],
                            case["id"],
                        )
                else:
                    self.assertTrue(
                        any(
                            expected["error_contains"] in error
                            for error in result["errors"]
                        ),
                        f"{case['id']}: {result['errors']}",
                    )

        partial_route = next(
            case for case in cases if case["id"] == "final-integration-lane"
        )["plan"]["lanes"][0]["route"]
        self.assertEqual("explicit_user", partial_route["model_basis"])
        self.assertEqual("auto_unspecified", partial_route["reasoning_basis"])

    def test_orchestration_rejects_windows_path_escape_and_record_aliases(self):
        cases = json.loads(
            (TEST_ROOT / "orchestration-cases.json").read_text(encoding="utf-8")
        )
        source = next(
            case for case in cases if case["id"] == "parallel-worktree-writers"
        )["plan"]
        script = SKILL_ROOT / "scripts" / "validate_orchestration_plan.py"

        with tempfile.TemporaryDirectory() as temp_dir:
            for unsafe_path in (r"\outside\secret", r"C:outside\secret"):
                plan = json.loads(json.dumps(source))
                plan["run_id"] = "windows-path-escape"
                plan["lanes"] = [plan["lanes"][0]]
                plan["lanes"][0]["write_paths"] = [unsafe_path]
                plan_path = Path(temp_dir) / "escape.json"
                plan_path.write_text(json.dumps(plan), encoding="utf-8")
                proc = subprocess.run(
                    [sys.executable, "-B", str(script), str(plan_path), "--format", "json"],
                    text=True, capture_output=True, check=False, timeout=10,
                )
                result = json.loads(proc.stdout)
                self.assertEqual(2, proc.returncode, unsafe_path)
                self.assertTrue(
                    any("must be relative to workspace_path" in error for error in result["errors"]),
                    result,
                )

            plan = json.loads(json.dumps(source))
            plan["run_id"] = "windows-canonical-record-alias"
            plan["lanes"] = [plan["lanes"][0]]
            lane = plan["lanes"][0]
            lane["worktree_source"] = r"C:\Repo"
            lane["repository_root"] = r"C:\WT-A"
            lane["workspace_path"] = r"C:\WT-A"
            lane["write_paths"] = ["Memory/2026-08-20.md"]
            plan_path = Path(temp_dir) / "record-alias.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-B", str(script), str(plan_path), "--format", "json"],
                text=True, capture_output=True, check=False, timeout=10,
            )
            result = json.loads(proc.stdout)
            self.assertEqual(2, proc.returncode, result)
            self.assertTrue(
                any("integration-owner-only shared records" in error for error in result["errors"]),
                result,
            )

            plan["lanes"][0]["execution_mode"] = "claimed-worktree"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-B", str(script), str(plan_path), "--format", "json"],
                text=True, capture_output=True, check=False, timeout=10,
            )
            result = json.loads(proc.stdout)
            self.assertEqual(2, proc.returncode, result)
            self.assertTrue(
                any("unsupported fields: execution_mode" in error for error in result["errors"]),
                result,
            )

            plan = json.loads(json.dumps(source))
            plan["run_id"] = "windows-unc-alias"
            first, second = plan["lanes"]
            first["worktree_source"] = r"\\server\share\repo"
            second["worktree_source"] = "//server/share/repo"
            first["repository_root"] = first["workspace_path"] = r"C:\WT-A"
            second["repository_root"] = second["workspace_path"] = r"C:\WT-B"
            first["read_paths"] = first["write_paths"] = ["README.md"]
            second["read_paths"] = second["write_paths"] = ["README.md"]
            plan_path = Path(temp_dir) / "unc-alias.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-B", str(script), str(plan_path), "--format", "json"],
                text=True, capture_output=True, check=False, timeout=10,
            )
            result = json.loads(proc.stdout)
            self.assertEqual(2, proc.returncode, result)
            self.assertTrue(
                any("unordered write/write conflict" in error for error in result["errors"]),
                result,
            )

            for ambiguous_path in ("README.md.", "Memory./2026-08-20.md", "folder "):
                plan = json.loads(json.dumps(source))
                plan["run_id"] = "windows-trailing-dot"
                plan["lanes"] = [plan["lanes"][0]]
                lane = plan["lanes"][0]
                lane["worktree_source"] = r"C:\Repo"
                lane["repository_root"] = lane["workspace_path"] = r"C:\WT-A"
                lane["write_paths"] = [ambiguous_path]
                plan_path = Path(temp_dir) / "trailing-dot.json"
                plan_path.write_text(json.dumps(plan), encoding="utf-8")
                proc = subprocess.run(
                    [sys.executable, "-B", str(script), str(plan_path), "--format", "json"],
                    text=True, capture_output=True, check=False, timeout=10,
                )
                result = json.loads(proc.stdout)
                self.assertEqual(2, proc.returncode, result)
                self.assertTrue(
                    any(
                        "Windows component ending in dot or space" in error
                        or "must not start or end with whitespace" in error
                        for error in result["errors"]
                    ),
                    result,
                )

    def test_dispatch_route_guard_rejects_route_drift_and_bad_retries(self):
        cases = json.loads(
            (TEST_ROOT / "dispatch-route-cases.json").read_text(encoding="utf-8")
        )
        required_cases = {
            "portable-handoff-for-external-harness",
            "reject-external-handoff-via-create-thread",
            "reject-review-to-repair-without-replan",
            "reject-unknown-followup-effect-field",
        }
        self.assertTrue(required_cases.issubset({case["id"] for case in cases}))

        script = SKILL_ROOT / "scripts" / "validate_dispatch_route.py"
        self.assertTrue(os.access(script, os.X_OK))

        with tempfile.TemporaryDirectory() as temp_dir:
            for case in cases:
                attempt_path = Path(temp_dir) / f"{case['id']}.json"
                attempt_path.write_text(
                    json.dumps(case["attempt"], ensure_ascii=False), encoding="utf-8"
                )
                proc = subprocess.run(
                    [sys.executable, "-B", str(script), str(attempt_path), "--format", "json"],
                    text=True,
                    capture_output=True,
                    check=False,
                    timeout=10,
                )
                result = json.loads(proc.stdout)
                expected = case["expected"]
                self.assertEqual(expected["valid"], result["valid"], case["id"])
                self.assertEqual(0 if expected["valid"] else 2, proc.returncode)
                disposition = result["failure_disposition"]
                self.assertEqual(
                    expected["classification"], disposition["classification"], case["id"]
                )
                self.assertEqual(
                    expected["spark_unavailable_supported"],
                    disposition["spark_unavailable_supported"],
                    case["id"],
                )
                for field in (
                    "terminal",
                    "next_action",
                    "visible_task_allowed",
                    "same_lane_retry_allowed",
                    "automatic_fallback_allowed",
                    "route_change_requires_new_user_request",
                ):
                    if field in expected:
                        self.assertEqual(
                            expected[field], disposition[field], case["id"]
                        )
                if not expected["valid"]:
                    self.assertTrue(
                        any(
                            expected["error_contains"] in error
                            for error in result["errors"]
                        ),
                        f"{case['id']}: {result['errors']}",
                    )

    def test_visible_task_receipt_guard_rejects_subagent_evidence(self):
        cases = json.loads(
            (TEST_ROOT / "visible-task-receipt-cases.json").read_text(
                encoding="utf-8"
            )
        )
        required_cases = {
            "ready-read-only-local-task",
            "ready-worktree-task",
            "queued-worktree-task",
            "reject-worktree-resolved-local",
            "reject-worktree-without-evidence",
            "reject-worktree-common-git-dir",
            "reject-dirty-worktree",
            "reject-windows-worktree-alias",
            "reject-confirmed-unverified-environment",
        }
        self.assertTrue(required_cases.issubset({case["id"] for case in cases}))

        script = SKILL_ROOT / "scripts" / "validate_visible_task_receipt.py"
        self.assertTrue(os.access(script, os.X_OK))

        with tempfile.TemporaryDirectory() as temp_dir:
            for case in cases:
                receipt_path = Path(temp_dir) / f"{case['id']}.json"
                receipt_path.write_text(
                    json.dumps(case["receipt"], ensure_ascii=False), encoding="utf-8"
                )
                proc = subprocess.run(
                    [sys.executable, "-B", str(script), str(receipt_path), "--format", "json"],
                    text=True,
                    capture_output=True,
                    check=False,
                    timeout=10,
                )
                result = json.loads(proc.stdout)
                expected = case["expected"]
                self.assertEqual(expected["valid"], result["valid"], case["id"])
                self.assertEqual(
                    expected["classification"], result["classification"], case["id"]
                )
                self.assertEqual(
                    expected["registerable"], result["registerable"], case["id"]
                )
                if "execution_ready" in expected:
                    self.assertEqual(
                        expected["execution_ready"],
                        result["execution_ready"],
                        case["id"],
                    )
                self.assertEqual(0 if expected["valid"] else 2, proc.returncode)
                if not expected["valid"]:
                    self.assertTrue(
                        any(
                            expected["error_contains"] in error
                            for error in result["errors"]
                        ),
                        f"{case['id']}: {result['errors']}",
                    )

            invalid_root_path = Path(temp_dir) / "invalid-root.json"
            invalid_root_path.write_text("[]", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-B", str(script), str(invalid_root_path), "--format", "json"],
                text=True,
                capture_output=True,
                check=False,
                timeout=10,
            )
            result = json.loads(proc.stdout)
            self.assertFalse(result["valid"])
            self.assertEqual("invalid_visible_task_evidence", result["classification"])
            self.assertFalse(result["registerable"])

            valid_receipt = next(
                case for case in cases if case["id"] == "ready-read-only-local-task"
            )["receipt"]
            claimed_receipt = json.loads(json.dumps(valid_receipt))
            claimed_receipt["claimed_execution_ready"] = True
            claimed_path = Path(temp_dir) / "unsupported-receipt-field.json"
            claimed_path.write_text(json.dumps(claimed_receipt), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-B", str(script), str(claimed_path), "--format", "json"],
                text=True, capture_output=True, check=False, timeout=10,
            )
            result = json.loads(proc.stdout)
            self.assertEqual(2, proc.returncode, result)
            self.assertTrue(
                any("unsupported fields: claimed_execution_ready" in error for error in result["errors"]),
                result,
            )

            disguised_worktree = json.loads(json.dumps(valid_receipt))
            disguised_worktree["environment_evidence"]["git_dir"] = (
                "/workspace/project/.git/worktrees/disguised"
            )
            disguised_path = Path(temp_dir) / "disguised-worktree.json"
            disguised_path.write_text(json.dumps(disguised_worktree), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-B", str(script), str(disguised_path), "--format", "json"],
                text=True, capture_output=True, check=False, timeout=10,
            )
            result = json.loads(proc.stdout)
            self.assertEqual(2, proc.returncode, result)
            self.assertTrue(
                any("shared_checkout git_dir must equal git_common_dir" in error for error in result["errors"]),
                result,
            )

            ambiguous_root = next(
                case for case in cases if case["id"] == "ready-worktree-task"
            )["receipt"]
            ambiguous_root = json.loads(json.dumps(ambiguous_root))
            ambiguous_root["worktree_source"] = r"C:\Repo"
            ambiguous_root["repository_root"] = r"C:\WT."
            ambiguous_root["workspace_path"] = r"C:\WT."
            evidence = ambiguous_root["environment_evidence"]
            evidence["worktree_source"] = r"C:\Repo"
            evidence["repository_root"] = r"C:\WT."
            evidence["workspace_path"] = r"C:\WT."
            evidence["git_dir"] = r"C:\Repo\.git\worktrees\wt"
            evidence["git_common_dir"] = r"C:\Repo\.git"
            ambiguous_path = Path(temp_dir) / "ambiguous-windows-root.json"
            ambiguous_path.write_text(json.dumps(ambiguous_root), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-B", str(script), str(ambiguous_path), "--format", "json"],
                text=True, capture_output=True, check=False, timeout=10,
            )
            result = json.loads(proc.stdout)
            self.assertEqual(2, proc.returncode, result)
            self.assertTrue(
                any("Windows component ending in dot or space" in error for error in result["errors"]),
                result,
            )

    def test_orchestration_reference_closes_control_lifecycle(self):
        text = (
            SKILL_ROOT / "references" / "orchestration-control.md"
        ).read_text(encoding="utf-8")
        for required in (
            "dependency graph",
            "controller/plan.json",
            "controller/thread-registry.md",
            "controller/status.md",
            "controller/router-log.jsonl",
            "integration owner",
            "succeeded_pending_integration",
            "Retry rules",
            "Abort rules",
            "Archive rules",
            "Creating many tasks",
        ):
            self.assertIn(required, text)

    def test_visible_receipt_binds_to_updated_plan(self):
        cases = json.loads(
            (TEST_ROOT / "visible-task-receipt-cases.json").read_text(encoding="utf-8")
        )
        receipt = next(case for case in cases if case["id"] == "ready-worktree-task")["receipt"]
        plan = {
            "run_id": receipt["run_id"],
            "integration_owner": "controller",
            "lanes": [
                {
                    "id": receipt["lane_id"],
                    "goal": "Write one isolated file.",
                    "depends_on": [],
                    "read_paths": ["src/a.py"],
                    "write_paths": ["src/a.py"],
                    "mutable_resources": [],
                    "harness": receipt["harness"],
                    "file_access": receipt["file_access"],
                    "workspace_mode": receipt["workspace_mode"],
                    "worktree_source": receipt["worktree_source"],
                    "repository_root": receipt["repository_root"],
                    "workspace_path": receipt["workspace_path"],
                    "base_revision": receipt["base_revision"],
                    "expected_outputs": ["src/a.py"],
                    "validation": "test -s src/a.py",
                    "route": {
                        "requested_route": "terra-max",
                        "model": "gpt-5.6-terra",
                        "reasoning": "max",
                        "surface": "visible_thread",
                        "model_basis": "auto_unspecified",
                        "reasoning_basis": "auto_unspecified",
                    },
                }
            ],
        }
        script = SKILL_ROOT / "scripts" / "validate_visible_task_receipt.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            receipt_path = Path(temp_dir) / "receipt.json"
            plan_path = Path(temp_dir) / "plan.json"
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-B", str(script), str(receipt_path), "--plan", str(plan_path), "--format", "json"],
                text=True, capture_output=True, check=False, timeout=10,
            )
            result = json.loads(proc.stdout)
            self.assertEqual(0, proc.returncode, result)
            self.assertTrue(result["valid"])
            self.assertTrue(result["plan_bound"])
            self.assertTrue(result["execution_ready"])

            plan["lanes"][0]["repository_root"] = "/workspace/worktrees/other"
            plan["lanes"][0]["workspace_path"] = "/workspace/worktrees/other"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-B", str(script), str(receipt_path), "--plan", str(plan_path), "--format", "json"],
                text=True, capture_output=True, check=False, timeout=10,
            )
            result = json.loads(proc.stdout)
            self.assertEqual(2, proc.returncode)
            self.assertFalse(result["plan_bound"])
            self.assertTrue(any("repository_root must match plan lane" in error for error in result["errors"]))

    def test_same_wave_worktree_writers_wait_for_all_actual_paths(self):
        receipt_cases = json.loads(
            (TEST_ROOT / "visible-task-receipt-cases.json").read_text(encoding="utf-8")
        )
        receipt = next(
            case for case in receipt_cases if case["id"] == "ready-worktree-task"
        )["receipt"]
        plan_cases = json.loads(
            (TEST_ROOT / "orchestration-cases.json").read_text(encoding="utf-8")
        )
        plan = next(
            case for case in plan_cases if case["id"] == "parallel-worktree-writers"
        )["plan"]
        plan = json.loads(json.dumps(plan))
        plan["run_id"] = receipt["run_id"]
        first, second = plan["lanes"]
        first["repository_root"] = receipt["repository_root"]
        first["workspace_path"] = receipt["workspace_path"]
        script = SKILL_ROOT / "scripts" / "validate_visible_task_receipt.py"

        with tempfile.TemporaryDirectory() as temp_dir:
            receipt_path = Path(temp_dir) / "receipt.json"
            plan_path = Path(temp_dir) / "plan.json"
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-B", str(script), str(receipt_path), "--plan", str(plan_path), "--format", "json"],
                text=True, capture_output=True, check=False, timeout=10,
            )
            result = json.loads(proc.stdout)
            self.assertEqual(2, proc.returncode, result)
            self.assertFalse(result["execution_ready"])
            self.assertTrue(
                any("same-wave writer" in error for error in result["errors"]),
                result,
            )

            second["repository_root"] = "/workspace/worktrees/writer-b"
            second["workspace_path"] = "/workspace/worktrees/writer-b"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-B", str(script), str(receipt_path), "--plan", str(plan_path), "--format", "json"],
                text=True, capture_output=True, check=False, timeout=10,
            )
            result = json.loads(proc.stdout)
            self.assertEqual(0, proc.returncode, result)
            self.assertTrue(result["execution_ready"])
            self.assertTrue(result["plan_bound"])

    def test_external_environment_receipt_closes_standby_gate(self):
        cases = json.loads(
            (TEST_ROOT / "orchestration-cases.json").read_text(encoding="utf-8")
        )
        plan = next(
            case for case in cases if case["id"] == "non-git-document-editor"
        )["plan"]
        lane = plan["lanes"][0]
        receipt = {
            "run_id": plan["run_id"],
            "lane_id": lane["id"],
            "harness": lane["harness"],
            "status": "verified",
            "surface": "portable_handoff",
            "file_access": lane["file_access"],
            "workspace_mode": lane["workspace_mode"],
            "worktree_source": lane["worktree_source"],
            "repository_root": lane["repository_root"],
            "workspace_path": lane["workspace_path"],
            "base_revision": lane["base_revision"],
            "environment_verified": True,
            "evidence_source": "controller_disk_readback",
            "environment_evidence": {
                "verified_by": "snapshot_readback",
                "worktree_source": None,
                "repository_root": None,
                "workspace_path": lane["workspace_path"],
                "base_revision": lane["base_revision"],
                "content_state_verified": True,
            },
            "failure": None,
        }
        script = SKILL_ROOT / "scripts" / "validate_external_environment_receipt.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            receipt_path = Path(temp_dir) / "external-receipt.json"
            plan_path = Path(temp_dir) / "plan.json"
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-B", str(script), str(receipt_path), "--plan", str(plan_path), "--format", "json"],
                text=True, capture_output=True, check=False, timeout=10,
            )
            result = json.loads(proc.stdout)
            self.assertEqual(0, proc.returncode, result)
            self.assertTrue(result["execution_ready"])
            self.assertTrue(result["plan_bound"])

            receipt["workspace_path"] = "/workspace/wrong"
            receipt["environment_evidence"]["workspace_path"] = "/workspace/wrong"
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-B", str(script), str(receipt_path), "--plan", str(plan_path), "--format", "json"],
                text=True, capture_output=True, check=False, timeout=10,
            )
            result = json.loads(proc.stdout)
            self.assertEqual(2, proc.returncode)
            self.assertFalse(result["execution_ready"])
            self.assertTrue(any("workspace_path must match plan lane" in error for error in result["errors"]))

            failed_receipt = {
                "run_id": plan["run_id"],
                "lane_id": lane["id"],
                "harness": lane["harness"],
                "status": "failed",
                "surface": "portable_handoff",
                "file_access": lane["file_access"],
                "workspace_mode": lane["workspace_mode"],
                "worktree_source": None,
                "repository_root": None,
                "workspace_path": None,
                "base_revision": None,
                "environment_verified": False,
                "evidence_source": "external_receipt",
                "environment_evidence": None,
                "failure": "external harness did not start",
            }
            receipt_path.write_text(json.dumps(failed_receipt), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-B", str(script), str(receipt_path), "--plan", str(plan_path), "--format", "json"],
                text=True, capture_output=True, check=False, timeout=10,
            )
            result = json.loads(proc.stdout)
            self.assertEqual(0, proc.returncode, result)
            self.assertTrue(result["valid"])
            self.assertFalse(result["execution_ready"])
            self.assertEqual("external_environment_failure", result["classification"])

            git_plan = next(
                case
                for case in cases
                if case["id"] == "parallel-cross-harness-worktrees"
            )["plan"]
            git_lane = next(
                item for item in git_plan["lanes"] if item["id"] == "trae-write"
            )
            git_receipt = {
                "run_id": git_plan["run_id"],
                "lane_id": git_lane["id"],
                "harness": git_lane["harness"],
                "status": "verified",
                "surface": "portable_handoff",
                "file_access": git_lane["file_access"],
                "workspace_mode": git_lane["workspace_mode"],
                "worktree_source": git_lane["worktree_source"],
                "repository_root": git_lane["repository_root"],
                "workspace_path": git_lane["workspace_path"],
                "base_revision": git_lane["base_revision"],
                "environment_verified": True,
                "evidence_source": "controller_disk_readback",
                "environment_evidence": {
                    "verified_by": "git_readback",
                    "worktree_source": git_lane["worktree_source"],
                    "repository_root": git_lane["repository_root"],
                    "workspace_path": git_lane["workspace_path"],
                    "base_revision": git_lane["base_revision"],
                    "git_dir": "/workspace/project/.git/worktrees/trae-ui",
                    "git_common_dir": "/workspace/project/.git",
                    "head_revision": git_lane["base_revision"],
                    "working_tree_clean": True,
                },
                "failure": None,
            }
            plan_path.write_text(json.dumps(git_plan), encoding="utf-8")
            receipt_path.write_text(json.dumps(git_receipt), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-B", str(script), str(receipt_path), "--plan", str(plan_path), "--format", "json"],
                text=True, capture_output=True, check=False, timeout=10,
            )
            result = json.loads(proc.stdout)
            self.assertEqual(2, proc.returncode, result)
            self.assertFalse(result["execution_ready"])
            self.assertTrue(any("same-wave writer" in error for error in result["errors"]))

            codex_lane = next(
                item for item in git_plan["lanes"] if item["id"] == "codex-write"
            )
            codex_lane["repository_root"] = "/workspace/worktrees/codex-api"
            codex_lane["workspace_path"] = "/workspace/worktrees/codex-api"
            plan_path.write_text(json.dumps(git_plan), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-B", str(script), str(receipt_path), "--plan", str(plan_path), "--format", "json"],
                text=True, capture_output=True, check=False, timeout=10,
            )
            result = json.loads(proc.stdout)
            self.assertEqual(0, proc.returncode, result)
            self.assertTrue(result["execution_ready"])

            git_receipt["environment_evidence"]["working_tree_clean"] = False
            receipt_path.write_text(json.dumps(git_receipt), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-B", str(script), str(receipt_path), "--plan", str(plan_path), "--format", "json"],
                text=True, capture_output=True, check=False, timeout=10,
            )
            result = json.loads(proc.stdout)
            self.assertEqual(2, proc.returncode, result)
            self.assertFalse(result["execution_ready"])
            self.assertTrue(any("clean pre-write worktree" in error for error in result["errors"]))

    def test_model_routing_preserves_explicit_fields_independently(self):
        text = (
            SKILL_ROOT / "references" / "model-routing.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Resolve `model` and `reasoning` independently", text)
        self.assertIn("model_basis: explicit_user", text)
        self.assertIn("reasoning_basis: explicit_user", text)
        self.assertIn("dispatch the full ready, conflict-free wave", text)
        self.assertIn("capability is not route authority", text)
        self.assertIn("luna-max", text)
        self.assertIn("produce_portable_handoff", text)
        self.assertIn("portable_handoff", text)
        self.assertIn("For `operation: followup` only", text)

    def test_thread_dispatch_has_sync_abort_and_archive_contracts(self):
        text = (
            SKILL_ROOT / "references" / "thread-dispatch.md"
        ).read_text(encoding="utf-8")
        for required in (
            "direct user-to-worker intervention",
            "set_thread_archived",
            "marking the old task superseded",
            "On abort",
            "integration owner",
            "unsupported_parameter",
            "must not be retried",
            "validate_visible_task_receipt.py",
            "collaboration.spawn_agent",
            "requested_environment",
            "actual_environment",
            "workspace_path",
            "base_revision",
            "environment_evidence",
            "harness: codex",
            "verified_by: git_readback",
            "content_state_verified: true",
            "Controller registry fields only (do not pass this superset to the receipt validator)",
        ):
            self.assertIn(required, text)

    def test_execution_isolation_contract_is_explicit(self):
        text = (
            SKILL_ROOT / "references" / "execution-isolation.md"
        ).read_text(encoding="utf-8")
        for required in (
            "read_only",
            "write",
            "shared_checkout",
            "worktree",
            "non_git",
            "worktree_source",
            "Response-only findings",
            "external harness",
            "standby",
            "Review-to-repair",
            "integration owner",
            "A verified external non-Git launch uses this exact receipt shape",
            "valid evidence but never execution-ready",
            "memory/",
            "conversation/",
        ):
            self.assertIn(required, text)

    def test_spark_route_is_integrated(self):
        text = (
            SKILL_ROOT / "references" / "spark-cli-route.md"
        ).read_text(encoding="utf-8")
        self.assertIn("scripts/run-spark-cli.sh", text)
        self.assertIn("Good Spark tasks", text)
        self.assertIn("Do not send to Spark", text)
        self.assertIn("Never call `create_thread`", text)
        self.assertIn("spark_unavailable_supported", text)
        self.assertIn("private temporary `CODEX_HOME`", text)
        self.assertIn("PROJECT_HANDOFF_SPARK_TERMINAL_FAILURE", text)
        self.assertIn("explicit request", text)
        self.assertIn("pre-dispatch permission stop", text)
        self.assertIn("64 KiB", text)
        self.assertIn("minified JSON/JSONL", text)
        self.assertIn("tool_output_token_limit=4096", text)
        self.assertIn("--output-last-message", text)
        self.assertIn("final 8 KiB", text)

    @unittest.skipIf(os.name == "nt", "POSIX Spark wrapper contract")
    def test_bundled_spark_wrapper_contract(self):
        script = SKILL_ROOT / "scripts" / "run-spark-cli.sh"
        self.assertTrue(os.access(script, os.X_OK))

        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            source_home = temp / "source-home"
            source_home.mkdir()
            (source_home / "auth.json").write_text(
                '{"test":"credential"}\n', encoding="utf-8"
            )
            source_state = source_home / "state_5.sqlite"
            source_state.write_text("do-not-touch\n", encoding="utf-8")
            runtime_home_receipt = temp / "runtime-home.txt"
            fake_codex_receipt = temp / "fake-codex-receipt.txt"
            fake_codex = temp / "codex"
            fake_codex.write_text(
                "#!/bin/sh\n"
                "last_message=''\n"
                "previous=''\n"
                "for argument in \"$@\"; do\n"
                "  if [ \"$previous\" = '--output-last-message' ]; then last_message=$argument; fi\n"
                "  previous=$argument\n"
                "done\n"
                "{\n"
                "printf 'ARGS:%s\\n' \"$*\"\n"
                "printf 'RUNTIME_HOME:%s\\n' \"$CODEX_HOME\"\n"
                "if [ -r \"$CODEX_HOME/auth.json\" ]; then printf 'AUTH:present\\n'; fi\n"
                "if [ ! -e \"$CODEX_HOME/state_5.sqlite\" ]; then printf 'LIVE_STATE:absent\\n'; fi\n"
                "printf 'STDIN:'\n"
                "cat\n"
                "} > \"$FAKE_CODEX_RECEIPT\"\n"
                "printf '%s\\n' \"$CODEX_HOME\" > \"$RUNTIME_HOME_RECEIPT\"\n"
                "printf 'TRACE:must-not-reach-parent\\n'\n"
                "printf 'OK\\n' > \"$last_message\"\n",
                encoding="utf-8",
            )
            fake_codex.chmod(0o755)
            prompt = temp / "prompt.txt"
            prompt.write_text("Reply exactly OK.\n", encoding="utf-8")
            env = os.environ.copy()
            env["PATH"] = f"{temp_dir}:{env['PATH']}"
            env["CODEX_HOME"] = str(source_home)
            env["TMPDIR"] = temp_dir
            env["RUNTIME_HOME_RECEIPT"] = str(runtime_home_receipt)
            env["FAKE_CODEX_RECEIPT"] = str(fake_codex_receipt)
            proc = subprocess.run(
                [
                    str(script),
                    "--cwd",
                    str(WORKSPACE_ROOT),
                    "--prompt-file",
                    str(prompt),
                ],
                text=True,
                capture_output=True,
                check=True,
                timeout=10,
                env=env,
            )
            isolated_home = Path(
                runtime_home_receipt.read_text(encoding="utf-8").strip()
            )
            self.assertNotEqual(source_home, isolated_home)
            self.assertFalse(isolated_home.exists())
            self.assertEqual("do-not-touch\n", source_state.read_text(encoding="utf-8"))
            receipt_text = fake_codex_receipt.read_text(encoding="utf-8")

        self.assertEqual("OK\n", proc.stdout)
        self.assertNotIn("TRACE:must-not-reach-parent", proc.stdout)
        self.assertIn("--ignore-user-config", receipt_text)
        self.assertIn("--strict-config", receipt_text)
        self.assertIn("--ephemeral", receipt_text)
        self.assertIn("-s read-only", receipt_text)
        self.assertIn("-m gpt-5.3-codex-spark", receipt_text)
        self.assertIn('model_reasoning_effort="xhigh"', receipt_text)
        self.assertIn("tool_output_token_limit=4096", receipt_text)
        self.assertIn("--output-last-message", receipt_text)
        self.assertNotIn("model_supports_reasoning_summaries", receipt_text)
        self.assertIn("AUTH:present", receipt_text)
        self.assertIn("LIVE_STATE:absent", receipt_text)
        self.assertIn("STDIN:Reply exactly OK.", receipt_text)

    @unittest.skipIf(os.name == "nt", "POSIX Spark wrapper contract")
    def test_bundled_spark_wrapper_failure_is_terminal(self):
        script = SKILL_ROOT / "scripts" / "run-spark-cli.sh"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            runtime_home_receipt = temp / "runtime-home.txt"
            fake_codex = temp / "codex"
            fake_codex.write_text(
                "#!/bin/sh\n"
                "printf '%s\\n' \"$CODEX_HOME\" > \"$RUNTIME_HOME_RECEIPT\"\n"
                "exit 23\n",
                encoding="utf-8",
            )
            fake_codex.chmod(0o755)
            prompt = temp / "prompt.txt"
            prompt.write_text("Reply exactly OK.\n", encoding="utf-8")
            env = os.environ.copy()
            env["PATH"] = f"{temp_dir}:{env['PATH']}"
            env["TMPDIR"] = temp_dir
            env["RUNTIME_HOME_RECEIPT"] = str(runtime_home_receipt)
            proc = subprocess.run(
                [
                    str(script),
                    "--cwd",
                    str(WORKSPACE_ROOT),
                    "--prompt-file",
                    str(prompt),
                ],
                text=True,
                capture_output=True,
                check=False,
                timeout=10,
                env=env,
            )
            isolated_home = Path(
                runtime_home_receipt.read_text(encoding="utf-8").strip()
            )
            self.assertFalse(isolated_home.exists())

        self.assertEqual(23, proc.returncode)
        self.assertIn("PROJECT_HANDOFF_SPARK_TERMINAL_FAILURE", proc.stderr)
        self.assertIn("action=stop_lane", proc.stderr)
        self.assertIn("visible_fallback=forbidden", proc.stderr)
        self.assertIn("route_change=requires_new_user_request", proc.stderr)

    def test_internal_prompt_uses_flat_sections_in_order(self):
        text = (
            TEST_ROOT / "fixtures" / "internal-handoff-prompt.txt"
        ).read_text(encoding="utf-8")
        required_sections = [
            "Background:",
            "Materials:",
            "Constraints:",
            "Tools:",
            "Task:",
            "Output format:",
            "Success criteria:",
            "Progress state:",
        ]
        positions = [text.index(section) for section in required_sections]
        self.assertEqual(sorted(positions), positions)
        self.assertLess(text.index("Materials:"), text.index("Task:"))
        self.assertIn("NEEDS_CONTEXT", text)
        self.assertIn("Run id / lane id:", text)
        self.assertIn("File access:", text)
        self.assertIn("Workspace mode:", text)
        self.assertIn("Worktree source:", text)
        self.assertIn("Environment receipt:", text)
        self.assertIn("Write scope:", text)
        self.assertIn("integration owner", text)
        self.assertIn("Task creation or multi-Agent use alone is not success", text)

    def test_complete_handoff_scaffold_remains_runnable(self):
        script = SKILL_ROOT / "scripts" / "make_handoff.py"
        proc = subprocess.run(
            [sys.executable, "-B", str(script), "--cwd", str(WORKSPACE_ROOT)],
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=True,
            timeout=10,
        )
        self.assertIn(f"cwd: {WORKSPACE_ROOT}", proc.stdout)
        self.assertIn("## 风险/需复核", proc.stdout)
        self.assertIn("# Complete Project Handoff", proc.stdout)
        self.assertIn("## 交接类型与接收方", proc.stdout)
        self.assertIn("## 任务图、路由与负责人", proc.stdout)
        self.assertIn("## 项目、执行环境与权限", proc.stdout)
        self.assertIn("file access: read_only | write", proc.stdout)
        self.assertIn("workspace mode: shared_checkout | worktree | non_git", proc.stdout)
        self.assertIn("environment receipt: pending", proc.stdout)
        self.assertIn("remain standby until launch/environment evidence exists", proc.stdout)
        self.assertIn("If review changes to repair", proc.stdout)
        self.assertIn("## 验证与集成状态", proc.stdout)
        self.assertIn("## 失败、重试、中止与归档", proc.stdout)
        self.assertIn("## 接收 Agent 第一动作", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
