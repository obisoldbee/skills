#!/usr/bin/env python3
"""
DOI 出版社论文下载器 v3
用法: python3 doi_downloader.py <batch_file.json> [delay_min] [delay_max]
  batch_file.json  - 包含论文列表的 JSON 文件（由 extract_doi_papers.py 生成）
  delay_min        - 每篇之间最小延迟秒数 (默认 5)
  delay_max        - 每篇之间最大延迟秒数 (默认 10)

环境变量:
  PAPER_DIR        - PDF 保存目录 (默认: ./paper)
  MANIFEST_FILE    - manifest JSON 路径 (默认: ./download-manifest.json)
  CHROME_PROFILE   - 临时 Chrome 用户数据目录 (默认: 系统临时目录下的 akashic-paperdownloader-browser-data/doi)
"""
import asyncio
import json
import os
import re
import tempfile
import time
import random
import base64
import sys

try:
    from playwright.async_api import async_playwright
except ModuleNotFoundError as exc:
    raise SystemExit(
        "blocked_runtime_missing_python_playwright: install/activate Python "
        "Playwright before running doi_downloader.py; do not mark paper rows "
        "as failed because this runtime dependency is missing"
    ) from exc

PAPER_DIR = os.environ.get('PAPER_DIR', './paper')
MANIFEST_FILE = os.environ.get('MANIFEST_FILE', './download-manifest.json')
USER_DATA_DIR = os.environ.get('CHROME_PROFILE',
    os.path.join(tempfile.gettempdir(), 'akashic-paperdownloader-browser-data', 'doi'))
FAILURE_SCREENSHOT_DIR = os.environ.get(
    'FAILURE_SCREENSHOT_DIR',
    os.path.join(os.path.dirname(MANIFEST_FILE) or '.', 'failure-screenshots')
)
SKIP_FAILED = os.environ.get('SKIP_FAILED', '').lower() in ('1', 'true', 'yes')

BATCH_FILE = sys.argv[1] if len(sys.argv) > 1 else None
DELAY_MIN = int(sys.argv[2]) if len(sys.argv) > 2 else 5
DELAY_MAX = int(sys.argv[3]) if len(sys.argv) > 3 else 10

os.makedirs(PAPER_DIR, exist_ok=True)

def safe_slug(value, fallback='unknown', limit=90):
    value = str(value or fallback)
    value = re.sub(r'[^A-Za-z0-9._-]+', '-', value).strip('-._')
    return (value or fallback)[:limit]

def clean_doi(doi):
    if not doi: return None
    doi = doi.split('|')[0]
    doi = re.sub(r'）.*$', '', doi)
    doi = doi.rstrip('.,;)"\'…')
    doi = re.sub(r'\.t\d+$', '', doi)
    if not re.match(r'^10\.\d{4,}/', doi): return None
    return doi

async def try_fetch_pdf(page, url, filename):
    try:
        result = await asyncio.wait_for(page.evaluate('''async (url) => {
            const controller = new AbortController();
            const timer = setTimeout(() => controller.abort(), 20000);
            try {
                const resp = await fetch(url, {credentials: 'include', redirect: 'follow', signal: controller.signal});
                if (!resp.ok) return {ok: false, status: resp.status};
                const buf = await resp.arrayBuffer();
                const bytes = new Uint8Array(buf);
                if (bytes.length < 5000) return {ok: false, status: 'too_small:' + bytes.length};
                const hdr = String.fromCharCode(bytes[0], bytes[1], bytes[2], bytes[3]);
                if (hdr !== '%PDF') return {ok: false, status: 'not_pdf:' + hdr};
                let bin = '';
                for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
                return {ok: true, b64: btoa(bin), len: bytes.length};
            } catch(e) {
                return {ok: false, status: 'err:' + e.message};
            } finally {
                clearTimeout(timer);
            }
        }''', url), timeout=25)
        if not result or not result.get('ok'):
            return {'ok': False, 'error': result.get('status', 'unknown') if result else 'no_result'}
        pdf_bytes = base64.b64decode(result['b64'])
        with open(os.path.join(PAPER_DIR, filename), 'wb') as f:
            f.write(pdf_bytes)
        return {'ok': True, 'size': len(pdf_bytes) // 1024}
    except Exception as e:
        return {'ok': False, 'error': str(e)[:100]}

async def navigate_and_wait(page, url, timeout=30000):
    try:
        await page.goto(url, wait_until='networkidle', timeout=timeout)
        await page.wait_for_timeout(3000)
        await dismiss_cookie_banner(page)
        return True
    except:
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=20000)
            await page.wait_for_timeout(2000)
            await dismiss_cookie_banner(page)
            return True
        except:
            return False

