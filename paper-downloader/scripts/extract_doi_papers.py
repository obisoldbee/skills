#!/usr/bin/env python3
"""
提取无 PMCID 的论文，按出版社分组
用法: python3 extract_doi_papers.py <input.md> <manifest.json> [output_dir]
"""
import re
import json
import os
import sys
from collections import Counter

filepath = sys.argv[1] if len(sys.argv) > 1 else None
manifest_path = sys.argv[2] if len(sys.argv) > 2 else './download-manifest.json'
output_dir = sys.argv[3] if len(sys.argv) > 3 else '.'

def identify_publisher(doi):
    if not doi:
        return 'unknown'
    d = doi.lower()
    if d.startswith('10.3390'): return 'MDPI'
    if d.startswith('10.3389'): return 'Frontiers'
    if d.startswith('10.1371'): return 'PLOS'
    if d.startswith('10.1186'): return 'BMC'
    if d.startswith('10.2147'): return 'DovePress'
    if d.startswith('10.3892'): return 'Spandidos'
    if d.startswith('10.1161'): return 'JAHA_AHA'
    if d.startswith('10.7150'): return 'Theranostics'
    if d.startswith('10.18632'): return 'Oncotarget'
    if d.startswith('10.3748'): return 'WJG'
    if d.startswith('10.1007'): return 'Springer'
    if d.startswith('10.1038'): return 'Nature'
    if d.startswith('10.1016'): return 'Elsevier'
    if d.startswith('10.1002'): return 'Wiley'
    if d.startswith('10.1001'): return 'JAMA'
    if d.startswith('10.1093'): return 'Oxford'
    if d.startswith('10.1080'): return 'TandF'
    if d.startswith('10.1177') or d.startswith('10.1176'): return 'Sage'
    if d.startswith('10.1021'): return 'ACS'
    if d.startswith('10.1039'): return 'RSC'
    if d.startswith('10.1158'): return 'AACR'
    if d.startswith('10.1056'): return 'NEJM'
    if d.startswith('10.1159'): return 'Karger'
    if d.startswith('10.1097'): return 'LWW_WoltersKluwer'
    if d.startswith('10.1017'): return 'Cambridge'
    if d.startswith('10.1055'): return 'Thieme'
    if d.startswith('10.1210'): return 'EndocrineSociety'
    if d.startswith('10.1126'): return 'Science_AAAS'
    if d.startswith('10.1136'): return 'BMJ'
    if d.startswith('10.1111'): return 'Wiley_Blackwell'
    if d.startswith('10.7307'): return 'AnticancerResearch'
    if d.startswith('10.2337'): return 'ADA_Diabetes'
    if d.startswith('10.1084'): return 'JEM_Rockefeller'
    if d.startswith('10.4049'): return 'J_Immunol'
    if d.startswith('10.1073'): return 'PNAS'
    if d.startswith('10.1074'): return 'JBC'
    if d.startswith('10.1194'): return 'JLR_Lipids'
    if d.startswith('10.3168'): return 'JDS_Dairy'
    if d.startswith('10.3945'): return 'ASN_Nutrition'
    if d.startswith('10.1096'): return 'FASEB'
    return 'other'

with open(manifest_path) as f:
    manifest = json.load(f)
all_pmcids_in_manifest = set(m['pmcid'] for m in manifest if m.get('pmcid'))

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

table_ranges = {}
current_table = None
for i, line in enumerate(lines):
    m = re.match(r'^## ([A-H])\.', line)
    if m:
        if current_table:
            table_ranges[current_table] = (table_ranges[current_table][0], i)
        current_table = m.group(1)
        table_ranges[current_table] = (i, len(lines))
if current_table:
    table_ranges[current_table] = (table_ranges[current_table][0], len(lines))

