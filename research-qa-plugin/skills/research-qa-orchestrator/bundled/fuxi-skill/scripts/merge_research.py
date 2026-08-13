#!/usr/bin/env python3
"""
合并 6 个 Agent 的调研结果，生成 fuxi-skill Phase 1.5 调研 Review 检查点的摘要表格。

fuxi-skill 适配（与 nuwa-skill 的差异）：
  - 不强调"一手/二手"占比，改为"本人素材/他源素材"占比
  - 总结建议不再"在诚实边界中标注"（fuxi-skill 不要求诚实边界）
  - 简化输出

扫描 references/research/ 目录下的 01-06 md 文件，统计每个维度的来源数量、关键发现、矛盾点。

用法:
    python3 merge_research.py <skill目录路径>

示例:
    python3 merge_research.py .claude/skills/[name]-perspective

输出: 打印 markdown 格式的摘要表格到 stdout
"""

import sys
import re
from pathlib import Path

AGENTS = {
    '01-writings': '著作',
    '02-conversations': '对话',
    '03-expression-dna': '表达',
    '04-external-views': '他者',
    '05-decisions': '决策',
    '06-timeline': '时间线',
}


def count_sources(content: str) -> dict:
    """统计来源数量和本人/他源占比"""
    # 计算 URL 数量作为来源数
    urls = re.findall(r'https?://[^\s\)]+', content)

    # 本人素材标记（YouTube 字幕、本人著作、本人采访、本人博客）
    primary_markers = len(re.findall(
        r'本人|YouTube|视频字幕|本人著作|本人采访|本人博客|本人播客|原始|直接引用|本人发言',
        content, re.IGNORECASE
    ))
    # 他源素材标记（他人评价、媒体报道、评论）
    secondary_markers = len(re.findall(
        r'他人评价|媒体报道|二手|评论文章|第三方|secondary|third.party',
        content, re.IGNORECASE
    ))

    return {
        'url_count': len(urls),
        'unique_urls': len(set(urls)),
        'primary_markers': primary_markers,
        'secondary_markers': secondary_markers,
    }


def extract_key_findings(content: str, max_items: int = 3) -> list[str]:
    """提取关键发现（取前几个二级标题或加粗项）"""
    headings = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
    if headings:
        return headings[:max_items]

    bolds = re.findall(r'\*\*(.+?)\*\*', content)
    if bolds:
        return bolds[:max_items]

    lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
    return [l[:50] + '...' if len(l) > 50 else l for l in lines[:max_items]]


def find_contradictions(files: dict[str, str]) -> list[str]:
    """检测跨文件矛盾（保留 fuxi-skill 风格：不评价对错，只标记存在）"""
    contradictions = []
    for name, content in files.items():
        matches = re.findall(r'(?:矛盾|相反|但实际上|然而.*?不同|争议).{0,100}', content)
        for m in matches:
            contradictions.append(f"{AGENTS.get(name, name)}: {m[:80]}")
    return contradictions[:5]


def main():
    if len(sys.argv) < 2:
        print("用法: python3 merge_research.py <skill目录路径>")
        sys.exit(1)

    skill_dir = Path(sys.argv[1])
    research_dir = skill_dir / 'references' / 'research'

    if not research_dir.exists():
        print(f"目录不存在: {research_dir}")
        sys.exit(1)

    files = {}
    rows = []
    total_sources = 0
    total_primary = 0
    total_secondary = 0
    missing = []

    for key, label in AGENTS.items():
        md_file = research_dir / f"{key}.md"
        if not md_file.exists():
            missing.append(label)
            rows.append(f"| {label:<12} | 缺失       | -                          |")
            continue

        content = md_file.read_text(encoding='utf-8')
        files[key] = content
        stats = count_sources(content)
        findings = extract_key_findings(content)

        total_sources += stats['unique_urls']
        total_primary += stats['primary_markers']
        total_secondary += stats['secondary_markers']

        findings_str = ', '.join(findings) if findings else '-'
        if len(findings_str) > 40:
            findings_str = findings_str[:37] + '...'

        rows.append(f"| {label:<12} | {stats['unique_urls']:<8} | {findings_str:<26} |")

    contradictions = find_contradictions(files)

    # 输出 markdown 表格
    print("| Agent        | 来源数量  | 关键发现                  |")
    print("|--------------|-----------|---------------------------|")
    for row in rows:
        print(row)

    primary_ratio = f"{total_primary}/{total_primary + total_secondary}" if (total_primary + total_secondary) > 0 else "未标记"
    print(f"| **总来源**    | **{total_sources}**   | 本人素材占比: {primary_ratio:<13} |")

    if contradictions:
        print(f"| **矛盾点**    | **{len(contradictions)}处**   | {contradictions[0][:26]:<26} |")
    else:
        print(f"| **矛盾点**    | **0处**     | -                          |")

    if missing:
        print(f"| **信息不足**  | **{len(missing)}个**   | {', '.join(missing):<26} |")
    else:
        print(f"| **信息不足**  | **无**       | -                          |")

    # 总结
    print()
    if total_sources < 10:
        print("提示：总来源数 < 10，建议降低期望或补充调研")
    if missing:
        print(f"提示：缺失维度 {', '.join(missing)}，建议补充或在 SKILL 中标注")


if __name__ == '__main__':
    main()