async def dismiss_cookie_banner(page):
    selectors = [
        'button:has-text("Reject optional cookies")',
        'button:has-text("Reject optional")',
        'button:has-text("Accept all cookies")',
        'button:has-text("Accept all")',
        'button:has-text("I agree")',
        'button:has-text("Agree")',
        'button:has-text("Close")',
    ]
    for selector in selectors:
        try:
            locator = page.locator(selector).first
            if await locator.count() and await locator.is_visible(timeout=800):
                await locator.click(timeout=1500)
                await page.wait_for_timeout(800)
                return True
        except Exception:
            continue
    return False

async def capture_failure_screenshot(page, paper, reason):
    os.makedirs(FAILURE_SCREENSHOT_DIR, exist_ok=True)
    ident = (
        paper.get('section')
        or paper.get('row_id')
        or paper.get('pmid')
        or paper.get('doi')
        or 'doi-row'
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
        info['observed_title'] = await page.title()
    except Exception:
        pass
    try:
        await page.screenshot(path=path, full_page=True, timeout=10000)
    except Exception:
        try:
            await page.screenshot(path=path, full_page=False, timeout=5000)
        except Exception as exc:
            info['failure_screenshot_error'] = str(exc)[:120]
            return info
    info['failure_screenshot_path'] = os.path.relpath(path, os.getcwd())
    return info

async def failure_result(page, paper, status, reason, doi, publisher, **extra):
    screenshot = await capture_failure_screenshot(page, paper, reason)
    result = {
        'status': status,
        'reason': reason,
        'doi': doi,
        'publisher': publisher,
    }
    result.update(extra)
    result.update(screenshot)
    return result

async def page_indicates_paywall(page):
    try:
        text = await page.evaluate('''() => document.body ? document.body.innerText : ''')
    except Exception:
        text = ''
    try:
        html = await page.content()
    except Exception:
        html = ''
    low = ((text or '') + '\n' + (html or '')).lower()
    paywall_markers = [
        'buy article pdf',
        'ppv-article',
        'price:',
        'purchase article',
        'purchase this article',
        'access this article',
        'rent or buy',
        'subscribe to journal',
        'log in to check access',
        'instant access to the full article pdf',
        'get access',
    ]
    return any(marker in low for marker in paywall_markers)

async def find_pdf_url(page):
    try:
        return await page.evaluate('''() => {
            const meta = document.querySelector('meta[name="citation_pdf_url"]');
            if (meta && meta.content) return meta.content;
            const links = document.querySelectorAll('a');
            const candidates = [];
            for (const a of links) {
                const text = (a.textContent || '').toLowerCase();
                const href = a.href || '';
                if (!href) continue;
                if (text.includes('supplement') || href.toLowerCase().includes('supplement')) continue;
                if (text.includes('pdf') || href.includes('.pdf') || href.includes('/pdf/') ||
                    href.includes('/content/pdf/') || href.includes('pdfft') || href.includes('article/file')) {
                    candidates.push(href);
                }
            }
            if (location.pathname.includes('/doi/')) {
                const doiPart = location.pathname.split('/doi/')[1];
                if (doiPart && !doiPart.includes('/pdf/')) {
                    candidates.unshift(location.origin + '/doi/pdf/' + doiPart);
                }
            }
            return candidates.length > 0 ? candidates[0] : null;
        }''')
    except Exception:
        return None

async def download_one(page, paper, idx, total):
    doi = clean_doi(paper['doi'])
    publisher = paper['publisher']
    pmid = paper.get('pmid')
    fname = f"PMID_{pmid}__{publisher.lower()}.pdf" if pmid else f"DOI_{doi.replace('/','_').replace('.','-')}__{publisher.lower()}.pdf"

    print(f"[{idx}/{total}] {publisher}: {doi}")

    article_url = f'https://doi.org/{doi}'
    pdf_url = None
    r = {'ok': False}

    if publisher == 'Springer':
        pdf_url = f'https://link.springer.com/content/pdf/{doi}.pdf'
        await navigate_and_wait(page, f'https://link.springer.com/article/{doi}', 20000)
        r = await try_fetch_pdf(page, pdf_url, fname)
        if r['ok']:
            print(f"  ✓ {r['size']}KB [springer_direct]")
            return {'status': 'downloaded', 'doi': doi, 'size': r['size'], 'method': 'springer_direct', 'filename': fname}
        pdf_url = await find_pdf_url(page)
        if pdf_url:
            r = await try_fetch_pdf(page, pdf_url, fname)
            if r['ok']:
                print(f"  ✓ {r['size']}KB [springer_meta_pdf]")
                return {'status': 'downloaded', 'doi': doi, 'size': r['size'], 'method': 'springer_meta_pdf', 'filename': fname}
        if await page_indicates_paywall(page):
            print("  ✗ paywalled")
            return await failure_result(
                page, paper, 'paywalled', 'buy_article_pdf_or_login_required',
                doi, publisher
            )

    elif publisher == 'Nature':
        await navigate_and_wait(page, article_url, 25000)
        try:
            pdf_url = await page.evaluate('''() => {
                const links = document.querySelectorAll('a');
                for (const a of links) {
                    if (a.href && a.href.includes('.pdf')) return a.href;
                    if (a.getAttribute('data-track-label') === 'download PDF') return a.href;
                }
                if (location.hostname.includes('nature.com') && location.pathname.includes('/articles/')) {
                    return location.href.replace(/\\/$/, '') + '.pdf';
                }
                return null;
            }''')
        except Exception:
            pdf_url = None
        if pdf_url:
            r = await try_fetch_pdf(page, pdf_url, fname)
            if r['ok']:
                print(f"  ✓ {r['size']}KB [nature_pdf]")
                return {'status': 'downloaded', 'doi': doi, 'size': r['size'], 'method': 'nature_pdf', 'filename': fname}
        pdf_url = await find_pdf_url(page)
        if pdf_url:
            r = await try_fetch_pdf(page, pdf_url, fname)
            if r['ok']:
                print(f"  ✓ {r['size']}KB [nature_meta_pdf]")
                return {'status': 'downloaded', 'doi': doi, 'size': r['size'], 'method': 'nature_meta_pdf', 'filename': fname}
        if await page_indicates_paywall(page):
            print("  ✗ paywalled")
            return await failure_result(
                page, paper, 'paywalled', 'buy_article_pdf_or_login_required',
                doi, publisher
            )

    elif publisher == 'Science_AAAS':
        await navigate_and_wait(page, article_url, 25000)
        try:
            pdf_url = await page.evaluate('''() => {
                const links = document.querySelectorAll('a');
                for (const a of links) {
                    if ((a.textContent.includes('PDF') || a.href.includes('.pdf')) && a.href) return a.href;
                }
                return null;
            }''')
        except Exception:
            pdf_url = None
        if pdf_url:
            r = await try_fetch_pdf(page, pdf_url, fname)
            if r['ok']:
                print(f"  ✓ {r['size']}KB [science_pdf]")
                return {'status': 'downloaded', 'doi': doi, 'size': r['size'], 'method': 'science_pdf', 'filename': fname}

    elif publisher in ('Cambridge', 'NEJM', 'JBC', 'PNAS', 'JLR_Lipids', 'JAHA_AHA',
                        'Oxford', 'TandF', 'Sage', 'Karger', 'LWW_WoltersKluwer',
                        'AACR', 'ADA_Diabetes', 'FASEB', 'ASN_Nutrition',
                        'J_Immunol', 'JEM_Rockefeller', 'JDS_Dairy', 'BMJ', 'BMC',
                        'PLOS', 'MDPI', 'Frontiers', 'DovePress', 'Spandidos',
                        'Theranostics', 'Oncotarget', 'WJG', 'AnticancerResearch'):
        try:
            await navigate_and_wait(page, article_url, 25000)
            pdf_url = await page.evaluate('''() => {
                const links = document.querySelectorAll('a');
                const candidates = [];
                for (const a of links) {
                    const text = (a.textContent || '').toLowerCase();
                    const href = a.href || '';
                    if ((text.includes('pdf') || href.includes('pdf') || href.includes('/pdf/')) &&
                        !text.includes('supplement') && !text.includes('supplementary') && href) {
                        candidates.push(href);
                    }
                }
                if (location.pathname.includes('/doi/')) {
                    const doiPart = location.pathname.split('/doi/')[1];
                    if (doiPart && !doiPart.includes('/pdf/')) {
                        candidates.unshift(location.origin + '/doi/pdf/' + doiPart);
                    }
                }
                return candidates.length > 0 ? candidates[0] : null;
            }''')
        except Exception:
            pdf_url = None
        if pdf_url:
            r = await try_fetch_pdf(page, pdf_url, fname)
            if r['ok']:
                print(f"  ✓ {r['size']}KB [{publisher.lower()}_pdf]")
                return {'status': 'downloaded', 'doi': doi, 'size': r['size'],
                        'method': f'{publisher.lower()}_pdf', 'filename': fname}

    elif publisher in ('Elsevier', 'Wiley', 'Wiley_Blackwell', 'JAMA', 'ACS', 'RSC',
                        'EndocrineSociety', 'Thieme'):
        await navigate_and_wait(page, article_url, 25000)
        try:
            pdf_url = await page.evaluate('''() => {
                const links = document.querySelectorAll('a');
                for (const a of links) {
                    const text = (a.textContent || '').toLowerCase();
                    const href = a.href || '';
                    if ((text.includes('pdf') || href.includes('pdf')) &&
                        !text.includes('supplement') && href) return href;
                }
                const elsevierLink = document.querySelector('a[href*="pdfft"]') ||
                                      document.querySelector('a[href*="/pdfft/"]');
                if (elsevierLink) return elsevierLink.href;
                return null;
            }''')
        except Exception:
            pdf_url = None
        if pdf_url:
            r = await try_fetch_pdf(page, pdf_url, fname)
            if r['ok']:
                print(f"  ✓ {r['size']}KB [{publisher.lower()}_pdf]")
                return {'status': 'downloaded', 'doi': doi, 'size': r['size'],
                        'method': f'{publisher.lower()}_pdf', 'filename': fname}

    else:
        await navigate_and_wait(page, article_url, 25000)
        try:
            pdf_url = await page.evaluate('''() => {
                const links = document.querySelectorAll('a');
                for (const a of links) {
                    const text = (a.textContent || '').toLowerCase();
                    const href = a.href || '';
                    if ((text.includes('pdf') || href.includes('pdf')) &&
                        !text.includes('supplement') && href) return href;
                }
                if (location.pathname.includes('/doi/') && !location.pathname.includes('/pdf/')) {
                    const doiPart = location.pathname.split('/doi/')[1];
                    if (doiPart) return location.origin + '/doi/pdf/' + doiPart;
                }
                return null;
            }''')
        except Exception:
            pdf_url = None
        if pdf_url:
            r = await try_fetch_pdf(page, pdf_url, fname)
            if r['ok']:
                print(f"  ✓ {r['size']}KB [generic_pdf]")
                return {'status': 'downloaded', 'doi': doi, 'size': r['size'],
                        'method': 'generic_pdf', 'filename': fname}

    if not pdf_url or not r['ok']:
        pdf_url = await find_pdf_url(page)
        if pdf_url:
            r = await try_fetch_pdf(page, pdf_url, fname)
            if r['ok']:
                print(f"  ✓ {r['size']}KB [fallback]")
                return {'status': 'downloaded', 'doi': doi, 'size': r['size'],
                        'method': 'fallback', 'filename': fname}

    pmcids = paper.get('pmcids', [])
    valid_pmcids = [p for p in pmcids if re.match(r'^PMC\d{5,}$', p)]
    for pmcid in valid_pmcids:
        try:
            await page.goto(f'https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/',
                           wait_until='domcontentloaded', timeout=15000)
            await page.wait_for_timeout(2000)
        except: pass
        r = await try_fetch_pdf(page, f'https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/pdf/',
                                fname.replace(f'__{publisher.lower()}', '__pmc'))
        if r['ok']:
            print(f"  ✓ {r['size']}KB [pmc:{pmcid}]")
            return {'status': 'downloaded', 'doi': doi, 'size': r['size'],
                    'method': 'pmc_fallback', 'filename': fname, 'pmcid': pmcid}

    try:
        page_text = await page.evaluate('() => document.title')
    except:
        page_text = ''
    reason = 'no_pdf_found'
    if 'access' in (page_text or '').lower() or 'sign in' in (page_text or '').lower() or await page_indicates_paywall(page):
        reason = 'paywalled'

    print(f"  ✗ {reason}")
    return await failure_result(
        page, paper,
        'failed' if reason == 'no_pdf_found' else 'paywalled',
        reason,
        doi,
        publisher
    )

async def main():
    if not BATCH_FILE:
        print("用法: python3 doi_downloader.py <batch_file.json> [delay_min] [delay_max]")
        return

    with open(BATCH_FILE) as f:
        papers = json.load(f)

    seen = set()
    clean = []
    for p in papers:
        d = clean_doi(p['doi'])
        if not d: continue
        if d.lower() in seen: continue
        seen.add(d.lower())
        p['doi'] = d
        clean.append(p)

    mdir = os.path.dirname(MANIFEST_FILE)
    if mdir:
        os.makedirs(mdir, exist_ok=True)
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE) as f:
            manifest = json.load(f)
    else:
        manifest = []
    existing = set()
    for m in manifest:
        if m.get('doi') and (m.get('status') in ('downloaded', 'paywalled') or SKIP_FAILED):
            existing.add(m['doi'].lower())

    to_download = [p for p in clean if p['doi'].lower() not in existing]

    batch_name = os.path.basename(BATCH_FILE)
    print(f"=== DOI 下载器 v3 [{batch_name}] ===")
    print(f"  输入: {len(clean)} 篇, 去重后: {len(clean)} 篇")
    print(f"  已下载: {len(clean) - len(to_download)} 篇")
    print(f"  待下载: {len(to_download)} 篇")
    print(f"  延迟: {DELAY_MIN}-{DELAY_MAX} 秒")
    print()

    if not to_download:
        print("没有需要下载的论文")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=False,
            args=['--disable-blink-features=AutomationControlled'],
            viewport={'width': 1280, 'height': 800}
        )
        page = browser.pages[0] if browser.pages else await browser.new_page()

        ok = 0
        fail = 0
        paywall = 0

        for i, paper in enumerate(to_download):
            try:
                r = await download_one(page, paper, i + 1, len(to_download))
            except Exception as e:
                print(f"  ✗ ERROR: {str(e)[:80]}")
                r = await failure_result(
                    page, paper, 'failed', 'crash:' + str(e)[:50],
                    paper['doi'], paper.get('publisher')
                )

            manifest.append({
                'doi': r.get('doi', paper['doi']),
                'pmid': paper.get('pmid'),
                'section': paper.get('section'),
                'publisher': paper.get('publisher'),
                'status': r['status'],
                'filename': r.get('filename'),
                'method': r.get('method'),
                'failure_reason': r.get('reason'),
                'failure_screenshot_path': r.get('failure_screenshot_path'),
                'failure_screenshot_error': r.get('failure_screenshot_error'),
                'observed_url': r.get('observed_url'),
                'observed_title': r.get('observed_title'),
                'file_size_kb': r.get('size'),
                'downloaded_at': time.strftime('%Y-%m-%d %H:%M')
            })

            if r['status'] == 'downloaded': ok += 1
            elif r['status'] == 'paywalled': paywall += 1
            else: fail += 1

            with open(MANIFEST_FILE, 'w') as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)

            if i < len(to_download) - 1:
                await page.wait_for_timeout(random.randint(DELAY_MIN * 1000, DELAY_MAX * 1000))

        with open(MANIFEST_FILE, 'w') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        print(f"\n{'='*50}")
        print(f"成功: {ok}  付费墙: {paywall}  失败: {fail}")
        print(f"{'='*50}")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
