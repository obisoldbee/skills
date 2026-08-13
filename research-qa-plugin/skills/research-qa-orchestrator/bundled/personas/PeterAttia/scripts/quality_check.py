#!/usr/bin/env python3
"""
自动检查生成的SKILL.md是否通过fuxi-skill的Phase 4质量标准。

fuxi-skill 9 项检查（v2）：
  1. 心智模型数量（3-7 个）
  2. 表达 DNA 辨识度（≥3 项特征）
  3. 内在张力（≥2 对，源自人物自述）
  4. 决策启发式数量（5-10 条）
  5. 心智模型 vs 决策启发式区分度（两个 section 都在 + 字符数 >100）
  6. "我"的视角一致性（第一人称 ≥10 / 3rd-person 泛指代词 <5）
  7. 关键金句 section 存在（v2 新增：替代 v1 的"角色扮演规则"——v2 SKILL 不再要求角色扮演规则）
  8. 回答工作流（Agentic Protocol）section 存在
  9. 调研素材引用（≥5 处 references/research/ 路径或字幕文件名）

v2 vs v1 改动：
  - 删除"角色扮演规则 section 存在"检查（v2 SKILL 不要求激活/退出角色）
  - 删除"字幕文件路径 ≥5 处"硬性要求（agent 看不到字幕）
  - 改为检查 references/research/ 路径（fact-check 友好）
  - 第一人称一致性：3rd-person 检查排除人名（角色扮演中提自己姓名不算漂移）
  - 决策启发式：只数主标题（### 启发式 N）不算列表项

删除（与 nuwa-skill 相比）：
  - 模型局限性硬性要求（不自证局限）
  - 诚实边界 ≥3 条（不要诚实边界 section）
  - 本人素材占比（你自用，知道素材来源）

用法:
    python3 quality_check.py <SKILL.md路径>

示例:
    python3 quality_check.py .claude/skills/[name]-perspective/SKILL.md
"""

import sys
import re
from pathlib import Path


def parse_sections(content: str) -> list[tuple[str, str]]:
    """行级解析 SKILL.md，返回 [(section_name, section_body), ...]"""
    sections = []
    current_name = None
    current_lines = []
    for line in content.split('\n'):
        if re.match(r'^##\s+', line):
            if current_name is not None:
                sections.append((current_name, '\n'.join(current_lines)))
            current_name = line
            current_lines = []
        else:
            if current_name is not None:
                current_lines.append(line)
    if current_name is not None:
        sections.append((current_name, '\n'.join(current_lines)))
    return sections


def find_section(content: str, name_pattern: str) -> tuple[bool, str]:
    """查找匹配 pattern 的 section，返回 (存在, 内容)"""
    sections = parse_sections(content)
    for sec_name, sec_body in sections:
        if re.search(name_pattern, sec_name):
            return True, sec_body
    return False, ""


def extract_main_body(content: str) -> str:
    """提取 frontmatter 之后的正文（排除 --- 之间的元数据）"""
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            content = content[end + 3:]
    return content


def check_mental_models(content: str) -> tuple[bool, str]:
    """1. 心智模型数量（3-7 个）"""
    exists, section = find_section(content, r'心智模型|Mental Model')
    if not exists:
        return False, "未检测到心智模型 section"

    # 数 ### 子项
    items = re.findall(r'^###\s+', section, re.MULTILINE)
    count = len(items)
    if count == 0:
        return False, "心智模型 section 存在但无 ### 子项"
    passed = 3 <= count <= 7
    return passed, f"{count}个心智模型 {'PASS' if passed else 'FAIL (应为3-7个)'}"


def check_expression_dna(content: str) -> tuple[bool, str]:
    """2. 表达 DNA 辨识度（≥3 项特征）"""
    exists, section = find_section(content, r'表达\s?DNA|Expression\s?DNA|表达风格|表达特征')
    if not exists:
        return False, "未找到表达 DNA section"

    # 特征词
    style_markers = re.findall(
        r'句式|词汇|语气|幽默|节奏|确定性|引用|口头禅|高频词|句法|语速|用词|情绪|长短句|修辞',
        section, re.IGNORECASE
    )
    count = len(set(style_markers))
    passed = count >= 3
    return passed, f"表达 DNA 特征: {count}项 {'PASS' if passed else 'FAIL (应≥3项)'}"


