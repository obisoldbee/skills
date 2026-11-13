import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from common import package_relative, sha256_file, stable_id  # noqa: E402
from capture_pipeline import decide_gate  # noqa: E402
from plan_batch import batch_write_lock  # noqa: E402


class BatchQualityGateTests(unittest.TestCase):
    def test_login_phrase_in_substantive_article_is_not_a_wall(self):
        paragraphs = ["研究方法讨论采样过程与证据的适用范围。" * 18,
                      "数据分析需要比较多个来源并保留不确定性。" * 18 + "登录后可添加书签。"]
        html = "<article>" + "".join(f"<p>{p}</p>" for p in paragraphs) + "</article>"
        self.assertEqual("pass", decide_gate(html, rendered=True)["status"])

    def test_short_and_repeated_loading_walls_are_not_articles(self):
        for paragraphs in (["登录后继续", "请登录"], ["加载中" * 180, "加载中" * 180]):
            html = "<article>" + "".join(f"<p>{p}</p>" for p in paragraphs) + "</article>"
            self.assertNotEqual("pass", decide_gate(html, rendered=True)["status"])

    def run_plan(self, root: Path, out_dir: Path, *urls: str):
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [
                sys.executable,
                "-B",
                str(SCRIPT_DIR / "plan_batch.py"),
                "--urls",
                *urls,
                "--package-root",
                str(root),
                "--out-dir",
                str(out_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
            env=environment,
        )

    def write_case_evidence(
        self,
        root: Path,
        out_dir: Path,
        case_id: str,
        source_url: str,
        *,
        receipt_case_id: str | None = None,
        forge_empty_as_substantive: bool = False,
        include_image: bool = False,
    ) -> None:
        case_root = out_dir / "cases" / case_id
        case_root.mkdir(parents=True)
        relative_root = package_relative(case_root, root)
        intake = case_root / "intake.json"
        intake.write_text(
            json.dumps(
                {
                    "schema": "web-bookmark-intelligence/intake/v2",
                    "case_id": case_id,
                    "case_root": relative_root,
                    "input_kind": "web_page",
                    "source_locator": source_url,
                }
            ),
            encoding="utf-8",
        )
        html = case_root / "rendered.html"
        rich_document = (
            "<html><body><article><p>" + "可验证正文" * 90 + "</p><p>"
            + "第二段证据" * 90 + "</p>"
            + ("<img src='claim.png'>" if include_image else "")
            + "</article></body></html>"
        )
        html.write_text("<html><body></body></html>" if forge_empty_as_substantive else rich_document, encoding="utf-8")
        declared_quality = decide_gate(rich_document, True)
        capture = case_root / "capture.json"
        capture.write_text(
            json.dumps(
                {
                    "schema": "web-bookmark-intelligence/capture-record/v3",
                    "case_id": case_id,
                    "case_root": relative_root,
                    "intake": {
                        "path": package_relative(intake, root),
                        "sha256": sha256_file(intake),
                    },
                    "source": {
                        "url": source_url,
                        "local_html": package_relative(html, root),
                        "sha256": sha256_file(html),
                    },
                    "source_assets": [],
                    "dom_media_inventory": (
                        [
                            {
                                "dom_id": "media-0001",
                                "kind": "img",
                                "locator": "claim.png",
                                "duplicate_of": None,
                                "availability": "unavailable",
                                "source_asset": None,
                            }
                        ]
                        if include_image
                        else []
                    ),
                    "capture_adapter": "rendered_html_probe",
                    "quality_gate": declared_quality,
                }
            ),
            encoding="utf-8",
        )
        assessment = {
            "schema": "web-bookmark-intelligence/evidence-assessment/v2",
            "case_id": receipt_case_id or case_id,
            "case_root": relative_root,
            "case_binding": {"valid": True, "failures": []},
            "final_status": "full_body",
            "page_purpose_ready": True,
            "intake": {
                "path": package_relative(intake, root),
                "sha256": sha256_file(intake),
            },
            "dom": {
                "capture_path": package_relative(capture, root),
                "sha256": sha256_file(capture),
                **{
                    field: declared_quality[field]
                    for field in (
                        "body_evidence_state",
                        "body_provenance",
                        "body_meaningful_chars",
                        "dom_noise_or_placeholder",
                        "meta_description_as_body",
                    )
                },
            },
            "media": {
                "provided": False,
                "path": None,
                "sha256": None,
                "available": False,
                "inventory_required": include_image,
                "inventory_completed": False,
                "claims_required": False,
            },
        }
        (case_root / "evidence-assessment.json").write_text(
            json.dumps(assessment), encoding="utf-8"
        )

    def test_pending_quality_promotes_only_with_matching_assessment(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out_dir = root / "batch"
            out_dir.mkdir()
            valid_url = "https://example.com/valid"
            mismatched_url = "https://example.com/mismatch"
            forged_url = "https://example.com/forged"
            valid_id = stable_id("case", valid_url)
            mismatched_id = stable_id("case", mismatched_url)
            forged_id = stable_id("case", forged_url)
            prior = {
                "cases": [
                    {"case_id": valid_id, "source_url": valid_url, "status": "pending_quality"},
                    {"case_id": mismatched_id, "source_url": mismatched_url, "status": "pending_quality"},
                    {"case_id": forged_id, "source_url": forged_url, "status": "pending_quality"},
                ]
            }
            (out_dir / "batch-state.json").write_text(json.dumps(prior), encoding="utf-8")
            self.write_case_evidence(root, out_dir, valid_id, valid_url)
            self.write_case_evidence(
                root,
                out_dir,
                mismatched_id,
                mismatched_url,
                receipt_case_id="other-case",
            )
            self.write_case_evidence(
                root,
                out_dir,
                forged_id,
                forged_url,
                forge_empty_as_substantive=True,
            )

            completed = self.run_plan(root, out_dir, valid_url, mismatched_url, forged_url)

            self.assertEqual(0, completed.returncode, completed.stderr)
            batch = json.loads((out_dir / "batch-plan.json").read_text(encoding="utf-8"))
            by_url = {item["source_url"]: item for item in batch["cases"]}
            self.assertEqual("captured", by_url[valid_url]["status"])
            self.assertEqual("pending_quality", by_url[mismatched_url]["status"])
            self.assertEqual("pending_quality", by_url[forged_url]["status"])
            self.assertIn("quality_assessment", by_url[valid_url])
            self.assertNotIn("quality_assessment", by_url[mismatched_url])
            self.assertNotIn("quality_assessment", by_url[forged_url])

    def test_new_plan_never_claims_captured(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out_dir = root / "batch"

            completed = self.run_plan(root, out_dir, "https://example.com/new")

            self.assertEqual(0, completed.returncode, completed.stderr)
            batch = json.loads((out_dir / "batch-plan.json").read_text(encoding="utf-8"))
            self.assertEqual("planned", batch["cases"][0]["status"])
            self.assertTrue(batch["cases"][0]["quality_assessment_required"])

    def test_resume_reads_case_local_capture_and_assessment_from_planned(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out = root / "batch"
            urls = ("https://example.com/first", "https://example.com/second")
            self.assertEqual(self.run_plan(root, out, *urls).returncode, 0)
            def script(name, case, *args):
                result = subprocess.run(
                    [sys.executable, "-B", str(SCRIPT_DIR / name), "--package-root", str(root),
                     "--case-root", str(case), *map(str, args)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            for url in urls:
                case = out / "cases" / stable_id("case", url)
                case.mkdir(parents=True)
                intake, html, capture = case / "intake.json", case / "page.html", case / "capture.json"
                script("intake_case.py", case, "--url", url, "--out", intake)
                html.write_text("<article><p>" + "研究样本" * 100 + "</p><p>" + "对照观察" * 100 + "</p></article>")
                script("capture_pipeline.py", case, "--html", html, "--intake", intake, "--rendered", "--out", capture)
                if url == urls[0]:
                    script("assess_capture_evidence.py", case, "--intake", intake, "--capture", capture,
                           "--out", case / "evidence-assessment.json")
            def states():
                self.assertEqual(self.run_plan(root, out, *urls).returncode, 0)
                return [row["status"] for row in json.loads((out / "batch-state.json").read_text())["cases"]]
            self.assertEqual(states(), ["captured", "pending_quality"])
            script("assess_capture_evidence.py", case, "--intake", intake, "--capture", capture,
                   "--out", case / "evidence-assessment.json")
            self.assertEqual(states(), ["captured", "captured"])

    def test_subset_resume_preserves_unselected_case_with_block_reason(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out = root / "batch"
            blocked, selected = "ftp://example.com/old", "https://example.com/current"
            self.assertEqual(self.run_plan(root, out, blocked, selected).returncode, 0)
            state = out / "batch-state.json"
            previous = json.loads(state.read_text())["cases"]
            self.assertEqual(previous[0]["status"], "blocked")
            self.assertTrue(previous[0]["blocked_reason"])
            self.assertEqual(self.run_plan(root, out, selected, selected).returncode, 0)
            self.assertEqual(json.loads(state.read_text())["cases"], previous)
            self.assertEqual(json.loads((out / "batch-plan.json").read_text())["cases"], [previous[1]])

    def test_concurrent_resume_refuses_before_changing_either_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out = root / "batch"
            old, new = "ftp://example.com/blocked", "https://example.com/new"
            self.assertEqual(self.run_plan(root, out, old).returncode, 0)
            state, plan = out / "batch-state.json", out / "batch-plan.json"
            before = (state.read_bytes(), plan.read_bytes())
            for locked in (state, plan):
                with batch_write_lock(locked):
                    competing = self.run_plan(root, out, new)
                    self.assertNotEqual(competing.returncode, 0)
                    self.assertIn("cannot acquire batch write lock", competing.stderr)
                    self.assertEqual((state.read_bytes(), plan.read_bytes()), before)
            self.assertEqual(self.run_plan(root, out, new).returncode, 0)
            self.assertEqual([row["status"] for row in json.loads(state.read_bytes())["cases"]], ["blocked", "planned"])

    def test_default_plan_is_runtime_neutral_for_web_and_wechat(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out_dir = root / "batch"
            web_url = "https://example.com/article"
            wechat_url = "https://mp.weixin.qq.com/s/example"

            completed = self.run_plan(root, out_dir, web_url, wechat_url)

            self.assertEqual(0, completed.returncode, completed.stderr)
            batch = json.loads((out_dir / "batch-plan.json").read_text(encoding="utf-8"))
            self.assertEqual("web-bookmark-intelligence/batch/v3", batch["schema"])
            self.assertEqual("runtime_browser_or_case_local_html", batch["capture_pipeline"])
            self.assertEqual("runtime_selected", batch["capture_adapter"])
            self.assertNotIn("workbuddy_adapter", batch)
            self.assertEqual(2, len(batch["cases"]))
            for item in batch["cases"]:
                self.assertEqual("runtime_browser_or_case_local_html", item["capture_pipeline"])
                self.assertEqual("runtime_selected", item["capture_adapter"])
                self.assertNotIn("workbuddy_adapter", item)

    def test_resume_replaces_legacy_adapter_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out_dir = root / "batch"
            out_dir.mkdir()
            source_url = "https://example.com/resume"
            case_id = stable_id("case", source_url)
            (out_dir / "batch-state.json").write_text(
                json.dumps(
                    {
                        "schema": "web-bookmark-intelligence/batch/v2",
                        "workbuddy_adapter": "workbuddy_wechat_article_archive",
                        "cases": [
                            {
                                "case_id": case_id,
                                "source_url": source_url,
                                "status": "planned",
                                "capture_pipeline": "workbuddy_shared_pending_quality",
                                "workbuddy_adapter": "workbuddy_wechat_article_archive",
                                "capture_mode": "playwright",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            completed = self.run_plan(root, out_dir, source_url)

            self.assertEqual(0, completed.returncode, completed.stderr)
            batch = json.loads((out_dir / "batch-plan.json").read_text(encoding="utf-8"))
            item = batch["cases"][0]
            self.assertEqual("web-bookmark-intelligence/batch/v3", batch["schema"])
            self.assertEqual("runtime_browser_or_case_local_html", item["capture_pipeline"])
            self.assertEqual("runtime_selected", item["capture_adapter"])
            self.assertEqual("rendered_browser_or_case_local_html", item["capture_mode"])
            self.assertNotIn("workbuddy_adapter", batch)
            self.assertNotIn("workbuddy_adapter", item)

    def test_resume_replans_legacy_adapter_only_block_and_preserves_attempt(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out_dir = root / "batch"
            out_dir.mkdir()
            source_url = "https://example.com/recover"
            case_id = stable_id("case", source_url)
            (out_dir / "batch-state.json").write_text(
                json.dumps(
                    {
                        "schema": "web-bookmark-intelligence/batch/v2",
                        "cases": [
                            {
                                "case_id": case_id,
                                "source_url": source_url,
                                "status": "blocked",
                                "blocked_reason": "missing_workbuddy_script",
                                "capture_pipeline": "workbuddy_shared_pending_quality",
                                "workbuddy_adapter": "workbuddy_wechat_article_archive",
                                "capture_mode": "playwright",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            completed = self.run_plan(root, out_dir, source_url)

            self.assertEqual(0, completed.returncode, completed.stderr)
            item = json.loads((out_dir / "batch-plan.json").read_text(encoding="utf-8"))["cases"][0]
            self.assertEqual("planned", item["status"])
            self.assertIsNone(item["blocked_reason"])
            self.assertEqual("runtime_selected", item["capture_adapter"])
            self.assertNotIn("workbuddy_adapter", item)
            previous = item["previous_legacy_capture_attempt"]
            self.assertEqual("blocked", previous["status"])
            self.assertEqual("missing_workbuddy_script", previous["blocked_reason"])
            self.assertEqual("workbuddy_wechat_article_archive", previous["workbuddy_adapter"])

    def test_resume_keeps_captured_legacy_provenance(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out_dir = root / "batch"
            out_dir.mkdir()
            source_url = "https://example.com/captured"
            case_id = stable_id("case", source_url)
            (out_dir / "batch-state.json").write_text(
                json.dumps(
                    {
                        "schema": "web-bookmark-intelligence/batch/v2",
                        "cases": [
                            {
                                "case_id": case_id,
                                "source_url": source_url,
                                "status": "captured",
                                "capture_pipeline": "workbuddy_shared_pending_quality",
                                "workbuddy_adapter": "workbuddy_wechat_article_archive",
                                "capture_mode": "playwright",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            self.write_case_evidence(root, out_dir, case_id, source_url)

            completed = self.run_plan(root, out_dir, source_url)

            self.assertEqual(0, completed.returncode, completed.stderr)
            item = json.loads((out_dir / "batch-plan.json").read_text(encoding="utf-8"))["cases"][0]
            self.assertEqual("captured", item["status"])
            self.assertEqual("workbuddy_shared_pending_quality", item["capture_pipeline"])
            self.assertEqual("workbuddy_wechat_article_archive", item["workbuddy_adapter"])
            self.assertNotIn("capture_adapter", item)

    def test_resume_keeps_real_blocker_and_legacy_provenance(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out_dir = root / "batch"
            out_dir.mkdir()
            source_url = "https://example.com/profile-blocked"
            case_id = stable_id("case", source_url)
            (out_dir / "batch-state.json").write_text(
                json.dumps(
                    {
                        "schema": "web-bookmark-intelligence/batch/v2",
                        "cases": [
                            {
                                "case_id": case_id,
                                "source_url": source_url,
                                "status": "blocked",
                                "blocked_reason": "shoulong_profile_host_mismatch",
                                "capture_pipeline": "workbuddy_shared_pending_quality",
                                "workbuddy_adapter": "workbuddy_wechat_article_archive",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            completed = self.run_plan(root, out_dir, source_url)

            self.assertEqual(0, completed.returncode, completed.stderr)
            item = json.loads((out_dir / "batch-plan.json").read_text(encoding="utf-8"))["cases"][0]
            self.assertEqual("blocked", item["status"])
            self.assertEqual("shoulong_profile_host_mismatch", item["blocked_reason"])
            self.assertEqual("workbuddy_wechat_article_archive", item["workbuddy_adapter"])
            self.assertNotIn("capture_adapter", item)

    def test_substantive_dom_with_image_stays_pending_without_inventory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out_dir = root / "batch"
            out_dir.mkdir()
            source_url = "https://example.com/image-claim"
            case_id = stable_id("case", source_url)
            (out_dir / "batch-state.json").write_text(
                json.dumps(
                    {"cases": [{"case_id": case_id, "source_url": source_url, "status": "pending_quality"}]}
                ),
                encoding="utf-8",
            )
            self.write_case_evidence(
                root,
                out_dir,
                case_id,
                source_url,
                include_image=True,
            )

            completed = self.run_plan(root, out_dir, source_url)

            self.assertEqual(0, completed.returncode, completed.stderr)
            batch = json.loads((out_dir / "batch-plan.json").read_text(encoding="utf-8"))
            self.assertEqual("pending_quality", batch["cases"][0]["status"])
            self.assertEqual(
                "stale_or_invalid_quality_assessment",
                batch["cases"][0]["blocked_reason"],
            )

    def test_batch_url_cannot_reuse_another_urls_case(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out_dir = root / "batch"
            out_dir.mkdir()
            requested_url = "https://example.com/requested"
            evidence_url = "https://example.com/evidence"
            evidence_case_id = stable_id("case", evidence_url)
            (out_dir / "batch-state.json").write_text(
                json.dumps(
                    {
                        "cases": [
                            {
                                "case_id": evidence_case_id,
                                "source_url": requested_url,
                                "status": "pending_quality",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            self.write_case_evidence(
                root,
                out_dir,
                evidence_case_id,
                evidence_url,
            )

            completed = self.run_plan(root, out_dir, requested_url)

            self.assertEqual(0, completed.returncode, completed.stderr)
            batch = json.loads((out_dir / "batch-plan.json").read_text(encoding="utf-8"))
            self.assertEqual("pending_quality", batch["cases"][0]["status"])
            self.assertEqual(
                "stale_or_invalid_quality_assessment",
                batch["cases"][0]["blocked_reason"],
            )


if __name__ == "__main__":
    unittest.main()
