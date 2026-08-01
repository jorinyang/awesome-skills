# Training Document Cascade Workflow

When producing training materials, a single source document (PDF/DOCX) drives multiple output artifacts. Changes to the source MUST cascade to all outputs.

## Cascade Order

```
Source PDF/DOCX
    ↓
05-课程教材.md (唯一内容源头)
    ↓
07-培训PPT.html ← 评分标准、案例、流程
    ↓
08-学员手册.html ← 评分标准、作业要求、作品提交模板
    ↓
06-课后考核.md ← 考核维度、评分权重
    ↓
产出文档/ (交付副本，每次修改后同步)
```

## Sync Checklist

When updating ANY training document, check ALL of these for consistency:

| Content | PPT Page | Handbook Section | Must Match |
|---------|----------|-----------------|------------|
| 评分标准/权重 | S42 (评分标准) | §6 作业与考核 | ✅ 维度数量、分值、描述 |
| 作业要求 | S39 (作业布置) | §6 作业要求 | ✅ 提交方式、截止时间 |
| 命名规范 | — | §6 质量要求 | ✅ 命名格式 |
| 作品提交模板 | — | §6 作品提交模板 | ✅ 模块列表 |

## Sync Command Pattern

```bash
# After any edit, always sync both copies
cp AI培训项目/07-培训PPT.html 产出文档/培训PPT.html
cp AI培训项目/08-学员手册.html 产出文档/学员手册.html
```

## Document Extraction for Training Projects

When user provides supplementary documents (DOCX, PDF) to incorporate:

| Format | Tool | Notes |
|--------|------|-------|
| `.docx` | `python-docx` via `execute_code` | Handles tables; check `doc.tables` |
| `.pdf` | `pymupdf` (`fitz`) via `execute_code` | `page.get_text()`, page-by-page |
| `.docx` fallback | zipfile → `word/document.xml` → ET | When python-docx fails |

**firecrawl_parse** requires `FIRECRAWL_API_URL` (self-hosted). Do not rely on it for local file parsing in Hermes default config.

## Common Cascade Bugs

1. **PPT updated, handbook NOT updated** — scoring criteria diverges silently
2. **Percentage vs score mismatch** — PPT says "25%", handbook says "25分", but the underlying dimensions differ
3. **New dimension added in PPT, handbook table still has old row count** — always count rows after editing
4. **产出文档/ not synced** — user opens old version, reports bug that's already fixed
