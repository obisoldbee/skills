"""Check one canvas's observed leaders and an independently prepared rule list."""

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path


def coords(value, size):
    if not isinstance(value, list) or len(value) != size or any(type(n) is not int for n in value):
        raise ValueError(f"坐标需为 {size} 个整数")
    return tuple(value)


def rect(value):
    x, y, w, h = coords(value, 4)
    if w <= 0 or h <= 0:
        raise ValueError("矩形的宽高必须为正数")
    return x, y, x + w, y + h


def inside(p, box, tolerance=0):
    x, y = p
    l, t, r, b = box
    return l - tolerance <= x <= r + tolerance and t - tolerance <= y <= b + tolerance


def side(a, b, p):
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def on_segment(p, a, b):
    return (side(a, b, p) == 0 and
            min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and
            min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))


def segments_meet(a, b, c, d, allowed_tip):
    if side(a, b, c) * side(a, b, d) < 0 and side(c, d, a) * side(c, d, b) < 0:
        return True
    contacts = {p for p in (a, b, c, d) if on_segment(p, a, b) and on_segment(p, c, d)}
    return bool(contacts - {allowed_tip})


def lines_conflict(first, second, same_target):
    for i, (a, b) in enumerate(zip(first, first[1:])):
        for j, (c, d) in enumerate(zip(second, second[1:])):
            last = i == len(first) - 2 and j == len(second) - 2
            allowed_tip = b if same_target and last and b == d else None
            if segments_meet(a, b, c, d, allowed_tip):
                return True
    return False


def self_intersects(line):
    segments = list(zip(line, line[1:]))
    for i, (a, b) in enumerate(segments):
        for j in range(i + 1, len(segments)):
            c, d = segments[j]
            # Consecutive segments may meet at their bend, but may not retrace it.
            shared_bend = b if j == i + 1 else None
            if segments_meet(a, b, c, d, shared_bend):
                return True
    return False


def crosses_own_text_box(line, box):
    # Ignore the same two-pixel measurement tolerance used for the attachment.
    left, top, right, bottom = box
    left, top, right, bottom = left + 2, top + 2, right - 2, bottom - 2
    if left >= right or top >= bottom:
        return False
    corners = [(left, top), (right, top), (right, bottom), (left, bottom)]
    for a, b in zip(line, line[1:]):
        if max(a[0], b[0]) <= left or min(a[0], b[0]) >= right:
            continue
        if max(a[1], b[1]) <= top or min(a[1], b[1]) >= bottom:
            continue
        # With overlapping x/y ranges, the segment enters the open rectangle
        # exactly when its supporting line has corners on both sides.
        sides = [side(a, b, corner) for corner in corners]
        if min(sides) < 0 < max(sides):
            return True
    return False


def boxes_overlap(first, second):
    return (max(first[0], second[0]) < min(first[2], second[2]) and
            max(first[1], second[1]) < min(first[3], second[3]))


def touches_box(line, box):
    l, t, r, b = box
    border = [(l, t), (r, t), (r, b), (l, b), (l, t)]
    if any(inside(point, box) for point in line):
        return True
    return any(segments_meet(a, b, c, d, None)
               for a, b in zip(line, line[1:])
               for c, d in zip(border, border[1:]))


def named_mapping(value, label):
    if not isinstance(value, dict) or not value or not all(k.strip() for k in value):
        raise ValueError(f"{label} 需按名称列出至少一项")
    return value


def check(data):
    bounds = rect(data["bounds"])
    targets = {k: rect(v) for k, v in named_mapping(data["targets"], "targets").items()}
    required = named_mapping(data["required"], "required")
    if not all(isinstance(v, str) and v in targets for v in required.values()):
        raise ValueError("每条应注规则必须绑定已列出的目标")
    if not isinstance(data["notes"], list):
        raise ValueError("notes 需为数组；实际没有备注时用空数组")

    observed, covered, issues = {}, set(), []
    for note in data["notes"]:
        name, target, rules = note["id"], note["target"], note["rules"]
        if not isinstance(name, str) or not name.strip() or name in observed or target not in targets:
            raise ValueError("备注缺少唯一名称或有效目标")
        if not isinstance(rules, list) or not all(isinstance(r, str) and r in required for r in rules):
            raise ValueError(f"{name} 的 rules 需列出来源清单中的规则编号")
        box = rect(note["box"])
        line = [coords(p, 2) for p in note["line"]]
        if len(line) < 2 or any(a == b for a, b in zip(line, line[1:])):
            raise ValueError(f"{name} 的引线需要从框边到目标的实际折点")
        observed[name] = (box, line, target)

        if not (inside(box[:2], bounds) and inside(box[2:], bounds) and all(inside(p, bounds) for p in line)):
            issues.append(f"{name} 的框或引线超出图像边界")
        start = line[0]
        edge_distance = min(abs(start[i % 2] - edge) for i, edge in enumerate(box))
        if not inside(start, box, 2) or edge_distance > 2:
            issues.append(f"{name} 的引线起点未接框边")
        if self_intersects(line):
            issues.append(f"{name} 的引线自交或沿原路折返")
        if crosses_own_text_box(line, box):
            issues.append(f"{name} 的引线穿过自己的文字框")
        if not boxes_overlap(targets[target], bounds):
            issues.append(f"{name} 的目标「{target}」在图像中没有可见区域")
        if not inside(line[-1], targets[target], 2):
            issues.append(f"{name} 的线尾未到目标「{target}」")
        for rule in rules:
            if required[rule] == target:
                covered.add(rule)
            else:
                issues.append(f"{name} 的 {rule} 应指向「{required[rule]}」")

    crossings = []
    for (n1, (box1, line1, t1)), (n2, (box2, line2, t2)) in combinations(observed.items(), 2):
        if lines_conflict(line1, line2, t1 == t2):
            crossings.append([n1, n2])
        if touches_box(line1, box2):
            issues.append(f"{n1} 的引线触及 {n2} 的文字框")
        if touches_box(line2, box1):
            issues.append(f"{n2} 的引线触及 {n1} 的文字框")
        if boxes_overlap(box1, box2):
            issues.append(f"{n1} 与 {n2} 的文字框重叠")
    return {"required": len(required), "matched_rule_ids": len(covered),
            "missing": sorted(required.keys() - covered), "crossing_pairs": crossings, "issues": issues}


def unique_keys(pairs):
    data = {}
    for key, value in pairs:
        if key in data:
            raise ValueError(f"重复字段或编号：{key}")
        data[key] = value
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("map", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.map.read_text(encoding="utf-8"), object_pairs_hook=unique_keys)
        result = check(data)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"无法检查此记录：{exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(bool(result["missing"] or result["crossing_pairs"] or result["issues"]))


if __name__ == "__main__":
    sys.exit(main())
