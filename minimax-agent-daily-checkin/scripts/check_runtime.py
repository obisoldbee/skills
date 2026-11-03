#!/usr/bin/env python3
"""Probe the installed ego-browser CLI without opening a space or visiting a site."""
import json
from pathlib import Path
import shutil
import subprocess


def check():
    cli = shutil.which('ego-browser')
    if not cli:
        candidate = Path.home()/'.local/bin/ego-browser'
        if candidate.is_file(): cli = str(candidate)
    if not cli:
        return {'status':'runtime_unavailable','reason':'未找到已安装的 ego-browser 命令'}
    script = 'await listTaskSpaces(); console.log("MINIMAX_RUNTIME_OK");'
    try:
        result = subprocess.run([cli,'nodejs','-e',script],capture_output=True,text=True,timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return {'status':'runtime_unavailable','cli':cli,'reason':'浏览器连接检测失败或超时'}
    if result.returncode or 'MINIMAX_RUNTIME_OK' not in result.stdout+result.stderr:
        return {'status':'runtime_unavailable','cli':cli,'reason':'浏览器命令实际调用失败',
                'exit_code':result.returncode}
    skills = [Path.home()/p/'ego-browser/SKILL.md' for p in ('.agents/skills','.codex/skills')]
    return {'status':'available','cli':cli,
            'skill_paths':[str(p) for p in skills if p.is_file()]}


if __name__ == '__main__':
    value = check()
    print(json.dumps(value,ensure_ascii=False))
    raise SystemExit(0 if value['status']=='available' else 1)