papers = []
for table_name in ['B', 'C', 'D', 'E', 'F', 'G', 'H']:
    if table_name not in table_ranges:
        continue
    start, end = table_ranges[table_name]
    for i in range(start, end):
        line = lines[i]
        if not line.strip().startswith('|'):
            continue
        if re.match(r'^\|[\s\-:|]+\|\s*$', line):
            continue

        pmcids = re.findall(r'PMC\d+', line)
        dois = re.findall(r'(?:doi:|doi\.org/)?(10\.\d{4,9}/[^\s<>"\';,)]+)', line, re.IGNORECASE)
        clean_dois = []
        for d in dois:
            d = d.rstrip('.,;)"')
            if len(d) > 8:
                clean_dois.append(d)
        unique_dois = list(dict.fromkeys(clean_dois))

        pmids = re.findall(r'PMID[:\s]*(\d{6,})', line)

        if pmcids:
            all_handled = all(p in all_pmcids_in_manifest for p in pmcids)
            if all_handled:
                continue

        if not unique_dois and not pmids:
            continue

        main_doi = unique_dois[0] if unique_dois else None
        pmid = pmids[0] if pmids else None
        publisher = identify_publisher(main_doi)

        papers.append({
            'section': table_name,
            'doi': main_doi,
            'all_dois': unique_dois[:3],
            'pmid': pmid,
            'pmcids': pmcids,
            'publisher': publisher,
            'line': i + 1,
        })

pub_counts = Counter(p['publisher'] for p in papers)
print(f"=== 无 PMCID（或有未处理 PMCID）的论文 ===")
print(f"总计: {len(papers)} 篇\n")
print(f"按出版社分组:")
oa_publishers = {'MDPI', 'Frontiers', 'PLOS', 'BMC', 'DovePress', 'Spandidos',
                 'JAHA_AHA', 'Theranostics', 'Oncotarget', 'WJG', 'AnticancerResearch'}
for pub, count in pub_counts.most_common():
    tag = " [OA]" if pub in oa_publishers else ""
    print(f"  {pub:25s}: {count:4d}{tag}")

no_doi = [p for p in papers if not p['doi']]
print(f"\n无 DOI 的论文: {len(no_doi)} 篇")
no_ids = [p for p in papers if not p['doi'] and not p['pmid']]
print(f"既无 DOI 也无 PMID: {len(no_ids)} 篇")

batch1 = [p for p in papers if p['publisher'] in oa_publishers]
batch2 = [p for p in papers if p['publisher'] in {'Springer', 'Nature', 'Science_AAAS', 'BMJ'}]
batch3 = [p for p in papers if p['publisher'] in
          {'Oxford', 'LWW_WoltersKluwer', 'TandF', 'NEJM', 'Karger', 'Sage', 'AACR', 'PNAS', 'JBC'}]
batch4 = [p for p in papers if p['publisher'] in
          {'Wiley', 'Wiley_Blackwell', 'JAMA', 'EndocrineSociety', 'Thieme', 'Elsevier', 'ACS', 'RSC'}]
batch5 = [p for p in papers if p['publisher'] == 'other']
classified = set()
for b in [batch1, batch2, batch3, batch4, batch5]:
    for p in b:
        classified.add(id(p))
batch5 += [p for p in papers if id(p) not in classified]

print(f"\n=== 分批策略 ===")
print(f"第一波 OA高成功率: {len(batch1)} 篇")
print(f"第二波 Springer/Nature/Science/BMJ: {len(batch2)} 篇")
print(f"第三波 常被误判为付费墙: {len(batch3)} 篇")
print(f"第四波 高付费墙概率: {len(batch4)} 篇")
print(f"第五波 小出版社/其他: {len(batch5)} 篇")

os.makedirs(output_dir, exist_ok=True)
output = os.path.join(output_dir, 'doi_papers.json')
with open(output, 'w', encoding='utf-8') as f:
    json.dump(papers, f, ensure_ascii=False, indent=2)

batches = {'batch1_oa': batch1, 'batch2_springer_nature': batch2,
           'batch3_often_oa': batch3, 'batch4_likely_paywall': batch4, 'batch5_small': batch5}
for name, batch in batches.items():
    path = os.path.join(output_dir, f'{name}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(batch, f, ensure_ascii=False, indent=2)

print(f"\n所有数据已保存")
