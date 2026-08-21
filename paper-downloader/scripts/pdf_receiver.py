#!/usr/bin/env python3
"""
本地 HTTP 接收服务器：接收浏览器发来的 PDF 数据并保存到磁盘
用法: python3 pdf_receiver.py [port]
环境变量:
  PAPER_DIR     - PDF 保存目录 (默认: ./paper)
  MANIFEST_FILE - manifest JSON 路径 (默认: ./download-manifest.json)
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import hashlib
import json
import time
import sys

PAPERS_DIR = os.environ.get('PAPER_DIR', './paper')
MANIFEST_FILE = os.environ.get('MANIFEST_FILE', os.path.join(PAPERS_DIR, "..", "download-manifest.json"))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 18923

os.makedirs(PAPERS_DIR, exist_ok=True)

class PDFReceiver(BaseHTTPRequestHandler):
    download_count = 0
    failed_count = 0
    manifest = []

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        filename = self.headers.get("X-Filename", f"paper_{int(time.time())}.pdf")
        pmcid = self.headers.get("X-Pmcid", "")
        pmid = self.headers.get("X-Pmid", "")
        section = self.headers.get("X-Section", "")
        status = self.headers.get("X-Status", "downloaded")
        failure_reason = self.headers.get("X-Failure-Reason", "")

        filename = filename.replace('/', '_').replace('\\', '_')
        filepath = os.path.join(PAPERS_DIR, filename)

        if content_length > 0:
            data = self.rfile.read(content_length)

            if len(data) > 4 and data[:4] == b'%PDF':
                sha256 = hashlib.sha256(data).hexdigest()

                with open(filepath, 'wb') as f:
                    f.write(data)

                PDFReceiver.download_count += 1

                entry = {
                    'filename': filename,
                    'pmcid': pmcid,
                    'pmid': pmid,
                    'section': section,
                    'status': 'downloaded',
                    'file_size_bytes': len(data),
                    'sha256': sha256,
                    'downloaded_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                PDFReceiver.manifest.append(entry)

                print(f"[{PDFReceiver.download_count}] ✓ {filename} ({len(data)//1024}KB) - {pmcid}")

                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'OK')
            else:
                PDFReceiver.failed_count += 1
                entry = {
                    'filename': filename,
                    'pmcid': pmcid,
                    'pmid': pmid,
                    'section': section,
                    'status': 'failed',
                    'failure_reason': failure_reason or 'not_pdf_header',
                    'file_size_bytes': len(data)
                }
                PDFReceiver.manifest.append(entry)

                print(f"[FAIL] ✗ {filename} - 不是有效的PDF (大小: {len(data)}字节)")

                self.send_response(400)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'NOT_PDF')
        else:
            PDFReceiver.failed_count += 1
            entry = {
                'filename': filename,
                'pmcid': pmcid,
                'pmid': pmid,
                'section': section,
                'status': 'failed',
                'failure_reason': failure_reason or 'empty_content'
            }
            PDFReceiver.manifest.append(entry)
            print(f"[FAIL] ✗ {filename} - 空内容, 原因: {failure_reason}")

            self.send_response(400)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'EMPTY')

    def do_GET(self):
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Access-Control-Allow-origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            data = json.dumps({
                'downloaded': PDFReceiver.download_count,
                'failed': PDFReceiver.failed_count,
                'total': PDFReceiver.download_count + PDFReceiver.failed_count
            })
            self.wfile.write(data.encode())
        else:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(b'Paper Download Receiver Running')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST,OPTIONS,GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type,X-Filename,X-Pmcid,X-Pmid,X-Section,X-Status,X-Failure-Reason')
        self.end_headers()

    def log_message(self, format, *args):
        pass

def save_manifest():
    mdir = os.path.dirname(MANIFEST_FILE)
    if mdir:
        os.makedirs(mdir, exist_ok=True)
    with open(MANIFEST_FILE, 'w', encoding='utf-8') as f:
        json.dump(PDFReceiver.manifest, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    import atexit
    atexit.register(save_manifest)

    server = HTTPServer(('127.0.0.1', PORT), PDFReceiver)
    print("=" * 60)
    print("PDF 接收服务器启动")
    print(f"地址: http://127.0.0.1:{PORT}")
    print(f"保存目录: {PAPERS_DIR}")
    print("=" * 60)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        save_manifest()
        print(f"\n\n下载完成: {PDFReceiver.download_count} 成功, {PDFReceiver.failed_count} 失败")
        print(f"Manifest 已保存到: {MANIFEST_FILE}")
        server.server_close()
