#!/usr/bin/env python3
import copy
import hashlib
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
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from validate_dispatch_route import resolve_request_case


class ProjectHandoffContractTests(unittest.TestCase):
    def test_skill_frontmatter_and_triggers(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        frontmatter = text.split("---", 2)[1]
        self.assertIn("name: project-handoff", frontmatter)
        for required in (
            "astra-ultra",
            "astra-max",
            "gpt6-max",
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
        self.assertIn("platform_default", text)
        self.assertIn("silent_default_override", text)

    def test_openai_metadata_invokes_skill(self):
        text = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Project Handoff Controller"', text)
        self.assertIn("$project-handoff", text)
        self.assertIn("complete portable handoff", text)
        self.assertIn("visible Codex tasks", text)
        self.assertIn("never substitute subagents", text)
        self.assertIn("stop its lane on any CLI failure", text)

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

    def test_natural_language_routing_cases_preserve_field_authority(self):
        cases = json.loads(
            (TEST_ROOT / "routing-cases.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(cases), len({case["id"] for case in cases}))

        allowed = {
            ("gpt-6-astra", "max", "visible_thread"),
            ("gpt-5.6-sol", "max", "visible_thread"),
            ("gpt-5.6-luna", "max", "visible_thread"),
            ("gpt-5.3-codex-spark", "xhigh", "bundled_cli"),
        }

        for case in cases:
            actual = resolve_request_case(case["request"], case.get("context"))
            expected = case["expected"]
            self.assertEqual(
                expected,
                {key: actual.get(key) for key in expected},
                case["id"],
            )
            if expected.get("mode") == "complete_handoff":
                self.assertEqual("portable_prompt_or_file", actual["surface"])
                continue
            if "sequence" in expected:
                self.assertEqual("visible_thread_pipeline", actual["surface"])
                self.assertEqual("explicit_auto", actual["model_basis"])
                self.assertEqual("explicit_auto", actual["reasoning_basis"])
                self.assertEqual(
                    [
                        {"model": "gpt-6-astra", "reasoning": "max"},
                        {"model": "gpt-5.6-sol", "reasoning": "max"},
                    ],
                    actual["sequence"],
                )
                continue

            if expected.get("requested_route") == "platform-default":
                self.assertIsNone(actual["model"])
                self.assertIsNone(actual["reasoning"])
                self.assertEqual("platform_default", actual["model_basis"])
                self.assertEqual("platform_default", actual["reasoning_basis"])
                self.assertEqual({}, actual["create_thread_arguments"])
                continue

            if "create_thread_arguments" in expected:
                arguments = actual["create_thread_arguments"]
                if actual["model_basis"] == "platform_default":
                    self.assertNotIn("model", arguments)
                if actual["reasoning_basis"] == "platform_default":
                    self.assertNotIn("thinking", arguments)
                for axis in ("model", "reasoning"):
                    authority = actual["requested_axes"][axis]
                    self.assertEqual(actual[f"{axis}_basis"], authority["basis"])
                    self.assertEqual(actual[axis], authority["effective"])
                continue

            contract = (
                actual["model"],
                actual["reasoning"],
                actual["surface"],
            )
            self.assertIn(contract, allowed)
            self.assertIn("模型和推理都自动选", case["request"])
            self.assertEqual("explicit_auto", actual["model_basis"])
            self.assertEqual("explicit_auto", actual["reasoning_basis"])

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

        alias_case = next(
            case for case in cases if case["id"] == "explicit-sol-ultra-alias"
        )["expected"]
        self.assertEqual("explicit_skill_route", alias_case["model_basis"])
        self.assertEqual("explicit_skill_route", alias_case["reasoning_basis"])

        auto_case = next(
            case for case in cases if case["id"] == "explicit-auto-route"
        )["expected"]
        self.assertEqual("explicit_auto", auto_case["model_basis"])
        self.assertEqual("explicit_auto", auto_case["reasoning_basis"])

        for case in cases:
            actual = resolve_request_case(case["request"], case.get("context"))
            if actual.get("model_basis") == "explicit_auto":
                self.assertNotEqual("gpt-5.6-terra", actual.get("model"), case["id"])
                for step in actual.get("sequence", []):
                    self.assertNotEqual("gpt-5.6-terra", step["model"], case["id"])

    def test_partial_auto_and_model_names_do_not_invent_axis_authority(self):
        for name in ("Astra", "GPT6"):
            for request in (
                f"创建任务，模型用 {name}，其他用平台默认。",
                f"用 {name} 创建任务。",
                f"使用 {name} 创建任务。",
                f"{name} 创建任务。",
                f"use {name} to create a task.",
            ):
                actual = resolve_request_case(request)
                self.assertEqual({"model": "gpt-6-astra"}, actual["create_thread_arguments"], request)
                self.assertEqual(name.lower(), actual["requested_axes"]["model"]["requested"])
                self.assertEqual(["thinking"], actual["omitted_create_thread_fields"])

        with self.assertRaisesRegex(ValueError, "Spark model requires reasoning=xhigh"):
            resolve_request_case("创建任务，模型自动选，只读检查 manifest 的 SHA。")
        with self.assertRaisesRegex(ValueError, "conflicting explicit and auto"):
            resolve_request_case("创建任务，模型用 gpt-5.6-sol，模型自动选。")
        with self.assertRaisesRegex(ValueError, "conflicting explicit and auto"):
            resolve_request_case("创建任务，推理用 high，推理自动选。")
        for unsupported_name in ("Astra2", "Astra-ultra", "GPT6-next"):
            with self.assertRaisesRegex(ValueError, "unrecognized explicit model"):
                resolve_request_case(f"创建任务，模型用 {unsupported_name}。")
        with self.assertRaisesRegex(ValueError, "alias plus separate axis selection"):
            resolve_request_case("用 astra-max 创建任务，推理用 low。")
        with self.assertRaisesRegex(ValueError, "alias plus separate axis selection"):
            resolve_request_case("用 astra-max 创建任务，模型和推理都自动选。")
        with self.assertRaisesRegex(ValueError, "unrecognized explicit reasoning"):
            resolve_request_case("创建任务，推理用 highness。")
        with self.assertRaisesRegex(ValueError, "multiple explicit selections"):
            resolve_request_case("创建任务，模型用 Astra，模型用 gpt-5.6-sol。")

    def test_orchestration_cases_and_validator(self):
        cases = json.loads(
            (TEST_ROOT / "orchestration-cases.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(cases), len({case["id"] for case in cases}))

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
                if expected["valid"]:
                    self.assertEqual(
                        expected["ready_groups"], result["ready_groups"], case["id"]
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
        self.assertEqual("explicit_user", partial_route["reasoning_basis"])

    def test_dispatch_route_guard_rejects_route_drift_and_bad_retries(self):
        cases = json.loads(
            (TEST_ROOT / "dispatch-route-cases.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(cases), len({case["id"] for case in cases}))

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
                self.assertRegex(result["attempt_sha256"], r"^[0-9a-f]{64}$")
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
                if "create_thread_arguments" in expected:
                    self.assertEqual(
                        expected["create_thread_arguments"],
                        result["route"]["create_thread_arguments"],
                        case["id"],
                    )
                    self.assertEqual(
                        expected["omitted_create_thread_fields"],
                        result["route"]["omitted_create_thread_fields"],
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

    def test_visible_task_receipt_guard_binds_attempt_tool_route_and_arguments(self):
        fixture = json.loads(
            (TEST_ROOT / "visible-task-receipt-cases.json").read_text(
                encoding="utf-8"
            )
        )
        attempts = fixture["attempts"]
        cases = fixture["cases"]
        self.assertIn("astra-max", attempts)
        self.assertIn("gpt6-model-only", attempts)
        self.assertEqual(len(cases), len({case["id"] for case in cases}))

        script = SKILL_ROOT / "scripts" / "validate_visible_task_receipt.py"
        self.assertTrue(os.access(script, os.X_OK))

        with tempfile.TemporaryDirectory() as temp_dir:
            for case in cases:
                attempt = attempts[case["attempt"]]
                attempt_path = Path(temp_dir) / f"{case['id']}-attempt.json"
                attempt_path.write_text(
                    json.dumps(attempt, ensure_ascii=False), encoding="utf-8"
                )
                receipt = copy.deepcopy(case["receipt"])
                if receipt["dispatch_attempt_sha256"] == "$ATTEMPT_SHA256":
                    canonical_attempt = json.dumps(
                        attempt,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("utf-8")
                    receipt["dispatch_attempt_sha256"] = hashlib.sha256(
                        canonical_attempt
                    ).hexdigest()
                receipt_path = Path(temp_dir) / f"{case['id']}.json"
                receipt_path.write_text(
                    json.dumps(receipt, ensure_ascii=False), encoding="utf-8"
                )
                proc = subprocess.run(
                    [
                        sys.executable,
                        "-B",
                        str(script),
                        str(receipt_path),
                        "--dispatch-attempt",
                        str(attempt_path),
                        "--format",
                        "json",
                    ],
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
                self.assertEqual(0 if expected["valid"] else 2, proc.returncode)
                if not expected["valid"]:
                    self.assertTrue(
                        any(
                            expected["error_contains"] in error
                            for error in result["errors"]
                        ),
                        f"{case['id']}: {result['errors']}",
                    )

            attempt = attempts["sol-max"]
            attempt_path = Path(temp_dir) / "invalid-root-attempt.json"
            attempt_path.write_text(
                json.dumps(attempt, ensure_ascii=False), encoding="utf-8"
            )
            invalid_root_path = Path(temp_dir) / "invalid-root.json"
            invalid_root_path.write_text("[]", encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(script),
                    str(invalid_root_path),
                    "--dispatch-attempt",
                    str(attempt_path),
                    "--format",
                    "json",
                ],
                text=True,
                capture_output=True,
                check=False,
                timeout=10,
            )
            result = json.loads(proc.stdout)
            self.assertFalse(result["valid"])
            self.assertEqual("invalid_visible_task_evidence", result["classification"])
            self.assertFalse(result["registerable"])

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

    def test_model_routing_preserves_explicit_fields_independently(self):
        text = (
            SKILL_ROOT / "references" / "model-routing.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Resolve `model` and `reasoning` independently", text)
        self.assertIn("model_basis: explicit_user", text)
        self.assertIn("reasoning_basis: explicit_user", text)
        self.assertIn("explicit_skill_route", text)
        self.assertIn("explicit_auto", text)
        self.assertIn("platform_default", text)
        self.assertIn("silent_default_override", text)
        self.assertIn("create_thread_arguments", text)
        self.assertIn("requested_axes", text)
        self.assertIn("requested_model", text)
        self.assertIn("requested_reasoning", text)
        self.assertIn("attempt_sha256", text)
        self.assertIn("dispatch the full ready, conflict-free wave", text)
        self.assertIn("capability is not route authority", text)
        self.assertIn("luna-max", text)

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
            "platform_default",
            "create_thread_arguments",
            "dispatch_attempt_sha256",
            "actual_create_thread_arguments",
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
            source_home = temp / "source-home"
            source_home.mkdir()
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
            env["CODEX_HOME"] = str(source_home)
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
        self.assertIn("## 验证与集成状态", proc.stdout)
        self.assertIn("## 失败、重试、中止与归档", proc.stdout)
        self.assertIn("## 接收 Agent 第一动作", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
