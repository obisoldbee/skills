#!/usr/bin/env python3
"""
PMC 论文下载器 v6 - 慢速重试版
用法: python3 pmc_downloader.py
环境变量:
  PAPER_DIR     - PDF 保存目录 (默认: ./paper)
  MANIFEST_FILE - manifest JSON 路径 (默认: ./download-manifest.json)
  BROWSER_DATA  - 临时浏览器数据目录 (默认: 系统临时目录下的 akashic-paperdownloader-browser-data/pmc)
"""
import json
import os
import time
import random
import base64
import tempfile
import sys
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

try:
    from playwright.sync_api import sync_playwright
except ModuleNotFoundError as exc:
    raise SystemExit(
        "blocked_runtime_missing_python_playwright: install/activate Python "
        "Playwright before running pmc_downloader.py; do not mark paper rows "
        "as failed because this runtime dependency is missing"
    ) from exc

OUTPUT_DIR = os.environ.get('PAPER_DIR', './paper')
MANIFEST_FILE = os.environ.get('MANIFEST_FILE', './download-manifest.json')
USER_DATA_DIR = os.environ.get('BROWSER_DATA',
    os.path.join(tempfile.gettempdir(), 'akashic-paperdownloader-browser-data', 'pmc'))
FAILURE_SCREENSHOT_DIR = os.environ.get(
    'FAILURE_SCREENSHOT_DIR',
    os.path.join(os.path.dirname(MANIFEST_FILE) or '.', 'failure-screenshots')
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

def safe_slug(value, fallback='unknown', limit=90):
    value = str(value or fallback)
    value = re.sub(r'[^A-Za-z0-9._-]+', '-', value).strip('-._')
    return (value or fallback)[:limit]

def load_manifest():
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_manifest(manifest):
    mdir = os.path.dirname(MANIFEST_FILE)
    if mdir:
        os.makedirs(mdir, exist_ok=True)
    with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

def is_valid_pdf(filepath):
    if not os.path.exists(filepath):
        return False
    size = os.path.getsize(filepath)
    if size < 10000:
        return False
    with open(filepath, 'rb') as f:
        header = f.read(4)
    return header == b'%PDF'

def is_browser_check_title(title):
    low = (title or '').lower()
    return 'recaptcha' in low or '检查您的浏览器' in title or 'checking your browser' in low

def wait_for_browser_check(page, max_seconds=300):
    print("\n⚠️  遇到 PMC 浏览器检查 / reCAPTCHA")
    print("   请在打开的浏览器窗口中手动通过验证；脚本会等待。")
    waited = 0
    while waited < max_seconds:
        time.sleep(5)
        waited += 5
        try:
            title = page.title()
            if not is_browser_check_title(title):
                print(f"✓ 浏览器检查已通过！（等待了 {waited} 秒）")
                return True
        except:
            pass
        if waited % 30 == 0:
            print(f"  等待中... 已等待 {waited} 秒")
    print("✗ 浏览器检查等待超时。")
    return False

def capture_failure_screenshot(page, paper, reason):
    os.makedirs(FAILURE_SCREENSHOT_DIR, exist_ok=True)
    ident = (
        paper.get('row_id')
        or paper.get('pmcid')
        or paper.get('pmid')
        or paper.get('doi')
        or 'pmc-row'
    )
    path = os.path.join(
        FAILURE_SCREENSHOT_DIR,
        f"{safe_slug(ident)}__{safe_slug(reason, 'failure', 60)}.png"
    )
    info = {}
    try:
        info['observed_url'] = page.url
    except Exception:
        pass
    try:
        info['observed_title'] = page.title()
    except Exception:
        pass
    try:
        page.screenshot(path=path, full_page=True, timeout=10000)
    except Exception:
        try:
            page.screenshot(path=path, full_page=False, timeout=5000)
        except Exception as exc:
            info['failure_screenshot_error'] = str(exc)[:120]
            return info
    info['failure_screenshot_path'] = os.path.relpath(path, os.getcwd())
    return info

def failure_info(page, paper, reason, **extra):
    info = {'reason': reason}
    info.update(extra)
    info.update(capture_failure_screenshot(page, paper, reason))
    return info

def find_pdf_url_on_page(page):
    try:
        btn = page.query_selector('button:has-text("Download PDF")')
        if btn:
            return 'button', btn
        links = page.query_selector_all('a[href*="pdf"]')
        for link in links:
            href = link.get_attribute('href') or ''
            if 'pdf' in href.lower():
                return 'link', link
        resources_btn = page.query_selector('button:has-text("Open resources")')
        if resources_btn:
            resources_btn.click()
            time.sleep(1)
            links = page.query_selector_all('a[href*="pdf"]')
            for link in links:
                href = link.get_attribute('href') or ''
                if 'pdf' in href.lower():
                    return 'link_in_resources', link
        return None, None
    except:
        return None, None

def download_paper(page, paper):
    pmcid = paper['pmcid']
    filename = paper.get('filename', f"{pmcid}__pmc.pdf")
    filepath = os.path.join(OUTPUT_DIR, filename)

    if is_valid_pdf(filepath):
        return True, {'skipped': True, 'reason': 'already_exists'}

    article_url = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/"

    try:
        page.goto(article_url, wait_until='domcontentloaded', timeout=60000)
        time.sleep(random.uniform(5, 8))

        title = page.title()
        if is_browser_check_title(title):
            if wait_for_browser_check(page):
                page.goto(article_url, wait_until='domcontentloaded', timeout=60000)
                time.sleep(random.uniform(3, 5))
                title = page.title()
            else:
                return False, failure_info(page, paper, 'manual_browser_required', detail=title[:80])
        if '404' in title or 'Page Not Found' in title:
            return False, failure_info(page, paper, '404_not_found')
        if 'PMC' not in title and 'pmc' not in title.lower():
            return False, failure_info(page, paper, f'bad_page_title:{title[:50]}')

        page.evaluate("window.scrollTo(0, 300)")
        time.sleep(random.uniform(1, 2))
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(random.uniform(1, 2))

        pdf_type, pdf_element = find_pdf_url_on_page(page)
        if pdf_element:
            try:
                with page.expect_download(timeout=45000) as dl_info:
                    pdf_element.click()
                dl = dl_info.value
                dl.save_as(filepath)
                if is_valid_pdf(filepath):
                    size = os.path.getsize(filepath)
                    return True, {'size': size, 'method': f'click_{pdf_type}'}
            except Exception:
                pass

        pdf_url = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/pdf/"
        try:
            with page.expect_download(timeout=45000) as dl_info:
                page.goto(pdf_url)
            dl = dl_info.value
            dl.save_as(filepath)
            if is_valid_pdf(filepath):
                size = os.path.getsize(filepath)
                return True, {'size': size, 'method': 'direct_pdf_url'}
        except Exception:
            try:
                page.goto(article_url, wait_until='domcontentloaded', timeout=60000)
                time.sleep(random.uniform(3, 5))
            except:
                pass

        try:
            result = page.evaluate("""async (pmcid) => {
                try {
                    const pdfUrl = 'https://pmc.ncbi.nlm.nih.gov/articles/' + pmcid + '/pdf/';
                    const resp = await fetch(pdfUrl, { credentials: 'include', redirect: 'follow' });
                    const buf = await resp.arrayBuffer();
                    const bytes = new Uint8Array(buf);
                    const hdr = String.fromCharCode(bytes[0], bytes[1], bytes[2], bytes[3]);
                    if (hdr === '%PDF') {
                        let binary = '';
                        for (let i = 0; i < bytes.length; i++) binary += String.fromCharCode(bytes[i]);
                        return { success: true, data: btoa(binary), size: bytes.length };
                    }
                    return { success: false, size: bytes.length, header: hdr, status: resp.status };
                } catch(e) {
                    return { success: false, error: e.message };
                }
            }""", pmcid)

            if result.get('success') and result.get('data'):
                pdf_data = base64.b64decode(result['data'])
                with open(filepath, 'wb') as f:
                    f.write(pdf_data)
                if is_valid_pdf(filepath):
                    return True, {'size': len(pdf_data), 'method': 'fetch_base64'}

            return False, failure_info(
                page, paper, 'fetch_failed',
                detail=str(result.get('status') or result.get('error') or 'unknown')[:50]
            )
        except Exception:
            pass

        return False, failure_info(page, paper, 'all_methods_failed')

    except Exception as e:
        return False, failure_info(page, paper, 'exception', error=str(e)[:80])

def main():
    manifest = load_manifest()
    pending = [m for m in manifest if m.get('status') != 'downloaded']

    print(f"{'=' * 60}")
    print(f"PMC 剩余论文下载器 v6 (超慢速版)")
    print(f"  总计: {len(manifest)}")
    print(f"  已下载: {len(manifest) - len(pending)}")
    print(f"  待下载: {len(pending)}")
    print(f"{'=' * 60}")

    if not pending:
        print("所有论文已下载完成！")
        return

    print(f"\n启动浏览器（使用已有用户数据目录）...")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            viewport={'width': 1440, 'height': 900},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            accept_downloads=True,
            slow_mo=500
        )

        page = context.new_page()

        print(f"\n预热: 打开 PMC 主页...")
        page.goto("https://pmc.ncbi.nlm.nih.gov/", wait_until='domcontentloaded', timeout=60000)
        time.sleep(5)

        title = page.title()
        if is_browser_check_title(title):
            if not wait_for_browser_check(page):
                context.close()
                return

        print("\n开始下载（超慢模式，每篇间隔 15-25 秒）...")
        print("-" * 60)

        success_count = 0
        fail_count = 0

        for i, paper in enumerate(pending):
            pmcid = paper['pmcid']
            progress = f"[{i+1}/{len(pending)}]"

            if i > 0 and i % 5 == 0:
                print(f"  ── 休息 2 分钟（防限流）...")
                time.sleep(120)

            success, info = download_paper(page, paper)

            if success:
                if info.get('skipped'):
                    print(f"{progress} ↷ {pmcid} - 已存在")
                else:
                    success_count += 1
                    size_kb = info.get('size', 0) // 1024
                    method = info.get('method', 'unknown')
                    print(f"{progress} ✓ {pmcid} ({size_kb}KB) [{method}]")

                    for m in manifest:
                        if m['pmcid'] == pmcid:
                            m['status'] = 'downloaded'
                            m['file_size_bytes'] = info.get('size')
                            m['download_method'] = method
                            m['downloaded_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
                            break
            else:
                fail_count += 1
                reason = info.get('reason', 'unknown')
                error = info.get('error', '')
                detail = info.get('detail', '')
                print(f"{progress} ✗ {pmcid} - {reason}")
                if error:
                    print(f"     错误: {error[:80]}")
                if detail:
                    print(f"     详情: {detail[:80]}")

                for m in manifest:
                    if m['pmcid'] == pmcid:
                        m['status'] = 'manual_browser_required' if reason == 'manual_browser_required' else 'failed'
                        m['failure_reason'] = reason
                        if error:
                            m['error'] = error
                        if detail:
                            m['failure_detail'] = detail
                        if info.get('failure_screenshot_path'):
                            m['failure_screenshot_path'] = info['failure_screenshot_path']
                        if info.get('failure_screenshot_error'):
                            m['failure_screenshot_error'] = info['failure_screenshot_error']
                        if info.get('observed_url'):
                            m['observed_url'] = info['observed_url']
                        if info.get('observed_title'):
                            m['observed_title'] = info['observed_title']
                        m['attempted_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        break

            if (i + 1) % 3 == 0:
                save_manifest(manifest)

            if i < len(pending) - 1:
                time.sleep(random.uniform(15, 25))

        save_manifest(manifest)

        print(f"\n{'=' * 60}")
        print(f"下载完成！")
        print(f"  本次成功: {success_count}")
        print(f"  本次失败: {fail_count}")
        print(f"{'=' * 60}")

        final_downloaded = sum(1 for m in manifest if m['status'] == 'downloaded')
        final_failed = sum(1 for m in manifest if m['status'] == 'failed')
        print(f"\n最终统计:")
        print(f"  已下载: {final_downloaded}")
        print(f"  失败: {final_failed}")
        print(f"  总数: {len(manifest)}")

        print(f"\n浏览器保持打开状态 30 秒后自动关闭...")
        time.sleep(30)
        context.close()

if __name__ == '__main__':
    main()