def check_tensions(content: str) -> tuple[bool, str]:
    """3. 内在张力（≥2 对，源自人物自述）"""
    # fuxi-skill: 接受"内在张力"、"内在矛盾"、"价值观与反模式"等 section
    # 因为内在矛盾经常嵌在"价值观与反模式"section 里
    sections = parse_sections(content)
    candidate_bodies = []
    for sec_name, sec_body in sections:
        if re.search(r'内在张力|内在矛盾|Tensions|Paradoxes|价值观与反模式', sec_name):
            candidate_bodies.append(sec_body)

    if not candidate_bodies:
        return False, "未找到内在张力/矛盾/价值观与反模式 section"

    combined = '\n'.join(candidate_bodies)
    tension_markers = re.findall(
        r'张力|矛盾|tension|paradox|一方面.*另一方面|既.*又',
        combined, re.IGNORECASE
    )
    count = len(tension_markers)
    passed = count >= 2
    return passed, f"内在张力: {count}处 {'PASS' if passed else 'FAIL (应≥2对，建议源自人物自述而非与外部主流冲突)'}"


def check_decision_heuristics(content: str) -> tuple[bool, str]:
    """4. 决策启发式数量（5-10 条）"""
    exists, section = find_section(content, r'决策启发式|Heuristics|Decision Rules')
    if not exists:
        return False, "未找到决策启发式 section"

    # 只数 ### 启发式 N 这种主标题（每条启发式一个），不数 list item
    # 因为启发式内部常包含"原话""案例"等列表项
    items = re.findall(r'^###\s+(?:启发式|Heuristic)\s*\d', section, re.MULTILINE | re.IGNORECASE)
    count = len(items)
    if count == 0:
        # fallback: 数"### N"开头的标题
        items = re.findall(r'^###\s+\d+[.、\s]', section, re.MULTILINE)
        count = len(items)
    passed = 5 <= count <= 10
    return passed, f"决策启发式: {count}条 {'PASS' if passed else 'FAIL (应5-10条)'}"


def check_mental_vs_heuristic_distinction(content: str) -> tuple[bool, str]:
    """5. 心智模型 vs 决策启发式区分度（两个 section 都在 + 字符数 >100）"""
    mm_exists, mm_section = find_section(content, r'心智模型|Mental Model')
    dh_exists, dh_section = find_section(content, r'决策启发式|Heuristics|Decision Rules')

    if not mm_exists:
        return False, "未找到心智模型 section"
    if not dh_exists:
        return False, "未找到决策启发式 section"

    mm_len = len(mm_section.strip())
    dh_len = len(dh_section.strip())

    if mm_len < 100:
        return False, f"心智模型 section 字符数 {mm_len} < 100，可能过简"
    if dh_len < 100:
        return False, f"决策启发式 section 字符数 {dh_len} < 100，可能过简"

    return True, f"心智模型 {mm_len} 字符 + 决策启发式 {dh_len} 字符，区分度 PASS"


def check_first_person_consistency(content: str) -> tuple[bool, str]:
    """6. "我"的视角一致性（第一人称 ≥10 / 3rd-person <5）"""
    main_body = extract_main_body(content)

    # 第一人称代词
    first_person = re.findall(r'我|我的|我们|我们的', main_body)
    fp_count = len(first_person)

    # 3rd-person 引用——但要排除"角色扮演中提自己姓名"的情况
    # 角色扮演里"Berg 公开说 X"——这是叙述者=Berg，所以是 1st-person
    # 真正的 3rd-person 是泛指代词（此人 / 该人物 / 他 / 她）
    third_person_markers = re.findall(
        r'\b(此人|该人物|他|她|他们)\b',
        main_body
    )
    tp_count = len(third_person_markers)

    if fp_count < 10:
        return False, f"第一人称代词 {fp_count} < 10，角色扮演视角不足"
    if tp_count > 5:
        return False, f"3rd-person 引用 {tp_count} > 5，视角漂移"

    return True, f"第一人称 {fp_count} 次 / 3rd-person {tp_count} 处 PASS"


