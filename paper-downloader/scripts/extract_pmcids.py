#!/usr/bin/env python3
"""
从 markdown 文件中提取非A表中有 PMCID 的文献
用法: python3 extract_pmcids.py <input.md> [output.json]
"""
import re
import json
import sys

MARKDOWN_FILE = sys.argv[1] if len(sys.argv) > 1 else None
OUTPUT_FILE = sys.argv[2] if len(sys.argv) > 2 else './pmc_papers.json'

def extract_pmcids(text):
    pmcids = re.findall(r'PMC\d{5,}', text)
    seen = set()
    result = []
    for pmcid in pmcids:
        if pmcid not in seen:
            seen.add(pmcid)
            result.append(pmcid)
    return result

def extract_pmids(text):
    pmids = re.findall(r'pmid:(\d{5,})', text, re.IGNORECASE)
    seen = set()
    result = []
    for pmid in pmids:
        if pmid not in seen:
            seen.add(pmid)
            result.append(pmid)
    return result

def extract_dois(text):
    dois = re.findall(r'doi:(10\.\d{4,}/[^\s<]+)', text, re.IGNORECASE)
    seen = set()
    result = []
    for doi in dois:
        doi = doi.rstrip('.,;:)]')
        if doi not in seen:
            seen.add(doi)
            result.append(doi)
    return result

def parse_markdown():
    with open(MARKDOWN_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    section_starts = {}
    for i, line in enumerate(lines):
        m = re.match(r'^## ([A-Z])\.', line)
        if m:
            section_starts[m.group(1)] = i

    print("各表起始行:")
    for sec, line_num in sorted(section_starts.items()):
        print(f"  表 {sec}: 第 {line_num+1} 行 - {lines[line_num].strip()}")

    papers = []
    seen_pmcids = set()

    for sec in ['B', 'C', 'D', 'E', 'F', 'G', 'H']:
        if sec not in section_starts:
            continue
        start = section_starts[sec]
        next_sections = [s for s in section_starts.values() if s > start]
        end = min(next_sections) if next_sections else len(lines)

        print(f"\n处理表 {sec} (第 {start+1}-{end} 行)...")

        in_table = False
        for i in range(start, end):
            line = lines[i].strip()
            if line.startswith('|优先级|'):
                in_table = True
                continue
            if in_table and line.startswith('|---'):
                continue
            if in_table and line.startswith('|'):
                cells = [c.strip() for c in line.split('|')[1:-1]]
                if len(cells) >= 7:
                    priority = cells[0]
                    identifiers = cells[1]
                    title = cells[2]
                    topics = cells[3]
                    occurrences = cells[4]
                    sources = cells[5]
                    comparison = cells[6]

                    pmcids = extract_pmcids(identifiers)
                    pmids = extract_pmids(identifiers)
                    dois = extract_dois(identifiers)

                    for pmcid in pmcids:
                        if pmcid not in seen_pmcids:
                            seen_pmcids.add(pmcid)
                            pmid_part = f"PMID_{pmids[0]}__" if pmids else ""
                            filename = f"{pmid_part}{pmcid}__pmc.pdf"

                            papers.append({
                                'section': sec,
                                'pmcid': pmcid,
                                'pmid': pmids[0] if pmids else None,
                                'dois': dois,
                                'title': title[:200],
                                'priority': priority,
                                'topics': topics,
                                'sources': sources,
                                'comparison': comparison[:200],
                                'filename': filename,
                                'download_status': 'pending'
                            })

    print(f"\n总计提取到 {len(papers)} 篇有唯一 PMCID 的文献（去重后）")

    from collections import Counter
    sec_counts = Counter(p['section'] for p in papers)
    for sec in sorted(sec_counts.keys()):
        print(f"  表 {sec}: {sec_counts[sec]} 篇")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到: {OUTPUT_FILE}")
    return papers

if __name__ == '__main__':
    papers = parse_markdown()
