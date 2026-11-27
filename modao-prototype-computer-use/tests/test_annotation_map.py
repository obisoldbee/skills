"""Regression cases for the observed note-coverage and leader-layout failures."""

import json
import unittest
from pathlib import Path

from scripts.check_annotation_map import check, lines_conflict


class AnnotationMapTests(unittest.TestCase):
    def setUp(self):
        sample = Path(__file__).resolve().parents[1] / "examples" / "annotation-map.json"
        self.sheet = json.loads(sample.read_text(encoding="utf-8"))

    def test_nearby_straight_leaders(self):
        result = check(self.sheet)
        self.assertEqual((result["missing"], result["crossing_pairs"], result["issues"]), ([], [], []))

    def test_count_matches_but_rule_is_missing(self):
        self.sheet["notes"][1]["rules"] = ["R1"]  # Two notes, but neither explains the Save rule.
        result = check(self.sheet)
        self.assertEqual(result["missing"], ["R2"])
        self.assertTrue(result["issues"])

    def test_swap_boxes_and_keep_both_correct_targets(self):
        a, b = self.sheet["notes"]
        a["box"], b["box"] = b["box"], a["box"]
        a["line"][0], b["line"][0] = b["line"][0], a["line"][0]
        result = check(self.sheet)
        self.assertEqual(result["crossing_pairs"], [[a["id"], b["id"]]])
        self.assertEqual(result["missing"], [])

    def test_shared_tip_allowed_but_overlapping_tail_flagged(self):
        route = [(0, 0), (10, 0)]
        self.assertFalse(lines_conflict(route, [(10, 8), (10, 0)], True))
        self.assertTrue(lines_conflict(route, [(4, 8), (4, 0), (10, 0)], True))

    def test_bend_contacts_another_text_box(self):
        a, _ = self.sheet["notes"]
        a["line"] = [[320, 112], [540, 112], [540, 252], [255, 252], [210, 112]]
        self.assertTrue(any("触及" in item for item in check(self.sheet)["issues"]))

    def test_wrong_or_floating_endpoint_even_when_count_matches(self):
        a, _ = self.sheet["notes"]
        a["line"] = [[290, 112], [220, 112]]
        issues = check(self.sheet)["issues"]
        self.assertTrue(any("起点" in item for item in issues))
        self.assertTrue(any("线尾" in item for item in issues))

    def test_a_note_is_clipped_in_the_page_export(self):
        self.sheet["bounds"] = [0, 0, 500, 210]
        result = check(self.sheet)
        self.assertEqual(result["missing"], [])
        self.assertTrue(any("图像边界" in item for item in result["issues"]))

    def test_self_crossing_leader_and_retrace_are_reported(self):
        note = self.sheet["notes"][0]
        for route in (
            [[320, 112], [260, 145], [300, 145], [260, 110], [210, 112]],
            [[320, 112], [250, 112], [265, 112], [210, 112]],
        ):
            with self.subTest(route=route):
                note["line"] = route
                result = check(self.sheet)
                self.assertEqual(result["crossing_pairs"], [])
                self.assertTrue(any("自交" in item for item in result["issues"]))

    def test_leader_from_far_edge_runs_through_its_own_box(self):
        self.sheet["notes"][0]["line"][0] = [540, 112]
        self.assertTrue(any("自己的文字框" in item for item in check(self.sheet)["issues"]))

    def test_valid_bends_and_attachment_tolerance(self):
        self.sheet["notes"][0]["line"] = [[322, 112], [280, 112], [280, 110], [210, 110]]
        self.assertEqual(check(self.sheet)["issues"], [])

    def test_target_visibility_at_export_edge(self):
        note = self.sheet["notes"][0]
        self.sheet["bounds"] = [40, 0, 560, 320]
        note["line"][-1] = [40, 112]
        for target_right, visible in [(39, False), (40, False), (41, True)]:
            with self.subTest(target_right=target_right):
                self.sheet["targets"][note["target"]] = [target_right - 15, 100, 15, 30]
                issues = check(self.sheet)["issues"]
                self.assertEqual(bool(issues), not visible)
                if not visible:
                    self.assertIn("没有可见区域", issues[0])