def check_key_quote_section(content: str) -> tuple[bool, str]:
    """7. 关键金句 section 存在（替代"角色扮演规则"——v2 不再要求角色扮演规则）"""
    exists, _ = find_section(content, r'关键金句|Key\s?Quotes?|核心引语')
    return (True, "关键金句 section 存在 PASS") if exists else (False, "未找到关键金句 section")


def check_agentic_protocol(content: str) -> tuple[bool, str]:
    """8. 回答工作流（Agentic Protocol）section 存在"""
    exists, _ = find_section(content, r'回答工作流|Agentic\s?Protocol|Work\s?Flow')
    return (True, "回答工作流 section 存在 PASS") if exists else (False, "未找到回答工作流 section")


def check_research_source_citation(content: str) -> tuple[bool, str]:
    """9. 调研素材引用（v2 改：检查产物 SKILL 应"无"调研文件路径）

    v2 设计：SKILL.md 是角色 prompt，不应含调研文件路径（references/research/）
    或字幕文件名——这些是蒸馏过程产物，不应进入角色 prompt。
    如果 SKILL 大量引用调研文件，意味着没有清理蒸馏过程产物，违反 v2 设计原则。
    """
    # 模式 1: references/research/ 路径
    research_paths = re.findall(r'references/research/\d+-[a-z\-]+\.md', content)
    # 模式 2: 调研文件名
    research_files = re.findall(r'0[1-6]-[a-z\-]+\.md', content)
    # 模式 3: 字幕文件名
    caption_files = re.findall(r'\b(20[0-9]{6})[0-9]{3}\.md\b', content)

    total = len(set(research_paths)) + len(set(research_files)) + len(set(caption_files))
    # v2 反向检查：SKILL 不应有调研素材引用（≤3 处可接受，过多表示没清理）
    passed = total <= 3
    detail = f"调研素材引用 {total} 处 {'PASS' if passed else 'FAIL (应≤3处——v2 SKILL 不应含蒸馏过程产物)'}"
    if total > 0:
        detail += f"；如保留少量属正常（如调研路径在引用来源section）"
    return passed, detail

def main():
    if len(sys.argv) < 2:
        print("用法: python3 quality_check.py <SKILL.md路径>")
        sys.exit(1)

    skill_path = Path(sys.argv[1])
    if not skill_path.exists():
        print(f"FAIL 文件不存在: {skill_path}")
        sys.exit(1)

    content = skill_path.read_text(encoding='utf-8')

    checks = [
        ("1.心智模型数量", check_mental_models),
        ("2.表达DNA辨识度", check_expression_dna),
        ("3.内在张力", check_tensions),
        ("4.决策启发式数量", check_decision_heuristics),
        ("5.心智vs启发式区分", check_mental_vs_heuristic_distinction),
        ("6.第一人称一致性", check_first_person_consistency),
        ("7.关键金句section", check_key_quote_section),
        ("8.回答工作流", check_agentic_protocol),
        ("9.调研素材引用", check_research_source_citation),
    ]

    print(f"fuxi-skill 质量检查: {skill_path.name}")
    print("=" * 60)

    passed_count = 0
    total = len(checks)
    results = []

    for name, check_fn in checks:
        passed, detail = check_fn(content)
        status = "PASS" if passed else "FAIL"
        print(f"  {name:<24} {status:<5} {detail}")
        results.append((name, passed, detail))
        if passed:
            passed_count += 1

    print("=" * 60)
    print(f"结果: {passed_count}/{total} 通过")
    print()

    if passed_count == total:
        print("全部通过，可以交付")
    elif passed_count >= total - 2:
        print("基本通过，建议修复 FAIL 项后交付")
    else:
        print("多项不通过，建议回到 Phase 2 迭代")

    print()
    print("=" * 60)
    print("fuxi-skill 9 项检查说明：")
    print("  [1-3] 保留自 nuwa-skill（结构质量）")
    print("  [4-9] fuxi-skill 新增（自用头脑风暴场景适配）")
    print("  删除了 nuwa-skill 的：模型局限性、诚实边界、本人素材占比")

    sys.exit(0 if passed_count == total else 1)


if __name__ == '__main__':
    main()
