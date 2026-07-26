# Versioned Records Pattern — Template & Guide

This document provides the complete specification for the versioned records pattern, used by document/submission projects (e.g., 申报材料, 合同管理, 报表, 认证材料) to track versions without a single growing log file.

## When to Use This Pattern

- **Document projects**: primary deliverable is forms, submissions, certifications, or reports
- **Any project with versioned submissions**: where each version has distinct content, limits, and outcomes
- **Instead of daily memory logs**: when the project spans months/years and a daily log would grow unboundedly

## When NOT to Use

- **Code projects**: use `memory/YYYY-MM-DD.md` daily logs instead
- **One-off documents**: a single spec or plan doesn't need versioned records
- **Projects with no submission/versioning cycle**

## Structure

```
提交记录/ (or submissions/, 版本记录/)
├── INDEX.md          # One line per version — never grows long
├── v001/
│   ├── RECORD.md     # This version's content, limits, result, rejection reasons
│   ├── 上传包/        # Physical files prepared for upload (copies, NOT symlinks)
│   └── 提交凭证/      # Screenshots, receipts, rejection pages
├── v002/
│   ├── RECORD.md
│   ├── 上传包/
│   └── 提交凭证/
└── ...
```

### Directory naming

- `提交记录/` — Chinese name (use if the project is Chinese-language)
- `submissions/` — English equivalent (use for international projects)
- Pick one and be consistent within the project

### Version naming

- `v001`, `v002`, `v003`... — zero-padded 3-digit incrementing number
- Never renumber existing versions (breaks references)
- Scan the directory first; if `v003` is the highest, the next is `v004`

## INDEX.md Template

```markdown
# 提交记录索引

| 版本 | 日期 | 状态 | 主要变化 | 详情 |
|---|---|---|---|---|
| v001 | 2026-07-09 | 已退回 | 首次提交 | `v001/RECORD.md` |
| v002 | 2026-07-14 | 准备中 | 更新证书和信用报告 | `v002/RECORD.md` |
| v003 | 2026-07-18 | 已提交 | 补充起草人信息 | `v003/RECORD.md` |
```

### INDEX.md Rules

- **One line per version** — never expand a version into multiple rows
- **Status values**: `准备中` (preparing), `已提交` (submitted), `已退回` (rejected), `已通过` (approved), `已撤回` (withdrawn)
- **主要变化** — one short phrase, NOT a paragraph
- **详情** — link to the version's `RECORD.md`
- **Never delete rows** — if a version is withdrawn, update the status column; don't remove the row

## RECORD.md Template

```markdown
# [版本号] 提交记录

> **版本**: vNNN
> **日期**: YYYY-MM-DD
> **状态**: [准备中 / 已提交 / 已退回 / 已通过]
> **申报路线**: [标准制修订 / 产品评价 / ...]

---

## 本轮提交内容

[List of files/documents included in this submission]

| 文件 | 来源 | 说明 |
|---|---|---|
| [filename] | [source path or "新建"] | [brief description] |

---

## 页面限制与字段要求

[Constraints discovered from the submission website or instructions]

- 单文件大小限制: [e.g., 10MB]
- 允许格式: [e.g., PDF, JPG]
- 必填字段: [list]
- 数量限制: [e.g., 最多 5 个附件]

---

## 上传包说明

[What was prepared in 上传包/ and why]

- `[filename]` — 原文件 131.8MB，压缩至 8MB
- `[filename]` — 三份证书合并为一个 PDF
- `[filename]` — 源文件为 Word，转换为 PDF

---

## 提交结果

- **提交时间**: [timestamp or "未提交"]
- **提交方式**: [网页上传 / 邮件 / 现场]
- **回执/凭证**: `提交凭证/[filename]`
- **审核结果**: [待审核 / 已通过 / 已退回]

---

## 驳回原因（如有）

[If rejected, list the specific rejection reasons from the website or reviewer]

- [原因 1]
- [原因 2]

---

## 下一版待办

[What needs to be done for the next version, based on rejection reasons or new requirements]

- [ ] [待办 1]
- [ ] [待办 2]

---

## 参考链接

- 申报说明: `docs/specs/...`
- 相关决策: `docs/decisions/...`
- 源文件位置: `公司资料/合作企业/.../`
```

## Source File Principle (Critical)

### The Rule

**Source files are read-only. Never modify, overwrite, or delete the original.**

### Why

- Source files (certificates, credit reports, contracts) are often irreplaceable or expensive to re-obtain
- Different submission rounds may need different modifications (compress, split, convert) — you can't predict future needs
- If you modify the source, you lose the canonical version and can't reproduce previous submissions
- Regulatory audits may require the original unmodified file

