#!/usr/bin/env python3
"""Offline package shape, source syntax, link and local-data checks."""
import ast
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

EXPECTED = {'SKILL.md', 'agents/openai.yaml', 'references/private-state.md',
            'references/change-validation.md', 'scripts/rules_inventory.py',
            'scripts/validate_package.py', 'tests/test_inventory.py'}

def validate(root):
    issues=[]
    files=set()
    for p in root.rglob('*'):
        rel=p.relative_to(root).as_posix()
        if p.is_symlink():
            issues.append('symlink:'+rel)
        elif p.is_file():
            files.add(rel)
            try:
                s=p.read_text()
                if re.search(r'/(?:Users|home)/[^/\s]+/',s):issues.append('private-home:'+rel)
                if p.suffix=='.py':ast.parse(s)
                if p.suffix=='.md':
                    for target in re.findall(r'\[[^\]]*\]\(([^ )]+)\)',s):
                        if urlsplit(target).scheme or target.startswith('#'):continue
                        dest=(p.parent/target.split('#')[0]).resolve()
                        if not dest.is_relative_to(root.resolve()) or not dest.is_file():issues.append('link:'+rel)
            except (ValueError,UnicodeError,SyntaxError):issues.append('syntax:'+rel)
    if files != EXPECTED:issues.append('unexpected_or_missing_files:'+','.join(sorted(files^EXPECTED)))
    if not (root/'SKILL.md').read_text().startswith('---\nname: clash-direct-rules\n'):issues.append('metadata')
    return issues

if __name__=='__main__':
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
    issues=validate(root)
    print(json.dumps({'valid':not issues,'issues':issues}))
    sys.exit(bool(issues))
