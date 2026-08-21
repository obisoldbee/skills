#!/usr/bin/env python3
"""
重建 download-manifest.json：根据磁盘上已有的 PDF 文件同步状态
用法: python3 rebuild_manifest.py [paper_dir] [manifest_file] [papers_json]
环境变量:
  PAPER_DIR     - PDF 保存目录 (默认: ./paper)
  MANIFEST_FILE - manifest JSON 路径 (默认: ./download-manifest.json)
  PAPERS_JSON   - 论文列表 JSON (默认: ./pmc_papers.json)
"""
import json
import os
import hashlib
import sys

PAPERS_JSON = sys.argv[3] if len(sys.argv) > 3 else os.environ.get('PAPERS_JSON', './pmc_papers.json')
OUTPUT_DIR = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('PAPER_DIR', './paper')
MANIFEST_FILE = sys.argv[2] if len(sys.argv) > 2 else os.environ.get('MANIFEST_FILE', './download-manifest.json')

def is_valid_pdf(filepath):
    if not os.path.exists(filepath):
        return False
    size = os.path.getsize(filepath)
    if size < 10000:
        return False
    with open(filepath, 'rb') as f:
        header = f.read(4)
    return header == b'%PDF'

def get_pmcid_from_filename(fname):
    fname = fname.replace('.pdf', '')
    if fname.startswith('PMC') and '__' in fname:
        return fname.split('__')[0]
    if '__PMC' in fname:
        parts = fname.split('__')
        for p in parts:
            if p.startswith('PMC'):
                return p
    return None

def main():
    with open(PAPERS_JSON, 'r', encoding='utf-8') as f:
        papers = json.load(f)

    paper_by_pmcid = {p['pmcid']: p for p in papers}

    downloaded = {}
    for fname in os.listdir(OUTPUT_DIR):
        if not fname.endswith('.pdf'):
            continue
        fpath = os.path.join(OUTPUT_DIR, fname)
        if not is_valid_pdf(fpath):
            continue

        pmcid = get_pmcid_from_filename(fname)
        if pmcid and pmcid in paper_by_pmcid:
            downloaded[pmcid] = {
                'filename': fname,
                'file_size_bytes': os.path.getsize(fpath),
                'sha256': hashlib.sha256(open(fpath, 'rb').read()).hexdigest()
            }

    manifest = []
    for paper in papers:
        pmcid = paper['pmcid']
        if pmcid in downloaded:
            info = downloaded[pmcid]
            manifest.append({
                'pmcid': pmcid,
                'pmid': paper.get('pmid'),
                'doi': paper.get('dois', [None])[0] if paper.get('dois') else None,
                'title': paper.get('title', ''),
                'section': paper.get('section', ''),
                'filename': info['filename'],
                'status': 'downloaded',
                'file_size_bytes': info['file_size_bytes'],
                'sha256': info['sha256'],
                'download_method': 'rebuild_from_disk',
                'downloaded_at': time.strftime('%Y-%m-%d') if 'time' in dir() else '2026-06-23'
            })
        else:
            manifest.append({
                'pmcid': pmcid,
                'pmid': paper.get('pmid'),
                'doi': paper.get('dois', [None])[0] if paper.get('dois') else None,
                'title': paper.get('title', ''),
                'section': paper.get('section', ''),
                'filename': paper.get('filename', f"{pmcid}__pmc.pdf"),
                'status': 'pending'
            })

    mdir = os.path.dirname(MANIFEST_FILE)
    if mdir:
        os.makedirs(mdir, exist_ok=True)
    with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    downloaded_count = sum(1 for m in manifest if m['status'] == 'downloaded')
    pending_count = sum(1 for m in manifest if m['status'] == 'pending')

    print(f"{'=' * 60}")
    print(f"Manifest 重建完成")
    print(f"  总计: {len(manifest)}")
    print(f"  已下载: {downloaded_count}")
    print(f"  待下载: {pending_count}")
    print(f"{'=' * 60}")

    from collections import Counter
    sections = Counter(m['section'] for m in manifest)
    print(f"\n按 section 统计:")
    for s in sorted(sections.keys()):
        dl = sum(1 for m in manifest if m['section'] == s and m['status'] == 'downloaded')
        total = sections[s]
        print(f"  Section {s}: {dl}/{total}")

if __name__ == '__main__':
    import time
    main()