### How to Prepare an Upload Package

1. **Read the submission website** — note field names, required/optional, format, size limit, quantity limit, error messages.
2. **Record the limits** in this version's `RECORD.md` under "页面限制与字段要求".
3. **Copy source files** into `vNNN/上传包/` — never modify the source.
4. **Modify the copies** as needed:
   - Compress large files (e.g., 131.8MB credit report → 8MB ZIP)
   - Split or merge certificates (e.g., 3 certificates → 1 PDF)
   - Convert formats (e.g., Word → PDF)
   - Resize images for size limits
5. **Verify** the upload package: format, size, quantity, clarity, QR codes, file hashes.
6. **Upload** only from the `上传包/` directory — never from the source location.
7. **Save proof** — screenshots, receipts, rejection pages go into `vNNN/提交凭证/`.

### What Goes Where

| File type | Location | Why |
|---|---|---|
| Original certificate/report/contract | `公司资料/.../` (canonical source) | Read-only, irreplaceable |
| Modified copy for upload | `vNNN/上传包/` | Version-specific, disposable after submission |
| Submission screenshot/receipt | `vNNN/提交凭证/` | Proof of submission, needed for audit |
| Material checklist | `MATERIALS.md` (product-level) | References source files by path, doesn't duplicate them |

## Upload Interaction Workflow

This workflow standardizes the process of preparing and submitting materials to a website or portal:

1. **Read the target page** — field names, required/optional, format, size limit, quantity limit, error messages.
2. **Record constraints** in `vNNN/RECORD.md` under "页面限制与字段要求".
3. **Generate upload package** in `vNNN/上传包/` based on constraints (compress, split, convert — copies only).
4. **Source files stay untouched** — `上传包/` contains physical files only, no symlinks.
5. **Pre-upload check** — verify format, size, quantity, clarity, QR codes, file hashes.
6. **Upload from `上传包/` only** — browser selects files from this directory.
7. **Post-upload** — save page feedback (success/rejection) to `vNNN/提交凭证/`; if rejected, write reasons in `RECORD.md` and create `vNNN+1/`.

## Worked Example (圳品申报 scenario)

### Scenario

A company is submitting standard revision documents. The submission website has a 10MB per-file limit, but the source Word document is 16.7MB (due to embedded fonts). The first submission was rejected for missing drafter information.

### Structure

```
标准制修订申报/2026年立项/
├── INDEX.md
├── 工作版本/
│   ├── v001/                    # Jul 9 initial draft
│   ├── v002/                    # Jul 14 updated draft
│   └── v003/                    # "ob 提交版" (current working version)
└── 提交记录/
    ├── INDEX.md
    ├── v001/
    │   ├── RECORD.md            # First submission, rejected (missing drafters)
    │   ├── 上传包/
    │   │   └── 申报书-compressed.pdf   # 16.7MB → 8MB
    │   └── 提交凭证/
    │       └── rejection-screenshot.png
    └── v002/
        ├── RECORD.md            # Preparing: added drafters, 4 fields still missing
        └── (not yet uploaded)
```

### INDEX.md

```markdown
# 提交记录索引

| 版本 | 日期 | 状态 | 主要变化 | 详情 |
|---|---|---|---|---|
| v001 | 2026-07-14 | 已退回 | 首次提交，缺起草人 | `v001/RECORD.md` |
| v002 | 2026-07-20 | 准备中 | 补起草人，4字段待补 | `v002/RECORD.md` |
```

### v001/RECORD.md (excerpt)

```markdown
## 提交结果
- 提交时间: 2026-07-14 15:30
- 审核结果: 已退回

## 驳回原因
- 缺少联系人信息
- 缺少四名起草人信息

## 上传包说明
- `申报书-compressed.pdf` — 原文件 16.7MB（含字体），压缩为 8MB PDF
- 源文件: `工作版本/v002/申报书.docx`（只读，未修改）

## 下一版待办
- [ ] 补充联系人
- [ ] 补充四名起草人
- [ ] 补充经费保障、经费来源、经费金额、是否申请补助
```

## Relationship to Other Patterns

| Pattern | Use for | Key difference |
|---|---|---|
| `memory/YYYY-MM-DD.md` | Code project daily logs | Chronological, one file per day |
| `提交记录/vNNN/RECORD.md` | Document project submissions | Per-version, one file per submission round |
| `conversation/NN-*.md` | Discussion records | Per-topic, captures agent-user dialogue |
| `docs/decisions/*.md` | Decision records | Per-decision, ADR-style |

A project may use multiple patterns simultaneously (e.g., a hybrid project might have both `memory/` daily logs and `提交记录/` versioned records).
